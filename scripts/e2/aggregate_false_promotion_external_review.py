"""Aggregate C14 false-promotion external-review labels.

The C14 packet is prepared reviewer material. This script validates reviewer
CSV files filled from ``papers/diffaudit-evidence-paper/data/false_promotion_external_review_template.csv`` and
summarizes majority labels, disagreements, and comparison against the author
adjudication key. It never fabricates labels: with ``--check`` and no reviewer
files, it only validates that the packet is ready to receive labels.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers" / "diffaudit-evidence-paper"
DEFAULT_REVIEW_DIR = PAPER / "build" / "false_promotion_external_review_labels"
DEFAULT_OUTPUT_DIR = PAPER / "build"

GATE_FIELDS = [
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
]
REVIEW_FIELDS = GATE_FIELDS + ["false_promotion_verdict", "compute_release"]
TEMPLATE_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "reviewer",
    "gate_allowed_values",
    "verdict_allowed_values",
    "compute_release_allowed_values",
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
    "false_promotion_verdict",
    "first_blocker",
    "allowed_wording",
    "compute_release",
    "notes",
]
BLINDED_PACKET_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "weak_surface_family",
    "weak_rules_under_test",
    "public_surface_observation",
    "review_question",
    "packet_status",
]
ADJUDICATION_KEY_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "author_false_promotion_verdict",
    "author_contract_blocker",
    "author_allowed_wording",
    "author_compute_release",
    "author_no_compute_release",
    "key_status",
]
VALID_GATES = {"Pass", "Partial", "Fail", "N/A"}
VALID_VERDICTS = {
    "false_promotion_control",
    "semantic_boundary_block",
    "artifact_surface_block",
    "needs_external_adjudication",
    "invalid_row",
}
VALID_COMPUTE_RELEASE = {"no", "yes_with_full_contract"}
EXCLUDED_VERDICTS = {"needs_external_adjudication", "invalid_row"}
REVIEW_FILE_GLOBS = [
    "false_promotion_external_review_*.csv",
    "c14_false_promotion_review_*.csv",
]
DECLARATION_FILE_GLOBS = [
    "REVIEWER_DECLARATION_*.md",
    "reviewer_declaration_*.md",
    "false_promotion_external_review_*_declaration.md",
]
DECLARATION_YES_FIELDS = [
    "used_same_reviewer_id",
    "no_post_label_author_key_before_labels",
    "no_llm_ai_assistance",
    "no_reviewer_discussion",
    "did_not_create_c14_materials",
    "no_large_download_or_execution",
    "understands_no_post_submission_revision",
]
DECLARATION_REQUIRED_FIELDS = ["reviewer_id", *DECLARATION_YES_FIELDS, "signature", "date"]
REVIEW_FILENAME_PATTERNS = [
    re.compile(r"^false_promotion_external_review_(?P<reviewer>.+)\.csv$"),
    re.compile(r"^c14_false_promotion_review_(?P<reviewer>.+)\.csv$"),
]
DECLARATION_FILENAME_PATTERNS = [
    re.compile(r"^REVIEWER_DECLARATION_(?P<reviewer>.+)\.md$"),
    re.compile(r"^reviewer_declaration_(?P<reviewer>.+)\.md$"),
    re.compile(r"^false_promotion_external_review_(?P<reviewer>.+)_declaration\.md$"),
]
REVIEWER_ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,31}$")
PACKET_STATUS_FIELDS = [
    "packet_label_readiness",
    "reviewer_count_status",
    "n_reviewers",
    "min_reviewers",
    "reliability_min_reviewers",
    "min_mean_kappa",
    "min_field_kappa",
    "require_no_majority_ties",
    "majority_resolution_status",
    "reliability_threshold_status",
    "declaration_status",
    "reliability_threshold_met",
    "external_label_aggregation_available",
    "completed_external_adjudication_allowed",
    "reliability_claim_allowed",
    "compute_release_allowed",
    "allowed_claim_scope",
]
LABEL_DEPENDENT_OUTPUTS = [
    "false_promotion_external_review_declarations.csv",
    "false_promotion_external_review_aggregation.csv",
    "false_promotion_external_review_disagreements.csv",
    "false_promotion_external_review_agreement.csv",
    "false_promotion_external_review_author_key_comparison.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_header(path: Path, rows: list[dict[str, str]], header: list[str], errors: list[str]) -> None:
    actual = list(rows[0].keys()) if rows else []
    require(actual == header, f"{path} header drifted: {actual}", errors)


def load_packet_inputs(paper: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    template = read_csv(paper / "data" / "false_promotion_external_review_template.csv")
    blinded = read_csv(paper / "data" / "false_promotion_blinded_review_packet.csv")
    key = read_csv(paper / "data" / "false_promotion_adjudication_key.csv")
    return template, blinded, key


def validate_packet_inputs(
    template_rows: list[dict[str, str]],
    blinded_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    errors: list[str],
) -> None:
    require(len(template_rows) == 13, "template must contain exactly thirteen rows", errors)
    require(len(blinded_rows) == 13, "blinded packet must contain exactly thirteen rows", errors)
    require(len(key_rows) == 13, "author answer key must contain exactly thirteen rows", errors)

    if template_rows:
        require_header(PAPER / "data" / "false_promotion_external_review_template.csv", template_rows, TEMPLATE_FIELDS, errors)
    if blinded_rows:
        require_header(PAPER / "data" / "false_promotion_blinded_review_packet.csv", blinded_rows, BLINDED_PACKET_FIELDS, errors)
    if key_rows:
        require_header(PAPER / "data" / "false_promotion_adjudication_key.csv", key_rows, ADJUDICATION_KEY_FIELDS, errors)

    template_ids = {row.get("source_row_id", "") for row in template_rows}
    blinded_ids = {row.get("source_row_id", "") for row in blinded_rows}
    key_ids = {row.get("source_row_id", "") for row in key_rows}
    require(template_ids == blinded_ids == key_ids, "template/blinded/key source_row_id sets differ", errors)

    template_review_ids = {row.get("review_id", "") for row in template_rows}
    blinded_review_ids = {row.get("review_id", "") for row in blinded_rows}
    key_review_ids = {row.get("review_id", "") for row in key_rows}
    require(
        template_review_ids == blinded_review_ids == key_review_ids,
        "template/blinded/key review_id sets differ",
        errors,
    )

    for row in template_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(row.get("gate_allowed_values") == "Pass|Partial|Fail|N/A", f"{row_id} gate values drifted", errors)
        require(
            set(row.get("verdict_allowed_values", "").split("|")) == VALID_VERDICTS,
            f"{row_id} verdict values drifted",
            errors,
        )
        require(
            set(row.get("compute_release_allowed_values", "").split("|")) == VALID_COMPUTE_RELEASE,
            f"{row_id} compute-release values drifted",
            errors,
        )
        for field in ["reviewer", *REVIEW_FIELDS, "first_blocker", "allowed_wording", "notes"]:
            require(row.get(field, "") == "", f"{row_id} template field {field} must stay blank", errors)

    for row in blinded_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(
            row.get("packet_status") == "blocker_blinded_prepared_not_adjudicated",
            f"{row_id} blinded packet status drifted",
            errors,
        )
        require("weak-rule promotion" in row.get("review_question", ""), f"{row_id} lost weak-rule question", errors)

    for row in key_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(
            row.get("author_false_promotion_verdict") in VALID_VERDICTS,
            f"{row_id} author verdict is invalid",
            errors,
        )
        require(row.get("author_compute_release") == "no", f"{row_id} author compute release must stay no", errors)
        require(row.get("author_no_compute_release") == "1", f"{row_id} lost author no-compute flag", errors)
        require(row.get("key_status") == "author_key_not_external_label", f"{row_id} key status drifted", errors)


def discover_review_files(review_dir: Path, explicit_files: list[Path]) -> list[Path]:
    if explicit_files:
        return sorted(path.resolve() for path in explicit_files)
    files: list[Path] = []
    if review_dir.exists():
        for pattern in REVIEW_FILE_GLOBS:
            files.extend(review_dir.glob(pattern))
    return sorted(set(path.resolve() for path in files if path.is_file()))


def discover_declaration_files(review_dir: Path, explicit_files: list[Path]) -> list[Path]:
    if explicit_files:
        return sorted(path.resolve() for path in explicit_files)
    files: list[Path] = []
    if review_dir.exists():
        for pattern in DECLARATION_FILE_GLOBS:
            files.extend(review_dir.glob(pattern))
    return sorted(set(path.resolve() for path in files if path.is_file()))


def parse_declaration(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_ -]+)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip().lower().replace("-", "_").replace(" ", "_")
        parsed[key] = match.group(2).strip()
    return parsed


def reviewer_id_from_review_filename(path: Path) -> str:
    for pattern in REVIEW_FILENAME_PATTERNS:
        match = pattern.match(path.name)
        if match:
            return match.group("reviewer")
    return ""


def reviewer_id_from_declaration_filename(path: Path) -> str:
    for pattern in DECLARATION_FILENAME_PATTERNS:
        match = pattern.match(path.name)
        if match:
            return match.group("reviewer")
    return ""


def require_valid_reviewer_id(reviewer_id: str, label: str, errors: list[str]) -> None:
    require(
        bool(REVIEWER_ID_RE.fullmatch(reviewer_id)),
        f"{label} {reviewer_id!r} must match [a-z][a-z0-9-]{{2,31}}",
        errors,
    )


def validate_declarations(
    declaration_files: list[Path],
    reviewers: list[str],
    errors: list[str],
) -> list[dict[str, str]]:
    if not reviewers:
        return []
    require(
        bool(declaration_files),
        "reviewer declaration files are required when reviewer CSVs are present",
        errors,
    )

    rows: list[dict[str, str]] = []
    seen_reviewers: set[str] = set()
    expected_reviewers = set(reviewers)
    for path in declaration_files:
        parsed = parse_declaration(path)
        reviewer_id = parsed.get("reviewer_id", "").strip()
        require(reviewer_id != "", f"{path} missing reviewer_id", errors)
        if reviewer_id:
            require_valid_reviewer_id(reviewer_id, f"{path} reviewer_id", errors)
        filename_reviewer = reviewer_id_from_declaration_filename(path)
        require(
            filename_reviewer != "",
            f"{path} filename must be REVIEWER_DECLARATION_<reviewer-id>.md",
            errors,
        )
        if filename_reviewer:
            require_valid_reviewer_id(filename_reviewer, f"{path} filename reviewer", errors)
            require(
                reviewer_id == filename_reviewer,
                f"{path} filename reviewer {filename_reviewer!r} does not match declaration reviewer_id {reviewer_id!r}",
                errors,
            )
        require(reviewer_id in expected_reviewers, f"{path} reviewer_id {reviewer_id!r} has no matching CSV reviewer", errors)
        require(reviewer_id not in seen_reviewers, f"duplicate declaration for reviewer {reviewer_id}", errors)
        seen_reviewers.add(reviewer_id)
        for field in DECLARATION_REQUIRED_FIELDS:
            require(parsed.get(field, "").strip() != "", f"{path} missing declaration field {field}", errors)
        for field in DECLARATION_YES_FIELDS:
            require(
                parsed.get(field, "").strip().lower() == "yes",
                f"{path} declaration field {field} must be yes",
                errors,
            )
        rows.append(
            {
                "reviewer": reviewer_id,
                "declaration_file": str(path),
                "declaration_status": "valid_independence_attestation",
                **{field: parsed.get(field, "") for field in DECLARATION_REQUIRED_FIELDS},
            }
        )
    missing = sorted(expected_reviewers - seen_reviewers)
    require(not missing, f"missing reviewer declarations for: {', '.join(missing)}", errors)
    extra = sorted(seen_reviewers - expected_reviewers)
    require(not extra, f"declarations without matching reviewer CSV: {', '.join(extra)}", errors)
    return sorted(rows, key=lambda row: row["reviewer"])


def validate_review_rows(
    review_files: list[Path],
    expected_rows: list[dict[str, str]],
    errors: list[str],
) -> list[dict[str, str]]:
    expected_by_review_id = {row["review_id"]: row for row in expected_rows}
    expected_review_ids = set(expected_by_review_id)
    expected_source_ids = {row["source_row_id"] for row in expected_rows}
    all_rows: list[dict[str, str]] = []

    for path in review_files:
        rows = read_csv(path)
        if rows:
            require_header(path, rows, TEMPLATE_FIELDS, errors)
        require(len(rows) == len(expected_rows), f"{path} must contain exactly {len(expected_rows)} rows", errors)
        file_reviewers = {row.get("reviewer", "").strip() for row in rows if row.get("reviewer", "").strip()}
        require(len(file_reviewers) == 1, f"{path} must contain exactly one non-empty reviewer label", errors)
        filename_reviewer = reviewer_id_from_review_filename(path)
        require(filename_reviewer != "", f"{path} filename must be false_promotion_external_review_<reviewer-id>.csv", errors)
        if filename_reviewer:
            require_valid_reviewer_id(filename_reviewer, f"{path} filename reviewer", errors)
        if len(file_reviewers) == 1 and filename_reviewer:
            file_reviewer = next(iter(file_reviewers))
            require_valid_reviewer_id(file_reviewer, f"{path} CSV reviewer", errors)
            require(
                file_reviewer == filename_reviewer,
                f"{path} filename reviewer {filename_reviewer!r} does not match CSV reviewer {file_reviewer!r}",
                errors,
            )
        for row_index, (row, expected) in enumerate(zip(rows, expected_rows, strict=False), start=1):
            require(
                row.get("review_id", "") == expected["review_id"]
                and row.get("source_row_id", "") == expected["source_row_id"],
                f"{path} row order changed at position {row_index}",
                errors,
            )
        file_review_ids = {row.get("review_id", "") for row in rows}
        require(file_review_ids == expected_review_ids, f"{path} review_id set differs from template", errors)
        all_rows.extend(rows)

    seen_pairs: set[tuple[str, str]] = set()
    by_reviewer: dict[str, set[str]] = defaultdict(set)
    for row in all_rows:
        reviewer = row.get("reviewer", "").strip()
        review_id = row.get("review_id", "")
        source_row_id = row.get("source_row_id", "")
        require(reviewer != "", f"{source_row_id or review_id} missing reviewer", errors)
        require(review_id in expected_review_ids, f"{reviewer}/{review_id} is not in the template", errors)
        require(source_row_id in expected_source_ids, f"{reviewer}/{source_row_id} is not in the template", errors)
        if review_id in expected_by_review_id:
            expected = expected_by_review_id[review_id]
            require(source_row_id == expected["source_row_id"], f"{reviewer}/{review_id} source_row_id drifted", errors)
            require(row.get("title", "") == expected["title"], f"{reviewer}/{review_id} title drifted", errors)
        pair = (reviewer, review_id)
        require(pair not in seen_pairs, f"duplicate reviewer/review_id label: {reviewer}/{review_id}", errors)
        seen_pairs.add(pair)
        by_reviewer[reviewer].add(review_id)

        for field in GATE_FIELDS:
            require(row.get(field, "") in VALID_GATES, f"{reviewer}/{source_row_id} invalid {field}", errors)
        require(
            row.get("false_promotion_verdict", "") in VALID_VERDICTS,
            f"{reviewer}/{source_row_id} invalid false_promotion_verdict",
            errors,
        )
        require(
            row.get("compute_release", "") in VALID_COMPUTE_RELEASE,
            f"{reviewer}/{source_row_id} invalid compute_release",
            errors,
        )
        if row.get("compute_release", "") == "yes_with_full_contract":
            release_blockers = [
                field
                for field in [
                    "target_gate",
                    "split_gate",
                    "score_or_response_gate",
                    "metric_gate",
                    "provenance_gate",
                    "consumer_boundary_gate",
                ]
                if row.get(field, "") != "Pass"
            ]
            require(
                not release_blockers,
                f"{reviewer}/{source_row_id} compute_release=yes_with_full_contract but contract gates are not all Pass: {', '.join(release_blockers)}",
                errors,
            )
        require(row.get("allowed_wording", "").strip() != "", f"{reviewer}/{source_row_id} missing allowed_wording", errors)
        require(row.get("first_blocker", "").strip() != "", f"{reviewer}/{source_row_id} missing first_blocker", errors)

    for reviewer, ids in by_reviewer.items():
        require(ids == expected_review_ids, f"reviewer {reviewer} does not cover all selected rows", errors)
    return all_rows


def majority(values: list[str]) -> tuple[str, bool]:
    counts = Counter(values)
    top_count = max(counts.values())
    winners = sorted(label for label, count in counts.items() if count == top_count)
    tied = len(winners) > 1
    return ("UNRESOLVED_TIE" if tied else winners[0]), tied


def cohen_kappa(left_values: list[str], right_values: list[str]) -> float | None:
    if len(left_values) != len(right_values) or not left_values:
        return None
    labels = sorted(set(left_values) | set(right_values))
    observed = sum(left == right for left, right in zip(left_values, right_values)) / len(left_values)
    left_counts = Counter(left_values)
    right_counts = Counter(right_values)
    expected = sum(
        (left_counts[label] / len(left_values)) * (right_counts[label] / len(right_values))
        for label in labels
    )
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def reviewer_count_status(
    n_reviewers: int,
    min_reviewers: int,
    reliability_min_reviewers: int,
) -> str:
    if n_reviewers == 0:
        return "none"
    if n_reviewers < min_reviewers:
        return f"below_min_{min_reviewers}"
    if n_reviewers < reliability_min_reviewers:
        return f"min_{min_reviewers}_external_label_aggregation_available"
    return "three_plus_reliability_protocol_available"


def reliability_threshold_status(
    n_reviewers: int,
    mean_pairwise_kappa: float | None,
    min_pairwise_kappa: float | None,
    reliability_min_reviewers: int,
    min_mean_kappa: float,
    min_field_kappa: float,
) -> str:
    if n_reviewers < reliability_min_reviewers:
        return f"not_applicable_below_{reliability_min_reviewers}"
    if mean_pairwise_kappa is None or min_pairwise_kappa is None:
        return "failed_kappa_undefined_degenerate_distribution"
    if mean_pairwise_kappa >= min_mean_kappa and min_pairwise_kappa >= min_field_kappa:
        return "passed"
    return "failed"


def build_packet_status_rows(
    reviewers: list[str],
    combined: list[dict[str, object]],
    agreement: list[dict[str, object]],
    min_reviewers: int,
    reliability_min_reviewers: int,
    min_mean_kappa: float,
    min_field_kappa: float,
    require_no_majority_ties: bool,
    declaration_status: str = "not_checked",
) -> list[dict[str, object]]:
    n_reviewers = len(reviewers)
    n_rows = len({str(row.get("review_id", "")) for row in combined if row.get("review_id")})
    if n_reviewers == 0:
        majority_resolution_status = "no_labels"
    elif any(row["external_review_status"] == "unresolved_majority_tie" for row in combined):
        majority_resolution_status = "unresolved_majority_tie"
    elif any(row["external_review_status"] == "excluded_pending_resolution" for row in combined):
        majority_resolution_status = "excluded_pending_resolution"
    else:
        majority_resolution_status = "resolved"

    field_statuses = [str(row.get("reliability_threshold_status", "")) for row in agreement]
    if n_reviewers < reliability_min_reviewers:
        packet_reliability_status = f"not_applicable_below_{reliability_min_reviewers}"
    elif not field_statuses:
        packet_reliability_status = "not_evaluated_no_agreement_rows"
    elif require_no_majority_ties and majority_resolution_status == "unresolved_majority_tie":
        packet_reliability_status = "failed_majority_ties"
    elif all(status == "passed" for status in field_statuses):
        packet_reliability_status = "passed"
    else:
        packet_reliability_status = "failed"

    if n_reviewers == 0:
        allowed_claim_scope = "packet_ready_only"
    elif n_reviewers < min_reviewers:
        allowed_claim_scope = "packet_ready_only_below_min_reviewers"
    elif majority_resolution_status != "resolved":
        allowed_claim_scope = f"reviewer_labels_available_unresolved_selected_{n_rows}_rows_only"
    elif packet_reliability_status == "passed":
        allowed_claim_scope = f"external_label_aggregation_selected_{n_rows}_rows_only_reliability_thresholds_met_not_adjudication"
    else:
        allowed_claim_scope = f"external_label_aggregation_selected_{n_rows}_rows_only_reliability_claim_not_allowed"

    return [
        {
            "packet_label_readiness": (
                "prepared_no_reviewer_csvs" if n_reviewers == 0 else "review_csvs_available"
            ),
            "reviewer_count_status": reviewer_count_status(
                n_reviewers,
                min_reviewers,
                reliability_min_reviewers,
            ),
            "n_reviewers": n_reviewers,
            "min_reviewers": min_reviewers,
            "reliability_min_reviewers": reliability_min_reviewers,
            "min_mean_kappa": min_mean_kappa,
            "min_field_kappa": min_field_kappa,
            "require_no_majority_ties": int(require_no_majority_ties),
            "majority_resolution_status": majority_resolution_status,
            "reliability_threshold_status": packet_reliability_status,
            "declaration_status": declaration_status,
            "reliability_threshold_met": int(packet_reliability_status == "passed"),
            "external_label_aggregation_available": int(n_reviewers >= min_reviewers),
            "completed_external_adjudication_allowed": 0,
            "reliability_claim_allowed": 0,
            "compute_release_allowed": 0,
            "allowed_claim_scope": allowed_claim_scope,
        }
    ]


def aggregate_reviews(
    template_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    review_rows: list[dict[str, str]],
    min_reviewers: int,
    reliability_min_reviewers: int,
    min_mean_kappa: float,
    min_field_kappa: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    by_review_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in review_rows:
        by_review_id[row["review_id"]].append(row)

    key_by_review_id = {row["review_id"]: row for row in key_rows}
    combined: list[dict[str, object]] = []
    disagreements: list[dict[str, object]] = []
    author_comparison: list[dict[str, object]] = []

    for template in template_rows:
        review_id = template["review_id"]
        labels = sorted(by_review_id[review_id], key=lambda row: row["reviewer"])
        reviewers = [row["reviewer"] for row in labels]
        combined_row: dict[str, object] = {
            "review_id": review_id,
            "source_row_id": template["source_row_id"],
            "title": template["title"],
            "n_reviewers": len(labels),
            "reviewers": ";".join(reviewers),
        }
        has_tie = False
        has_disagreement = False
        for field in REVIEW_FIELDS:
            values = [row[field] for row in labels]
            maj, tied = majority(values)
            all_agree = len(set(values)) == 1
            has_tie = has_tie or tied
            has_disagreement = has_disagreement or not all_agree
            combined_row[f"{field}_majority"] = maj
            combined_row[f"{field}_tie"] = int(tied)
            combined_row[f"{field}_all_agree"] = int(all_agree)
            combined_row[f"{field}_labels"] = ";".join(f"{row['reviewer']}={row[field]}" for row in labels)
            if not all_agree:
                disagreements.append(
                    {
                        "review_id": review_id,
                        "source_row_id": template["source_row_id"],
                        "title": template["title"],
                        "field": field,
                        "labels": combined_row[f"{field}_labels"],
                        "first_blockers": "; ".join(
                            f"{row['reviewer']}={row.get('first_blocker', '')}" for row in labels
                        ),
                        "notes": " | ".join(f"{row['reviewer']}: {row.get('notes', '')}" for row in labels),
                    }
                )

        verdict = str(combined_row["false_promotion_verdict_majority"])
        compute_release = str(combined_row["compute_release_majority"])
        if len(labels) < min_reviewers:
            status = "insufficient_reviewers"
        elif has_tie:
            status = "unresolved_majority_tie"
        elif verdict in EXCLUDED_VERDICTS:
            status = "excluded_pending_resolution"
        elif compute_release == "yes_with_full_contract":
            status = "compute_release_claim_requires_contract_audit"
        elif has_disagreement:
            status = "majority_resolved_with_disagreements_selected_rows_only"
        else:
            status = "unanimous_resolved_selected_rows_only"
        combined_row["external_review_status"] = status
        combined.append(combined_row)

        key = key_by_review_id[review_id]
        author_comparison.append(
            {
                "review_id": review_id,
                "source_row_id": template["source_row_id"],
                "title": template["title"],
                "external_false_promotion_verdict_majority": verdict,
                "author_false_promotion_verdict": key["author_false_promotion_verdict"],
                "author_verdict_match": int(verdict == key["author_false_promotion_verdict"]),
                "external_compute_release_majority": compute_release,
                "author_compute_release": key["author_compute_release"],
                "author_compute_release_match": int(compute_release == key["author_compute_release"]),
                "author_contract_blocker": key["author_contract_blocker"],
            }
        )

    reviewers = sorted({row["reviewer"] for row in review_rows})
    agreement: list[dict[str, object]] = []
    for field in REVIEW_FIELDS:
        all_agree_count = sum(int(row[f"{field}_all_agree"]) for row in combined)
        pair_kappas: list[float] = []
        for left, right in combinations(reviewers, 2):
            left_values: list[str] = []
            right_values: list[str] = []
            for template in template_rows:
                labels = {row["reviewer"]: row for row in by_review_id[template["review_id"]]}
                left_values.append(labels[left][field])
                right_values.append(labels[right][field])
            kappa = cohen_kappa(left_values, right_values)
            if kappa is not None:
                pair_kappas.append(kappa)
        mean_kappa = sum(pair_kappas) / len(pair_kappas) if pair_kappas else None
        min_kappa = min(pair_kappas) if pair_kappas else None
        threshold_status = reliability_threshold_status(
            len(reviewers),
            mean_kappa,
            min_kappa,
            reliability_min_reviewers,
            min_mean_kappa,
            min_field_kappa,
        )
        agreement.append(
            {
                "field": field,
                "n_reviewers": len(reviewers),
                "n_complete_rows": len(template_rows),
                "raw_all_reviewer_agreement": round(all_agree_count / len(template_rows), 4),
                "mean_pairwise_kappa": round(mean_kappa, 4) if mean_kappa is not None else "",
                "min_pairwise_kappa": round(min_kappa, 4) if min_kappa is not None else "",
                "max_pairwise_kappa": round(max(pair_kappas), 4) if pair_kappas else "",
                "min_mean_kappa": min_mean_kappa,
                "min_field_kappa": min_field_kappa,
                "reliability_threshold_status": threshold_status,
                "reliability_threshold_met": int(threshold_status == "passed"),
                "reliability_status": (
                    "three_plus_reviewers_and_thresholds_passed_not_automatically_paper_claim"
                    if threshold_status == "passed"
                    else "three_plus_reviewers_but_thresholds_failed_not_reliability_claim"
                    if len(reviewers) >= 3
                    else "not_inter_rater_reliability_evidence"
                ),
            }
        )

    return combined, disagreements, agreement, author_comparison


def write_markdown(
    path: Path,
    reviewers: list[str],
    combined: list[dict[str, object]],
    disagreements: list[dict[str, object]],
    agreement: list[dict[str, object]],
    packet_status: list[dict[str, object]],
) -> None:
    verdict_counts = Counter(str(row["false_promotion_verdict_majority"]) for row in combined)
    statuses = Counter(str(row["external_review_status"]) for row in combined)
    packet = packet_status[0]
    lines = [
        "# C14 False-Promotion External Review Aggregation",
        "",
        "> Scope: reviewer-label aggregation for the prepared C14 packet.",
        "> Boundary: not N50 denominator evidence, not field prevalence, not completed external adjudication, not compute release, and not inter-rater reliability unless an explicit three-reviewer reliability protocol is reported.",
        "",
        f"Reviewers loaded: `{', '.join(reviewers)}`.",
        f"Rows aggregated: `{len(combined)}`.",
        f"Disagreement cells: `{len(disagreements)}`.",
        "",
        "## Packet Status",
        "",
        f"- Packet label readiness: `{packet['packet_label_readiness']}`",
        f"- Reviewer count status: `{packet['reviewer_count_status']}`",
        f"- Declaration status: `{packet['declaration_status']}`",
        f"- Majority resolution status: `{packet['majority_resolution_status']}`",
        f"- Reliability threshold status: `{packet['reliability_threshold_status']}`",
        f"- Allowed claim scope: `{packet['allowed_claim_scope']}`",
        f"- Completed external adjudication allowed: `{packet['completed_external_adjudication_allowed']}`",
        f"- Reliability claim allowed: `{packet['reliability_claim_allowed']}`",
        f"- Compute release allowed: `{packet['compute_release_allowed']}`",
        "",
        "## Majority Verdict Counts",
        "",
    ]
    for verdict, count in sorted(verdict_counts.items()):
        lines.append(f"- `{verdict}`: `{count}`")
    lines.extend(["", "## Row Status Counts", ""])
    for status, count in sorted(statuses.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Agreement", ""])
    for row in agreement:
        lines.append(
            f"- `{row['field']}`: all-reviewer agreement `{row['raw_all_reviewer_agreement']}`, "
            f"mean pairwise kappa `{row['mean_pairwise_kappa']}`, "
            f"threshold `{row['reliability_threshold_status']}`, status `{row['reliability_status']}`"
        )
    if disagreements:
        lines.extend(["", "## Disagreements", ""])
        for row in disagreements[:12]:
            lines.append(f"- `{row['source_row_id']}` / `{row['field']}`: {row['labels']}")
        if len(disagreements) > 12:
            lines.append(f"- Additional disagreement cells: `{len(disagreements) - 12}`")
    lines.extend(
        [
            "",
            "## Reporting Boundary",
            "",
            "These outputs summarize reviewer-filled templates. Majority labels can support a future external-label statement only for the supplied reviewers and the selected rows. Rows labeled `needs_external_adjudication` or `invalid_row` remain excluded until resolved. The author-key comparison is disagreement analysis, not an external label. The generated packet status keeps completed adjudication, reliability claims, and compute release disabled until a separate protocol and paper wording explicitly justify them.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_no_label_markdown(path: Path, packet_status: list[dict[str, object]]) -> None:
    packet = packet_status[0]
    lines = [
        "# C14 False-Promotion External Review Status",
        "",
        "> Scope: packet-readiness status before independent reviewer CSVs are returned.",
        "> Boundary: this is not external adjudication, not reviewer reliability evidence, not an N50 denominator, not field prevalence, not admitted evidence, and not compute release.",
        "",
        "No reviewer CSVs were loaded. The C14 packet is ready to receive labels, but no external-label aggregation exists yet.",
        "",
        "## Packet Status",
        "",
        f"- Packet label readiness: `{packet['packet_label_readiness']}`",
        f"- Reviewer count status: `{packet['reviewer_count_status']}`",
        f"- Declaration status: `{packet['declaration_status']}`",
        f"- Majority resolution status: `{packet['majority_resolution_status']}`",
        f"- Reliability threshold status: `{packet['reliability_threshold_status']}`",
        f"- Allowed claim scope: `{packet['allowed_claim_scope']}`",
        f"- External label aggregation available: `{packet['external_label_aggregation_available']}`",
        f"- Completed external adjudication allowed: `{packet['completed_external_adjudication_allowed']}`",
        f"- Reliability claim allowed: `{packet['reliability_claim_allowed']}`",
        f"- Compute release allowed: `{packet['compute_release_allowed']}`",
        "",
        "## Next Required Evidence",
        "",
        # GONE - build subdirectory not found; re-run build pipeline to regenerate
        # "Place one completed thirteen-row reviewer CSV and one matching reviewer declaration per reviewer under `papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/`, or pass them with `--review-file` and `--declaration-file`.",
        "Place completed reviewer CSVs via --review-file and --declaration-file. The build/false_promotion_external_review_labels/ directory has been removed.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_no_label_outputs(
    output_dir: Path,
    min_reviewers: int,
    reliability_min_reviewers: int,
    min_mean_kappa: float,
    min_field_kappa: float,
    require_no_majority_ties: bool,
) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in LABEL_DEPENDENT_OUTPUTS:
        stale_path = output_dir / filename
        if stale_path.exists():
            stale_path.unlink()
    packet_status = build_packet_status_rows(
        [],
        [],
        [],
        min_reviewers,
        reliability_min_reviewers,
        min_mean_kappa,
        min_field_kappa,
        require_no_majority_ties,
        "not_checked_no_reviewer_csvs",
    )
    write_csv(
        output_dir / "false_promotion_external_review_packet_status.csv",
        packet_status,
        PACKET_STATUS_FIELDS,
    )
    write_no_label_markdown(output_dir / "false_promotion_external_review_aggregation.md", packet_status)
    return packet_status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, default=PAPER)
    parser.add_argument("--review-dir", type=Path, default=DEFAULT_REVIEW_DIR)
    parser.add_argument("--review-file", type=Path, action="append", default=[])
    parser.add_argument("--declaration-file", type=Path, action="append", default=[])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--min-reviewers", type=int, default=2)
    parser.add_argument("--reliability-min-reviewers", type=int, default=3)
    parser.add_argument("--min-mean-kappa", type=float, default=0.6)
    parser.add_argument("--min-field-kappa", type=float, default=0.5)
    parser.add_argument("--require-no-majority-ties", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate packet inputs and any discovered reviewer files. Does not require reviewer files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    template_rows, blinded_rows, key_rows = load_packet_inputs(args.paper_dir)
    validate_packet_inputs(template_rows, blinded_rows, key_rows, errors)

    review_files = discover_review_files(args.review_dir, args.review_file)
    review_rows = validate_review_rows(review_files, template_rows, errors) if review_files else []
    reviewers = sorted({row["reviewer"] for row in review_rows})
    declaration_files = discover_declaration_files(args.review_dir, args.declaration_file)
    if declaration_files and not review_rows:
        errors.append("reviewer declaration files require matching reviewer CSVs")
    declaration_rows = validate_declarations(declaration_files, reviewers, errors) if review_rows else []
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not review_rows:
        packet_status = build_packet_status_rows(
            [],
            [],
            [],
            args.min_reviewers,
            args.reliability_min_reviewers,
            args.min_mean_kappa,
            args.min_field_kappa,
            args.require_no_majority_ties,
            "not_checked_no_reviewer_csvs",
        )
        message = (
            "C14 false-promotion aggregation check passed: packet inputs are valid; "
            "packet_label_readiness=prepared_no_reviewer_csvs; "
            "reviewer_count_status=none; allowed_claim_scope=packet_ready_only."
        )
        if args.check:
            print(message)
            return 0
        write_no_label_outputs(
            args.output_dir,
            args.min_reviewers,
            args.reliability_min_reviewers,
            args.min_mean_kappa,
            args.min_field_kappa,
            args.require_no_majority_ties,
        )
        print(
            f"{message} Wrote status-only outputs to {args.output_dir}; "
            f"completed_external_adjudication_allowed={packet_status[0]['completed_external_adjudication_allowed']}; "
            f"reliability_claim_allowed={packet_status[0]['reliability_claim_allowed']}; "
            f"compute_release_allowed={packet_status[0]['compute_release_allowed']}."
        )
        return 0

    if len(reviewers) < args.min_reviewers:
        print(f"ERROR: only {len(reviewers)} reviewer(s) found; need at least {args.min_reviewers}")
        return 1

    combined, disagreements, agreement, author_comparison = aggregate_reviews(
        template_rows,
        key_rows,
        review_rows,
        args.min_reviewers,
        args.reliability_min_reviewers,
        args.min_mean_kappa,
        args.min_field_kappa,
    )
    packet_status = build_packet_status_rows(
        reviewers,
        combined,
        agreement,
        args.min_reviewers,
        args.reliability_min_reviewers,
        args.min_mean_kappa,
        args.min_field_kappa,
        args.require_no_majority_ties,
        "valid_independence_attestation",
    )

    if args.check:
        print(
            f"C14 false-promotion aggregation check passed: "
            f"{len(reviewers)} reviewer(s), {len(review_rows)} labels; "
            f"majority_resolution_status={packet_status[0]['majority_resolution_status']}; "
            f"reliability_threshold_status={packet_status[0]['reliability_threshold_status']}; "
            f"allowed_claim_scope={packet_status[0]['allowed_claim_scope']}."
        )
        return 0

    output_dir = args.output_dir
    write_csv(
        output_dir / "false_promotion_external_review_packet_status.csv",
        packet_status,
        PACKET_STATUS_FIELDS,
    )
    write_csv(
        output_dir / "false_promotion_external_review_declarations.csv",
        declaration_rows,
        [
            "reviewer",
            "declaration_file",
            "declaration_status",
            *DECLARATION_REQUIRED_FIELDS,
        ],
    )
    write_csv(
        output_dir / "false_promotion_external_review_aggregation.csv",
        combined,
        [
            "review_id",
            "source_row_id",
            "title",
            "n_reviewers",
            "reviewers",
            *[f"{field}_{suffix}" for field in REVIEW_FIELDS for suffix in ["majority", "tie", "all_agree", "labels"]],
            "external_review_status",
        ],
    )
    write_csv(
        output_dir / "false_promotion_external_review_disagreements.csv",
        disagreements,
        ["review_id", "source_row_id", "title", "field", "labels", "first_blockers", "notes"],
    )
    write_csv(
        output_dir / "false_promotion_external_review_agreement.csv",
        agreement,
        [
            "field",
            "n_reviewers",
            "n_complete_rows",
            "raw_all_reviewer_agreement",
            "mean_pairwise_kappa",
            "min_pairwise_kappa",
            "max_pairwise_kappa",
            "min_mean_kappa",
            "min_field_kappa",
            "reliability_threshold_status",
            "reliability_threshold_met",
            "reliability_status",
        ],
    )
    write_csv(
        output_dir / "false_promotion_external_review_author_key_comparison.csv",
        author_comparison,
        [
            "review_id",
            "source_row_id",
            "title",
            "external_false_promotion_verdict_majority",
            "author_false_promotion_verdict",
            "author_verdict_match",
            "external_compute_release_majority",
            "author_compute_release",
            "author_compute_release_match",
            "author_contract_blocker",
        ],
    )
    write_markdown(
        output_dir / "false_promotion_external_review_aggregation.md",
        reviewers,
        combined,
        disagreements,
        agreement,
        packet_status,
    )
    print(f"Aggregated C14 false-promotion external reviews: {len(reviewers)} reviewer(s), {len(review_rows)} labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
