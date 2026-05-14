"""OpenRouter provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import requests

from .base import BaseProvider

if TYPE_CHECKING:
    pass


FALLBACK_MODELS: dict[str, str] = {
    "haiku": "z-ai/glm-5.1",
    "sonnet": "minimax/minimax-m2.7",
    "opus": "z-ai/glm-5.1",
}


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider for fallback routing."""

    def __init__(self, config: dict) -> None:
        """Initialize OpenRouter provider.

        Args:
            config: Provider configuration with base_url, model, timeout.
        """
        super().__init__(config)
        self.api_key: str | None = os.getenv("OPENROUTER_API_KEY")
        self.default_model: str = config.get("model", "deepseek/deepseek-chat")

    def _resolve_model(self, model_key: str) -> str:
        """Resolve model key to OpenRouter model identifier.

        Args:
            model_key: haiku, sonnet, or opus.

        Returns:
            OpenRouter model identifier.
        """
        return FALLBACK_MODELS.get(model_key, self.default_model)

    def send(self, request_body: dict, headers: dict) -> requests.Response:
        """Send request to OpenRouter API.

        Args:
            request_body: Anthropic request body.
            headers: Request headers.

        Returns:
            Response from OpenRouter API.
        """
        model_key = request_body.get("_model_key", "sonnet")
        model = self._resolve_model(model_key)
        url = f"{self.base_url}/v1/messages"
        body = {**request_body, "model": model}
        for key in ("_model_key", "metadata", "output_config"):
            body.pop(key, None)

        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            json=body,
            timeout=self.timeout,
            stream=body.get("stream", False),
        )
        resp.raise_for_status()
        return resp

    def send_non_stream(self, request_body: dict) -> dict:
        """Send non-streaming request to OpenRouter API.

        Args:
            request_body: Anthropic request body.

        Returns:
            Parsed JSON response.
        """
        model_key = request_body.get("_model_key", "sonnet")
        model = self._resolve_model(model_key)
        url = f"{self.base_url}/v1/messages"
        body = {**request_body, "model": model, "stream": False}
        for key in ("_model_key", "metadata", "output_config"):
            body.pop(key, None)

        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
