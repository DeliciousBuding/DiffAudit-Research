"""Export the admitted recon row as a system-consumable evidence card."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TABLE = Path("workspaces/implementation/artifacts/unified-attack-defense-table.json")
DEFAULT_OUTPUT = Path("workspaces/implementation/artifacts/recon-product-evidence-card.json")
RECON_ROW_SELECTOR = {
    "track": "black-box",
    "attack": "recon DDIM public-100 step30",
    "defense": "none",
    "evidence_level": "runtime-mainline",
}
REQUIRED_METRICS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_numeric(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"admitted recon row {key} must be numeric, got {value!r}")
    return float(value)


def _select_recon_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [
        row
        for row in rows
        if all(row.get(key) == value for key, value in RECON_ROW_SELECTOR.items())
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one admitted recon product row, found {len(matches)}")
    return matches[0]


def build_recon_product_evidence_card(table: dict[str, Any], *, table_path: Path, root: Path) -> dict[str, Any]:
    rows = table.get("rows")
    if not isinstance(rows, list):
        raise ValueError("table.rows must be a list")
    row = _select_recon_row(rows)
    metrics = {key: _require_numeric(row, key) for key in REQUIRED_METRICS}
    source = row.get("source")
    if source != "docs/evidence/recon-product-validation-result.md":
        raise ValueError("admitted recon row must point to docs/evidence/recon-product-validation-result.md")
    if row.get("metric_source") != "upstream_threshold_reimplementation":
        raise ValueError("admitted recon row must use upstream_threshold_reimplementation")

    return {
        "schema": "diffaudit.product_evidence_card.v1",
        "updated_at": table.get("updated_at"),
        "status": "admitted",
        "audience": "platform-runtime",
        "track": row["track"],
        "method": {
            "attack": row["attack"],
            "defense": row["defense"],
            "model": row["model"],
        },
        "metrics": metrics,
        "metric_source": row["metric_source"],
        "evidence_level": row["evidence_level"],
        "quality_cost": row["quality_cost"],
        "finite_tail": {
            "target_member_count": 100,
            "target_nonmember_count": 100,
            "gates": {
                "tpr_at_1pct_fpr": {
                    "allowed_false_positives": 1,
                    "true_positives": 22,
                    "false_positives": 1,
                    "empirical_tpr": metrics["tpr_at_1pct_fpr"],
                    "empirical_fpr": 0.01,
                },
                "tpr_at_0_1pct_fpr": {
                    "allowed_false_positives": 0,
                    "true_positives": 11,
                    "false_positives": 0,
                    "empirical_tpr": metrics["tpr_at_0_1pct_fpr"],
                    "empirical_fpr": 0.0,
                },
            },
            "interpretation": (
                "Finite public-100 target split; strict-tail values are count-level "
                "empirical gates, not continuous sub-percent calibration."
            ),
        },
        "boundary": {
            "summary": row["boundary"],
            "allowed_claims": [
                "verified black-box privacy-risk signal on a controlled public-100 packet",
                "all four headline metrics come from one upstream-threshold metric source",
                "nonzero strict-tail signal with explicit finite-sample caveat",
            ],
            "blocked_claims": [
                "paper-complete reproduction",
                "general conditional-diffusion result",
                "full real-world exploit benchmark",
                "fine-grained sub-percent FPR calibration",
            ],
        },
        "provenance": {
            "table": _repo_relative(table_path, root),
            "source": source,
            "handoff": "docs/product-bridge/recon-product-validation-handoff.md",
            "run": "recon-product-validation-public100-step30-20260501-r1",
        },
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="export_recon_product_evidence_card",
        description="Export and validate the admitted recon product evidence card.",
    )
    parser.add_argument("--table", type=Path, default=root / DEFAULT_TABLE)
    parser.add_argument("--output", type=Path, default=root / DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the output file is missing or differs from the generated card",
    )
    args = parser.parse_args(argv)

    try:
        table_path = args.table if args.table.is_absolute() else root / args.table
        output_path = args.output if args.output.is_absolute() else root / args.output
        card = build_recon_product_evidence_card(_load_json(table_path), table_path=table_path, root=root)
        rendered = json.dumps(card, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not output_path.exists():
                raise ValueError(f"missing evidence card: {output_path}")
            existing = output_path.read_text(encoding="utf-8")
            if existing != rendered:
                raise ValueError(f"evidence card is out of sync: {output_path}")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
    except Exception as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2

    print(f"OK {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
