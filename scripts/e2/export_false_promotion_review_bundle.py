"""Export the C14 false-promotion external-style review bundle.

The bundle is a reviewer-material packet only. It prepares the row packet,
template, rule summary, figure, and codebook for external labeling, but it does
not turn the thirteen rows into completed adjudication, reliability evidence, an
N50 denominator, or compute-release evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


ZIP_ROOT = "diffaudit-false-promotion-review"
ZIP_TIMESTAMP = (2026, 6, 7, 0, 0, 0)
POST_LABEL_ZIP_NAME = "diffaudit-false-promotion-post-label-key.zip"
PAPER_RELATIVE_INPUTS = [
    ("blinded_row_packet", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_blinded_review_packet.csv"),
    ("blank_template", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_external_review_template.csv"),
    ("adjudication_key", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_adjudication_key.csv"),
    ("author_keyed_row_packet", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_external_review_packet.csv"),
    ("row_trace", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_row_trace.csv"),
    ("rule_summary", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_rule_summary.csv"),
    ("author_gate_matrix", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_author_gate_matrix.csv"),
    ("author_gate_summary", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_gate_summary.csv"),
    ("source_rows", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_exemplars.csv"),
    ("claim_trace", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_trace.csv"),
    ("source_provenance", "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/source_provenance.csv"),
    ("claim_register", "claim_register.md"),
    ("codebook", "versions/direction-a-false-promotion-audit-codebook.md"),
    ("launch_protocol", "versions/direction-a-c14-external-review-launch-protocol.md"),
    ("figure", "figures/false_promotion_exemplars.pdf"),
    ("author_gate_figure", "figures/false_promotion_gate_matrix.pdf"),
]
BLANK_REVIEW_FIELDS = [
    "reviewer",
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
AUTHOR_GATE_MATRIX_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "label_source",
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
    "author_false_promotion_verdict",
    "first_blocking_gate",
    "gate_rationale",
    "compute_release",
    "matrix_boundary",
]
AUTHOR_GATE_SUMMARY_FIELDS = [
    "gate",
    "outcome",
    "count",
    "selected_row_count",
    "boundary_note",
]
AUTHOR_GATE_VALUES = {"Pass", "Partial", "Fail", "N/A"}
FALSE_PROMOTION_VERDICT_VALUES = {
    "false_promotion_control",
    "semantic_boundary_block",
    "artifact_surface_block",
    "needs_external_adjudication",
    "invalid_row",
}
COMPUTE_RELEASE_VALUES = {"no", "yes_with_full_contract"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PRIVATE_SURFACE_PATTERNS = [
    r"(?<![A-Za-z0-9_])[A-Za-z]:(?:\\\\|\\)[A-Za-z0-9_. -]",
    r"\\Users\\[A-Za-z0-9_. -]",
    r"/home/[A-Za-z0-9_. -]",
    r"/mnt/[A-Za-z0-9_. -]",
    r"OPENAI_API_KEY",
    r"sk-[A-Za-z0-9_-]{12,}",
]
TEXT_SUFFIXES = {".csv", ".md", ".txt"}
TRACE_EVIDENCE_FIELDS = [
    ("source_check_md", "source_check_md_sha256", "row_evidence_note"),
    ("source_check_csv", "source_check_csv_sha256", "row_evidence_table"),
]
AUTHOR_KEYED_CATEGORIES = {
    "adjudication_key",
    "author_keyed_row_packet",
    "author_gate_matrix",
    "author_gate_summary",
    "author_gate_figure",
    "claim_register",
    "claim_trace",
    "figure",
    "rule_summary",
    "row_trace",
    "source_provenance",
    "source_rows",
}
AUTHOR_KEYED_EVIDENCE_CATEGORIES = {
    "row_evidence_note",
    "row_evidence_table",
}
PRE_LABEL_FORBIDDEN_BASENAMES = {
    "claim_register.md",
    "claim_trace.csv",
    "false_promotion_adjudication_key.csv",
    "false_promotion_author_gate_matrix.csv",
    "false_promotion_exemplars.csv",
    "false_promotion_exemplars.pdf",
    "false_promotion_external_review_packet.csv",
    "false_promotion_gate_matrix.pdf",
    "false_promotion_gate_summary.csv",
    "false_promotion_rule_summary.csv",
    "source_provenance.csv",
}


def archive_name_for(category: str, rel_path: str) -> str:
    if category in AUTHOR_KEYED_EVIDENCE_CATEGORIES:
        return f"{ZIP_ROOT}/post-label-author-key/evidence-notes/{Path(rel_path).name}"
    if category in AUTHOR_KEYED_CATEGORIES:
        return f"{ZIP_ROOT}/post-label-author-key/{Path(rel_path).name}"
    return f"{ZIP_ROOT}/{rel_path}"


def is_post_label_item(item: "BundleItem") -> bool:
    return item.archive_name.startswith(f"{ZIP_ROOT}/post-label-author-key/")


@dataclass(frozen=True)
class BundleItem:
    category: str
    rel_path: str
    source_path: Path
    archive_name: str
    size_bytes: int
    sha256: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["category", "source_path", "archive_name", "size_bytes", "sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def scan_text(path: Path, errors: list[str]) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in PRIVATE_SURFACE_PATTERNS:
        require(
            not re.search(pattern, text, flags=re.IGNORECASE),
            f"{path.name} contains private-surface pattern: {pattern}",
            errors,
        )


def validate_inputs(paper: Path, errors: list[str]) -> list[BundleItem]:
    repo_root = paper.parents[1]
    packet = paper / "data" / "false_promotion_external_review_packet.csv"
    blinded_packet = paper / "data" / "false_promotion_blinded_review_packet.csv"
    adjudication_key = paper / "data" / "false_promotion_adjudication_key.csv"
    template = paper / "data" / "false_promotion_external_review_template.csv"
    row_trace = paper / "data" / "false_promotion_row_trace.csv"
    author_gate_matrix = paper / "data" / "false_promotion_author_gate_matrix.csv"
    author_gate_summary = paper / "data" / "false_promotion_gate_summary.csv"
    codebook = paper / "versions" / "direction-a-false-promotion-audit-codebook.md"
    launch_protocol = paper / "versions" / "direction-a-c14-external-review-launch-protocol.md"

    packet_rows = read_csv(packet) if packet.exists() else []
    blinded_rows = read_csv(blinded_packet) if blinded_packet.exists() else []
    key_rows = read_csv(adjudication_key) if adjudication_key.exists() else []
    template_rows = read_csv(template) if template.exists() else []
    trace_rows = read_csv(row_trace) if row_trace.exists() else []
    matrix_rows = read_csv(author_gate_matrix) if author_gate_matrix.exists() else []
    gate_summary_rows = read_csv(author_gate_summary) if author_gate_summary.exists() else []
    require(len(packet_rows) == 13, "review packet must contain exactly thirteen rows", errors)
    require(len(blinded_rows) == 13, "blinded review packet must contain exactly thirteen rows", errors)
    require(len(key_rows) == 13, "adjudication key must contain exactly thirteen rows", errors)
    require(len(template_rows) == 13, "review template must contain exactly thirteen rows", errors)
    require(len(trace_rows) == 13, "row trace must contain exactly thirteen rows", errors)
    require(len(matrix_rows) == 13, "author gate matrix must contain exactly thirteen rows", errors)
    require(len(gate_summary_rows) == 28, "author gate summary must contain seven gates x four outcomes", errors)
    id_sets = {
        "author packet": {row.get("review_id", "") for row in packet_rows},
        "blinded packet": {row.get("review_id", "") for row in blinded_rows},
        "adjudication key": {row.get("review_id", "") for row in key_rows},
        "template": {row.get("review_id", "") for row in template_rows},
        "row trace": {row.get("review_id", "") for row in trace_rows},
        "author gate matrix": {row.get("review_id", "") for row in matrix_rows},
    }
    first_name, first_set = next(iter(id_sets.items()))
    for name, id_set in id_sets.items():
        require(id_set == first_set, f"{first_name}/{name} review_id sets differ", errors)

    for row in packet_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(row.get("packet_status") == "prepared_not_adjudicated", f"{row_id} is not prepared_not_adjudicated", errors)
        require(row.get("reviewer", "") == "", f"{row_id} packet reviewer field must stay blank", errors)
        require(row.get("external_decision", "") == "", f"{row_id} packet external_decision must stay blank", errors)
        require(row.get("external_notes", "") == "", f"{row_id} packet external_notes must stay blank", errors)
        require(row.get("source_no_compute_release") == "1", f"{row_id} lost source_no_compute_release", errors)
        require("weak-rule promotion" in row.get("review_question", ""), f"{row_id} lost false-promotion question", errors)

    for row in blinded_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(list(row.keys()) == BLINDED_PACKET_FIELDS, f"{row_id} blinded packet columns drifted", errors)
        require(
            row.get("packet_status") == "blocker_blinded_prepared_not_adjudicated",
            f"{row_id} is not blocker_blinded_prepared_not_adjudicated",
            errors,
        )
        require("weak-rule promotion" in row.get("review_question", ""), f"{row_id} lost neutral review question", errors)

    for row in key_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(list(row.keys()) == ADJUDICATION_KEY_FIELDS, f"{row_id} adjudication key columns drifted", errors)
        require(row.get("author_false_promotion_verdict") in FALSE_PROMOTION_VERDICT_VALUES,
                f"{row_id} has invalid author verdict", errors)
        require(row.get("author_compute_release") == "no", f"{row_id} author compute release must be no", errors)
        require(row.get("author_no_compute_release") == "1", f"{row_id} lost author_no_compute_release", errors)
        require(row.get("key_status") == "author_key_not_external_label", f"{row_id} key status drifted", errors)

    for row in template_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(row.get("gate_allowed_values") == "Pass|Partial|Fail|N/A", f"{row_id} gate values drifted", errors)
        require(
            set(row.get("verdict_allowed_values", "").split("|")) == FALSE_PROMOTION_VERDICT_VALUES,
            f"{row_id} verdict values drifted",
            errors,
        )
        require(
            set(row.get("compute_release_allowed_values", "").split("|")) == COMPUTE_RELEASE_VALUES,
            f"{row_id} compute-release values drifted",
            errors,
        )
        for field in BLANK_REVIEW_FIELDS:
            require(row.get(field, "") == "", f"{row_id} template {field} must stay blank", errors)

    for row in trace_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(row.get("trace_status") == "no-download public-surface trace", f"{row_id} trace status drifted", errors)
        require("http" in row.get("public_urls", ""), f"{row_id} trace lost public URLs", errors)
        for field in ("source_check_csv_sha256", "source_check_md_sha256", "source_summary_row_sha256"):
            require(bool(SHA256_RE.fullmatch(row.get(field, ""))), f"{row_id} has invalid {field}", errors)

    for row in matrix_rows:
        row_id = row.get("source_row_id", "<missing>")
        require(list(row.keys()) == AUTHOR_GATE_MATRIX_FIELDS, f"{row_id} author gate matrix columns drifted", errors)
        require(row.get("label_source") == "author_key_not_external_label", f"{row_id} gate matrix label source drifted", errors)
        require(row.get("compute_release") == "no", f"{row_id} gate matrix compute release must be no", errors)
        require(
            "not external adjudication" in row.get("matrix_boundary", ""),
            f"{row_id} gate matrix lost no-external-adjudication boundary",
            errors,
        )
        require(
            "denominator evidence" in row.get("matrix_boundary", ""),
            f"{row_id} gate matrix lost no-denominator-evidence boundary",
            errors,
        )
        for field in [
            "target_gate",
            "split_gate",
            "score_or_response_gate",
            "metric_gate",
            "semantic_boundary_gate",
            "provenance_gate",
            "consumer_boundary_gate",
        ]:
            require(row.get(field) in AUTHOR_GATE_VALUES, f"{row_id} has invalid {field}", errors)

    expected_summary_keys = {
        (field, value)
        for field in [
            "target_gate",
            "split_gate",
            "score_or_response_gate",
            "metric_gate",
            "semantic_boundary_gate",
            "provenance_gate",
            "consumer_boundary_gate",
        ]
        for value in AUTHOR_GATE_VALUES
    }
    actual_summary_keys = set()
    for row in gate_summary_rows:
        require(list(row.keys()) == AUTHOR_GATE_SUMMARY_FIELDS, "author gate summary columns drifted", errors)
        actual_summary_keys.add((row.get("gate", ""), row.get("outcome", "")))
        require(row.get("selected_row_count") == "13", "author gate summary selected row count must be 13", errors)
        require(
            "not external reliability or prevalence evidence" in row.get("boundary_note", ""),
            "author gate summary lost no-reliability/prevalence boundary",
            errors,
        )
    require(actual_summary_keys == expected_summary_keys, "author gate summary gate/outcome grid drifted", errors)

    if codebook.exists():
        text = codebook.read_text(encoding="utf-8")
        for phrase in [
            "not completed external adjudication",
            "not inter-rater reliability evidence",
            "not an N50 denominator result",
            "blocker-blinded packet",
            "Leave `compute_release` as `no` unless",
        ]:
            require(phrase in text, f"codebook lost boundary phrase: {phrase}", errors)
    if launch_protocol.exists():
        text = launch_protocol.read_text(encoding="utf-8")
        for phrase in [
            "zero independent labels",
            "not external adjudication",
            "not reviewer reliability evidence",
            "not an N50 external denominator",
            "does not release compute",
            "Do not use LLM/AI-assisted labels",
            "reviewer declaration",
            "false_promotion_external_review_<reviewer-id>.csv",
        ]:
            require(phrase in text, f"launch protocol lost boundary phrase: {phrase}", errors)
    items: list[BundleItem] = []
    archive_names: set[str] = set()
    for category, rel_path in PAPER_RELATIVE_INPUTS:
        source_path = paper / rel_path
        require(source_path.exists(), f"bundle input is missing: {rel_path}", errors)
        if not source_path.exists():
            continue
        scan_text(source_path, errors)
        items.append(
            BundleItem(
                category=category,
                rel_path=rel_path,
                source_path=source_path,
                archive_name=archive_name_for(category, rel_path),
                size_bytes=source_path.stat().st_size,
                sha256=sha256_file(source_path),
            )
        )
        archive_names.add(items[-1].archive_name)
    for row in trace_rows:
        row_id = row.get("source_row_id", "<missing>")
        for path_field, sha_field, category in TRACE_EVIDENCE_FIELDS:
            rel_path = row.get(path_field, "")
            source_path = repo_root / rel_path
            require(source_path.exists(), f"{row_id} trace evidence is missing: {rel_path}", errors)
            if not source_path.exists():
                continue
            scan_text(source_path, errors)
            actual_sha = sha256_file(source_path)
            require(
                actual_sha == row.get(sha_field, ""),
                f"{row_id} {path_field} sha256 differs from row trace",
                errors,
            )
            archive_name = archive_name_for(category, rel_path)
            require(archive_name not in archive_names, f"duplicate bundle archive name: {archive_name}", errors)
            archive_names.add(archive_name)
            items.append(
                BundleItem(
                    category=category,
                    rel_path=rel_path,
                    source_path=source_path,
                    archive_name=archive_name,
                    size_bytes=source_path.stat().st_size,
                    sha256=actual_sha,
                )
            )
    return items


def reviewer_readme() -> bytes:
    text = """# DiffAudit False-Promotion Review Bundle

