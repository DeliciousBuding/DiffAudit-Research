from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from peft import LoraConfig
from PIL import Image
from sklearn.metrics import roc_auc_score
from transformers import CLIPTextModel, CLIPTokenizer


PROMPT = "a clear documentary photograph of a bean leaf"


@dataclass(frozen=True)
class ImageRecord:
    split: str
    label: int
    source_index: int
    path: Path
    sha256: str | None

    @property
    def record_id(self) -> str:
        return f"{self.split}_{self.source_index:03d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score exact Beans member/nonmember images by measuring how strongly "
            "a member-only LoRA changes the base UNet noise prediction."
        )
    )
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--sd15-model-dir", type=Path, required=True)
    parser.add_argument("--lora-state", type=Path, required=True)
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples-per-split", type=int, default=25)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--score-timesteps", default="100,300,600")
    parser.add_argument("--noise-seed-base", type=int, default=2026051400)
    parser.add_argument("--lora-rank", type=int, default=4)
    parser.add_argument("--lora-alpha", type=int, default=4)
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, *, download_root: Path) -> str:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(download_root.resolve())
        return f"<DOWNLOAD_ROOT>/{rel.as_posix()}"
    except ValueError:
        return path.as_posix()


def _parse_timesteps(value: str) -> list[int]:
    timesteps = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not timesteps:
        raise ValueError("--score-timesteps must contain at least one timestep")
    if any(timestep < 0 or timestep >= 1000 for timestep in timesteps):
        raise ValueError(f"score timesteps must be in [0, 999], got {timesteps}")
    return timesteps


def _records(dataset_root: Path, samples_per_split: int) -> list[ImageRecord]:
    manifest = _load_json(dataset_root / "manifest.json")
    integrity = manifest.get("integrity", {})
    records: list[ImageRecord] = []
    for split, label in (("member", 1), ("nonmember", 0)):
        split_dir = dataset_root / "query" / split
        paths = sorted(split_dir.glob("*.png"))
        if len(paths) < samples_per_split:
            raise ValueError(f"{split_dir} has {len(paths)} PNGs, need {samples_per_split}")
        for source_index, path in enumerate(paths[:samples_per_split]):
            records.append(
                ImageRecord(
                    split=split,
                    label=label,
                    source_index=source_index,
                    path=path,
                    sha256=integrity.get(split, {}).get(path.name),
                )
            )
    return records


def _image_to_tensor(path: Path, image_size: int) -> torch.Tensor:
    image = Image.open(path).convert("RGB").resize((image_size, image_size), Image.Resampling.BICUBIC)
    array = np.asarray(image, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array).permute(2, 0, 1)
    return tensor.mul(2.0).sub(1.0)


def _batch_tensors(records: list[ImageRecord], image_size: int) -> torch.Tensor:
    return torch.stack([_image_to_tensor(record.path, image_size) for record in records], dim=0)


def _prompt_embeds(tokenizer: Any, text_encoder: Any, prompt: str, batch_size: int, device: torch.device) -> torch.Tensor:
    tokens = tokenizer(
        [prompt],
        padding="max_length",
        max_length=tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt",
    )
    input_ids = tokens.input_ids.to(device)
    with torch.no_grad():
        embeds = text_encoder(input_ids)[0]
    return embeds.repeat(batch_size, 1, 1)


@torch.no_grad()
def _encode_latents(vae: AutoencoderKL, pixel_values: torch.Tensor) -> torch.Tensor:
    encoded = vae.encode(pixel_values).latent_dist.mode()
    return encoded * float(vae.config.scaling_factor)


def _torch_generator(device: torch.device, seed: int) -> torch.Generator:
    if device.type == "cuda":
        return torch.Generator(device=device).manual_seed(seed)
    return torch.Generator().manual_seed(seed)


def _load_static_components(model_dir: Path, device: torch.device) -> tuple[Any, ...]:
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    tokenizer = CLIPTokenizer.from_pretrained(model_dir, subfolder="tokenizer", local_files_only=True)
    text_encoder = CLIPTextModel.from_pretrained(
        model_dir,
        subfolder="text_encoder",
        torch_dtype=dtype,
        local_files_only=True,
    ).to(device)
    vae = AutoencoderKL.from_pretrained(
        model_dir,
        subfolder="vae",
        torch_dtype=dtype,
        local_files_only=True,
    ).to(device)
    scheduler = DDPMScheduler.from_pretrained(model_dir, subfolder="scheduler", local_files_only=True)
    text_encoder.eval().requires_grad_(False)
    vae.eval().requires_grad_(False)
    return tokenizer, text_encoder, vae, scheduler


def _load_unet(model_dir: Path, device: torch.device) -> UNet2DConditionModel:
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    unet = UNet2DConditionModel.from_pretrained(
        model_dir,
        subfolder="unet",
        torch_dtype=dtype,
        local_files_only=True,
    ).to(device)
    unet.eval().requires_grad_(False)
    return unet


