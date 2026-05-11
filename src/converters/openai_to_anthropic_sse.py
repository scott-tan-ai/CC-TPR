"""Converter from OpenAI SSE format to Anthropic SSE format."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from typing import Any


def _sse_event(event_type: str, data: dict) -> str:
    """Create an SSE event string.

    Args:
        event_type: Event type name.
        data: Event data dictionary.

    Returns:
        SSE formatted string.
    """
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def openai_to_anthropic_sse(
    openai_stream: Iterator[bytes], model: str, input_tokens: int = 0
) -> Iterator[str]:
    """Convert OpenAI SSE stream to Anthropic SSE format.

    Note: This converter is kept for reference. Currently all providers
    use Anthropic format directly.

    Args:
        openai_stream: Iterator of OpenAI SSE response lines.
        model: Model name for the response.
        input_tokens: Input token count for usage stats.

    Yields:
        SSE event strings in Anthropic format.
    """
    yield _sse_event(
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": f"msg_{uuid.uuid4().hex[:24]}",
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": model,
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": input_tokens, "output_tokens": 1},
            },
        },
    )

    yield _sse_event(
        "content_block_start",
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""},
        },
    )

    yield _sse_event("ping", {"type": "ping"})

    output_tokens = 0
    tool_call_index = 1
    has_content = False

    for line in openai_stream:
        line = line.strip()
        if not line:
            continue
        if not line.startswith(b"data: "):
            continue

        payload = line[6:]
        if payload == "[DONE]":
            break

        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue

        choice = chunk.get("choices", [{}])[0]
        delta = choice.get("delta", {})

        if delta.get("content"):
            has_content = True
            output_tokens += 1
            yield _sse_event(
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": delta["content"]},
                },
            )

        if delta.get("tool_calls"):
            for tc in delta["tool_calls"]:
                has_content = True
                fn = tc.get("function", {})
                if fn.get("name"):
                    yield _sse_event(
                        "content_block_start",
                        {
                            "type": "content_block_start",
                            "index": tool_call_index,
                            "content_block": {
                                "type": "tool_use",
                                "id": tc.get("id", f"toolu_{uuid.uuid4().hex[:24]}"),
                                "name": fn["name"],
                                "input": {},
                            },
                        },
                    )
                if fn.get("arguments"):
                    yield _sse_event(
                        "content_block_delta",
                        {
                            "type": "content_block_delta",
                            "index": tool_call_index,
                            "delta": {
                                "type": "input_json_delta",
                                "partial_json": fn["arguments"],
                            },
                        },
                    )
                output_tokens += 1

        finish_reason = choice.get("finish_reason")
        if finish_reason:
            if delta.get("tool_calls"):
                yield _sse_event(
                    "content_block_stop",
                    {
                        "type": "content_block_stop",
                        "index": tool_call_index,
                    },
                )
                tool_call_index += 1

    if not has_content:
        yield _sse_event(
            "content_block_delta",
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": ""},
            },
        )

    yield _sse_event(
        "content_block_stop",
        {
            "type": "content_block_stop",
            "index": 0,
        },
    )

    stop_reason = "end_turn"

    yield _sse_event(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": stop_reason, "stop_sequence": None},
            "usage": {"output_tokens": max(output_tokens, 1)},
        },
    )

    yield _sse_event("message_stop", {"type": "message_stop"})


def openai_to_anthropic_response(response_json: dict[str, Any], model: str) -> dict[str, Any]:
    """Convert OpenAI non-streaming response to Anthropic format.

    Args:
        response_json: OpenAI response JSON.
        model: Model name for the response.

    Returns:
        Anthropic format response dictionary.
    """
    choice = response_json.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content", "")

    anthropic_content = [{"type": "text", "text": content or ""}]

    for tc in message.get("tool_calls", []):
        fn = tc.get("function", {})
        try:
            args = json.loads(fn.get("arguments", "{}"))
        except json.JSONDecodeError:
            args = {}
        anthropic_content.append(
            {
                "type": "tool_use",
                "id": tc.get("id", f"toolu_{uuid.uuid4().hex[:24]}"),
                "name": fn.get("name", ""),
                "input": args,
            }
        )

    finish_reason = choice.get("finish_reason", "stop")
    stop_reason = "end_turn" if finish_reason == "stop" else "tool_use"

    return {
        "id": response_json.get("id", f"msg_{uuid.uuid4().hex[:24]}"),
        "type": "message",
        "role": "assistant",
        "content": anthropic_content,
        "model": model,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": response_json.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": response_json.get("usage", {}).get("completion_tokens", 0),
        },
    }
