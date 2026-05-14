"""Quota monitoring for MiniMax and ZAI providers."""

from __future__ import annotations

import os
import threading
import time
from typing import Any

import requests

from .utils.logger import setup_logger

logger = setup_logger()

_MINIMAX_CACHE: dict[str, Any] = {"data": None, "expires": 0.0}
_ZAI_CACHE: dict[str, Any] = {"data": None, "expires": 0.0}
_cache_lock = threading.Lock()

MINIMAX_CACHE_TTL = 90
ZAI_CACHE_TTL = 90


def _fetch_minimax_raw() -> dict[str, Any] | None:
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return None

    try:
        resp = requests.get(
            "https://api.minimax.io/v1/api/openplatform/coding_plan/remains",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"MiniMax quota fetch failed: {e}")
        return None


def _fetch_zai_raw() -> dict[str, Any] | None:
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        return None

    try:
        resp = requests.get(
            "https://api.z.ai/api/monitor/usage/quota/limit",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"ZAI quota fetch failed: {e}")
        return None


def get_minimax_quota() -> dict[str, Any] | None:
    now = time.time()
    with _cache_lock:
        if _MINIMAX_CACHE["data"] is not None and now < _MINIMAX_CACHE["expires"]:
            return _MINIMAX_CACHE["data"]

    raw = _fetch_minimax_raw()
    if raw is None:
        with _cache_lock:
            if _MINIMAX_CACHE["data"] is not None:
                return _MINIMAX_CACHE["data"]
            return None

    model_data = None
    for m in raw.get("model_remains", []):
        if m.get("model_name", "").startswith("MiniMax-M"):
            model_data = m
            break

    if model_data is None:
        return None

    interval_total = model_data.get("current_interval_total_count", 0)
    interval_remaining = model_data.get("current_interval_usage_count", 0)
    if interval_total > 0:
        hr5_pct = round((1 - interval_remaining / interval_total) * 100, 1)
    else:
        hr5_pct = 0.0

    hr5_reset_ms = model_data.get("remains_time")

    weekly_total = model_data.get("current_weekly_total_count", 0)
    weekly_remaining = model_data.get("current_weekly_usage_count", 0)
    if weekly_total > 0:
        weekly_pct = round((1 - weekly_remaining / weekly_total) * 100, 1)
    else:
        weekly_pct = 0.0

    weekly_reset_ms = model_data.get("weekly_remains_time")

    result = {
        "5hr_pct": hr5_pct,
        "5hr_reset_ms": hr5_reset_ms,
        "weekly_pct": weekly_pct,
        "weekly_reset_ms": weekly_reset_ms,
    }

    with _cache_lock:
        _MINIMAX_CACHE["data"] = result
        _MINIMAX_CACHE["expires"] = now + MINIMAX_CACHE_TTL

    return result


def get_zai_quota() -> dict[str, Any] | None:
    now = time.time()
    with _cache_lock:
        if _ZAI_CACHE["data"] is not None and now < _ZAI_CACHE["expires"]:
            return _ZAI_CACHE["data"]

    raw = _fetch_zai_raw()
    if raw is None:
        with _cache_lock:
            if _ZAI_CACHE["data"] is not None:
                return _ZAI_CACHE["data"]
            return None

    limits = raw.get("data", {}).get("limits", [])

    hr5_pct = None
    hr5_reset_ms = None
    weekly_pct = None
    weekly_reset_ms = None

    for limit in limits:
        ltype = limit.get("type", "")
        unit = limit.get("unit", 0)

        if ltype == "TOKENS_LIMIT" and unit == 3:
            hr5_pct = limit.get("percentage", 0)
            hr5_reset_ms = limit.get("nextResetTime")
        elif ltype == "TOKENS_LIMIT" and unit == 6:
            weekly_pct = limit.get("percentage", 0)
            weekly_reset_ms = limit.get("nextResetTime")

    if hr5_pct is None:
        hr5_pct = 0

    now_ms = int(time.time() * 1000)

    if hr5_reset_ms is not None:
        hr5_reset_ms = max(0, hr5_reset_ms - now_ms)
    if weekly_reset_ms is not None:
        weekly_reset_ms = max(0, weekly_reset_ms - now_ms)

    result = {
        "5hr_pct": hr5_pct,
        "5hr_reset_ms": hr5_reset_ms if hr5_reset_ms is not None else 0,
        "weekly_pct": weekly_pct if weekly_pct is not None else 0,
        "weekly_reset_ms": weekly_reset_ms if weekly_reset_ms is not None else 0,
    }

    with _cache_lock:
        _ZAI_CACHE["data"] = result
        _ZAI_CACHE["expires"] = now + ZAI_CACHE_TTL

    return result


def get_quota() -> dict[str, Any]:
    return {
        "minimax": get_minimax_quota(),
        "zai": get_zai_quota(),
    }
