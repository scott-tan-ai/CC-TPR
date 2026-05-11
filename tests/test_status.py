"""Tests for status tracker."""

from __future__ import annotations

from src.status import StatusTracker


class TestStatusTracker:
    """Tests for status tracker."""

    def test_initial_snapshot(self):
        """Initial snapshot should have default values."""
        tracker = StatusTracker()
        snap = tracker.snapshot()
        assert snap["model"] is None
        assert snap["provider"] is None
        assert snap["tokens"] == 0

    def test_record_updates_state(self):
        """Record should update tracker state."""
        tracker = StatusTracker()
        tracker.record("sonnet", "minimax", "MiniMax-M2.7", 50000, 200000)
        snap = tracker.snapshot()
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["provider"] == "minimax"
        assert snap["model_key"] == "sonnet"
        assert snap["tokens"] == 50000

    def test_usage_percentage_calculation(self):
        """Usage percentage should be calculated correctly."""
        tracker = StatusTracker()
        tracker.record("sonnet", "minimax", "MiniMax-M2.7", 50000, 200000)
        snap = tracker.snapshot()
        assert snap["usage_pct"] == 25.0

    def test_usage_percentage_rounds(self):
        """Usage percentage should be rounded to 1 decimal."""
        tracker = StatusTracker()
        tracker.record("sonnet", "minimax", "MiniMax-M2.7", 33333, 100000)
        snap = tracker.snapshot()
        assert snap["usage_pct"] == 33.3

    def test_total_requests_increments(self):
        """Total requests should increment on each record."""
        tracker = StatusTracker()
        tracker.record("sonnet", "minimax", "MiniMax-M2.7", 1000, 200000)
        tracker.record("haiku", "zai", "glm-4.7", 2000, 200000)
        snap = tracker.snapshot()
        assert snap["total_requests"] == 2

    def test_request_time_is_set(self):
        """Last request time should be set after record."""
        tracker = StatusTracker()
        tracker.record("sonnet", "minimax", "MiniMax-M2.7", 1000, 200000)
        snap = tracker.snapshot()
        assert snap["last_request"] is not None
        assert "T" in snap["last_request"]
