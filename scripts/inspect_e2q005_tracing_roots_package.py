"""Inspect the E2Q-005 Tracing the Roots public supplement package.

This script is intentionally narrow. It checks the OpenReview supplementary ZIP
identity, the four released CIFAR10 feature tensors, and the existing local
replay JSON. It does not train, run inference, download data, or touch GPU.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any


EXPECTED_ZIP_SIZE = 45_499_156
EXPECTED_ZIP_SHA256 = "62e9ae3833bcc0f102612d05898262eea2b6025fe8949a72c3f055a8534c7b41"

TENSOR_ENTRIES = {
    "train/member": "data/cifar10/train/member.pt",
    "train/external": "data/cifar10/train/external.pt",
    "eval/member": "data/cifar10/eval/member.pt",
    "eval/external": "data/cifar10/eval/external.pt",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_replay(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def inspect_zip(zip_path: Path, replay: dict[str, Any] | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "candidate": "E2Q-005 Tracing the Roots",
        "source_url": "https://openreview.net/attachment?id=mE74JKHTCE&name=supplementary_material",
        "zip_path": str(zip_path),
        "zip_size": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "expected_zip_size": EXPECTED_ZIP_SIZE,
        "expected_zip_sha256": EXPECTED_ZIP_SHA256,
        "zip_identity_match": False,
        "entry_count": 0,
        "entries": [],
        "tensor_entries": {},
        "replay_json_match": None,
        "adjudication_readiness": "no_go_n50",
        "allowed_scope": "single-row feature-packet package-work only",
    }
    result["zip_identity_match"] = (
        result["zip_size"] == EXPECTED_ZIP_SIZE
        and result["zip_sha256"] == EXPECTED_ZIP_SHA256
    )

    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        result["entry_count"] = len(infos)
        for info in infos:
            result["entries"].append(
                {
                    "filename": info.filename,
                    "file_size": info.file_size,
                    "compress_size": info.compress_size,
                    "crc": f"{info.CRC:08x}",
                }
            )

        for label, filename in TENSOR_ENTRIES.items():
            with archive.open(filename) as handle:
                data = handle.read()
            tensor_info: dict[str, Any] = {
                "filename": filename,
                "file_size": len(data),
                "sha256": sha256_bytes(data),
            }
            if replay is not None:
                expected = replay.get("tensor_summary", {}).get(label, {})
                tensor_info["replay_sha256"] = expected.get("sha256")
                tensor_info["hash_matches_replay"] = (
                    tensor_info["sha256"] == expected.get("sha256")
                )
                tensor_info["replay_raw_shape"] = expected.get("raw_shape")
                tensor_info["replay_selected_shape"] = expected.get("selected_shape")
                tensor_info["replay_dtype"] = expected.get("dtype")
            result["tensor_entries"][label] = tensor_info

    if replay is not None:
        result["replay_metrics"] = {
            "auc": replay.get("eval", {}).get("auc"),
            "accuracy": replay.get("eval", {}).get("accuracy"),
            "tpr_at_1pct_fpr": replay.get("eval", {}).get("tpr_at_1pct_fpr"),
            "tpr_at_0_1pct_fpr": replay.get("eval", {}).get("tpr_at_0_1pct_fpr"),
            "train_samples": replay.get("train", {}).get("n_samples"),
            "eval_samples": replay.get("eval", {}).get("n_samples"),
            "features": replay.get("train", {}).get("n_features"),
        }
        result["replay_json_match"] = all(
            info.get("hash_matches_replay") for info in result["tensor_entries"].values()
        )

    return result


def maybe_add_torch_shapes(result: dict[str, Any], zip_path: Path) -> None:
    try:
        import torch  # type: ignore
    except Exception as exc:  # pragma: no cover - environment-dependent
        result["torch_shape_check"] = {"available": False, "error": repr(exc)}
        return

    shape_result: dict[str, Any] = {
        "available": True,
        "torch_version": getattr(torch, "__version__", "unknown"),
        "tensors": {},
    }
    with zipfile.ZipFile(zip_path) as archive:
        for label, filename in TENSOR_ENTRIES.items():
            data = archive.read(filename)
            try:
                tensor = torch.load(io.BytesIO(data), map_location="cpu", weights_only=False)
            except TypeError:
                tensor = torch.load(io.BytesIO(data), map_location="cpu")
            shape_result["tensors"][label] = {
                "type": type(tensor).__name__,
                "shape": list(tensor.shape) if hasattr(tensor, "shape") else None,
                "dtype": str(tensor.dtype) if hasattr(tensor, "dtype") else None,
                "numel": int(tensor.numel()) if hasattr(tensor, "numel") else None,
                "has_nan": (
                    bool(torch.isnan(tensor).any().item())
                    if hasattr(tensor, "dtype") and tensor.dtype.is_floating_point
                    else None
                ),
            }
    result["torch_shape_check"] = shape_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path, help="OpenReview supplement ZIP path.")
    parser.add_argument("--replay-json", type=Path, help="Existing local replay JSON.")
    parser.add_argument("--output", required=True, type=Path, help="JSON output path.")
    parser.add_argument(
        "--torch-shapes",
        action="store_true",
        help="Load tensors with torch on CPU and record dtype/shape checks.",
    )
    args = parser.parse_args()

    replay = load_replay(args.replay_json) if args.replay_json else None
    result = inspect_zip(args.zip, replay)
    if args.torch_shapes:
        maybe_add_torch_shapes(result, args.zip)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    if not result["zip_identity_match"]:
        raise SystemExit("ZIP identity does not match expected size/SHA256")
    if result.get("replay_json_match") is False:
        raise SystemExit("Tensor hashes do not match replay JSON")


if __name__ == "__main__":
    main()
