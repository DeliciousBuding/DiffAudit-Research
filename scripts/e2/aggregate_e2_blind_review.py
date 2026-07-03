"""Aggregate E2 internal blind review labels.

This script consumes reviewer-filled blind review CSVs and the already-generated
pilot baseline table. Agreement is computed only from blind labels. Baseline
false-promotion summaries are computed only after blind labels are loaded.
"""

from __future__ import annotations

import csv
import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_DIR = ROOT / "docs" / "internal" / "e2-pilot-2026-06-06"

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

BASELINE_RULES = [
    "score_only",
    "code_availability",
    "artifact_availability",
    "paper_claim_artifact_link",
    "metric_code_split",
    "reproducibility_checklist",
    "diffaudit_contract",
]


def read_csv(path: Path) -> list[dict[str, str]]:
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


def review_files(pilot_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in pilot_dir.glob("e2_blind_review_*.csv")
        if path.stem.removeprefix("e2_blind_review_")[:1].isupper()
    )


def validate_reviews(template_rows: list[dict[str, str]], rows: list[dict[str, str]]) -> None:
    expected_ids = {row["pilot_id"] for row in template_rows}
    seen = {(row.get("reviewer", ""), row.get("pilot_id", "")) for row in rows}
    duplicate_count = len(rows) - len(seen)
    if duplicate_count:
        raise SystemExit(f"Duplicate reviewer/pilot labels: {duplicate_count}")
    for row in rows:
        pilot_id = row.get("pilot_id", "")
        if pilot_id not in expected_ids:
            raise SystemExit(f"Unknown pilot_id in blind review: {pilot_id}")
        reviewer = row.get("reviewer", "")
        if not reviewer:
            raise SystemExit(f"Missing reviewer for {pilot_id}")
        for field in GATE_FIELDS:
            value = row.get(field, "")
            if value not in VALID_GATES:
                raise SystemExit(f"Invalid {field}={value!r} for {reviewer}/{pilot_id}")
        wording = row.get(WORDING_FIELD, "")
        if wording not in VALID_WORDING:
            raise SystemExit(f"Invalid allowed_wording={wording!r} for {reviewer}/{pilot_id}")


def cohen_kappa(a_values: list[str], b_values: list[str]) -> float | None:
    if len(a_values) != len(b_values) or not a_values:
        return None
    labels = sorted(set(a_values) | set(b_values))
    observed = sum(1 for a, b in zip(a_values, b_values) if a == b) / len(a_values)
    a_counts = Counter(a_values)
    b_counts = Counter(b_values)
    expected = sum((a_counts[label] / len(a_values)) * (b_counts[label] / len(b_values)) for label in labels)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def majority(values: list[str]) -> tuple[str, bool]:
    counts = Counter(values)
    top_count = max(counts.values())
    winners = sorted(label for label, count in counts.items() if count == top_count)
    return winners[0], len(winners) > 1


def false_promotion(decision: str, wording: str) -> int:
    return int(decision == "admit" and wording in {"candidate-only", "blocked"})


def bounded_mismatch(decision: str, wording: str) -> int:
    return int(decision == "admit" and wording == "bounded-support")


def false_block(decision: str, wording: str) -> int:
    return int(decision == "block" and wording == "admitted")


