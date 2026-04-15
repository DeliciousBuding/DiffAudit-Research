"""Bounded SimA runtime feasibility on the current DDPM/CIFAR-10 asset line."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from diffaudit.attacks.pia_adapter import (
    PiaDefaults,
    _build_pia_subset_loader,
    _compute_auc,
    _compute_threshold_metrics,
    load_pia_model,
    prepare_pia_runtime,
    probe_pia_assets,
)
from diffaudit.config import AuditConfig


def _compute_sima_scores_from_eps(
    eps_prediction: torch.Tensor,
    p_norm: int | float = 4,
) -> torch.Tensor:
    flattened = eps_prediction.flatten(start_dim=1)
    norms = torch.linalg.vector_norm(flattened, ord=p_norm, dim=1)
    return (-norms).detach().cpu()


def _alpha_bar_schedule(
    defaults: PiaDefaults | None = None,
) -> torch.Tensor:
    config = defaults or PiaDefaults()
    betas = torch.linspace(config.beta_1, config.beta_T, config.T, dtype=torch.float32)
    alphas = 1.0 - betas
    return torch.cumprod(alphas, dim=0)


def _score_loader_for_timestep(
    model: torch.nn.Module,
    loader,
    timestep: int,
    alpha_bars: torch.Tensor,
    device: str,
    p_norm: int | float,
    noise_seed: int,
) -> torch.Tensor:
    scores: list[torch.Tensor] = []
    alpha_bar_t = alpha_bars[int(timestep)].to(device=device)
    sqrt_alpha = torch.sqrt(alpha_bar_t)
    sqrt_one_minus_alpha = torch.sqrt(1.0 - alpha_bar_t)
    generator = torch.Generator(device=device if device.startswith("cuda") else "cpu")
    generator.manual_seed(int(noise_seed) + int(timestep))
    model.eval()
    with torch.no_grad():
        for batch, _ in loader:
            normalized = batch.to(device) * 2 - 1
            noise = torch.randn(
                normalized.shape,
                generator=generator,
                device=device,
                dtype=normalized.dtype,
            )
            noisy = sqrt_alpha * normalized + sqrt_one_minus_alpha * noise
            timestep_tensor = torch.full(
                (normalized.shape[0],),
                fill_value=int(timestep),
                device=device,
                dtype=torch.long,
            )
            eps_prediction = model(noisy, t=timestep_tensor)
            scores.append(_compute_sima_scores_from_eps(eps_prediction, p_norm=p_norm))
    return torch.cat(scores, dim=0)


def run_sima_runtime_feasibility(
    config: AuditConfig,
    workspace: str | Path,
    repo_root: str | Path = "external/PIA",
    member_split_root: str | Path | None = None,
    device: str = "cpu",
    max_samples: int | None = None,
    batch_size: int = 8,
    scan_timesteps: list[int] | tuple[int, ...] | None = None,
    p_norm: int | float = 4,
    noise_seed: int = 0,
    provenance_status: str = "workspace-verified",
) -> dict[str, Any]:
    started_at = time.perf_counter()
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    runtime_context = prepare_pia_runtime(
        config,
        repo_root=repo_root,
        member_split_root=member_split_root,
        device=device,
    )
    model, weights_key = load_pia_model(
        runtime_context.checkpoint_path,
        runtime_context.model_module,
        device=device,
    )
    split_root = Path(member_split_root) if member_split_root else Path(repo_root) / "DDPM"
    asset_summary = probe_pia_assets(
        dataset=runtime_context.plan.dataset,
        dataset_root=runtime_context.plan.data_root,
        model_dir=runtime_context.plan.model_dir,
        member_split_root=split_root,
    )
    selected_max_samples = max_samples or runtime_context.plan.num_samples
    member_loader, member_indices = _build_pia_subset_loader(
        dataset=runtime_context.plan.dataset,
        dataset_dir=asset_summary["paths"]["dataset_dir"],
        member_split_path=asset_summary["paths"]["member_split"],
        batch_size=batch_size,
        max_samples=selected_max_samples,
        membership="member",
    )
    nonmember_loader, nonmember_indices = _build_pia_subset_loader(
        dataset=runtime_context.plan.dataset,
        dataset_dir=asset_summary["paths"]["dataset_dir"],
        member_split_path=asset_summary["paths"]["member_split"],
        batch_size=batch_size,
        max_samples=selected_max_samples,
        membership="nonmember",
    )

    scan_points = [int(t) for t in (scan_timesteps or [20, 40, 60, 80, 100, 120])]
    alpha_bars = _alpha_bar_schedule()
    scan_results: list[dict[str, Any]] = []
    best_entry: dict[str, Any] | None = None
    for timestep in scan_points:
        member_scores = _score_loader_for_timestep(
            model,
            member_loader,
            timestep=timestep,
            alpha_bars=alpha_bars,
            device=device,
            p_norm=p_norm,
            noise_seed=noise_seed,
        )
        nonmember_scores = _score_loader_for_timestep(
            model,
            nonmember_loader,
            timestep=timestep,
            alpha_bars=alpha_bars,
            device=device,
            p_norm=p_norm,
            noise_seed=noise_seed,
        )
        metrics = {
            "auc": round(_compute_auc(member_scores, nonmember_scores), 6),
            **_compute_threshold_metrics(
                member_scores.numpy(),
                nonmember_scores.numpy(),
            ),
            "member_score_mean": round(float(member_scores.mean().item()), 6),
            "nonmember_score_mean": round(float(nonmember_scores.mean().item()), 6),
        }
        entry = {
            "timestep": int(timestep),
            "metrics": metrics,
        }
        scan_results.append(entry)
        if best_entry is None:
            best_entry = entry
        else:
            if (
                entry["metrics"]["auc"] > best_entry["metrics"]["auc"]
                or (
                    entry["metrics"]["auc"] == best_entry["metrics"]["auc"]
                    and entry["timestep"] < best_entry["timestep"]
                )
            ):
                best_entry = entry

    if best_entry is None:
        raise RuntimeError("SimA feasibility scan produced no results")

    scores_path = workspace_path / "scan-results.json"
    scores_path.write_text(json.dumps(scan_results, indent=2, ensure_ascii=True), encoding="utf-8")

    result = {
        "status": "ready",
        "track": "gray-box",
        "method": "sima",
        "paper": "SimA_arXiv2025",
        "mode": "runtime-feasibility",
        "device": device,
        "workspace": str(workspace_path),
        "workspace_name": workspace_path.name,
        "contract_stage": "target",
        "asset_grade": "single-machine-real-asset",
        "provenance_status": provenance_status,
        "evidence_level": "feasibility",
        "artifact_paths": {
            "summary": str(workspace_path / "summary.json"),
            "scan_results": str(scores_path),
        },
        "checks": {
            **asset_summary["checks"],
            "runtime_probe_ready": True,
            "scan_completed": True,
        },
        "runtime": {
            "repo_root": str(Path(repo_root)),
            "model_dir": runtime_context.plan.model_dir,
            "dataset_root": runtime_context.plan.data_root,
            "member_split_root": str(split_root),
            "batch_size": int(batch_size),
            "max_samples": int(selected_max_samples),
            "num_samples": int(len(member_indices)),
            "weights_key": weights_key,
            "scan_timesteps": scan_points,
            "p_norm": float(p_norm),
            "noise_seed": int(noise_seed),
            "elapsed_seconds": round(time.perf_counter() - started_at, 6),
        },
        "sample_count_per_split": int(len(member_indices)),
        "best_timestep": int(best_entry["timestep"]),
        "metrics": best_entry["metrics"],
        "scan_results": scan_results,
        "notes": [
            "SimA feasibility uses a single-query score-norm statistic over DDPM denoiser outputs.",
            "This is a bounded local feasibility result, not yet a promoted gray-box challenger verdict.",
        ],
    }
    (workspace_path / "summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    return result
