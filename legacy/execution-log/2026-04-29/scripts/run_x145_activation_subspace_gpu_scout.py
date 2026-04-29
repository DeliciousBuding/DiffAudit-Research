from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from diffaudit.attacks.gsa_observability import (
    _capture_activation_tensor,
    _channelwise_profile,
    _load_gsa_unet_checkpoint,
    _load_image_tensor,
    _prepare_noisy_sample,
    resolve_gsa_layer_selector,
    resolve_gsa_sample_binding,
    validate_gsa_workspace,
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
]


def _auc(member_scores: list[float], nonmember_scores: list[float]) -> float:
    if not member_scores or not nonmember_scores:
        return 0.0
    wins = 0.0
    total = float(len(member_scores) * len(nonmember_scores))
    for member_score in member_scores:
        for nonmember_score in nonmember_scores:
            if member_score > nonmember_score:
                wins += 1.0
            elif member_score == nonmember_score:
                wins += 0.5
    return wins / total


def _tpr_at_fpr(member_scores: list[float], nonmember_scores: list[float], fpr: float) -> float:
    if not member_scores or not nonmember_scores:
        return 0.0
    false_positive_budget = int(float(fpr) * len(nonmember_scores))
    ordered_nonmembers = sorted(nonmember_scores, reverse=True)
    if false_positive_budget <= 0:
        threshold = ordered_nonmembers[0]
        return sum(score > threshold for score in member_scores) / float(len(member_scores))
    threshold = ordered_nonmembers[min(false_positive_budget - 1, len(ordered_nonmembers) - 1)]
    return sum(score >= threshold for score in member_scores) / float(len(member_scores))


def _as_float_list(tensor: torch.Tensor) -> list[float]:
    return [float(value) for value in tensor.detach().cpu().reshape(-1).tolist()]


def _score_from_subspace(
    member_matrix: torch.Tensor,
    nonmember_matrix: torch.Tensor,
    *,
    top_indices: torch.Tensor,
    direction: torch.Tensor,
) -> dict[str, Any]:
    member_scores_tensor = (member_matrix[:, top_indices] * direction).mean(dim=1)
    nonmember_scores_tensor = (nonmember_matrix[:, top_indices] * direction).mean(dim=1)
    member_scores = _as_float_list(member_scores_tensor)
    nonmember_scores = _as_float_list(nonmember_scores_tensor)
    auc = _auc(member_scores, nonmember_scores)
    return {
        "auc": round(auc, 6),
        "asr": round(max(auc, 1.0 - auc), 6),
        "tpr_at_1pct_fpr": round(_tpr_at_fpr(member_scores, nonmember_scores, 0.01), 6),
        "tpr_at_0_1pct_fpr": round(_tpr_at_fpr(member_scores, nonmember_scores, 0.001), 6),
        "member_scores": member_scores,
        "nonmember_scores": nonmember_scores,
    }


