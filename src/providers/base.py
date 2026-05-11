"""Base provider interface for CC-TPR."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    pass


class BaseProvider(ABC):
    """Abstract base class for all model providers."""

    def __init__(self, config: dict) -> None:
        """Initialize provider.

        Args:
            config: Provider configuration dictionary.
        """
        self.name: str = config.get("name", "unknown")
        self.base_url: str = config["base_url"]
        self.timeout: int = config.get("timeout", 180)

    @abstractmethod
    def send(self, request_body: dict, headers: dict) -> requests.Response:
        """Send a request to the provider.

        Args:
            request_body: Request body dictionary.
            headers: Request headers.

        Returns:
            Response object.

        Raises:
            requests.HTTPError: On HTTP error.
        """
        pass
