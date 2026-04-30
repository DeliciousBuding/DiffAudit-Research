"""Command-line interface package for research audit workflows."""

from __future__ import annotations

from diffaudit.cli._dispatch import main
from diffaudit.cli._parser import build_parser

__all__ = ["build_parser", "main"]
