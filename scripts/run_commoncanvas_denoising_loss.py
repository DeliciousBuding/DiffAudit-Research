from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from diffusers import DDPMScheduler, StableDiffusionXLPipeline
from PIL import Image
from sklearn.metrics import roc_auc_score
from torchvision import transforms


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded CommonCanvas conditional denoising-loss membership scout."
    )
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--supplementary-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples-per-split", type=int, default=50)
    parser.add_argument("--timesteps", default="200,500,800")
    parser.add_argument("--resolution", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--noise-seed-base", type=int, default=20260513)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--checkpoint", type=Path, default=None)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_caption(row: dict[str, Any]) -> str:
    captions = row.get("source_caption", [])
    if isinstance(captions, list) and captions:
        return str(captions[0])
    if isinstance(captions, str) and captions.strip():
        return captions.strip()
    raise ValueError(f"missing source_caption for {row.get('id')}")


def _selected_rows(dataset_manifest: dict[str, Any], samples_per_split: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split, label in (("member", 1), ("nonmember", 0)):
        split_rows = dataset_manifest["queries"][split][:samples_per_split]
        if len(split_rows) != samples_per_split:
            raise ValueError(f"not enough {split} rows: {len(split_rows)} < {samples_per_split}")
        for row in split_rows:
            rows.append(
                {
                    "id": str(row["id"]),
                    "split": split,
                    "label": label,
                    "prompt": _first_caption(row),
                    "query_path": str(row["query_path"]),
                    "source_dataset_dir": row.get("source_dataset_dir"),
                    "source_image_path": row.get("source_image_path"),
                    "sha256": row.get("sha256"),
                }
            )
    return rows


def _resolve_checkpoint(args: argparse.Namespace, response_manifest: dict[str, Any]) -> Path:
    if args.checkpoint is not None:
        return args.checkpoint
    checkpoint = response_manifest.get("checkpoint")
    if not checkpoint:
        raise ValueError("--checkpoint is required when response_manifest.json has no checkpoint")
    return Path(str(checkpoint))


def _load_pipeline(checkpoint: Path, device: torch.device) -> StableDiffusionXLPipeline:
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    pipe = StableDiffusionXLPipeline.from_single_file(
        checkpoint.as_posix(),
        torch_dtype=dtype,
        local_files_only=True,
    )
    pipe.set_progress_bar_config(disable=True)
    pipe.vae.eval()
    pipe.unet.eval()
    return pipe


def _clear_cuda() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _move_optional(module: torch.nn.Module | None, device: torch.device) -> None:
    if module is not None:
        module.to(device)


def _offload_optional(module: torch.nn.Module | None) -> None:
    if module is not None:
        module.to("cpu")


def _image_transform(resolution: int) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(resolution, interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.CenterCrop(resolution),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ]
    )


