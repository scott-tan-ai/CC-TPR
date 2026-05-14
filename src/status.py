"""Status tracker for router state."""

from __future__ import annotations

import threading
from datetime import datetime


class StatusTracker:
    """Thread-safe singleton for tracking last request state.

    Uses internal flag to decide what to update:
    - Internal requests (haiku/sonnet pings under 4000 tokens): nothing updated
      except last_request_model and total_requests, so they don't overwrite
      real user display state or token count
    - Non-internal requests (user-initiated): all fields updated unconditionally
      since user explicitly chose this model
    """

    def __init__(self) -> None:
        """Initialize tracker."""
        self._lock = threading.Lock()
        self.last_request_model: str | None = None
        self.last_model: str | None = None
        self.last_provider: str | None = None
        self.last_token_count: int = 0
        self.last_context_limit: int = 200000
        self.last_model_key: str | None = None
        self.last_request_time: str | None = None
        self.total_requests: int = 0

    def record(
        self,
        request_model: str,
        model_key: str,
        provider_name: str,
        model_name: str,
        token_count: int,
        context_limit: int,
        internal: bool = False,
    ) -> None:
        """Record a request's routing outcome.

        Args:
            request_model: Raw request model string (e.g. "claude-sonnet-4-5").
            model_key: haiku, sonnet, or opus.
            provider_name: Actual provider used.
            model_name: Model name shown in status.
            token_count: Token count for this request.
            context_limit: Context limit of the provider.
            internal: True for internal haiku/sonnet pings (skip display update).
        """
        with self._lock:
            self.last_request_model = request_model
            if internal:
                pass
            else:
                self.last_model_key = model_key
                self.last_provider = provider_name
                self.last_model = model_name
                self.last_token_count = token_count
                self.last_context_limit = context_limit
                self.last_request_time = datetime.now().isoformat()
            self.total_requests += 1

    def snapshot(self) -> dict:
        """Get current state snapshot.

        Returns:
            Dictionary with current state.
        """
        with self._lock:
            pct = 0.0
            if self.last_context_limit > 0 and self.last_token_count > 0:
                pct = round(self.last_token_count / self.last_context_limit * 100, 1)
            return {
                "model": self.last_model,
                "provider": self.last_provider,
                "model_key": self.last_model_key,
                "request_model": self.last_request_model,
                "tokens": self.last_token_count,
                "context_limit": self.last_context_limit,
                "usage_pct": pct,
                "total_requests": self.total_requests,
                "last_request": self.last_request_time,
            }


tracker = StatusTracker()
