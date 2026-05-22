"""Asset probe for the public CopyMark + laion_mi binding surface."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_PACKAGE_RELATIVE = Path("Download/black-box/supplementary/copymark-laion-mi-public-20260517/raw")
DEFAULT_MEMBER_PARQUET = "members.parquet"
DEFAULT_MEMBER_IMAGE_LOG = "pia_laion_mi_image_log.json"
DEFAULT_MEMBER_SCRIPT = "get_laion_mi_2_5k_member_img_caption.py"
REQUIRED_FILES = (DEFAULT_MEMBER_PARQUET, DEFAULT_MEMBER_IMAGE_LOG, DEFAULT_MEMBER_SCRIPT)


def diffaudit_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_package_root() -> Path:
    return diffaudit_root() / DEFAULT_PACKAGE_RELATIVE


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path.name} must contain a top-level JSON object")
    return payload


def _read_member_parquet(path: Path) -> dict[str, Any]:
    df = pd.read_parquet(path)
    return {
        "columns": [str(column) for column in df.columns.tolist()],
        "row_count": int(len(df)),
        "head": df.head(3).to_dict(orient="records"),
    }


def _member_image_log_summary(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    member_files = payload.get("member") or []
    numeric_ids = []
    non_numeric = []
    for name in member_files:
        stem = Path(str(name)).stem
        if stem.isdigit():
            numeric_ids.append(int(stem))
        else:
            non_numeric.append(str(name))
    return {
        "member_count": int(len(member_files)),
        "numeric_member_id_count": int(len(numeric_ids)),
        "min_numeric_member_id": min(numeric_ids) if numeric_ids else None,
        "max_numeric_member_id": max(numeric_ids) if numeric_ids else None,
        "first_member_files": [str(name) for name in member_files[:10]],
        "non_numeric_member_files": non_numeric[:10],
    }


def _member_script_summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    hidden_id_patterns = [
        r"df\.iloc\s*\[\s*idx\s*,\s*2\s*\]",
        r"iloc\s*\[\s*idx\s*,\s*2\s*\]",
    ]
    uses_hidden_id = any(re.search(pattern, text) for pattern in hidden_id_patterns)
    return {
        "uses_hidden_id_column": uses_hidden_id,
        "uses_row_index_filename": "idx=idx" in text or "f'{idx}.png'" in text or 'f"{idx}.png"' in text,
        "preview": text[:400],
    }


def probe_copymark_laion_mi_assets(
    package_root: str | Path | None = None,
    member_parquet: str | Path | None = None,
    member_image_log: str | Path | None = None,
    member_script: str | Path | None = None,
) -> dict[str, Any]:
    package = Path(package_root) if package_root else default_package_root()
    member_parquet_path = Path(member_parquet) if member_parquet else package / DEFAULT_MEMBER_PARQUET
    member_image_log_path = Path(member_image_log) if member_image_log else package / DEFAULT_MEMBER_IMAGE_LOG
    member_script_path = Path(member_script) if member_script else package / DEFAULT_MEMBER_SCRIPT

    file_checks = {
        "member_parquet": member_parquet_path.exists(),
        "member_image_log": member_image_log_path.exists(),
        "member_script": member_script_path.exists(),
    }
    if not package.exists() or not all(file_checks.values()):
        missing = [path for path, ready in {
            str(member_parquet_path): file_checks["member_parquet"],
            str(member_image_log_path): file_checks["member_image_log"],
            str(member_script_path): file_checks["member_script"],
        }.items() if not ready]
        return {
            "status": "blocked",
            "track": "black-box",
            "method": "copymark_laion_mi",
            "mode": "asset-probe",
            "asset_family": "public-copymark-laion-mi",
            "checks": {
                "package_root": package.exists(),
                **file_checks,
            },
            "paths": {
                "package_root": str(package),
                "member_parquet": str(member_parquet_path),
                "member_image_log": str(member_image_log_path),
                "member_script": str(member_script_path),
            },
            "member_parquet": {},
            "member_image_log": {},
            "member_script": {},
            "missing": missing,
            "missing_items": [Path(path).name for path in missing],
            "notes": [
                "The minimal public CopyMark + laion_mi binding package is incomplete, so the public row-binding gate cannot run yet."
            ],
        }

    member_parquet_summary = _read_member_parquet(member_parquet_path)
    member_image_log_summary = _member_image_log_summary(member_image_log_path)
    member_script_summary = _member_script_summary(member_script_path)

    row_count = member_parquet_summary["row_count"]
    max_id = member_image_log_summary["max_numeric_member_id"]
    member_filenames_within_row_range = (
        member_image_log_summary["numeric_member_id_count"] == member_image_log_summary["member_count"]
        and max_id is not None
        and max_id < row_count
    )
    public_member_schema_has_two_columns = member_parquet_summary["columns"] == ["url", "caption"]
    binding_reconstructible = (
        not member_script_summary["uses_hidden_id_column"]
        and member_filenames_within_row_range
    )

    checks = {
        "package_root": True,
        **file_checks,
        "public_member_schema_has_two_columns": public_member_schema_has_two_columns,
        "member_script_uses_hidden_id_column": member_script_summary["uses_hidden_id_column"],
        "member_filenames_within_public_row_range": member_filenames_within_row_range,
        "binding_reconstructible_from_public_surface": binding_reconstructible,
    }
    status = "ready" if binding_reconstructible else "blocked"

    notes = [
        "This probe asks whether the public CopyMark laion_mi score surface can be rebound to public row identities, not whether the aggregate AUROC artifacts exist.",
    ]
    if public_member_schema_has_two_columns:
        notes.append(
            "The current public HF members parquet exposes only url/caption columns, so no explicit public numeric image identifier is available from the parquet schema."
        )
    if member_script_summary["uses_hidden_id_column"]:
        notes.append(
            "The official member-download utility expects a third parquet column via df.iloc[idx, 2], which the current public parquet schema does not expose."
        )
    if not member_filenames_within_row_range:
        notes.append(
            "Official member image-log filenames are numeric but exceed the current public member row range, so they cannot be interpreted as simple public row indices."
        )
    if binding_reconstructible:
        notes.append(
            "This public surface is row-bindable under the supplied synthetic/local inputs."
        )

    return {
        "status": status,
        "track": "black-box",
        "method": "copymark_laion_mi",
        "mode": "asset-probe",
        "asset_family": "public-copymark-laion-mi",
        "checks": checks,
        "paths": {
            "package_root": str(package),
            "member_parquet": str(member_parquet_path),
            "member_image_log": str(member_image_log_path),
            "member_script": str(member_script_path),
        },
        "member_parquet": member_parquet_summary,
        "member_image_log": member_image_log_summary,
        "member_script": member_script_summary,
        "missing": [],
        "missing_items": [],
        "notes": notes,
    }
