from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from diffaudit.attacks.gsa_observability import (
    _load_gsa_unet_checkpoint,
    resolve_gsa_layer_selector,
    validate_gsa_workspace,
)

try:
    from run_x145_activation_subspace_gpu_scout import (
        _capture_profile,
        _score_from_subspace,
    )
except ModuleNotFoundError:  # pragma: no cover - supports `python -m scripts...`
    from scripts.run_x145_activation_subspace_gpu_scout import (
        _capture_profile,
        _score_from_subspace,
    )


DEFAULT_MEMBER_IDS = [
    "00-data_batch_1-00965",
    "00-data_batch_1-01493",
    "00-data_batch_1-01674",
    "00-data_batch_1-02478",
    "00-data_batch_1-02662",
    "00-data_batch_1-02964",
    "00-data_batch_1-04080",
    "00-data_batch_1-04081",
    "00-data_batch_1-04314",
    "00-data_batch_1-04348",
    "00-data_batch_1-04621",
    "00-data_batch_1-05331",
    "00-data_batch_1-05349",
    "00-data_batch_1-05470",
    "00-data_batch_1-05587",
    "00-data_batch_1-05696",
]

DEFAULT_NONMEMBER_IDS = [
    "00-data_batch_1-00467",
    "00-data_batch_1-01278",
    "00-data_batch_1-02287",
    "00-data_batch_1-02578",
    "00-data_batch_1-02848",
    "00-data_batch_1-02946",
    "00-data_batch_1-03263",
    "00-data_batch_1-03352",
    "00-data_batch_1-04018",
    "00-data_batch_1-04523",
    "00-data_batch_1-04787",
    "00-data_batch_1-05010",
    "00-data_batch_1-05426",
    "00-data_batch_1-05873",
    "00-data_batch_1-07212",
    "00-data_batch_1-07788",
]


