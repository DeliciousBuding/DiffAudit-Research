from __future__ import annotations

import argparse
import json
from pathlib import Path

from diffaudit.attacks.clid_control_attribution import compare_clid_control_packets


def _parse_label_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected LABEL=PATH")
    label, path = value.split("=", 1)
    if not label:
        raise argparse.ArgumentTypeError("Label must not be empty")
    return label, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare CLiD prompt-control packets against one baseline packet.")
    parser.add_argument("--baseline", type=_parse_label_path, required=True)
    parser.add_argument("--control", type=_parse_label_path, action="append", required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare_clid_control_packets(args.baseline, args.control)
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
