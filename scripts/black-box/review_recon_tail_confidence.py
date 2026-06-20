"""Review finite-sample confidence bounds for the admitted recon tail metrics."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_CARD = Path("workspaces/implementation/artifacts/recon-product-evidence-card.json")
Z_95 = 1.959963984540054
TAIL_TARGET_FPR = {
    "tpr_at_1pct_fpr": 0.01,
    "tpr_at_0_1pct_fpr": 0.001,
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repo_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def wilson_interval(successes: int, total: int, *, z: float = Z_95) -> dict[str, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must be in [0, total]")

    p_hat = successes / total
    denom = 1.0 + (z * z / total)
    center = (p_hat + (z * z / (2.0 * total))) / denom
    margin = (
        z
        * math.sqrt((p_hat * (1.0 - p_hat) / total) + (z * z / (4.0 * total * total)))
        / denom
    )
    lower = max(0.0, center - margin)
    if successes == 0:
        lower = 0.0
    return {
        "estimate": p_hat,
        "lower_95": lower,
        "upper_95": min(1.0, center + margin),
    }


def build_review(card_path: Path, *, root: Path) -> dict[str, Any]:
    card = json.loads(card_path.read_text(encoding="utf-8"))
    finite_tail = card["finite_tail"]
    gates = finite_tail["gates"]
    member_count = int(finite_tail["target_member_count"])
    nonmember_count = int(finite_tail["target_nonmember_count"])

    reviewed_gates: dict[str, Any] = {}
    for gate_name, gate in gates.items():
        if gate_name not in TAIL_TARGET_FPR:
            raise KeyError(f"Unsupported finite-tail gate: {gate_name}")
        true_positives = int(gate["true_positives"])
        false_positives = int(gate["false_positives"])
        target_fpr = TAIL_TARGET_FPR[gate_name]
        fpr_interval = wilson_interval(false_positives, nonmember_count)
        tpr_interval = wilson_interval(true_positives, member_count)
        reviewed_gates[gate_name] = {
            "target_fpr": target_fpr,
            "member_count": member_count,
            "nonmember_count": nonmember_count,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "tpr_interval": {key: round(value, 6) for key, value in tpr_interval.items()},
            "fpr_interval": {key: round(value, 6) for key, value in fpr_interval.items()},
            "calibrated_to_target_fpr": fpr_interval["upper_95"] <= target_fpr,
        }

    strict_gate = reviewed_gates.get("tpr_at_0_1pct_fpr")
    if strict_gate is None:
        raise KeyError("Missing required finite-tail gate: tpr_at_0_1pct_fpr")
    verdict = (
        "admitted-finite-tail-only"
        if strict_gate["true_positives"] > 0 and not strict_gate["calibrated_to_target_fpr"]
        else "needs-review"
    )
    return {
        "schema": "diffaudit.recon_tail_confidence_review.v1",
        "track": "black-box",
        "method": card["method"]["attack"],
        "device": "cpu",
        "source_card": _repo_relative(card_path, root),
        "confidence_method": "wilson_95",
        "verdict": verdict,
        "gates": reviewed_gates,
        "decision": (
            "Keep the recon row admitted with finite-tail wording; do not describe "
            "TPR@0.1%FPR as calibrated below one percent on a public-100 split."
        ),
        "next_gpu_candidate": "none selected; scale-up only if the product claim requires calibrated sub-percent FPR",
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="review_recon_tail_confidence",
        description="Review confidence bounds for finite-sample recon tail metrics.",
    )
    parser.add_argument("--card", type=Path, default=DEFAULT_CARD)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    card_path = args.card if args.card.is_absolute() else root / args.card
    review = build_review(card_path, root=root)
    text = json.dumps(review, indent=2, ensure_ascii=True) + "\n"
    if args.output is not None:
        output_path = args.output if args.output.is_absolute() else root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
