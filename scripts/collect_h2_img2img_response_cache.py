from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image

from diffaudit.attacks.h2_cross_asset import default_roots
from diffaudit.attacks.h2_response_strength import compute_lowpass_min_distances


DEFAULT_STRENGTHS = (0.35, 0.55, 0.75)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    if isinstance(value, np.ndarray):
        return _sanitize(value.tolist())
    if isinstance(value, np.generic):
        return _sanitize(value.item())
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _load_torch_payload(path: Path) -> Any:
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def _load_recon_split(split_root: Path) -> tuple[list[str], list[Image.Image], list[str], list[Image.Image]]:
    member_payload = _load_torch_payload(split_root / "target_member.pt")
    nonmember_payload = _load_torch_payload(split_root / "target_non_member.pt")
    for name, payload in (("target_member", member_payload), ("target_non_member", nonmember_payload)):
        if not isinstance(payload, dict) or "text" not in payload or "image" not in payload:
            raise ValueError(f"{name}.pt must contain dict keys 'text' and 'image'")
        if len(payload["text"]) != len(payload["image"]):
            raise ValueError(f"{name}.pt text/image lengths differ")
    return (
        [str(value) for value in member_payload["text"]],
        [image.convert("RGB") for image in member_payload["image"]],
        [str(value) for value in nonmember_payload["text"]],
        [image.convert("RGB") for image in nonmember_payload["image"]],
    )


def _pil_to_chw_float(image: Image.Image, image_size: int) -> np.ndarray:
    resized = image.convert("RGB").resize((int(image_size), int(image_size)), Image.Resampling.LANCZOS)
    array = np.asarray(resized, dtype=np.float32) / 255.0
    return np.transpose(array, (2, 0, 1)).astype(np.float32)


def _validate_strengths(values: list[float]) -> list[float]:
    strengths = [float(value) for value in values]
    if len(strengths) == 0:
        raise ValueError("--strengths must contain at least one value")
    if sorted(strengths) != strengths or len(set(strengths)) != len(strengths):
        raise ValueError("--strengths must be sorted unique values")
    if any(value <= 0.0 or value >= 1.0 for value in strengths):
        raise ValueError("--strengths values must be between 0 and 1")
    return strengths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect the frozen H2 SD/CelebA image-to-image response cache."
    )
    parser.add_argument("--download-root", type=Path, default=Path("../Download"))
    parser.add_argument("--sd15-model-dir", type=Path, default=None)
    parser.add_argument("--recon-root", type=Path, default=None)
    parser.add_argument("--split-name", default="derived-public-10")
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--packet-size", type=int, default=10)
    parser.add_argument("--sample-offset", type=int, default=0)
    parser.add_argument("--strengths", type=float, nargs="+", default=list(DEFAULT_STRENGTHS))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--num-inference-steps", type=int, default=30)
    parser.add_argument("--guidance-scale", type=float, default=7.5)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--frequency-cutoff", type=float, default=0.5)
    parser.add_argument("--no-lora", action="store_true")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run the GPU collection. Without this flag the script only writes a dry-run plan.",
    )
    return parser.parse_args()


