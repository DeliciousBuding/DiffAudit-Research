from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT = Path("workspaces/white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json")
REQUIRED_MUST_NOT_BE = (
    "scalar diffusion reconstruction loss under a new name",
    "plain gradient norm under a new name",
    "per-parameter gradient-norm dump from _extract_gsa_gradients_with_fixed_mask",
    "GSA loss-score threshold transfer",
    "GSA loss-score Gaussian likelihood-ratio transfer",
    "prior activation-subspace or channel-mask observable under a new name",
)
REQUIRED_BASELINES = (
    "scalar loss",
    "raw gradient norm",
    "GSA loss-score LR",
    "activation-subspace or masked-observability packet when available",
)
REQUIRED_OUTPUTS = (
    "extractor provenance",
    "feature dimensionality after truncation or projection",
    "score direction",
    "AUC",
    "ASR",
    "TPR@1%FPR",
    "TPR@0.1%FPR",
    "baseline comparison table",
    "runtime seconds",
    "failure reason if not runnable",
)
REQUIRED_BLOCKED_CLAIMS = (
    "admitted Platform/Runtime white-box row",
    "new white-box family established",
    "GPU packet authorized",
    "paper-level benchmark",
    "conditional diffusion generalization",
)
REQUIRED_DOCS = (
    "docs/evidence/post-secmi-next-lane-reselection-20260511.md",
    "docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_list_contains(errors: list[str], prefix: str, value: Any, required: tuple[str, ...]) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return
    for item in required:
        if item not in value:
            errors.append(f"{prefix} missing required item: {item}")


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]

    if payload.get("schema") != "diffaudit.whitebox_influence_curvature_feasibility.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "cpu-contract-ready":
        errors.append("status must be cpu-contract-ready")
    if payload.get("verdict") != "selected-cpu-first":
        errors.append("verdict must be selected-cpu-first")
    if payload.get("admitted") is not False:
        errors.append("white-box influence/curvature scout must not mark an admitted row")
    if payload.get("gpu_release") != "none":
        errors.append("white-box influence/curvature scout must not release GPU")

    asset_probe = payload.get("asset_probe")
    if not isinstance(asset_probe, dict):
        errors.append("asset_probe must be an object")
    else:
        if asset_probe.get("status") != "ready":
            errors.append("asset_probe.status must be ready")
        if asset_probe.get("repo_root") != "workspaces/white-box/external/GSA":
            errors.append("asset_probe.repo_root must use the workspace-scoped GSA checkout")
        if asset_probe.get("assets_root") != "workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1":
            errors.append("asset_probe.assets_root must use the reviewed GSA asset identity")
        bad_default = asset_probe.get("known_bad_default")
        if not isinstance(bad_default, dict) or bad_default.get("repo_root") != "external/GSA":
            errors.append("asset_probe.known_bad_default must record the non-runnable external/GSA default")

    observable = payload.get("candidate_observable")
    if not isinstance(observable, dict):
        errors.append("candidate_observable must be an object")
    else:
        raw_signal = observable.get("required_raw_signal", "")
        implementation_scope = observable.get("minimum_implementation_scope", "")
        score_family = observable.get("score_family", "")
        if "gradient vector" not in raw_signal:
            errors.append("candidate_observable.required_raw_signal must require non-scalar gradient vectors")
        if "selected-layer raw parameter gradients" not in implementation_scope:
            errors.append("candidate_observable.minimum_implementation_scope must require selected-layer raw gradients")
        if "F + lambda" not in score_family and "preconditioned" not in score_family:
            errors.append("candidate_observable.score_family must describe diagonal Fisher/preconditioned scoring")

    gate = payload.get("distinctness_gate")
    if not isinstance(gate, dict):
        errors.append("distinctness_gate must be an object")
    else:
        _require_list_contains(errors, "distinctness_gate.must_not_be", gate.get("must_not_be"), REQUIRED_MUST_NOT_BE)
        _require_list_contains(errors, "distinctness_gate.required_baselines", gate.get("required_baselines"), REQUIRED_BASELINES)
        release_rule = gate.get("release_rule")
        if not isinstance(release_rule, str) or "GPU stays blocked" not in release_rule:
            errors.append("distinctness_gate.release_rule must explicitly block GPU")

    micro_board = payload.get("cpu_micro_board_contract")
    if not isinstance(micro_board, dict):
        errors.append("cpu_micro_board_contract must be an object")
    else:
        if micro_board.get("mode") != "CPU-first":
            errors.append("cpu_micro_board_contract.mode must be CPU-first")
        for prefix in ("target_sample_cap", "shadow_sample_cap_per_shadow"):
            cap = micro_board.get(prefix)
            if not isinstance(cap, dict):
                errors.append(f"cpu_micro_board_contract.{prefix} must be an object")
                continue
            for split in ("member", "nonmember"):
                value = cap.get(split)
                if not isinstance(value, int) or isinstance(value, bool) or value <= 0 or value > 8:
                    errors.append(f"cpu_micro_board_contract.{prefix}.{split} must be a small positive integer <= 8")
        _require_list_contains(
            errors,
            "cpu_micro_board_contract.required_outputs",
            micro_board.get("required_outputs"),
            REQUIRED_OUTPUTS,
        )
        raw_policy = micro_board.get("raw_artifact_policy")
        if not isinstance(raw_policy, str) or "do not persist raw gradient tensors" not in raw_policy:
            errors.append("cpu_micro_board_contract.raw_artifact_policy must block default raw gradient tensor persistence")
        floor = micro_board.get("promotion_floor")
        if not isinstance(floor, dict):
            errors.append("cpu_micro_board_contract.promotion_floor must be an object")
        else:
            if floor.get("heldout_shadow_folds_improving_over_baselines") != 2:
                errors.append("promotion_floor must require 2 improving held-out shadow folds")
            if floor.get("total_shadow_folds") != 3:
                errors.append("promotion_floor must record 3 total shadow folds")
            if floor.get("target_must_not_regress_all_low_fpr_fields") is not True:
                errors.append("promotion_floor must protect low-FPR target fields")

    _require_list_contains(errors, "blocked_claims", payload.get("blocked_claims"), REQUIRED_BLOCKED_CLAIMS)
    _require_list_contains(errors, "evidence_docs", payload.get("evidence_docs"), REQUIRED_DOCS)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_whitebox_influence_curvature_contract",
        description="Validate the CPU-first white-box influence/curvature feasibility contract.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Path to the white-box influence/curvature feasibility artifact.",
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
            print(f"ERROR {error}", file=sys.stderr)
        return 2

    print(f"OK {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