This packet is prepared reviewer material for the Direction A C14 false-promotion baseline.
It has zero independent labels by default. It is not external adjudication,
not reviewer reliability evidence, not an N50 denominator, not field
prevalence, not admitted score/response evidence, and not compute release.

## Suggested Cover Note

We are asking you to label a small artifact-surface review packet for
DiffAudit. The task is to judge whether weak public-surface rules would
over-promote thirteen selected rows. You are not being asked to reproduce
models, download large or gated assets, train or fine-tune models, query closed
services, or decide whether the paper should be accepted.

Please accept only if you did not create the C14 row checks, author gate labels,
codebook, paper claims, or answer key. Return one completed CSV named
`false_promotion_external_review_<reviewer-id>.csv` and one completed
declaration named `REVIEWER_DECLARATION_<reviewer-id>.md`. Do not use LLM/AI
assistance for labels, verdicts, first blockers, allowed wording, or notes.

## Reviewer Task

You are judging whether a public artifact surface would be over-promoted by
weak shortcut rules. You are not reproducing models, downloading gated assets,
or deciding whether the paper is publishable.

Review exactly thirteen rows. For each row, fill the blank template with:

- seven gate labels: `Pass`, `Partial`, `Fail`, or `N/A`;
- one `false_promotion_verdict`;
- the first blocker that prevents stronger wording;
- the narrowest allowed wording;
- `compute_release`, which should remain `no` unless every contract surface is
  present.