def _split_matrix(
    matrix: torch.Tensor,
    *,
    selector_count: int,
    validation_count: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if selector_count <= 0 or validation_count <= 0:
        raise ValueError("selector_count and validation_count must be positive.")
    holdout_count = int(matrix.shape[0]) - int(selector_count) - int(validation_count)
    if holdout_count <= 0:
        raise ValueError("Need at least one holdout sample after selector and validation splits.")
    return (
        matrix[:selector_count],
        matrix[selector_count : selector_count + validation_count],
        matrix[selector_count + validation_count :],
    )


def _select_validation_stable_subspace(
    *,
    selector_member_matrix: torch.Tensor,
    selector_nonmember_matrix: torch.Tensor,
    validation_member_matrix: torch.Tensor,
    validation_nonmember_matrix: torch.Tensor,
    top_k: int,
    candidate_multiplier: int,
) -> dict[str, Any]:
    selector_delta = selector_member_matrix.mean(dim=0) - selector_nonmember_matrix.mean(dim=0)
    validation_delta = validation_member_matrix.mean(dim=0) - validation_nonmember_matrix.mean(dim=0)

    top_k = min(int(top_k), int(selector_delta.numel()))
    candidate_count = min(max(top_k * int(candidate_multiplier), top_k), int(selector_delta.numel()))
    candidate_values, candidate_indices = torch.topk(selector_delta.abs(), k=candidate_count)

    selector_sign = torch.sign(selector_delta[candidate_indices])
    validation_sign = torch.sign(validation_delta[candidate_indices])
    selector_sign[selector_sign == 0] = 1
    validation_sign[validation_sign == 0] = 1
    sign_consistent = selector_sign == validation_sign

    stable_indices = candidate_indices[sign_consistent]
    stable_selector_abs_delta = selector_delta[stable_indices].abs()
    stable_validation_abs_delta = validation_delta[stable_indices].abs()
    stable_score = torch.minimum(stable_selector_abs_delta, stable_validation_abs_delta)

    if int(stable_indices.numel()) == 0:
        raise RuntimeError("No validation-stable activation channels survived sign-consistency filtering.")

    selected_count = min(top_k, int(stable_indices.numel()))
    selected_scores, selected_order = torch.topk(stable_score, k=selected_count)
    selected_indices = stable_indices[selected_order]
    direction = torch.sign(selector_delta[selected_indices])
    direction[direction == 0] = 1

    baseline_values, baseline_indices = torch.topk(selector_delta.abs(), k=top_k)
    baseline_direction = torch.sign(selector_delta[baseline_indices])
    baseline_direction[baseline_direction == 0] = 1

    return {
        "top_indices": selected_indices,
        "direction": direction,
        "stable_score": selected_scores,
        "selector_abs_delta": selector_delta[selected_indices].abs(),
        "validation_abs_delta": validation_delta[selected_indices].abs(),
        "candidate_indices": candidate_indices,
        "candidate_abs_delta": candidate_values,
        "sign_consistent_count": int(sign_consistent.sum().item()),
        "candidate_count": int(candidate_count),
        "baseline_top_indices": baseline_indices,
        "baseline_direction": baseline_direction,
        "baseline_abs_delta": baseline_values,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run X-148 validation-regularized activation-subspace scout on admitted GSA/CIFAR10 assets. "
            "This is a bounded GPU preflight after X-145/X-146 overfit, not a headline result."
        )
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("workspaces/white-box/runs/x148-activation-subspace-regularized-scout-20260429-r1"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("workspaces/white-box/external/GSA"))
    parser.add_argument(
        "--assets-root",
        type=Path,
        default=Path("workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1"),
    )
    parser.add_argument(
        "--checkpoint-root",
        type=Path,
        default=Path("workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target"),
    )
    parser.add_argument("--checkpoint-dir", type=Path, default=None)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--layer-selector", default="mid_block.attentions.0.to_v")
    parser.add_argument("--timesteps", nargs="+", type=int, default=[250, 500, 750, 999])
    parser.add_argument("--noise-seed", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--candidate-multiplier", type=int, default=4)
    parser.add_argument("--selector-count", type=int, default=8)
    parser.add_argument("--validation-count", type=int, default=4)
    parser.add_argument("--resolution", type=int, default=32)
    parser.add_argument("--ddpm-num-steps", type=int, default=1000)
    parser.add_argument("--prediction-type", default="epsilon")
    parser.add_argument("--member-ids", nargs="+", default=DEFAULT_MEMBER_IDS)
    parser.add_argument("--nonmember-ids", nargs="+", default=DEFAULT_NONMEMBER_IDS)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.device.startswith("cuda"):
        raise ValueError("X-148 is a bounded GPU scout; pass a cuda device.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available for X-148 activation-subspace scout.")
    if len(args.member_ids) != len(args.nonmember_ids):
        raise ValueError("X-148 requires paired member/nonmember counts.")
    if args.workspace.exists() and any(args.workspace.iterdir()) and not args.overwrite:
        raise FileExistsError(f"Workspace exists and is not empty: {args.workspace}. Pass --overwrite to replace.")

    args.workspace.mkdir(parents=True, exist_ok=True)
    validate_gsa_workspace(args.repo_root)
    selector = resolve_gsa_layer_selector(args.layer_selector, resolution=args.resolution)
    model, resolved_checkpoint_dir = _load_gsa_unet_checkpoint(
        checkpoint_root=args.checkpoint_root,
        checkpoint_dir=args.checkpoint_dir,
        resolution=args.resolution,
        device=args.device,
    )

    records: list[dict[str, Any]] = []
    profiles: dict[str, list[torch.Tensor]] = {"member": [], "nonmember": []}
    sample_specs = [
        ("member", "target-member", sample_id) for sample_id in args.member_ids
    ] + [
        ("nonmember", "target-nonmember", sample_id) for sample_id in args.nonmember_ids
    ]
    for role, split, sample_id in sample_specs:
        payload = _capture_profile(
            model=model,
            assets_root=args.assets_root,
            split=split,
            sample_id=sample_id,
            layer_id=selector["layer_id"],
            timesteps=args.timesteps,
            noise_seed=args.noise_seed,
            prediction_type=args.prediction_type,
            ddpm_num_steps=args.ddpm_num_steps,
            resolution=args.resolution,
            device=args.device,
        )
        profiles[role].append(payload["profile"])
        records.append(
            {
                "role": role,
                "split": split,
                "sample_id": payload["binding"]["sample_id"],
                "dataset_relpath": payload["binding"]["dataset_relpath"],
                "profile_shape": list(payload["profile"].shape),
                "profile_mean": float(payload["profile"].mean().item()),
                "profile_std": float(payload["profile"].std(unbiased=False).item()),
            }
        )

    member_matrix = torch.stack(profiles["member"], dim=0)
    nonmember_matrix = torch.stack(profiles["nonmember"], dim=0)
    selector_member_matrix, validation_member_matrix, holdout_member_matrix = _split_matrix(
        member_matrix,
        selector_count=args.selector_count,
        validation_count=args.validation_count,
    )
    selector_nonmember_matrix, validation_nonmember_matrix, holdout_nonmember_matrix = _split_matrix(
        nonmember_matrix,
        selector_count=args.selector_count,
        validation_count=args.validation_count,
    )

    selected = _select_validation_stable_subspace(
        selector_member_matrix=selector_member_matrix,
        selector_nonmember_matrix=selector_nonmember_matrix,
        validation_member_matrix=validation_member_matrix,
        validation_nonmember_matrix=validation_nonmember_matrix,
        top_k=args.top_k,
        candidate_multiplier=args.candidate_multiplier,
    )

    selector_metrics = _score_from_subspace(
        selector_member_matrix,
        selector_nonmember_matrix,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    validation_metrics = _score_from_subspace(
        validation_member_matrix,
        validation_nonmember_matrix,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    holdout_metrics = _score_from_subspace(
        holdout_member_matrix,
        holdout_nonmember_matrix,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    baseline_holdout_metrics = _score_from_subspace(
        holdout_member_matrix,
        holdout_nonmember_matrix,
        top_indices=selected["baseline_top_indices"],
        direction=selected["baseline_direction"],
    )
    pooled_metrics = _score_from_subspace(
        member_matrix,
        nonmember_matrix,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )

    profile_artifact = args.workspace / "activation-subspace-regularized-profiles.pt"
    torch.save(
        {
            "member_matrix": member_matrix,
            "nonmember_matrix": nonmember_matrix,
            "selector_member_matrix": selector_member_matrix,
            "selector_nonmember_matrix": selector_nonmember_matrix,
            "validation_member_matrix": validation_member_matrix,
            "validation_nonmember_matrix": validation_nonmember_matrix,
            "holdout_member_matrix": holdout_member_matrix,
            "holdout_nonmember_matrix": holdout_nonmember_matrix,
            "top_indices": selected["top_indices"],
            "stable_score": selected["stable_score"],
            "selector_abs_delta": selected["selector_abs_delta"],
            "validation_abs_delta": selected["validation_abs_delta"],
            "baseline_top_indices": selected["baseline_top_indices"],
        },
        profile_artifact,
    )
    records_path = args.workspace / "records.jsonl"
    records_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in records) + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema": "diffaudit.x148_activation_subspace_regularized_gpu_scout.v1",
        "status": "ready",
        "track": "white-box",
        "method": "activation-subspace-validation-regularized-scout",
        "mode": "gpu-preflight-scout",
        "verdict_scope": "bounded preflight only",
        "gpu_release": "bounded-scout",
        "admitted_change": "none",
        "workspace": str(args.workspace.as_posix()),
        "device": args.device,
        "contract": {
            "repo_root": str(args.repo_root.as_posix()),
            "assets_root": str(args.assets_root.as_posix()),
            "checkpoint_root": str(args.checkpoint_root.as_posix()),
            "resolved_checkpoint_dir": str(resolved_checkpoint_dir.as_posix()),
            "layer_selector": args.layer_selector,
            "layer_id": selector["layer_id"],
            "timesteps": args.timesteps,
            "noise_seed": args.noise_seed,
            "top_k": min(int(args.top_k), int(selected["top_indices"].numel())),
            "candidate_multiplier": int(args.candidate_multiplier),
            "member_count": len(args.member_ids),
            "nonmember_count": len(args.nonmember_ids),
            "selector_count": int(args.selector_count),
            "validation_count": int(args.validation_count),
            "holdout_count": int(holdout_member_matrix.shape[0]),
            "batching": "single-sample loop",
        },
        "metrics": {
            "selector": selector_metrics,
            "validation": validation_metrics,
            "holdout": holdout_metrics,
            "baseline_top_delta_holdout": baseline_holdout_metrics,
            "pooled": pooled_metrics,
        },
        "selection": {
            "candidate_count": selected["candidate_count"],
            "sign_consistent_count": selected["sign_consistent_count"],
            "selected_count": int(selected["top_indices"].numel()),
            "top_indices": [int(value) for value in selected["top_indices"].tolist()],
            "stable_score": [round(float(value), 8) for value in selected["stable_score"].tolist()],
            "selector_abs_delta": [round(float(value), 8) for value in selected["selector_abs_delta"].tolist()],
            "validation_abs_delta": [round(float(value), 8) for value in selected["validation_abs_delta"].tolist()],
            "baseline_top_indices": [int(value) for value in selected["baseline_top_indices"].tolist()],
            "baseline_abs_delta": [round(float(value), 8) for value in selected["baseline_abs_delta"].tolist()],
        },
        "artifact_paths": {
            "summary": "summary.json",
            "records": "records.jsonl",
            "profiles": profile_artifact.name,
        },
        "notes": [
            "X-148 changes the X-145/X-146 selector rule: channels must survive a validation sign-consistency filter before holdout scoring.",
            "The packet remains intentionally small and does not promote a white-box second family.",
            "Holdout metrics are the verdict surface; selector and validation metrics are diagnostic only.",
            (
                "Low-FPR fields are reported but are coarse at "
                f"{int(holdout_member_matrix.shape[0])}/{int(holdout_nonmember_matrix.shape[0])} holdout scale; "
                "treat them as preflight diagnostics only."
            ),
        ],
    }
    (args.workspace / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