def _build_plan(args: argparse.Namespace) -> dict[str, Any]:
    roots = default_roots(args.download_root)
    sd15_model_dir = args.sd15_model_dir or roots["sd15_model_dir"]
    recon_root = args.recon_root or roots["recon_root"]
    split_root = recon_root / args.split_name
    lora_dir = recon_root / "model-checkpoints" / "celeba_partial_target" / "checkpoint-25000"
    strengths = _validate_strengths(args.strengths)
    if args.packet_size <= 0:
        raise ValueError("--packet-size must be positive")
    if args.sample_offset < 0:
        raise ValueError("--sample-offset must be non-negative")
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    if args.image_size <= 0:
        raise ValueError("--image-size must be positive")
    sample_count = int(args.packet_size) * 2
    return {
        "status": "planned",
        "task": "H2 SD/CelebA image-to-image response cache collection",
        "mode": "dry-run" if not args.execute else "gpu-collection",
        "track": "black-box",
        "method": "H2 response-strength image-to-image",
        "inputs": {
            "sd15_model_dir": sd15_model_dir,
            "recon_root": recon_root,
            "split_name": args.split_name,
            "split_root": split_root,
            "lora_dir": None if args.no_lora else lora_dir,
            "packet_size_per_class": int(args.packet_size),
            "sample_offset_per_class": int(args.sample_offset),
            "sample_position_range_per_class": [int(args.sample_offset), int(args.sample_offset) + int(args.packet_size)],
            "strengths": strengths,
            "repeats": int(args.repeats),
            "num_inference_steps": int(args.num_inference_steps),
            "guidance_scale": float(args.guidance_scale),
            "image_size": int(args.image_size),
            "seed": int(args.seed),
            "frequency_cutoff": float(args.frequency_cutoff),
            "device": args.device,
        },
        "cache_schema": {
            "required": ["labels", "strengths", "inputs", "responses", "min_distances_rmse"],
            "optional": ["lowpass_min_distances_rmse", "member_prompts", "nonmember_prompts"],
            "shape": {
                "labels": f"[{sample_count}]",
                "strengths": f"[{len(strengths)}]",
                "inputs": f"[{sample_count}, 3, {int(args.image_size)}, {int(args.image_size)}]",
                "responses": f"[{sample_count}, {len(strengths)}, {int(args.repeats)}, 3, {int(args.image_size)}, {int(args.image_size)}]",
                "min_distances_rmse": f"[{sample_count}, {len(strengths)}]",
            },
        },
        "verdict": "dry-run ready; pass --execute only for a frozen bounded GPU packet",
    }


def _load_lora(pipe: Any, lora_dir: Path) -> str:
    weights_path = lora_dir / "pytorch_lora_weights.bin"
    state_dict = _load_torch_payload(weights_path)
    if isinstance(state_dict, dict) and any(
        str(key).startswith(("unet.", "text_encoder.")) for key in state_dict.keys()
    ):
        pipe.load_lora_weights(lora_dir)
        return "pipeline_lora_weights"
    pipe.unet.load_attn_procs(lora_dir)
    return "unet_attn_procs"


def _load_pipeline(plan: dict[str, Any]) -> Any:
    from diffusers import StableDiffusionImg2ImgPipeline

    model_dir = Path(plan["inputs"]["sd15_model_dir"])
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_dir,
        torch_dtype=torch.float16 if str(plan["inputs"]["device"]).startswith("cuda") else torch.float32,
        safety_checker=None,
        local_files_only=True,
    )
    lora_dir = plan["inputs"]["lora_dir"]
    if lora_dir is not None:
        plan["runtime"] = {"lora_load_mode": _load_lora(pipe, Path(lora_dir))}
    pipe = pipe.to(plan["inputs"]["device"])
    pipe.set_progress_bar_config(disable=True)
    return pipe


