"""Command-line interface package for research audit workflows."""

from __future__ import annotations

from diffaudit.cli._parser import build_parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI without importing command implementations at package import time."""
    from diffaudit.cli._dispatch import main as dispatch_main

    return dispatch_main(argv)


__all__ = ["build_parser", "main"]