def _inject_lora(unet: UNet2DConditionModel, *, rank: int, alpha: int) -> None:
    config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        init_lora_weights="gaussian",
        target_modules=["to_q", "to_k", "to_v", "to_out.0"],
    )
    unet.add_adapter(config)
    unet.eval().requires_grad_(False)


def _normalize_lora_state(raw_state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    normalized: dict[str, torch.Tensor] = {}
    for key, value in raw_state.items():
        if ".lora_A.weight" in key:
            key = key.replace(".lora_A.weight", ".lora_A.default.weight")
        elif ".lora_B.weight" in key:
            key = key.replace(".lora_B.weight", ".lora_B.default.weight")
        normalized[key] = value
    return normalized


def _load_lora_state(unet: UNet2DConditionModel, lora_state: Path) -> tuple[int, int]:
    raw_state = torch.load(lora_state, map_location="cpu", weights_only=True)
    if not isinstance(raw_state, dict):
        raise TypeError(f"expected LoRA state dict at {lora_state}, got {type(raw_state)!r}")
    normalized = _normalize_lora_state(raw_state)
    missing, unexpected = unet.load_state_dict(normalized, strict=False)
    missing_lora = [key for key in missing if ".lora_" in key]
    if missing_lora or unexpected:
        raise RuntimeError(
            "LoRA state did not load cleanly: "
            f"missing_lora={missing_lora[:5]} unexpected={unexpected[:5]}"
        )
    return len(missing), len(unexpected)


@torch.no_grad()
def _score_records(
    *,
    records: list[ImageRecord],
    pixels: torch.Tensor,
    tokenizer: Any,
    text_encoder: Any,
    vae: AutoencoderKL,
    scheduler: DDPMScheduler,
    base_unet: UNet2DConditionModel,
    lora_unet: UNet2DConditionModel,
    timesteps: list[int],
    noise_seed_base: int,
    device: torch.device,
) -> list[dict[str, Any]]:
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    embeds = _prompt_embeds(tokenizer, text_encoder, PROMPT, 1, device)
    rows: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        pixel_values = pixels[idx : idx + 1].to(device=device, dtype=dtype)
        latents = _encode_latents(vae, pixel_values)
        per_timestep: dict[str, dict[str, float]] = {}
        delta_scores: list[float] = []
        relative_delta_scores: list[float] = []
        loss_delta_scores: list[float] = []
        for timestep in timesteps:
            noise_seed = noise_seed_base + idx * 10_000 + timestep
            generator = _torch_generator(device, noise_seed)
            noise = torch.randn(latents.shape, generator=generator, device=device, dtype=latents.dtype)
            t = torch.tensor([timestep], device=device, dtype=torch.long)
            noised_latents = scheduler.add_noise(latents, noise, t)
            base_pred = base_unet(noised_latents, t, encoder_hidden_states=embeds).sample
            lora_pred = lora_unet(noised_latents, t, encoder_hidden_states=embeds).sample
            delta = (lora_pred.float() - base_pred.float()).flatten()
            base_flat = base_pred.float().flatten()
            lora_loss = F.mse_loss(lora_pred.float(), noise.float()).detach()
            base_loss = F.mse_loss(base_pred.float(), noise.float()).detach()
            delta_l2 = torch.linalg.vector_norm(delta).detach()
            base_l2 = torch.linalg.vector_norm(base_flat).detach().clamp_min(1e-12)
            relative_delta = delta_l2 / base_l2
            loss_delta = base_loss - lora_loss
            delta_scores.append(float(delta_l2.cpu()))
            relative_delta_scores.append(float(relative_delta.cpu()))
            loss_delta_scores.append(float(loss_delta.cpu()))
            per_timestep[str(timestep)] = {
                "delta_l2": float(delta_l2.cpu()),
                "relative_delta_l2": float(relative_delta.cpu()),
                "base_loss": float(base_loss.cpu()),
                "lora_loss": float(lora_loss.cpu()),
                "base_minus_lora_loss": float(loss_delta.cpu()),
            }
        mean_delta = float(np.mean(delta_scores))
        mean_relative_delta = float(np.mean(relative_delta_scores))
        mean_loss_delta = float(np.mean(loss_delta_scores))
        rows.append(
            {
                "id": record.record_id,
                "split": record.split,
                "label": record.label,
                "source_index": record.source_index,
                "query_file": record.path.name,
                "query_sha256": record.sha256,
                "per_timestep": per_timestep,
                "mean_delta_l2": mean_delta,
                "mean_relative_delta_l2": mean_relative_delta,
                "mean_base_minus_lora_loss": mean_loss_delta,
                "score": mean_relative_delta,
            }
        )
    return rows


def _summarize(rows: list[dict[str, Any]], *, score_key: str, score_name: str) -> dict[str, Any]:
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    scores = np.asarray([float(row[score_key]) for row in rows], dtype=np.float64)
    positives = int(labels.sum())
    negatives = int((labels == 0).sum())
    thresholds = sorted(set(float(value) for value in scores), reverse=True)
    best: dict[str, Any] | None = None
    tpr_details: dict[str, Any] = {}

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
            allowed_fp = int(math.floor(cap * negatives))
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
            {"tpr": 0.0, "threshold": None, "tp": 0, "fp": None, "allowed_fp": int(math.floor(cap * negatives))},
        )

    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    auc = float(roc_auc_score(labels, scores))
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
        "member_score_mean": float(member_scores.mean()),
        "nonmember_score_mean": float(nonmember_scores.mean()),
        "member_count": positives,
        "nonmember_count": negatives,
    }


