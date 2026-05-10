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


def _read_json_object(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.is_file():
        return {}, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON in {path.as_posix()}: {exc.msg}"
    if not isinstance(payload, dict):
        return {}, f"expected JSON object in {path.as_posix()}"
    return payload, None


def _split_counts(root: Path, suffixes: set[str], *, recursive: bool = False) -> dict[str, int]:
    return {split: len(_list_files(root / split, suffixes, recursive=recursive)) for split in SPLITS}


def _parse_repeat_count(*values: Any) -> tuple[int, bool]:
    for value in values:
        if value is None or value == "":
            continue
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0, False
        return parsed, parsed > 0
    return 0, False


def _response_coverage(
    *,
    query_files: list[Path],
    response_files: list[Path],
    split: str,
    repeat_count: int,
    response_manifest: dict[str, Any],
) -> dict[str, Any]:
    if repeat_count <= 0:
        return {"ready": False, "covered_queries": 0, "missing_queries": [path.name for path in query_files]}

    manifest_mapping = response_manifest.get("responses_by_query", {})
    if isinstance(manifest_mapping, dict) and isinstance(manifest_mapping.get(split), dict):
        split_mapping = manifest_mapping[split]
        missing = [
            query.name
            for query in query_files
            if len(split_mapping.get(query.name, split_mapping.get(query.stem, []))) < repeat_count
        ]
        return {
            "ready": not missing and bool(query_files),
            "covered_queries": len(query_files) - len(missing),
            "missing_queries": missing,
            "source": "response_manifest.responses_by_query",
        }

    response_stems = [path.stem for path in response_files]
    missing = [
        query.name
        for query in query_files
        if sum(stem == query.stem or stem.startswith(f"{query.stem}-") for stem in response_stems) < repeat_count
    ]
    return {
        "ready": not missing and bool(query_files),
        "covered_queries": len(query_files) - len(missing),
        "missing_queries": missing,
        "source": "filename-prefix",
    }


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

    query_files = {split: _list_files(query_root / split, QUERY_SUFFIXES) for split in SPLITS}
    response_files = {split: _list_files(response_root / split, RESPONSE_SUFFIXES, recursive=True) for split in SPLITS}
    query_counts = {split: len(query_files[split]) for split in SPLITS}
    response_counts = {split: len(response_files[split]) for split in SPLITS}

    dataset_manifest_path = dataset / "manifest.json"
    endpoint_contract_path = supplementary / "endpoint_contract.json"
    response_manifest_path = supplementary / "response_manifest.json"
    dataset_manifest, dataset_manifest_error = _read_json_object(dataset_manifest_path)
    endpoint_contract, endpoint_contract_error = _read_json_object(endpoint_contract_path)
    response_manifest, response_manifest_error = _read_json_object(response_manifest_path)

    repeat_count, parsed_repeat_count_valid = _parse_repeat_count(
        endpoint_contract.get("repeat_count"),
        response_manifest.get("repeat_count"),
    )
    endpoint_mode = str(endpoint_contract.get("endpoint_mode", "")).strip()
    fixed_seed_policy = bool(endpoint_contract.get("fixed_seed_policy") or endpoint_contract.get("fixed_stochastic_policy"))
    repeat_count_valid = parsed_repeat_count_valid or fixed_seed_policy
    controlled_repeats = repeat_count > 0 or fixed_seed_policy
    expected_responses = {
        split: query_counts[split] * max(repeat_count, 1)
        for split in SPLITS
    }
    response_coverage = {
        split: _response_coverage(
            query_files=query_files[split],
            response_files=response_files[split],
            split=split,
            repeat_count=max(repeat_count, 1),
            response_manifest=response_manifest,
        )
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
        "dataset_manifest_json_valid": dataset_manifest_error is None,
        "endpoint_contract": endpoint_contract_path.is_file(),
        "endpoint_contract_json_valid": endpoint_contract_error is None,
        "endpoint_mode_supported": endpoint_mode in SUPPORTED_ENDPOINT_MODES,
        "repeat_count_valid": repeat_count_valid,
        "controlled_repeats_or_seed_policy": controlled_repeats,
        "response_manifest": response_manifest_path.is_file(),
        "response_manifest_json_valid": response_manifest_error is None,
        "response_member_count": expected_responses["member"] > 0
        and response_counts["member"] >= expected_responses["member"]
        and bool(response_coverage["member"]["ready"]),
        "response_nonmember_count": expected_responses["nonmember"] > 0
        and response_counts["nonmember"] >= expected_responses["nonmember"]
        and bool(response_coverage["nonmember"]["ready"]),
    }

    missing = [name for name, ready in checks.items() if not ready]
    if not checks["dataset_root"] or not checks["supplementary_root"]:
        status = "needs_assets"
    elif not checks["query_member_min_count"] or not checks["query_nonmember_min_count"]:
        status = "needs_query_split"
    elif not checks["dataset_manifest_json_valid"] or not checks["endpoint_contract_json_valid"] or not checks["response_manifest_json_valid"]:
        status = "blocked"
    elif not checks["endpoint_contract"] or not checks["response_manifest"]:
        status = "needs_protocol"
    elif (
        not checks["endpoint_mode_supported"]
        or not checks["repeat_count_valid"]
        or not checks["controlled_repeats_or_seed_policy"]
    ):
        status = "blocked"
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
            "response_coverage": response_coverage,
        },
        "parse_errors": {
            "dataset_manifest": dataset_manifest_error,
            "endpoint_contract": endpoint_contract_error,
            "response_manifest": response_manifest_error,
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
    if status == "needs_assets":
        return "create the dataset and supplementary package roots under Download/black-box"
    return "review the missing list and satisfy the response-contract gate requirements"
