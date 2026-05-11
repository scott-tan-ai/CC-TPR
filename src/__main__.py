"""CLI entry point for CC-TPR."""

from __future__ import annotations

from .main import run_server


def main() -> None:
    """CLI entry point."""
    run_server()


if __name__ == "__main__":
    main()
