"""Flask app entry point for CC-TPR."""

from __future__ import annotations

from flask import Flask, Response, jsonify, request

from .quota import get_quota
from .router import circuit_breaker, config, handle_message, logger
from .status import tracker

app = Flask(__name__)


@app.route("/v1/messages", methods=["POST"])
def messages() -> tuple:
    """Handle incoming message requests."""
    body = request.get_json(force=True)
    headers = dict(request.headers)
    is_stream = body.get("stream", False)

    try:
        upstream, provider_name = handle_message(body, headers)
    except Exception as e:
        logger.error(f"Provider error: {e}")
        return jsonify({"type": "error", "error": {"type": "api_error", "message": str(e)}}), 502

    return _respond_passthrough(upstream, is_stream)


def _respond_passthrough(upstream, is_stream: bool):
    """Respond by passing through upstream response.

    Args:
        upstream: Upstream response object.
        is_stream: Whether streaming was requested.

    Returns:
        Flask response.
    """
    if is_stream:
        return Response(
            _stream_passthrough(upstream),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    return jsonify(upstream.json())


def _stream_passthrough(upstream_resp):
    """Stream passthrough generator.

    Args:
        upstream_resp: Upstream response with iter_content.

    Yields:
        Chunks from upstream.
    """
    for chunk in upstream_resp.iter_content(chunk_size=None):
        if chunk:
            yield chunk


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "ok",
            "model_mapping": config.get("routing", {}).get("models", {}),
            "smart_switch": config.get("routing", {}).get("smart_switch", {}),
        }
    )


@app.route("/status", methods=["GET"])
def status():
    """Status endpoint with current router state."""
    snap = tracker.snapshot()
    snap["circuit_breaker"] = circuit_breaker.status()
    return jsonify(snap)


@app.route("/quota", methods=["GET"])
def quota():
    """Quota endpoint with MiniMax and ZAI usage data."""
    return jsonify(get_quota())


def run_server() -> None:
    """Run the Flask server."""
    host = config["server"].get("host", "127.0.0.1")
    port = config["server"].get("port", 3456)
    log_level = config["server"].get("log_level", "INFO")
    logger.setLevel(log_level)
    logger.info(f"CC-TPR starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    run_server()


def main() -> None:
    """CLI entry point."""
    from dotenv import load_dotenv

    load_dotenv()
    run_server()
