"""Probe a black-box response-contract package without running a model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from diffaudit.attacks.response_contract import inspect_response_contract_package


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
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--supplementary-root", type=Path, default=None)
    parser.add_argument("--min-split-count", type=int, default=25)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset_root = args.dataset_root or args.download_root / "black-box" / "datasets" / args.asset_id
    supplementary_root = (
        args.supplementary_root or args.download_root / "black-box" / "supplementary" / args.asset_id
    )
    payload = inspect_response_contract_package(
        asset_id=args.asset_id,
        dataset_root=dataset_root,
        supplementary_root=supplementary_root,
        min_split_count=args.min_split_count,
    )
    text = json.dumps(_sanitize(payload), indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
