from __future__ import annotations

import argparse
import json
from pathlib import Path


def _rewrite_metadata(path: Path, prompt: str) -> int:
    rows = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        row = json.loads(raw_line)
        row["text"] = prompt
        rows.append(json.dumps(row, ensure_ascii=False))
    path.write_text("\n".join(rows), encoding="utf-8")
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rewrite local CLiD bridge metadata prompts to a fixed prompt.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--prompt", type=str, default="a face")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    member_path = args.run_root / "datasets" / "member" / "metadata.jsonl"
    nonmember_path = args.run_root / "datasets" / "nonmember" / "metadata.jsonl"
    member_count = _rewrite_metadata(member_path, args.prompt)
    nonmember_count = _rewrite_metadata(nonmember_path, args.prompt)
    payload = {
        "status": "ready",
        "mode": "prompt-neutral-perturbation",
        "run_root": args.run_root.as_posix(),
        "prompt": args.prompt,
        "member_rows": member_count,
        "nonmember_rows": nonmember_count,
        "verdict": "metadata prompts rewritten to fixed prompt",
    }
    output = args.output or args.run_root / "prompt-perturbation.json"
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