## Primary Reviewer Path

1. Use `data/false_promotion_blinded_review_packet.csv` for row context.
2. Use `REVIEWER_PUBLIC_URLS.csv` and `data/false_promotion_row_trace.csv` to
   follow public URLs. Treat `public_url_note` as launch hygiene only; it flags
   known accessibility issues without changing the row label.
3. Apply the codebook in `versions/direction-a-false-promotion-audit-codebook.md`.
4. Follow `versions/direction-a-c14-external-review-launch-protocol.md` for
   independence, return-file, and stop-rule requirements.
5. Copy `data/false_promotion_external_review_template.csv`, fill the copy, and
   return one CSV named `false_promotion_external_review_<reviewer-id>.csv`.
6. Fill and return `REVIEWER_DECLARATION_<reviewer-id>.md` using the same reviewer id.

Fill the `reviewer` column with the same stable reviewer id in all thirteen
rows, for example `fpr-r01`. Reviewer ids must use lowercase ASCII letters,
digits, and hyphens, start with a letter, and be 3--32 characters long. Do not
change `review_id`, `source_row_id`,
`title`, allowed-value columns, or row order.

## Reviewer Checklist

- Confirm that you can label from the supplied public-surface packet alone.
- Label all thirteen rows before returning the CSV.
- Preserve `review_id`, `source_row_id`, `title`, allowed-value columns, and row
  order.
