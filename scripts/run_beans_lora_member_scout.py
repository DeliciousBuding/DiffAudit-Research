from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from peft import LoraConfig, get_peft_model_state_dict
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
            "Train a bounded known-split Beans LoRA target on member images and "
            "score member/nonmember images with conditional denoising loss."
        )
    )
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--sd15-model-dir", type=Path, required=True)
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--weights-output-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples-per-split", type=int, default=25)
    parser.add_argument("--train-steps", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--lora-rank", type=int, default=4)
    parser.add_argument("--lora-alpha", type=int, default=4)
    parser.add_argument("--score-timesteps", default="100,300,600")
    parser.add_argument("--seed", type=int, default=20260513)
    parser.add_argument("--noise-seed-base", type=int, default=2026051300)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--gradient-checkpointing", action="store_true")
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


def _parse_score_timesteps(value: str) -> list[int]:
    timesteps = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not timesteps:
        raise ValueError("--score-timesteps must contain at least one timestep")
    if any(t < 0 or t >= 1000 for t in timesteps):
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


def _load_components(
    model_dir: Path,
    device: torch.device,
    *,
    gradient_checkpointing: bool,
    lora_rank: int,
    lora_alpha: int,
) -> tuple[Any, ...]:
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
    unet = UNet2DConditionModel.from_pretrained(
        model_dir,
        subfolder="unet",
        torch_dtype=dtype,
        local_files_only=True,
    ).to(device)
    scheduler = DDPMScheduler.from_pretrained(model_dir, subfolder="scheduler", local_files_only=True)

    text_encoder.eval().requires_grad_(False)
    vae.eval().requires_grad_(False)
    unet.requires_grad_(False)
    if gradient_checkpointing:
        unet.enable_gradient_checkpointing()

    lora_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_alpha,
        init_lora_weights="gaussian",
        target_modules=["to_q", "to_k", "to_v", "to_out.0"],
    )
    unet.add_adapter(lora_config)
    for parameter in unet.parameters():
        if parameter.requires_grad:
            parameter.data = parameter.data.to(torch.float32)
    return tokenizer, text_encoder, vae, unet, scheduler


def _apply_lora_config(unet: UNet2DConditionModel, *, rank: int, alpha: int) -> None:
    # UNet2DConditionModel.add_adapter currently accepts one active adapter.
    if not hasattr(unet, "peft_config"):
        raise RuntimeError("UNet adapter injection failed before custom LoRA config could be applied")
    default_name = next(iter(unet.peft_config.keys()))
    if int(unet.peft_config[default_name].r) == rank and int(unet.peft_config[default_name].lora_alpha) == alpha:
        return
    raise RuntimeError(
        "LoRA config mismatch after adapter injection: "
        f"requested r={rank}, alpha={alpha}; "
        f"actual r={unet.peft_config[default_name].r}, alpha={unet.peft_config[default_name].lora_alpha}"
    )


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


