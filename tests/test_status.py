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
        assert snap["request_model"] is None

    def test_record_updates_state(self):
        """Record should update tracker state."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 50000, 200000)
        snap = tracker.snapshot()
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["provider"] == "minimax"
        assert snap["model_key"] == "sonnet"
        assert snap["request_model"] == "claude-sonnet"
        assert snap["tokens"] == 50000

    def test_usage_percentage_calculation(self):
        """Usage percentage should be calculated correctly."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 50000, 200000)
        snap = tracker.snapshot()
        assert snap["usage_pct"] == 25.0

    def test_usage_percentage_rounds(self):
        """Usage percentage should be rounded to 1 decimal."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 33333, 100000)
        snap = tracker.snapshot()
        assert snap["usage_pct"] == 33.3

    def test_total_requests_increments(self):
        """Total requests should increment on each record."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 1000, 200000)
        tracker.record("claude-haiku", "haiku", "zai", "glm-5.1", 2000, 200000)
        snap = tracker.snapshot()
        assert snap["total_requests"] == 2

    def test_request_time_is_set(self):
        """Last request time should be set after record."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 1000, 200000)
        snap = tracker.snapshot()
        assert snap["last_request"] is not None
        assert "T" in snap["last_request"]

    def test_request_model_always_updated(self):
        """last_request_model should be updated on every record call."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 1000, 200000)
        tracker.record("claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 500, 200000)
        snap = tracker.snapshot()
        assert snap["request_model"] == "claude-haiku"

    def test_internal_haiku_does_not_update_display(self):
        """Internal haiku ping does not update any display fields or tokens."""
        tracker = StatusTracker()
        tracker.record("claude-opus", "opus", "zai", "GLM-5.1", 10000, 200000)
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 500, 200000, internal=True
        )
        snap = tracker.snapshot()
        assert snap["model"] == "GLM-5.1"
        assert snap["provider"] == "zai"
        assert snap["model_key"] == "opus"
        assert snap["tokens"] == 10000
        assert snap["total_requests"] == 2
        assert snap["request_model"] == "claude-haiku"

    def test_internal_sonnet_does_not_update_display(self):
        """Internal sonnet ping does not update any display fields or tokens."""
        tracker = StatusTracker()
        tracker.record("claude-opus", "opus", "zai", "GLM-5.1", 10000, 200000)
        tracker.record(
            "claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 500, 200000, internal=True
        )
        snap = tracker.snapshot()
        assert snap["model"] == "GLM-5.1"
        assert snap["provider"] == "zai"
        assert snap["model_key"] == "opus"
        assert snap["tokens"] == 10000
        assert snap["total_requests"] == 2

    def test_user_haiku_overwrites_opus(self):
        """Non-internal haiku (user switched model) overwrites opus display."""
        tracker = StatusTracker()
        tracker.record("claude-opus", "opus", "zai", "GLM-5.1", 10000, 200000)
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 11000, 200000, internal=False
        )
        snap = tracker.snapshot()
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["provider"] == "minimax"
        assert snap["model_key"] == "haiku"

    def test_user_opus_overwrites_haiku(self):
        """Non-internal opus (user switched model) overwrites haiku display."""
        tracker = StatusTracker()
        tracker.record("claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 10000, 200000)
        tracker.record("claude-opus", "opus", "zai", "GLM-5.1", 11000, 200000, internal=False)
        snap = tracker.snapshot()
        assert snap["model"] == "GLM-5.1"
        assert snap["provider"] == "zai"
        assert snap["model_key"] == "opus"

    def test_user_sonnet_overwrites_haiku(self):
        """Non-internal sonnet overwrites haiku display."""
        tracker = StatusTracker()
        tracker.record("claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 10000, 200000)
        tracker.record(
            "claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 11000, 200000, internal=False
        )
        snap = tracker.snapshot()
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["model_key"] == "sonnet"

    def test_multiple_internal_pings_do_not_update_tokens(self):
        """Multiple internal pings do not update token count."""
        tracker = StatusTracker()
        tracker.record("claude-sonnet", "sonnet", "minimax", "MiniMax-M2.7", 50000, 200000)
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 500, 200000, internal=True
        )
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 600, 200000, internal=True
        )
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 700, 200000, internal=True
        )
        snap = tracker.snapshot()
        assert snap["tokens"] == 50000
        assert snap["total_requests"] == 4
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["model_key"] == "sonnet"

    def test_first_request_is_non_internal(self):
        """First non-internal request always does full update."""
        tracker = StatusTracker()
        tracker.record(
            "claude-haiku", "haiku", "minimax", "MiniMax-M2.7", 500, 200000, internal=False
        )
        snap = tracker.snapshot()
        assert snap["model"] == "MiniMax-M2.7"
        assert snap["provider"] == "minimax"
        assert snap["model_key"] == "haiku"
        assert snap["tokens"] == 500
