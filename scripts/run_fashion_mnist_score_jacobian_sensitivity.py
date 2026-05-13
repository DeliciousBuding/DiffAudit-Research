from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from diffusers import DDPMPipeline
from torchvision import datasets, transforms

from diffaudit.utils.metrics import threshold_metrics_grid


EXPERIMENT_ID = "fashion-mnist-ddpm-score-jacobian-sensitivity-20260514"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one bounded score-Jacobian sensitivity scout on Fashion-MNIST DDPM."
    )
    parser.add_argument("--model-id", default="ynwag9/fashion_mnist_ddpm_32")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("../Download/shared/datasets/fashion-mnist"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("workspaces/gray-box/artifacts") / f"{EXPERIMENT_ID}.json",
    )
    parser.add_argument("--samples-per-split", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timestep", type=int, default=100)
    parser.add_argument("--p-norm", type=float, default=2.0)
    parser.add_argument("--perturbation-scale", type=float, default=0.01)
    parser.add_argument("--noise-seed-base", type=int, default=20260514)
    parser.add_argument("--perturbation-seed-base", type=int, default=20260515)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--local-files-only", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--download-dataset", action="store_true")
    return parser.parse_args()


def _display_path(path: Path) -> str:
    try:
        rel = path.resolve().relative_to((Path.cwd().parent / "Download").resolve())
        return f"<DOWNLOAD_ROOT>/{rel.as_posix()}"
    except ValueError:
        return path.as_posix()


def _image_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((32, 32), interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ]
    )


def _score_jacobian_sensitivity_scores(
    base_prediction: torch.Tensor,
    perturbed_prediction: torch.Tensor,
    *,
    perturbation_scale: float,
    p_norm: int | float = 2,
) -> np.ndarray:
    delta = (perturbed_prediction.detach().float() - base_prediction.detach().float()) / float(
        perturbation_scale
    )
    flattened = delta.flatten(start_dim=1)
    norms = torch.linalg.vector_norm(flattened, ord=p_norm, dim=1)
    return (-norms).detach().cpu().numpy()


