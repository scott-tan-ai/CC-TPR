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
