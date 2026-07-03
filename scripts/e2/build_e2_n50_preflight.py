"""Build the E2 N=50 freeze preflight seed table.

This is not the frozen E2 denominator. It collects distinct candidate surfaces
from existing paper-side corpus files and marks what is still missing before an
external-adjudication freeze.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "papers" / "diffaudit-evidence-paper" / "data"
# GONE - docs/internal/ directory not found
# OUT = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
OUT = ROOT / "outputs" / "e2-n50-freeze-preflight-2026-06-06"  # relocated

SOURCES = [
    "artifact_corpus_v1.csv",
    "artifact_corpus_fixed_search_20260526.csv",
    "artifact_corpus_targeted_artifact_links_20260527.csv",
    "artifact_corpus_broader_source_20260527.csv",
]

GATES = [
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
]

ACTIONABLE_STATUSES = {"candidate_for_freeze_review", "needs_artifact_followup"}
URL_PATTERN = re.compile(r"https?://[^\s)<>\]\"]+")
URL_TRAILING_PUNCTUATION = ".,;`'"
CURRENT_CYCLE_PACKAGE_STATUS = "current_cycle_external_package_no_go"
CURRENT_CYCLE_SOURCE = "v1_review_and_post_c14_expansion_queue_2026_06_07"
CURRENT_CYCLE_NEXT_ACTION = (
    "do not package this seed row for external adjudication in the current cycle; "
    "use e2_false_promotion_expansion_queue_2026_06_07.md and the measurement-route gap board"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def present(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() not in {"", "n/a", "none", "no result"}


def row_id(row: dict[str, str]) -> str:
    return row.get("id") or row.get("batch_id") or row.get("claim_id") or ""


def title(row: dict[str, str]) -> str:
    return row.get("candidate") or row.get("title") or row.get("candidate_name") or ""


def source_url(row: dict[str, str]) -> str:
    return row.get("paper_or_repo_url") or row.get("paper_url") or row.get("source_note") or row.get("source_url") or ""


def artifact_url(row: dict[str, str]) -> str:
    return row.get("artifact_url") or row.get("public_surface") or ""


def observed(row: dict[str, str]) -> str:
    return row.get("observed_public_files") or row.get("artifact_surface") or row.get("artifact_type") or ""


def extract_public_url_candidates(source_value: str) -> str:
    candidates: list[str] = []
    for url in URL_PATTERN.findall(source_value):
        candidates.append(url.rstrip(URL_TRAILING_PUNCTUATION))

    for part in source_value.split(";"):
        note_path = part.strip()
        if not note_path.startswith("docs/"):
            continue
        path = ROOT / note_path
        if not path.exists() or path.suffix.lower() not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for url in URL_PATTERN.findall(text):
            cleaned = url.rstrip(URL_TRAILING_PUNCTUATION)
            if cleaned not in candidates:
                candidates.append(cleaned)
            if len(candidates) >= 8:
                break
    return "; ".join(candidates[:8])


def gate(row: dict[str, str], name: str) -> str:
    return (row.get(name) or "N/A").strip() or "N/A"


def gate_failures(row: dict[str, str]) -> list[str]:
    return [name for name in GATES if gate(row, name) in {"Fail", "N/A"}]


def key_part(value: str | None) -> str:
    if not present(value):
        return ""
    return (value or "").strip().lower()


def canonical_key(source_table: str, row: dict[str, str]) -> str:
    source = key_part(source_url(row))
    artifact = key_part(artifact_url(row))
    source_row_id = key_part(row_id(row))
    label = key_part(title(row))
    if source and artifact:
        return f"source+artifact:{source}|{artifact}"
    if source:
        return f"source:{source}"
    if artifact:
        return f"artifact:{artifact}"
    if source_row_id:
        return f"row:{source_table}:{source_row_id}"
    return f"title:{source_table}:{label}"


def stratum(row: dict[str, str]) -> str:
    return (
        row.get("stratum")
        or row.get("claim_support_level")
        or row.get("inclusion_decision")
        or row.get("source")
        or "unknown"
    )


def seed_status(row: dict[str, str]) -> tuple[str, str]:
    failures = gate_failures(row)
    if not present(source_url(row)):
        return "exclude_no_public_source", "missing public source"
    if not present(artifact_url(row)) and not present(observed(row)):
        return "needs_source_refresh", "no artifact surface observed"
    if len(failures) >= 4:
        return "weak_seed_only", "most gates fail: " + ";".join(failures)
    if "metric_gate" in failures or "evidence_gate" in failures:
        return "needs_artifact_followup", "missing score/response or metric surface"
    if "boundary_gate" in failures or "delta_gate" in failures:
        return "candidate_for_freeze_review", "consumer/delta boundary needs blind review"
    return "candidate_for_freeze_review", "eligible for E2 blind freeze review"


def normalize(source_table: str, row: dict[str, str], index: int) -> dict[str, object]:
    status, blocker = seed_status(row)
    return {
        "e2_seed_id": f"E2S-{index:03d}",
        "source_table": source_table,
        "source_row_id": row_id(row),
        "title": title(row),
        "source_url": source_url(row),
        "artifact_url": artifact_url(row),
        "observed_public_files": observed(row),
        "stratum": stratum(row),
        "seed_status": status,
        "first_freeze_blocker": blocker,
        "needs_external_source_check": int(source_url(row).startswith("docs/evidence/")),
        **{name: gate(row, name) for name in GATES},
    }


def load_seed_rows() -> list[dict[str, object]]:
    by_key: dict[str, dict[str, object]] = {}
    duplicate_notes: list[dict[str, object]] = []
    index = 1
    for source_table in SOURCES:
        for raw in read_csv(DATA / source_table):
            key = canonical_key(source_table, raw)
            if not key:
                continue
            normalized = normalize(source_table, raw, index)
            index += 1
            if key in by_key:
                duplicate_notes.append(
                    {
                        "kept_dedup_key": key,
                        "duplicate_source_table": source_table,
                        "duplicate_source_row_id": row_id(raw),
                        "duplicate_title": title(raw),
                        "dedup_key": key,
                    }
                )
                continue
            by_key[key] = normalized
    rows = list(by_key.values())
    for new_index, row in enumerate(rows, start=1):
        row["e2_seed_id"] = f"E2S-{new_index:03d}"
    for note in duplicate_notes:
        note["kept_seed_id"] = by_key[str(note.pop("kept_dedup_key"))]["e2_seed_id"]
    write_csv(
        OUT / "e2_n50_duplicate_notes.csv",
        duplicate_notes,
        ["kept_seed_id", "duplicate_source_table", "duplicate_source_row_id", "duplicate_title", "dedup_key"],
    )
    return rows


def summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    status_counts = Counter(str(row["seed_status"]) for row in rows)
    stratum_counts = Counter(str(row["stratum"]) for row in rows)
    summary: list[dict[str, object]] = []
    for status, count in sorted(status_counts.items()):
        summary.append(
            {
                "summary_type": "seed_status",
                "label": status,
                "count": count,
                "target_n50_gap_after_candidate_review": max(
                    0, 50 - sum(status_counts[s] for s in ["candidate_for_freeze_review", "needs_artifact_followup"])
                ),
            }
        )
    for label, count in sorted(stratum_counts.items()):
        summary.append(
            {
                "summary_type": "stratum",
                "label": label,
                "count": count,
                "target_n50_gap_after_candidate_review": "",
            }
        )
    return summary


def actionable_queue_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    queue_rows: list[dict[str, object]] = []
    for queue_index, row in enumerate(
        [row for row in rows if row["seed_status"] in ACTIONABLE_STATUSES], start=1
    ):
        needs_source_refresh = int(row["needs_external_source_check"]) == 1
        needs_artifact_followup = row["seed_status"] == "needs_artifact_followup"
        if needs_source_refresh and needs_artifact_followup:
            next_action = "replace local evidence note with public source URL and inspect artifact surface"
            freeze_state = "needs_public_source_and_artifact_followup"
        elif needs_source_refresh:
            next_action = "replace local evidence note with public source URL"
            freeze_state = "needs_public_source_refresh"
        elif needs_artifact_followup:
            next_action = "inspect public artifact surface for score/response or metric packet"
            freeze_state = "needs_artifact_followup"
        else:
            next_action = "prepare blind adjudication row package after duplicate review"
            freeze_state = "ready_for_package_after_duplicate_review"
        public_candidates = extract_public_url_candidates(str(row["source_url"]))
        queue_rows.append(
            {
                "queue_id": f"E2Q-{queue_index:03d}",
                "e2_seed_id": row["e2_seed_id"],
                "source_table": row["source_table"],
                "source_row_id": row["source_row_id"],
                "title": row["title"],
                "source_url": row["source_url"],
                "artifact_url": row["artifact_url"],
                "observed_public_files": row["observed_public_files"],
                "seed_status": row["seed_status"],
                "first_freeze_blocker": row["first_freeze_blocker"],
                "needs_external_source_check": row["needs_external_source_check"],
                "public_source_candidates": public_candidates,
                "freeze_state": freeze_state,
                "next_action": next_action,
                "current_cycle_package_status": CURRENT_CYCLE_PACKAGE_STATUS,
                "current_cycle_next_action": CURRENT_CYCLE_NEXT_ACTION,
                "current_cycle_source": CURRENT_CYCLE_SOURCE,
            }
        )
    return queue_rows


def public_source_refresh_rows(actionable_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        row
        for row in actionable_rows
        if int(row["needs_external_source_check"]) == 1 or not present(str(row["artifact_url"]))
    ]


def write_readme(rows: list[dict[str, object]], summary: list[dict[str, object]]) -> None:
    status_counts = Counter(str(row["seed_status"]) for row in rows)
    candidate_like = status_counts["candidate_for_freeze_review"] + status_counts["needs_artifact_followup"]
    candidate_like_rows = [
        row
        for row in rows
        if row["seed_status"] in {"candidate_for_freeze_review", "needs_artifact_followup"}
    ]
    needs_external_source_refresh = sum(int(row["needs_external_source_check"]) for row in candidate_like_rows)
    n50_gap = max(0, 50 - candidate_like)
    text = [
        "# E2 N=50 Freeze Preflight",
        "",
        "> Date: 2026-06-06",
        "> Scope: internal seed table only; not the frozen E2 denominator.",
        "",
        "This directory collects existing distinct-surface candidates after the v2 blind pilot passed the Go/No-Go gate.",
        "Rows here are seeds for an external-adjudication freeze, not final E2 rows.",
        "",
        "## Outputs",
        "",
        "- `e2_n50_preflight_seeds.csv`",
        "- `e2_n50_preflight_summary.csv`",
        "- `e2_n50_duplicate_notes.csv`",
        "- `e2_n50_actionable_queue.csv`",
        "- `e2_n50_public_source_refresh_queue.csv`",
        "",
        "`e2_n50_actionable_queue.csv` preserves the original seed-preflight view.",
        "For current-cycle package decisions, use its `current_cycle_package_status` and",
        "`current_cycle_next_action` columns plus the post-C14 expansion queue.",
        "",
        "## Current Counts",
        "",
        f"- distinct seed rows: `{len(rows)}`",
        f"- candidate or artifact-followup rows: `{candidate_like}`",
        f"- gap to N=50 after candidate review: `{n50_gap}`",
        f"- candidate/followup rows needing public-source refresh: `{needs_external_source_refresh}`",
        "",
        "## Seed Status Counts",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        text.append(f"- `{status}`: {count}")
    text.extend(
        [
            "",
            "## Current Preflight Verdict",
            "",
            f"This is enough to start freeze-package preparation, but not enough to freeze `E2-20260606-N50`: the actionable candidate/followup pool is `{candidate_like}`, so the preflight still needs `{n50_gap}` additional distinct actionable public surfaces or successful artifact follow-ups before external adjudication packaging.",
            "",
            "## Freeze Boundary",
            "",
            "Before `E2-20260606-N50` can be frozen, each selected row needs a new E2 row id, public-source refresh, duplicate-surface review, and blind adjudication package. Do not pool the current seed denominators as prevalence or reliability evidence.",
            "",
        ]
    )
    (OUT / "README.md").write_text("\n".join(text), encoding="utf-8")


def main() -> int:
    rows = load_seed_rows()
    summary = summary_rows(rows)
    actionable_rows = actionable_queue_rows(rows)
    source_refresh_rows = public_source_refresh_rows(actionable_rows)
    fieldnames = [
        "e2_seed_id",
        "source_table",
        "source_row_id",
        "title",
        "source_url",
        "artifact_url",
        "observed_public_files",
        "stratum",
        "seed_status",
        "first_freeze_blocker",
        "needs_external_source_check",
        *GATES,
    ]
    write_csv(OUT / "e2_n50_preflight_seeds.csv", rows, fieldnames)
    write_csv(OUT / "e2_n50_preflight_summary.csv", summary)
    queue_fieldnames = [
        "queue_id",
        "e2_seed_id",
        "source_table",
        "source_row_id",
        "title",
        "source_url",
        "artifact_url",
        "observed_public_files",
        "seed_status",
        "first_freeze_blocker",
        "needs_external_source_check",
        "public_source_candidates",
        "freeze_state",
        "next_action",
        "current_cycle_package_status",
        "current_cycle_next_action",
        "current_cycle_source",
    ]
    write_csv(OUT / "e2_n50_actionable_queue.csv", actionable_rows, queue_fieldnames)
    write_csv(OUT / "e2_n50_public_source_refresh_queue.csv", source_refresh_rows, queue_fieldnames)
    write_readme(rows, summary)
    print(f"Wrote {OUT} with {len(rows)} distinct seed rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
