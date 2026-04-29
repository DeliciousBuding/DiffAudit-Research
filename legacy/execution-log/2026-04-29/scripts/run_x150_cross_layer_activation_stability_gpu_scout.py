from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from diffaudit.attacks.gsa_observability import (
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


def _score_from_layer_average(
    member_matrices: list[torch.Tensor],
    nonmember_matrices: list[torch.Tensor],
    *,
    top_indices: torch.Tensor,
    direction: torch.Tensor,
) -> dict[str, Any]:
    member_scores_tensor = torch.stack(
        [(matrix[:, top_indices] * direction).mean(dim=1) for matrix in member_matrices],
        dim=0,
    ).mean(dim=0)
    nonmember_scores_tensor = torch.stack(
        [(matrix[:, top_indices] * direction).mean(dim=1) for matrix in nonmember_matrices],
        dim=0,
    ).mean(dim=0)
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


def _support_labels_for_candidate(
    candidate_position: int,
    *,
    comparator_names: list[str],
    comparator_supported: dict[str, torch.Tensor],
) -> list[str]:
    labels: list[str] = []
    for name in comparator_names:
        if bool(comparator_supported[name][candidate_position].item()):
            labels.append(name)
    return labels


def _select_primary_validation_stable_subspace(
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
    primary_validation_stable = (selector_sign != 0) & (selector_sign == validation_sign)
    stable_indices = candidate_indices[primary_validation_stable]
    if int(stable_indices.numel()) == 0:
        raise RuntimeError("No primary validation-stable channels survived sign filtering.")
    stable_selector_abs_delta = selector_delta[stable_indices].abs()
    stable_validation_abs_delta = validation_delta[stable_indices].abs()
    stable_score = torch.minimum(stable_selector_abs_delta, stable_validation_abs_delta)
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
        "sign_consistent_count": int(primary_validation_stable.sum().item()),
        "candidate_indices": candidate_indices,
        "candidate_abs_delta": candidate_values,
    }


def _select_cross_layer_stable_subspace(
    *,
    primary_selector_member_matrix: torch.Tensor,
    primary_selector_nonmember_matrix: torch.Tensor,
    primary_validation_member_matrix: torch.Tensor,
    primary_validation_nonmember_matrix: torch.Tensor,
    comparator_validation_matrices: dict[str, tuple[torch.Tensor, torch.Tensor]],
    top_k: int,
    candidate_multiplier: int,
    min_comparator_abs_delta: float = 0.0,
    required_comparator_support: int = 1,
) -> dict[str, Any]:
    primary_selector_delta = _mean_delta(primary_selector_member_matrix, primary_selector_nonmember_matrix)
    primary_validation_delta = _mean_delta(primary_validation_member_matrix, primary_validation_nonmember_matrix)
    top_k = min(int(top_k), int(primary_selector_delta.numel()))
    candidate_count = min(max(top_k * int(candidate_multiplier), top_k), int(primary_selector_delta.numel()))
    candidate_values, candidate_indices = torch.topk(primary_selector_delta.abs(), k=candidate_count)

    primary_selector_sign = _nonzero_sign(primary_selector_delta[candidate_indices])
    primary_validation_sign = _nonzero_sign(primary_validation_delta[candidate_indices])
    primary_validation_stable = (primary_selector_sign != 0) & (primary_selector_sign == primary_validation_sign)

    comparator_names = sorted(comparator_validation_matrices.keys())
    if not comparator_names:
        raise ValueError("At least one comparator validation matrix is required.")

    comparator_supported: dict[str, torch.Tensor] = {}
    comparator_abs_by_name: dict[str, torch.Tensor] = {}
    for name in comparator_names:
        member_matrix, nonmember_matrix = comparator_validation_matrices[name]
        comparator_delta = _mean_delta(member_matrix, nonmember_matrix)
        if int(comparator_delta.numel()) != int(primary_selector_delta.numel()):
            raise ValueError(
                f"Comparator channel count mismatch for {name}: "
                f"{int(comparator_delta.numel())} != {int(primary_selector_delta.numel())}"
            )
        comparator_sign = _nonzero_sign(comparator_delta[candidate_indices])
        comparator_abs = comparator_delta[candidate_indices].abs()
        comparator_abs_by_name[name] = comparator_abs
        comparator_supported[name] = (
            (comparator_sign != 0)
            & (comparator_sign == primary_selector_sign)
            & (comparator_abs >= float(min_comparator_abs_delta))
        )

    support_count = torch.zeros(candidate_count, dtype=torch.long)
    comparator_abs_stack = []
    for name in comparator_names:
        support_count = support_count + comparator_supported[name].to(torch.long)
        comparator_abs_stack.append(
            torch.where(
                comparator_supported[name],
                comparator_abs_by_name[name],
                torch.zeros_like(comparator_abs_by_name[name]),
            )
        )
    strongest_comparator_abs = torch.stack(comparator_abs_stack, dim=0).max(dim=0).values
    cross_layer_stable = primary_validation_stable & (support_count >= int(required_comparator_support))
    stable_candidate_positions = torch.nonzero(cross_layer_stable, as_tuple=False).reshape(-1)
    if int(stable_candidate_positions.numel()) == 0:
        raise RuntimeError("No cross-layer-stable activation channels survived validation and comparator support gates.")

    stable_indices = candidate_indices[stable_candidate_positions]
    stable_score = torch.minimum(
        primary_selector_delta[stable_indices].abs(),
        torch.minimum(
            primary_validation_delta[stable_indices].abs(),
            strongest_comparator_abs[stable_candidate_positions],
        ),
    )
    selected_count = min(top_k, int(stable_indices.numel()))
    selected_scores, selected_order = torch.topk(stable_score, k=selected_count)
    selected_candidate_positions = stable_candidate_positions[selected_order]
    selected_indices = candidate_indices[selected_candidate_positions]
    direction = torch.sign(primary_selector_delta[selected_indices])
    direction[direction == 0] = 1

    return {
        "top_indices": selected_indices,
        "direction": direction,
        "stable_score": selected_scores,
        "candidate_count": int(candidate_count),
        "primary_validation_stable_count": int(primary_validation_stable.sum().item()),
        "cross_layer_stable_count": int(cross_layer_stable.sum().item()),
        "candidate_indices": candidate_indices,
        "candidate_abs_delta": candidate_values,
        "support_count": [int(value) for value in support_count[selected_candidate_positions].tolist()],
        "support_labels": [
            _support_labels_for_candidate(
                int(position),
                comparator_names=comparator_names,
                comparator_supported=comparator_supported,
            )
            for position in selected_candidate_positions.tolist()
        ],
        "primary_selector_abs_delta": primary_selector_delta[selected_indices].abs(),
        "primary_validation_abs_delta": primary_validation_delta[selected_indices].abs(),
        "strongest_comparator_abs_delta": strongest_comparator_abs[selected_candidate_positions],
    }


def _capture_layer_profiles(
    *,
    model: torch.nn.Module,
    assets_root: Path,
    split: str,
    sample_id: str,
    layer_ids: dict[str, str],
    timesteps: list[int],
    noise_seed: int,
    prediction_type: str,
    ddpm_num_steps: int,
    resolution: int,
    device: str,
) -> dict[str, Any]:
    binding = resolve_gsa_sample_binding(assets_root, split=split, sample_id=sample_id)
    sample_tensor = _load_image_tensor(binding["absolute_path"], resolution=resolution).to(device)
    modules = dict(model.named_modules())
    layer_profiles: dict[str, list[torch.Tensor]] = {name: [] for name in layer_ids}

    for timestep in timesteps:
        noisy_sample = _prepare_noisy_sample(
            sample_tensor=sample_tensor,
            timestep=int(timestep),
            noise_seed=int(noise_seed),
            prediction_type=prediction_type,
            ddpm_num_steps=int(ddpm_num_steps),
        )
        captured: dict[str, torch.Tensor] = {}
        handles = []

        def _make_hook(name: str):
            def _hook(_: torch.nn.Module, __: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
                tensor = output[0] if isinstance(output, tuple) else output
                captured[name] = tensor.detach().cpu()

            return _hook

        for name, layer_id in layer_ids.items():
            if layer_id not in modules:
                raise KeyError(f"Layer id not found in model: {layer_id}")
            handles.append(modules[layer_id].register_forward_hook(_make_hook(name)))
        try:
            with torch.no_grad():
                model(noisy_sample, timestep=torch.tensor([int(timestep)], device=noisy_sample.device))
        finally:
            for handle in handles:
                handle.remove()

        missing = [name for name in layer_ids if name not in captured]
        if missing:
            raise RuntimeError(f"Activation hook did not capture outputs for layers: {missing}")
        for name, activation in captured.items():
            layer_profiles[name].append(_channelwise_profile(activation).to(torch.float32))

    profiles = {
        name: torch.stack(timestep_profiles, dim=0).mean(dim=0)
        for name, timestep_profiles in layer_profiles.items()
    }
    return {
        "binding": binding,
        "profiles": profiles,
        "timesteps": timesteps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run X-150 cross-layer activation-stability scout on admitted GSA/CIFAR10 assets. "
            "This is a bounded GPU preflight after X-148, not a headline result."
        )
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("workspaces/white-box/runs/x150-cross-layer-activation-stability-scout-20260429-r1"),
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
    parser.add_argument("--primary-layer", default="mid_block.attentions.0.to_v")
    parser.add_argument(
        "--comparator-layers",
        nargs="+",
        default=["mid_block.attentions.0.to_q", "mid_block.attentions.0.to_k"],
    )
    parser.add_argument("--timesteps", nargs="+", type=int, default=[250, 500, 750, 999])
    parser.add_argument("--noise-seed", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--candidate-multiplier", type=int, default=4)
    parser.add_argument("--selector-count", type=int, default=8)
    parser.add_argument("--validation-count", type=int, default=4)
    parser.add_argument("--min-comparator-abs-delta", type=float, default=0.0)
    parser.add_argument("--required-comparator-support", type=int, default=1)
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
        raise ValueError("X-150 is a bounded GPU scout; pass a cuda device.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available for X-150 activation-stability scout.")
    if len(args.member_ids) != len(args.nonmember_ids):
        raise ValueError("X-150 requires paired member/nonmember counts.")
    if args.workspace.exists() and any(args.workspace.iterdir()) and not args.overwrite:
        raise FileExistsError(f"Workspace exists and is not empty: {args.workspace}. Pass --overwrite to replace.")

    args.workspace.mkdir(parents=True, exist_ok=True)
    validate_gsa_workspace(args.repo_root)
    primary_selector = resolve_gsa_layer_selector(args.primary_layer, resolution=args.resolution)
    comparator_selectors = {
        layer: resolve_gsa_layer_selector(layer, resolution=args.resolution)
        for layer in args.comparator_layers
    }
    layer_ids = {
        args.primary_layer: primary_selector["layer_id"],
        **{layer: selector["layer_id"] for layer, selector in comparator_selectors.items()},
    }
    model, resolved_checkpoint_dir = _load_gsa_unet_checkpoint(
        checkpoint_root=args.checkpoint_root,
        checkpoint_dir=args.checkpoint_dir,
        resolution=args.resolution,
        device=args.device,
    )

    records: list[dict[str, Any]] = []
    profiles: dict[str, dict[str, list[torch.Tensor]]] = {
        layer: {"member": [], "nonmember": []}
        for layer in layer_ids
    }
    sample_specs = [
        ("member", "target-member", sample_id) for sample_id in args.member_ids
    ] + [
        ("nonmember", "target-nonmember", sample_id) for sample_id in args.nonmember_ids
    ]
    for role, split, sample_id in sample_specs:
        payload = _capture_layer_profiles(
            model=model,
            assets_root=args.assets_root,
            split=split,
            sample_id=sample_id,
            layer_ids=layer_ids,
            timesteps=args.timesteps,
            noise_seed=args.noise_seed,
            prediction_type=args.prediction_type,
            ddpm_num_steps=args.ddpm_num_steps,
            resolution=args.resolution,
            device=args.device,
        )
        for layer, profile in payload["profiles"].items():
            profiles[layer][role].append(profile)
            records.append(
                {
                    "role": role,
                    "split": split,
                    "sample_id": payload["binding"]["sample_id"],
                    "dataset_relpath": payload["binding"]["dataset_relpath"],
                    "layer_selector": layer,
                    "layer_id": layer_ids[layer],
                    "profile_shape": list(profile.shape),
                    "profile_mean": float(profile.mean().item()),
                    "profile_std": float(profile.std(unbiased=False).item()),
                }
            )

    matrices = {
        layer: {
            "member": torch.stack(by_role["member"], dim=0),
            "nonmember": torch.stack(by_role["nonmember"], dim=0),
        }
        for layer, by_role in profiles.items()
    }
    primary_channel_count = int(matrices[args.primary_layer]["member"].shape[1])
    for layer, by_role in matrices.items():
        for role, matrix in by_role.items():
            if int(matrix.shape[1]) != primary_channel_count:
                raise ValueError(
                    f"Channel count mismatch for {layer}/{role}: "
                    f"{int(matrix.shape[1])} != {primary_channel_count}"
                )

    split_matrices: dict[str, dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]] = {}
    for layer, by_role in matrices.items():
        split_matrices[layer] = {
            "member": _split_matrix(
                by_role["member"],
                selector_count=args.selector_count,
                validation_count=args.validation_count,
            ),
            "nonmember": _split_matrix(
                by_role["nonmember"],
                selector_count=args.selector_count,
                validation_count=args.validation_count,
            ),
        }

    primary_member_selector, primary_member_validation, primary_member_holdout = split_matrices[args.primary_layer]["member"]
    primary_nonmember_selector, primary_nonmember_validation, primary_nonmember_holdout = split_matrices[args.primary_layer]["nonmember"]
    comparator_validation_matrices = {
        layer: (
            split_matrices[layer]["member"][1],
            split_matrices[layer]["nonmember"][1],
        )
        for layer in args.comparator_layers
    }

    selected = _select_cross_layer_stable_subspace(
        primary_selector_member_matrix=primary_member_selector,
        primary_selector_nonmember_matrix=primary_nonmember_selector,
        primary_validation_member_matrix=primary_member_validation,
        primary_validation_nonmember_matrix=primary_nonmember_validation,
        comparator_validation_matrices=comparator_validation_matrices,
        top_k=args.top_k,
        candidate_multiplier=args.candidate_multiplier,
        min_comparator_abs_delta=args.min_comparator_abs_delta,
        required_comparator_support=args.required_comparator_support,
    )
    primary_validation_baseline = _select_primary_validation_stable_subspace(
        selector_member_matrix=primary_member_selector,
        selector_nonmember_matrix=primary_nonmember_selector,
        validation_member_matrix=primary_member_validation,
        validation_nonmember_matrix=primary_nonmember_validation,
        top_k=args.top_k,
        candidate_multiplier=args.candidate_multiplier,
    )

    primary_selector_metrics = _score_from_subspace(
        primary_member_selector,
        primary_nonmember_selector,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    primary_validation_metrics = _score_from_subspace(
        primary_member_validation,
        primary_nonmember_validation,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    primary_holdout_metrics = _score_from_subspace(
        primary_member_holdout,
        primary_nonmember_holdout,
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )
    primary_validation_baseline_holdout_metrics = _score_from_subspace(
        primary_member_holdout,
        primary_nonmember_holdout,
        top_indices=primary_validation_baseline["top_indices"],
        direction=primary_validation_baseline["direction"],
    )
    comparator_holdout_metrics = {
        layer: _score_from_subspace(
            split_matrices[layer]["member"][2],
            split_matrices[layer]["nonmember"][2],
            top_indices=selected["top_indices"],
            direction=selected["direction"],
        )
        for layer in args.comparator_layers
    }
    cross_projection_holdout_metrics = _score_from_layer_average(
        [primary_member_holdout] + [split_matrices[layer]["member"][2] for layer in args.comparator_layers],
        [primary_nonmember_holdout] + [split_matrices[layer]["nonmember"][2] for layer in args.comparator_layers],
        top_indices=selected["top_indices"],
        direction=selected["direction"],
    )

    profile_artifact = args.workspace / "cross-layer-activation-stability-profiles.pt"
    torch.save(
        {
            "matrices": matrices,
            "split_matrices": split_matrices,
            "selected_top_indices": selected["top_indices"],
            "selected_direction": selected["direction"],
            "selected_stable_score": selected["stable_score"],
            "primary_validation_baseline_top_indices": primary_validation_baseline["top_indices"],
        },
        profile_artifact,
    )
    records_path = args.workspace / "records.jsonl"
    records_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in records) + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema": "diffaudit.x150_cross_layer_activation_stability_gpu_scout.v1",
        "status": "ready",
        "track": "white-box",
        "method": "cross-layer-activation-stability-scout",
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
            "primary_layer": args.primary_layer,
            "primary_layer_id": primary_selector["layer_id"],
            "comparator_layers": args.comparator_layers,
            "comparator_layer_ids": {
                layer: selector["layer_id"] for layer, selector in comparator_selectors.items()
            },
            "timesteps": args.timesteps,
            "noise_seed": args.noise_seed,
            "top_k": min(int(args.top_k), int(selected["top_indices"].numel())),
            "candidate_multiplier": int(args.candidate_multiplier),
            "member_count": len(args.member_ids),
            "nonmember_count": len(args.nonmember_ids),
            "selector_count": int(args.selector_count),
            "validation_count": int(args.validation_count),
            "holdout_count": int(primary_member_holdout.shape[0]),
            "min_comparator_abs_delta": float(args.min_comparator_abs_delta),
            "required_comparator_support": int(args.required_comparator_support),
            "batching": "single-sample loop with same-forward multi-hook capture",
        },
        "metrics": {
            "primary_selector": primary_selector_metrics,
            "primary_validation": primary_validation_metrics,
            "primary_holdout_verdict": primary_holdout_metrics,
            "primary_validation_stable_baseline_holdout": primary_validation_baseline_holdout_metrics,
            "cross_projection_mean_holdout_diagnostic": cross_projection_holdout_metrics,
            "comparator_holdout_by_layer": comparator_holdout_metrics,
        },
        "selection": {
            "candidate_count": selected["candidate_count"],
            "primary_validation_stable_count": selected["primary_validation_stable_count"],
            "cross_layer_stable_count": selected["cross_layer_stable_count"],
            "selected_count": int(selected["top_indices"].numel()),
            "top_indices": [int(value) for value in selected["top_indices"].tolist()],
            "direction": [float(value) for value in selected["direction"].tolist()],
            "stable_score": [round(float(value), 8) for value in selected["stable_score"].tolist()],
            "primary_selector_abs_delta": [
                round(float(value), 8) for value in selected["primary_selector_abs_delta"].tolist()
            ],
            "primary_validation_abs_delta": [
                round(float(value), 8) for value in selected["primary_validation_abs_delta"].tolist()
            ],
            "strongest_comparator_abs_delta": [
                round(float(value), 8) for value in selected["strongest_comparator_abs_delta"].tolist()
            ],
            "support_count": selected["support_count"],
            "support_labels": selected["support_labels"],
            "baseline_primary_validation_stable": {
                "candidate_count": primary_validation_baseline["candidate_count"],
                "sign_consistent_count": primary_validation_baseline["sign_consistent_count"],
                "top_indices": [
                    int(value) for value in primary_validation_baseline["top_indices"].tolist()
                ],
            },
        },
        "artifact_paths": {
            "summary": "summary.json",
            "records": "records.jsonl",
            "profiles": profile_artifact.name,
        },
        "notes": [
            "X-150 freezes the first cross-layer stability contract to one attention block: to_v primary with to_q/to_k validation support.",
            "Selection uses selector and validation splits only; holdout metrics are the verdict surface.",
            "The packet remains intentionally small and does not promote a white-box second family.",
            (
                "Low-FPR fields are reported but are coarse at "
                f"{int(primary_member_holdout.shape[0])}/{int(primary_nonmember_holdout.shape[0])} holdout scale; "
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
