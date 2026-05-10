"""Review whether gray-box tri-score evidence survives CPU-only hardening."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


METRIC_FIELDS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def _round6(value: float) -> float:
    return round(float(value), 6)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def review_triscore_truth_hardening(summary_path: Path) -> dict[str, Any]:
    payload = _load_json(summary_path)
    packets = payload.get("packets", [])
    if not isinstance(packets, list) or not packets:
        raise ValueError("summary must contain a non-empty packets list")
    comparator = payload.get("admitted_comparator", {})
    if not isinstance(comparator, dict):
        raise ValueError("summary admitted_comparator must be an object")

    per_packet = []
    for packet in packets:
        if not isinstance(packet, dict):
            raise ValueError("each packet must be an object")
        metric_delta = {
            metric: _round6(float(packet[metric]) - float(comparator[metric]))
            for metric in METRIC_FIELDS
        }
        per_packet.append(
            {
                "label": packet.get("label", ""),
                "source_run_id": packet.get("source_run_id", ""),
                "metrics": {metric: packet[metric] for metric in METRIC_FIELDS},
                "delta_vs_admitted_pia": metric_delta,
                "beats_admitted_pia": {metric: metric_delta[metric] > 0 for metric in METRIC_FIELDS},
            }
        )

    beats_counts = {
        metric: sum(1 for packet in per_packet if packet["beats_admitted_pia"][metric])
        for metric in METRIC_FIELDS
    }
    packet_count = len(per_packet)
    mean_metrics = {
        metric: _round6(mean(float(packet["metrics"][metric]) for packet in per_packet))
        for metric in METRIC_FIELDS
    }
    min_delta = {
        metric: _round6(min(float(packet["delta_vs_admitted_pia"][metric]) for packet in per_packet))
        for metric in METRIC_FIELDS
    }
    max_delta = {
        metric: _round6(max(float(packet["delta_vs_admitted_pia"][metric]) for packet in per_packet))
        for metric in METRIC_FIELDS
    }

    auc_gate = beats_counts["auc"] >= 2
    tpr1_gate = beats_counts["tpr_at_1pct_fpr"] >= 2
    strict_tail_positive = beats_counts["tpr_at_0_1pct_fpr"] >= 2
    no_admission_contract = not bool(payload.get("claim_boundary", {}).get("headline_use_allowed"))
    gate_passed = auc_gate and tpr1_gate and no_admission_contract

    if gate_passed:
        verdict = "positive-but-bounded"
        next_action = "keep as internal candidate; do not run GPU until a separate story-changing expansion is preflighted"
    else:
        verdict = "negative-but-useful"
        next_action = "close tri-score as unstable and reselect another CPU-first lane"

    return {
        "schema": "diffaudit.graybox_triscore_truth_hardening_review.v1",
        "status": verdict,
        "summary_source": summary_path.as_posix(),
        "packet_count": packet_count,
        "admitted_comparator": comparator,
        "per_packet": per_packet,
        "aggregate": {
            "mean_metrics": mean_metrics,
            "beats_admitted_pia_counts": beats_counts,
            "min_delta_vs_admitted_pia": min_delta,
            "max_delta_vs_admitted_pia": max_delta,
        },
        "gates": {
            "auc_beats_in_at_least_2_of_3": auc_gate,
            "tpr_at_1pct_fpr_beats_in_at_least_2_of_3": tpr1_gate,
            "tpr_at_0_1pct_fpr_reported_positive_in_at_least_2_of_3": strict_tail_positive,
            "internal_only_contract_preserved": no_admission_contract,
            "gpu_release": False,
            "admitted_promotion": False,
        },
        "verdict": verdict,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("workspaces/gray-box/artifacts/graybox-triscore-consolidation-summary.json"),
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    result = review_triscore_truth_hardening(args.summary)
    text = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
