"""Converter from Anthropic format to OpenAI format."""

from __future__ import annotations

import json
import uuid
from typing import Any


def anthropic_to_openai(body: dict[str, Any], model: str) -> dict[str, Any]:
    """Convert Anthropic request body to OpenAI format.

    Note: This converter is kept for reference. Currently all providers
    use Anthropic format directly.

    Args:
        body: Anthropic request body.
        model: OpenAI model name.

    Returns:
        OpenAI format request body.
    """
    messages = []

    if body.get("system"):
        system = body["system"]
        if isinstance(system, str):
            messages.append({"role": "system", "content": system})
        elif isinstance(system, list):
            text = " ".join(b.get("text", "") for b in system if b.get("type") == "text")
            messages.append({"role": "system", "content": text})

    for msg in body.get("messages", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if isinstance(content, str):
            messages.append({"role": role, "content": content})
        elif isinstance(content, list):
            parts = []
            tool_use_blocks = []
            for block in content:
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    tool_id = block.get("tool_use_id", "")
                    result_content = block.get("content", "")
                    if isinstance(result_content, list):
                        result_content = " ".join(
                            b.get("text", "") for b in result_content if b.get("type") == "text"
                        )
                    parts.append(f"[Tool Result {tool_id}]: {result_content}")
                elif block.get("type") == "tool_use":
                    tool_use_blocks.append(block)

            if parts:
                messages.append({"role": role, "content": "\n".join(parts)})

            for tb in tool_use_blocks:
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tb.get("id", f"call_{uuid.uuid4().hex[:8]}"),
                                "type": "function",
                                "function": {
                                    "name": tb.get("name", ""),
                                    "arguments": json.dumps(tb.get("input", {})),
                                },
                            }
                        ],
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tb["tool_calls"][0]["id"]
                        if tool_use_blocks
                        else tb.get("id", ""),
                        "content": "",
                    }
                )

    openai_body = {
        "model": model,
        "messages": messages,
        "stream": body.get("stream", False),
    }

    if body.get("max_tokens"):
        openai_body["max_tokens"] = body["max_tokens"]
    if body.get("temperature") is not None:
        openai_body["temperature"] = body["temperature"]
    if body.get("tools"):
        openai_body["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {}),
                },
            }
            for t in body["tools"]
        ]

    return openai_body
