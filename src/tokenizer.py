"""Token counting for request size estimation."""

from __future__ import annotations

import tiktoken

_encoding = None


def _get_encoding():
    """Get or create the cl100k_base encoding singleton."""
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding("cl100k_base")
    return _encoding


def count_messages(messages: list[dict]) -> int:
    """Estimate token count for a messages array.

    Args:
        messages: List of message dicts with role and content.

    Returns:
        Estimated token count.
    """
    enc = _get_encoding()
    total = 0
    for msg in messages:
        total += 4
        total += len(enc.encode(msg.get("role", "")))

        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(enc.encode(content))
        elif isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    total += len(enc.encode(block.get("text", "")))
                elif block.get("type") == "image":
                    total += 85

    total += 2
    return total


def count_text(text: str) -> int:
    """Count tokens in a text string.

    Args:
        text: Text to count.

    Returns:
        Token count.
    """
    enc = _get_encoding()
    return len(enc.encode(text))
