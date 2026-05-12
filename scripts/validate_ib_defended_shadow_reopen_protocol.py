from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT = Path("workspaces/defense/artifacts/ib-defended-shadow-reopen-protocol-20260512.json")
REQUIRED_PRIMARY_METRICS = ("AUC", "ASR", "TPR@1%FPR", "TPR@0.1%FPR", "retained_utility")
REQUIRED_IDENTITY_FIELDS = (
    "target_checkpoint",
    "member_split",
    "nonmember_split",
    "forget_set",
    "retain_set",
)
REQUIRED_EVIDENCE_DOCS = (
    "docs/evidence/ib-adaptive-defense-contract-20260511.md",
    "docs/evidence/ib-defense-reopen-protocol-audit-20260512.md",
    "docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_non_empty(errors: list[str], prefix: str, payload: dict[str, Any], field: str) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}.{field} must be non-empty")


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]

    if payload.get("schema") != "diffaudit.ib_defended_shadow_reopen_protocol.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "protocol-frozen":
        errors.append("status must be protocol-frozen")
    if payload.get("admitted") is not False:
        errors.append("protocol must not mark the row admitted")
    if payload.get("gpu_release") != "none":
        errors.append("protocol must not release GPU work")

    hypothesis = payload.get("hypothesis")
    if not isinstance(hypothesis, str) or not hypothesis.strip():
        errors.append("hypothesis must be non-empty")

    falsifier = payload.get("falsifier")
    if not isinstance(falsifier, str) or not falsifier.strip():
        errors.append("falsifier must be non-empty")

    defended_shadow = payload.get("defended_shadow_training_protocol")
    if not isinstance(defended_shadow, dict):
        errors.append("defended_shadow_training_protocol must be an object")
    else:
        _require_non_empty(errors, "defended_shadow_training_protocol", defended_shadow, "entrypoint")
        if defended_shadow.get("shadow_type") != "defended":
            errors.append("defended_shadow_training_protocol.shadow_type must be defended")
        if defended_shadow.get("budget") != "tiny-first":
            errors.append("defended_shadow_training_protocol.budget must be tiny-first")
        if defended_shadow.get("raw_asset_policy") != "no-git-large-artifacts":
            errors.append(
                "defended_shadow_training_protocol.raw_asset_policy must be no-git-large-artifacts"
            )

    adaptive_attacker = payload.get("adaptive_attacker_protocol")
    if not isinstance(adaptive_attacker, dict):
        errors.append("adaptive_attacker_protocol must be an object")
    else:
        _require_non_empty(errors, "adaptive_attacker_protocol", adaptive_attacker, "entrypoint")
        if adaptive_attacker.get("threshold_reference") != "defended-shadows":
            errors.append(
                "adaptive_attacker_protocol.threshold_reference must be defended-shadows"
            )
        if adaptive_attacker.get("baseline_reference") != "matched-undefended-target":
            errors.append(
                "adaptive_attacker_protocol.baseline_reference must be matched-undefended-target"
            )
        if adaptive_attacker.get("attacker_knows_defense") is not True:
            errors.append("adaptive_attacker_protocol.attacker_knows_defense must be true")

    identity = payload.get("identity_contract")
    if not isinstance(identity, dict):
        errors.append("identity_contract must be an object")
    else:
        for field in REQUIRED_IDENTITY_FIELDS:
            if identity.get(field) != "fixed":
                errors.append(f"identity_contract.{field} must be fixed")

    primary_metrics = payload.get("primary_metrics")
    if not isinstance(primary_metrics, list):
        errors.append("primary_metrics must be a list")
    else:
        for metric in REQUIRED_PRIMARY_METRICS:
            if metric not in primary_metrics:
                errors.append(f"missing primary metric: {metric}")

    finite_tail = payload.get("finite_tail_contract")
    if not isinstance(finite_tail, dict):
        errors.append("finite_tail_contract must be an object")
    else:
        if finite_tail.get("report_denominators") is not True:
            errors.append("finite_tail_contract.report_denominators must be true")
        if finite_tail.get("continuous_subpercent_claim") is not False:
            errors.append("finite_tail_contract.continuous_subpercent_claim must be false")

    stop_conditions = payload.get("stop_conditions")
    if not isinstance(stop_conditions, dict):
        errors.append("stop_conditions must be an object")
    else:
        if stop_conditions.get("no_strict_tail_improvement") != "close-line":
            errors.append("stop_conditions.no_strict_tail_improvement must be close-line")
        if stop_conditions.get("retained_utility_regresses") != "close-line":
            errors.append("stop_conditions.retained_utility_regresses must be close-line")
        if stop_conditions.get("defended_shadow_training_not_available") != "blocked":
            errors.append("stop_conditions.defended_shadow_training_not_available must be blocked")

    blocked_claims = payload.get("blocked_claims")
    if not isinstance(blocked_claims, list):
        errors.append("blocked_claims must be a list")
    else:
        for claim in (
            "admitted defense evidence",
            "adaptive robustness",
            "Platform/Runtime defense row",
            "old undefended threshold-transfer GPU packet",
            "GPU packet authorized",
        ):
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
        prog="validate_ib_defended_shadow_reopen_protocol",
        description="Validate the I-B defended-shadow/adaptive-attacker reopen protocol.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Path to the I-B reopen protocol artifact (default: repository artifact path).",
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
