"""MiniMax MCP auto-detect and fix utility."""

from __future__ import annotations

import json
import os
from pathlib import Path

MINIMAX_MCP_CONFIG = {
    "type": "stdio",
    "command": "uvx",
    "args": ["minimax-coding-plan-mcp", "-y"],
    "env": {
        "MINIMAX_API_KEY": "${MINIMAX_API_KEY}",
        "MINIMAX_API_HOST": "https://api.minimax.io",
    },
}


def is_valid_minimax_mcp(config: dict | None) -> bool:
    if not config:
        return False
    if config.get("type") != "stdio":
        return False
    if config.get("command") != "uvx":
        return False
    args = config.get("args", [])
    if not isinstance(args, list) or "minimax-coding-plan-mcp" not in args:
        return False
    env = config.get("env", {})
    if env.get("MINIMAX_API_KEY") == "api_key":
        return False
    return True


def fix_mcp_in_file(filepath: str) -> str:
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"      WARNING: Could not read {filepath}: {e}")
        return "error"

    mcp_servers = data.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        return "error"

    existing = mcp_servers.get("MiniMax")
    if is_valid_minimax_mcp(existing):
        return "ok"

    mcp_servers["MiniMax"] = MINIMAX_MCP_CONFIG.copy()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"      WARNING: Could not write {filepath}: {e}")
        return "error"

    return "fixed" if existing else "added"


def _get_mcp_paths() -> list[tuple[str, bool]]:
    paths: list[tuple[str, bool]] = []
    claude_json = Path.home() / ".claude.json"
    if claude_json.exists():
        paths.append((str(claude_json), True))

    for mcp_file in Path.cwd().rglob(".mcp.json"):
        paths.append((str(mcp_file), False))

    return paths


def check_and_fix_all() -> None:
    if not os.environ.get("MINIMAX_API_KEY"):
        print("      WARNING: MINIMAX_API_KEY env var not set - MCP will not function")

    fixed_count = 0
    added_count = 0

    for path, _is_user_level in _get_mcp_paths():
        result = fix_mcp_in_file(path)
        if result == "ok":
            pass
        elif result == "fixed":
            fixed_count += 1
        elif result == "added":
            added_count += 1

    if fixed_count > 0 or added_count > 0:
        total = fixed_count + added_count
        print(f"      MiniMax MCP: Fixed {total} file(s) ({fixed_count} corrected, {added_count} added)")
    else:
        print("      MiniMax MCP: OK")


if __name__ == "__main__":
    check_and_fix_all()
