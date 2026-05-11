"""Provider implementations for CC-TPR."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseProvider
from .deepseek import DeepSeekProvider
from .minimax import MiniMaxProvider
from .openrouter import OpenRouterProvider
from .zai import ZAIProvider

if TYPE_CHECKING:
    pass


def get_provider(name: str, providers_config: dict) -> BaseProvider:
    """Factory function to get a provider by name.

    Args:
        name: Provider name (minimax, zai, deepseek, openrouter).
        providers_config: Full providers config dict from config.yaml.

    Returns:
        Provider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    if name == "minimax":
        cfg = {**providers_config["minimax"], "name": "minimax"}
        return MiniMaxProvider(cfg)
    if name == "zai":
        cfg = {**providers_config["zai"], "name": "zai"}
        return ZAIProvider(cfg)
    if name == "deepseek":
        cfg = {**providers_config["deepseek"], "name": "deepseek"}
        return DeepSeekProvider(cfg)
    if name == "openrouter":
        cfg = {**providers_config["openrouter"], "name": "openrouter"}
        return OpenRouterProvider(cfg)
    raise ValueError(f"Unknown provider: {name}")


__all__ = [
    "MiniMaxProvider",
    "ZAIProvider",
    "DeepSeekProvider",
    "OpenRouterProvider",
    "get_provider",
]
