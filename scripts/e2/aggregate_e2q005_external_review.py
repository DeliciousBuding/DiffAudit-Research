"""Aggregate E2Q-005 external-style single-row review labels."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"

GATE_FIELDS = [
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "provenance_gate",
    "consumer_or_delta_gate",
]
WORDING_FIELD = "allowed_wording"
REVIEW_FIELDS = GATE_FIELDS + [WORDING_FIELD]
VALID_GATES = {"Pass", "Partial", "Fail", "N/A"}
VALID_WORDING = {"admitted", "bounded-support", "candidate-only", "blocked"}
EXPECTED_HEADER = [
    "pilot_id",
    "title",
    "source_url",
    "artifact_url",
    "observed_public_files",
    "consumer_question",
    "reviewer",
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "provenance_gate",
    "consumer_or_delta_gate",
    "allowed_wording",
    "first_blocker",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if rows and list(rows[0].keys()) != EXPECTED_HEADER:
        raise SystemExit(f"{path.name} header drifted")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def review_files(preflight: Path) -> list[Path]:
    return sorted(preflight.glob("e2q005_external_style_review_[A-Z]_2026_06_06.csv"))


def majority(values: list[str]) -> tuple[str, bool]:
    counts = Counter(values)
    top_count = max(counts.values())
    winners = sorted(label for label, count in counts.items() if count == top_count)
    return winners[0], len(winners) > 1


def validate(rows: list[dict[str, str]]) -> None:
    seen_reviewers: set[str] = set()
    for row in rows:
        reviewer = row.get("reviewer", "")
        if not reviewer:
            raise SystemExit("Missing reviewer label")
        if reviewer in seen_reviewers:
            raise SystemExit(f"Duplicate reviewer: {reviewer}")
        seen_reviewers.add(reviewer)
        if row.get("pilot_id") != "E2Q-005":
            raise SystemExit(f"Unexpected pilot_id for {reviewer}: {row.get('pilot_id')}")
        for field in GATE_FIELDS:
            if row[field] not in VALID_GATES:
                raise SystemExit(f"Invalid {field}={row[field]!r} for reviewer {reviewer}")
        if row[WORDING_FIELD] not in VALID_WORDING:
            raise SystemExit(f"Invalid allowed_wording={row[WORDING_FIELD]!r} for reviewer {reviewer}")


def aggregate(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    reviewers = [row["reviewer"] for row in rows]
    summary: list[dict[str, object]] = []
    disagreements: list[dict[str, object]] = []
    for field in REVIEW_FIELDS:
        labels = [row[field] for row in rows]
        maj, tied = majority(labels)
        summary_row = {
            "pilot_id": "E2Q-005",
            "field": field,
            "n_reviewers": len(rows),
            "reviewers": ";".join(reviewers),
            "majority": maj,
            "tie": int(tied),
            "all_agree": int(len(set(labels)) == 1),
            "labels": ";".join(f"{row['reviewer']}={row[field]}" for row in rows),
        }
        summary.append(summary_row)
        if len(set(labels)) > 1:
            disagreements.append(
                {
                    "pilot_id": "E2Q-005",
                    "field": field,
                    "labels": summary_row["labels"],
                    "first_blockers": "; ".join(
                        f"{row['reviewer']}={row.get('first_blocker', '')}" for row in rows
                    ),
                    "notes": " | ".join(f"{row['reviewer']}: {row.get('notes', '')}" for row in rows),
                }
            )
    return summary, disagreements


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    summary: list[dict[str, object]],
    disagreements: list[dict[str, object]],
) -> None:
    wording = next(row for row in summary if row["field"] == WORDING_FIELD)
    decision = "accept_feature_packet_review_row" if wording["majority"] == "bounded-support" else "hold_support_only"
    lines = [
        "# E2Q-005 External-Style Review Aggregation",
        "",
        "> Date: 2026-06-06",
        "> Scope: single-row feature-packet review only; not N50 denominator evidence.",
        "",
        f"Reviewers loaded: `{', '.join(row['reviewer'] for row in rows)}`.",
        "",
        "## Majority Labels",
        "",
    ]
    for field in REVIEW_FIELDS:
        row = next(item for item in summary if item["field"] == field)
        lines.append(f"- {field}: `{row['majority']}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{decision}`.",
            "",
            "`E2Q-005` can be used as a provenance-limited feature-packet review row",
            "for a false-promotion study because reviewers agree that the public",
            "supplement identity, tensor roles, hash alignment, and replay metrics are",
            "useful. It remains outside N50/external denominator evidence because",
            "target checkpoint identity and raw sample IDs are absent.",
            "",
            "## Boundary",
            "",
            "- Do not call this an admitted row.",
            "- Do not call this N50 evidence or external adjudication.",
            "- Do not call this black-box response evidence.",
            "- Do not release GPU/DCU work from this review.",
        ]
    )
    if disagreements:
        lines.extend(["", "## Disagreements", ""])
        for item in disagreements:
            lines.append(f"- `{item['field']}`: {item['labels']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-dir", type=Path, default=PREFLIGHT)
    parser.add_argument("--min-reviewers", type=int, default=2)
    args = parser.parse_args()

    all_rows: list[dict[str, str]] = []
    for path in review_files(args.preflight_dir):
        rows = read_csv(path)
        if len(rows) != 1:
            raise SystemExit(f"{path.name} must contain exactly one row")
        all_rows.extend(rows)
    validate(all_rows)
    if len(all_rows) < args.min_reviewers:
        raise SystemExit(f"Only {len(all_rows)} reviewer(s) found; need {args.min_reviewers}")

    summary, disagreements = aggregate(all_rows)
    write_csv(
        args.preflight_dir / "e2q005_external_style_review_aggregation_2026_06_06.csv",
        summary,
        ["pilot_id", "field", "n_reviewers", "reviewers", "majority", "tie", "all_agree", "labels"],
    )
    write_csv(
        args.preflight_dir / "e2q005_external_style_review_disagreements_2026_06_06.csv",
        disagreements,
        ["pilot_id", "field", "labels", "first_blockers", "notes"],
    )
    write_markdown(
        args.preflight_dir / "e2q005_external_style_review_aggregation_2026_06_06.md",
        all_rows,
        summary,
        disagreements,
    )
    print(f"Aggregated E2Q-005 external-style reviews: {len(all_rows)} reviewer(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
