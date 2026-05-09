"""Asset probes for the collaborator-provided ReDiffuse DDIM bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.utils.io import torch_load_safe


EXPECTED_CIFAR10_SPLIT_SHA256 = "aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0"
DEFAULT_BUNDLE_RELATIVE = Path("Download/shared/supplementary/collaborator-ddim-rediffuse-20260509/raw/DDIMrediffuse")
DEFAULT_CHECKPOINT_RELATIVE = Path("Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt")
REQUIRED_BUNDLE_FILES = (
    "attack.py",
    "components.py",
    "model_unet.py",
    "dataset_utils.py",
    "resnet.py",
    "diffusion.py",
    "CIFAR10_train_ratio0.5.npz",
)


def diffaudit_root() -> Path:
    """Return the workspace root that owns Research/ and Download/."""
    return Path(__file__).resolve().parents[4]


def default_bundle_root() -> Path:
    return diffaudit_root() / DEFAULT_BUNDLE_RELATIVE


def default_checkpoint_path() -> Path:
    return diffaudit_root() / DEFAULT_CHECKPOINT_RELATIVE


def default_dataset_root() -> Path:
    return diffaudit_root() / "Download/gray-box/supplementary/pia-upstream-assets/contents/datasets/cifar10"


def sha256_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _split_summary(split_path: Path) -> dict[str, Any]:
    if not split_path.exists():
        return {
            "exists": False,
            "path": str(split_path),
        }
    payload = np.load(split_path, allow_pickle=False)
    arrays = {
        name: {
            "shape": list(payload[name].shape),
            "dtype": str(payload[name].dtype),
            "first10": payload[name].reshape(-1)[:10].astype(int).tolist()
            if payload[name].size and np.issubdtype(payload[name].dtype, np.integer)
            else payload[name].reshape(-1)[:10].tolist(),
        }
        for name in payload.files
    }
    digest = sha256_file(split_path)
    return {
        "exists": True,
        "path": str(split_path),
        "sha256": digest,
        "hash_matches_pia_split": digest == EXPECTED_CIFAR10_SPLIT_SHA256,
        "arrays": arrays,
    }


def _checkpoint_summary(checkpoint_path: Path) -> dict[str, Any]:
    if not checkpoint_path.exists():
        return {
            "exists": False,
            "path": str(checkpoint_path),
        }
    checkpoint = torch_load_safe(checkpoint_path, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict):
        return {
            "exists": True,
            "path": str(checkpoint_path),
            "sha256": sha256_file(checkpoint_path),
            "container": type(checkpoint).__name__,
        }
    return {
        "exists": True,
        "path": str(checkpoint_path),
        "sha256": sha256_file(checkpoint_path),
        "container": "dict",
        "top_level_keys": list(checkpoint.keys()),
        "step": int(checkpoint["step"]) if "step" in checkpoint else None,
        "x_T_shape": list(checkpoint["x_T"].shape) if "x_T" in checkpoint else None,
        "has_ema_model": "ema_model" in checkpoint,
        "has_net_model": "net_model" in checkpoint,
        "ema_model_state_dict_keys": len(checkpoint["ema_model"]) if isinstance(checkpoint.get("ema_model"), dict) else None,
    }


def probe_rediffuse_assets(
    bundle_root: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    dataset_root: str | Path | None = None,
) -> dict[str, Any]:
    bundle_path = Path(bundle_root) if bundle_root else default_bundle_root()
    checkpoint = Path(checkpoint_path) if checkpoint_path else default_checkpoint_path()
    dataset = Path(dataset_root) if dataset_root else default_dataset_root()

    file_checks = {
        relative: (bundle_path / relative).exists()
        for relative in REQUIRED_BUNDLE_FILES
    }
    split = _split_summary(bundle_path / "CIFAR10_train_ratio0.5.npz")
    checkpoint_info = _checkpoint_summary(checkpoint)
    checks = {
        "bundle_root": bundle_path.exists(),
        "required_files": all(file_checks.values()),
        "split_hash": bool(split.get("hash_matches_pia_split")),
        "checkpoint": bool(checkpoint_info.get("exists")),
        "checkpoint_has_ema_model": bool(checkpoint_info.get("has_ema_model")),
        "dataset_root": dataset.exists(),
    }
    missing = []
    if not checks["bundle_root"]:
        missing.append(str(bundle_path))
    missing.extend(str(bundle_path / rel) for rel, ready in file_checks.items() if not ready)
    if not checks["checkpoint"]:
        missing.append(str(checkpoint))
    if not checks["dataset_root"]:
        missing.append(str(dataset))
    status = "ready" if all(checks.values()) else "blocked"
    return {
        "status": status,
        "track": "gray-box",
        "method": "rediffuse",
        "mode": "asset-probe",
        "checks": checks,
        "paths": {
            "bundle_root": str(bundle_path),
            "checkpoint": str(checkpoint),
            "dataset_root": str(dataset),
            "split": str(bundle_path / "CIFAR10_train_ratio0.5.npz"),
        },
        "required_files": file_checks,
        "split": split,
        "checkpoint": checkpoint_info,
        "missing": missing,
        "missing_items": [Path(item).name for item in missing],
        "provenance": {
            "source": "collaborator-manual-transfer",
            "seed": 42,
            "seed_evidence": "collaborator-statement",
            "training_script_caveat": "train1.py defaults to total_steps=200000 while the checkpoint stores step=750000",
        },
    }


def explain_rediffuse_assets(
    bundle_root: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    dataset_root: str | Path | None = None,
) -> dict[str, Any]:
    return probe_rediffuse_assets(
        bundle_root=bundle_root,
        checkpoint_path=checkpoint_path,
        dataset_root=dataset_root,
    )


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