def _train_lora(
    *,
    train_pixels: torch.Tensor,
    tokenizer: Any,
    text_encoder: Any,
    vae: AutoencoderKL,
    unet: UNet2DConditionModel,
    scheduler: DDPMScheduler,
    args: argparse.Namespace,
    device: torch.device,
) -> list[dict[str, Any]]:
    unet.train()
    trainable = [param for param in unet.parameters() if param.requires_grad]
    if not trainable:
        raise RuntimeError("LoRA adapter injection produced no trainable parameters")
    optimizer = torch.optim.AdamW(trainable, lr=float(args.learning_rate))
    rng = random.Random(int(args.seed))
    history: list[dict[str, Any]] = []
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    prompt_embeds_one = _prompt_embeds(tokenizer, text_encoder, PROMPT, 1, device)

    for step in range(1, int(args.train_steps) + 1):
        batch_indices = [rng.randrange(train_pixels.shape[0]) for _ in range(int(args.batch_size))]
        pixel_values = train_pixels[batch_indices].to(device=device, dtype=dtype)
        with torch.no_grad():
            latents = _encode_latents(vae, pixel_values)

        step_generator = _torch_generator(device, int(args.seed) + step)
        noise = torch.randn(latents.shape, generator=step_generator, device=device, dtype=latents.dtype)
        timesteps = torch.randint(
            0,
            int(scheduler.config.num_train_timesteps),
            (latents.shape[0],),
            generator=step_generator,
            device=device,
            dtype=torch.long,
        )
        noisy_latents = scheduler.add_noise(latents, noise, timesteps)
        embeds = prompt_embeds_one.repeat(latents.shape[0], 1, 1)

        prediction = unet(noisy_latents, timesteps, encoder_hidden_states=embeds).sample
        loss = F.mse_loss(prediction.float(), noise.float())
        if not torch.isfinite(loss):
            raise RuntimeError(f"non-finite training loss at step {step}: {float(loss.detach().cpu())}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, max_norm=1.0)
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)

        if step == 1 or step == int(args.train_steps) or step % max(1, int(args.train_steps) // 10) == 0:
            history.append({"step": step, "loss": float(loss.detach().cpu())})
            print(f"step={step} loss={history[-1]['loss']:.6f}", flush=True)

    unet.eval()
    return history


@torch.no_grad()
def _score_records(
    *,
    records: list[ImageRecord],
    all_pixels: torch.Tensor,
    tokenizer: Any,
    text_encoder: Any,
    vae: AutoencoderKL,
    unet: UNet2DConditionModel,
    scheduler: DDPMScheduler,
    timesteps: list[int],
    args: argparse.Namespace,
    device: torch.device,
) -> list[dict[str, Any]]:
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    prompt_embeds_one = _prompt_embeds(tokenizer, text_encoder, PROMPT, 1, device)
    rows: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        pixel_values = all_pixels[idx : idx + 1].to(device=device, dtype=dtype)
        latents = _encode_latents(vae, pixel_values)
        losses: dict[str, float] = {}
        for timestep in timesteps:
            noise_seed = int(args.noise_seed_base) + idx * 10_000 + timestep
            generator = _torch_generator(device, noise_seed)
            noise = torch.randn(latents.shape, generator=generator, device=device, dtype=latents.dtype)
            t = torch.tensor([timestep], device=device, dtype=torch.long)
            noisy_latents = scheduler.add_noise(latents, noise, t)
            prediction = unet(noisy_latents, t, encoder_hidden_states=prompt_embeds_one).sample
            loss = F.mse_loss(prediction.float(), noise.float(), reduction="mean")
            losses[str(timestep)] = float(loss.detach().cpu())
        mean_loss = float(np.mean(list(losses.values())))
        rows.append(
            {
                "id": record.record_id,
                "split": record.split,
                "label": record.label,
                "source_index": record.source_index,
                "query_file": record.path.name,
                "query_sha256": record.sha256,
                "per_timestep_denoising_loss": losses,
                "mean_denoising_loss": mean_loss,
                "score": -mean_loss,
            }
        )
    return rows


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
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
    member_losses = -member_scores
    nonmember_losses = -nonmember_scores
    auc = float(roc_auc_score(labels, scores))
    return {
        "score_name": "negative_mean_conditional_denoising_loss_after_member_lora",
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
        "member_loss_mean": float(member_losses.mean()),
        "nonmember_loss_mean": float(nonmember_losses.mean()),
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

    random.seed(int(args.seed))
    np.random.seed(int(args.seed))
    torch.manual_seed(int(args.seed))
    if device.type == "cuda":
        torch.cuda.manual_seed_all(int(args.seed))

    records = _records(args.dataset_root, int(args.samples_per_split))
    member_records = [record for record in records if record.label == 1]
    all_pixels = _batch_tensors(records, int(args.image_size))
    train_pixels = _batch_tensors(member_records, int(args.image_size))
    timesteps = _parse_score_timesteps(str(args.score_timesteps))

    tokenizer, text_encoder, vae, unet, scheduler = _load_components(
        args.sd15_model_dir,
        device,
        gradient_checkpointing=bool(args.gradient_checkpointing),
        lora_rank=int(args.lora_rank),
        lora_alpha=int(args.lora_alpha),
    )
    _apply_lora_config(unet, rank=int(args.lora_rank), alpha=int(args.lora_alpha))

    train_history = _train_lora(
        train_pixels=train_pixels,
        tokenizer=tokenizer,
        text_encoder=text_encoder,
        vae=vae,
        unet=unet,
        scheduler=scheduler,
        args=args,
        device=device,
    )
    score_rows = _score_records(
        records=records,
        all_pixels=all_pixels,
        tokenizer=tokenizer,
        text_encoder=text_encoder,
        vae=vae,
        unet=unet,
        scheduler=scheduler,
        timesteps=timesteps,
        args=args,
        device=device,
    )
    metrics = _summarize(score_rows)

    args.weights_output_dir.mkdir(parents=True, exist_ok=True)
    weights_path = args.weights_output_dir / "unet_lora_peft_state.pt"
    lora_state = get_peft_model_state_dict(unet)
    torch.save({key: value.detach().cpu() for key, value in lora_state.items()}, weights_path)
    weights_sha256 = _sha256(weights_path)

    verdict = (
        "candidate_signal; needs independent split before promotion"
        if float(metrics["auc"]) >= 0.60 and float(metrics["tpr_at_1pct_fpr"]) > 0.0
        else "weak; close this exact Beans LoRA denoising-loss scout"
    )
    result = {
        "experiment_id": "beans-lora-member-denoising-loss-scout-20260513",
        "date": "2026-05-13",
        "status": "bounded_scout",
        "question": (
            "If the target SD1.5 LoRA is fine-tuned on the Beans member split, "
            "does conditional denoising loss separate exact training members "
            "from held-out Beans nonmembers?"
        ),
        "membership_semantics": {
            "target_model_identity": "stable-diffusion-v1-5 plus bounded Beans member-only UNet LoRA",
            "member_definition": "the first N query/member PNGs are used as LoRA fine-tuning images",
            "nonmember_definition": "the first N query/nonmember PNGs are held out from LoRA fine-tuning",
            "not_black_box": True,
            "not_sd15_base_membership": True,
        },
        "inputs": {
            "dataset_root": _display_path(args.dataset_root, download_root=args.download_root),
            "sd15_model_dir": _display_path(args.sd15_model_dir, download_root=args.download_root),
            "weights_output_dir": _display_path(args.weights_output_dir, download_root=args.download_root),
            "samples_per_split": int(args.samples_per_split),
            "prompt": PROMPT,
            "image_size": int(args.image_size),
            "score_timesteps": timesteps,
            "seed": int(args.seed),
            "noise_seed_base": int(args.noise_seed_base),
        },
        "training": {
            "train_member_count": len(member_records),
            "train_steps": int(args.train_steps),
            "batch_size": int(args.batch_size),
            "learning_rate": float(args.learning_rate),
            "lora_rank": int(args.lora_rank),
            "lora_alpha": int(args.lora_alpha),
            "gradient_checkpointing": bool(args.gradient_checkpointing),
            "history": train_history,
        },
        "runtime": {
            "python_device": str(device),
            "torch_version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "weights": {
            "path": _display_path(weights_path, download_root=args.download_root),
            "sha256": weights_sha256,
            "format": "PEFT UNet LoRA state dict saved outside git",
        },
        "metrics": metrics,
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
            ],
        },
        "verdict": verdict,
        "platform_runtime_impact": "none; this is a known-split internal scout, not admitted black-box evidence",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics, "verdict": verdict, "output": args.output.as_posix()}, indent=2), flush=True)


if __name__ == "__main__":
    main()
