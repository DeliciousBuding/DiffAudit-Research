"""Audit whether the variation line has a real query-image contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from diffaudit.attacks.variation import probe_variation_assets


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit_variation_query_contract",
        description="Check whether variation has enough real query images and an endpoint contract.",
    )
    parser.add_argument(
        "--query-root",
        type=Path,
        default=Path("../Download/black-box/datasets/variation-query-set"),
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("DIFFAUDIT_VARIATION_ENDPOINT", ""),
        help="real variation endpoint; defaults to DIFFAUDIT_VARIATION_ENDPOINT",
    )
    parser.add_argument("--min-split-count", type=int, default=25)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    payload = probe_variation_assets(
        query_image_root=args.query_root,
        endpoint=args.endpoint.strip(),
        min_split_count=args.min_split_count,
    )
    payload["contract"] = {
        "required_layout": "member/nonmember query-image split",
        "min_split_count": args.min_split_count,
        "endpoint_required": True,
        "promotion_gate": "nonzero strict-tail metrics on a held-out member/nonmember query split",
    }
    text = json.dumps(_sanitize(payload), indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