- Use only `Pass`, `Partial`, `Fail`, or `N/A` for the seven gate columns.
- Choose one allowed `false_promotion_verdict` value per row.
- Write the first blocker that prevents stronger wording.
- Write the narrowest wording the row can support.
- Leave `compute_release` as `no` unless every contract surface is present.
- Do not use LLM/AI assistance for gate labels, verdict labels, first blockers,
  allowed wording, or notes.
- Complete and return `REVIEWER_DECLARATION_<reviewer-id>.md`.
- Stop and report the issue if a row cannot be judged without downloading large
  assets, running upstream code, generating scores, reading the author key, or
  relying on a dead/rate-limited URL.

## Hard-Blind Packet Boundary

This reviewer ZIP intentionally does not contain `post-label-author-key/`.
Same-team comparison material is kept in the separate maintainer-only
`diffaudit-false-promotion-post-label-key.zip` and must not be shared until the
reviewer's labels and declaration are final.

Stop and report the issue if you receive, open, or are asked to inspect any
author-keyed material before submitting labels. That includes the adjudication
key, author gate matrix, author-keyed row packet, source rows, rule summaries,
full row trace, claim trace, source provenance, summary figures, or cached
same-team evidence notes.

## Maintainer Aggregation

After at least two independent reviewer CSV files are returned, place them under
`papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/`  # GONE - build subdirectory not found; re-run build pipeline
and run from the Research repository root:

