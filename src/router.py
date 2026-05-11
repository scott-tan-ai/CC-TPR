"""Router logic for CC-TPR."""

from __future__ import annotations

from typing import Any

from .failover import CircuitBreaker
from .providers import get_provider
from .status import tracker
from .tokenizer import count_messages
from .utils.config import load_config
from .utils.logger import setup_logger

logger = setup_logger()
config = load_config()

circuit_breaker = CircuitBreaker(
    threshold=config.get("failover", {}).get("circuit_breaker", {}).get("failure_threshold", 3),
    cooldown_minutes=config.get("failover", {})
    .get("circuit_breaker", {})
    .get("cooldown_minutes", 2),
)


def _get_context_limit(provider_name: str) -> int:
    """Get context limit for a provider.

    Args:
        provider_name: Provider name.

    Returns:
        Context limit in tokens.
    """
    providers = config.get("providers", {})
    return providers.get(provider_name, {}).get("context_limit", 200000)


def _get_model_display_name(provider_name: str, model_key: str) -> str:
    """Get the actual model display name for a provider.

    Args:
        provider_name: Provider name.
        model_key: haiku, sonnet, or opus.

    Returns:
        Model name string.
    """
    providers = config.get("providers", {})
    if provider_name == "minimax":
        return providers.get("minimax", {}).get("model", "MiniMax-M2.7")
    if provider_name == "zai":
        return providers.get("zai", {}).get("models", {}).get(model_key, "glm-4.7")
    if provider_name == "deepseek":
        return providers.get("deepseek", {}).get("model", "deepseek-v4-pro")
    if provider_name == "openrouter":
        return model_key
    return model_key


def resolve_provider(model_key: str, token_count: int = 0) -> tuple[str, int]:
    """Resolve the provider for a given model and token count.

    Args:
        model_key: haiku, sonnet, or opus.
        token_count: Current token count.

    Returns:
        Tuple of (provider_name, token_count).
    """
    smart_switch = config.get("routing", {}).get("smart_switch", {})
    threshold = config.get("routing", {}).get("context_threshold", 165000)

    if smart_switch.get("enabled", False):
        target_models = smart_switch.get("target_models", [])
        if token_count > threshold and model_key in target_models:
            target = smart_switch.get("target_provider", "deepseek")
            logger.info(f"Smart switch: {token_count} tokens > {threshold} -> {target}")
            return target, token_count

    routing = config.get("routing", {}).get("models", {})
    provider_name = routing.get(model_key, routing.get("sonnet", "minimax"))
    return provider_name, token_count


def handle_message(request_body: dict[str, Any], headers: dict[str, str]) -> tuple:
    """Route a message to the appropriate provider.

    Args:
        request_body: Anthropic request body.
        headers: Request headers.

    Returns:
        Tuple of (response, provider_name).

    Raises:
        Exception: On provider failure.
    """
    model = request_body.get("model", "sonnet")
    model_lower = model.lower()

    if "haiku" in model_lower:
        model_key = "haiku"
    elif "opus" in model_lower:
        model_key = "opus"
    else:
        model_key = "sonnet"

    token_count = count_messages(request_body.get("messages", []))

    provider_name, tc = resolve_provider(model_key, token_count)
    logger.info(f"Routing {model_key} ({model}) -> {provider_name} [{tc} tokens]")

    failover_enabled = config.get("failover", {}).get("enabled", False)

    if failover_enabled and not circuit_breaker.is_available(provider_name):
        logger.warning(f"{provider_name} circuit open, failing over to openrouter")
        provider_name = "openrouter"

    model_display = _get_model_display_name(provider_name, model_key)
    context_limit = _get_context_limit(provider_name)
    tracker.record(model_key, provider_name, model_display, token_count, context_limit)

    try:
        provider = get_provider(provider_name, config.get("providers", {}))
        resp = provider.send(request_body, headers)
        if failover_enabled:
            circuit_breaker.record_success(provider_name)
        return resp, provider_name
    except Exception as e:
        if not failover_enabled:
            raise

        circuit_breaker.record_failure(provider_name)
        logger.warning(f"{provider_name} failed, trying same model via openrouter: {e}")
        try:
            provider = get_provider("openrouter", config.get("providers", {}))
            return provider.send(request_body, headers), "openrouter"
        except Exception as fallback_err:
            logger.error(f"Failover also failed: {fallback_err}")
            raise
