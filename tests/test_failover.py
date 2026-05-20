"""Tests for circuit breaker."""

from __future__ import annotations

from src.failover import CircuitBreaker


class TestCircuitBreaker:
    """Tests for circuit breaker functionality."""

    def test_initial_state_available(self):
        """New provider should be available."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        assert cb.is_available("testprovider") is True

    def test_success_resets_failures(self):
        """Success should reset failure count."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_failure("testprovider")
        cb.record_failure("testprovider")
        cb.record_success("testprovider")
        assert cb.is_available("testprovider") is True
        assert cb.failures.get("testprovider") is None

    def test_threshold_opens_circuit(self):
        """Reaching threshold should open circuit."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_failure("testprovider")
        cb.record_failure("testprovider")
        cb.record_failure("testprovider")
        assert cb.is_available("testprovider") is False

    def test_below_threshold_still_available(self):
        """Failures below threshold should not open circuit."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_failure("testprovider")
        cb.record_failure("testprovider")
        assert cb.is_available("testprovider") is True

    def test_status_returns_all_providers(self):
        """Status should return all tracked providers."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_failure("provider1")
        cb.record_failure("provider2")
        status = cb.status()
        assert "provider1" in status
        assert "provider2" in status

    def test_status_open_is_true_when_threshold_reached(self):
        """Status open should be True after threshold reached."""
        cb = CircuitBreaker(threshold=2, cooldown_minutes=2)
        cb.record_failure("testprovider")
        cb.record_failure("testprovider")
        status = cb.status()
        assert status["testprovider"]["open"] is True
        assert status["testprovider"]["failures"] == 2


class Test429Cooldown:
    """Tests for 429 rate-limit cooldown."""

    def test_initial_no_429_cooldown(self):
        """New provider should not be in 429 cooldown."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        assert cb.is_in_429_cooldown("zai") is False

    def test_record_429_sets_cooldown(self):
        """Recording a 429 should set cooldown."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_429("zai")
        assert cb.is_in_429_cooldown("zai") is True

    def test_clear_429_removes_cooldown(self):
        """Clearing 429 cooldown should remove it."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_429("zai")
        cb.clear_429_cooldown("zai")
        assert cb.is_in_429_cooldown("zai") is False

    def test_different_providers_independent(self):
        """429 cooldown should be independent per provider."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        cb.record_429("zai")
        assert cb.is_in_429_cooldown("zai") is True
        assert cb.is_in_429_cooldown("openrouter") is False

    def test_cooldown_expires_after_seconds(self, monkeypatch):
        """Cooldown should expire after configured seconds."""
        cb = CircuitBreaker(threshold=3, cooldown_minutes=2)
        from datetime import datetime, timedelta
        past_time = datetime(2026, 5, 20, 12, 0, 0) - timedelta(seconds=61)
        cb._last_429["zai"] = past_time

        assert cb.is_in_429_cooldown("zai") is False
