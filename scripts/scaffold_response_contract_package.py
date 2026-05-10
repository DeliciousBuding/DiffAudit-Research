"""Create or dry-run a portable response-contract package skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.response_contract import SUPPORTED_ENDPOINT_MODES, scaffold_response_contract_package


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
    parser.add_argument("--dataset-name", default="")
    parser.add_argument("--model-identity", default="")
    parser.add_argument("--endpoint-mode", choices=sorted(SUPPORTED_ENDPOINT_MODES), default="image_to_image")
    parser.add_argument("--repeat-count", type=int, default=1)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = scaffold_response_contract_package(
        asset_id=args.asset_id,
        download_root=args.download_root,
        dataset_name=args.dataset_name,
        model_identity=args.model_identity,
        endpoint_mode=args.endpoint_mode,
        repeat_count=args.repeat_count,
        create=args.create,
    )
    text = json.dumps(_sanitize(payload), indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
