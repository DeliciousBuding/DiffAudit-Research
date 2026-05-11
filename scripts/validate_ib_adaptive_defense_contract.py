from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT = Path("workspaces/defense/artifacts/ib-adaptive-defense-contract-20260511.json")
REQUIRED_DELTAS = ("delta_auc", "delta_tpr_at_1pct_fpr", "delta_tpr_at_0_1pct_fpr")
REQUIRED_REOPEN_FIELDS = (
    "defended_shadow_training_protocol",
    "adaptive_attacker_protocol",
    "same_member_nonmember_identity",
    "low_fpr_primary_gate",
    "retained_utility_metric",
    "stop_condition_for_no_strict_tail_improvement",
)
REQUIRED_BLOCKERS = (
    "no defended-shadow attacker",
    "no adaptive attacker review",
    "strict-tail improvement is absent or too small",
    "retained utility is not part of the current evidence",
)
REQUIRED_BLOCKED_CLAIMS = (
    "admitted defense evidence",
    "adaptive robustness",
    "low-FPR defense improvement",
    "Platform/Runtime defense row",
)
REQUIRED_EVIDENCE_DOCS = (
    "docs/evidence/ib-adaptive-defense-contract-20260511.md",
    "docs/evidence/ib-risk-targeted-unlearning-successor-scope.md",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_delta(errors: list[str], prefix: str, payload: dict[str, Any], fields: tuple[str, ...]) -> None:
    for field in fields:
        value = payload.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{prefix}.{field} must be numeric, got {value!r}")
        elif not math.isfinite(float(value)):
            errors.append(f"{prefix}.{field} must be finite, got {value!r}")
        elif not -1.0 <= float(value) <= 1.0:
            errors.append(f"{prefix}.{field} must be in [-1, 1], got {value!r}")


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]

    if payload.get("schema") != "diffaudit.ib_adaptive_defense_contract.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "hold":
        errors.append("status must remain hold")
    if payload.get("admitted") is not False:
        errors.append("I-B adaptive defense contract must not mark the row admitted")
    if payload.get("gpu_release") != "none":
        errors.append("I-B adaptive defense contract must not release GPU work")

    reviewed_runs = payload.get("reviewed_runs")
    if not isinstance(reviewed_runs, list) or len(reviewed_runs) < 3:
        errors.append("reviewed_runs must contain at least three reviewed deltas")
    else:
        for index, run in enumerate(reviewed_runs):
            prefix = f"reviewed_runs[{index}]"
            if not isinstance(run, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if not run.get("run"):
                errors.append(f"{prefix}.run must be non-empty")
            _require_delta(errors, prefix, run, REQUIRED_DELTAS)

    boundary = payload.get("observed_boundary")
    if not isinstance(boundary, dict):
        errors.append("observed_boundary must be an object")
    else:
        _require_delta(
            errors,
            "observed_boundary",
            boundary,
            (
                "best_auc_reduction",
                "best_tpr_at_1pct_fpr_reduction",
                "best_tpr_at_0_1pct_fpr_reduction",
            ),
        )
        if boundary.get("strict_tail_claim_supported") is not False:
            errors.append("observed_boundary.strict_tail_claim_supported must be false")
        if boundary.get("defense_aware_attacker_used") is not False:
            errors.append("observed_boundary.defense_aware_attacker_used must be false")

    reopen_contract = payload.get("required_reopen_contract")
    if not isinstance(reopen_contract, dict):
        errors.append("required_reopen_contract must be an object")
    else:
        for field in REQUIRED_REOPEN_FIELDS:
            if reopen_contract.get(field) != "required":
                errors.append(f"required_reopen_contract.{field} must be required")

    blockers = payload.get("promotion_blockers")
    if not isinstance(blockers, list):
        errors.append("promotion_blockers must be a list")
    else:
        for blocker in REQUIRED_BLOCKERS:
            if blocker not in blockers:
                errors.append(f"missing promotion blocker: {blocker}")

    blocked_claims = payload.get("blocked_claims")
    if not isinstance(blocked_claims, list):
        errors.append("blocked_claims must be a list")
    else:
        for claim in REQUIRED_BLOCKED_CLAIMS:
            if claim not in blocked_claims:
                errors.append(f"missing blocked claim: {claim}")

    evidence_docs = payload.get("evidence_docs")
    if not isinstance(evidence_docs, list):
        errors.append("evidence_docs must be a list")
    else:
        for doc in REQUIRED_EVIDENCE_DOCS:
            if doc not in evidence_docs:
                errors.append(f"missing evidence doc: {doc}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_ib_adaptive_defense_contract",
        description="Validate the I-B risk-targeted unlearning adaptive-defense hold contract.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Path to the I-B adaptive defense contract artifact (default: repository artifact path).",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    artifact_arg = args.artifact
    if artifact_arg is None:
        artifact_path = (root / DEFAULT_ARTIFACT).resolve()
    else:
        artifact_path = (artifact_arg if artifact_arg.is_absolute() else root / artifact_arg).resolve()

    errors: list[str] = []
    if not artifact_path.exists():
        errors.append(f"artifact does not exist: {artifact_path}")
    else:
        try:
            errors.extend(validate(_load_json(artifact_path)))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load artifact: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 2

    print(f"OK {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
