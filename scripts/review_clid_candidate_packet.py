from __future__ import annotations

import argparse
import json
from pathlib import Path

from diffaudit.attacks.clid_candidate_review import review_clid_candidate_packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a local CLiD candidate packet before admission.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--permutations", type=int, default=512)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = review_clid_candidate_packet(args.run_root, permutations=args.permutations)
    text = json.dumps(payload, indent=2, ensure_ascii=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
