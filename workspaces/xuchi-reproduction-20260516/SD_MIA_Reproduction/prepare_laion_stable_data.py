"""
Download LAION member images and prepare the COCO2017-val nonmember split.

Usage:
    python prepare_laion_stable_data.py --member-size 2500

Output:
    stable_diffusion_data/images-random/       — downloaded LAION images
    stable_diffusion_data/val-list-2500-random.npy  — [stem, caption] metadata
    coco-2500-random.yaml                      — COCO nonmember index list

Paper Appendix A:
    2500 LAION member images  +  2500 COCO nonmember images
"""

import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

DEFAULT_PARQUET_URL = (
    "https://huggingface.co/datasets/xingjianleng/laion_aesthetics_v2_6.5plus/"
    "resolve/main/part-00000.snappy.parquet"
)
USER_AGENT = "sd-mia-reproduction/1.0"


def _backup(path: Path) -> None:
    if not path.exists():
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path.rename(path.with_name(f"{path.name}.backup_{ts}"))


def _write_yaml(path: Path, indices: Iterable[int]) -> None:
    path.write_text("\n".join(f"- {i}" for i in indices) + "\n", encoding="utf-8")


def _load_coco_index(captions_json: Path) -> List[Dict]:
    data = json.loads(captions_json.read_text(encoding="utf-8"))
    images = sorted(data["images"], key=lambda x: x["id"])
    first_cap: Dict[int, str] = {}
    for ann in data["annotations"]:
        img_id = ann["image_id"]
        if img_id not in first_cap:
            first_cap[img_id] = ann["caption"]
    for img in images:
        img["caption"] = first_cap.get(img["id"], "a photo")
    return images


def _candidate_rows_from_parquet(
    parquet_path: Path, parquet_url: str, seed: int, min_side: int, timeout: int
) -> List[Dict]:
    if not parquet_path.exists():
        print(f"[info] downloading LAION metadata parquet → {parquet_path}")
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        headers = {"User-Agent": USER_AGENT}
        tmp = parquet_path.with_suffix(".tmp")
        with requests.get(parquet_url, headers=headers, timeout=timeout, stream=True) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    if chunk:
                        f.write(chunk)
        tmp.rename(parquet_path)
        print(f"[ok] parquet saved: {parquet_path}")

    import pandas as pd
    df = pd.read_parquet(parquet_path, columns=["URL", "TEXT", "WIDTH", "HEIGHT"])
    df = df.dropna(subset=["URL", "TEXT", "WIDTH", "HEIGHT"])
    df = df[(df["WIDTH"] >= min_side) & (df["HEIGHT"] >= min_side)]
    df = df.sample(frac=1, random_state=seed)
    rows = []
    for idx, row in df.iterrows():
        rows.append({"row_idx": int(idx), "URL": row["URL"], "TEXT": row["TEXT"]})
    return rows


