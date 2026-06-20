from __future__ import annotations

import argparse
import json
from pathlib import Path

from diffaudit.attacks.clid import summarize_clid_bridge_pair_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a tiny local CLiD member/nonmember bridge output pair.")
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = summarize_clid_bridge_pair_outputs(
        artifact_dir=args.artifact_dir,
        workspace=args.workspace,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