def _summarize_scores(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    metrics = threshold_metrics_grid(labels.astype(int), scores.astype(float))
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    return {
        "auc": float(metrics["auc"]),
        "asr": float(metrics["asr"]),
        "tpr_at_1pct_fpr": float(metrics["tpr_at_1pct_fpr"]),
        "tpr_at_0_1pct_fpr": float(metrics["tpr_at_0_1pct_fpr"]),
        "threshold": float(metrics["threshold"]),
        "best_tpr": float(metrics["best_tpr"]),
        "best_fpr": float(metrics["best_fpr"]),
        "member_score_mean": float(member_scores.mean()),
        "nonmember_score_mean": float(nonmember_scores.mean()),
        "member_directional_derivative_norm_mean": float((-member_scores).mean()),
        "nonmember_directional_derivative_norm_mean": float((-nonmember_scores).mean()),
        "member_count": int((labels == 1).sum()),
        "nonmember_count": int((labels == 0).sum()),
    }


def _verdict_from_metrics(metrics: dict[str, float]) -> str:
    if float(metrics["auc"]) >= 0.60 and float(metrics["tpr_at_1pct_fpr"]) > 0.0:
        return "candidate signal; requires stronger provenance before promotion"
    return "weak; close Fashion-MNIST score-Jacobian sensitivity scout"


def _load_split(
    *,
    dataset_root: Path,
    train: bool,
    samples_per_split: int,
    download: bool,
) -> list[dict[str, Any]]:
    dataset = datasets.FashionMNIST(
        root=dataset_root,
        train=train,
        transform=_image_transform(),
        download=download,
    )
    if len(dataset) < samples_per_split:
        split_name = "train" if train else "test"
        raise ValueError(f"Fashion-MNIST {split_name} split has {len(dataset)} rows, need {samples_per_split}")
    split = "member" if train else "nonmember"
    label = 1 if train else 0
    rows: list[dict[str, Any]] = []
    for dataset_index in range(samples_per_split):
        image, class_label = dataset[dataset_index]
        rows.append(
            {
                "id": f"{split}_{dataset_index:03d}",
                "split": split,
                "label": label,
                "dataset_index": int(dataset_index),
                "class_label": int(class_label),
                "image": image,
            }
        )
    return rows


def _load_pipeline(model_id: str, *, device: torch.device, local_files_only: bool) -> DDPMPipeline:
    pipe = DDPMPipeline.from_pretrained(model_id, local_files_only=local_files_only)
    pipe.set_progress_bar_config(disable=True)
    pipe.unet.to(device)
    pipe.unet.eval().requires_grad_(False)
    if hasattr(pipe.scheduler, "alphas_cumprod"):
        pipe.scheduler.alphas_cumprod = pipe.scheduler.alphas_cumprod.to(device)
    return pipe


def _randn_like(shape: torch.Size, *, seed: int, device: torch.device) -> torch.Tensor:
    generator = torch.Generator(device=device.type).manual_seed(int(seed))
    return torch.randn(shape, generator=generator, device=device)


def _score_rows(
    *,
    pipe: DDPMPipeline,
    rows: list[dict[str, Any]],
    batch_size: int,
    timestep: int,
    p_norm: int | float,
    perturbation_scale: float,
    noise_seed_base: int,
    perturbation_seed_base: int,
    device: torch.device,
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        images = torch.stack([row["image"] for row in batch_rows], dim=0).to(device=device, dtype=torch.float32)
        noises: list[torch.Tensor] = []
        perturbations: list[torch.Tensor] = []
        for offset, row in enumerate(batch_rows):
            noise_seed = int(noise_seed_base) + int(timestep) * 100_000 + int(row["dataset_index"])
            perturbation_seed = int(perturbation_seed_base) + int(timestep) * 100_000 + int(row["dataset_index"])
            noises.append(_randn_like(images[offset : offset + 1].shape, seed=noise_seed, device=device))
            direction = _randn_like(images[offset : offset + 1].shape, seed=perturbation_seed, device=device)
            direction = direction / torch.clamp(
                torch.linalg.vector_norm(direction.flatten(start_dim=1), ord=2, dim=1).view(-1, 1, 1, 1),
                min=1.0e-12,
            )
            perturbations.append(direction)
        noise = torch.cat(noises, dim=0)
        perturbation = torch.cat(perturbations, dim=0)
        timestep_tensor = torch.full((len(batch_rows),), int(timestep), device=device, dtype=torch.long)
        noisy = pipe.scheduler.add_noise(images, noise, timestep_tensor)
        perturbed_noisy = noisy + float(perturbation_scale) * perturbation
        with torch.inference_mode():
            base_prediction = pipe.unet(noisy, timestep_tensor).sample
            perturbed_prediction = pipe.unet(perturbed_noisy, timestep_tensor).sample
        scores = _score_jacobian_sensitivity_scores(
            base_prediction,
            perturbed_prediction,
            perturbation_scale=float(perturbation_scale),
            p_norm=p_norm,
        )
        norms = -scores
        for offset, row in enumerate(batch_rows):
            noise_seed = int(noise_seed_base) + int(timestep) * 100_000 + int(row["dataset_index"])
            perturbation_seed = int(perturbation_seed_base) + int(timestep) * 100_000 + int(row["dataset_index"])
            scored.append(
                {
                    "id": row["id"],
                    "split": row["split"],
                    "label": int(row["label"]),
                    "dataset_index": int(row["dataset_index"]),
                    "class_label": int(row["class_label"]),
                    "timestep": int(timestep),
                    "p_norm": float(p_norm),
                    "perturbation_scale": float(perturbation_scale),
                    "noise_seed": int(noise_seed),
                    "perturbation_seed": int(perturbation_seed),
                    "score": float(scores[offset]),
                    "directional_derivative_norm": float(norms[offset]),
                }
            )
    return scored


def main() -> None:
    started_at = time.perf_counter()
    args = parse_args()
    if args.samples_per_split <= 0:
        raise ValueError("--samples-per-split must be positive")
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    if not 0 <= int(args.timestep) < 1000:
        raise ValueError("--timestep must be in [0, 999]")
    if float(args.p_norm) <= 0.0:
        raise ValueError("--p-norm must be positive")
    if float(args.perturbation_scale) <= 0.0:
        raise ValueError("--perturbation-scale must be positive")

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")
    if str(args.device).startswith("cuda") and device.type != "cuda":
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false")

    member_rows = _load_split(
        dataset_root=args.dataset_root,
        train=True,
        samples_per_split=int(args.samples_per_split),
        download=bool(args.download_dataset),
    )
    nonmember_rows = _load_split(
        dataset_root=args.dataset_root,
        train=False,
        samples_per_split=int(args.samples_per_split),
        download=bool(args.download_dataset),
    )
    rows = member_rows + nonmember_rows
    pipe = _load_pipeline(str(args.model_id), device=device, local_files_only=bool(args.local_files_only))
    records = _score_rows(
        pipe=pipe,
        rows=rows,
        batch_size=int(args.batch_size),
        timestep=int(args.timestep),
        p_norm=float(args.p_norm),
        perturbation_scale=float(args.perturbation_scale),
        noise_seed_base=int(args.noise_seed_base),
        perturbation_seed_base=int(args.perturbation_seed_base),
        device=device,
    )

    labels = np.asarray([record["label"] for record in records], dtype=int)
    scores = np.asarray([record["score"] for record in records], dtype=float)
    metrics = _summarize_scores(labels, scores)
    verdict = _verdict_from_metrics(metrics)
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "date": "2026-05-14",
        "status": "bounded_scout",
        "track": "gray-box",
        "method": "score_jacobian_sensitivity",
        "question": (
            "On the same clean Fashion-MNIST train/test split used by the weak PIA-loss "
            "and SimA score-norm scouts, does local UNet score-field sensitivity under a "
            "fixed input perturbation direction separate members from nonmembers?"
        ),
        "contract": {
            "target_model": str(args.model_id),
            "target_type": "diffusers DDPMPipeline / UNet denoiser local input sensitivity",
            "member_split": f"torchvision FashionMNIST train first {int(args.samples_per_split)}",
            "nonmember_split": f"torchvision FashionMNIST test first {int(args.samples_per_split)}",
            "score_name": (
                f"negative_l{float(args.p_norm):g}_unet_epsilon_directional_derivative_norm_"
                f"t{int(args.timestep)}_delta{float(args.perturbation_scale):g}"
            ),
            "score_direction": "higher_is_more_member",
            "timestep": int(args.timestep),
            "p_norm": float(args.p_norm),
            "perturbation_scale": float(args.perturbation_scale),
            "noise_seed_base": int(args.noise_seed_base),
            "perturbation_seed_base": int(args.perturbation_seed_base),
        },
        "boundary": (
            "Single bounded score-Jacobian sensitivity check. This is not denoising MSE, "
            "not x0 residual, not score norm, not final-layer gradient, and not a "
            "timestep/seed/perturbation matrix."
        ),
        "provenance_warning": (
            "The Hugging Face repo has no README/model card; this assumes the standard "
            "Fashion-MNIST train split as members from repository identity. Scout only, "
            "not admitted evidence."
        ),
        "runtime": {
            "dataset_root": _display_path(args.dataset_root),
            "samples_per_split": int(args.samples_per_split),
            "batch_size": int(args.batch_size),
            "device": str(device),
            "torch_version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "local_files_only": bool(args.local_files_only),
            "duration_seconds": round(float(time.perf_counter() - started_at), 3),
        },
        "metrics": metrics,
        "verdict": verdict,
        "stop_condition": (
            "If AUC < 0.60 or TPR@1%FPR remains zero/near-zero, close this observable and "
            "do not expand timestep, perturbation-scale, seed, scheduler, or packet-size matrices."
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("experiment_id", "metrics", "verdict")}, indent=2))


if __name__ == "__main__":
    main()