def aggregate_agreement(
    template_rows: list[dict[str, str]], review_rows: list[dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in review_rows:
        by_id[row["pilot_id"]].append(row)

    combined: list[dict[str, object]] = []
    disagreements: list[dict[str, object]] = []
    per_field_summary: list[dict[str, object]] = []

    for template in template_rows:
        pilot_id = template["pilot_id"]
        labels = sorted(by_id[pilot_id], key=lambda row: row["reviewer"])
        reviewers = [row["reviewer"] for row in labels]
        combined_row: dict[str, object] = {
            "pilot_id": pilot_id,
            "title": template["title"],
            "n_reviewers": len(labels),
            "reviewers": ";".join(reviewers),
        }
        for field in REVIEW_FIELDS:
            values = [row[field] for row in labels]
            if values:
                maj, tied = majority(values)
                combined_row[f"{field}_majority"] = maj
                combined_row[f"{field}_tie"] = int(tied)
                combined_row[f"{field}_all_agree"] = int(len(set(values)) == 1)
                combined_row[f"{field}_labels"] = ";".join(f"{row['reviewer']}={row[field]}" for row in labels)
                if len(set(values)) > 1:
                    disagreements.append(
                        {
                            "pilot_id": pilot_id,
                            "title": template["title"],
                            "field": field,
                            "labels": combined_row[f"{field}_labels"],
                            "first_blockers": "; ".join(
                                f"{row['reviewer']}={row.get('first_blocker', '')}" for row in labels
                            ),
                            "notes": " | ".join(f"{row['reviewer']}: {row.get('notes', '')}" for row in labels),
                        }
                    )
            else:
                combined_row[f"{field}_majority"] = ""
                combined_row[f"{field}_tie"] = ""
                combined_row[f"{field}_all_agree"] = ""
                combined_row[f"{field}_labels"] = ""
        combined.append(combined_row)

    reviewers = sorted({row["reviewer"] for row in review_rows})
    for field in REVIEW_FIELDS:
        complete_items = [
            row for row in combined if int(row["n_reviewers"]) == len(reviewers) and len(reviewers) >= 1
        ]
        all_agree = sum(int(row.get(f"{field}_all_agree") or 0) for row in complete_items)
        raw_all_agreement = all_agree / len(complete_items) if complete_items else 0.0
        pair_kappas: list[float] = []
        for left, right in combinations(reviewers, 2):
            left_values = []
            right_values = []
            for pilot_id in [row["pilot_id"] for row in template_rows]:
                labels = {row["reviewer"]: row for row in by_id[pilot_id]}
                if left in labels and right in labels:
                    left_values.append(labels[left][field])
                    right_values.append(labels[right][field])
            kappa = cohen_kappa(left_values, right_values)
            if kappa is not None:
                pair_kappas.append(kappa)
        per_field_summary.append(
            {
                "field": field,
                "n_reviewers": len(reviewers),
                "n_complete_rows": len(complete_items),
                "raw_all_reviewer_agreement": round(raw_all_agreement, 4),
                "mean_pairwise_kappa": round(sum(pair_kappas) / len(pair_kappas), 4) if pair_kappas else "",
                "min_pairwise_kappa": round(min(pair_kappas), 4) if pair_kappas else "",
                "max_pairwise_kappa": round(max(pair_kappas), 4) if pair_kappas else "",
            }
        )

    return combined, disagreements, per_field_summary


def baseline_summary(combined: list[dict[str, object]], pilot_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows_by_id = {row["pilot_id"]: row for row in pilot_rows}
    reviewed = [
        row
        for row in combined
        if row.get("allowed_wording_majority") in VALID_WORDING and int(row.get("n_reviewers") or 0) >= 1
    ]
    total = len(reviewed)
    summary: list[dict[str, object]] = []
    for rule in BASELINE_RULES:
        admits = 0
        bounded_support = 0
        false_promotions = 0
        false_blocks = 0
        bounded_mismatches = 0
        examples = []
        for review in reviewed:
            pilot_id = str(review["pilot_id"])
            wording = str(review["allowed_wording_majority"])
            decision = rows_by_id[pilot_id][f"{rule}_decision"]
            admits += int(decision == "admit")
            bounded_support += int(decision == "bounded-support")
            false_promotions += false_promotion(decision, wording)
            false_blocks += false_block(decision, wording)
            bounded_mismatches += bounded_mismatch(decision, wording)
            if false_promotion(decision, wording) and len(examples) < 5:
                examples.append(pilot_id)
        summary.append(
            {
                "rule": rule,
                "pilot_scope": "internal_blind_pilot_not_external_adjudication",
                "n_reviewed_rows": total,
                "admit_count": admits,
                "bounded_support_count": bounded_support,
                "false_promotion_count": false_promotions,
                "false_promotion_rate": round(false_promotions / total, 4) if total else "",
                "false_block_count": false_blocks,
                "bounded_mismatch_count": bounded_mismatches,
                "example_false_promotion_pilot_ids": ";".join(examples),
            }
        )
    return summary


def write_readme_update(
    pilot_dir: Path,
    reviewers: list[str],
    agreement: list[dict[str, object]],
    blind_summary: list[dict[str, object]],
    disagreements: list[dict[str, object]],
) -> None:
    wording_row = next(row for row in agreement if row["field"] == WORDING_FIELD)
    consumer_row = next(row for row in agreement if row["field"] == "consumer_or_delta_gate")
    provenance_row = next(row for row in agreement if row["field"] == "provenance_gate")
    top_rules = sorted(
        [row for row in blind_summary if row["rule"] != "diffaudit_contract"],
        key=lambda row: float(row["false_promotion_rate"] or 0),
        reverse=True,
    )[:3]
    nontrivial_rules = [
        row
        for row in blind_summary
        if row["rule"]
        in {
            "score_only",
            "code_availability",
            "artifact_availability",
            "paper_claim_artifact_link",
            "metric_code_split",
            "reproducibility_checklist",
        }
        and int(row["false_promotion_count"]) > 0
    ]
    wording_agreement = float(wording_row["raw_all_reviewer_agreement"])
    pilot_decision = (
        "revise-codebook-rerun-small-pilot"
        if wording_agreement < 0.70
        else "go-freeze-n50-preflight"
    )
    reason = (
        f"allowed wording agreement is `{wording_row['raw_all_reviewer_agreement']}`, above the protocol target `>= 0.70`; "
        f"false-promotion examples exist for `{len(nontrivial_rules)}` weaker baselines. Proceed to `N=50` freeze preflight, while keeping this pilot marked internal and non-external."
    )
    if wording_agreement < 0.70:
        reason = (
            f"allowed wording agreement is `{wording_row['raw_all_reviewer_agreement']}`; protocol target is `>= 0.70`. "
            f"False-promotion examples exist for `{len(nontrivial_rules)}` weaker baselines, but provenance and consumer/delta gate disagreements need codebook refinement before `N=50` freeze."
        )
    if len(nontrivial_rules) < 2:
        pilot_decision = "revise-baselines-rerun-small-pilot"
        reason = (
            f"allowed wording agreement is `{wording_row['raw_all_reviewer_agreement']}`, but only `{len(nontrivial_rules)}` weaker baselines produced false-promotion examples. "
            "Revise the baseline set or pilot strata before `N=50` freeze."
        )
    lines = [
        "# E2 Blind Review Aggregation",
        "",
        "> Date: 2026-06-06",
        "> Scope: internal blind pilot only; not external adjudication evidence.",
        "",
        f"Reviewers loaded: `{', '.join(reviewers) if reviewers else 'none'}`.",
        "",
        "## Agreement",
        "",
        f"- allowed wording raw all-reviewer agreement: `{wording_row['raw_all_reviewer_agreement']}`",
        f"- allowed wording mean pairwise kappa: `{wording_row['mean_pairwise_kappa']}`",
        f"- provenance gate raw all-reviewer agreement: `{provenance_row['raw_all_reviewer_agreement']}`",
        f"- consumer/delta gate raw all-reviewer agreement: `{consumer_row['raw_all_reviewer_agreement']}`",
        f"- disagreement cells: `{len(disagreements)}`",
        "",
        "## Pilot Go/No-Go",
        "",
        f"- decision: `{pilot_decision}`",
        f"- reason: {reason}",
        "",
        "## Blind-Majority False-Promotion Stress Check",
        "",
    ]
    for row in top_rules:
        lines.append(
            f"- `{row['rule']}`: {row['false_promotion_count']}/{row['n_reviewed_rows']} "
            f"(rate `{row['false_promotion_rate']}`), examples `{row['example_false_promotion_pilot_ids']}`"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This aggregation is an internal pilot-calibration artifact. It can support the E2 Go/No-Go decision, but it is not an external adjudication result and must not be cited as paper evidence.",
            "",
        ]
    )
    (pilot_dir / "e2_blind_review_aggregation.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilot-dir",
        type=Path,
        default=DEFAULT_PILOT_DIR,
        help="Directory containing blind review CSV files and where aggregation outputs are written.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Reviewer-facing template CSV. Defaults to <pilot-dir>/e2_blind_review_template.csv.",
    )
    parser.add_argument(
        "--pilot-rows",
        type=Path,
        default=None,
        help="Baseline pilot rows CSV. Defaults to <pilot-dir>/e2_false_promotion_pilot_rows.csv.",
    )
    parser.add_argument(
        "--min-reviewers",
        type=int,
        default=1,
        help="Minimum number of reviewers required before writing aggregation outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pilot_dir = args.pilot_dir.resolve()
    template = (args.template or (pilot_dir / "e2_blind_review_template.csv")).resolve()
    pilot_rows_path = (args.pilot_rows or (pilot_dir / "e2_false_promotion_pilot_rows.csv")).resolve()

    template_rows = read_csv(template)
    all_review_rows: list[dict[str, str]] = []
    for path in review_files(pilot_dir):
        all_review_rows.extend(read_csv(path))
    validate_reviews(template_rows, all_review_rows)
    reviewers = sorted({row["reviewer"] for row in all_review_rows})
    if len(reviewers) < args.min_reviewers:
        raise SystemExit(
            f"Only {len(reviewers)} reviewer(s) found in {pilot_dir}; "
            f"need at least {args.min_reviewers}."
        )

    combined, disagreements, agreement = aggregate_agreement(template_rows, all_review_rows)
    pilot_rows = read_csv(pilot_rows_path)
    blind_summary = baseline_summary(combined, pilot_rows)

    write_csv(pilot_dir / "e2_blind_review_combined.csv", combined)
    write_csv(pilot_dir / "e2_blind_review_agreement.csv", agreement)
    write_csv(
        pilot_dir / "e2_blind_review_disagreements.csv",
        disagreements,
        ["pilot_id", "title", "field", "labels", "first_blockers", "notes"],
    )
    write_csv(pilot_dir / "e2_blind_review_baseline_summary.csv", blind_summary)
    write_readme_update(pilot_dir, reviewers, agreement, blind_summary, disagreements)
    print(f"Aggregated {len(reviewers)} reviewer(s), {len(all_review_rows)} labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
