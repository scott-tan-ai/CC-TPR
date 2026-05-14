"""DeepSeek provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import requests

from .base import BaseProvider

if TYPE_CHECKING:
    pass


class DeepSeekProvider(BaseProvider):
    """DeepSeek provider for V4 Pro model (1M context)."""

    def __init__(self, config: dict) -> None:
        """Initialize DeepSeek provider.

        Args:
            config: Provider configuration with base_url, model, timeout.
        """
        super().__init__(config)
        self.api_key: str | None = os.getenv("DEEPSEEK_API_KEY")
        self.model: str = config.get("model", "deepseek-v4-pro")

    def send(self, request_body: dict, headers: dict) -> requests.Response:
        """Send request to DeepSeek API.

        Args:
            request_body: Anthropic request body.
            headers: Request headers.

        Returns:
            Response from DeepSeek API.
        """
        url = f"{self.base_url}/v1/messages"
        body = {**request_body, "model": self.model}
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
        """Send non-streaming request to DeepSeek API.

        Args:
            request_body: Anthropic request body.

        Returns:
            Parsed JSON response.
        """
        url = f"{self.base_url}/v1/messages"
        body = {**request_body, "model": self.model, "stream": False}
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
