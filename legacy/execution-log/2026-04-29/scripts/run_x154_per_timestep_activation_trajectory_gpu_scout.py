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

DEFAULT_FEATURES = [
    "mean_profile",
    "late_minus_early",
    "linear_slope",
    "early_late_gap",
    "trajectory_energy",
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


def _mean_delta(member_matrix: torch.Tensor, nonmember_matrix: torch.Tensor) -> torch.Tensor:
    return member_matrix.mean(dim=0) - nonmember_matrix.mean(dim=0)


def _nonzero_sign(tensor: torch.Tensor) -> torch.Tensor:
    sign = torch.sign(tensor)
    sign[sign == 0] = 0
    return sign


def _build_trajectory_feature(trajectories: torch.Tensor, feature_name: str) -> torch.Tensor:
    if trajectories.ndim != 3:
        raise ValueError("trajectories must have shape [samples, timesteps, channels].")
    if int(trajectories.shape[1]) < 2:
        raise ValueError("at least two timesteps are required for trajectory features.")

    if feature_name == "mean_profile":
        return trajectories.mean(dim=1)
    if feature_name == "late_minus_early":
        return trajectories[:, -1, :] - trajectories[:, 0, :]
    if feature_name == "early_late_gap":
        midpoint = int(trajectories.shape[1]) // 2
        return trajectories[:, midpoint:, :].mean(dim=1) - trajectories[:, :midpoint, :].mean(dim=1)
    if feature_name == "trajectory_energy":
        return trajectories.diff(dim=1).abs().mean(dim=1)
    if feature_name == "linear_slope":
        time = torch.linspace(0.0, 1.0, int(trajectories.shape[1]), device=trajectories.device)
        centered = time - time.mean()
        denominator = torch.sum(centered * centered)
        return (trajectories * centered.view(1, -1, 1)).sum(dim=1) / denominator
    raise ValueError(f"Unknown trajectory feature: {feature_name}")


def _select_validation_stable_subspace(
    *,
    selector_member_matrix: torch.Tensor,
    selector_nonmember_matrix: torch.Tensor,
    validation_member_matrix: torch.Tensor,
    validation_nonmember_matrix: torch.Tensor,
    top_k: int,
    candidate_multiplier: int,
) -> dict[str, Any]:
    selector_delta = _mean_delta(selector_member_matrix, selector_nonmember_matrix)
    validation_delta = _mean_delta(validation_member_matrix, validation_nonmember_matrix)
    top_k = min(int(top_k), int(selector_delta.numel()))
    candidate_count = min(max(top_k * int(candidate_multiplier), top_k), int(selector_delta.numel()))
    candidate_values, candidate_indices = torch.topk(selector_delta.abs(), k=candidate_count)
    selector_sign = _nonzero_sign(selector_delta[candidate_indices])
    validation_sign = _nonzero_sign(validation_delta[candidate_indices])
    stable_mask = (selector_sign != 0) & (selector_sign == validation_sign)
    stable_indices = candidate_indices[stable_mask]
    if int(stable_indices.numel()) == 0:
        raise RuntimeError("No validation-stable trajectory channels survived sign filtering.")
    stable_score = torch.minimum(selector_delta[stable_indices].abs(), validation_delta[stable_indices].abs())
    selected_count = min(top_k, int(stable_indices.numel()))
    selected_scores, selected_order = torch.topk(stable_score, k=selected_count)
    selected_indices = stable_indices[selected_order]
    direction = torch.sign(selector_delta[selected_indices])
    direction[direction == 0] = 1
    return {
        "top_indices": selected_indices,
        "direction": direction,
        "stable_score": selected_scores,
        "candidate_count": int(candidate_count),
        "sign_consistent_count": int(stable_mask.sum().item()),
        "candidate_indices": candidate_indices,
        "candidate_abs_delta": candidate_values,
        "selector_abs_delta": selector_delta[selected_indices].abs(),
        "validation_abs_delta": validation_delta[selected_indices].abs(),
    }


def _rank_feature_candidate(candidate: dict[str, Any]) -> tuple[float, float, float, float]:
    validation_metrics = candidate["metrics"]["validation"]
    return (
        float(validation_metrics["auc"]),
        float(validation_metrics["tpr_at_1pct_fpr"]),
        float(validation_metrics["tpr_at_0_1pct_fpr"]),
        float(sum(candidate["selection"]["stable_score"])),
    )


def _select_trajectory_feature(
    *,
    feature_matrices: dict[str, dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]],
    feature_names: list[str],
    top_k: int,
    candidate_multiplier: int,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    failures: dict[str, str] = {}
    for feature_name in feature_names:
        try:
            member_selector, member_validation, member_holdout = feature_matrices[feature_name]["member"]
            nonmember_selector, nonmember_validation, nonmember_holdout = feature_matrices[feature_name]["nonmember"]
            selected = _select_validation_stable_subspace(
                selector_member_matrix=member_selector,
                selector_nonmember_matrix=nonmember_selector,
                validation_member_matrix=member_validation,
                validation_nonmember_matrix=nonmember_validation,
                top_k=top_k,
                candidate_multiplier=candidate_multiplier,
            )
            metrics = {
                "selector": _score_from_subspace(
                    member_selector,
                    nonmember_selector,
                    top_indices=selected["top_indices"],
                    direction=selected["direction"],
                ),
                "validation": _score_from_subspace(
                    member_validation,
                    nonmember_validation,
                    top_indices=selected["top_indices"],
                    direction=selected["direction"],
                ),
                "holdout": _score_from_subspace(
                    member_holdout,
                    nonmember_holdout,
                    top_indices=selected["top_indices"],
                    direction=selected["direction"],
                ),
            }
            candidates.append(
                {
                    "feature": feature_name,
                    "selection": selected,
                    "metrics": metrics,
                }
            )
        except Exception as exc:  # keep diagnostics for failed feature families
            failures[feature_name] = f"{type(exc).__name__}: {exc}"
    if not candidates:
        raise RuntimeError(f"No trajectory feature candidate survived selection: {failures}")
    candidates.sort(key=_rank_feature_candidate, reverse=True)
    return {
        "selected": candidates[0],
        "candidates": candidates,
        "failures": failures,
    }


def _capture_trajectory(
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
    return {
        "binding": binding,
        "trajectory": torch.stack(timestep_profiles, dim=0),
        "timesteps": timesteps,
    }


def _json_selection(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_count": selection["candidate_count"],
        "sign_consistent_count": selection["sign_consistent_count"],
        "selected_count": int(selection["top_indices"].numel()),
        "top_indices": [int(value) for value in selection["top_indices"].tolist()],
        "direction": [float(value) for value in selection["direction"].tolist()],
        "stable_score": [round(float(value), 8) for value in selection["stable_score"].tolist()],
        "selector_abs_delta": [round(float(value), 8) for value in selection["selector_abs_delta"].tolist()],
        "validation_abs_delta": [round(float(value), 8) for value in selection["validation_abs_delta"].tolist()],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run X-154 per-timestep activation-trajectory scout on admitted GSA/CIFAR10 assets. "
            "This is the single bounded GPU scout released by X-153, not a headline result."
        )
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("workspaces/white-box/runs/x154-per-timestep-activation-trajectory-scout-20260429-r1"),
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
    parser.add_argument("--trajectory-features", nargs="+", default=DEFAULT_FEATURES)
    parser.add_argument("--noise-seed", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=8)
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
        raise ValueError("X-154 is a bounded GPU scout; pass a cuda device.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available for X-154 activation-trajectory scout.")
    if len(args.member_ids) != len(args.nonmember_ids):
        raise ValueError("X-154 requires paired member/nonmember counts.")
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
    trajectories: dict[str, list[torch.Tensor]] = {"member": [], "nonmember": []}
    sample_specs = [
        ("member", "target-member", sample_id) for sample_id in args.member_ids
    ] + [
        ("nonmember", "target-nonmember", sample_id) for sample_id in args.nonmember_ids
    ]
    for role, split, sample_id in sample_specs:
        payload = _capture_trajectory(
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
        trajectory = payload["trajectory"]
        trajectories[role].append(trajectory)
        records.append(
            {
                "role": role,
                "split": split,
                "sample_id": payload["binding"]["sample_id"],
                "dataset_relpath": payload["binding"]["dataset_relpath"],
                "layer_selector": args.layer_selector,
                "layer_id": selector["layer_id"],
                "trajectory_shape": list(trajectory.shape),
                "trajectory_mean": float(trajectory.mean().item()),
                "trajectory_std": float(trajectory.std(unbiased=False).item()),
            }
        )

    trajectory_tensors = {
        role: torch.stack(role_trajectories, dim=0)
        for role, role_trajectories in trajectories.items()
    }
    feature_matrices: dict[str, dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]] = {}
    for feature_name in args.trajectory_features:
        member_matrix = _build_trajectory_feature(trajectory_tensors["member"], feature_name)
        nonmember_matrix = _build_trajectory_feature(trajectory_tensors["nonmember"], feature_name)
        feature_matrices[feature_name] = {
            "member": _split_matrix(
                member_matrix,
                selector_count=args.selector_count,
                validation_count=args.validation_count,
            ),
            "nonmember": _split_matrix(
                nonmember_matrix,
                selector_count=args.selector_count,
                validation_count=args.validation_count,
            ),
        }

    selected_payload = _select_trajectory_feature(
        feature_matrices=feature_matrices,
        feature_names=args.trajectory_features,
        top_k=args.top_k,
        candidate_multiplier=args.candidate_multiplier,
    )
    selected = selected_payload["selected"]

    mean_baseline = selected
    if "mean_profile" in feature_matrices:
        mean_baseline = _select_trajectory_feature(
            feature_matrices=feature_matrices,
            feature_names=["mean_profile"],
            top_k=args.top_k,
            candidate_multiplier=args.candidate_multiplier,
        )["selected"]

    profile_artifact = args.workspace / "per-timestep-activation-trajectories.pt"
    torch.save(
        {
            "trajectory_tensors": trajectory_tensors,
            "feature_matrices": feature_matrices,
            "selected_feature": selected["feature"],
            "selected_top_indices": selected["selection"]["top_indices"],
            "selected_direction": selected["selection"]["direction"],
            "mean_baseline_top_indices": mean_baseline["selection"]["top_indices"],
            "mean_baseline_direction": mean_baseline["selection"]["direction"],
        },
        profile_artifact,
    )
    records_path = args.workspace / "records.jsonl"
    records_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in records) + "\n",
        encoding="utf-8",
    )

    candidate_summaries = []
    for candidate in selected_payload["candidates"]:
        candidate_summaries.append(
            {
                "feature": candidate["feature"],
                "selection": _json_selection(candidate["selection"]),
                "metrics": candidate["metrics"],
                "validation_rank_key": list(_rank_feature_candidate(candidate)),
            }
        )

    selected_holdout = selected["metrics"]["holdout"]
    mean_holdout = mean_baseline["metrics"]["holdout"]
    passes_fire_gate = (
        selected["feature"] != "mean_profile"
        and float(selected_holdout["auc"]) > float(mean_holdout["auc"])
        and float(selected_holdout["tpr_at_1pct_fpr"]) > 0.0
    )

    summary = {
        "schema": "diffaudit.x154_per_timestep_activation_trajectory_gpu_scout.v1",
        "status": "ready",
        "track": "white-box",
        "method": "per-timestep-activation-trajectory-scout",
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
            "trajectory_features": args.trajectory_features,
            "noise_seed": args.noise_seed,
            "top_k": int(args.top_k),
            "candidate_multiplier": int(args.candidate_multiplier),
            "member_count": len(args.member_ids),
            "nonmember_count": len(args.nonmember_ids),
            "selector_count": int(args.selector_count),
            "validation_count": int(args.validation_count),
            "holdout_count": int(feature_matrices[selected["feature"]]["member"][2].shape[0]),
            "selection_policy": (
                "feature family and channels selected using selector plus validation splits only; "
                "holdout is verdict-only"
            ),
        },
        "metrics": {
            "selected_feature": selected["feature"],
            "selected_selector": selected["metrics"]["selector"],
            "selected_validation": selected["metrics"]["validation"],
            "selected_holdout_verdict": selected_holdout,
            "mean_profile_baseline_holdout": mean_holdout,
            "candidate_holdout_diagnostics": {
                candidate["feature"]: candidate["metrics"]["holdout"]
                for candidate in selected_payload["candidates"]
            },
        },
        "selection": {
            "selected": {
                "feature": selected["feature"],
                "selection": _json_selection(selected["selection"]),
                "validation_rank_key": list(_rank_feature_candidate(selected)),
            },
            "mean_profile_baseline": {
                "feature": mean_baseline["feature"],
                "selection": _json_selection(mean_baseline["selection"]),
                "validation_rank_key": list(_rank_feature_candidate(mean_baseline)),
            },
            "all_candidates": candidate_summaries,
            "feature_failures": selected_payload["failures"],
        },
        "fire_gate": {
            "passes": bool(passes_fire_gate),
            "requires_non_mean_profile": True,
            "requires_holdout_auc_gt_mean_profile": True,
            "requires_selected_tpr_at_1pct_fpr_gt_0": True,
        },
        "artifact_paths": {
            "summary": "summary.json",
            "records": "records.jsonl",
            "trajectories": profile_artifact.name,
        },
        "notes": [
            "X-154 keeps the timestep axis until feature construction; it is not another averaged mean-profile selector.",
            "Feature family and channel selection use selector and validation splits only.",
            "Holdout metrics are the only verdict surface.",
            (
                "Low-FPR fields are reported but are coarse at "
                f"{int(feature_matrices[selected['feature']]['member'][2].shape[0])}/"
                f"{int(feature_matrices[selected['feature']]['nonmember'][2].shape[0])} holdout scale; "
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
