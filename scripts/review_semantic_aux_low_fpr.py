"""Review whether semantic-auxiliary black-box packets justify GPU follow-up."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.semantic_aux_fusion import analyze_semantic_aux_fusion, load_semantic_aux_records


DEFAULT_SUMMARY = Path(
    "workspaces/black-box/runs/semantic-aux-fusion-20260416-r1/summary.json"
)
RAW_RECORD_HINTS = (
    "workspaces/black-box/runs/semantic-aux-classifier-comparator-20260415-r1/outputs/records.json",
    "workspaces/black-box/runs/semantic-aux-classifier-comparator-20260416-r2/outputs/records.json",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repo_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def build_review(record_paths: list[Path], *, root: Path) -> dict[str, Any]:
    per_run: list[dict[str, Any]] = []
    best_gain = 0.0
    strict_tail_positive = False
    for path in record_paths:
        analysis = analyze_semantic_aux_fusion(load_semantic_aux_records(path))
        analysis["records_path"] = _repo_relative(path, root)
        per_run.append(analysis)
        best_gain = max(best_gain, float(analysis.get("best_auc_gain_vs_mean_cos", 0.0)))
        for candidate in analysis.get("candidates", {}).values():
            strict_tail_positive = strict_tail_positive or float(candidate.get("tpr_at_0_1pct_fpr", 0.0)) > 0.0

    clears_gain_gate = best_gain >= 0.01
    verdict = (
        "hold-candidate"
        if clears_gain_gate and strict_tail_positive
        else "negative but useful"
    )
    return {
        "schema": "diffaudit.semantic_aux_low_fpr_review.v1",
        "track": "black-box",
        "method_family": "semantic-auxiliary-classifier",
        "device": "cpu",
        "verdict": verdict,
        "gate": {
            "min_auc_gain_vs_mean_cos": 0.01,
            "requires_positive_tpr_at_0_1pct_fpr": True,
            "clears_auc_gain_gate": clears_gain_gate,
            "strict_tail_positive_any_candidate": strict_tail_positive,
        },
        "best_auc_gain_vs_mean_cos": round(best_gain, 6),
        "per_run": per_run,
        "decision": (
            "Do not schedule a semantic-aux GPU packet under the current protocol."
            if verdict == "negative but useful"
            else "Freeze a held-out packet contract before any GPU run."
        ),
    }


def build_review_from_summary(summary_path: Path, *, root: Path) -> dict[str, Any]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    per_run = summary.get("per_run", [])
    best_gain = max(
        (float(run.get("best_auc_gain_vs_mean_cos", 0.0)) for run in per_run),
        default=0.0,
    )
    strict_tail_positive = any(
        float(candidate.get("tpr_at_0_1pct_fpr", 0.0)) > 0.0
        for run in per_run
        for candidate in run.get("candidates", {}).values()
    )
    clears_gain_gate = best_gain >= 0.01
    verdict = (
        "hold-candidate"
        if clears_gain_gate and strict_tail_positive
        else "negative but useful"
    )
    return {
        "schema": "diffaudit.semantic_aux_low_fpr_review.v1",
        "track": "black-box",
        "method_family": "semantic-auxiliary-classifier",
        "device": "cpu",
        "source_mode": "committed-summary",
        "summary_path": _repo_relative(summary_path, root),
        "raw_record_hints": list(RAW_RECORD_HINTS),
        "verdict": verdict,
        "gate": {
            "min_auc_gain_vs_mean_cos": 0.01,
            "requires_positive_tpr_at_0_1pct_fpr": True,
            "clears_auc_gain_gate": clears_gain_gate,
            "strict_tail_positive_any_candidate": strict_tail_positive,
        },
        "best_auc_gain_vs_mean_cos": round(best_gain, 6),
        "per_run": per_run,
        "decision": (
            "Do not schedule a semantic-aux GPU packet under the current protocol."
            if verdict == "negative but useful"
            else "Freeze a held-out packet contract before any GPU run."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="review_semantic_aux_low_fpr",
        description="Review existing semantic-aux records against low-FPR promotion gates.",
    )
    parser.add_argument("--records", action="append", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.records:
        record_paths = [path if path.is_absolute() else root / path for path in args.records]
        review = build_review(record_paths, root=root)
        review["source_mode"] = "raw-records"
    else:
        summary_path = args.summary if args.summary.is_absolute() else root / args.summary
        review = build_review_from_summary(summary_path, root=root)
    text = json.dumps(review, indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        output_path = args.output if args.output.is_absolute() else root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
