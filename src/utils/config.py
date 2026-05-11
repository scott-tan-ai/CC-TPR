"""Configuration loader for CC-TPR."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def load_config(config_path: str | Path | None = None) -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Optional path to config file. Defaults to config.yaml in project root.

    Returns:
        Configuration dictionary.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["server"]["port"] = int(os.getenv("PORT", config["server"].get("port", 3456)))
    config["server"]["log_level"] = os.getenv(
        "LOG_LEVEL", config["server"].get("log_level", "INFO")
    )

    return config