def _encode_prompt(
    pipe: StableDiffusionXLPipeline,
    prompts: list[str],
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    encoded = pipe.encode_prompt(
        prompt=prompts,
        device=device,
        num_images_per_prompt=1,
        do_classifier_free_guidance=False,
    )
    if len(encoded) == 4:
        prompt_embeds, _negative_prompt_embeds, pooled_prompt_embeds, _negative_pooled_prompt_embeds = encoded
        return prompt_embeds, pooled_prompt_embeds
    if len(encoded) == 2:
        prompt_embeds, pooled_prompt_embeds = encoded
        return prompt_embeds, pooled_prompt_embeds
    raise ValueError(f"unexpected encode_prompt return length: {len(encoded)}")


def _time_ids(
    pipe: StableDiffusionXLPipeline,
    *,
    batch_size: int,
    resolution: int,
    dtype: torch.dtype,
    device: torch.device,
    pooled_prompt_embeds: torch.Tensor,
) -> torch.Tensor:
    add_time_ids = pipe._get_add_time_ids(
        (resolution, resolution),
        (0, 0),
        (resolution, resolution),
        dtype=dtype,
        text_encoder_projection_dim=pooled_prompt_embeds.shape[-1],
    )
    return add_time_ids.to(device).repeat(batch_size, 1)


def _sample_noise(shape: torch.Size, *, device: torch.device, dtype: torch.dtype, seed: int) -> torch.Tensor:
    generator = torch.Generator(device=device.type).manual_seed(seed)
    return torch.randn(shape, generator=generator, device=device, dtype=dtype)


def _summarize_scores(labels: np.ndarray, scores: np.ndarray, *, score_name: str) -> dict[str, Any]:
    auc = float(roc_auc_score(labels, scores))
    thresholds = sorted(set(float(value) for value in scores), reverse=True)
    best: dict[str, Any] | None = None
    tpr_details: dict[str, Any] = {}
    positives = int(labels.sum())
    negatives = int((labels == 0).sum())

    for threshold in thresholds:
        predicted = scores >= threshold
        tp = int(((labels == 1) & predicted).sum())
        fp = int(((labels == 0) & predicted).sum())
        tn = negatives - fp
        fn = positives - tp
        asr = (tp + tn) / len(labels)
        if best is None or asr > float(best["asr"]):
            best = {
                "asr": float(asr),
                "threshold": float(threshold),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
            }
        for name, cap in (("tpr_at_1pct_fpr", 0.01), ("tpr_at_0_1pct_fpr", 0.001)):
            allowed_fp = int(np.floor(cap * negatives))
            if fp <= allowed_fp:
                tpr = tp / positives if positives else 0.0
                current = tpr_details.get(name)
                if current is None or tpr > float(current["tpr"]):
                    tpr_details[name] = {
                        "tpr": float(tpr),
                        "threshold": float(threshold),
                        "tp": tp,
                        "fp": fp,
                        "allowed_fp": allowed_fp,
                    }

    assert best is not None
    for name, cap in (("tpr_at_1pct_fpr", 0.01), ("tpr_at_0_1pct_fpr", 0.001)):
        tpr_details.setdefault(
            name,
            {"tpr": 0.0, "threshold": None, "tp": 0, "fp": None, "allowed_fp": int(np.floor(cap * negatives))},
        )

    return {
        "score_name": score_name,
        "score_direction": "higher_is_more_member",
        "auc": auc,
        "reverse_auc": float(1.0 - auc),
        "asr": float(best["asr"]),
        "best_threshold": best,
        "tpr_at_1pct_fpr": float(tpr_details["tpr_at_1pct_fpr"]["tpr"]),
        "tpr_at_1pct_fpr_detail": tpr_details["tpr_at_1pct_fpr"],
        "tpr_at_0_1pct_fpr": float(tpr_details["tpr_at_0_1pct_fpr"]["tpr"]),
        "tpr_at_0_1pct_fpr_detail": tpr_details["tpr_at_0_1pct_fpr"],
        "member_score_mean": float(scores[labels == 1].mean()),
        "nonmember_score_mean": float(scores[labels == 0].mean()),
        "member_loss_mean": float((-scores[labels == 1]).mean()),
        "nonmember_loss_mean": float((-scores[labels == 0]).mean()),
    }


class CommonCanvasDenoisingLossScorer:
    def __init__(self, args: argparse.Namespace, checkpoint: Path, device: torch.device) -> None:
        self.args = args
        self.device = device
        self.dtype = torch.float16 if device.type == "cuda" else torch.float32
        self.pipe = _load_pipeline(checkpoint, device)
        self.scheduler = DDPMScheduler(
            num_train_timesteps=1000,
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
        )
        self.scheduler.alphas_cumprod = self.scheduler.alphas_cumprod.to(device)
        self.transform = _image_transform(args.resolution)

    def _load_pixels(self, rows: list[dict[str, Any]], dataset_root: Path) -> torch.Tensor:
        images = []
        for row in rows:
            path = dataset_root / row["query_path"]
            image = Image.open(path).convert("RGB")
            images.append(self.transform(image))
        return torch.stack(images).to(self.device, dtype=self.dtype)

    def score_batch(
        self,
        rows: list[dict[str, Any]],
        *,
        dataset_root: Path,
        timesteps: list[int],
        global_start_index: int,
    ) -> list[dict[str, Any]]:
        prompts = [row["prompt"] for row in rows]

        self.pipe.vae.to(self.device)
        self.pipe.vae.float()
        pixels = self._load_pixels(rows, dataset_root)
        pixels = pixels.float()
        with torch.inference_mode(), torch.autocast(
            device_type=self.device.type,
            dtype=torch.float32,
            enabled=False,
        ):
            latents = self.pipe.vae.encode(pixels).latent_dist.mean
            latents = latents * self.pipe.vae.config.scaling_factor
        del pixels
        if not torch.isfinite(latents).all():
            raise ValueError("non-finite VAE latents; aborting denoising-loss scout")
        latents = latents.to(dtype=self.dtype)
        self.pipe.vae.to("cpu")
        _clear_cuda()

        _move_optional(self.pipe.text_encoder, self.device)
        _move_optional(self.pipe.text_encoder_2, self.device)
        with torch.inference_mode(), torch.autocast(
            device_type=self.device.type,
            dtype=self.dtype,
            enabled=self.device.type == "cuda",
        ):
            prompt_embeds, pooled_prompt_embeds = _encode_prompt(self.pipe, prompts, self.device)
            add_time_ids = _time_ids(
                self.pipe,
                batch_size=len(rows),
                resolution=self.args.resolution,
                dtype=prompt_embeds.dtype,
                device=self.device,
                pooled_prompt_embeds=pooled_prompt_embeds,
            )
            added_cond_kwargs = {"text_embeds": pooled_prompt_embeds, "time_ids": add_time_ids}
        _offload_optional(self.pipe.text_encoder)
        _offload_optional(self.pipe.text_encoder_2)
        _clear_cuda()

        self.pipe.unet.to(self.device)
        with torch.inference_mode(), torch.autocast(
            device_type=self.device.type,
            dtype=self.dtype,
            enabled=self.device.type == "cuda",
        ):
            per_timestep_losses: list[torch.Tensor] = []
            for timestep in timesteps:
                noises = []
                for local_index in range(len(rows)):
                    seed = self.args.noise_seed_base + int(timestep) * 100_000 + global_start_index + local_index
                    noises.append(_sample_noise(latents[local_index : local_index + 1].shape, device=self.device, dtype=latents.dtype, seed=seed))
                noise = torch.cat(noises, dim=0)
                timestep_tensor = torch.full((len(rows),), int(timestep), device=self.device, dtype=torch.long)
                noised_latents = self.scheduler.add_noise(latents, noise, timestep_tensor)
                pred_noise = self.pipe.unet(
                    noised_latents,
                    timestep_tensor,
                    encoder_hidden_states=prompt_embeds,
                    added_cond_kwargs=added_cond_kwargs,
                ).sample
                if not torch.isfinite(pred_noise).all():
                    raise ValueError(f"non-finite UNet prediction at timestep {timestep}")
                loss = torch.mean((pred_noise.float() - noise.float()) ** 2, dim=(1, 2, 3))
                if not torch.isfinite(loss).all():
                    raise ValueError(f"non-finite denoising loss at timestep {timestep}")
                per_timestep_losses.append(loss.detach().cpu())
                del noise, timestep_tensor, noised_latents, pred_noise, loss

        losses = torch.stack(per_timestep_losses, dim=1).numpy()
        del latents, prompt_embeds, pooled_prompt_embeds, add_time_ids, added_cond_kwargs, per_timestep_losses
        self.pipe.unet.to("cpu")
        _clear_cuda()
        records: list[dict[str, Any]] = []
        for local_index, row in enumerate(rows):
            loss_by_timestep = {
                str(timestep): float(losses[local_index, timestep_index])
                for timestep_index, timestep in enumerate(timesteps)
            }
            mean_loss = float(np.mean(list(loss_by_timestep.values())))
            records.append(
                {
                    **row,
                    "query_path": f"<DOWNLOAD_ROOT>/black-box/datasets/response-contract-copymark-commoncanvas-20260512/{row['query_path']}",
                    "loss_by_timestep": loss_by_timestep,
                    "mean_loss": mean_loss,
                    "score": -mean_loss,
                }
            )
        return records


def main() -> None:
    args = parse_args()
    if args.samples_per_split <= 0:
        raise ValueError("--samples-per-split must be positive")
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    timesteps = [int(value.strip()) for value in args.timesteps.split(",") if value.strip()]
    if not timesteps:
        raise ValueError("--timesteps must contain at least one integer")
    if any(timestep < 0 or timestep >= 1000 for timestep in timesteps):
        raise ValueError("--timesteps values must be in [0, 999]")

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")
    dataset_manifest = _load_json(args.dataset_root / "manifest.json")
    response_manifest = _load_json(args.supplementary_root / "response_manifest.json")
    checkpoint = _resolve_checkpoint(args, response_manifest)
    rows = _selected_rows(dataset_manifest, args.samples_per_split)

    scorer = CommonCanvasDenoisingLossScorer(args, checkpoint, device)
    records: list[dict[str, Any]] = []
    for start in range(0, len(rows), args.batch_size):
        batch = rows[start : start + args.batch_size]
        batch_records = scorer.score_batch(
            batch,
            dataset_root=args.dataset_root,
            timesteps=timesteps,
            global_start_index=start,
        )
        records.extend(batch_records)
        print(
            f"scored {min(start + len(batch), len(rows))}/{len(rows)} "
            f"last_score={batch_records[-1]['score']:.6f}",
            flush=True,
        )

    labels = np.asarray([record["label"] for record in records], dtype=int)
    scores = np.asarray([record["score"] for record in records], dtype=float)
    score_name = "negative_conditional_denoising_mse_mean_t" + "_".join(str(value) for value in timesteps)
    metrics = _summarize_scores(labels, scores, score_name=score_name)
    verdict = (
        "positive_scout"
        if float(metrics["auc"]) >= 0.6 and float(metrics["tpr_at_1pct_fpr"]) > 0.0
        else "negative_or_weak"
    )
    payload = {
        "asset_id": dataset_manifest.get("asset_id", "response-contract-copymark-commoncanvas-20260512"),
        "model_identity": response_manifest.get("model_identity", "common-canvas/CommonCanvas-XL-C"),
        "method": "commoncanvas_conditional_denoising_loss",
        "hypothesis": (
            "If CommonCanvas memorizes its CommonCatalog training images in the diffusion training objective, "
            "member query images should have lower caption-conditioned noise-prediction MSE than COCO holdout images."
        ),
        "boundary": (
            "Single bounded PIA-style internal-score scout on the existing CopyMark/CommonCanvas 50/50 packet. "
            "This is not a pixel/CLIP/prompt-response/seed-stability variant and is not admitted evidence."
        ),
        "config": {
            "samples_per_split": args.samples_per_split,
            "timesteps": timesteps,
            "resolution": args.resolution,
            "batch_size": args.batch_size,
            "noise_seed_base": args.noise_seed_base,
            "checkpoint_name": checkpoint.name,
            "checkpoint_bytes": checkpoint.stat().st_size if checkpoint.is_file() else None,
            "device": str(device),
            "torch": torch.__version__,
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "scheduler": "DDPMScheduler(beta_start=0.00085,beta_end=0.012,beta_schedule=scaled_linear)",
        },
        "metric": metrics,
        "verdict": verdict,
        "stop_condition": (
            "If AUC is below 0.60 or TPR@1%FPR is near zero, close CommonCanvas PIA-style denoising-loss "
            "as a successor mechanism and do not expand timestep, subset, scheduler, or loss-weight matrices."
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("asset_id", "method", "metric", "verdict")}, indent=2, ensure_ascii=False))

    del scorer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
