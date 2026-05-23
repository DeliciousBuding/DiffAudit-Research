"""
Generate BLIP captions for the laion5_blip experiment route.

Paper Section 5.4:
  "Not knowing the ground truth text and generating text through BLIP (Li et al., 2022),
   which we denote as Laion5 with BLIP."

Outputs:
  stable_diffusion_data/text_generation/images-random.csv  — member captions
  stable_diffusion_data/text_generation/val2017.csv        — nonmember captions
"""

import argparse
import csv
import json
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
from PIL import Image, ImageFile
from transformers import BlipForConditionalGeneration, BlipProcessor
from transformers import logging as hf_logging

ImageFile.LOAD_TRUNCATED_IMAGES = True
hf_logging.set_verbosity_error()
warnings.filterwarnings("ignore", message="The channel dimension is ambiguous.*")


def _read_csv(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "text" not in reader.fieldnames or "file_name" not in reader.fieldnames:
            return {}
        return {row["file_name"]: row["text"] for row in reader if row.get("file_name") and row.get("text")}


def _write_csv(path: Path, rows: Sequence[Tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "file_name"])
        writer.writeheader()
        for file_name, text in rows:
            writer.writerow({"text": text, "file_name": file_name})


def _parse_coco_yaml(path: Path) -> List[int]:
    values: List[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("-"):
            values.append(int(line[1:].strip()))
    return values


def _member_items(project_dir: Path) -> List[Tuple[str, Path]]:
    meta = np.load(project_dir / "stable_diffusion_data" / "val-list-2500-random.npy", allow_pickle=True)
    img_dir = project_dir / "stable_diffusion_data" / "images-random"
    return [(f"{row[0]}.jpg", img_dir / f"{row[0]}.jpg") for row in meta]


def _nonmember_items(project_dir: Path) -> List[Tuple[str, Path]]:
    caps_json = project_dir / "coco_data" / "annotations" / "captions_val2017.json"
    yaml_path = project_dir / "coco-2500-random.yaml"
    img_dir   = project_dir / "coco_data" / "val2017"
    images    = sorted(json.loads(caps_json.read_text())["images"], key=lambda x: int(x["id"]))
    return [(images[i]["file_name"], img_dir / images[i]["file_name"]) for i in _parse_coco_yaml(yaml_path)]


def _batched(items: Sequence, size: int) -> Iterable:
    for s in range(0, len(items), size):
        yield items[s: s + size]


def _caption_batch(
    items: Sequence[Tuple[str, Path]],
    existing: Dict[str, str],
    processor: BlipProcessor,
    model: BlipForConditionalGeneration,
    device: str,
    batch_size: int,
    max_new_tokens: int,
) -> Dict[str, str]:
    missing = [(n, p) for n, p in items if n not in existing]
    if not missing:
        return {}
    generated: Dict[str, str] = {}
    done = 0
    for batch in _batched(missing, batch_size):
        imgs   = [Image.open(p).convert("RGB") for _, p in batch]
        names  = [n for n, _ in batch]
        inputs = processor(images=imgs, return_tensors="pt").to(device)
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=max_new_tokens)
        for name, cap in zip(names, processor.batch_decode(out, skip_special_tokens=True)):
            generated[name] = cap.strip()
        done += len(batch)
        print(f"[caption] {done}/{len(missing)}")
    return generated


def _run(label, items, out_csv, processor, model, device, batch_size, max_new_tokens, reuse):
    existing = _read_csv(out_csv) if reuse else {}
    existing = {n: t for n, t in existing.items() if any(item[0] == n for item in items)}
    print(f"[caption] {label}: total={len(items)}, reusable={len(existing)}")
    generated = _caption_batch(items, existing, processor, model, device, batch_size, max_new_tokens)
    all_text   = {**existing, **generated}
    rows       = [(n, all_text[n]) for n, _ in items]
    _write_csv(out_csv, rows)
    print(f"[ok] wrote {len(rows)} captions → {out_csv}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate BLIP captions for laion5_blip route."
    )
    parser.add_argument("--project-dir",  default=".")
    parser.add_argument("--output-dir",   default="stable_diffusion_data/text_generation")
    parser.add_argument("--model",        default="Salesforce/blip-image-captioning-base")
    parser.add_argument("--device",       default="auto")
    parser.add_argument("--batch-size",   type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=30)
    parser.add_argument("--member-only",  action="store_true")
    parser.add_argument("--nonmember-only", action="store_true")
    parser.add_argument("--no-reuse-existing", action="store_true")
    args = parser.parse_args()

    if args.member_only and args.nonmember_only:
        raise ValueError("Use at most one of --member-only / --nonmember-only.")

    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    print(f"[caption] loading {args.model} on {device}")
    processor = BlipProcessor.from_pretrained(args.model)
    blip      = BlipForConditionalGeneration.from_pretrained(args.model, use_safetensors=True).to(device)
    blip.eval()

    root    = Path(args.project_dir).resolve()
    out_dir = Path(args.output_dir) if Path(args.output_dir).is_absolute() else root / args.output_dir
    reuse   = not args.no_reuse_existing

    if not args.nonmember_only:
        _run("LAION members", _member_items(root),
             out_dir / "images-random.csv", processor, blip, device,
             args.batch_size, args.max_new_tokens, reuse)

    if not args.member_only:
        _run("COCO nonmembers", _nonmember_items(root),
             out_dir / "val2017.csv", processor, blip, device,
             args.batch_size, args.max_new_tokens, reuse)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
