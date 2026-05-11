"""Export all admitted Platform/Runtime evidence rows as one bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_attack_defense_table import ADMITTED_CONSUMER_ROWS, REQUIRED_METRICS

DEFAULT_TABLE = Path("workspaces/implementation/artifacts/unified-attack-defense-table.json")
DEFAULT_OUTPUT = Path("workspaces/implementation/artifacts/admitted-evidence-bundle.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_numeric(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"admitted evidence row {key} must be numeric, got {value!r}")
    return float(value)


def _row_matches(row: dict[str, Any], selector: dict[str, str]) -> bool:
    return all(row.get(key) == value for key, value in selector.items())


def _select_row(rows: list[dict[str, Any]], selector: dict[str, str]) -> dict[str, Any]:
    identity_keys = ("track", "attack", "defense", "evidence_level")
    identity = {key: selector[key] for key in identity_keys}
    matches = [row for row in rows if _row_matches(row, identity)]
    label = f"{selector['track']}:{selector['attack']}:{selector['defense']}:{selector['evidence_level']}"
    if len(matches) != 1:
        raise ValueError(f"expected exactly one admitted evidence row for {label}, found {len(matches)}")
    row = matches[0]
    if row.get("source") != selector["source"]:
        raise ValueError(f"admitted evidence row {label} source drift: {row.get('source')!r}")
    return row


def _allowed_claims(row: dict[str, Any]) -> list[str]:
    track = row["track"]
    if track == "black-box":
        return [
            "verified black-box privacy-risk signal under the stated controlled packet",
            "all headline metrics are tied to the recorded metric source",
            "strict-tail values are finite empirical gates, not continuous calibration",
        ]
    if track == "gray-box":
        return [
            "workspace-verified DDPM/CIFAR10 gray-box evidence under the stated query budget",
            "bounded repeated-query adaptive review is recorded when adaptive_check.status is completed",
            "strict-tail values are finite empirical points over the recorded packet scale",
        ]
    if track == "white-box":
        return [
            "workspace-verified white-box risk or defended-comparator evidence under the stated protocol",
            "the row can be used as an admitted upper-bound or comparator with its boundary language attached",
            "strict-tail values are finite empirical points, not paper-complete calibration",
        ]
    return ["verified row under the stated evidence boundary"]


def _blocked_claims(row: dict[str, Any]) -> list[str]:
    blocked = [
        "paper-complete reproduction",
        "general conditional-diffusion result",
        "commercial-model or real-world deployment benchmark",
        "continuous sub-percent FPR calibration",
    ]
    if row["track"] == "gray-box":
        blocked.append("full adaptive robustness beyond the recorded repeated-query review")
    if row["track"] == "white-box":
        blocked.append("final paper-level benchmark")
    return blocked


def _tail_nonmember_count(row: dict[str, Any]) -> int:
    cost = row.get("cost")
    if isinstance(cost, dict):
        sample_count = cost.get("sample_count_per_split")
        if isinstance(sample_count, int) and not isinstance(sample_count, bool) and sample_count > 0:
            return sample_count

    quality_cost = str(row.get("quality_cost", ""))
    for pattern in (
        r"(?P<count>\d+)\s+public samples per split",
        r"target_eval_size=(?P<count>\d+)",
    ):
        match = re.search(pattern, quality_cost)
        if match:
            return int(match.group("count"))

    raise ValueError(
        "admitted evidence row needs a recoverable nonmember denominator for low-FPR interpretation"
    )


def _low_fpr_interpretation(row: dict[str, Any]) -> dict[str, Any]:
    nonmember_count = _tail_nonmember_count(row)
    return {
        "type": "finite_empirical_tail",
        "nonmember_denominator": nonmember_count,
        "false_positive_budget": {
            "at_1pct_fpr": nonmember_count * 0.01,
            "at_0_1pct_fpr": nonmember_count * 0.001,
        },
        "minimum_nonzero_fpr": 1.0 / nonmember_count,
        "summary": (
            "TPR@1%FPR and TPR@0.1%FPR are finite packet readouts. "
            "They must not be treated as calibrated continuous sub-percent FPR estimates."
        ),
    }


def _build_card(row: dict[str, Any], *, table_path: Path, root: Path) -> dict[str, Any]:
    metrics = {key: _require_numeric(row, key) for key in REQUIRED_METRICS}
    card: dict[str, Any] = {
        "id": f"{row['track']}::{row['attack']}::{row['defense']}::{row['evidence_level']}",
        "status": "admitted",
        "audience": "platform-runtime",
        "track": row["track"],
        "method": {
            "attack": row["attack"],
            "defense": row["defense"],
            "model": row["model"],
        },
        "metrics": metrics,
        "evidence_level": row["evidence_level"],
        "quality_cost": row["quality_cost"],
        "boundary": {
            "summary": row["boundary"],
            "allowed_claims": _allowed_claims(row),
            "blocked_claims": _blocked_claims(row),
        },
        "low_fpr_interpretation": _low_fpr_interpretation(row),
        "provenance": {
            "table": _repo_relative(table_path, root),
            "source": row["source"],
        },
    }
    if "metric_source" in row:
        card["metric_source"] = row["metric_source"]
    if "provenance_status" in row:
        card["provenance_status"] = row["provenance_status"]
    if isinstance(row.get("cost"), dict):
        card["cost"] = row["cost"]
    if isinstance(row.get("adaptive_check"), dict):
        card["adaptive_check"] = row["adaptive_check"]
    return card


def build_admitted_evidence_bundle(table: dict[str, Any], *, table_path: Path, root: Path) -> dict[str, Any]:
    rows = table.get("rows")
    if not isinstance(rows, list):
        raise ValueError("table.rows must be a list")
    cards = [_build_card(_select_row(rows, selector), table_path=table_path, root=root) for selector in ADMITTED_CONSUMER_ROWS]
    return {
        "schema": "diffaudit.admitted_evidence_bundle.v1",
        "updated_at": table.get("updated_at"),
        "status": "admitted-only",
        "audience": "platform-runtime",
        "source_table": _repo_relative(table_path, root),
        "row_count": len(cards),
        "rows": cards,
        "excluded_states": [
            "candidate-only",
            "hold",
            "needs-assets",
            "negative-but-useful",
            "runtime-candidate",
            "runtime-challenger",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="export_admitted_evidence_bundle",
        description="Export and validate the admitted Platform/Runtime evidence bundle.",
    )
    parser.add_argument("--table", type=Path, default=root / DEFAULT_TABLE)
    parser.add_argument("--output", type=Path, default=root / DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the output file is missing or differs from the generated bundle",
    )
    args = parser.parse_args(argv)

    try:
        table_path = args.table.resolve()
        output_path = args.output.resolve()
        bundle = build_admitted_evidence_bundle(_load_json(table_path), table_path=table_path, root=root)
        rendered = json.dumps(bundle, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not output_path.exists():
                raise ValueError(f"missing admitted evidence bundle: {output_path}")
            existing = output_path.read_text(encoding="utf-8")
            if existing != rendered:
                raise ValueError(f"admitted evidence bundle is out of sync: {output_path}")
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
