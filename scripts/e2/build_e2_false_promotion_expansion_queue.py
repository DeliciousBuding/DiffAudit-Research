"""Build the next E2 false-promotion expansion queue.

The queue is derived from the latest no-download public-surface metadata
refresh. It is a planning artifact only: rows here are not admitted evidence,
not N50 denominator rows, and do not release compute.
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"

SCOUT_QUEUE = PREFLIGHT / "e2_n50_public_surface_scout_2026_06_06.csv"
METADATA_REFRESH = PREFLIGHT / "e2_n50_public_surface_metadata_refresh.csv"
GATE_QUEUE = PREFLIGHT / "e2_n50_scout_gate_review_queue.csv"
OUT_CSV = PREFLIGHT / "e2_false_promotion_expansion_queue_2026_06_07.csv"
OUT_MD = PREFLIGHT / "e2_false_promotion_expansion_queue_2026_06_07.md"

COMPLETED_EXEMPLARS = {
    "E2SCT-002",
    "E2SCT-004",
    "E2SCT-005",
    "E2SCT-009",
    "E2SCT-011",
    "E2SCT-012",
    "E2SCT-013",
    "E2SCT-014",
    "E2SCT-019",
    "E2SCT-016",
    "E2SCT-020",
    "E2SCT-021",
    "E2SCT-024",
}

CLOSED_AFTER_DETAILED_CHECK = {
    "E2SCT-022",
    "E2SCT-023",
    "E2SCT-025",
    "E2SCT-028",
}

FIELDNAMES = [
    "priority",
    "row_id",
    "title",
    "source_urls",
    "metadata_refreshed_at_utc",
    "artifact_surface_hint",
    "source_kinds",
    "metadata_quality",
    "public_surface_observed",
    "weak_rules_pressure",
    "first_blocker",
    "next_no_download_check",
    "denominator_status",
    "admission_status",
    "compute_release",
    "paper_action",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def compact(value: str, limit: int = 260) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def weak_rules_for(row: dict[str, str]) -> str:
    rules = ["paper_claim_artifact_link_would_promote"]
    source_kinds = row["source_kinds"].split(";")
    surface = row["artifact_surface_hint"]
    if "github" in source_kinds or surface == "code_only_surface_hint":
        rules.append("code_availability_would_promote")
    if surface in {"score_or_metric_surface_hint", "split_checkpoint_surface_hint"}:
        rules.append("artifact_availability_would_promote")
    if surface == "score_or_metric_surface_hint":
        rules.append("metric_code_split_would_promote")
    return "; ".join(dict.fromkeys(rules))


def metadata_quality(row: dict[str, str]) -> str:
    notes = row["metadata_notes"].lower()
    if "github_rate_limited=1" in notes:
        return "fallback_metadata_after_github_rate_limit"
    return "current_no_download_metadata"


def latest_metadata_refresh() -> str:
    rows = read_csv(METADATA_REFRESH)
    return sorted({row["refreshed_at_utc"] for row in rows})[-1] if rows else ""


def first_blocker(meta: dict[str, str], gate: dict[str, str]) -> str:
    blocker = f"Detailed row-level public-surface check not yet completed; {gate['gate_review_focus']}."
    if metadata_quality(meta).startswith("fallback"):
        blocker += " GitHub API metadata was rate-limited, so the detailed check must use raw/page fallback or authenticated metadata."
    return compact(f"{blocker} Risk/boundary: {gate['risk_or_duplicate']}", 420)


def build_rows() -> list[dict[str, str]]:
    scout_by_id = {row["queue_id"]: row for row in read_csv(SCOUT_QUEUE)}
    metadata_by_id = {row["queue_id"]: row for row in read_csv(METADATA_REFRESH)}
    gate_rows = read_csv(GATE_QUEUE)

    rows: list[dict[str, str]] = []
    priority = 1
    for gate in gate_rows:
        row_id = gate["scout_queue_id"]
        if row_id in COMPLETED_EXEMPLARS:
            continue
        if row_id in CLOSED_AFTER_DETAILED_CHECK:
            continue
        scout = scout_by_id[row_id]
        meta = metadata_by_id[row_id]
        observed = (
            f"{meta['artifact_surface_hint']} from {meta['source_kinds']}; "
            f"signals: {meta['signal_items_sample'] or 'metadata only'}"
        )
        rows.append(
            {
                "priority": str(priority),
                "row_id": row_id,
                "title": gate["title"],
                "source_urls": scout["public_source_candidates"],
                "metadata_refreshed_at_utc": meta["refreshed_at_utc"],
                "artifact_surface_hint": meta["artifact_surface_hint"],
                "source_kinds": meta["source_kinds"],
                "metadata_quality": metadata_quality(meta),
                "public_surface_observed": compact(observed, 360),
                "weak_rules_pressure": weak_rules_for(meta),
                "first_blocker": first_blocker(meta, gate),
                "next_no_download_check": gate["gate_review_focus"],
                "denominator_status": "not_denominator_pending_detailed_check",
                "admission_status": "not_admitted",
                "compute_release": "no",
                "paper_action": "do_not_update_C14_until_row_check_passes",
            }
        )
        priority += 1
    return rows


def render_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def render_markdown(rows: list[dict[str, str]]) -> str:
    refreshed_at = sorted({row["metadata_refreshed_at_utc"] for row in rows})[-1] if rows else latest_metadata_refresh()
    c14_count = len(COMPLETED_EXEMPLARS)
    lines = [
        "# E2 False-Promotion Expansion Queue",
        "",
        "> Date: 2026-06-07",
        f"> Source refresh: `{refreshed_at}`",
        f"> Scope: next no-download public-surface checks after the {c14_count}-row C14 baseline.",
        "",
        "## Decision",
        "",
        f"最新 metadata refresh、`E2SCT-011`、`E2SCT-020`、`E2SCT-019` 和 `E2SCT-024` 行级 exemplar 复核，以及 `E2SCT-022`、`E2SCT-023`、`E2SCT-025`、`E2SCT-028` 的详细关闭检查后，C14 `{c14_count}` 行以外还有 `{len(rows)}` 个值得下一轮 no-download 复核的 public-surface rows。`E2SCT-022`、`E2SCT-023`、`E2SCT-025` 和 `E2SCT-028` 已关闭为 support-only / watch-plus / code-public reference，不进入 C14，也不再作为待首轮检查的扩展队列成员；`E2SCT-019` 和 `E2SCT-024` 已成为 C14 false-promotion exemplars。剩余队列只用于扩展 false-promotion corpus 的候选检查，不是 admitted evidence，不是 N50 external denominator，也不释放 GPU/DCU。",
        "",
        f"Do not update the paper C14 selected-row count from `{c14_count}` until a detailed row-level public-surface check turns another row into a clean exemplar and the review packet/codebook are regenerated.",
        "",
        "## Queue",
        "",
        "| Priority | Row | Title | Public surface observed | Weak-rule pressure | First blocker | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        status = f"{row['admission_status']}; {row['denominator_status']}; compute={row['compute_release']}"
        lines.append(
            "| {priority} | `{row_id}` | {title} | {surface} | {rules} | {blocker} | {status} |".format(
                priority=row["priority"],
                row_id=row["row_id"],
                title=row["title"],
                surface=row["public_surface_observed"].replace("|", "/"),
                rules=row["weak_rules_pressure"].replace("|", "/"),
                blocker=row["first_blocker"].replace("|", "/"),
                status=status,
            )
        )
    if not rows:
        lines.append("| - | - | - | - | - | No remaining post-C14 expansion row after the 2026-06-07/2026-06-08 detailed checks. | closed |")
    lines.extend(
        [
            "",
            "## Execution Boundary",
            "",
            "- Use only public metadata, README/raw page text, API tree/catalog metadata, and existing no-download scripts.",
            "- Do not download archives, media payloads, model weights, datasets, or generated responses.",
            "- Do not run GPU/DCU jobs from this queue.",
            "- If a row only restates a known semantic mismatch, close it as bounded support instead of expanding taxonomy.",
            "- If a row becomes a clean false-promotion exemplar, add a dedicated public-surface check first, then regenerate the C14 assets and review bundle.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(rows: list[dict[str, str]]) -> None:
    OUT_CSV.write_text(render_csv(rows), encoding="utf-8")
    OUT_MD.write_text(render_markdown(rows), encoding="utf-8")
    print(f"Wrote {OUT_CSV} with {len(rows)} row(s)")
    print(f"Wrote {OUT_MD}")


def check_outputs(rows: list[dict[str, str]]) -> None:
    expected_csv = render_csv(rows)
    expected_md = render_markdown(rows)
    if not OUT_CSV.exists() or OUT_CSV.read_text(encoding="utf-8") != expected_csv:
        raise SystemExit(f"{OUT_CSV} is stale; run scripts/build_e2_false_promotion_expansion_queue.py")
    if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != expected_md:
        raise SystemExit(f"{OUT_MD} is stale; run scripts/build_e2_false_promotion_expansion_queue.py")
    print("E2 false-promotion expansion queue is current")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated queue outputs without writing")
    args = parser.parse_args()

    rows = build_rows()
    if args.check:
        check_outputs(rows)
    else:
        write_outputs(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