```powershell
python -X utf8 scripts\\aggregate_false_promotion_external_review.py
```

The aggregation output is reviewer-bounded and row-bounded. It does not create
field prevalence, N50 denominator, compute-release, or paper-acceptance
evidence.

## Boundary

- This packet is not completed external adjudication.
- It is not inter-rater reliability evidence.
- It is not an N50 denominator, prevalence result, admitted score/response
  packet, or compute release.
- Do not use LLM/AI assistance for labels, verdicts, first blockers, allowed
  wording, or notes.
- Do not download large assets, run upstream code, train models, or generate new
  scores while filling the template.
"""
    return text.encode("utf-8")


def reviewer_declaration() -> bytes:
    text = """# Reviewer Declaration

Fill this file and return it as `REVIEWER_DECLARATION_<reviewer-id>.md`.
Use the same `reviewer_id` in the returned CSV's `reviewer` column.
Reviewer ids must use lowercase ASCII letters, digits, and hyphens, start with
a letter, and be 3--32 characters long, for example `fpr-r01`.

reviewer_id:
used_same_reviewer_id: yes
no_post_label_author_key_before_labels: yes
no_llm_ai_assistance: yes
no_reviewer_discussion: yes
did_not_create_c14_materials: yes
no_large_download_or_execution: yes
understands_no_post_submission_revision: yes
signature:
date:

