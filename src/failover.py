"""Circuit breaker pattern for provider failover."""

from __future__ import annotations

from datetime import datetime, timedelta

from .utils.config import load_config
from .utils.logger import setup_logger

logger = setup_logger()
config = load_config()

circuit_breaker_cooldown_seconds: int = config.get("failover", {}).get("429_cooldown_seconds", 60)


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures when a provider is down.

    After a provider experiences too many failures, it enters a cooldown period.
    During cooldown, requests to that provider are automatically routed to fallback.
    """

    def __init__(self, threshold: int = 3, cooldown_minutes: int = 2) -> None:
        """Initialize circuit breaker.

        Args:
            threshold: Number of failures before opening circuit.
            cooldown_minutes: Minutes to wait before allowing retry.
        """
        self.threshold = threshold
        self.cooldown = timedelta(minutes=cooldown_minutes)
        self.failures: dict[str, int] = {}
        self.last_failure: dict[str, datetime] = {}

    def is_available(self, provider: str) -> bool:
        """Check if a provider is available (circuit not open).

        Args:
            provider: Provider name.

        Returns:
            True if provider can be used, False if circuit is open.
        """
        if provider not in self.failures or self.failures[provider] < self.threshold:
            return True

        elapsed = datetime.now() - self.last_failure.get(provider, datetime.min)
        if elapsed >= self.cooldown:
            logger.info(f"Circuit breaker reset for {provider}")
            self.reset(provider)
            return True

        remaining = self.cooldown - elapsed
        logger.warning(f"Circuit open for {provider}, {remaining.seconds // 60}m remaining")
        return False

    def record_failure(self, provider: str) -> None:
        """Record a failure for a provider.

        Args:
            provider: Provider name.
        """
        self.failures[provider] = self.failures.get(provider, 0) + 1
        self.last_failure[provider] = datetime.now()
        logger.warning(f"Failure #{self.failures[provider]} for {provider}")

    def record_success(self, provider: str) -> None:
        """Record a success, resetting the circuit breaker.

        Args:
            provider: Provider name.
        """
        self.reset(provider)

    def reset(self, provider: str) -> None:
        """Manually reset circuit breaker for a provider.

        Args:
            provider: Provider name.
        """
        self.failures.pop(provider, None)
        self.last_failure.pop(provider, None)

    # 429 rate-limit tracking (independent of circuit breaker)
    _last_429: dict[str, datetime] = {}

    def is_in_429_cooldown(self, provider: str) -> bool:
        if provider not in self._last_429:
            return False
        elapsed = datetime.now() - self._last_429[provider]
        if elapsed.total_seconds() >= circuit_breaker_cooldown_seconds:
            self._last_429.pop(provider, None)
            return False
        return True

    def record_429(self, provider: str) -> None:
        self._last_429[provider] = datetime.now()
        logger.warning(f"429 cooldown recorded for {provider}, skipping for {circuit_breaker_cooldown_seconds}s")

    def clear_429_cooldown(self, provider: str) -> None:
        self._last_429.pop(provider, None)

    def status(self) -> dict:
        """Get circuit breaker status for all providers.

        Returns:
            Dictionary mapping provider name to status dict.
        """
        result = {}
        for name, count in self.failures.items():
            last_failure_time = self.last_failure.get(name)
            if last_failure_time:
                last_failure_str = last_failure_time.isoformat()
            else:
                last_failure_str = None
            result[name] = {
                "failures": count,
                "open": count >= self.threshold,
                "last_failure": last_failure_str,
            }
        return result
