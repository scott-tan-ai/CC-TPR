"""Tests for router logic."""

from __future__ import annotations

from src.router import resolve_provider


class TestResolveProvider:
    """Tests for provider resolution."""

    def test_haiku_routes_to_minimax(self):
        """Haiku should route to minimax."""
        provider, tokens = resolve_provider("haiku", 1000)
        assert provider == "minimax"

    def test_sonnet_routes_to_minimax(self):
        """Sonnet should route to minimax."""
        provider, tokens = resolve_provider("sonnet", 1000)
        assert provider == "minimax"

    def test_opus_routes_to_zai(self):
        """Opus should route to zai."""
        provider, tokens = resolve_provider("opus", 1000)
        assert provider == "zai"

    def test_sonnet_over_threshold_routes_to_deepseek(self):
        """Sonnet over 165k threshold should route to deepseek."""
        provider, tokens = resolve_provider("sonnet", 170000)
        assert provider == "deepseek"

    def test_opus_over_threshold_routes_to_deepseek(self):
        """Opus over 165k threshold should route to deepseek."""
        provider, tokens = resolve_provider("opus", 170000)
        assert provider == "deepseek"

    def test_haiku_never_smart_switches(self):
        """Haiku should never trigger smart switch."""
        provider, tokens = resolve_provider("haiku", 500000)
        assert provider == "minimax"

    def test_exact_threshold_does_not_trigger(self):
        """Exact threshold (165000) should not trigger smart switch."""
        provider, tokens = resolve_provider("sonnet", 165000)
        assert provider == "minimax"

    def test_token_count_passed_through(self):
        """Token count should be returned unchanged."""
        provider, tokens = resolve_provider("sonnet", 123456)
        assert tokens == 123456
