#!/usr/bin/env python3
import sys
import json
import os
import urllib.request

ROUTER_URL = "http://127.0.0.1:3456"
_STATUS_CACHE = {}
_LAST_MODEL_KEY = None
_TOKEN_FILE = os.path.join(os.path.expanduser("~/.claude"), ".cc_tpr_tokens")


def _get_cached_tokens() -> tuple[int, int]:
    try:
        if os.path.exists(_TOKEN_FILE):
            with open(_TOKEN_FILE) as f:
                ctx_limit, tokens = f.read().strip().split(",")
                return int(ctx_limit), int(tokens)
    except Exception:
        pass
    return 0, 0


def _save_tokens(ctx_limit: int, tokens: int) -> None:
    try:
        claude_dir = os.path.expanduser("~/.claude")
        os.makedirs(claude_dir, exist_ok=True)
        with open(_TOKEN_FILE, "w") as f:
            f.write(f"{ctx_limit},{tokens}")
    except Exception:
        pass


def _maybe_refresh_status(model_key: str) -> None:
    global _LAST_MODEL_KEY, _STATUS_CACHE
    if model_key == _LAST_MODEL_KEY:
        return
    _LAST_MODEL_KEY = model_key
    status_data = fetch_json("/status")
    quota_data = fetch_json("/quota")
    if status_data:
        _STATUS_CACHE = {"status": status_data, "quota": quota_data}
        _save_tokens(status_data.get("context_limit", 0), status_data.get("tokens", 0))


GREEN = "\033[32m"
ORANGE = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


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


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print(f"{DIM}cc-tpr | waiting...{RESET}")
        return

    project = os.path.basename(data.get("workspace", {}).get("current_dir", os.getcwd()))
    if not project:
        project = os.path.basename(os.getcwd())

    cw = data.get("context_window", {})
    pct = cw.get("used_percentage")
    size = cw.get("context_window_size")

    user_model = data.get("model", {}).get("display_name", "unknown")
    user_model_lower = user_model.lower()
    if "haiku" in user_model_lower:
        user_model_key = "haiku"
    elif "opus" in user_model_lower:
        user_model_key = "opus"
    else:
        user_model_key = "sonnet"

    _maybe_refresh_status(user_model_key)

    if _STATUS_CACHE:
        status_data = _STATUS_CACHE.get("status", {})
        quota_data = _STATUS_CACHE.get("quota", {})
    else:
        status_data = fetch_json("/status")
        quota_data = fetch_json("/quota")

    if status_data:
        provider = status_data.get("provider")
        ctx_limit = status_data.get("context_limit") or size
        tokens = status_data.get("tokens", 0)
    else:
        provider = None
        ctx_limit, tokens = _get_cached_tokens()
        if not ctx_limit:
            ctx_limit = size
            tokens = 0

    if provider == "deepseek":
        model = "deepseek-v4-pro"
    elif user_model_key == "haiku":
        model = "MiniMax-M2.7"
    elif user_model_key == "sonnet":
        model = "MiniMax-M2.7"
    elif user_model_key == "opus":
        model = "GLM-5.1"
    else:
        model = user_model

    if pct is None:
        print(f"{DIM}{project}{RESET} | {DIM}{model}{RESET} | {DIM}waiting...{RESET}")
        return

    if ctx_limit and tokens:
        pct = round(tokens / ctx_limit * 100, 1)

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

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
