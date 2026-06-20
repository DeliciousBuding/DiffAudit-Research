"""Discover black-box response-contract packages under Download."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.response_contract import discover_response_contract_packages


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--min-split-count", type=int, default=25)
    parser.add_argument(
        "--include-asset-id",
        action="append",
        default=[],
        help="candidate id to include even if one or both roots are missing; may be repeated",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = discover_response_contract_packages(
        download_root=args.download_root,
        min_split_count=args.min_split_count,
        include_asset_ids=args.include_asset_id,
    )
    text = json.dumps(_sanitize(payload), indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
