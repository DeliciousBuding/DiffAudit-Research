from __future__ import annotations

import argparse
import json
from pathlib import Path

ADMITTED_CONSUMER_ROWS = (
    {
        "track": "black-box",
        "attack": "recon DDIM public-100 step30",
        "defense": "none",
        "evidence_level": "runtime-mainline",
        "source": "docs/evidence/recon-product-validation-result.md",
    },
    {
        "track": "gray-box",
        "attack": "PIA GPU512 baseline",
        "defense": "none",
        "evidence_level": "runtime-mainline",
        "source": "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/summary.json",
    },
    {
        "track": "gray-box",
        "attack": "PIA GPU512 baseline",
        "defense": "provisional G-1 = stochastic-dropout (all_steps)",
        "evidence_level": "runtime-mainline",
        "source": "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/summary.json",
    },
    {
        "track": "white-box",
        "attack": "GSA 1k-3shadow",
        "defense": "none",
        "evidence_level": "runtime-mainline",
        "source": "workspaces/white-box/runs/gsa-runtime-mainline-20260409-cifar10-1k-3shadow-epoch300-rerun1/summary.json",
    },
    {
        "track": "white-box",
        "attack": "GSA 1k-3shadow",
        "defense": "W-1 strong-v3 full-scale",
        "evidence_level": "runtime-smoke",
        "source": "workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/summary.json",
    },
)
REQUIRED_METRICS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_rel_path(value: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    return not (value.startswith("/") or (len(value) >= 3 and value[1:3] == ":\\"))  # repo-relative only


def _require_fields(errors: list[str], prefix: str, payload: dict, required: tuple[str, ...]) -> None:
    for key in required:
        if key not in payload:
            errors.append(f"{prefix} missing required field: {key}")


def _require_numeric(errors: list[str], prefix: str, payload: dict, fields: tuple[str, ...]) -> None:
    for key in fields:
        value = payload.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{prefix}.{key} must be numeric, got {value!r}")


def _validate_recon_product_row(errors: list[str], rows: list[dict]) -> None:
    candidates = [
        row
        for row in rows
        if row.get("track") == "black-box"
        and row.get("attack") == "recon DDIM public-100 step30"
        and row.get("defense") == "none"
        and row.get("evidence_level") == "runtime-mainline"
    ]
    if len(candidates) != 1:
        errors.append(f"expected exactly one admitted recon product row, found {len(candidates)}")
        return

    row = candidates[0]
    _require_fields(
        errors,
        "admitted_recon_row",
        row,
        ("metric_source", "quality_cost", "note", "boundary", "source"),
    )
    _require_numeric(errors, "admitted_recon_row", row, ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"))

    if row.get("metric_source") != "upstream_threshold_reimplementation":
        errors.append(
            "admitted_recon_row.metric_source must be 'upstream_threshold_reimplementation'"
        )
    if row.get("source") != "docs/evidence/recon-product-validation-result.md":
        errors.append("admitted_recon_row.source must point to recon-product-validation-result.md")

    boundary = str(row.get("boundary", ""))
    for phrase in (
        "controlled",
        "public-subset",
        "proxy-shadow-member",
        "zero-false-positive empirical tail",
        "not a final exploit",
    ):
        if phrase not in boundary:
            errors.append(f"admitted_recon_row.boundary missing phrase: {phrase}")


def _row_matches(row: dict, selector: dict[str, str]) -> bool:
    return all(row.get(key) == value for key, value in selector.items())


def _validate_admitted_consumer_rows(errors: list[str], rows: list[dict]) -> None:
    for selector in ADMITTED_CONSUMER_ROWS:
        label = f"{selector['track']}:{selector['attack']}:{selector['defense']}"
        matches = [row for row in rows if _row_matches(row, selector)]
        if len(matches) != 1:
            errors.append(f"expected exactly one admitted consumer row for {label}, found {len(matches)}")
            continue
        row = matches[0]
        _require_numeric(errors, f"admitted_consumer_row[{label}]", row, REQUIRED_METRICS)
        _require_fields(errors, f"admitted_consumer_row[{label}]", row, ("quality_cost", "boundary"))
        if not str(row.get("boundary", "")).strip():
            errors.append(f"admitted_consumer_row[{label}].boundary must be non-empty")
        if not str(row.get("quality_cost", "")).strip():
            errors.append(f"admitted_consumer_row[{label}].quality_cost must be non-empty")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_attack_defense_table",
        description="Validate the admitted unified attack-defense table contract.",
    )
    parser.add_argument(
        "--table",
        type=Path,
        default=None,
        help="Path to unified attack-defense table JSON (default: <research_root>/workspaces/implementation/artifacts/unified-attack-defense-table.json).",
    )
    args = parser.parse_args(argv)

    research_root = Path(__file__).resolve().parents[1]
    table_path = (
        args.table
        or research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json"
    ).resolve()

    errors: list[str] = []

    if not table_path.exists():
        errors.append(f"table does not exist: {table_path}")
    else:
        payload = _load_json(table_path)
        if payload.get("schema") != "diffaudit.attack_defense_table.v1":
            errors.append(f"unsupported schema: {payload.get('schema')!r}")
        _require_fields(errors, "table", payload, ("schema", "updated_at", "rows"))

        rows = payload.get("rows")
        if not isinstance(rows, list) or not rows:
            errors.append("rows must be a non-empty list")
        else:
            typed_rows: list[dict] = []
            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    errors.append(f"rows[{idx}] must be an object")
                    continue
                typed_rows.append(row)

                _require_fields(
                    errors,
                    f"rows[{idx}]",
                    row,
                    ("track", "attack", "defense", "model", "evidence_level", "source", "boundary"),
                )

                source = row.get("source")
                if isinstance(source, str) and source and not _is_rel_path(source):
                    errors.append(f"rows[{idx}].source must be a repo-relative path: {source!r}")

                if row.get("track") != "gray-box":
                    continue

                _require_fields(
                    errors,
                    f"rows[{idx}]",
                    row,
                    ("quality", "cost", "adaptive_check", "provenance_status"),
                )

                adaptive_check = row.get("adaptive_check")
                if not isinstance(adaptive_check, dict):
                    continue
                if adaptive_check.get("status") != "completed":
                    continue

                _require_fields(
                    errors,
                    f"rows[{idx}].adaptive_check",
                    adaptive_check,
                    ("query_repeats", "aggregation", "metrics"),
                )
            _validate_recon_product_row(errors, typed_rows)
            _validate_admitted_consumer_rows(errors, typed_rows)

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 2

    print(f"OK {table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
