from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.h2_cross_asset import (
    default_roots,
    evaluate_h2_cross_asset_contract,
    inspect_celeba_assets,
    inspect_recon_celeba_assets,
    inspect_sd15_assets,
)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe whether a cross-asset H2 contract is protocol-compatible.")
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--sd15-model-dir", type=Path, default=None)
    parser.add_argument("--celeba-root", type=Path, default=None)
    parser.add_argument("--recon-root", type=Path, default=None)
    parser.add_argument(
        "--endpoint-mode",
        choices=("text_to_image", "image_to_image", "ddpm_unconditional"),
        default="text_to_image",
    )
    parser.add_argument("--controlled-repeats", action="store_true")
    parser.add_argument("--response-images-observable", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    roots = default_roots(args.download_root)
    sd15_model_dir = args.sd15_model_dir or roots["sd15_model_dir"]
    celeba_root = args.celeba_root or roots["celeba_root"]
    recon_root = args.recon_root or roots["recon_root"]
    return evaluate_h2_cross_asset_contract(
        endpoint_mode=args.endpoint_mode,
        sd15_assets=inspect_sd15_assets(sd15_model_dir),
        celeba_assets=inspect_celeba_assets(celeba_root),
        recon_assets=inspect_recon_celeba_assets(recon_root),
        controlled_repeats=bool(args.controlled_repeats),
        response_images_observable=bool(args.response_images_observable),
    )


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    text = json.dumps(_sanitize(payload), indent=2, ensure_ascii=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] != "needs_assets" else 1


if __name__ == "__main__":
    raise SystemExit(main())
