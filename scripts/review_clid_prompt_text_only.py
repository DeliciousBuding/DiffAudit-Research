from __future__ import annotations

import argparse
import json
from pathlib import Path

from diffaudit.attacks.clid_prompt_text_review import review_clid_prompt_text_only


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review CLiD prompt-text-only split separability.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--min-count", type=int, default=2)
    parser.add_argument("--max-features", type=int, default=256)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = review_clid_prompt_text_only(
        args.run_root,
        min_count=args.min_count,
        max_features=args.max_features,
    )
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
