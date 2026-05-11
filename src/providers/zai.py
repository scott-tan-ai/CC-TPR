"""ZAI provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import requests

from .base import BaseProvider

if TYPE_CHECKING:
    pass


class ZAIProvider(BaseProvider):
    """ZAI provider for GLM-4.7 and GLM-5.1 models."""

    def __init__(self, config: dict) -> None:
        """Initialize ZAI provider.

        Args:
            config: Provider configuration with base_url, models dict, timeout.
        """
        super().__init__(config)
        self.api_key: str | None = os.getenv("ZAI_API_KEY")
        self.models: dict = config.get("models", {})

    def _resolve_model(self, model_key: str) -> str:
        """Resolve model key to actual model name.

        Args:
            model_key: haiku or opus.

        Returns:
            Model name string.
        """
        return self.models.get(model_key, "glm-4.7")

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
        body.pop("_model_key", None)

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
