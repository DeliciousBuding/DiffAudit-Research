"""Render a public-safe Markdown risk card from the admitted evidence bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_BUNDLE = Path("workspaces/implementation/artifacts/admitted-evidence-bundle.json")
DEFAULT_OUTPUT = Path("workspaces/implementation/artifacts/admitted-risk-card.md")

FORBIDDEN_REPORTABLE_TERMS = (
    "H2 output-cloud",
    "Tracing the Roots",
    "CommonCanvas",
    "MIDST",
    "CLiD",
    "ReDiffuse",
    "weak scout",
    "source-confounded",
)

PRIVATE_SURFACE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local DiffAudit D: path", re.compile(r"D:(?:\\+|/+)+Code(?:\\+|/+)+DiffAudit")),
    ("local Ding user path", re.compile(r"C:(?:\\+|/+)+Users(?:\\+|/+)+Ding")),
    ("WSL Ding user path", re.compile(r"/mnt/c/Users/" + "Ding", re.IGNORECASE)),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _method_label(row: dict[str, Any]) -> str:
    method = row.get("method")
    if not isinstance(method, dict):
        raise ValueError(f"risk-card row {row.get('id', '<missing>')} missing method object")
    attack = str(method.get("attack", ""))
    defense = str(method.get("defense", ""))
    if defense and defense != "none":
        return f"{attack} / {defense}"
    return attack


def _private_surface_hits(value: Any, *, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        for label, pattern in PRIVATE_SURFACE_PATTERNS:
            if pattern.search(value):
                hits.append(f"{path}: {label}")
    elif isinstance(value, dict):
        for key, nested in value.items():
            hits.extend(_private_surface_hits(nested, path=f"{path}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            hits.extend(_private_surface_hits(nested, path=f"{path}[{index}]"))
    return hits


def _report_replay_tier(row: dict[str, Any]) -> str:
    track = str(row.get("track", ""))
    role = str(row.get("report_role", ""))
    if role == "defense-bridge":
        return "target-score replay"
    if role == "upper-bound-comparator":
        return "source-documented point estimate"
    if track == "black-box":
        return "source-documented point estimate"
    if track == "gray-box":
        return "row-score replay"
    return "declared admitted tier"


def _public_caveat(summary: Any) -> str:
    text = str(summary)
    replacements = {
        "workspace-verified + adaptive-reviewed + paper-alignment blocked by checkpoint/source provenance": (
            "row-score replay with adaptive review recorded; checkpoint/source provenance "
            "limits broader paper-alignment wording"
        ),
        "admitted white-box bridge / risk upper-bound; not a final paper-level benchmark": (
            "white-box upper-bound comparator; not a final paper-level benchmark"
        ),
        "admitted white-box bridge / defended comparator; not a final paper-level benchmark": (
            "white-box defense bridge comparator; not a final paper-level benchmark"
        ),
    }
    return replacements.get(text, text)


def _validate_bundle(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    if bundle.get("schema") != "diffaudit.admitted_evidence_bundle.v1":
        raise ValueError("risk card requires diffaudit.admitted_evidence_bundle.v1")
    if bundle.get("status") != "admitted-only":
        raise ValueError("risk card requires bundle status admitted-only")
    if bundle.get("audience") != "platform-runtime":
        raise ValueError("risk card requires platform-runtime audience")
    rows = bundle.get("rows")
    if not isinstance(rows, list):
        raise ValueError("risk card requires rows list")
    if bundle.get("row_count") != len(rows):
        raise ValueError(f"risk card row_count drift: {bundle.get('row_count')!r} != {len(rows)}")
    if len(rows) != 5:
        raise ValueError(f"risk card expects five admitted case-study rows, got {len(rows)}")

    for row in rows:
        row_id = str(row.get("id", "<missing>"))
        private_hits = _private_surface_hits(row)
        if private_hits:
            raise ValueError(f"risk-card row {row_id} contains private surface: {private_hits[0]}")
        if row.get("status") != "admitted":
            raise ValueError(f"risk card refuses non-admitted row: {row_id}")
        if row.get("audience") != "platform-runtime":
            raise ValueError(f"risk card refuses non-platform-runtime row: {row_id}")
        evidence_level = str(row.get("evidence_level", ""))
        if "candidate" in evidence_level or "support" in evidence_level or "watch" in evidence_level:
            raise ValueError(f"risk card refuses non-reportable evidence level for row: {row_id}")
        method_label = _method_label(row)
        for term in FORBIDDEN_REPORTABLE_TERMS:
            if term.lower() in method_label.lower():
                raise ValueError(f"risk card refuses candidate/support method in admitted rows: {term}")
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError(f"risk-card row {row_id} missing metrics")
        low_fpr = row.get("low_fpr_interpretation")
        if not isinstance(low_fpr, dict) or not low_fpr.get("nonmember_denominator"):
            raise ValueError(f"risk-card row {row_id} missing nonmember denominator")
        boundary = row.get("boundary")
        if not isinstance(boundary, dict) or not boundary.get("summary"):
            raise ValueError(f"risk-card row {row_id} missing boundary summary")
    return rows


def render_risk_card(bundle: dict[str, Any], *, bundle_path: Path, root: Path) -> str:
    rows = _validate_bundle(bundle)
    lines = [
        "# DiffAudit Admitted Risk Card",
        "",
        "> Public-safe case-study report surface generated from the admitted evidence bundle.",
        "",
        f"- Source bundle: `{_repo_relative(bundle_path, root)}`",
        f"- Bundle status: `{bundle['status']}`",
        "- Report surface: `report-facing case-study artifact`",
        f"- Row count: `{bundle['row_count']}`",
        "- Boundary: three rows are replay-admitted from row/target-score arrays; two rows are source-documented point estimates.",
        "- Candidate exclusion: H2 output-cloud geometry, Tracing the Roots, ReDiffuse, CommonCanvas, MIDST, CLiD, weak scouts, and source-confounded packets are not reportable audit rows in this card.",
        "- Tail caveat: low-FPR values are finite packet readouts, not calibrated continuous sub-percent risk estimates.",
        "",
        "| Report role | Access | Method | AUC | TPR@0.1%FPR | Replay/source tier | Tail n0 | Required caveat |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for row in rows:
        metrics = row["metrics"]
        low_fpr = row["low_fpr_interpretation"]
        boundary = row["boundary"]
        lines.append(
            "| {role} | {access} | {method} | {auc} | {tail} | {tier} | {n0} | {caveat} |".format(
                role=row.get("report_role", "admitted-evidence"),
                access=row.get("required_access", row.get("track", "declared")),
                method=_method_label(row).replace("|", "/"),
                auc=_fmt(metrics.get("auc")),
                tail=_fmt(metrics.get("tpr_at_0_1pct_fpr")),
                tier=_report_replay_tier(row),
                n0=low_fpr.get("nonmember_denominator"),
                caveat=_public_caveat(boundary.get("summary", "")).replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Report-Correctness Rules",
            "",
            "- Do not rank these rows as a cross-access leaderboard.",
            "- Do not describe source-documented point estimates as replay-admitted rows.",
            "- Do not add candidate, support-only, watch, weak-scout, or source-confounded rows to this card without a reviewed admission-state change.",
            "- Do not interpret finite low-FPR tails as calibrated continuous sub-percent rates.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="render_admitted_risk_card",
        description="Render and check the public-safe admitted evidence risk card.",
    )
    parser.add_argument("--bundle", type=Path, default=root / DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=root / DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="fail if output differs from rendered card")
    args = parser.parse_args(argv)

    try:
        bundle_path = args.bundle.resolve()
        output_path = args.output.resolve()
        rendered = render_risk_card(_load_json(bundle_path), bundle_path=bundle_path, root=root)
        if args.check:
            if not output_path.exists():
                raise ValueError(f"missing admitted risk card: {output_path}")
            existing = output_path.read_text(encoding="utf-8")
            if existing != rendered:
                raise ValueError(f"admitted risk card is out of sync: {output_path}")
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
