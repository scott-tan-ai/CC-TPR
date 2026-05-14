"""ZAI provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import requests

from .base import BaseProvider

if TYPE_CHECKING:
    pass


class ZAIProvider(BaseProvider):
    """ZAI provider for GLM-5.1 model."""

    def __init__(self, config: dict) -> None:
        """Initialize ZAI provider.

        Args:
            config: Provider configuration with base_url, models dict, timeout.
        """
        super().__init__(config)
        self.api_key: str = os.getenv("ZAI_API_KEY") or ""
        self.models: dict = config.get("models", {})

    def _resolve_model(self, model_key: str) -> str:
        """Resolve model key to actual model name.

        Args:
            model_key: haiku or opus.

        Returns:
            Model name string.
        """
        return self.models.get(model_key, "glm-5.1")

    def send(self, request_body: dict, headers: dict) -> requests.Response:
        """Send request to ZAI API.

        Args:
            request_body: Anthropic request body.
            headers: Request headers.

        Returns:
            Response from ZAI API.
        """
        model_key = request_body.get("_model_key", "haiku")
        glm_model = self._resolve_model(model_key)
        url = f"{self.base_url}/v1/messages"
        body = {**request_body, "model": glm_model}
        for key in ("_model_key", "metadata", "output_config"):
            body.pop(key, None)

        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key or "",
                "anthropic-version": "2023-06-01",
            },
            json=body,
            timeout=self.timeout,
            stream=body.get("stream", False),
        )
        resp.raise_for_status()
        return resp
