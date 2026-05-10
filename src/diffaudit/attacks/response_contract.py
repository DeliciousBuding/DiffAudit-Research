"""CPU-only checks for black-box response-contract packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


QUERY_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
RESPONSE_SUFFIXES = QUERY_SUFFIXES | {".pt", ".pth", ".npy", ".npz", ".json", ".jsonl", ".safetensors"}
SPLITS = ("member", "nonmember")
SUPPORTED_ENDPOINT_MODES = {"image_to_image", "repeated_response_api", "ddpm_unconditional"}


def _list_files(root: Path, suffixes: set[str], *, recursive: bool = False) -> list[Path]:
    if not root.is_dir():
        return []
    iterator = root.rglob("*") if recursive else root.iterdir()
    return sorted(path for path in iterator if path.is_file() and path.suffix.lower() in suffixes)


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _split_counts(root: Path, suffixes: set[str], *, recursive: bool = False) -> dict[str, int]:
    return {split: len(_list_files(root / split, suffixes, recursive=recursive)) for split in SPLITS}


def inspect_response_contract_package(
    *,
    asset_id: str,
    dataset_root: str | Path,
    supplementary_root: str | Path,
    min_split_count: int = 25,
) -> dict[str, Any]:
    """Inspect whether a candidate response-contract package is executable.

    The check is intentionally CPU-only. It validates portable package shape and
    response accounting, not model quality or membership-inference performance.
    """

    if min_split_count <= 0:
        raise ValueError("min_split_count must be positive")

    dataset = Path(dataset_root)
    supplementary = Path(supplementary_root)
    query_root = dataset / "query"
    split_root = dataset / "splits"
    response_root = supplementary / "responses"

    query_counts = _split_counts(query_root, QUERY_SUFFIXES)
    response_counts = _split_counts(response_root, RESPONSE_SUFFIXES, recursive=True)

    dataset_manifest_path = dataset / "manifest.json"
    endpoint_contract_path = supplementary / "endpoint_contract.json"
    response_manifest_path = supplementary / "response_manifest.json"
    dataset_manifest = _read_json_object(dataset_manifest_path)
    endpoint_contract = _read_json_object(endpoint_contract_path)
    response_manifest = _read_json_object(response_manifest_path)

    repeat_count = int(endpoint_contract.get("repeat_count", response_manifest.get("repeat_count", 0)) or 0)
    endpoint_mode = str(endpoint_contract.get("endpoint_mode", "")).strip()
    fixed_seed_policy = bool(endpoint_contract.get("fixed_seed_policy") or endpoint_contract.get("fixed_stochastic_policy"))
    controlled_repeats = repeat_count > 0 or fixed_seed_policy
    expected_responses = {
        split: query_counts[split] * max(repeat_count, 1)
        for split in SPLITS
    }

    checks = {
        "dataset_root": dataset.is_dir(),
        "supplementary_root": supplementary.is_dir(),
        "query_member_min_count": query_counts["member"] >= min_split_count,
        "query_nonmember_min_count": query_counts["nonmember"] >= min_split_count,
        "member_ids_json": (split_root / "member_ids.json").is_file(),
        "nonmember_ids_json": (split_root / "nonmember_ids.json").is_file(),
        "dataset_manifest": dataset_manifest_path.is_file(),
        "endpoint_contract": endpoint_contract_path.is_file(),
        "endpoint_mode_supported": endpoint_mode in SUPPORTED_ENDPOINT_MODES,
        "controlled_repeats_or_seed_policy": controlled_repeats,
        "response_manifest": response_manifest_path.is_file(),
        "response_member_count": expected_responses["member"] > 0
        and response_counts["member"] >= expected_responses["member"],
        "response_nonmember_count": expected_responses["nonmember"] > 0
        and response_counts["nonmember"] >= expected_responses["nonmember"],
    }

    missing = [name for name, ready in checks.items() if not ready]
    if not checks["dataset_root"] or not checks["supplementary_root"]:
        status = "needs_assets"
    elif not checks["query_member_min_count"] or not checks["query_nonmember_min_count"]:
        status = "needs_query_split"
    elif not checks["endpoint_contract"] or not checks["response_manifest"]:
        status = "needs_protocol"
    elif not checks["response_member_count"] or not checks["response_nonmember_count"]:
        status = "needs_responses"
    elif all(checks.values()):
        status = "ready"
    else:
        status = "blocked"

    return {
        "status": status,
        "asset_id": asset_id,
        "track": "black-box",
        "method": "response-contract-package-preflight",
        "min_split_count": min_split_count,
        "paths": {
            "dataset_root": dataset.as_posix(),
            "supplementary_root": supplementary.as_posix(),
            "query_root": query_root.as_posix(),
            "response_root": response_root.as_posix(),
            "dataset_manifest": dataset_manifest_path.as_posix(),
            "endpoint_contract": endpoint_contract_path.as_posix(),
            "response_manifest": response_manifest_path.as_posix(),
        },
        "counts": {
            "query": query_counts,
            "responses": response_counts,
            "expected_responses": expected_responses,
        },
        "contract": {
            "endpoint_mode": endpoint_mode,
            "repeat_count": repeat_count,
            "controlled_repeats_or_seed_policy": controlled_repeats,
            "response_observability": endpoint_contract.get("response_observability", ""),
            "dataset_name": dataset_manifest.get("dataset_name", dataset_manifest.get("dataset", "")),
            "model_identity": endpoint_contract.get("model_identity", endpoint_contract.get("model", "")),
        },
        "checks": checks,
        "missing": missing,
        "verdict": _verdict_for_status(status),
        "next_action": _next_action_for_status(status),
    }


def _verdict_for_status(status: str) -> str:
    if status == "ready":
        return "CPU package gate passed; eligible for a bounded scout, not admitted evidence"
    if status == "needs_assets":
        return "needs-assets; package roots are missing"
    if status == "needs_query_split":
        return "needs-assets; member/nonmember query split is incomplete"
    if status == "needs_protocol":
        return "needs-assets; endpoint or response manifest is incomplete"
    if status == "needs_responses":
        return "needs-assets; response files do not cover the fixed query budget"
    return "blocked; package exists but does not satisfy the response-contract gate"


def _next_action_for_status(status: str) -> str:
    if status == "ready":
        return "freeze scout size, scoring surface, low-FPR gate, and adaptive boundary before any execution"
    if status == "needs_query_split":
        return "add at least the minimum member/nonmember query images and split metadata"
    if status == "needs_protocol":
        return "add endpoint_contract.json and response_manifest.json with repeat or seed policy"
    if status == "needs_responses":
        return "capture or attach responses for every query under the fixed repeat policy"
    return "create the dataset and supplementary package roots under Download/black-box"
