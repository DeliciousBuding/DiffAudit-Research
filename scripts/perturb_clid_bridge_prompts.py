from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_metadata(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        rows.append(json.loads(raw_line))
    return rows


def _write_metadata(path: Path, rows: list[dict[str, object]]) -> int:
    encoded = [json.dumps(row, ensure_ascii=False) for row in rows]
    path.write_text("\n".join(encoded), encoding="utf-8")
    return len(rows)


def _fixed_prompt(rows: list[dict[str, object]], prompt: str) -> list[dict[str, object]]:
    rewritten = []
    for row in rows:
        next_row = dict(row)
        next_row["text"] = prompt
        rewritten.append(next_row)
    return rewritten


def perturb_metadata_prompts(
    member_path: Path,
    nonmember_path: Path,
    *,
    mode: str,
    prompt: str,
) -> dict[str, object]:
    member_rows = _read_metadata(member_path)
    nonmember_rows = _read_metadata(nonmember_path)

    if mode == "fixed":
        next_member_rows = _fixed_prompt(member_rows, prompt)
        next_nonmember_rows = _fixed_prompt(nonmember_rows, prompt)
    elif mode == "swap-split-prompts":
        if len(member_rows) != len(nonmember_rows):
            raise ValueError("swap-split-prompts requires equal member and nonmember row counts")
        next_member_rows = []
        next_nonmember_rows = []
        for member_row, nonmember_row in zip(member_rows, nonmember_rows):
            next_member = dict(member_row)
            next_nonmember = dict(nonmember_row)
            next_member["text"] = nonmember_row.get("text", "")
            next_nonmember["text"] = member_row.get("text", "")
            next_member_rows.append(next_member)
            next_nonmember_rows.append(next_nonmember)
    else:
        raise ValueError(f"unsupported prompt perturbation mode: {mode}")

    member_count = _write_metadata(member_path, next_member_rows)
    nonmember_count = _write_metadata(nonmember_path, next_nonmember_rows)

    return {
        "status": "ready",
        "mode": mode,
        "prompt": prompt if mode == "fixed" else None,
        "member_rows": member_count,
        "nonmember_rows": nonmember_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rewrite local CLiD bridge metadata prompts for CPU prompt controls.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=["fixed", "swap-split-prompts"],
        default="fixed",
        help="Prompt perturbation mode. fixed rewrites every prompt; swap-split-prompts swaps member/nonmember prompt text by row.",
    )
    parser.add_argument("--prompt", type=str, default="a face")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    member_path = args.run_root / "datasets" / "member" / "metadata.jsonl"
    nonmember_path = args.run_root / "datasets" / "nonmember" / "metadata.jsonl"
    review = perturb_metadata_prompts(
        member_path,
        nonmember_path,
        mode=args.mode,
        prompt=args.prompt,
    )
    payload = {
        "status": "ready",
        "mode": "prompt-perturbation",
        "perturbation_mode": args.mode,
        "run_root": args.run_root.as_posix(),
        "prompt": args.prompt if args.mode == "fixed" else None,
        "member_rows": review["member_rows"],
        "nonmember_rows": review["nonmember_rows"],
        "verdict": (
            "metadata prompts rewritten to fixed prompt"
            if args.mode == "fixed"
            else "member and nonmember prompt text swapped by row"
        ),
    }
    output = args.output or args.run_root / "prompt-perturbation.json"
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
