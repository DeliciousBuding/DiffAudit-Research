"""
Concatenate feature arrays from multiple ReDiffuse score NPZ files.

This is for offline detector fusion only. It requires all input NPZ files to
use the same sample order and the same member/nonmember count.
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
    return value.tolist()


def main() -> int:
    parser = argparse.ArgumentParser(description="Concatenate ReDiffuse feature NPZ files.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--names", nargs="*", default=[])
    args = parser.parse_args()

    inputs = [Path(path) for path in args.inputs]
    names = args.names or [path.stem for path in inputs]
    if len(names) != len(inputs):
        raise SystemExit("--names must have the same length as --inputs")

    member_parts = []
    nonmember_parts = []
    feature_names = []
    first = None
    expected_shape0 = None

    for name, path in zip(names, inputs):
        data = np.load(path, allow_pickle=True)
        if first is None:
            first = data
        member = data["member_features"].astype(np.float32)
        nonmember = data["nonmember_features"].astype(np.float32)
        if member.shape != nonmember.shape:
            raise SystemExit(f"{path} member/nonmember shape mismatch: {member.shape} vs {nonmember.shape}")
        if expected_shape0 is None:
            expected_shape0 = member.shape[0]
        elif member.shape[0] != expected_shape0:
            raise SystemExit(f"{path} sample count mismatch: expected {expected_shape0}, got {member.shape[0]}")
        member_parts.append(member)
        nonmember_parts.append(nonmember)
        feature_names.extend(f"{name}_step{idx}" for idx in range(member.shape[1]))

    member_features = np.concatenate(member_parts, axis=1)
    nonmember_features = np.concatenate(nonmember_parts, axis=1)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        output,
        member_features=member_features,
        nonmember_features=nonmember_features,
        feature_names=np.asarray(feature_names),
        dataset=np.asarray(scalar(first, "dataset", "laion5_blip")),
        attacker_name=np.asarray("ReDiffuse"),
        checkpoint=np.asarray(scalar(first, "checkpoint", "CompVis/stable-diffusion-v1-4")),
        score_mode=np.asarray("combined_features"),
        rediffuse_scorer=np.asarray("combined"),
        torch_dtype=np.asarray(scalar(first, "torch_dtype", "auto")),
        source_files=np.asarray([str(path) for path in inputs]),
    )

    print(f"[ok] combined {len(inputs)} files")
    print(f"[ok] member_features={member_features.shape} nonmember_features={nonmember_features.shape}")
    print(f"[ok] wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
