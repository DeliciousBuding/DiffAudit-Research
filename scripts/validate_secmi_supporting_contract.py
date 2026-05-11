from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT = Path("workspaces/gray-box/artifacts/secmi-full-split-admission-boundary-20260511.json")
DEFAULT_HARDENING_ARTIFACT = Path(
    "workspaces/gray-box/artifacts/secmi-admission-contract-hardening-20260511.json"
)
REQUIRED_METRICS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
REQUIRED_BLOCKERS = (
    "missing admitted-consumer boundary contract",
    "missing structured admitted-row cost/adaptive_check fields",
    "NNS auxiliary head needs an explicit product-facing scorer contract",
    "no bounded repeated-query adaptive review",
)
REQUIRED_HARDENING_DOCS = (
    "docs/evidence/secmi-full-split-admission-boundary-review.md",
    "docs/evidence/secmi-admission-contract-hardening-20260511.md",
)
REQUIRED_BLOCKED_CLAIMS = (
    "admitted Platform/Runtime row",
    "PIA replacement",
    "product-facing NNS auxiliary head",
    "adaptive robustness",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_numeric(errors: list[str], prefix: str, payload: dict[str, Any], fields: tuple[str, ...]) -> None:
    for field in fields:
        value = payload.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{prefix}.{field} must be numeric, got {value!r}")
        elif not math.isfinite(float(value)):
            errors.append(f"{prefix}.{field} must be finite, got {value!r}")
        elif not 0.0 <= float(value) <= 1.0:
            errors.append(f"{prefix}.{field} must be in [0, 1], got {value!r}")


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]
    if payload.get("schema") != "diffaudit.secmi_admission_boundary_review.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "evidence-ready-supporting-reference":
        errors.append("status must remain evidence-ready-supporting-reference")
    if payload.get("admitted") is not False:
        errors.append("SecMI supporting contract must not mark the row admitted")
    if payload.get("gpu_release") != "none":
        errors.append("SecMI supporting contract must not release GPU work")

    runtime = payload.get("secmi_runtime")
    if not isinstance(runtime, dict):
        errors.append("secmi_runtime must be an object")
    else:
        for field in ("member_samples", "nonmember_samples", "t_sec", "k", "batch_size"):
            value = runtime.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                errors.append(f"secmi_runtime.{field} must be a positive integer")

    for section in ("secmi_stat", "secmi_nns", "pia_admitted_baseline"):
        value = payload.get(section)
        if not isinstance(value, dict):
            errors.append(f"{section} must be an object")
            continue
        _require_numeric(errors, section, value, REQUIRED_METRICS)

    verdict = payload.get("verdict")
    if not isinstance(verdict, dict):
        errors.append("verdict must be an object")
    else:
        blockers = verdict.get("promotion_blockers")
        if not isinstance(blockers, list):
            errors.append("verdict.promotion_blockers must be a list")
        else:
            for blocker in REQUIRED_BLOCKERS:
                if blocker not in blockers:
                    errors.append(f"missing promotion blocker: {blocker}")
        blocked_claims = verdict.get("blocked_claims")
        if not isinstance(blocked_claims, list) or "admitted Platform/Runtime row" not in blocked_claims:
            errors.append("verdict.blocked_claims must block admitted Platform/Runtime row")

    return errors


def validate_hardening(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["hardening artifact must be a JSON object"]
    if payload.get("schema") != "diffaudit.secmi_admission_contract_hardening.v1":
        errors.append(f"unsupported hardening schema: {payload.get('schema')!r}")
    if payload.get("status") != "supporting-reference-hardened":
        errors.append("hardening status must remain supporting-reference-hardened")
    if payload.get("admitted") is not False:
        errors.append("SecMI hardening contract must not mark the row admitted")
    if payload.get("gpu_release") != "none":
        errors.append("SecMI hardening contract must not release GPU work")

    rows = payload.get("candidate_rows")
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("candidate_rows must contain exactly the stat and nns rows")
    else:
        heads = {row.get("head") for row in rows if isinstance(row, dict)}
        if heads != {"stat", "nns"}:
            errors.append(f"candidate_rows heads must be stat and nns, got {sorted(str(head) for head in heads)}")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"candidate_rows[{index}] must be an object")
                continue
            if row.get("consumer_decision") != "research-support-only":
                errors.append(f"candidate_rows[{index}].consumer_decision must be research-support-only")
            if row.get("admission_decision") != "blocked":
                errors.append(f"candidate_rows[{index}].admission_decision must be blocked")
            metrics = row.get("metrics")
            if not isinstance(metrics, dict):
                errors.append(f"candidate_rows[{index}].metrics must be an object")
            else:
                _require_numeric(errors, f"candidate_rows[{index}].metrics", metrics, REQUIRED_METRICS)
            missing = row.get("missing_for_admission")
            if not isinstance(missing, list) or "bounded repeated-query adaptive review" not in missing:
                errors.append(f"candidate_rows[{index}].missing_for_admission must include bounded repeated-query adaptive review")
            if row.get("head") == "nns" and (
                not isinstance(missing, list) or "explicit product-facing auxiliary-head contract" not in missing
            ):
                errors.append("NNS row must require an explicit product-facing auxiliary-head contract")

    blocked_claims = payload.get("blocked_claims")
    if not isinstance(blocked_claims, list):
        errors.append("blocked_claims must be a list")
    else:
        for claim in REQUIRED_BLOCKED_CLAIMS:
            if claim not in blocked_claims:
                errors.append(f"missing blocked claim: {claim}")

    reopen = payload.get("next_reopen_contract")
    if not isinstance(reopen, dict):
        errors.append("next_reopen_contract must be an object")
    else:
        if reopen.get("mode") != "CPU-first":
            errors.append("next_reopen_contract.mode must be CPU-first")
        if reopen.get("gpu_cap") != "none until the CPU contract is reviewed":
            errors.append("next_reopen_contract.gpu_cap must block GPU until CPU review")
        required = reopen.get("required_before_gpu")
        if not isinstance(required, list) or len(required) < 4:
            errors.append("next_reopen_contract.required_before_gpu must list the CPU gates")

    evidence_docs = payload.get("evidence_docs")
    if not isinstance(evidence_docs, list):
        errors.append("evidence_docs must be a list")
    else:
        for doc in REQUIRED_HARDENING_DOCS:
            if doc not in evidence_docs:
                errors.append(f"missing evidence doc: {doc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_secmi_supporting_contract",
        description="Validate the SecMI supporting-reference admission boundary contract.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Path to the SecMI boundary artifact (default: repository artifact path).",
    )
    parser.add_argument(
        "--hardening-artifact",
        type=Path,
        default=None,
        help="Path to the SecMI admission-contract hardening artifact.",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    artifact_path = (args.artifact or root / DEFAULT_ARTIFACT).resolve()
    errors: list[str] = []
    if not artifact_path.exists():
        errors.append(f"artifact does not exist: {artifact_path}")
    else:
        try:
            errors.extend(validate(_load_json(artifact_path)))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load artifact: {exc}")

    hardening_path = (args.hardening_artifact or root / DEFAULT_HARDENING_ARTIFACT).resolve()
    if not hardening_path.exists():
        errors.append(f"hardening artifact does not exist: {hardening_path}")
    else:
        try:
            errors.extend(validate_hardening(_load_json(hardening_path)))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load hardening artifact: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 2

    print(f"OK {artifact_path}")
    print(f"OK {hardening_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
