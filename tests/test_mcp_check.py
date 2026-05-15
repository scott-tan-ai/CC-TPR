"""Tests for MiniMax MCP auto-detect and fix."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.utils.mcp_check import (
    MINIMAX_MCP_CONFIG,
    check_and_fix_all,
    fix_mcp_in_file,
    is_valid_minimax_mcp,
)


class TestIsValidMinimaxMcp:
    def test_valid_config_returns_true(self):
        config = {
            "type": "stdio",
            "command": "uvx",
            "args": ["minimax-coding-plan-mcp", "-y"],
            "env": {
                "MINIMAX_API_KEY": "${MINIMAX_API_KEY}",
                "MINIMAX_API_HOST": "https://api.minimax.io",
            },
        }
        assert is_valid_minimax_mcp(config) is True

    def test_none_returns_false(self):
        assert is_valid_minimax_mcp(None) is False

    def test_empty_returns_false(self):
        assert is_valid_minimax_mcp({}) is False

    def test_wrong_type_returns_false(self):
        config = {
            "type": "http",
            "command": "uvx",
            "args": ["minimax-coding-plan-mcp", "-y"],
            "env": {"MINIMAX_API_KEY": "${MINIMAX_API_KEY}"},
        }
        assert is_valid_minimax_mcp(config) is False

    def test_wrong_command_returns_false(self):
        config = {
            "type": "stdio",
            "command": "npx",
            "args": ["minimax-coding-plan-mcp", "-y"],
            "env": {"MINIMAX_API_KEY": "${MINIMAX_API_KEY}"},
        }
        assert is_valid_minimax_mcp(config) is False

    def test_missing_args_entry_returns_false(self):
        config = {
            "type": "stdio",
            "command": "uvx",
            "args": ["some-other-package"],
            "env": {"MINIMAX_API_KEY": "${MINIMAX_API_KEY}"},
        }
        assert is_valid_minimax_mcp(config) is False

    def test_literal_api_key_returns_false(self):
        config = {
            "type": "stdio",
            "command": "uvx",
            "args": ["minimax-coding-plan-mcp", "-y"],
            "env": {
                "MINIMAX_API_KEY": "api_key",
                "MINIMAX_API_HOST": "https://api.minimax.io",
            },
        }
        assert is_valid_minimax_mcp(config) is False

    def test_empty_args_returns_false(self):
        config = {
            "type": "stdio",
            "command": "uvx",
            "args": [],
            "env": {"MINIMAX_API_KEY": "${MINIMAX_API_KEY}"},
        }
        assert is_valid_minimax_mcp(config) is False


class TestFixMcpInFile:
    def test_ok_when_valid_config_exists(self, tmp_path: Path):
        config = {"mcpServers": {"MiniMax": MINIMAX_MCP_CONFIG.copy()}}
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "ok"

    def test_fixed_when_config_is_wrong(self, tmp_path: Path):
        config = {
            "mcpServers": {
                "MiniMax": {
                    "type": "http",
                    "url": "https://example.com",
                }
            }
        }
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "fixed"

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG

    def test_added_when_missing(self, tmp_path: Path):
        config = {"mcpServers": {}}
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "added"

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG

    def test_added_to_user_claude_json(self, tmp_path: Path):
        config = {"mcpServers": {"higgsfield": {"type": "http", "url": "https://example.com"}}}
        fp = tmp_path / ".claude.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "added"

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert "MiniMax" in data["mcpServers"]
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG

    def test_error_on_malformed_json(self, tmp_path: Path):
        fp = tmp_path / ".mcp.json"
        fp.write_text("{invalid json}", encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "error"

    def test_error_on_missing_mcpservers(self, tmp_path: Path):
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps({"some": "data"}), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "error"

    def test_error_on_mcpservers_not_dict(self, tmp_path: Path):
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps({"mcpServers": "not a dict"}), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "error"

    def test_preserves_other_mcp_servers(self, tmp_path: Path):
        config = {
            "mcpServers": {
                "higgsfield": {"type": "http", "url": "https://example.com"}
            }
        }
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "added"

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert "higgsfield" in data["mcpServers"]
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG

    def test_overwrites_broken_minimax_entry(self, tmp_path: Path):
        config = {
            "mcpServers": {
                "MiniMax": {
                    "type": "stdio",
                    "command": "uvx",
                    "args": ["minimax-coding-plan-mcp"],
                    "env": {"MINIMAX_API_KEY": "api_key"},
                }
            }
        }
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        result = fix_mcp_in_file(str(fp))
        assert result == "fixed"

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG


class TestCheckAndFixAll:
    def test_warns_when_api_key_not_set(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)

        check_and_fix_all()

    def test_no_change_when_config_valid(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        monkeypatch.setenv("MINIMAX_API_KEY", "sk-test-key")
        monkeypatch.chdir(tmp_path)

        config = {"mcpServers": {"MiniMax": MINIMAX_MCP_CONFIG.copy()}}
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        check_and_fix_all()

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG

    def test_adds_minimax_when_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        monkeypatch.setenv("MINIMAX_API_KEY", "sk-test-key")
        monkeypatch.chdir(tmp_path)

        config = {"mcpServers": {}}
        fp = tmp_path / ".mcp.json"
        fp.write_text(json.dumps(config), encoding="utf-8")

        check_and_fix_all()

        data = json.loads(fp.read_text(encoding="utf-8"))
        assert data["mcpServers"]["MiniMax"] == MINIMAX_MCP_CONFIG
