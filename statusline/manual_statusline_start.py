#!/usr/bin/env python3
"""
CC-TPR Manual Status Line

Run this script in a terminal (Zed, iTerm, Terminal.app, cmd, PowerShell)
to see real-time CC-TPR routing status.

Usage:
    python statusline/manual_statusline_start.py

Requires:
    - CC-TPR router running on 127.0.0.1:3456
    - Python 3.12+

Exit: Ctrl+C
"""
import json
import os
import sys
import time
import urllib.request

ROUTER_URL = "http://127.0.0.1:3456"
_TOKEN_FILE = os.path.join(os.path.expanduser("~/.claude"), ".cc_tpr_tokens")

GREEN = "\033[32m"
ORANGE = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


def _get_cached_tokens():
    try:
        if os.path.exists(_TOKEN_FILE):
            with open(_TOKEN_FILE) as f:
                ctx_limit, tokens = f.read().strip().split(",")
                return int(ctx_limit), int(tokens)
    except Exception:
        pass
    return 0, 0


def _save_tokens(ctx_limit, tokens):
    try:
        claude_dir = os.path.expanduser("~/.claude")
        os.makedirs(claude_dir, exist_ok=True)
        with open(_TOKEN_FILE, "w") as f:
            f.write(f"{ctx_limit},{tokens}")
    except Exception:
        pass


def fetch_json(path):
    try:
        req = urllib.request.urlopen(f"{ROUTER_URL}{path}", timeout=2)
        return json.loads(req.read().decode())
    except Exception:
        return None


def render_bar(pct, width=10):
    filled = int(pct / 100 * width)
    empty = width - filled
    if pct >= 80:
        color = RED
    elif pct >= 70:
        color = ORANGE
    else:
        color = GREEN
    return color + ("#" * filled) + DIM + ("." * empty) + RESET


def fmt_countdown_ms(ms):
    if ms is None or ms <= 0:
        return None
    total_sec = ms / 1000
    hours = int(total_sec // 3600)
    minutes = int((total_sec % 3600) // 60)
    if hours >= 24:
        days = hours // 24
        rem_hours = hours % 24
        return f"{days}d{rem_hours:02d}h"
    return f"{hours}h{minutes:02d}m"


def get_pct_color(pct):
    if pct >= 80:
        return RED
    elif pct >= 70:
        return ORANGE
    return GREEN


def build_quota_segment(quota_data):
    if not quota_data:
        return ""

    hr5_pct = quota_data.get("5hr_pct", 0)
    hr5_reset_ms = quota_data.get("5hr_reset_ms")
    weekly_pct = quota_data.get("weekly_pct", 0)
    weekly_reset_ms = quota_data.get("weekly_reset_ms")

    parts = []

    hr5_bar = render_bar(hr5_pct, width=8)
    hr5_color = get_pct_color(hr5_pct)
    hr5_text = f"{hr5_bar} {hr5_color}{hr5_pct:.0f}%{RESET}"
    if hr5_pct > 0 and hr5_reset_ms is not None:
        cd = fmt_countdown_ms(hr5_reset_ms)
        if cd:
            hr5_text += f" \033[90m{cd}{RESET}"
    parts.append(hr5_text)

    if weekly_pct is not None:
        wk_bar = render_bar(weekly_pct, width=8)
        wk_color = get_pct_color(weekly_pct)
        wk_text = f"{wk_bar} {wk_color}{weekly_pct:.0f}%{RESET}"
        if weekly_reset_ms is not None:
            cd = fmt_countdown_ms(weekly_reset_ms)
            if cd:
                wk_text += f" \033[90m{cd}{RESET}"
        parts.append(wk_text)

    return " | ".join(parts)


def get_project_name():
    cwd = os.getcwd()
    return os.path.basename(cwd) or "cc-tpr"


def build_status_line(status_data, quota_data):
    provider = status_data.get("provider")
    ctx_limit = status_data.get("context_limit", 0)
    tokens = status_data.get("tokens", 0)
    model_key = status_data.get("model_key", "sonnet")

    if provider == "deepseek":
        model = "deepseek-v4-pro"
    elif model_key == "haiku":
        model = "MiniMax-M2.7"
    elif model_key == "sonnet":
        model = "MiniMax-M2.7"
    elif model_key == "opus":
        model = "GLM-5.1"
    else:
        model = model_key

    project = get_project_name()

    if ctx_limit and tokens:
        pct = round(tokens / ctx_limit * 100, 1)
    else:
        pct = 0.0

    ctx_bar = render_bar(pct)
    pct_color = get_pct_color(pct)
    if ctx_limit:
        ctx_str = f"{ctx_bar} {pct_color}{pct:.0f}%{RESET} ({ctx_limit // 1000:,}k)"
    else:
        ctx_str = f"{ctx_bar} {pct_color}{pct:.0f}%{RESET}"

    parts = [f"{project} | {model} | {ctx_str}"]

    if quota_data and provider:
        provider_quota = quota_data.get(provider)
        if provider_quota:
            quota_seg = build_quota_segment(provider_quota)
            if quota_seg:
                parts.append(quota_seg)

    return " | ".join(parts)


def main():
    print(f"{DIM}CC-TPR Status Line — press Ctrl+C to stop{RESET}")
    print()

    while True:
        status_data = fetch_json("/status")
        quota_data = fetch_json("/quota")

        if status_data:
            _save_tokens(status_data.get("context_limit", 0), status_data.get("tokens", 0))
            line = build_status_line(status_data, quota_data)
            print(f"\r{line}{RESET}", end="", flush=True)
        else:
            project = get_project_name()
            print(f"\r{DIM}{project}{RESET} | {DIM}waiting...{RESET}", end="", flush=True)

        sys.stdout.flush()
        time.sleep(2)


if __name__ == "__main__":
    main()
