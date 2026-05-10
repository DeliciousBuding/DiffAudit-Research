"""CPU-only ReDiffuse checkpoint-portability gate review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.rediffuse import EXPECTED_CIFAR10_SPLIT_SHA256, sha256_file
from diffaudit.utils.io import torch_load_safe, write_summary_json


def _resolve(path: str | Path, *, repo_root: Path) -> Path:
    raw = Path(str(path).replace("<DIFFAUDIT_RESEARCH>", str(repo_root)))
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def _checkpoint_metadata(path: Path, *, weights_key: str) -> dict[str, Any]:
    checkpoint = torch_load_safe(path, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict):
        return {
            "path": path.as_posix(),
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else "",
            "container": type(checkpoint).__name__,
            "has_weights_key": False,
            "state_dict_key_count": 0,
            "step": None,
        }
    state = checkpoint.get(weights_key, {})
    return {
        "path": path.as_posix(),
        "exists": path.is_file(),
        "sha256": sha256_file(path) if path.is_file() else "",
        "container": "dict",
        "top_level_keys": sorted(str(key) for key in checkpoint.keys()),
        "has_weights_key": isinstance(state, dict),
        "weights_key": weights_key,
        "state_dict_key_count": len(state) if isinstance(state, dict) else 0,
        "step": int(checkpoint["step"]) if "step" in checkpoint else None,
        "has_x_T": "x_T" in checkpoint,
    }


def review_portability_gate(
    *,
    collaborator_checkpoint: Path,
    comparison_checkpoint: Path,
    split_path: Path,
    output: Path,
) -> dict[str, Any]:
    collaborator = _checkpoint_metadata(collaborator_checkpoint, weights_key="ema_model")
    comparison = _checkpoint_metadata(comparison_checkpoint, weights_key="ema_model")
    split_hash = sha256_file(split_path) if split_path.is_file() else ""
    architecture_compatible = (
        collaborator["has_weights_key"]
        and comparison["has_weights_key"]
        and collaborator["state_dict_key_count"] == comparison["state_dict_key_count"]
        and collaborator["state_dict_key_count"] > 0
    )
    split_compatible = split_hash == EXPECTED_CIFAR10_SPLIT_SHA256
    runtime_compatible = bool(architecture_compatible and split_compatible)
    release_gate = {
        "runtime_compatible": runtime_compatible,
        "split_compatible": split_compatible,
        "architecture_compatible": architecture_compatible,
        "scoring_contract_resolved": False,
        "passed": False,
    }
    result = {
        "status": "blocked",
        "track": "gray-box",
        "method": "rediffuse",
        "mode": "checkpoint-portability-gate-review",
        "verdict": "blocked-by-scoring-contract",
        "hypothesis": (
            "A ReDiffuse 800k packet is releasable only if checkpoint/runtime "
            "portability and the scorer contract are both resolved."
        ),
        "falsifier": (
            "Hold GPU if checkpoint metadata is incompatible, the split hash "
            "does not match, or the ResNet/paper-faithful scoring contract "
            "remains unresolved."
        ),
        "release_gate": release_gate,
        "output": output.as_posix(),
        "checkpoints": {
            "collaborator_750k": collaborator,
            "comparison_800k": comparison,
        },
        "split": {
            "path": split_path.as_posix(),
            "sha256": split_hash,
            "expected_sha256": EXPECTED_CIFAR10_SPLIT_SHA256,
            "matches_expected": split_compatible,
        },
        "evidence_dependencies": {
            "runtime_probe": "docs/evidence/rediffuse-800k-runtime-probe.md",
            "resnet_parity": "docs/evidence/rediffuse-resnet-parity-packet.md",
            "direct_distance_boundary": "docs/evidence/rediffuse-direct-distance-boundary-review.md",
        },
        "notes": [
            "This review is CPU-only and does not score member/nonmember samples.",
            "Runtime/checkpoint portability is necessary but not sufficient for a GPU metrics packet.",
            "The existing 750k ResNet parity packet keeps the scorer contract unresolved.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_summary_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--collaborator-checkpoint",
        default="../Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt",
    )
    parser.add_argument(
        "--comparison-checkpoint",
        default="workspaces/gray-box/assets/pia/checkpoints/cifar10_ddpm/checkpoint.pt",
    )
    parser.add_argument(
        "--split-path",
        default="../Download/shared/supplementary/collaborator-ddim-rediffuse-20260509/raw/DDIMrediffuse/CIFAR10_train_ratio0.5.npz",
    )
    parser.add_argument(
        "--output",
        default="workspaces/gray-box/runs/rediffuse-checkpoint-portability-gate-20260510-cpu/summary.json",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    result = review_portability_gate(
        collaborator_checkpoint=_resolve(args.collaborator_checkpoint, repo_root=repo_root),
        comparison_checkpoint=_resolve(args.comparison_checkpoint, repo_root=repo_root),
        split_path=_resolve(args.split_path, repo_root=repo_root),
        output=_resolve(args.output, repo_root=repo_root),
    )
    print(json.dumps({"status": result["status"], "verdict": result["verdict"], "output": result["output"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
