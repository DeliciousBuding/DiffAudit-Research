"""Contract checks for local CLiD bridge preflight runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_CONFIG_KEYS = ("run_id", "track", "method", "status", "mode", "assets", "export")
REQUIRED_METADATA_KEYS = ("file_name", "text")
REQUIRED_SCRIPT_MARKERS = ("load_attn_procs", "imagefolder", "clid_clip")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _read_metadata(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        row = json.loads(raw_line)
        if not isinstance(row, dict):
            raise ValueError(f"Expected metadata object row at {path}")
        rows.append(row)
    return rows


def _relative_or_token(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _metadata_check(dataset_dir: Path, expected_count: int) -> dict[str, Any]:
    metadata_path = dataset_dir / "metadata.jsonl"
    rows = _read_metadata(metadata_path) if metadata_path.is_file() else []
    image_files = sorted(path for path in dataset_dir.glob("*.png") if path.is_file())
    missing_row_keys = [
        index
        for index, row in enumerate(rows)
        if any(key not in row or not str(row[key]).strip() for key in REQUIRED_METADATA_KEYS)
    ]
    missing_images = [
        str(row.get("file_name", ""))
        for row in rows
        if not (dataset_dir / str(row.get("file_name", ""))).is_file()
    ]
    return {
        "dataset_dir": dataset_dir.as_posix(),
        "metadata_jsonl": metadata_path.as_posix(),
        "expected_count": int(expected_count),
        "metadata_rows": len(rows),
        "image_count": len(image_files),
        "missing_row_keys": missing_row_keys,
        "missing_images": missing_images,
        "ready": (
            metadata_path.is_file()
            and len(rows) == int(expected_count)
            and len(image_files) == int(expected_count)
            and not missing_row_keys
            and not missing_images
        ),
    }


def validate_clid_bridge_run(run_root: str | Path) -> dict[str, Any]:
    """Validate the portable output contract of a prepared CLiD bridge run."""

    root = Path(run_root)
    config_path = root / "config.json"
    analysis_path = root / "analysis.md"
    localized_script = root / "mia_CLiD_clip_local.py"
    config = _read_json(config_path) if config_path.is_file() else {}
    missing_config_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    export = config.get("export", {}) if isinstance(config.get("export"), dict) else {}
    assets = config.get("assets", {}) if isinstance(config.get("assets"), dict) else {}
    member_count = int(export.get("member", {}).get("count", 0)) if isinstance(export.get("member"), dict) else 0
    nonmember_count = (
        int(export.get("nonmember", {}).get("count", 0)) if isinstance(export.get("nonmember"), dict) else 0
    )
    member_dir = Path(str(assets.get("member_dataset", root / "datasets" / "member")))
    nonmember_dir = Path(str(assets.get("nonmember_dataset", root / "datasets" / "nonmember")))
    if not member_dir.is_absolute():
        member_dir = Path(member_dir)
    if not nonmember_dir.is_absolute():
        nonmember_dir = Path(nonmember_dir)

    script_text = localized_script.read_text(encoding="utf-8") if localized_script.is_file() else ""
    checks = {
        "run_root": root.is_dir(),
        "config_json": config_path.is_file(),
        "analysis_md": analysis_path.is_file(),
        "localized_script": localized_script.is_file(),
        "config_required_keys": not missing_config_keys,
        "method_is_clid": config.get("method") == "clid",
        "status_is_prepared": config.get("status") == "prepared",
        "mode_is_bridge": config.get("mode") == "paper-alignment-local-bridge",
        "script_markers": all(marker in script_text for marker in REQUIRED_SCRIPT_MARKERS),
    }
    split_checks = {
        "member": _metadata_check(member_dir, member_count),
        "nonmember": _metadata_check(nonmember_dir, nonmember_count),
    }
    checks["member_dataset_contract"] = split_checks["member"]["ready"]
    checks["nonmember_dataset_contract"] = split_checks["nonmember"]["ready"]
    checks["nonempty_balanced_export"] = member_count > 0 and member_count == nonmember_count
    missing = [key for key, ready in checks.items() if not ready]
    return {
        "status": "ready" if not missing else "blocked",
        "track": "black-box",
        "method": "clid",
        "mode": "bridge-contract-review",
        "run_root": root.as_posix(),
        "artifact_paths": {
            "config": _relative_or_token(config_path, root),
            "analysis": _relative_or_token(analysis_path, root),
            "localized_script": _relative_or_token(localized_script, root),
        },
        "checks": checks,
        "split_checks": split_checks,
        "missing": missing,
        "missing_config_keys": missing_config_keys,
        "verdict": "prepared bridge contract is reusable" if not missing else "bridge contract is incomplete",
        "next_action": (
            "freeze score output schema before any GPU packet"
            if not missing
            else "fix missing bridge artifacts before execution"
        ),
    }