def main() -> None:
    args = parse_args()
    device = torch.device(args.device if torch.cuda.is_available() or not str(args.device).startswith("cuda") else "cpu")
    if str(args.device).startswith("cuda") and device.type != "cuda":
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false")
    if device.type == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True

    records = _records(args.dataset_root, int(args.samples_per_split))
    pixels = _batch_tensors(records, int(args.image_size))
    timesteps = _parse_timesteps(str(args.score_timesteps))

    tokenizer, text_encoder, vae, scheduler = _load_static_components(args.sd15_model_dir, device)
    base_unet = _load_unet(args.sd15_model_dir, device)
    lora_unet = _load_unet(args.sd15_model_dir, device)
    _inject_lora(lora_unet, rank=int(args.lora_rank), alpha=int(args.lora_alpha))
    lora_missing_count, lora_unexpected_count = _load_lora_state(lora_unet, args.lora_state)

    score_rows = _score_records(
        records=records,
        pixels=pixels,
        tokenizer=tokenizer,
        text_encoder=text_encoder,
        vae=vae,
        scheduler=scheduler,
        base_unet=base_unet,
        lora_unet=lora_unet,
        timesteps=timesteps,
        noise_seed_base=int(args.noise_seed_base),
        device=device,
    )
    metrics = _summarize(
        score_rows,
        score_key="mean_relative_delta_l2",
        score_name="mean_relative_unet_prediction_delta_l2_after_member_lora",
    )
    loss_delta_metrics = _summarize(
        score_rows,
        score_key="mean_base_minus_lora_loss",
        score_name="mean_base_minus_lora_denoising_loss_delta",
    )
    verdict = (
        "positive_scout"
        if float(metrics["auc"]) >= 0.6 and float(metrics["tpr_at_1pct_fpr"]) > 0.0
        else "negative_or_weak"
    )
    payload = {
        "experiment_id": "beans-lora-delta-sensitivity-20260513",
        "date": "2026-05-13",
        "status": "bounded_scout",
        "question": (
            "Does a member-only Beans LoRA perturb the SD1.5 UNet noise prediction more strongly "
            "on exact LoRA training members than on held-out Beans nonmembers?"
        ),
        "observable_family": "architecture-local parameter-delta sensitivity",
        "not_same_family_as": [
            "raw denoising MSE",
            "x0 residual",
            "pixel or CLIP distance",
            "final-layer gradient norm/cosine",
            "midfreq cutoff",
        ],
        "membership_semantics": {
            "target_model_identity": "stable-diffusion-v1-5 plus bounded Beans member-only UNet LoRA",
            "member_definition": "the first N query/member PNGs were used as LoRA fine-tuning images",
            "nonmember_definition": "the first N query/nonmember PNGs were held out from LoRA fine-tuning",
            "not_black_box": True,
            "not_sd15_base_membership": True,
        },
        "inputs": {
            "dataset_root": _display_path(args.dataset_root, download_root=args.download_root),
            "sd15_model_dir": _display_path(args.sd15_model_dir, download_root=args.download_root),
            "lora_state": _display_path(args.lora_state, download_root=args.download_root),
            "lora_state_sha256": _sha256(args.lora_state),
            "samples_per_split": int(args.samples_per_split),
            "prompt": PROMPT,
            "image_size": int(args.image_size),
            "score_timesteps": timesteps,
            "noise_seed_base": int(args.noise_seed_base),
        },
        "runtime": {
            "python_device": str(device),
            "torch_version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "lora_load_missing_count": lora_missing_count,
            "lora_load_unexpected_count": lora_unexpected_count,
        },
        "metrics": metrics,
        "secondary_loss_delta_metrics": loss_delta_metrics,
        "rows": score_rows,
        "stop_gate": {
            "close_if_auc_below": 0.60,
            "close_if_tpr_at_1pct_fpr_is_zero_or_near_zero": True,
            "no_matrix_expansion": [
                "train_steps",
                "rank",
                "resolution",
                "prompt",
                "scheduler",
                "score_timestep",
                "layer or block sweep",
            ],
        },
        "verdict": verdict,
        "platform_runtime_impact": "none; this is a known-split internal mechanism scout, not admitted evidence",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics, "secondary_loss_delta_metrics": loss_delta_metrics, "verdict": verdict}, indent=2))


if __name__ == "__main__":
    main()
