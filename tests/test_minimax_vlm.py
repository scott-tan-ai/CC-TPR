"""Tests for MiniMax provider image stripping."""

from __future__ import annotations

from unittest.mock import patch

from src.providers.minimax import MiniMaxProvider


def make_provider():
    """Create a MiniMaxProvider with test config."""
    cfg = {"base_url": "https://api.minimax.io/anthropic", "model": "MiniMax-M2.7", "timeout": 180}
    return MiniMaxProvider(cfg)


class TestStripImages:
    """Tests for _strip_images static method."""

    def test_no_images_returns_same_content(self):
        """Request without images should pass through unchanged."""
        provider = make_provider()
        body = {
            "messages": [
                {"role": "user", "content": "hello"}
            ]
        }
        result = provider._strip_images(body)
        assert result["messages"][0]["content"] == "hello"

    def test_strips_image_blocks(self):
        """Image blocks should be removed from content list."""
        provider = make_provider()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "describe this"},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": "abc123",
                            },
                        },
                    ],
                }
            ]
        }
        result = provider._strip_images(body)
        content = result["messages"][0]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "describe this"

    def test_preserves_text_blocks(self):
        """Text blocks should be preserved."""
        provider = make_provider()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "line one"},
                        {"type": "text", "text": "line two"},
                    ],
                }
            ]
        }
        result = provider._strip_images(body)
        assert len(result["messages"][0]["content"]) == 2

    def test_string_content_untouched(self):
        """String content (not list) should pass through."""
        provider = make_provider()
        body = {
            "messages": [
                {"role": "user", "content": "plain string"}
            ]
        }
        result = provider._strip_images(body)
        assert result["messages"][0]["content"] == "plain string"

    def test_does_not_mutate_original(self):
        """Should return a new dict, not modify original."""
        provider = make_provider()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "hello"},
                        {"type": "image", "source": {"type": "base64", "data": "abc"}},
                    ],
                }
            ]
        }
        result = provider._strip_images(body)
        assert len(body["messages"][0]["content"]) == 2
        assert len(result["messages"][0]["content"]) == 1

    def test_multiple_messages_strips_from_all(self):
        """Should strip images from all messages."""
        provider = make_provider()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "data": "abc"}},
                        {"type": "text", "text": "first"},
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "reply"},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "second"},
                        {"type": "image", "source": {"type": "base64", "data": "def"}},
                    ],
                },
            ]
        }
        result = provider._strip_images(body)
        assert len(result["messages"][0]["content"]) == 1
        assert len(result["messages"][1]["content"]) == 1
        assert len(result["messages"][2]["content"]) == 1

    def test_empty_content_list(self):
        """Empty content list should pass through."""
        provider = make_provider()
        body = {
            "messages": [
                {"role": "user", "content": []}
            ]
        }
        result = provider._strip_images(body)
        assert result["messages"][0]["content"] == []


class TestSend:
    """Tests for send method."""

    @patch("src.providers.minimax.requests.post")
    def test_strips_images_before_sending(self, mock_post):
        """send() should strip image blocks before posting to API."""
        mock_post.return_value.status_code = 200
        mock_post.return_value._content = b'{"type": "message", "id": "test"}'

        provider = make_provider()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "describe"},
                        {"type": "image", "source": {"type": "base64", "data": "abc"}},
                    ],
                }
            ]
        }
        provider.send(body, {})

        sent_body = mock_post.call_args[1]["json"]
        assert len(sent_body["messages"][0]["content"]) == 1
        assert sent_body["messages"][0]["content"][0]["type"] == "text"

    @patch("src.providers.minimax.requests.post")
    def test_text_only_unchanged(self, mock_post):
        """Text-only request should pass through unchanged."""
        mock_post.return_value.status_code = 200
        mock_post.return_value._content = b'{"type": "message", "id": "test"}'

        provider = make_provider()
        body = {
            "messages": [
                {"role": "user", "content": "hello"}
            ]
        }
        provider.send(body, {})

        sent_body = mock_post.call_args[1]["json"]
        assert sent_body["messages"][0]["content"] == "hello"