def _download_one(row: Dict, out_dir: Path, timeout: int) -> Optional[Tuple[str, str]]:
    url = row["URL"]
    stem = f"laion_{row['row_idx']:09d}"
    out_path = out_dir / f"{stem}.jpg"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        img.save(out_path, format="JPEG", quality=95)
        caption = str(row["TEXT"]).replace("\r", " ").replace("\n", " ").strip()
        return stem, caption
    except Exception:
        if out_path.exists():
            out_path.unlink()
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare LAION member + COCO nonmember data for SD MIA (paper: 2500 each)."
    )
    parser.add_argument("--project-dir", default=".",
                        help="Path to the SD_MIA_Reproduction project root.")
    parser.add_argument("--member-size", type=int, default=2500,
                        help="Number of LAION member images (paper uses 2500).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--metadata-parquet",
                        default="stable_diffusion_data/laion_metadata.parquet",
                        help="Local cache path for the LAION metadata parquet file.")
    parser.add_argument("--metadata-url", default=DEFAULT_PARQUET_URL,
                        help="Download URL for the LAION metadata parquet (if not cached).")
    parser.add_argument("--min-side", type=int, default=256,
                        help="Discard LAION rows whose shorter side is below this (pixels).")
    parser.add_argument("--workers", type=int, default=16,
                        help="Concurrent image download threads.")
    parser.add_argument("--request-timeout", type=int, default=15)
    parser.add_argument("--image-timeout",   type=int, default=12)
    args = parser.parse_args()

    root       = Path(args.project_dir).resolve()
    sd_dir     = root / "stable_diffusion_data"
    member_dir = sd_dir / "images-random"
    member_npy = sd_dir / "val-list-2500-random.npy"
    yaml_path  = root / "coco-2500-random.yaml"
    parquet    = Path(args.metadata_parquet)
    if not parquet.is_absolute():
        parquet = root / parquet

    if not sd_dir.exists():
        raise FileNotFoundError(f"Missing: {sd_dir}  (create it first)")

    # 1. Fetch LAION metadata & download images
    print(f"[info] reading LAION metadata from: {parquet}")
    rows = _candidate_rows_from_parquet(parquet, args.metadata_url, args.seed,
                                        args.min_side, args.request_timeout)
    print(f"[info] {len(rows)} candidate rows after size filter")
    if len(rows) < args.member_size:
        raise RuntimeError(f"Only {len(rows)} rows available, need {args.member_size}.")

    tmp_dir = sd_dir / f"images-random.tmp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    tmp_npy = sd_dir / "val-list-2500-random.tmp.npy"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    metadata: List[List[str]] = []
    batch_size = max(args.workers * 4, 16)
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for start in range(0, len(rows), batch_size):
            if len(metadata) >= args.member_size:
                break
            batch   = rows[start: start + batch_size]
            futures = [pool.submit(_download_one, r, tmp_dir, args.image_timeout) for r in batch]
            for fut in as_completed(futures):
                res = fut.result()
                if res is not None:
                    metadata.append(list(res))
                    if len(metadata) % 100 == 0:
                        print(f"[info] downloaded {len(metadata)}/{args.member_size}")
                if len(metadata) >= args.member_size:
                    for f in futures:
                        f.cancel()
                    break

    if len(metadata) < args.member_size:
        raise RuntimeError(f"Only {len(metadata)} images downloaded; need {args.member_size}.")

    # remove stray files from in-flight workers
    keep = {row[0] for row in metadata[: args.member_size]}
    for p in tmp_dir.glob("*.jpg"):
        if p.stem not in keep:
            p.unlink()

    arr = np.array(metadata[: args.member_size], dtype=object)
    np.save(tmp_npy, arr)

    _backup(member_dir)
    _backup(member_npy)
    tmp_dir.rename(member_dir)
    tmp_npy.rename(member_npy)
    print(f"[ok] {args.member_size} LAION member images → {member_dir}")

    # 2. Prepare COCO nonmember split
    coco_caps = root / "coco_data" / "annotations" / "captions_val2017.json"
    coco_imgs = root / "coco_data" / "val2017"
    if not coco_imgs.exists() or not coco_caps.exists():
        raise FileNotFoundError(
            "COCO2017-val not found. Download from https://cocodataset.org/ and place at:\n"
            f"  {coco_imgs}\n  {coco_caps}"
        )
    images = _load_coco_index(coco_caps)
    if args.member_size > len(images):
        raise ValueError(f"Need {args.member_size} COCO images but only {len(images)} available.")

    rng = random.Random(args.seed + 1009)
    indices = list(range(len(images)))
    rng.shuffle(indices)
    _backup(yaml_path)
    _write_yaml(yaml_path, sorted(indices[: args.member_size]))
    print(f"[ok] {args.member_size} COCO nonmember indices → {yaml_path}")

    elapsed = time.time() - t0
    print(f"\n[done] data preparation complete in {elapsed:.0f}s")
    print(f"  member_dir   = {member_dir}")
    print(f"  member_npy   = {member_npy}")
    print(f"  nonmember    = {yaml_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
