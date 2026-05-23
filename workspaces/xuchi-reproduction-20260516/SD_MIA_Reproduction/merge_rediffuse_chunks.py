"""
Merge ReDiffuse chunk NPZ files into one scores NPZ.

The chunk runner saves one partial NPZ per start/end batch range.  This script
validates that the chunks cover a continuous range, concatenates the saved
per-step features, and preserves the metadata needed by select_rediffuse_detector.py.
"""

import argparse
from pathlib import Path

import numpy as np


def scalar(data, key, default=None):
    if key not in data:
        return default
    value = np.asarray(data[key])
    if value.shape == ():
        return value.item()
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge saved ReDiffuse chunk NPZ files.")
    parser.add_argument("--chunk-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--pattern", default="chunk_*.npz")
    args = parser.parse_args()

    chunk_dir = Path(args.chunk_dir)
    paths = sorted(chunk_dir.glob(args.pattern))
    if not paths:
        raise SystemExit(f"no chunk files found in {chunk_dir} matching {args.pattern!r}")

    chunks = []
    for path in paths:
        data = np.load(path, allow_pickle=True)
        start = int(scalar(data, "chunk_start", -1))
        end = int(scalar(data, "chunk_end", -1))
        member = data["member_features"].astype(np.float32)
        nonmember = data["nonmember_features"].astype(np.float32)
        if start < 0 or end < 0:
            raise SystemExit(f"{path} is missing chunk_start/chunk_end metadata")
        if member.shape != nonmember.shape:
            raise SystemExit(f"{path} member/nonmember shape mismatch: {member.shape} vs {nonmember.shape}")
        if member.shape[0] != end - start:
            raise SystemExit(f"{path} has {member.shape[0]} rows but metadata says {start}:{end}")
        chunks.append((start, end, path, data, member, nonmember))

    chunks.sort(key=lambda item: item[0])
    expected = chunks[0][0]
    for start, end, path, _, _, _ in chunks:
        if start != expected:
            raise SystemExit(f"gap or overlap before {path}: expected start {expected}, got {start}")
        expected = end

    first = chunks[0][3]
    member_features = np.concatenate([item[4] for item in chunks], axis=0)
    nonmember_features = np.concatenate([item[5] for item in chunks], axis=0)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        output,
        member_features=member_features,
        nonmember_features=nonmember_features,
        steps=np.asarray(first["steps"]),
        dataset=np.asarray(scalar(first, "dataset", "laion5_blip")),
        attacker_name=np.asarray(scalar(first, "attacker_name", "ReDiffuse")),
        checkpoint=np.asarray(scalar(first, "checkpoint", "CompVis/stable-diffusion-v1-4")),
        attack_num=np.asarray(scalar(first, "attack_num", member_features.shape[1])),
        interval=np.asarray(scalar(first, "interval", 10)),
        k=np.asarray(scalar(first, "k", 10)),
        average=np.asarray(scalar(first, "average", 3)),
        score_mode=np.asarray(scalar(first, "score_mode", "first")),
        rediffuse_scorer=np.asarray(scalar(first, "rediffuse_scorer", "vae_ssim")),
        torch_dtype=np.asarray(scalar(first, "torch_dtype", "auto")),
        chunk_start=np.asarray(chunks[0][0]),
        chunk_end=np.asarray(chunks[-1][1]),
        total_batches=np.asarray(scalar(first, "total_batches", chunks[-1][1])),
        chunk_files=np.asarray([str(item[2]) for item in chunks]),
    )

    print(f"[ok] merged {len(chunks)} chunks")
    print(f"[ok] member_features={member_features.shape} nonmember_features={nonmember_features.shape}")
    print(f"[ok] coverage={chunks[0][0]}:{chunks[-1][1]}")
    print(f"[ok] wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