def _capture_profile(
    *,
    model: torch.nn.Module,
    assets_root: Path,
    split: str,
    sample_id: str,
    layer_id: str,
    timesteps: list[int],
    noise_seed: int,
    prediction_type: str,
    ddpm_num_steps: int,
    resolution: int,
    device: str,
) -> dict[str, Any]:
    binding = resolve_gsa_sample_binding(assets_root, split=split, sample_id=sample_id)
    sample_tensor = _load_image_tensor(binding["absolute_path"], resolution=resolution).to(device)
    timestep_profiles: list[torch.Tensor] = []
    for timestep in timesteps:
        noisy_sample = _prepare_noisy_sample(
            sample_tensor=sample_tensor,
            timestep=int(timestep),
            noise_seed=int(noise_seed),
            prediction_type=prediction_type,
            ddpm_num_steps=int(ddpm_num_steps),
        )
        activation = _capture_activation_tensor(
            model=model,
            layer_id=layer_id,
            noisy_sample=noisy_sample,
            timestep=int(timestep),
        )
        timestep_profiles.append(_channelwise_profile(activation).to(torch.float32))
    profile = torch.stack(timestep_profiles, dim=0).mean(dim=0)
    return {
        "binding": binding,
        "profile": profile,
        "timesteps": timesteps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a bounded X-145 GPU activation-subspace scout on admitted GSA/CIFAR10 assets. "
            "This is a preflight scout, not an admitted white-box headline."
        )
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("workspaces/white-box/runs/x145-activation-subspace-gpu-scout-20260429-r1"),
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
        raise ValueError("X-145 is the GPU-safe scout; pass a cuda device or choose a different CPU contract.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available for X-145 activation-subspace scout.")
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
    holdout_start = max(1, len(args.member_ids) // 2)
    if holdout_start >= len(args.member_ids) or holdout_start >= len(args.nonmember_ids):
        raise ValueError("X-145 holdout split requires at least two members and two nonmembers.")
    train_member_matrix = member_matrix[:holdout_start]
    train_nonmember_matrix = nonmember_matrix[:holdout_start]
    eval_member_matrix = member_matrix[holdout_start:]
    eval_nonmember_matrix = nonmember_matrix[holdout_start:]

    train_member_mean = train_member_matrix.mean(dim=0)
    train_nonmember_mean = train_nonmember_matrix.mean(dim=0)
    signed_delta = train_member_mean - train_nonmember_mean
    abs_delta = signed_delta.abs()
    top_k = min(int(args.top_k), int(abs_delta.numel()))
    top_values, top_indices = torch.topk(abs_delta, k=top_k)
    direction = torch.sign(signed_delta[top_indices])
    direction[direction == 0] = 1

    train_metrics = _score_from_subspace(
        train_member_matrix,
        train_nonmember_matrix,
        top_indices=top_indices,
        direction=direction,
    )
    holdout_metrics = _score_from_subspace(
        eval_member_matrix,
        eval_nonmember_matrix,
        top_indices=top_indices,
        direction=direction,
    )
    in_sample_metrics = _score_from_subspace(
        member_matrix,
        nonmember_matrix,
        top_indices=top_indices,
        direction=direction,
    )

    profile_artifact = args.workspace / "activation-subspace-profiles.pt"
    torch.save(
        {
            "member_matrix": member_matrix,
            "nonmember_matrix": nonmember_matrix,
            "train_member_matrix": train_member_matrix,
            "train_nonmember_matrix": train_nonmember_matrix,
            "eval_member_matrix": eval_member_matrix,
            "eval_nonmember_matrix": eval_nonmember_matrix,
            "top_indices": top_indices,
            "top_abs_delta": top_values,
        },
        profile_artifact,
    )
    records_path = args.workspace / "records.jsonl"
    records_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in records) + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema": "diffaudit.x145_activation_subspace_gpu_scout.v1",
        "status": "ready",
        "track": "white-box",
        "method": "activation-subspace-scout",
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
            "top_k": top_k,
            "member_count": len(args.member_ids),
            "nonmember_count": len(args.nonmember_ids),
            "batching": "single-sample loop",
        },
        "metrics": holdout_metrics,
        "train_metrics": train_metrics,
        "in_sample_metrics": in_sample_metrics,
        "subspace": {
            "top_indices": [int(value) for value in top_indices.tolist()],
            "top_abs_delta": [round(float(value), 8) for value in top_values.tolist()],
            "mean_top_abs_delta": round(float(top_values.mean().item()), 8),
            "selection_split": {
                "train_member_count": int(train_member_matrix.shape[0]),
                "train_nonmember_count": int(train_nonmember_matrix.shape[0]),
                "holdout_member_count": int(eval_member_matrix.shape[0]),
                "holdout_nonmember_count": int(eval_nonmember_matrix.shape[0]),
            },
        },
        "artifact_paths": {
            "summary": "summary.json",
            "records": "records.jsonl",
            "profiles": profile_artifact.name,
        },
        "notes": [
            "This is a GPU-safe activation-subspace scout, not the older CPU-only Finding NeMo canary.",
            "The packet is intentionally small and does not promote a white-box second family.",
            "Top-k channels are selected on the first half of each role and reported metrics are computed on the held-out half.",
            (
                "Low-FPR fields are reported but are coarse at "
                f"{int(eval_member_matrix.shape[0])}/{int(eval_nonmember_matrix.shape[0])} holdout scale; "
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
