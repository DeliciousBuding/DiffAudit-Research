"""CPU-only contract checks for H2 response-strength portability."""

from __future__ import annotations

from pathlib import Path
from typing import Any


SD15_REQUIRED_DIRS = ("unet", "vae", "text_encoder", "tokenizer", "scheduler")
CELEBA_REQUIRED_FILES = (
    "img_align_celeba.zip",
    "identity_CelebA.txt",
    "list_eval_partition.txt",
)
RECON_DERIVED_PUBLIC_SPLITS = ("derived-public-10", "derived-public-25", "derived-public-50", "derived-public-100")
H2_COMPATIBLE_ENDPOINT_MODES = ("ddpm_unconditional", "image_to_image")


def _exists(path: Path, *, kind: str) -> dict[str, Any]:
    if kind == "file":
        ready = path.is_file()
    elif kind == "dir":
        ready = path.is_dir()
    else:
        raise ValueError(f"Unsupported path kind: {kind}")
    return {"path": path.as_posix(), "kind": kind, "ready": ready}


def inspect_sd15_assets(model_dir: str | Path) -> dict[str, Any]:
    root = Path(model_dir)
    required = {name: _exists(root / name, kind="dir") for name in SD15_REQUIRED_DIRS}
    return {
        "root": root.as_posix(),
        "required": required,
        "ready": all(item["ready"] for item in required.values()) and (root / "model_index.json").is_file(),
    }


def inspect_celeba_assets(celeba_root: str | Path) -> dict[str, Any]:
    root = Path(celeba_root)
    required = {name: _exists(root / name, kind="file") for name in CELEBA_REQUIRED_FILES}
    return {
        "root": root.as_posix(),
        "required": required,
        "ready": all(item["ready"] for item in required.values()),
    }


def inspect_recon_celeba_assets(recon_root: str | Path) -> dict[str, Any]:
    root = Path(recon_root)
    split_checks: dict[str, dict[str, Any]] = {}
    for split_name in RECON_DERIVED_PUBLIC_SPLITS:
        split_root = root / split_name
        split_checks[split_name] = {
            "root": split_root.as_posix(),
            "member": _exists(split_root / "target_member.pt", kind="file"),
            "nonmember": _exists(split_root / "target_non_member.pt", kind="file"),
        }
        split_checks[split_name]["ready"] = (
            split_checks[split_name]["member"]["ready"] and split_checks[split_name]["nonmember"]["ready"]
        )
    target_lora = root / "model-checkpoints" / "celeba_partial_target" / "checkpoint-25000"
    return {
        "root": root.as_posix(),
        "derived_public_splits": split_checks,
        "target_lora": {
            "root": target_lora.as_posix(),
            "weights": _exists(target_lora / "pytorch_lora_weights.bin", kind="file"),
        },
        "ready": any(item["ready"] for item in split_checks.values())
        and (target_lora / "pytorch_lora_weights.bin").is_file(),
    }


def evaluate_h2_cross_asset_contract(
    *,
    endpoint_mode: str,
    sd15_assets: dict[str, Any],
    celeba_assets: dict[str, Any],
    recon_assets: dict[str, Any],
    controlled_repeats: bool,
    response_images_observable: bool,
) -> dict[str, Any]:
    """Return a gate verdict for H2 portability without running a model."""

    if endpoint_mode not in {"text_to_image", "image_to_image", "ddpm_unconditional"}:
        raise ValueError(f"Unsupported endpoint mode: {endpoint_mode}")
    asset_ready = bool(sd15_assets["ready"] and celeba_assets["ready"] and recon_assets["ready"])
    protocol_checks = {
        "endpoint_supports_query_image_or_unconditional_state": endpoint_mode in H2_COMPATIBLE_ENDPOINT_MODES,
        "controlled_repeats": bool(controlled_repeats),
        "response_images_observable": bool(response_images_observable),
    }
    protocol_ready = all(protocol_checks.values())
    if not asset_ready:
        status = "needs_assets"
    elif not protocol_ready:
        status = "blocked_protocol_mismatch"
    else:
        status = "eligible_cpu_contract"
    return {
        "status": status,
        "asset_ready": asset_ready,
        "protocol_ready": protocol_ready,
        "endpoint_mode": endpoint_mode,
        "assets": {
            "sd15": sd15_assets,
            "celeba": celeba_assets,
            "recon_celeba": recon_assets,
        },
        "protocol_checks": protocol_checks,
        "verdict": _verdict_for_status(status),
        "next_action": _next_action_for_status(status),
    }


def _verdict_for_status(status: str) -> str:
    if status == "eligible_cpu_contract":
        return "eligible for a bounded GPU contract, not admitted evidence"
    if status == "blocked_protocol_mismatch":
        return "negative but useful; text-to-image assets alone do not instantiate H2 response-strength"
    return "needs assets before protocol evaluation"


def _next_action_for_status(status: str) -> str:
    if status == "eligible_cpu_contract":
        return "freeze packet size, split source, query budget, and low-FPR gate before any GPU run"
    if status == "blocked_protocol_mismatch":
        return "select image-to-image or unconditional-state endpoint, or switch to CLiD/recon/variation instead of H2"
    return "complete the missing local asset bindings or use the team asset mirror"


def default_roots(download_root: str | Path) -> dict[str, Path]:
    root = Path(download_root)
    return {
        "sd15_model_dir": root / "shared" / "weights" / "stable-diffusion-v1-5",
        "celeba_root": root / "shared" / "datasets" / "celeba",
        "recon_root": root
        / "black-box"
        / "supplementary"
        / "recon-assets"
        / "ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models",
    }
