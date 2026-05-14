"""MiniMax provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import requests

from .base import BaseProvider

if TYPE_CHECKING:
    pass


class MiniMaxProvider(BaseProvider):
    """MiniMax provider for M2.7 model."""

    def __init__(self, config: dict) -> None:
        """Initialize MiniMax provider.

        Args:
            config: Provider configuration with base_url, model, timeout.
        """
        super().__init__(config)
        self.api_key: str | None = os.getenv("MINIMAX_API_KEY")
        self.model: str = config.get("model", "MiniMax-M2.7")

    def send(self, request_body: dict, headers: dict) -> requests.Response:
        """Send request to MiniMax API.

        Args:
            request_body: Anthropic request body.
            headers: Request headers.

        Returns:
            Response from MiniMax API.
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
