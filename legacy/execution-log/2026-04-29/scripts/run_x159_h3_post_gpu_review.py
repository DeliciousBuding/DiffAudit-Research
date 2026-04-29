from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LOW_FPR_KEYS = ("tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
HEADLINE_KEYS = ("auc", "asr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-159 CPU review for H3 selective all-steps gating after the X-158 GPU scout."
    )
    parser.add_argument(
        "--x157-summary",
        type=Path,
        default=Path(
            "workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-20260429-r2-allsteps-primary/summary.json"
        ),
    )
    parser.add_argument(
        "--x158-summary",
        type=Path,
        default=Path("workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-20260429-r1/summary.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("workspaces/gray-box/runs/x159-h3-post-gpu-review-20260429-r1/summary.json"),
    )
    parser.add_argument("--max-gate-fraction", type=float, default=0.21)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics_delta(left: dict[str, float], right: dict[str, float], keys: tuple[str, ...]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in keys}


def bool_gate(name: str, passed: bool, detail: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), **detail}


def main() -> int:
    args = parse_args()
    x157 = load_json(args.x157_summary)
    x158 = load_json(args.x158_summary)

    x157_primary = x157["primary_selection"]["adaptive"]
    x157_selective = x157_primary["metrics"]
    x157_all_steps = x157["surface_metrics"]["adaptive"]["all_steps"]

    x158_selective = x158["selective_gated"]["adaptive"]["metrics"]
    x158_all_steps = x158["all_steps"]["adaptive_metrics"]
    x158_baseline = x158["baseline"]["adaptive_metrics"]
    x158_gate = x158["gate"]["adaptive"]

    x157_low_fpr_match = all(
        float(x157_selective[key]) <= float(x157_all_steps[key]) for key in LOW_FPR_KEYS
    )
    x158_low_fpr_match = all(
        float(x158_selective[key]) <= float(x158_all_steps[key]) for key in LOW_FPR_KEYS
    )
    x158_gate_budget_ok = float(x158_gate["gate_fraction_actual"]) <= float(args.max_gate_fraction)
    x158_full_metric_privacy_dominance = all(
        float(x158_selective[key]) <= float(x158_all_steps[key]) for key in HEADLINE_KEYS
    )

    gates = [
        bool_gate(
            "cache_low_fpr_tail_match",
            x157_low_fpr_match,
            {
                "selective": {key: x157_selective[key] for key in LOW_FPR_KEYS},
                "all_steps": {key: x157_all_steps[key] for key in LOW_FPR_KEYS},
            },
        ),
        bool_gate(
            "fresh_low_fpr_tail_match",
            x158_low_fpr_match,
            {
                "selective": {key: x158_selective[key] for key in LOW_FPR_KEYS},
                "all_steps": {key: x158_all_steps[key] for key in LOW_FPR_KEYS},
            },
        ),
        bool_gate(
            "fresh_gate_budget",
            x158_gate_budget_ok,
            {
                "gate_fraction_actual": x158_gate["gate_fraction_actual"],
                "max_gate_fraction": round(float(args.max_gate_fraction), 6),
            },
        ),
        bool_gate(
            "full_metric_privacy_dominance",
            x158_full_metric_privacy_dominance,
            {
                "selective_minus_all_steps": metrics_delta(x158_selective, x158_all_steps, HEADLINE_KEYS),
                "interpretation": "negative means more protective than all-steps; positive means weaker privacy than full all-steps",
            },
        ),
        bool_gate(
            "deployable_gate_without_score_leakage",
            False,
            {
                "reason": "current gate uses same-packet baseline PIA score tail, so it is an audit-time owner-side selector rather than a deployable cheap runtime detector",
            },
        ),
        bool_gate(
            "budget_fixed_adaptive_attacker_cleared",
            False,
            {
                "reason": "X-158 uses adaptive_query_repeats=3, but does not yet test an attacker who reallocates a fixed query budget against the gated policy",
            },
        ),
    ]

    summary = {
        "status": "ready",
        "task": "X-159 H3 post-GPU review / implementation-hardening decision",
        "mode": "cpu-post-gpu-review",
        "inputs": {
            "x157_summary": str(args.x157_summary),
            "x158_summary": str(args.x158_summary),
        },
        "evidence": {
            "x157_cached_primary_adaptive": {
                "selective_metrics": x157_selective,
                "all_steps_metrics": x157_all_steps,
                "gate_fraction_actual": x157_primary["gate_fraction_actual"],
            },
            "x158_fresh_adaptive": {
                "baseline_metrics": x158_baseline,
                "all_steps_metrics": x158_all_steps,
                "selective_metrics": x158_selective,
                "selective_minus_baseline": metrics_delta(x158_selective, x158_baseline, LOW_FPR_KEYS + HEADLINE_KEYS),
                "selective_minus_all_steps": metrics_delta(x158_selective, x158_all_steps, LOW_FPR_KEYS + HEADLINE_KEYS),
                "gate": x158_gate,
            },
        },
        "gates": gates,
        "verdict": "positive hardening / GPU hold",
        "decision": {
            "h3_status": "candidate-only quality/perturbation-exposure idea",
            "implementation_hardening_allowed": "CPU-only candidate runner contract review",
            "larger_gpu_release_allowed": False,
            "deployable_runner_allowed": False,
            "promotion_allowed": False,
            "next_gpu_candidate": "none",
            "next_live_lane": "X-160 non-graybox next-lane reselection after H3 review",
            "cpu_sidecar": "I-A low-FPR / adaptive-attacker boundary maintenance",
        },
        "notes": [
            "X-158 is real evidence that selective all-steps gating can match the full all-steps low-FPR tail on one fresh 64/64 packet while routing about 20% of samples.",
            "The result does not prove a stronger defense: selective AUC/ASR are closer to baseline than full all-steps, and the detector is the baseline PIA score tail.",
            "The honest implementation value is perturbation-exposure selectivity inside an audit pipeline, not a validated privacy mechanism or a cheap deployable runtime defense.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
