"""Logging setup for CC-TPR."""

from __future__ import annotations

import logging
import sys


def setup_logger(level: str = "INFO") -> logging.Logger:
    """Configure and return a logger for CC-TPR.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("cc-tpr")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)

    return logger