def _collect(plan: dict[str, Any]) -> dict[str, np.ndarray]:
    split_root = Path(plan["inputs"]["split_root"])
    packet_size = int(plan["inputs"]["packet_size_per_class"])
    sample_offset = int(plan["inputs"]["sample_offset_per_class"])
    image_size = int(plan["inputs"]["image_size"])
    strengths = [float(value) for value in plan["inputs"]["strengths"]]
    repeats = int(plan["inputs"]["repeats"])
    seed = int(plan["inputs"]["seed"])

    member_prompts, member_images, nonmember_prompts, nonmember_images = _load_recon_split(split_root)
    end = sample_offset + packet_size
    if len(member_images) < end or len(nonmember_images) < end:
        raise ValueError(
            f"split {split_root} has {len(member_images)} members and {len(nonmember_images)} nonmembers; "
            f"need offset {sample_offset} plus {packet_size} each"
        )
    member_slice = slice(sample_offset, end)
    nonmember_slice = slice(sample_offset, end)
    prompts = member_prompts[member_slice] + nonmember_prompts[nonmember_slice]
    images = member_images[member_slice] + nonmember_images[nonmember_slice]
    labels = np.concatenate(
        [np.ones(packet_size, dtype=np.int64), np.zeros(packet_size, dtype=np.int64)]
    )
    inputs = np.stack([_pil_to_chw_float(image, image_size) for image in images], axis=0)
    responses = np.zeros(
        (len(images), len(strengths), repeats, 3, image_size, image_size),
        dtype=np.float16,
    )
    distances = np.zeros((len(images), len(strengths), repeats), dtype=np.float32)

    pipe = _load_pipeline(plan)
    for sample_idx, (prompt, image) in enumerate(zip(prompts, images, strict=True)):
        resized = image.resize((image_size, image_size), Image.Resampling.LANCZOS)
        input_chw = inputs[sample_idx].astype(np.float32)
        for strength_idx, strength in enumerate(strengths):
            for repeat_idx in range(repeats):
                generator = torch.Generator(device=plan["inputs"]["device"])
                generator.manual_seed(seed + sample_idx * 100_000 + strength_idx * 10_000 + repeat_idx)
                output = pipe(
                    prompt=prompt,
                    image=resized,
                    strength=float(strength),
                    guidance_scale=float(plan["inputs"]["guidance_scale"]),
                    num_inference_steps=int(plan["inputs"]["num_inference_steps"]),
                    generator=generator,
                ).images[0]
                output_chw = _pil_to_chw_float(output, image_size)
                responses[sample_idx, strength_idx, repeat_idx] = output_chw.astype(np.float16)
                distances[sample_idx, strength_idx, repeat_idx] = float(
                    np.sqrt(np.mean((output_chw - input_chw) ** 2))
                )

    min_distances = distances.min(axis=2).astype(np.float32)
    lowpass_min_distances = compute_lowpass_min_distances(
        inputs.astype(np.float32),
        responses.astype(np.float32),
        cutoff=float(plan["inputs"]["frequency_cutoff"]),
    )
    return {
        "labels": labels,
        "strengths": np.asarray(strengths, dtype=np.float32),
        "inputs": inputs.astype(np.float16),
        "responses": responses.astype(np.float16),
        "distances_rmse": distances.astype(np.float32),
        "min_distances_rmse": min_distances,
        "lowpass_min_distances_rmse": lowpass_min_distances.astype(np.float32),
        "member_prompts": np.asarray(member_prompts[member_slice], dtype=str),
        "nonmember_prompts": np.asarray(nonmember_prompts[nonmember_slice], dtype=str),
        "member_source_positions": np.arange(sample_offset, end, dtype=np.int64),
        "nonmember_source_positions": np.arange(sample_offset, end, dtype=np.int64),
    }


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/black-box/runs/h2-img2img-micro-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()
    try:
        plan = _build_plan(args)
        if args.execute:
            payload = _collect(plan)
            response_cache = run_root / "response-cache.npz"
            np.savez_compressed(response_cache, **payload)
            plan["status"] = "ready"
            plan["artifact_paths"] = {
                "response_cache": response_cache.as_posix(),
                "plan": (run_root / "plan.json").as_posix(),
            }
            plan["runtime"] = {
                **plan.get("runtime", {}),
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            }
            plan["verdict"] = "response cache collected; evaluate before any promotion claim"
        else:
            plan["artifact_paths"] = {"plan": (run_root / "plan.json").as_posix()}
    except Exception as exc:
        plan = {
            "status": "blocked",
            "task": "H2 SD/CelebA image-to-image response cache collection",
            "mode": "dry-run" if not args.execute else "gpu-collection",
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    text = json.dumps(_sanitize(plan), indent=2, ensure_ascii=True)
    (run_root / "plan.json").write_text(text + "\n", encoding="utf-8")
    print(json.dumps(_sanitize(plan), indent=2, ensure_ascii=False))
    return 0 if plan["status"] in {"planned", "ready"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
