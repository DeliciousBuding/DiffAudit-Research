from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
from transformers import AutoProcessor, CLIPModel

from diffaudit.attacks.response_seed_stability import mean_pairwise_cosine, summarize_stability_scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded CommonCanvas multi-seed response-stability scout.")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--supplementary-root", type=Path, required=True)
    parser.add_argument("--clip-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--responses-subdir", default="stability_responses_20260513")
    parser.add_argument("--samples-per-split", type=int, default=12)
    parser.add_argument("--seeds", default="20260613,20260614,20260615")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--guidance-scale", type=float, default=7.5)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--checkpoint", type=Path, default=None)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_caption(row: dict[str, Any]) -> str:
    captions = row.get("source_caption", [])
    if isinstance(captions, list) and captions:
        return str(captions[0])
    if isinstance(captions, str):
        return captions
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
    pipe.to(device)
    pipe.set_progress_bar_config(disable=True)
    return pipe


def _generate_responses(
    *,
    pipe: StableDiffusionXLPipeline,
    device: torch.device,
    rows: list[dict[str, Any]],
    seeds: list[int],
    output_root: Path,
    width: int,
    height: int,
    steps: int,
    guidance_scale: float,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for row in rows:
        split_dir = output_root / row["split"]
        split_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(row["id"]).stem
        for seed in seeds:
            path = split_dir / f"{stem}-seed{seed}-w{width}-h{height}-steps{steps}.png"
            if path.is_file():
                continue
            generator = torch.Generator(device=device.type).manual_seed(seed)
            started_at = time.time()
            image = pipe(
                prompt=row["prompt"],
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator,
            ).images[0]
            image.save(path)
            elapsed = time.time() - started_at
            print(f"generated {row['split']} {row['id']} seed={seed} seconds={elapsed:.2f}", flush=True)


class ClipImageEmbedder:
    def __init__(self, clip_dir: Path, device: torch.device) -> None:
        self.device = device
        self.dtype = torch.float16 if device.type == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(clip_dir, local_files_only=True)
        self.model = CLIPModel.from_pretrained(clip_dir, torch_dtype=self.dtype, local_files_only=True).to(device)
        self.model.eval()

    def image_embedding(self, path: Path) -> np.ndarray:
        image = Image.open(path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad(), torch.autocast(
            device_type=self.device.type,
            dtype=self.dtype,
            enabled=self.device.type == "cuda",
        ):
            vision_outputs = self.model.vision_model(pixel_values=inputs["pixel_values"])
            features = self.model.visual_projection(vision_outputs.pooler_output)
        features = features / features.norm(dim=-1, keepdim=True)
        return features[0].detach().float().cpu().numpy()


def _score_rows(
    *,
    rows: list[dict[str, Any]],
    seeds: list[int],
    response_root: Path,
    supplementary_root: Path,
    width: int,
    height: int,
    steps: int,
    embedder: ClipImageEmbedder,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        stem = Path(row["id"]).stem
        image_paths = [
            response_root / row["split"] / f"{stem}-seed{seed}-w{width}-h{height}-steps{steps}.png"
            for seed in seeds
        ]
        missing = [path for path in image_paths if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"missing generated response(s): {[path.as_posix() for path in missing]}")
        embeddings = np.asarray([embedder.image_embedding(path) for path in image_paths], dtype=float)
        pairwise = []
        for left in range(embeddings.shape[0]):
            for right in range(left + 1, embeddings.shape[0]):
                pairwise.append(mean_pairwise_cosine(embeddings[[left, right], :]))
        score = mean_pairwise_cosine(embeddings)
        records.append(
            {
                **row,
                "response_paths": [
                    path.relative_to(supplementary_root).as_posix()
                    for path in image_paths
                ],
                "pairwise_cosines": [round(float(value), 6) for value in pairwise],
                "score": float(score),
            }
        )
    return records


def main() -> None:
    args = parse_args()
    if args.samples_per_split <= 0:
        raise ValueError("--samples-per-split must be positive")
    seeds = [int(value.strip()) for value in args.seeds.split(",") if value.strip()]
    if len(seeds) < 2:
        raise ValueError("at least two seeds are required")

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")
    dataset_manifest = _load_json(args.dataset_root / "manifest.json")
    response_manifest = _load_json(args.supplementary_root / "response_manifest.json")
    checkpoint = _resolve_checkpoint(args, response_manifest)
    rows = _selected_rows(dataset_manifest, args.samples_per_split)
    response_root = args.supplementary_root / args.responses_subdir

    pipe = _load_pipeline(checkpoint, device)
    _generate_responses(
        pipe=pipe,
        device=device,
        rows=rows,
        seeds=seeds,
        output_root=response_root,
        width=args.width,
        height=args.height,
        steps=args.steps,
        guidance_scale=args.guidance_scale,
    )
    del pipe
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()

    embedder = ClipImageEmbedder(args.clip_dir, device)
    records = _score_rows(
        rows=rows,
        seeds=seeds,
        response_root=response_root,
        supplementary_root=args.supplementary_root,
        width=args.width,
        height=args.height,
        steps=args.steps,
        embedder=embedder,
    )
    labels = np.asarray([record["label"] for record in records], dtype=int)
    scores = np.asarray([record["score"] for record in records], dtype=float)
    metrics = summarize_stability_scores(labels, scores)
    verdict = (
        "positive_scout"
        if float(metrics["auc"]) >= 0.7 and float(metrics["tpr_at_1pct_fpr"]) > 0.0
        else "negative_or_weak"
    )
    payload = {
        "asset_id": dataset_manifest.get("asset_id", "response-contract-copymark-commoncanvas-20260512"),
        "model_identity": response_manifest.get("model_identity", "common-canvas/CommonCanvas-XL-C"),
        "endpoint_mode": response_manifest.get("endpoint_mode", "text_to_image"),
        "hypothesis": (
            "If training membership makes CommonCanvas outputs collapse to a more memorized response distribution, "
            "member prompts should show higher cross-seed image-embedding stability than nonmember prompts."
        ),
        "boundary": (
            "single bounded 12/12 by default multi-seed response-distribution scout; not a query-response, "
            "pixel, or prompt-adherence metric matrix"
        ),
        "generation": {
            "samples_per_split": args.samples_per_split,
            "seeds": seeds,
            "width": args.width,
            "height": args.height,
            "num_inference_steps": args.steps,
            "guidance_scale": args.guidance_scale,
            "response_subdir": args.responses_subdir,
            "checkpoint_name": checkpoint.name,
            "checkpoint_bytes": checkpoint.stat().st_size if checkpoint.is_file() else None,
            "device": str(device),
            "torch": torch.__version__,
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "metric": metrics,
        "verdict": verdict,
        "stop_condition": (
            "If the small packet is negative_or_weak, close this stability mechanism and do not expand "
            "seed, subset, or embedding-metric sweeps."
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("asset_id", "metric", "verdict")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
