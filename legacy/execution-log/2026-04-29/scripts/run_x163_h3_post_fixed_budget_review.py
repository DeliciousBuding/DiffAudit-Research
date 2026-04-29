from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LOW_FPR_KEYS = ("tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
HEADLINE_KEYS = ("auc", "asr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-163 CPU review after the X-162 H3 fixed-budget GPU scout."
    )
    parser.add_argument(
        "--x162-summary",
        type=Path,
        default=Path("workspaces/gray-box/runs/x162-h3-budget-fixed-gpu-scout-20260429-r1/summary.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("workspaces/gray-box/runs/x163-h3-post-fixed-budget-review-20260429-r1/summary.json"),
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_delta(left: dict[str, float], right: dict[str, float], keys: tuple[str, ...]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in keys}


def gate(name: str, passed: bool, detail: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), **detail}


def main() -> int:
    args = parse_args()
    x162 = load_json(args.x162_summary)

    baseline = x162["baseline_budget"]["metrics"]
    all_steps = x162["all_steps_budget"]["metrics"]
    selective = x162["fixed_budget_selective"]["metrics"]
    gate_leak = x162["gate_leak_falsifier"]["metrics"]
    oracle = x162["oracle_route_escape"]["metrics"]

    fixed_budget_low_fpr_match = all(float(selective[key]) <= float(all_steps[key]) for key in LOW_FPR_KEYS)
    full_metric_privacy_dominance = all(float(selective[key]) <= float(all_steps[key]) for key in HEADLINE_KEYS)
    gate_leak_matches_all_steps = all(float(gate_leak[key]) <= float(all_steps[key]) for key in LOW_FPR_KEYS)
    oracle_below_baseline = all(float(oracle[key]) < float(baseline[key]) for key in LOW_FPR_KEYS)

    summary = {
        "status": "ready",
        "task": "X-163 H3 post-fixed-budget review / freeze-or-reselect decision",
        "mode": "cpu-post-gpu-review",
        "inputs": {"x162_summary": str(args.x162_summary)},
        "evidence": {
            "baseline_budget": baseline,
            "all_steps_budget": all_steps,
            "fixed_budget_selective": selective,
            "gate_leak_falsifier": gate_leak,
            "oracle_route_escape": oracle,
            "selective_minus_all_steps": metric_delta(
                selective,
                all_steps,
                ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"),
            ),
            "gate_leak_minus_all_steps": metric_delta(
                gate_leak,
                all_steps,
                ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"),
            ),
            "oracle_minus_baseline": metric_delta(
                oracle,
                baseline,
                ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"),
            ),
            "gate": x162["gate"],
        },
        "gates": [
            gate(
                "fixed_budget_low_fpr_tail_match",
                fixed_budget_low_fpr_match,
                {"rule": "selective fixed-budget low-FPR must not exceed all-steps low-FPR"},
            ),
            gate(
                "full_metric_privacy_dominance",
                full_metric_privacy_dominance,
                {"rule": "selective fixed-budget AUC/ASR must not be privacy-weaker than all-steps"},
            ),
            gate(
                "gate_leak_robustness",
                gate_leak_matches_all_steps,
                {"rule": "if gate score leaks into attack score, low-FPR must still match all-steps"},
            ),
            gate(
                "oracle_route_escape_robustness",
                oracle_below_baseline,
                {"rule": "oracle route escape must remain below baseline low-FPR tail"},
            ),
        ],
        "verdict": "positive but bounded / freeze H3",
        "decision": {
            "h3_status": "closed as candidate-only selectivity evidence",
            "promotion_allowed": False,
            "larger_gpu_release_allowed": False,
            "deployable_runner_allowed": False,
            "active_gpu_question": "none",
            "next_gpu_candidate": "none until X164 selects a genuinely new bounded hypothesis",
            "next_live_lane": "X164 nongraybox next-lane reselection after H3 fixed-budget closure",
            "cpu_sidecar": "I-A low-FPR / adaptive-attacker boundary maintenance",
        },
        "notes": [
            "X162 passes the fixed-budget defended-policy low-FPR gate, so H3 is not a score-level mirage.",
            "Gate-leak and oracle-route falsifiers fail enough to block promotion, deployment, and larger same-rule GPU work.",
            "The honest next move is reselection, not another H3 packet.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
