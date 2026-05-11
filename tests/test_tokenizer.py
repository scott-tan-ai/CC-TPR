"""Tests for tokenizer."""

from __future__ import annotations

from src.tokenizer import count_messages, count_text


class TestCountText:
    """Tests for simple text counting."""

    def test_empty_string(self):
        """Empty string should return 0."""
        assert count_text("") == 0

    def test_simple_text(self):
        """Simple text should return reasonable count."""
        result = count_text("hello world")
        assert result > 0

    def test_longer_text(self):
        """Longer text should have proportionally more tokens."""
        short = count_text("hello")
        long = count_text("hello world this is a longer sentence")
        assert long > short


class TestCountMessages:
    """Tests for message counting."""

    def test_empty_messages(self):
        """Empty list should return minimal count."""
        result = count_messages([])
        assert result >= 2

    def test_single_user_message(self):
        """Single user message should be counted."""
        messages = [{"role": "user", "content": "hello"}]
        result = count_messages(messages)
        assert result > 0

    def test_multiple_messages(self):
        """Multiple messages should have higher count."""
        single = count_messages([{"role": "user", "content": "hello"}])
        multiple = count_messages(
            [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi there"},
            ]
        )
        assert multiple > single

    def test_content_list_with_text_block(self):
        """Content list with text block should be counted."""
        messages = [{"role": "user", "content": [{"type": "text", "text": "hello"}]}]
        result = count_messages(messages)
        assert result > 0

    def test_role_only_message(self):
        """Message with no content should still count role."""
        messages = [{"role": "system", "content": ""}]
        result = count_messages(messages)
        assert result > 0