The declaration is machine-checked during aggregation. Keep each yes/no value
exactly `yes` unless the statement is false; if any statement is false, stop and
report the issue instead of returning labels as independent reviewer evidence.
"""
    return text.encode("utf-8")


def reviewer_public_url_note(row: dict[str, str]) -> str:
    if (
        row.get("source_row_id") == "E2SCT-019"
        and "https://github.com/wangli-codes/T2V_MIA/tree/v1.0.1" in row.get("public_urls", "")
    ):
        return (
            "Zenodo record/API are the primary public surfaces; the related "
            "GitHub tag returned 404 during the no-download row check."
        )
    return ""


def reviewer_public_urls(items: list[BundleItem]) -> bytes:
    trace_item = next(item for item in items if item.category == "row_trace")
    trace_rows = read_csv(trace_item.source_path)
    output = io.StringIO()
    fieldnames = ["review_id", "source_row_id", "title", "public_urls", "public_url_note"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in trace_rows:
        writer.writerow(
            {
                "review_id": row["review_id"],
                "source_row_id": row["source_row_id"],
                "title": row["title"],
                "public_urls": row["public_urls"],
                "public_url_note": reviewer_public_url_note(row),
            }
        )
    return output.getvalue().encode("utf-8")


def reviewer_row_trace(items: list[BundleItem]) -> bytes:
    trace_item = next(item for item in items if item.category == "row_trace")
    trace_rows = read_csv(trace_item.source_path)
    output = io.StringIO()
    fieldnames = [
        "review_id",
        "source_row_id",
        "title",
        "observed_at",
        "public_urls",
        "trace_status",
        "review_boundary",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in trace_rows:
        writer.writerow({field: row[field] for field in fieldnames})
    return output.getvalue().encode("utf-8")


def manifest_rows(items: list[BundleItem]) -> list[dict[str, str]]:
    return [
        {
            "category": item.category,
            "source_path": item.rel_path,
            "archive_name": item.archive_name,
            "size_bytes": str(item.size_bytes),
            "sha256": item.sha256,
        }
        for item in sorted(items, key=lambda item: item.archive_name)
    ]


def payload_manifest_row(category: str, source_path: str, archive_name: str, payload: bytes) -> dict[str, str]:
    return {
        "category": category,
        "source_path": source_path,
        "archive_name": archive_name,
        "size_bytes": str(len(payload)),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def review_bundle_manifest_rows(reviewer_items: list[BundleItem], all_items: list[BundleItem]) -> list[dict[str, str]]:
    generated_rows = [
        payload_manifest_row(
            "generated_reviewer_readme",
# RUNTIME - regenerated by running export_false_promotion_review_bundle.py
            "__generated__/REVIEWER_README.md",
            f"{ZIP_ROOT}/REVIEWER_README.md",
            reviewer_readme(),
        ),
        payload_manifest_row(
            "generated_reviewer_declaration",
            "__generated__/REVIEWER_DECLARATION.md",
            f"{ZIP_ROOT}/REVIEWER_DECLARATION.md",
            reviewer_declaration(),
        ),
        payload_manifest_row(
            "generated_reviewer_public_urls",
            "__generated__/REVIEWER_PUBLIC_URLS.csv",
            f"{ZIP_ROOT}/REVIEWER_PUBLIC_URLS.csv",
            reviewer_public_urls(all_items),
        ),
        payload_manifest_row(
            "generated_reviewer_row_trace",
            "__generated__/data/false_promotion_row_trace.csv",
            f"{ZIP_ROOT}/data/false_promotion_row_trace.csv",
            reviewer_row_trace(all_items),
        ),
    ]
    return sorted(
        [*manifest_rows(reviewer_items), *generated_rows],
        key=lambda row: row["archive_name"],
    )


def write_entry(archive: zipfile.ZipFile, archive_name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(archive_name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, payload)


def write_review_zip(
    zip_path: Path,
    reviewer_items: list[BundleItem],
    all_items: list[BundleItem],
    manifest_path: Path,
) -> str:
    readme_payload = reviewer_readme()
    declaration_payload = reviewer_declaration()
    public_urls_payload = reviewer_public_urls(all_items)
    reviewer_trace_payload = reviewer_row_trace(all_items)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in sorted(reviewer_items, key=lambda item: item.archive_name):
            write_entry(archive, item.archive_name, item.source_path.read_bytes())
        for archive_name, payload in [
            (f"{ZIP_ROOT}/REVIEWER_README.md", readme_payload),
            (f"{ZIP_ROOT}/REVIEWER_DECLARATION.md", declaration_payload),
            (f"{ZIP_ROOT}/REVIEWER_PUBLIC_URLS.csv", public_urls_payload),
            (f"{ZIP_ROOT}/data/false_promotion_row_trace.csv", reviewer_trace_payload),
            (f"{ZIP_ROOT}/REVIEW_BUNDLE_MANIFEST.csv", manifest_path.read_bytes()),
        ]:
            write_entry(archive, archive_name, payload)
    return sha256_file(zip_path)


def write_post_label_zip(zip_path: Path, post_label_items: list[BundleItem], manifest_path: Path) -> str:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in sorted(post_label_items, key=lambda item: item.archive_name):
            write_entry(archive, item.archive_name, item.source_path.read_bytes())
        write_entry(
            archive,
            f"{ZIP_ROOT}/post-label-author-key/POST_LABEL_KEY_MANIFEST.csv",
            manifest_path.read_bytes(),
        )
    return sha256_file(zip_path)


def validate_output_zip(
    zip_path: Path,
    manifest_path: Path,
    reviewer_items: list[BundleItem],
    all_items: list[BundleItem],
    post_label_zip_path: Path,
    post_label_manifest_path: Path,
    post_label_items: list[BundleItem],
    errors: list[str],
) -> None:
    sha_path = zip_path.with_name(f"{zip_path.name}.sha256")
    post_label_sha_path = post_label_zip_path.with_name(f"{post_label_zip_path.name}.sha256")
    require(zip_path.exists(), f"review bundle ZIP is missing: {zip_path}", errors)
    require(manifest_path.exists(), f"review bundle manifest is missing: {manifest_path}", errors)
    require(sha_path.exists(), f"review bundle sha256 file is missing: {sha_path}", errors)
    require(post_label_zip_path.exists(), f"post-label key ZIP is missing: {post_label_zip_path}", errors)
    require(post_label_manifest_path.exists(), f"post-label key manifest is missing: {post_label_manifest_path}", errors)
    require(post_label_sha_path.exists(), f"post-label key sha256 file is missing: {post_label_sha_path}", errors)
    if (
        not zip_path.exists()
        or not manifest_path.exists()
        or not post_label_zip_path.exists()
        or not post_label_manifest_path.exists()
    ):
        return

    expected_rows = review_bundle_manifest_rows(reviewer_items, all_items)
    actual_rows = read_csv(manifest_path)
    require(
        actual_rows == expected_rows,
        "review bundle manifest does not match current source or generated reviewer files",
        errors,
    )

    expected_entries = {row["archive_name"] for row in expected_rows}
    expected_entries.add(f"{ZIP_ROOT}/REVIEW_BUNDLE_MANIFEST.csv")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive_entries = set(archive.namelist())
        require(archive_entries == expected_entries, "review bundle ZIP entries do not match current manifest", errors)
        for entry in archive_entries:
            require(
                not entry.startswith(f"{ZIP_ROOT}/post-label-author-key/"),
                f"{entry} must not be included in the hard-blind reviewer ZIP",
                errors,
            )
            require(
                not entry.startswith(f"{ZIP_ROOT}/evidence-notes/"),
                f"{entry} must not be reviewer-facing evidence-notes material",
                errors,
            )
            require(
                Path(entry).name not in PRE_LABEL_FORBIDDEN_BASENAMES,
                f"{entry} exposes author-keyed material before labeling",
                errors,
            )
        for item in reviewer_items:
            payload = archive.read(item.archive_name)
            require(str(len(payload)) == str(item.size_bytes), f"{item.archive_name} size drifted in ZIP", errors)
            require(hashlib.sha256(payload).hexdigest() == item.sha256, f"{item.archive_name} sha256 drifted in ZIP", errors)
        require(
            archive.read(f"{ZIP_ROOT}/REVIEW_BUNDLE_MANIFEST.csv") == manifest_path.read_bytes(),
            "ZIP REVIEW_BUNDLE_MANIFEST.csv does not match local manifest",
            errors,
        )
        require(
            archive.read(f"{ZIP_ROOT}/REVIEWER_README.md") == reviewer_readme(),
            "ZIP REVIEWER_README.md does not match current exporter",
            errors,
        )
        require(
            archive.read(f"{ZIP_ROOT}/REVIEWER_DECLARATION.md") == reviewer_declaration(),
            "ZIP REVIEWER_DECLARATION.md does not match current exporter",
            errors,
        )
        require(
            archive.read(f"{ZIP_ROOT}/REVIEWER_PUBLIC_URLS.csv") == reviewer_public_urls(all_items),
            "ZIP REVIEWER_PUBLIC_URLS.csv does not match current exporter",
            errors,
        )
        public_url_rows = list(
            csv.DictReader(io.StringIO(archive.read(f"{ZIP_ROOT}/REVIEWER_PUBLIC_URLS.csv").decode("utf-8")))
        )
        e2sct019_url_rows = [row for row in public_url_rows if row.get("source_row_id") == "E2SCT-019"]
        require(len(e2sct019_url_rows) == 1, "REVIEWER_PUBLIC_URLS.csv must contain one E2SCT-019 row", errors)
        if e2sct019_url_rows:
            require(
                "GitHub tag returned 404" in e2sct019_url_rows[0].get("public_url_note", ""),
                "E2SCT-019 reviewer URL note must preserve the known GitHub 404 launch hint",
                errors,
            )
        require(
            archive.read(f"{ZIP_ROOT}/data/false_promotion_row_trace.csv") == reviewer_row_trace(all_items),
            "ZIP reviewer-facing false_promotion_row_trace.csv does not match current exporter",
            errors,
        )

    if sha_path.exists():
        expected_sha = sha_path.read_text(encoding="utf-8").split()[0]
        require(sha256_file(zip_path) == expected_sha, "review bundle sha256 file does not match ZIP bytes", errors)

    expected_post_label_rows = manifest_rows(post_label_items)
    actual_post_label_rows = read_csv(post_label_manifest_path)
    require(
        actual_post_label_rows == expected_post_label_rows,
        "post-label key manifest does not match current source files",
        errors,
    )
    expected_post_label_entries = {row["archive_name"] for row in expected_post_label_rows}
    expected_post_label_entries.add(f"{ZIP_ROOT}/post-label-author-key/POST_LABEL_KEY_MANIFEST.csv")
    with zipfile.ZipFile(post_label_zip_path, "r") as archive:
        archive_entries = set(archive.namelist())
        require(
            archive_entries == expected_post_label_entries,
            "post-label key ZIP entries do not match current manifest",
            errors,
        )
        for item in post_label_items:
            payload = archive.read(item.archive_name)
            require(str(len(payload)) == str(item.size_bytes), f"{item.archive_name} size drifted in post-label ZIP", errors)
            require(
                hashlib.sha256(payload).hexdigest() == item.sha256,
                f"{item.archive_name} sha256 drifted in post-label ZIP",
                errors,
            )
        require(
            archive.read(f"{ZIP_ROOT}/post-label-author-key/POST_LABEL_KEY_MANIFEST.csv")
            == post_label_manifest_path.read_bytes(),
            "ZIP POST_LABEL_KEY_MANIFEST.csv does not match local manifest",
            errors,
        )
    if post_label_sha_path.exists():
        expected_sha = post_label_sha_path.read_text(encoding="utf-8").split()[0]
        require(
            sha256_file(post_label_zip_path) == expected_sha,
            "post-label key sha256 file does not match ZIP bytes",
            errors,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs without writing a ZIP.")
    parser.add_argument("--check-output", action="store_true", help="Validate the existing ZIP, manifest, and sha256 against current inputs.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output ZIP path. Defaults to paper build directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    paper = repo_root / "papers" / "diffaudit-evidence-paper"
    errors: list[str] = []
    items = validate_inputs(paper, errors)
    reviewer_items = [item for item in items if not is_post_label_item(item)]
    post_label_items = [item for item in items if is_post_label_item(item)]

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    output = args.output or (paper / "build" / "diffaudit-false-promotion-review-bundle.zip")
    bundle_manifest = output.parent / "false_promotion_review_bundle_manifest.csv"
    post_label_output = output.with_name(POST_LABEL_ZIP_NAME)
    post_label_manifest = output.parent / "false_promotion_post_label_key_manifest.csv"

    if args.check_output:
        validate_output_zip(
            output,
            bundle_manifest,
            reviewer_items,
            items,
            post_label_output,
            post_label_manifest,
            post_label_items,
            errors,
        )
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            raise SystemExit(1)
        review_manifest_count = len(review_bundle_manifest_rows(reviewer_items, items))
        print(
            "False-promotion review bundle output check passed "
            f"({len(reviewer_items)} reviewer source files; "
            f"{review_manifest_count} reviewer manifest rows; "
            f"{len(post_label_items)} post-label source files)."
        )
        return

    if args.check:
        review_manifest_count = len(review_bundle_manifest_rows(reviewer_items, items))
        print(
            "False-promotion review bundle check passed "
            f"({len(reviewer_items)} reviewer source files; "
            f"{review_manifest_count} reviewer manifest rows; "
            f"{len(post_label_items)} post-label source files)."
        )
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(bundle_manifest, review_bundle_manifest_rows(reviewer_items, items))
    write_csv(post_label_manifest, manifest_rows(post_label_items))
    zip_sha = write_review_zip(output, reviewer_items, items, bundle_manifest)
    post_label_sha = write_post_label_zip(post_label_output, post_label_items, post_label_manifest)
    sha_path = output.with_name(f"{output.name}.sha256")
    post_label_sha_path = post_label_output.with_name(f"{post_label_output.name}.sha256")
    sha_path.write_text(f"{zip_sha}  {output.name}\n", encoding="utf-8")
    post_label_sha_path.write_text(f"{post_label_sha}  {post_label_output.name}\n", encoding="utf-8")

    print(f"Wrote {output}")
    print(f"Wrote {bundle_manifest}")
    print(f"Wrote {sha_path}")
    print(f"Wrote {post_label_output}")
    print(f"Wrote {post_label_manifest}")
    print(f"Wrote {post_label_sha_path}")
    print(f"Review bundle source files: {len(reviewer_items)}")
    print(f"Review bundle manifest rows: {len(review_bundle_manifest_rows(reviewer_items, items))}")
    print(f"Post-label key source files: {len(post_label_items)}")
    print(f"SHA256: {zip_sha}")
    print(f"Post-label SHA256: {post_label_sha}")


if __name__ == "__main__":
    main()
