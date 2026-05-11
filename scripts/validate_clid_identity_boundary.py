from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT = Path("workspaces/black-box/artifacts/clid-image-identity-boundary-20260511.json")
REQUIRED_METRICS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
REQUIRED_BLOCKERS = (
    "prompt controls degrade strict-tail signal",
    "auxiliary feature is unstable under prompt controls",
    "no independent image-identity contract",
    "no Platform/Runtime consumer contract",
)
REQUIRED_BLOCKED_CLAIMS = (
    "admitted black-box evidence",
    "image-identity membership signal",
    "replacement for recon product row",
    "conditional-diffusion generalization",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_probability(
    errors: list[str],
    prefix: str,
    payload: dict[str, Any],
    fields: tuple[str, ...],
) -> None:
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

    if payload.get("schema") != "diffaudit.clid_image_identity_boundary.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "hold-candidate":
        errors.append("status must remain hold-candidate")
    if payload.get("admitted") is not False:
        errors.append("CLiD identity boundary must not mark the row admitted")
    if payload.get("gpu_release") != "none":
        errors.append("CLiD identity boundary must not release GPU work")

    baseline = payload.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline must be an object")
    else:
        _require_probability(errors, "baseline", baseline, REQUIRED_METRICS)
        if baseline.get("tpr_at_0_1pct_fpr") != 1.0:
            errors.append("baseline.tpr_at_0_1pct_fpr must preserve the prompt-conditioned strict-tail reference")

    controls = payload.get("controls")
    control_strict_tails: list[float] = []
    if not isinstance(controls, list) or not controls:
        errors.append("controls must be a non-empty list")
    else:
        for index, control in enumerate(controls):
            prefix = f"controls[{index}]"
            if not isinstance(control, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if not control.get("contract"):
                errors.append(f"{prefix}.contract must be non-empty")
            _require_probability(errors, prefix, control, REQUIRED_METRICS)
            strict_tail = control.get("tpr_at_0_1pct_fpr")
            if isinstance(strict_tail, (int, float)) and not isinstance(strict_tail, bool):
                control_strict_tails.append(float(strict_tail))
            retention = control.get("strict_tail_retention_vs_baseline")
            if not isinstance(retention, (int, float)) or isinstance(retention, bool):
                errors.append(f"{prefix}.strict_tail_retention_vs_baseline must be numeric")
            elif not math.isfinite(float(retention)) or not 0.0 <= float(retention) <= 1.0:
                errors.append(f"{prefix}.strict_tail_retention_vs_baseline must be finite and in [0, 1]")

    boundary = payload.get("identity_boundary")
    if not isinstance(boundary, dict):
        errors.append("identity_boundary must be an object")
    else:
        if boundary.get("image_identity_admitted") is not False:
            errors.append("identity_boundary.image_identity_admitted must be false")
        if boundary.get("prompt_conditioned_auxiliary_stable") is not False:
            errors.append("identity_boundary.prompt_conditioned_auxiliary_stable must be false")
        max_control = boundary.get("max_control_tpr_at_0_1pct_fpr")
        if not isinstance(max_control, (int, float)) or isinstance(max_control, bool):
            errors.append("identity_boundary.max_control_tpr_at_0_1pct_fpr must be numeric")
        elif control_strict_tails and round(max(control_strict_tails), 6) != round(float(max_control), 6):
            errors.append("identity_boundary.max_control_tpr_at_0_1pct_fpr must match max control strict tail")
        if isinstance(max_control, (int, float)) and not isinstance(max_control, bool) and float(max_control) > 0.25:
            errors.append("identity_boundary.max_control_tpr_at_0_1pct_fpr is too high for hold-candidate boundary")

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

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_clid_identity_boundary",
        description="Validate the CLiD prompt-conditioned image-identity boundary contract.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Path to the CLiD identity boundary artifact (default: repository artifact path).",
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

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 2

    print(f"OK {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
