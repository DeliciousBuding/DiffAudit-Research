"""CPU-only diagonal-Fisher feasibility scout for GSA white-box assets."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from diffaudit.attacks.gsa import (
    _discover_shadow_specs,
    _draw_loss_score_noise,
    _extract_into_tensor,
    _filter_dataset_files_by_sample_ids,
    _iter_dataset_files,
    _load_gsa_image_tensor,
    probe_gsa_assets,
)
from diffaudit.attacks.gsa_observability import (
    _build_gsa_noise_scheduler,
    _extract_model_prediction,
    _load_gsa_unet_checkpoint,
    resolve_gsa_layer_selector,
)
from diffaudit.utils.io import write_summary_json
from diffaudit.utils.metrics import metric_bundle, round6


ModelCache = dict[
    tuple[str, str, str, int, int, str],
    tuple[torch.nn.Module, Path, dict[str, Any], list[torch.nn.Parameter], Any],
]


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def _normalize_paths(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_paths(item) for item in value]
    if isinstance(value, str):
        return value.replace("\\", "/")
    return value


def _select_layer_parameters(model: torch.nn.Module, layer_id: str) -> list[torch.nn.Parameter]:
    modules = dict(model.named_modules())
    if layer_id not in modules:
        raise KeyError(f"Layer id not found in model: {layer_id}")
    parameters = [parameter for parameter in modules[layer_id].parameters(recurse=True) if parameter.requires_grad]
    if not parameters:
        raise ValueError(f"Layer has no trainable parameters: {layer_id}")
    return parameters


def _timestep_values(ddpm_num_steps: int, sampling_frequency: int) -> list[int]:
    stride = max(1, int(ddpm_num_steps / sampling_frequency))
    return [x - 1 for x in range(stride, ddpm_num_steps + 1, stride)]


def _gradient_vector_for_sample(
    *,
    model: torch.nn.Module,
    layer_parameters: list[torch.nn.Parameter],
    scheduler: Any,
    image_path: Path,
    dataset_root: Path,
    resolution: int,
    timestep_values: list[int],
    attack_method: int,
    prediction_type: str,
    noise_seed: int | None,
    device: str,
) -> dict[str, Any]:
    clean_image = _load_gsa_image_tensor(image_path=image_path, resolution=resolution, device=device)
    clean_batch = clean_image.repeat(len(timestep_values), 1, 1, 1)
    sample_key = image_path.relative_to(dataset_root).as_posix()
    noise = _draw_loss_score_noise(
        shape=tuple(clean_batch.shape),
        device=clean_batch.device,
        dtype=clean_batch.dtype,
        noise_seed=noise_seed,
        sample_key=sample_key,
    )
    timesteps = torch.tensor(timestep_values, device=clean_batch.device).long()
    noisy_images = scheduler.add_noise(clean_batch, noise, timesteps)
    model.zero_grad(set_to_none=True)
    model_output = model(noisy_images, timesteps)
    prediction = _extract_model_prediction(model_output)

    if attack_method == 1:
        if prediction_type == "epsilon":
            loss = F.mse_loss(prediction, noise)
        elif prediction_type == "sample":
            alpha_t = _extract_into_tensor(scheduler.alphas_cumprod, timesteps, tuple(clean_batch.shape))
            loss = (alpha_t / (1 - alpha_t)) * F.mse_loss(prediction, clean_batch, reduction="none")
            loss = loss.mean()
        else:
            raise ValueError(f"Unsupported prediction type: {prediction_type}")
        loss.backward()
        scalar_loss = float(loss.detach().cpu())
    elif attack_method == 2:
        per_timestep_losses: list[torch.Tensor] = []
        for timestep_index in range(len(timesteps)):
            if prediction_type == "epsilon":
                loss = F.mse_loss(
                    prediction[timestep_index].unsqueeze(0),
                    noise[timestep_index].unsqueeze(0),
                )
            elif prediction_type == "sample":
                alpha_t = _extract_into_tensor(
                    scheduler.alphas_cumprod,
                    timesteps[timestep_index].unsqueeze(0),
                    tuple(clean_image.shape),
                )
                loss = (alpha_t / (1 - alpha_t)) * F.mse_loss(
                    prediction[timestep_index].unsqueeze(0),
                    clean_image,
                    reduction="none",
                )
                loss = loss.mean()
            else:
                raise ValueError(f"Unsupported prediction type: {prediction_type}")
            per_timestep_losses.append(loss)
        mean_loss = torch.stack(per_timestep_losses).mean()
        mean_loss.backward()
        scalar_loss = float(mean_loss.detach().cpu())
    else:
        raise ValueError(f"Unsupported GSA attack method: {attack_method}")

    gradients = [
        parameter.grad.detach().reshape(-1).cpu()
        for parameter in layer_parameters
        if parameter.grad is not None
    ]
    model.zero_grad(set_to_none=True)
    if not gradients:
        raise RuntimeError(f"No gradients captured for sample: {image_path}")
    vector = torch.cat(gradients).to(dtype=torch.float64).numpy()
    return {
        "dataset_relpath": sample_key,
        "loss_score": scalar_loss,
        "grad_vector": vector,
        "grad_numel": int(vector.shape[0]),
        "raw_grad_l2_sq": float(np.dot(vector, vector)),
    }


def _extract_split_gradient_records(
    *,
    dataset_dir: str | Path,
    checkpoint_root: str | Path,
    checkpoint_dir: str | Path | None,
    split: str,
    role: str,
    label: int,
    layer_selector: str,
    resolution: int,
    ddpm_num_steps: int,
    sampling_frequency: int,
    attack_method: int,
    prediction_type: str,
    max_samples: int,
    noise_seed: int | None,
    device: str,
    sample_id_allowlist: list[int] | None = None,
    model_cache: ModelCache | None = None,
) -> tuple[list[dict[str, Any]], Path, dict[str, Any]]:
    if device != "cpu":
        raise ValueError("GSA influence feasibility scout is CPU-only; pass device='cpu'")
    cache_key = (
        str(Path(checkpoint_root)),
        str(Path(checkpoint_dir)) if checkpoint_dir is not None else "",
        layer_selector,
        int(resolution),
        int(ddpm_num_steps),
        prediction_type,
    )
    if model_cache is not None and cache_key in model_cache:
        model, resolved_checkpoint_dir, selector, layer_parameters, scheduler = model_cache[cache_key]
    else:
        model, resolved_checkpoint_dir = _load_gsa_unet_checkpoint(
            checkpoint_root=checkpoint_root,
            checkpoint_dir=checkpoint_dir,
            resolution=resolution,
            device=device,
        )
        selector = resolve_gsa_layer_selector(layer_selector, resolution=resolution)
        layer_parameters = _select_layer_parameters(model, str(selector["layer_id"]))
        scheduler = _build_gsa_noise_scheduler(ddpm_num_steps=ddpm_num_steps, prediction_type=prediction_type)
        if model_cache is not None:
            model_cache[cache_key] = (model, resolved_checkpoint_dir, selector, layer_parameters, scheduler)
    dataset_root = Path(dataset_dir)
    dataset_files = _iter_dataset_files(dataset_root)
    dataset_files = _filter_dataset_files_by_sample_ids(dataset_files, sample_id_allowlist=sample_id_allowlist)
    dataset_files = dataset_files[: int(max_samples)]
    timestep_values = _timestep_values(ddpm_num_steps=ddpm_num_steps, sampling_frequency=sampling_frequency)

    rows: list[dict[str, Any]] = []
    for image_path in dataset_files:
        extracted = _gradient_vector_for_sample(
            model=model,
            layer_parameters=layer_parameters,
            scheduler=scheduler,
            image_path=image_path,
            dataset_root=dataset_root,
            resolution=resolution,
            timestep_values=timestep_values,
            attack_method=attack_method,
            prediction_type=prediction_type,
            noise_seed=noise_seed,
            device=device,
        )
        rows.append(
            {
                "split": split,
                "role": role,
                "label": int(label),
                "dataset_relpath": extracted["dataset_relpath"],
                "checkpoint_dir": str(resolved_checkpoint_dir),
                "layer_id": str(selector["layer_id"]),
                "timesteps": timestep_values,
                "loss_score": float(extracted["loss_score"]),
                "raw_grad_l2_sq": float(extracted["raw_grad_l2_sq"]),
                "grad_vector": extracted["grad_vector"],
                "grad_numel": int(extracted["grad_numel"]),
            }
        )
    return rows, resolved_checkpoint_dir, selector


def _fit_fisher_diag(rows: list[dict[str, Any]], damping: float) -> np.ndarray:
    if not rows:
        raise ValueError("Cannot fit Fisher diagonal without shadow rows")
    matrix = np.stack([np.asarray(row["grad_vector"], dtype=np.float64) for row in rows], axis=0)
    return np.mean(matrix * matrix, axis=0) + float(damping)


def _score_rows(rows: list[dict[str, Any]], fisher_diag: np.ndarray) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        vector = np.asarray(row["grad_vector"], dtype=np.float64)
        influence = float(np.sum((vector * vector) / fisher_diag))
        output = {key: value for key, value in row.items() if key != "grad_vector"}
        output["diag_fisher_self_influence"] = influence
        scored.append(output)
    return scored


def _metrics_for_rows(rows: list[dict[str, Any]], score_key: str, orientation: str | None = None) -> dict[str, Any]:
    if not rows:
        raise ValueError(f"Cannot compute metrics for empty rows: {score_key}")
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    if int((labels == 1).sum()) == 0 or int((labels == 0).sum()) == 0:
        raise ValueError(f"Cannot compute metrics without both classes: {score_key}")
    scores = np.asarray([float(row[score_key]) for row in rows], dtype=np.float64)
    if orientation is None:
        member_mean = float(scores[labels == 1].mean())
        nonmember_mean = float(scores[labels == 0].mean())
        orientation = "member-higher" if member_mean >= nonmember_mean else "member-lower"
    oriented = scores if orientation == "member-higher" else -scores
    metrics = metric_bundle(oriented, labels)
    metrics["score_direction"] = orientation
    metrics["member_mean"] = round6(float(scores[labels == 1].mean()))
    metrics["nonmember_mean"] = round6(float(scores[labels == 0].mean()))
    return metrics


def _board(rows: list[dict[str, Any]], orientations: dict[str, str] | None = None) -> dict[str, Any]:
    orientations = orientations or {}
    return {
        "diag_fisher_self_influence": _metrics_for_rows(
            rows,
            "diag_fisher_self_influence",
            orientation=orientations.get("diag_fisher_self_influence"),
        ),
        "scalar_loss": _metrics_for_rows(rows, "loss_score", orientation=orientations.get("scalar_loss")),
        "raw_grad_l2_sq": _metrics_for_rows(
            rows,
            "raw_grad_l2_sq",
            orientation=orientations.get("raw_grad_l2_sq"),
        ),
    }


def _strip_record_for_json(row: dict[str, Any], repo_root: Path, workspace: Path, damping: float) -> dict[str, Any]:
    checkpoint_dir = Path(str(row["checkpoint_dir"]))
    return {
        "split": row["split"],
        "role": row["role"],
        "label": row["label"],
        "dataset_relpath": row["dataset_relpath"],
        "checkpoint_dir": _relative_or_absolute(checkpoint_dir, repo_root),
        "layer_id": row["layer_id"],
        "timesteps": row["timesteps"],
        "loss_score": round6(float(row["loss_score"])),
        "raw_grad_l2_sq": round6(float(row["raw_grad_l2_sq"])),
        "diag_fisher_self_influence": round6(float(row["diag_fisher_self_influence"])),
        "grad_numel": int(row["grad_numel"]),
        "fisher_damping": float(damping),
        "score_source": "selected-layer-diagonal-fisher-self-influence",
    }


def run_gsa_diagonal_fisher_feasibility(
    *,
    workspace: str | Path,
    repo_root: str | Path,
    assets_root: str | Path,
    layer_selector: str = "mid_block.attentions.0.to_v",
    resolution: int = 32,
    ddpm_num_steps: int = 20,
    sampling_frequency: int = 2,
    attack_method: int = 1,
    prediction_type: str = "epsilon",
    max_samples_per_split: int = 1,
    fisher_damping: float = 1e-6,
    noise_seed: int | None = 0,
    device: str = "cpu",
) -> dict[str, Any]:
    if device != "cpu":
        raise ValueError("GSA diagonal-Fisher feasibility is CPU-only; GPU release is blocked")
    if max_samples_per_split <= 0 or max_samples_per_split > 8:
        raise ValueError("max_samples_per_split must be in [1, 8] for the CPU feasibility scout")

    started = time.perf_counter()
    repo_path = Path(repo_root)
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    records_path = workspace_path / "records.jsonl"
    summary_path = workspace_path / "summary.json"
    asset_probe = probe_gsa_assets(assets_root=assets_root, repo_root=repo_root)
    if asset_probe.get("status") != "ready":
        payload = {
            "schema": "diffaudit.gsa_influence.diagonal_fisher_contract.v1",
            "status": "blocked",
            "verdict": "blocked",
            "gpu_release": "none",
            "admitted_change": "none",
            "blocker": "asset probe is not ready",
            "asset_probe": asset_probe,
        "artifact_paths": {"summary": _relative_or_absolute(summary_path, Path.cwd())},
        }
        write_summary_json(summary_path, payload)
        return payload

    assets_path = Path(assets_root)
    dataset_root = assets_path / "datasets"
    checkpoint_root = assets_path / "checkpoints"
    shadow_specs = _discover_shadow_specs(dataset_root, checkpoint_root)
    shadow_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    resolved_checkpoints: dict[str, str] = {}
    selector: dict[str, Any] | None = None
    model_cache: ModelCache = {}

    for spec in shadow_specs:
        for split_suffix, label in (("member", 1), ("nonmember", 0)):
            rows, checkpoint_dir, selector = _extract_split_gradient_records(
                dataset_dir=spec[f"{split_suffix}_dataset"],
                checkpoint_root=spec["checkpoint_dir"],
                checkpoint_dir=None,
                split=f'{spec["name"]}-{split_suffix}',
                role="shadow-calibration",
                label=label,
                layer_selector=layer_selector,
                resolution=resolution,
                ddpm_num_steps=ddpm_num_steps,
                sampling_frequency=sampling_frequency,
                attack_method=attack_method,
                prediction_type=prediction_type,
                max_samples=max_samples_per_split,
                noise_seed=noise_seed,
                device=device,
                model_cache=model_cache,
            )
            shadow_rows.extend(rows)
            resolved_checkpoints[f'{spec["name"]}-{split_suffix}'] = str(checkpoint_dir)

    for split_name, label in (("target-member", 1), ("target-nonmember", 0)):
        rows, checkpoint_dir, selector = _extract_split_gradient_records(
            dataset_dir=dataset_root / split_name,
            checkpoint_root=checkpoint_root / "target",
            checkpoint_dir=None,
            split=split_name,
            role="target-transfer",
            label=label,
            layer_selector=layer_selector,
            resolution=resolution,
            ddpm_num_steps=ddpm_num_steps,
            sampling_frequency=sampling_frequency,
            attack_method=attack_method,
            prediction_type=prediction_type,
            max_samples=max_samples_per_split,
            noise_seed=noise_seed,
            device=device,
            model_cache=model_cache,
        )
        target_rows.extend(rows)
        resolved_checkpoints[split_name] = str(checkpoint_dir)

    fisher_diag = _fit_fisher_diag(shadow_rows, damping=fisher_damping)
    scored_shadow = _score_rows(shadow_rows, fisher_diag)
    scored_target = _score_rows(target_rows, fisher_diag)
    shadow_board = _board(scored_shadow)
    transferred_orientations = {
        score_name: score_board["score_direction"]
        for score_name, score_board in shadow_board.items()
    }
    target_board = _board(scored_target, orientations=transferred_orientations)
    target_self_board = _board(scored_target)
    all_records = scored_shadow + scored_target

    with records_path.open("w", encoding="utf-8") as handle:
        for row in all_records:
            handle.write(json.dumps(_strip_record_for_json(row, repo_path, workspace_path, fisher_damping), sort_keys=True))
            handle.write("\n")

    fisher_auc = target_board["diag_fisher_self_influence"]["auc"]
    baseline_auc = max(target_board["scalar_loss"]["auc"], target_board["raw_grad_l2_sq"]["auc"])
    verdict = "cpu-preflight-positive" if fisher_auc > baseline_auc else "negative-but-useful"
    payload = {
        "schema": "diffaudit.gsa_influence.diagonal_fisher_contract.v1",
        "status": "ready",
        "track": "white-box",
        "method": "gsa-diagonal-fisher-self-influence",
        "mode": "diagonal-fisher-feasibility-microboard",
        "contract_stage": "cpu-feasibility-scout",
        "gpu_release": "none",
        "admitted_change": "none",
        "verdict": verdict,
        "signal_definition": {
            "score": "sum(g_i^2 / (fisher_diag_i + damping))",
            "fisher_source": "shadow-calibration-only",
            "gradient_scope": "selected-layer-parameters-only",
            "baselines": ["scalar_loss", "raw_grad_l2_sq"],
            "raw_gradient_vectors_persisted": False,
        },
        "requested": {
            "assets_root": str(assets_root).replace("\\", "/"),
            "repo_root": str(repo_root).replace("\\", "/"),
            "layer_selector": layer_selector,
            "ddpm_num_steps": int(ddpm_num_steps),
            "sampling_frequency": int(sampling_frequency),
            "attack_method": int(attack_method),
            "prediction_type": prediction_type,
            "device": device,
            "max_samples_per_split": int(max_samples_per_split),
            "fisher_damping": float(fisher_damping),
            "noise_seed": noise_seed,
        },
        "resolved": {
            "layer_binding": selector or {},
            "shadow_specs": _normalize_paths(shadow_specs),
            "checkpoints": {
                key: _relative_or_absolute(Path(value), repo_path)
                for key, value in sorted(resolved_checkpoints.items())
            },
        },
        "checks": {
            "asset_probe_ready": True,
            "device_cpu_only": True,
            "shadow_calibration_present": bool(scored_shadow),
            "target_transfer_present": bool(scored_target),
            "raw_gradient_vectors_not_persisted_by_default": True,
            "records_written": len(all_records),
        },
        "score_boards": {
            "shadow_calibration": shadow_board,
            "target_transfer": target_board,
            "target_self_diagnostic": target_self_board,
        },
        "distinctness_checks": {
            "not_scalar_loss_only": True,
            "compared_against_raw_grad_l2": True,
            "fisher_fit_excludes_target": True,
            "uses_selected_layer_raw_gradients": True,
        },
        "runtime": {
            "elapsed_seconds": round6(time.perf_counter() - started),
            "shadow_sample_count": len(scored_shadow),
            "target_sample_count": len(scored_target),
            "grad_numel": int(scored_shadow[0]["grad_numel"]) if scored_shadow else 0,
        },
        "artifact_paths": {
            "summary": _relative_or_absolute(summary_path, Path.cwd()),
            "records": _relative_or_absolute(records_path, Path.cwd()),
        },
    }
    write_summary_json(summary_path, payload)
    return payload
