"""Validate the DiffAudit evidence-paper release packet.

This is a submission-facing guard, not a scientific claim upgrader. It checks
that the paper PDF, manifest, claim trace, and source provenance sidecars form a
reviewable packet and that the compiled PDF does not carry obvious private
surface leaks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path


GATE_OUTCOMES = {"Pass", "Partial", "Fail", "N/A"}
TRACE_GATE_COLUMNS = [
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
]
REPORTABLE_GATE_COLUMNS = [
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
]
REQUIRED_CLAIMS = {f"C{i}" for i in range(1, 16)}
PDF_FORBIDDEN_PATTERNS = [
    r"D:\\",
    r"C:\\",
    r"Users\\",
    r"Documents\\",
    r"\bsecret\b",
    r"\bapi[_ -]?key\b",
    r"\btoken\b",
    r"product[- ]ready",
    r"\bdisprove\b",
    r"field-wide\s+prevalence",
    r"measurement\s+error",
    r"scientifically\s+useful",
    r"should\s+not\s+be\s+described",
    r"should\s+use\s+the\s+narrower\s+claim",
    r"public\s+MoFit\s+score-surface\s+replay",
    r"Public\s+COCO\s+score\s+replay",
    r"hard-blind\s+reviewer\s+packet",
    r"support\s+shortcut\s+wording",
    r"H2-family\s+packet\s+is\s+positive",
    r"scientific\s+controls",
    r"deterministic\s+audit-decision\s+surface",
    r"it\s+reports\s+no\s+external\s+labels",
]
PDF_REQUIRED_PATTERNS = [
    r"C14\s+is\s+a\s+thirteen-row\s+author-keyed\s+pre-label\s+stress\s+object",
    r"thirteen\s+selected\s+no-?\s*download\s+E2\s+public-surface\s+checks",
    r"weak\s+rules\s+and\s+gate\s+blockers",
    r"pre-label\s+stress-control",
    r"paper(?:-?artifact)?-?link\s+in\s+12",
    r"current\s+status\s+is\s+n_reviewers=0",
    r"n_reviewers=0",
    r"packet_ready_only",
    r"Each\s+row\s+records\s+a\s+weak-admission\s+trigger\s+and\s+a\s+first[-\s]?blocker\s+label",
    r"code\s+in\s+12",
    r"metric/split\s+in\s+9",
    r"artifact\s+in\s+7",
    r"Every\s+selected\s+row\s+is\s+non-?\s*Pass\s+at\s+the\s+score/response\s+and\s+consumer-?\s*boundary\s+gates",
    r"Author-keyed\s+target\s+and\s+metric\s+blockers\s+support\s+packet-readiness",
    r"28[-\s]?case\s+release[-\s]?wording\s+regression\s+matrix",
    r"release\s+QA\s+for\s+wording\s+boundaries",
    r"Report\s+drift,\s+compute-release\s+gate\s+validity,\s+and\s+external-use\s+estimates\s+remain\s+outside\s+this\s+packet",
    r"agreement\s+and\s+prevalence\s+require\s+independent\s+labels\s+and\s+a\s+larger\s+sampled\s+corpus",
    r"C1(?:[-\s\u2013]+)?C15\s+claim\s+state",
    r"C1(?:[-\s\u2013]+)?C15\s+claim[-\s]?gate\s+recode\s+template",
    r"maps?\s+each\s+headline\s+claim",
    r"availability\s+tier",
    r"Public\s+Score[-\s]?File\s+Boundary:\s+MoFit",
    r"MoFit\s+is\s+a\s+support-only\s+score-file\s+diagnostic",
]
LOG_FORBIDDEN_PATTERNS = [
    r"Undefined",
    r"Citation.*undefined",
    r"Reference.*undefined",
    r"Overfull",
    r"Rerun to get cross-references right",
]
RELEASE_DOC_FORBIDDEN_PATTERNS = [
    r"false-promotion\s+baseline",
    r"counterfactual\s+baseline",
    r"strongest\s+failed\s+public",
]
GENERATED_TEXT_FORBIDDEN_PATTERNS = [
    r"false-promotion[-\s]+baseline",
    r"Strong\s+H2-family\s+packet",
    r"Strong\s+same-family\s+H2\s+candidate\s+evidence",
]
RELEASE_DOCS = [
    "README.md",
    "BUILD.md",
    "claim_register.md",
]
GENERATED_TEXT_SURFACES = [
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_trace.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_transition_examples.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_gate_recode_template.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/source_provenance.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_exemplars.csv",
]
MANUSCRIPT_REQUIRED_PATTERNS = [
    (
        r"(?:apply\s+the\s+rule\s+to\s+same-team-labeled\s+frozen\s+boundary\s+cases|frozen\s+boundary\s+cases\s+as\s+protocol\s+checks)",
        "main.tex must frame the row set as frozen boundary cases used as protocol checks",
    ),
    (
        r"role\s+is\s+boundary\s+checking;\s+frequency\s+estimation\s+requires\s+separate\s+corpus\s+sampling",
        "main.tex must reject frequency/prevalence interpretation for selected rows",
    ),
    (
        r"General\s+gate\s+sufficiency\s+and\s+independent-coding\s+reliability\s+require\s+broader\s+corpora\s+and\s+independent\s+labels",
        "main.tex must preserve the construct-validity limit for same-team gates",
    ),
    (
        r"register\s+check\s+covers\s+selected\s+boundary\s+cases",
        "main.tex must preserve the selected-boundary-case register scope",
    ),
    (
        r"(?:current\s+status\s+is\s+\\texttt\{n\\_reviewers=0\}|C14\s+has\s+\\texttt\{n\\_reviewers=0\})",
        "main.tex must preserve the C14 no-reviewer boundary",
    ),
    (
        r"reviewer\s+agreement\s+and\s+prevalence\s+require\s+independent\s+labels\s+and\s+a\s+larger\s+sampled\s+corpus",
        "main.tex must preserve the C14 reviewer-agreement/prevalence boundary",
    ),
    (
        r"n\\_reviewers=0",
        "main.tex must preserve C14 n_reviewers=0 status",
    ),
    (
        r"\\texttt\{packet\\_ready\\_only\}",
        "main.tex must preserve C14 packet_ready_only status",
    ),
    (
        r"All\s+six\s+gates\s+are\s+non-Pass",
        "main.tex must keep MoFit blocker-first/non-Pass framing",
    ),
    (
        r"MoFit\s+is\s+a\s+support-only\s+score-file\s+diagnostic",
        "main.tex must keep MoFit in support-only score-file diagnostics",
    ),
    (
        r"current\s+MoFit\s+packet\s+supplies\s+stress\s+coverage",
        "main.tex must state that MoFit supplies stress coverage only",
    ),
    (
        r"local\s+packet-identity\s+snapshot",
        "main.tex must identify dirty provenance as a local packet snapshot",
    ),
    (
        r"dirty\s+tree\s+state\s+and\s+local\s+paths\s+identify\s+the\s+review\s+snapshot",
        "main.tex must state that dirty provenance identifies the review snapshot only",
    ),
    (
        r"public-release\s+provenance\s+gate\s+remains\s+unresolved",
        "main.tex must reject clean-public-provenance interpretation",
    ),
    (
        r"fixed[-\s]?subset\s+overfit\s+setting",
        "main.tex must preserve STL-10 fixed-subset overfit support-only framing",
    ),
]
MANUSCRIPT_FORBIDDEN_PATTERNS = [
    (
        r"selected\s+stress\s+suite",
        "main.tex must not frame the selected rows as a stress-suite empirical sample",
    ),
    (
        r"high-scoring\s+compact\s+public\s+score-file\s+replay\s+candidate",
        "main.tex must not editorialize MoFit as a high-scoring candidate",
    ),
    (
        r"C14[^.\n;]*external\s+adjudication\s+evidence",
        "main.tex must not call C14 external adjudication evidence",
    ),
    (
        r"C14[^.\n;]*reliability\s+evidence",
        "main.tex must not call C14 reliability evidence",
    ),
    (
        r"C14[^.\n;]*prevalence\s+(?:evidence|estimate|sample)",
        "main.tex must not call C14 prevalence evidence",
    ),
]
CITATION_COMMAND_RE = re.compile(r"\\cite[a-zA-Z*]*\{([^}]*)\}")
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
BIB_PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|unknown|placeholder|forthcoming)\b", re.IGNORECASE)
BIB_REQUIRED_FIELDS = {
    "author",
    "title",
    "year",
}
REFERENCE_INTEGRITY_AUDIT = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/reference_integrity_audit.csv"
REFERENCE_INTEGRITY_FIELDS = [
    "bib_key",
    "entry_type",
    "title",
    "year",
    "identifier_kind",
    "identifier_value",
    "verification_url",
    "http_status",
    "verification_status",
    "verification_note",
    "metadata_status",
    "metadata_source",
    "metadata_note",
    "checked_at_utc",
]
REFERENCE_IDENTIFIER_KINDS = {"doi_handle", "arxiv_abs", "url"}
SUPPLEMENT_ZIP = "diffaudit-evidence-paper-anonymous-supplement.zip"
SUPPLEMENT_MANIFEST = "anonymous_supplement_manifest.csv"
SUPPLEMENT_ROOT = "diffaudit-evidence-paper"
REVIEW_SNAPSHOT_MANIFEST = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/review_snapshot_manifest.csv"
REVIEW_SNAPSHOT_FIELDS = [
    "schema_version",
    "snapshot_kind",
    "scope",
    "generated_at_utc",
    "repo_head",
    "repo_tree_state",
    "generator_command",
    "generator_script_sha256",
    "release_checker_script_sha256",
    "asset_manifest_sha256",
    "source_provenance_sha256",
    "claim_trace_sha256",
    "paper_pdf_sha256",
    "excluded_public_claims",
    "manifest_category",
    "relative_path",
    "exists",
    "git_status",
    "size_bytes",
    "sha256",
    "snapshot_role",
    "boundary_note",
]
REVIEW_SNAPSHOT_REQUIRED_METADATA = {
    "schema_version": "review-snapshot-v1",
    "snapshot_kind": "local_review_snapshot",
    "scope": "paper_release_packet_inputs_only",
    "generator_command": "python -X utf8 D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/scripts/build_paper_assets.py",
    "snapshot_role": "local-review-packet-identity",
}
REVIEW_SNAPSHOT_REQUIRED_BOUNDARY_PATTERNS = [
    r"not\s+clean\s+public\s+release\s+provenance",
    r"dirty\s+tree\s+is\s+not\s+public\s+provenance",
    r"candidate/support(?:/support-only)?\s+rows\s+are\s+not\s+admitted\s+evidence",
    r"permission-bound\s+artifacts\s+are\s+not\s+public\s+replay\s+evidence",
]
REVIEW_SNAPSHOT_FORBIDDEN_PATTERNS = [
    r"\bclean\s+provenance\b",
    r"\bpublicly\s+reproducible\b",
    r"\barchival\s+release\b",
    r"\bverified\s+public\s+source\b",
    r"\bcomplete\s+provenance\b",
    r"\bsource\s+completeness\b",
    r"\bfield-wide\b",
    r"\bN50\b",
    r"\bcompute\s+release\b",
    r"\bexternal\s+adjudication\b",
    r"\breviewer\s+reliability\b",
]
C14_REVIEW_DIR = "false_promotion_external_review_labels"
C14_REVIEW_FILE_GLOBS = [
    "false_promotion_external_review_*.csv",
    "c14_false_promotion_review_*.csv",
]
C14_PACKET_STATUS = "false_promotion_external_review_packet_status.csv"
C14_AGGREGATION_MD = "false_promotion_external_review_aggregation.md"
C14_PACKET_STATUS_FIELDS = [
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
C14_NO_REVIEWER_STATUS = {
    "packet_label_readiness": "prepared_no_reviewer_csvs",
    "reviewer_count_status": "none",
    "n_reviewers": "0",
    "min_reviewers": "2",
    "reliability_min_reviewers": "3",
    "min_mean_kappa": "0.6",
    "min_field_kappa": "0.5",
    "require_no_majority_ties": "1",
    "majority_resolution_status": "no_labels",
    "reliability_threshold_status": "not_applicable_below_3",
    "declaration_status": "not_checked_no_reviewer_csvs",
    "reliability_threshold_met": "0",
    "external_label_aggregation_available": "0",
    "completed_external_adjudication_allowed": "0",
    "reliability_claim_allowed": "0",
    "compute_release_allowed": "0",
    "allowed_claim_scope": "packet_ready_only",
}
C14_LABEL_DEPENDENT_OUTPUTS = [
    "false_promotion_external_review_declarations.csv",
    "false_promotion_external_review_aggregation.csv",
    "false_promotion_external_review_disagreements.csv",
    "false_promotion_external_review_agreement.csv",
    "false_promotion_external_review_author_key_comparison.csv",
]
C14_DISPATCH_NOTE = "docs/internal/c14-external-review-dispatch-2026-06-08.md"
C14_REVIEW_BUNDLE_ZIP = "build/diffaudit-false-promotion-review-bundle.zip"
C14_POST_LABEL_KEY_ZIP = "build/diffaudit-false-promotion-post-label-key.zip"
C14_DISPATCH_REQUIRED_PHRASES = [
    "This dispatch note is an internal aid.",
    "Packet status: `prepared_no_reviewer_csvs`",
    "Reviewer count: `0`",
    "Allowed claim scope: `packet_ready_only`",
    "Send each independent reviewer exactly these two files",
    "Do not send these files before that reviewer's labels and declaration are final",
    "python -X utf8 scripts\\aggregate_false_promotion_external_review.py",
]
C14_POST_LABEL_ALLOWED_CLAIM_SCOPE_PREFIXES = (
    "external_label_aggregation_selected_13_rows_only_",
    "reviewer_labels_available_unresolved_selected_13_rows_only",
)
MOFIT_GATE_STATUS = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/mofit_public_gate_status.csv"
MOFIT_SCORE_METRICS = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/mofit_public_score_metrics.json"
MOFIT_GATE_STATUS_FIELDS = [
    "surface",
    "gate",
    "status",
    "observed_surface",
    "first_blocker",
    "allowed_claim",
    "forbidden_claim",
]
MOFIT_GATE_SURFACE = "mofit-coco-public-score"
MOFIT_REQUIRED_GATE_STATUS = {
    "target_identity": "Partial",
    "split_identity": "Partial",
    "score_or_response_coverage": "Partial",
    "metric_provenance": "Partial",
    "consumer_boundary": "Fail",
    "surface_delta": "Fail",
}
MOFIT_FORBIDDEN_ALLOWED_CLAIM_PATTERNS = [
    r"\badmitted\b",
    r"\bN50\b",
    r"second\s+(?:independent\s+)?public\s+asset",
    r"compute\s+release",
    r"row[-\s]?bound(?:\s+admitted)?",
    r"official\s+(?:metric|upstream)",
    r"consumer[-\s]?admitted",
]
MOFIT_ALLOWED_CLAIM_REQUIRED_HINT_PATTERNS = [
    r"support[-\s]?only",
]
MOFIT_REQUIRED_FORBIDDEN_BOUNDARY_PATTERNS = [
    r"\badmitted\b",
    r"\bN50\b",
    r"second\s+(?:independent\s+)?public\s+asset",
    r"compute\s+release",
    r"row[-\s]?bound",
    r"official\s+(?:metric|upstream)",
    r"consumer[-\s]?admitted",
]
MOFIT_REQUIRED_FORBIDDEN_BY_GATE = {
    "target_identity": [
        r"\badmitted\b",
        r"\bN50\b",
        r"second\s+(?:independent\s+)?public\s+asset",
        r"compute\s+release",
    ],
    "split_identity": [
        r"row[-\s]?binding|row[-\s]?bound",
    ],
    "score_or_response_coverage": [
        r"row[-\s]?bound",
        r"\badmitted\b",
    ],
    "metric_provenance": [
        r"official\s+(?:metric|upstream)",
    ],
    "consumer_boundary": [
        r"consumer[-\s]?admitted",
    ],
    "surface_delta": [
        r"second\s+(?:independent\s+)?public\s+asset",
    ],
}
REQUIRED_REVIEWER_PACKET_ALLOWED_PRELABEL = {
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_blinded_review_packet.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_external_review_template.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_row_trace.csv",
    "versions/direction-a-false-promotion-audit-codebook.md",
    "versions/direction-a-c14-external-review-launch-protocol.md",
}
REQUIRED_MAINTAINER_ONLY_AUTHOR_KEY = {
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_external_review_packet.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_adjudication_key.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_author_gate_matrix.csv",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_gate_summary.csv",
    "figures/false_promotion_gate_matrix.pdf",
}
STL10_ROUTE_SUMMARY = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/stl10_rediffuse_route_summary.csv"
STL10_ROUTE_SUMMARY_FIELDS = [
    "route",
    "setting",
    "surface",
    "attacker",
    "average",
    "auc",
    "asr",
    "tpr_at_1pct_fpr",
    "claim_role",
    "first_blocker",
    "allowed_claim",
    "forbidden_claim",
    "evidence_source",
]
STL10_EXPECTED_SETTINGS = {
    "strict-300k": {
        "count": 4,
        "claim_role": "bounded_negative",
        "allowed_pattern": r"random[-\s]?level",
        "forbidden_patterns": [
            r"general\s+ReDiffuse\s+refutation",
            r"\badmitted\b",
            r"second\s+public\s+asset",
            r"strict\s+reproduction\s+success",
        ],
    },
    "strict-500k": {
        "count": 4,
        "claim_role": "bounded_negative",
        "allowed_pattern": r"random[-\s]?level",
        "forbidden_patterns": [
            r"general\s+ReDiffuse\s+refutation",
            r"\badmitted\b",
            r"second\s+public\s+asset",
            r"strict\s+reproduction\s+success",
        ],
    },
    "overfit-m1000-cont20k": {
        "count": 4,
        "claim_role": "support_only_memorization_sanity",
        "allowed_pattern": r"fixed[-\s]?subset\s+overfit\s+detects\s+memorization",
        "forbidden_patterns": [
            r"strict\s+STL-10\s+reproduction\s+success",
            r"\badmitted\b",
            r"second\s+public\s+asset",
            r"field[-\s]?level\s+method\s+validity",
        ],
    },
}
STL10_FORBIDDEN_ALLOWED_CLAIM_PATTERNS = [
    r"\badmitted\b",
    r"second\s+(?:independent\s+)?public\s+asset",
    r"strict\s+(?:STL-10\s+)?reproduction\s+success",
    r"field[-\s]?level",
    r"general\s+ReDiffuse\s+refutation",
]
REPORT_CORRECTNESS_FAULT_MATRIX = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/report_correctness_fault_injection.csv"
REPORT_CORRECTNESS_FAULT_FIELDS = [
    "case_id",
    "fault_class",
    "checked_surface",
    "expected",
    "observed",
    "passed",
    "evidence",
]
REPORT_CORRECTNESS_REQUIRED_RCF010 = {
    "fault_class": "metadata drift promoted to release language",
    "checked_surface": "direct phrase scan",
    "expected": "flag",
    "observed": "flagged",
}
REPORT_CORRECTNESS_RCF010_EVIDENCE_PATTERNS = [
    r"metadata-only\s+surface\s+described\s+as\s+admission/release",
    r"compute\s+release",
]
REPORT_CORRECTNESS_EXPECTED_ROWS = 28
REPORT_CORRECTNESS_REQUIRED_GRID_PREFIXES = {
    "RCF-CAND-": {
        "name": "candidate/support promotion mutation",
        "expected": "flag",
        "observed": "flagged",
    },
    "RCF-META-": {
        "name": "metadata-only promotion mutation",
        "expected": "flag",
        "observed": "flagged",
    },
    "RCF-CLEAN-": {
        "name": "clean boundary phrase control",
        "expected": "clean",
        "observed": "clean",
    },
}
MANUSCRIPT_CLAIM_AUDIT = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/manuscript_claim_audit.csv"
MANUSCRIPT_CLAIM_AUDIT_FIELDS = [
    "anchor_id",
    "paper_section",
    "manuscript_required_text",
    "source_paths",
    "source_values",
    "audit_status",
    "boundary_note",
]
MANUSCRIPT_CLAIM_AUDIT_REQUIRED_IDS = {
    "MCA-001",
    "MCA-002",
    "MCA-003",
    "MCA-004",
    "MCA-005",
    "MCA-006",
}
CITATION_CONTEXT_AUDIT = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/citation_context_audit.csv"
CITATION_CONTEXT_AUDIT_FIELDS = [
    "citation_id",
    "main_tex_line",
    "paper_section",
    "cited_keys",
    "claim_text_anchor",
    "expected_source_support",
    "manuscript_claim_role",
    "source_content_status",
    "audit_status",
    "boundary_note",
]
FALSE_PROMOTION_GATE_SUMMARY = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_gate_summary.csv"
FALSE_PROMOTION_AUTHOR_GATE_MATRIX = "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_author_gate_matrix.csv"
FALSE_PROMOTION_GATE_SUMMARY_FIELDS = [
    "gate",
    "outcome",
    "count",
    "selected_row_count",
    "boundary_note",
]
FALSE_PROMOTION_AUTHOR_GATES = [
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
]
FALSE_PROMOTION_GATE_OUTCOMES = ["Pass", "Partial", "Fail", "N/A"]
FALSE_PROMOTION_EXPECTED_SELECTED_ROW_COUNT = 13
FALSE_PROMOTION_REQUIRED_GATE_COUNTS = {
    ("target_gate", "Pass"): 0,
    ("target_gate", "Partial"): 6,
    ("target_gate", "Fail"): 7,
    ("target_gate", "N/A"): 0,
    ("split_gate", "Pass"): 1,
    ("split_gate", "Partial"): 6,
    ("split_gate", "Fail"): 6,
    ("split_gate", "N/A"): 0,
    ("score_or_response_gate", "Pass"): 0,
    ("score_or_response_gate", "Partial"): 0,
    ("score_or_response_gate", "Fail"): 13,
    ("score_or_response_gate", "N/A"): 0,
    ("metric_gate", "Pass"): 0,
    ("metric_gate", "Partial"): 6,
    ("metric_gate", "Fail"): 7,
    ("metric_gate", "N/A"): 0,
    ("semantic_boundary_gate", "Pass"): 4,
    ("semantic_boundary_gate", "Partial"): 3,
    ("semantic_boundary_gate", "Fail"): 6,
    ("semantic_boundary_gate", "N/A"): 0,
    ("provenance_gate", "Pass"): 0,
    ("provenance_gate", "Partial"): 13,
    ("provenance_gate", "Fail"): 0,
    ("provenance_gate", "N/A"): 0,
    ("consumer_boundary_gate", "Pass"): 0,
    ("consumer_boundary_gate", "Partial"): 0,
    ("consumer_boundary_gate", "Fail"): 13,
    ("consumer_boundary_gate", "N/A"): 0,
}
SUPPORT_ONLY_ROUTE_PROVENANCE = {
    "c14-e2-external-adjudication-preregistration": {
        "path": "docs/internal/c14-e2-external-adjudication-preregistration-2026-06-09.md",
        "source_kind": "internal-preregistration",
        "required_note_tokens": [
            "pre_label_preregistered",
            "prepared_no_reviewer_csvs",
            "n_reviewers=0",
            "packet_ready_only",
            "105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4",
            "post-label key path and sha256 sidecar frozen",
            "not external label result",
            "not report completed external adjudication",
        ],
        "negative_support_tokens": ["c14-e2-external-adjudication-preregistration"],
    },
    "sama-dlm-public-surface-check": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct031_sama_dlm_public_surface_check_2026_06_09.md",
        "required_note_tokens": [
            "support-only",
            "no_compute_release",
            "not a second public score/response asset",
            "outside the image-diffusion denominator lane",
        ],
        "negative_support_tokens": ["sama", "e2sct031", "sama-dlm-public-surface-check"],
    },
    "miaept-tabular-public-surface-check": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct032_miaept_tabular_public_surface_check_2026_06_09.md",
        "required_note_tokens": [
            "support-only",
            "no_compute_release",
            "not a second public score/response asset",
            "missing row-bound score/prediction packet",
        ],
        "negative_support_tokens": ["mia-ept", "miaept", "e2sct032", "miaept-tabular-public-surface-check"],
    },
    "diffusion-mia-public-surface-check": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct033_diffusion_mia_public_surface_check_2026_06_09.md",
        "required_note_tokens": [
            "support-only",
            "no_compute_release",
            "not a second public score/response asset",
            "missing row-bound result/verifier packet",
        ],
        "negative_support_tokens": ["diffusion mia", "e2sct033", "diffusion-mia-public-surface-check"],
    },
    "remia-tabular-public-result-archive-check": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md",
        "required_note_tokens": [
            "support-only",
            "no_compute_release",
            "not a second public score/response asset",
            "aggregate json only",
        ],
        "negative_support_tokens": ["remia", "e2sct034", "remia-tabular-public-result-archive-check"],
    },
    "e2-high-value-delta-refresh": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.md",
        "required_note_tokens": [
            "identity_matched",
            "priority_gate_review",
            "filename_hint_manual_gate_review_needed",
            "no c14/n50 update, no admitted evidence, no second public score/response asset, and no compute release",
        ],
        "negative_support_tokens": ["e2-high-value-delta-refresh"],
    },
    "e2-high-value-delta-refresh-csv": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.csv",
        "source_kind": "internal-preflight-table",
        "required_note_tokens": [
            "9/9 identity_matched",
            "priority_gate_review",
            "filename_hint_manual_gate_review_needed",
            "no_compact_reopen_surface_hint",
        ],
        "negative_support_tokens": ["e2-high-value-delta-refresh-csv"],
    },
    "e2-high-value-delta-watchlist": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_watchlist_2026_06_09.csv",
        "source_kind": "internal-preflight-watchlist",
        "required_note_tokens": [
            "source-refresh hygiene only",
            "not prevalence",
            "denominator",
            "compute-release evidence",
        ],
        "negative_support_tokens": ["e2-high-value-delta-watchlist"],
    },
    "e2-high-value-delta-gate-queue": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv",
        "source_kind": "internal-preflight-queue",
        "required_note_tokens": [
            "priority_gate_review",
            "check whether",
            "support-only",
            "c14-v2 candidate only",
        ],
        "negative_support_tokens": ["e2-high-value-delta-gate-queue"],
    },
    "openlvlm-vlm-public-surface-check": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md",
        "required_note_tokens": [
            "future vlm stratum only",
            "not current direction a image-diffusion evidence",
            "not c14/n50",
            "not a second public score/response asset",
            "no_compute_release",
        ],
        "negative_support_tokens": ["openlvlm", "e2sct035", "openlvlm-vlm-public-surface-check"],
    },
    "openlvlm-vlm-public-surface-csv": {
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.csv",
        "source_kind": "internal-preflight-table",
        "required_note_tokens": [
            "runtime score outputs only",
            "wrong current consumer lane",
            "no c14/n50/admitted-evidence/second-public-asset/compute-release upgrade",
        ],
        "negative_support_tokens": ["openlvlm-vlm-public-surface-csv"],
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_with_header(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def run_text(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(cmd)} failed with {completed.returncode}: {detail}")
    return completed.stdout


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_manifest(paper: Path, errors: list[str]) -> dict:
    manifest_path = paper / "asset_manifest.json"
    require(manifest_path.exists(), "asset_manifest.json is missing", errors)
    if not manifest_path.exists():
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("generated", "curated", "paper_sources"):
        paths = manifest.get(key)
        require(isinstance(paths, list) and paths, f"manifest.{key} must be a non-empty list", errors)
        if not isinstance(paths, list):
            continue
        for rel in paths:
            require(isinstance(rel, str) and rel, f"manifest.{key} contains an invalid path: {rel!r}", errors)
            if isinstance(rel, str) and rel:
                require((paper / rel).exists(), f"manifest path does not exist: {key}:{rel}", errors)

    required_policy_keys = [
        "source_policy",
        "validation_policy",
        "review_snapshot_policy",
        "anonymous_supplement_policy",
        "excluded_from_public_claims",
        "reviewer_packet_allowed_prelabel",
        "maintainer_only_author_key",
    ]
    for key in required_policy_keys:
        require(key in manifest, f"manifest lost policy key: {key}", errors)
    excluded = manifest.get("anonymous_supplement_excluded", [])
    require(isinstance(excluded, list), "manifest.anonymous_supplement_excluded must be a list", errors)
    reviewer_allowed = manifest.get("reviewer_packet_allowed_prelabel", [])
    maintainer_only = manifest.get("maintainer_only_author_key", [])
    require(isinstance(reviewer_allowed, list), "manifest.reviewer_packet_allowed_prelabel must be a list", errors)
    require(isinstance(maintainer_only, list), "manifest.maintainer_only_author_key must be a list", errors)
    manifest_paths = {
        str(path)
        for category in ("generated", "curated", "paper_sources")
        for path in manifest.get(category, [])
        if isinstance(manifest.get(category), list)
    }
    if isinstance(excluded, list):
        for rel in excluded:
            require(isinstance(rel, str) and rel, f"manifest anonymous_supplement_excluded contains an invalid path: {rel!r}", errors)
            if isinstance(rel, str) and rel:
                require(rel in manifest_paths, f"anonymous_supplement_excluded path is not in manifest inputs: {rel}", errors)
    excluded_set = {str(path) for path in excluded} if isinstance(excluded, list) else set()
    if isinstance(reviewer_allowed, list):
        reviewer_set = {str(path) for path in reviewer_allowed}
        require(
            REQUIRED_REVIEWER_PACKET_ALLOWED_PRELABEL.issubset(reviewer_set),
            "manifest reviewer_packet_allowed_prelabel lost required C14 pre-label reviewer inputs",
            errors,
        )
        for rel in reviewer_set:
            require(rel in manifest_paths, f"reviewer_packet_allowed_prelabel path is not in manifest inputs: {rel}", errors)
            require(rel not in excluded_set, f"reviewer_packet_allowed_prelabel path is excluded from anonymous supplement: {rel}", errors)
    if isinstance(maintainer_only, list):
        maintainer_set = {str(path) for path in maintainer_only}
        require(
            REQUIRED_MAINTAINER_ONLY_AUTHOR_KEY.issubset(maintainer_set),
            "manifest maintainer_only_author_key lost required C14 author-key paths",
            errors,
        )
        for rel in maintainer_set:
            require(rel in manifest_paths, f"maintainer_only_author_key path is not in manifest inputs: {rel}", errors)
            require(rel in excluded_set, f"maintainer_only_author_key path is not excluded from anonymous supplement: {rel}", errors)
    return manifest


def normalize_manifest_relpath(rel_path: str, errors: list[str]) -> str:
    rel = rel_path.replace("\\", "/")
    require(bool(rel), "empty supplement manifest path", errors)
    require(not rel.startswith("/"), f"absolute supplement manifest path is not allowed: {rel_path!r}", errors)
    require(".." not in Path(rel).parts, f"parent traversal is not allowed in supplement manifest path: {rel_path!r}", errors)
    return rel


def expected_supplement_rows(paper: Path, manifest: dict, errors: list[str]) -> list[dict[str, str]]:
    requested: list[tuple[str, str]] = []
    excluded = {
        normalize_manifest_relpath(str(path), errors)
        for path in manifest.get("anonymous_supplement_excluded", [])
        if isinstance(manifest.get("anonymous_supplement_excluded", []), list)
    }
    for category in ("generated", "curated", "paper_sources"):
        paths = manifest.get(category)
        if isinstance(paths, list):
            requested.extend((category, str(path)) for path in paths)
    requested.extend(
        [
            ("release_file", "asset_manifest.json"),
            ("release_file", "paper.pdf"),
        ]
    )

    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for category, raw_rel in requested:
        rel = normalize_manifest_relpath(raw_rel, errors)
        if rel in excluded:
            continue
        source_path = paper / rel
        if not source_path.exists():
            continue
        archive_name = f"{SUPPLEMENT_ROOT}/{rel}"
        require(archive_name not in seen, f"duplicate supplement archive path: {archive_name}", errors)
        seen.add(archive_name)
        rows.append(
            {
                "category": category,
                "source_path": rel,
                "archive_name": archive_name,
                "size_bytes": str(source_path.stat().st_size),
                "sha256": sha256_file(source_path),
            }
        )
    return sorted(rows, key=lambda row: row["archive_name"])


def validate_claim_trace(paper: Path, repo_root: Path, errors: list[str]) -> None:
    trace_path = paper / "data" / "claim_trace.csv"
    provenance_path = paper / "data" / "source_provenance.csv"
    require(trace_path.exists(), "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_trace.csv is missing", errors)
    require(provenance_path.exists(), "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/source_provenance.csv is missing", errors)
    if not trace_path.exists() or not provenance_path.exists():
        return

    trace_rows = read_csv(trace_path)
    provenance_rows = read_csv(provenance_path)
    provenance_by_id: dict[str, dict[str, str]] = {}
    for row in provenance_rows:
        provenance_id = row.get("provenance_id", "")
        require(bool(provenance_id), "source_provenance row missing provenance_id", errors)
        require(provenance_id not in provenance_by_id, f"duplicate provenance_id: {provenance_id}", errors)
        provenance_by_id[provenance_id] = row
        sha = row.get("sha256", "")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", sha)), f"{provenance_id} has invalid sha256", errors)
        require(row.get("exists") == "true", f"{provenance_id} is not marked as existing", errors)
        source_path = row.get("path", "")
        require(bool(source_path), f"{provenance_id} missing source path", errors)
        if source_path:
            full_source_path = repo_root / source_path
            require(full_source_path.exists(), f"{provenance_id} source path missing: {source_path}", errors)
            if full_source_path.exists():
                require(
                    sha256_file(full_source_path) == sha,
                    f"{provenance_id} sha256 does not match current source bytes",
                    errors,
                )

    claims = {row.get("claim_id", "") for row in trace_rows}
    require(REQUIRED_CLAIMS.issubset(claims), "claim_trace lost one or more C1-C15 claims", errors)
    for row in trace_rows:
        claim_id = row.get("claim_id", "<missing>")
        for column in TRACE_GATE_COLUMNS:
            require(row.get(column) in GATE_OUTCOMES, f"{claim_id} has invalid {column}: {row.get(column)!r}", errors)
        provenance_ids = [item for item in row.get("provenance_ids", "").split(";") if item]
        require(bool(provenance_ids), f"{claim_id} has no provenance_ids", errors)
        for provenance_id in provenance_ids:
            require(provenance_id in provenance_by_id, f"{claim_id} references missing provenance_id: {provenance_id}", errors)
        require(bool(row.get("evidence_state")), f"{claim_id} missing evidence_state", errors)
        require(bool(row.get("allowed_wording")), f"{claim_id} missing allowed_wording", errors)
        validate_claim_trace_gate_consistency(row, errors)
    validate_support_only_route_provenance(paper, trace_rows, provenance_by_id, errors)


def validate_support_only_route_provenance(
    paper: Path,
    trace_rows: list[dict[str, str]],
    provenance_by_id: dict[str, dict[str, str]],
    errors: list[str],
) -> None:
    """Keep current post-C14 route checks as C5 support-only provenance."""

    c5 = next((row for row in trace_rows if row.get("claim_id") == "C5"), None)
    c5_provenance = set(c5.get("provenance_ids", "").split(";")) if c5 else set()
    require(c5 is not None, "claim_trace missing C5 support/negative route claim", errors)

    for provenance_id, expected in SUPPORT_ONLY_ROUTE_PROVENANCE.items():
        row = provenance_by_id.get(provenance_id)
        require(row is not None, f"source_provenance missing support-only route check: {provenance_id}", errors)
        require(
            provenance_id in c5_provenance,
            f"C5 missing support-only route provenance: {provenance_id}",
            errors,
        )
        if row is None:
            continue
        require(
            row.get("path") == expected["path"],
            f"{provenance_id} path drifted: {row.get('path')!r}",
            errors,
        )
        require(
            row.get("source_kind") == expected.get("source_kind", "internal-preflight-note"),
            f"{provenance_id} must remain a {expected.get('source_kind', 'internal-preflight-note')}",
            errors,
        )
        note = row.get("note", "").lower()
        for token in expected["required_note_tokens"]:
            require(token in note, f"{provenance_id} note lost boundary token: {token}", errors)

    for row in trace_rows:
        claim_id = row.get("claim_id", "")
        provenance_ids = set(row.get("provenance_ids", "").split(";"))
        if claim_id == "C5":
            continue
        for provenance_id in SUPPORT_ONLY_ROUTE_PROVENANCE:
            require(
                provenance_id not in provenance_ids,
                f"{provenance_id} must not be referenced by {claim_id}; support-only route checks belong only to C5",
                errors,
            )

    negative_support_path = paper / "data" / "negative_support_rows.csv"
    if negative_support_path.exists():
        negative_support_text = negative_support_path.read_text(encoding="utf-8").lower()
        for provenance_id, expected in SUPPORT_ONLY_ROUTE_PROVENANCE.items():
            for token in expected["negative_support_tokens"]:
                require(
                    token.lower() not in negative_support_text,
                    f"{provenance_id} must not enter metric-bearing negative_support_rows.csv",
                    errors,
                )


def validate_claim_trace_gate_consistency(row: dict[str, str], errors: list[str]) -> None:
    claim_id = row.get("claim_id", "<missing>")
    evidence_state = row.get("evidence_state", "").strip().lower()
    allowed_wording = row.get("allowed_wording", "").strip().lower()
    replay_tier = row.get("replay_tier", "").strip()
    first_blocker = row.get("first_blocker", "").strip()
    gate_values = [row.get(column, "") for column in TRACE_GATE_COLUMNS]

    require(bool(replay_tier), f"{claim_id} missing replay_tier", errors)
    require(not re.search(r"\b(TODO|TBD|unknown|placeholder)\b", replay_tier, re.IGNORECASE), f"{claim_id} has placeholder replay_tier", errors)

    is_reportable_state = "reportable" in evidence_state
    if is_reportable_state:
        for column in REPORTABLE_GATE_COLUMNS:
            require(row.get(column) == "Pass", f"{claim_id} reportable state with non-Pass {column}: {row.get(column)!r}", errors)
        require(row.get("delta_gate") in {"Pass", "N/A"}, f"{claim_id} reportable state with blocking delta_gate: {row.get('delta_gate')!r}", errors)
    else:
        require(bool(first_blocker), f"{claim_id} non-reportable claim missing first_blocker", errors)

    has_blocking_or_partial_gate = any(value in {"Fail", "Partial"} for value in gate_values)
    if has_blocking_or_partial_gate:
        require(bool(first_blocker), f"{claim_id} has non-Pass gate but empty first_blocker", errors)
        require(not is_reportable_state, f"{claim_id} reportable state has Fail/Partial gate labels", errors)

        if "candidate" in evidence_state:
            require(
                any(token in allowed_wording for token in ("candidate", "not admitted", "no cross-model", "no cross-dataset")),
                f"{claim_id} candidate state wording does not preserve candidate/non-admission boundary",
                errors,
            )
    validate_h2_claim_trace_boundary(row, errors)


def validate_h2_claim_trace_boundary(row: dict[str, str], errors: list[str]) -> None:
    claim_id = row.get("claim_id", "")
    evidence_state = row.get("evidence_state", "").strip().lower()
    allowed_wording = row.get("allowed_wording", "").strip().lower()
    first_blocker = row.get("first_blocker", "").strip().lower()

    if claim_id == "C3":
        require("candidate" in evidence_state, "C3 H2 must remain candidate-only", errors)
        require(row.get("boundary_gate") == "Fail", f"C3 H2 boundary_gate must remain Fail: {row.get('boundary_gate')!r}", errors)
        require(row.get("delta_gate") == "Fail", f"C3 H2 delta_gate must remain Fail: {row.get('delta_gate')!r}", errors)
        require("consumer" in first_blocker and ("img2img" in first_blocker or "portability" in first_blocker), "C3 H2 first_blocker must preserve consumer/img2img portability blocker", errors)
        require("candidate" in allowed_wording and "not admitted" in allowed_wording, "C3 H2 allowed_wording must preserve candidate and not-admitted boundary", errors)
        require("strong" not in allowed_wording, "C3 H2 allowed_wording must not use strong-signal promotion wording", errors)

    if claim_id == "C4":
        require("support" in evidence_state, "C4 H2 same-family controls must remain support-only", errors)
        require(row.get("boundary_gate") == "Partial", f"C4 H2 boundary_gate must remain Partial: {row.get('boundary_gate')!r}", errors)
        require(row.get("delta_gate") == "Fail", f"C4 H2 delta_gate must remain Fail: {row.get('delta_gate')!r}", errors)
        require("non-adjacent" in first_blocker, "C4 H2 first_blocker must preserve non-adjacent asset blocker", errors)
        require("no cross-model" in allowed_wording or "no cross-dataset" in allowed_wording or "not portability" in allowed_wording, "C4 H2 allowed_wording must reject portability", errors)


def expected_review_snapshot_rows(paper: Path, repo_root: Path, manifest: dict, errors: list[str]) -> list[dict[str, str]]:
    excluded = {
        normalize_manifest_relpath(str(path), errors)
        for path in manifest.get("anonymous_supplement_excluded", [])
        if isinstance(manifest.get("anonymous_supplement_excluded", []), list)
    }
    requested: list[tuple[str, str]] = []
    for category in ("generated", "curated", "paper_sources"):
        paths = manifest.get(category)
        if isinstance(paths, list):
            requested.extend(
                (category, str(path))
                for path in paths
                if str(path) != REVIEW_SNAPSHOT_MANIFEST and str(path) not in excluded
            )
    repo_sources = manifest.get("repo_sources", [])
    if isinstance(repo_sources, list):
        requested.extend(("repo_sources", str(path)) for path in repo_sources)
    requested.extend(
        [
            ("release_file", "asset_manifest.json"),
            ("release_file", "paper.pdf"),
        ]
    )
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for category, raw_rel in requested:
        rel = normalize_manifest_relpath(raw_rel, errors)
        require(not re.search(r"[A-Za-z]:|\\|Users/", rel, flags=re.IGNORECASE), f"review snapshot path is not anonymized relative path: {rel}", errors)
        require(rel not in seen, f"duplicate review snapshot path: {rel}", errors)
        seen.add(rel)
        path = repo_root / rel if category == "repo_sources" else paper / rel
        rows.append(
            {
                "manifest_category": category,
                "relative_path": rel,
                "exists": str(path.exists()).lower(),
                "size_bytes": str(path.stat().st_size) if path.exists() else "",
                "sha256": sha256_file(path) if path.exists() else "",
            }
        )
    return sorted(rows, key=lambda row: row["relative_path"])


def validate_review_snapshot_manifest(paper: Path, repo_root: Path, manifest: dict, errors: list[str]) -> None:
    provenance_path = paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data" / "source_provenance.csv"
    require(provenance_path.exists(), "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/source_provenance.csv is missing", errors)
    if not provenance_path.exists():
        return

    provenance_rows = read_csv(provenance_path)
    dirty_provenance = any(row.get("repo_tree_state") == "dirty" for row in provenance_rows)
    path = paper / REVIEW_SNAPSHOT_MANIFEST
    if dirty_provenance:
        require(path.exists(), f"{REVIEW_SNAPSHOT_MANIFEST} is required when source_provenance is dirty", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == REVIEW_SNAPSHOT_FIELDS, f"{REVIEW_SNAPSHOT_MANIFEST} header drifted: {header}", errors)
    require(bool(rows), f"{REVIEW_SNAPSHOT_MANIFEST} has no rows", errors)
    if not rows:
        return

    metadata_fields = [
        "schema_version",
        "snapshot_kind",
        "scope",
        "generated_at_utc",
        "repo_head",
        "repo_tree_state",
        "generator_command",
        "generator_script_sha256",
        "release_checker_script_sha256",
        "asset_manifest_sha256",
        "source_provenance_sha256",
        "claim_trace_sha256",
        "paper_pdf_sha256",
        "excluded_public_claims",
        "snapshot_role",
        "boundary_note",
    ]
    first = rows[0]
    for row in rows:
        for field in metadata_fields:
            require(row.get(field) == first.get(field), f"review snapshot metadata field drifted within file: {field}", errors)
        for field, expected in REVIEW_SNAPSHOT_REQUIRED_METADATA.items():
            require(row.get(field) == expected, f"review snapshot {field} drifted: {row.get(field)!r}", errors)
        require(
            bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", row.get("generated_at_utc", ""))),
            "review snapshot generated_at_utc must be UTC second precision",
            errors,
        )
        require(row.get("repo_tree_state") in {"dirty", "clean"}, f"review snapshot repo_tree_state invalid: {row.get('repo_tree_state')!r}", errors)
        if dirty_provenance:
            require(row.get("repo_tree_state") == "dirty", "review snapshot must preserve dirty repo_tree_state", errors)
        boundary_text = f"{row.get('boundary_note', '')}\n{row.get('excluded_public_claims', '')}"
        for pattern in REVIEW_SNAPSHOT_REQUIRED_BOUNDARY_PATTERNS:
            require(
                bool(re.search(pattern, boundary_text, flags=re.IGNORECASE)),
                f"review snapshot lost boundary phrase: {pattern}",
                errors,
            )
        for pattern in REVIEW_SNAPSHOT_FORBIDDEN_PATTERNS:
            require(
                not re.search(pattern, boundary_text, flags=re.IGNORECASE),
                f"review snapshot overclaim phrase hit: {pattern}",
                errors,
            )

    require(first.get("repo_head") == run_text(["git", "rev-parse", "HEAD"], repo_root).strip(), "review snapshot repo_head does not match current HEAD", errors)
    require(first.get("generator_script_sha256") == sha256_file(paper / "scripts" / "build_paper_assets.py"), "review snapshot generator_script_sha256 drifted", errors)
    require(first.get("release_checker_script_sha256") == sha256_file(repo_root / "scripts" / "check_paper_release_packet.py"), "review snapshot release_checker_script_sha256 drifted", errors)
    require(first.get("asset_manifest_sha256") == sha256_file(paper / "asset_manifest.json"), "review snapshot asset_manifest_sha256 drifted", errors)
    require(first.get("source_provenance_sha256") == sha256_file(provenance_path), "review snapshot source_provenance_sha256 drifted", errors)
    require(first.get("claim_trace_sha256") == sha256_file(paper / "data" / "claim_trace.csv"), "review snapshot claim_trace_sha256 drifted", errors)
    paper_pdf = paper / "paper.pdf"
    require(first.get("paper_pdf_sha256") == (sha256_file(paper_pdf) if paper_pdf.exists() else ""), "review snapshot paper_pdf_sha256 drifted", errors)

    expected_rows = expected_review_snapshot_rows(paper, repo_root, manifest, errors)
    actual_rows = sorted(
        [
            {
                "manifest_category": row.get("manifest_category", ""),
                "relative_path": row.get("relative_path", ""),
                "exists": row.get("exists", ""),
                "size_bytes": row.get("size_bytes", ""),
                "sha256": row.get("sha256", ""),
            }
            for row in rows
        ],
        key=lambda row: row["relative_path"],
    )
    require(actual_rows == expected_rows, "review snapshot manifest does not match current packet input bytes", errors)


def validate_mofit_gate_status(paper: Path, errors: list[str]) -> None:
    """Keep MoFit's public score surface support-only in release checks."""

    path = paper / MOFIT_GATE_STATUS
    metrics_path = paper / MOFIT_SCORE_METRICS
    require(path.exists(), f"{MOFIT_GATE_STATUS} is missing", errors)
    require(metrics_path.exists(), f"{MOFIT_SCORE_METRICS} is missing", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == MOFIT_GATE_STATUS_FIELDS, f"{MOFIT_GATE_STATUS} header drifted: {header}", errors)
    require(
        len(rows) == len(MOFIT_REQUIRED_GATE_STATUS),
        f"{MOFIT_GATE_STATUS} must contain exactly {len(MOFIT_REQUIRED_GATE_STATUS)} gate rows",
        errors,
    )

    rows_by_gate: dict[str, dict[str, str]] = {}
    forbidden_claims: list[str] = []
    for row in rows:
        gate = row.get("gate", "")
        require(row.get("surface") == MOFIT_GATE_SURFACE, f"MoFit gate row has unexpected surface: {row.get('surface')!r}", errors)
        require(gate in MOFIT_REQUIRED_GATE_STATUS, f"MoFit gate row has unexpected gate: {gate!r}", errors)
        require(gate not in rows_by_gate, f"MoFit gate row duplicated gate: {gate}", errors)
        if gate:
            rows_by_gate[gate] = row

        for column in ("observed_surface", "first_blocker", "allowed_claim", "forbidden_claim"):
            require(bool(row.get(column, "").strip()), f"MoFit {gate or '<missing>'} row missing {column}", errors)

        status = row.get("status", "")
        require(status != "Pass", f"MoFit {gate or '<missing>'} row must not be Pass", errors)
        if gate in MOFIT_REQUIRED_GATE_STATUS:
            require(
                status == MOFIT_REQUIRED_GATE_STATUS[gate],
                f"MoFit {gate} status drifted: {status!r}",
                errors,
            )

        allowed_claim = row.get("allowed_claim", "")
        for pattern in MOFIT_FORBIDDEN_ALLOWED_CLAIM_PATTERNS:
            require(
                not re.search(pattern, allowed_claim, flags=re.IGNORECASE),
                f"MoFit {gate or '<missing>'} allowed_claim crosses support-only boundary: {pattern}",
                errors,
            )
        require(
            any(re.search(pattern, allowed_claim, flags=re.IGNORECASE) for pattern in MOFIT_ALLOWED_CLAIM_REQUIRED_HINT_PATTERNS),
            f"MoFit {gate or '<missing>'} allowed_claim lacks support-only framing",
            errors,
        )

        forbidden_claim = row.get("forbidden_claim", "")
        for pattern in MOFIT_REQUIRED_FORBIDDEN_BY_GATE.get(gate, []):
            require(
                bool(re.search(pattern, forbidden_claim, flags=re.IGNORECASE)),
                f"MoFit {gate} forbidden_claim lost gate boundary: {pattern}",
                errors,
            )
        forbidden_claims.append(row.get("forbidden_claim", ""))

    missing_gates = sorted(set(MOFIT_REQUIRED_GATE_STATUS) - set(rows_by_gate))
    require(not missing_gates, f"MoFit gate status missing gates: {', '.join(missing_gates)}", errors)
    for gate in ("consumer_boundary", "surface_delta"):
        row = rows_by_gate.get(gate)
        if row is not None:
            require(row.get("status") == "Fail", f"MoFit {gate} must remain Fail", errors)

    forbidden_claim_text = "\n".join(forbidden_claims)
    for pattern in MOFIT_REQUIRED_FORBIDDEN_BOUNDARY_PATTERNS:
        require(
            bool(re.search(pattern, forbidden_claim_text, flags=re.IGNORECASE)),
            f"MoFit forbidden_claims lost required boundary: {pattern}",
            errors,
        )
    validate_mofit_metric_values(paper, rows_by_gate, errors)


def validate_mofit_metric_values(paper: Path, rows_by_gate: dict[str, dict[str, str]], errors: list[str]) -> None:
    metrics_path = paper / MOFIT_SCORE_METRICS
    if not metrics_path.exists():
        return
    try:
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{MOFIT_SCORE_METRICS} is invalid JSON: {exc}")
        return

    best = payload.get("best")
    require(isinstance(best, dict), f"{MOFIT_SCORE_METRICS} missing best metrics object", errors)
    if not isinstance(best, dict):
        return

    required_values = {
        "AUC": best.get("auc"),
        "ASR": best.get("best_asr"),
        "TPR@1%FPR": best.get("tpr_at_1fpr"),
        "TPR@0.1%FPR": best.get("tpr_at_01fpr"),
    }
    for label, value in required_values.items():
        require(isinstance(value, (int, float)), f"{MOFIT_SCORE_METRICS} best.{label} is not numeric", errors)
    if not all(isinstance(value, (int, float)) for value in required_values.values()):
        return

    expected_text = {
        label: format(float(value), ".6f").rstrip("0").rstrip(".")
        for label, value in required_values.items()
    }
    metric_row_text = rows_by_gate.get("metric_provenance", {}).get("observed_surface", "")
    for label, text_value in expected_text.items():
        require(
            text_value in metric_row_text,
            f"MoFit metric_provenance observed_surface missing frozen {label}={text_value}",
            errors,
        )

    manuscript = paper / "main.tex"
    if manuscript.exists():
        manuscript_text = manuscript.read_text(encoding="utf-8")
        for label, text_value in expected_text.items():
            require(
                text_value in manuscript_text,
                f"main.tex missing frozen MoFit {label}={text_value}",
                errors,
            )


def validate_stl10_route_summary(paper: Path, errors: list[str]) -> None:
    """Keep STL-10 DDIM/ReDiffuse strict and overfit surfaces in support-only scope."""

    path = paper / STL10_ROUTE_SUMMARY
    require(path.exists(), f"{STL10_ROUTE_SUMMARY} is missing", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == STL10_ROUTE_SUMMARY_FIELDS, f"{STL10_ROUTE_SUMMARY} header drifted: {header}", errors)
    require(
        len(rows) == sum(item["count"] for item in STL10_EXPECTED_SETTINGS.values()),
        f"{STL10_ROUTE_SUMMARY} must contain the frozen strict/overfit rows",
        errors,
    )

    rows_by_setting: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        setting = row.get("setting", "")
        rows_by_setting.setdefault(setting, []).append(row)
        require(row.get("route") == "stl10-ddim-rediffuse", f"STL-10 route row has unexpected route: {row.get('route')!r}", errors)
        require(setting in STL10_EXPECTED_SETTINGS, f"STL-10 route row has unexpected setting: {setting!r}", errors)
        for column in ("surface", "attacker", "first_blocker", "allowed_claim", "forbidden_claim", "evidence_source"):
            require(bool(row.get(column, "").strip()), f"STL-10 {setting or '<missing>'} row missing {column}", errors)
        for column in ("auc", "asr", "tpr_at_1pct_fpr"):
            try:
                value = float(row.get(column, ""))
            except ValueError:
                errors.append(f"STL-10 {setting or '<missing>'} row has non-numeric {column}: {row.get(column)!r}")
                continue
            require(0.0 <= value <= 1.0, f"STL-10 {setting or '<missing>'} row has out-of-range {column}: {value}", errors)

        allowed_claim = row.get("allowed_claim", "")
        for pattern in STL10_FORBIDDEN_ALLOWED_CLAIM_PATTERNS:
            require(
                not re.search(pattern, allowed_claim, flags=re.IGNORECASE),
                f"STL-10 {setting or '<missing>'} allowed_claim crosses support boundary: {pattern}",
                errors,
            )

    for setting, expected in STL10_EXPECTED_SETTINGS.items():
        setting_rows = rows_by_setting.get(setting, [])
        require(
            len(setting_rows) == expected["count"],
            f"STL-10 {setting} row count drifted: {len(setting_rows)}",
            errors,
        )
        attacker_pairs = {(row.get("attacker", ""), row.get("average", "")) for row in setting_rows}
        require(
            attacker_pairs == {("SecMI", "1"), ("PIA", "1"), ("ReDiffuse", "10"), ("ReDiffuse", "2")},
            f"STL-10 {setting} attacker set drifted: {sorted(attacker_pairs)}",
            errors,
        )
        for row in setting_rows:
            require(
                row.get("claim_role") == expected["claim_role"],
                f"STL-10 {setting} claim_role drifted: {row.get('claim_role')!r}",
                errors,
            )
            require(
                bool(re.search(expected["allowed_pattern"], row.get("allowed_claim", ""), flags=re.IGNORECASE)),
                f"STL-10 {setting} allowed_claim lost required boundary: {expected['allowed_pattern']}",
                errors,
            )
            forbidden_claim = row.get("forbidden_claim", "")
            for pattern in expected["forbidden_patterns"]:
                require(
                    bool(re.search(pattern, forbidden_claim, flags=re.IGNORECASE)),
                    f"STL-10 {setting} forbidden_claim lost boundary: {pattern}",
                    errors,
                )
            try:
                auc = float(row.get("auc", ""))
            except ValueError:
                continue
            if setting.startswith("strict-"):
                require(auc < 0.55, f"STL-10 {setting} strict route no longer random-level: {auc}", errors)
            else:
                require(auc > 0.9, f"STL-10 {setting} overfit sanity no longer high-signal: {auc}", errors)


def validate_report_correctness_fault_matrix(paper: Path, errors: list[str]) -> None:
    """Keep the release-wording fault matrix tied to semantic CSV rows."""

    path = paper / REPORT_CORRECTNESS_FAULT_MATRIX
    require(path.exists(), f"{REPORT_CORRECTNESS_FAULT_MATRIX} is missing", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == REPORT_CORRECTNESS_FAULT_FIELDS, f"{REPORT_CORRECTNESS_FAULT_MATRIX} header drifted: {header}", errors)
    require(bool(rows), f"{REPORT_CORRECTNESS_FAULT_MATRIX} has no rows", errors)
    require(
        len(rows) == REPORT_CORRECTNESS_EXPECTED_ROWS,
        f"{REPORT_CORRECTNESS_FAULT_MATRIX} row count drifted: {len(rows)} != {REPORT_CORRECTNESS_EXPECTED_ROWS}",
        errors,
    )
    by_case: dict[str, dict[str, str]] = {}
    for row in rows:
        case_id = row.get("case_id", "")
        require(bool(case_id), f"{REPORT_CORRECTNESS_FAULT_MATRIX} row missing case_id", errors)
        require(case_id not in by_case, f"{REPORT_CORRECTNESS_FAULT_MATRIX} duplicated case_id: {case_id}", errors)
        if case_id:
            by_case[case_id] = row
        require(row.get("passed") == "1", f"{case_id or '<missing>'} report-correctness fault case did not pass", errors)

    rcf010 = by_case.get("RCF-010")
    require(rcf010 is not None, "report-correctness fault matrix lost RCF-010 metadata-drift guard", errors)
    if rcf010 is not None:
        for field, expected in REPORT_CORRECTNESS_REQUIRED_RCF010.items():
            require(
                rcf010.get(field) == expected,
                f"RCF-010 {field} drifted: {rcf010.get(field)!r}",
                errors,
            )
        evidence = rcf010.get("evidence", "")
        for pattern in REPORT_CORRECTNESS_RCF010_EVIDENCE_PATTERNS:
            require(
                bool(re.search(pattern, evidence, flags=re.IGNORECASE)),
                f"RCF-010 evidence lost required boundary: {pattern}",
                errors,
            )

    for prefix, spec in REPORT_CORRECTNESS_REQUIRED_GRID_PREFIXES.items():
        matching = [row for case_id, row in by_case.items() if case_id.startswith(prefix)]
        require(
            bool(matching),
            f"report-correctness fault matrix lost {spec['name']} rows ({prefix})",
            errors,
        )
        require(
            any(
                row.get("checked_surface") == "direct phrase scan"
                and row.get("expected") == spec["expected"]
                and row.get("observed") == spec["observed"]
                for row in matching
            ),
            f"report-correctness fault matrix {spec['name']} rows lost expected {spec['expected']}->{spec['observed']} outcome",
            errors,
        )


def normalize_manuscript_anchor_text(text: str) -> str:
    text = text.replace("\\%", "%").replace("\\_", "_")
    text = text.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip()


def expected_manuscript_claim_source_values(paper: Path, errors: list[str]) -> dict[str, str]:
    expected: dict[str, str] = {}

    admitted_rows = read_csv(paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/admitted_rows.csv")
    replay_admitted = sum(row.get("replay_tier") in {"row-score-replay", "target-score-replay"} for row in admitted_rows)
    point_estimates = sum(row.get("replay_tier") == "source-documented-point-estimate" for row in admitted_rows)
    expected["MCA-001"] = f"total={len(admitted_rows)}; replay_admitted={replay_admitted}; source_point={point_estimates}"

    h2_rows = read_csv(paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/h2_output_cloud_rows.csv")
    h2_candidates = [
        row for row in h2_rows
        if row.get("source") == "h2-main" and row.get("label") == "output-cloud 512/512"
    ]
    require(len(h2_candidates) == 1, "manuscript claim audit could not identify unique H2 candidate row", errors)
    if h2_candidates:
        expected["MCA-002"] = f"h2_candidate_auc={float(h2_candidates[0]['auc']):.6f}"

    metrics_path = paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/mofit_public_score_metrics.json"
    try:
        mofit_best = json.loads(metrics_path.read_text(encoding="utf-8"))["best"]
    except (KeyError, json.JSONDecodeError) as exc:
        errors.append(f"{metrics_path.relative_to(paper)} cannot supply MoFit manuscript audit values: {exc}")
        mofit_best = {}
    if mofit_best:
        expected["MCA-003"] = (
            f"auc={float(mofit_best['auc']):.6f}; asr={float(mofit_best['best_asr']):.3f}; "
            f"tpr1={float(mofit_best['tpr_at_1fpr']):.3f}; tpr01={float(mofit_best['tpr_at_01fpr']):.3f}"
        )

    weak_rules = {row.get("weak_rule", ""): row for row in read_csv(paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_rule_summary.csv")}
    try:
        code_rows = int(weak_rules["code_availability_would_promote"]["would_promote_rows"])
        paper_link_rows = int(weak_rules["paper_claim_artifact_link_would_promote"]["would_promote_rows"])
        selected_rows = int(weak_rules["code_availability_would_promote"]["selected_row_count"])
        expected["MCA-004"] = f"code={code_rows}; paper_link={paper_link_rows}; selected={selected_rows}"
    except KeyError as exc:
        errors.append(f"{MANUSCRIPT_CLAIM_AUDIT} missing false-promotion weak-rule source: {exc}")

    gate_counts = {
        (row.get("gate", ""), row.get("outcome", "")): row
        for row in read_csv(paper / "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/false_promotion_gate_summary.csv")
    }
    try:
        score_pass = int(gate_counts[("score_or_response_gate", "Pass")]["count"])
        consumer_pass = int(gate_counts[("consumer_boundary_gate", "Pass")]["count"])
        expected["MCA-005"] = f"score_or_response_pass={score_pass}; consumer_boundary_pass={consumer_pass}"
    except KeyError as exc:
        errors.append(f"{MANUSCRIPT_CLAIM_AUDIT} missing false-promotion gate source: {exc}")

    report_rows = read_csv(paper / REPORT_CORRECTNESS_FAULT_MATRIX)
    report_passed = sum(row.get("passed") == "1" for row in report_rows)
    expected["MCA-006"] = f"cases={len(report_rows)}; passed={report_passed}"
    return expected


def validate_manuscript_claim_audit(paper: Path, errors: list[str]) -> None:
    """Verify high-risk manuscript statements against generated claim anchors."""

    path = paper / MANUSCRIPT_CLAIM_AUDIT
    require(path.exists(), f"{MANUSCRIPT_CLAIM_AUDIT} is missing", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == MANUSCRIPT_CLAIM_AUDIT_FIELDS, f"{MANUSCRIPT_CLAIM_AUDIT} header drifted: {header}", errors)
    by_id: dict[str, dict[str, str]] = {}
    manuscript_text = normalize_manuscript_anchor_text((paper / "main.tex").read_text(encoding="utf-8", errors="replace"))
    expected_source_values = expected_manuscript_claim_source_values(paper, errors)

    for row in rows:
        anchor_id = row.get("anchor_id", "")
        require(anchor_id in MANUSCRIPT_CLAIM_AUDIT_REQUIRED_IDS, f"{MANUSCRIPT_CLAIM_AUDIT} unexpected anchor_id: {anchor_id!r}", errors)
        require(anchor_id not in by_id, f"{MANUSCRIPT_CLAIM_AUDIT} duplicated anchor_id: {anchor_id}", errors)
        if anchor_id:
            by_id[anchor_id] = row
        require(row.get("audit_status") == "pass", f"{anchor_id or '<missing>'} manuscript claim audit did not pass", errors)
        required_text = normalize_manuscript_anchor_text(row.get("manuscript_required_text", ""))
        require(bool(required_text), f"{anchor_id or '<missing>'} missing manuscript_required_text", errors)
        if required_text:
            require(required_text in manuscript_text, f"{anchor_id} manuscript_required_text not found in main.tex", errors)

        for source_path in [item.strip() for item in row.get("source_paths", "").split(";") if item.strip()]:
            require(not re.search(r"[A-Za-z]:|\\|Users/", source_path, flags=re.IGNORECASE), f"{anchor_id} source path is not anonymized relative path: {source_path}", errors)
            require((paper / source_path).exists(), f"{anchor_id} source path missing: {source_path}", errors)

        if anchor_id in expected_source_values:
            require(
                row.get("source_values") == expected_source_values[anchor_id],
                f"{anchor_id} source_values drifted: {row.get('source_values')!r}",
                errors,
            )

    missing = sorted(MANUSCRIPT_CLAIM_AUDIT_REQUIRED_IDS - set(by_id))
    require(not missing, f"{MANUSCRIPT_CLAIM_AUDIT} missing required anchors: {missing}", errors)
    require(
        "not prevalence" in by_id.get("MCA-004", {}).get("boundary_note", ""),
        "MCA-004 lost C14 non-prevalence boundary",
        errors,
    )
    require(
        "no external reviewer labels" in by_id.get("MCA-005", {}).get("boundary_note", ""),
        "MCA-005 lost no-external-reviewer-label boundary",
        errors,
    )


def extract_manuscript_citation_contexts(tex_text: str) -> list[dict[str, str]]:
    contexts: list[dict[str, str]] = []
    for line_no, line in enumerate(tex_text.splitlines(), start=1):
        for match in CITATION_COMMAND_RE.finditer(line):
            keys = ";".join(key.strip() for key in match.group(1).split(",") if key.strip())
            contexts.append(
                {
                    "main_tex_line": str(line_no),
                    "cited_keys": keys,
                    "line_text": line.strip(),
                }
            )
    return contexts


def validate_citation_context_audit(paper: Path, errors: list[str]) -> None:
    """Verify the citation-context inventory against main.tex and verified refs."""

    path = paper / CITATION_CONTEXT_AUDIT
    main_path = paper / "main.tex"
    refs_path = paper / "refs.bib"
    reference_audit_path = paper / REFERENCE_INTEGRITY_AUDIT
    require(path.exists(), f"{CITATION_CONTEXT_AUDIT} is missing", errors)
    require(main_path.exists(), "main.tex is missing", errors)
    require(refs_path.exists(), "refs.bib is missing", errors)
    require(reference_audit_path.exists(), f"{REFERENCE_INTEGRITY_AUDIT} is missing", errors)
    if not path.exists() or not main_path.exists() or not refs_path.exists() or not reference_audit_path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == CITATION_CONTEXT_AUDIT_FIELDS, f"{CITATION_CONTEXT_AUDIT} header drifted: {header}", errors)

    tex_text = main_path.read_text(encoding="utf-8", errors="replace")
    normalized_tex = normalize_manuscript_anchor_text(tex_text)
    expected_contexts = extract_manuscript_citation_contexts(tex_text)
    require(
        len(rows) == len(expected_contexts),
        f"{CITATION_CONTEXT_AUDIT} row count drifted: {len(rows)} != {len(expected_contexts)}",
        errors,
    )

    bib_entries = extract_bib_entries(refs_path.read_text(encoding="utf-8", errors="replace"))
    reference_rows = {row.get("bib_key", ""): row for row in read_csv(reference_audit_path)}
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        citation_id = row.get("citation_id", "")
        expected_id = f"CCA-{index:03d}"
        require(citation_id == expected_id, f"{CITATION_CONTEXT_AUDIT} citation_id drifted at row {index}: {citation_id!r}", errors)
        require(citation_id not in seen_ids, f"{CITATION_CONTEXT_AUDIT} duplicated citation_id: {citation_id}", errors)
        seen_ids.add(citation_id)

        if index <= len(expected_contexts):
            expected = expected_contexts[index - 1]
            require(
                row.get("main_tex_line") == expected["main_tex_line"],
                f"{citation_id} main_tex_line drifted: {row.get('main_tex_line')!r} != {expected['main_tex_line']}",
                errors,
            )
            require(
                row.get("cited_keys") == expected["cited_keys"],
                f"{citation_id} cited_keys drifted: {row.get('cited_keys')!r} != {expected['cited_keys']!r}",
                errors,
            )

        require(bool(row.get("paper_section", "").strip()), f"{citation_id} missing paper_section", errors)
        require(bool(row.get("expected_source_support", "").strip()), f"{citation_id} missing expected_source_support", errors)
        require(bool(row.get("manuscript_claim_role", "").strip()), f"{citation_id} missing manuscript_claim_role", errors)
        require(row.get("audit_status") == "pass_context_inventory", f"{citation_id} audit_status is not pass_context_inventory", errors)
        require(
            row.get("source_content_status") == "metadata_verified; full-text L3 pending",
            f"{citation_id} source_content_status must remain metadata_verified with full-text L3 pending",
            errors,
        )
        require(bool(row.get("boundary_note", "").strip()), f"{citation_id} missing boundary_note", errors)
        require(
            "full-text verified" not in row.get("source_content_status", "").lower(),
            f"{citation_id} must not claim full-text verification",
            errors,
        )

        anchor = normalize_manuscript_anchor_text(row.get("claim_text_anchor", ""))
        require(bool(anchor), f"{citation_id} missing claim_text_anchor", errors)
        if anchor:
            require(anchor in normalized_tex, f"{citation_id} claim_text_anchor not found in main.tex", errors)

        keys = [key.strip() for key in row.get("cited_keys", "").split(";") if key.strip()]
        require(bool(keys), f"{citation_id} missing cited_keys", errors)
        for key in keys:
            require(key in bib_entries, f"{citation_id} cites missing refs.bib key: {key}", errors)
            ref_row = reference_rows.get(key)
            require(ref_row is not None, f"{citation_id} cites key missing from reference integrity audit: {key}", errors)
            if ref_row:
                require(ref_row.get("verification_status") == "verified", f"{citation_id}/{key} reference verification is not verified", errors)
                require(ref_row.get("metadata_status") == "verified", f"{citation_id}/{key} reference metadata is not verified", errors)

        if "jeon2026mofit" in keys:
            require("support-only" in row.get("boundary_note", ""), f"{citation_id} lost MoFit support-only boundary", errors)
        if "tracingroots2025" in keys:
            require("feature-packet" in row.get("boundary_note", ""), f"{citation_id} lost Tracing Roots feature-packet boundary", errors)


def validate_false_promotion_gate_summary(paper: Path, errors: list[str]) -> None:
    """Keep the C14 author-keyed gate-summary claims tied to generated data."""

    path = paper / FALSE_PROMOTION_GATE_SUMMARY
    require(path.exists(), f"{FALSE_PROMOTION_GATE_SUMMARY} is missing", errors)
    if not path.exists():
        return

    header, rows = read_csv_with_header(path)
    require(header == FALSE_PROMOTION_GATE_SUMMARY_FIELDS, f"{FALSE_PROMOTION_GATE_SUMMARY} header drifted: {header}", errors)
    expected_keys = set(FALSE_PROMOTION_REQUIRED_GATE_COUNTS)
    require(
        len(rows) == len(expected_keys),
        f"{FALSE_PROMOTION_GATE_SUMMARY} row count drifted: {len(rows)}",
        errors,
    )
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row.get("gate", ""), row.get("outcome", ""))
        require(
            key[0] in FALSE_PROMOTION_AUTHOR_GATES,
            f"{FALSE_PROMOTION_GATE_SUMMARY} unknown gate: {key[0]!r}",
            errors,
        )
        require(
            key[1] in FALSE_PROMOTION_GATE_OUTCOMES,
            f"{FALSE_PROMOTION_GATE_SUMMARY} unknown outcome: {key[1]!r}",
            errors,
        )
        require(key not in by_key, f"{FALSE_PROMOTION_GATE_SUMMARY} duplicated row: {key}", errors)
        by_key[key] = row
        require(
            row.get("selected_row_count") == str(FALSE_PROMOTION_EXPECTED_SELECTED_ROW_COUNT),
            f"{key[0]}/{key[1]} selected_row_count drifted: {row.get('selected_row_count')!r}",
            errors,
        )
        require(
            "not external reliability or prevalence evidence" in row.get("boundary_note", ""),
            f"{key[0]}/{key[1]} boundary note lost non-reliability/prevalence scope",
            errors,
        )

    missing_keys = sorted(expected_keys - set(by_key))
    extra_keys = sorted(set(by_key) - expected_keys)
    require(not missing_keys, f"{FALSE_PROMOTION_GATE_SUMMARY} missing required rows: {missing_keys}", errors)
    require(not extra_keys, f"{FALSE_PROMOTION_GATE_SUMMARY} has unexpected rows: {extra_keys}", errors)

    for key, expected_count in FALSE_PROMOTION_REQUIRED_GATE_COUNTS.items():
        row = by_key.get(key)
        if row is None:
            continue
        require(
            row.get("count") == str(expected_count),
            f"{key[0]}/{key[1]} count drifted: {row.get('count')!r}",
            errors,
        )

    matrix_path = paper / FALSE_PROMOTION_AUTHOR_GATE_MATRIX
    require(matrix_path.exists(), f"{FALSE_PROMOTION_AUTHOR_GATE_MATRIX} is missing", errors)
    if not matrix_path.exists():
        return

    matrix_rows = read_csv(matrix_path)
    require(
        len(matrix_rows) == FALSE_PROMOTION_EXPECTED_SELECTED_ROW_COUNT,
        f"{FALSE_PROMOTION_AUTHOR_GATE_MATRIX} row count drifted: {len(matrix_rows)}",
        errors,
    )
    matrix_counts = {key: 0 for key in expected_keys}
    for index, matrix_row in enumerate(matrix_rows, start=1):
        for gate in FALSE_PROMOTION_AUTHOR_GATES:
            outcome = matrix_row.get(gate, "")
            require(
                outcome in FALSE_PROMOTION_GATE_OUTCOMES,
                f"{FALSE_PROMOTION_AUTHOR_GATE_MATRIX} row {index} {gate} unknown outcome: {outcome!r}",
                errors,
            )
            if outcome in FALSE_PROMOTION_GATE_OUTCOMES:
                matrix_counts[(gate, outcome)] += 1

    for key, expected_count in FALSE_PROMOTION_REQUIRED_GATE_COUNTS.items():
        require(
            matrix_counts.get(key) == expected_count,
            f"{FALSE_PROMOTION_AUTHOR_GATE_MATRIX} {key[0]}/{key[1]} count drifted: {matrix_counts.get(key)!r}",
            errors,
        )
        row = by_key.get(key)
        if row is not None:
            require(
                row.get("count") == str(matrix_counts.get(key)),
                f"{FALSE_PROMOTION_GATE_SUMMARY} {key[0]}/{key[1]} disagrees with author matrix",
                errors,
            )


def validate_pdf(paper: Path, errors: list[str]) -> None:
    paper = paper.resolve()
    pdf_path = paper / "paper.pdf"
    require(pdf_path.exists(), "paper.pdf is missing", errors)
    if not pdf_path.exists():
        return
    build_pdf = paper / "build" / "main.pdf"
    if build_pdf.exists():
        require(
            sha256_file(pdf_path) == sha256_file(build_pdf),
            "paper.pdf does not match build/main.pdf; copy the fresh build output",
            errors,
        )

    pdfinfo = run_text(["pdfinfo", str(pdf_path)], paper)
    pages_match = re.search(r"^Pages:\s+(\d+)$", pdfinfo, flags=re.MULTILINE)
    require(bool(pages_match), "pdfinfo output missing Pages", errors)
    if pages_match:
        pages = int(pages_match.group(1))
        require(1 <= pages <= 10, f"paper.pdf page count out of conference guardrail: {pages}", errors)
    require("Page size:       612 x 792 pts (letter)" in pdfinfo, "paper.pdf is not letter size", errors)

    fonts = run_text(["pdffonts", str(pdf_path)], paper)
    require("Type 3" not in fonts, "paper.pdf contains Type 3 fonts", errors)

    text = run_text(["pdftotext", str(pdf_path), "-"], paper)
    for pattern in PDF_FORBIDDEN_PATTERNS:
        require(not re.search(pattern, text, flags=re.IGNORECASE), f"paper.pdf forbidden text hit: {pattern}", errors)
    for pattern in PDF_REQUIRED_PATTERNS:
        require(
            bool(re.search(pattern, text, flags=re.IGNORECASE)),
            f"paper.pdf missing expected release/claim phrase: {pattern}",
            errors,
        )


def validate_latex_log(paper: Path, errors: list[str]) -> None:
    log_path = paper / "build" / "main.log"
    require(log_path.exists(), "build/main.log is missing", errors)
    if not log_path.exists():
        return
    text = log_path.read_text(encoding="utf-8", errors="replace")
    for pattern in LOG_FORBIDDEN_PATTERNS:
        require(not re.search(pattern, text, flags=re.IGNORECASE), f"LaTeX log forbidden hit: {pattern}", errors)


def validate_release_docs(paper: Path, errors: list[str]) -> None:
    for rel_path in RELEASE_DOCS:
        path = paper / rel_path
        require(path.exists(), f"{rel_path} is missing", errors)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in RELEASE_DOC_FORBIDDEN_PATTERNS:
            require(
                not re.search(pattern, text, flags=re.IGNORECASE),
                f"{rel_path} forbidden stale wording hit: {pattern}",
                errors,
            )


def validate_generated_text_boundaries(paper: Path, errors: list[str]) -> None:
    for rel_path in GENERATED_TEXT_SURFACES:
        path = paper / rel_path
        require(path.exists(), f"{rel_path} is missing", errors)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in GENERATED_TEXT_FORBIDDEN_PATTERNS:
            require(
                not re.search(pattern, text, flags=re.IGNORECASE),
                f"{rel_path} forbidden stale generated wording hit: {pattern}",
                errors,
            )


def validate_manuscript_claim_boundaries(paper: Path, errors: list[str]) -> None:
    tex_path = paper / "main.tex"
    require(tex_path.exists(), "main.tex is missing", errors)
    if not tex_path.exists():
        return

    text = tex_path.read_text(encoding="utf-8", errors="replace")
    for pattern, message in MANUSCRIPT_REQUIRED_PATTERNS:
        require(
            bool(re.search(pattern, text, flags=re.IGNORECASE)),
            message,
            errors,
        )
    for pattern, message in MANUSCRIPT_FORBIDDEN_PATTERNS:
        require(
            not re.search(pattern, text, flags=re.IGNORECASE),
            message,
            errors,
        )


def extract_bib_entries(refs_text: str) -> dict[str, str]:
    matches = list(BIB_ENTRY_RE.finditer(refs_text))
    entries: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1)
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(refs_text)
        entries[key] = refs_text[start:end]
    return entries


def bib_entry_has_field(entry: str, field: str) -> bool:
    return bool(re.search(rf"(?im)^\s*{re.escape(field)}\s*=", entry))


def bib_entry_field_value(entry: str, field: str) -> str:
    match = re.search(rf"(?im)^\s*{re.escape(field)}\s*=\s*(.+?)\s*,?\s*$", entry)
    if not match:
        return ""
    value = match.group(1).strip()
    if (value.startswith("{") and value.endswith("}")) or (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
    return value.strip()


def bib_entry_type(entry: str) -> str:
    match = re.match(r"@\s*(\w+)\s*\{", entry)
    return match.group(1).lower() if match else ""


def validate_bibliography(paper: Path, errors: list[str]) -> None:
    tex_path = paper / "main.tex"
    refs_path = paper / "refs.bib"
    require(tex_path.exists(), "main.tex is missing", errors)
    require(refs_path.exists(), "refs.bib is missing", errors)
    if not tex_path.exists() or not refs_path.exists():
        return

    tex = tex_path.read_text(encoding="utf-8", errors="replace")
    refs_text = refs_path.read_text(encoding="utf-8", errors="replace")
    cited_keys = {
        key.strip()
        for match in CITATION_COMMAND_RE.finditer(tex)
        for key in match.group(1).split(",")
        if key.strip()
    }
    bib_entries = extract_bib_entries(refs_text)
    bib_keys = set(bib_entries)

    require(bool(cited_keys), "main.tex has no citation commands", errors)
    missing = sorted(cited_keys - bib_keys)
    unused = sorted(bib_keys - cited_keys)
    require(not missing, f"refs.bib missing cited keys: {', '.join(missing)}", errors)
    require(not unused, f"refs.bib contains uncited entries: {', '.join(unused)}", errors)

    for key in sorted(cited_keys & bib_keys):
        entry = bib_entries[key]
        for field in BIB_REQUIRED_FIELDS:
            require(bib_entry_has_field(entry, field), f"{key} missing BibTeX field: {field}", errors)
        if re.match(r"(?i)@inproceedings", entry):
            require(bib_entry_has_field(entry, "booktitle"), f"{key} inproceedings entry missing booktitle", errors)
        if re.match(r"(?i)@article", entry):
            require(bib_entry_has_field(entry, "journal"), f"{key} article entry missing journal", errors)
        if re.match(r"(?i)@misc", entry):
            require(
                any(bib_entry_has_field(entry, field) for field in ("eprint", "url", "note")),
                f"{key} misc entry needs eprint, url, or note",
                errors,
            )
        require(not BIB_PLACEHOLDER_RE.search(entry), f"{key} contains placeholder BibTeX text", errors)


def validate_reference_integrity_audit(paper: Path, errors: list[str]) -> None:
    refs_path = paper / "refs.bib"
    audit_path = paper / REFERENCE_INTEGRITY_AUDIT
    require(refs_path.exists(), "refs.bib is missing", errors)
    require(audit_path.exists(), f"{REFERENCE_INTEGRITY_AUDIT} is missing", errors)
    if not refs_path.exists() or not audit_path.exists():
        return

    refs_text = refs_path.read_text(encoding="utf-8", errors="replace")
    bib_entries = extract_bib_entries(refs_text)
    header, rows = read_csv_with_header(audit_path)
    require(header == REFERENCE_INTEGRITY_FIELDS, f"{REFERENCE_INTEGRITY_AUDIT} header drifted: {header}", errors)
    rows_by_key: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get("bib_key", "")
        require(bool(key), f"{REFERENCE_INTEGRITY_AUDIT} row missing bib_key", errors)
        require(key not in rows_by_key, f"{REFERENCE_INTEGRITY_AUDIT} duplicated bib_key: {key}", errors)
        if key:
            rows_by_key[key] = row

    missing = sorted(set(bib_entries) - set(rows_by_key))
    extra = sorted(set(rows_by_key) - set(bib_entries))
    require(not missing, f"{REFERENCE_INTEGRITY_AUDIT} missing BibTeX keys: {', '.join(missing)}", errors)
    require(not extra, f"{REFERENCE_INTEGRITY_AUDIT} contains non-BibTeX keys: {', '.join(extra)}", errors)

    for key in sorted(set(bib_entries) & set(rows_by_key)):
        entry = bib_entries[key]
        row = rows_by_key[key]
        require(row.get("entry_type") == bib_entry_type(entry), f"{key} reference audit entry_type drifted: {row.get('entry_type')!r}", errors)
        require(row.get("title") == bib_entry_field_value(entry, "title"), f"{key} reference audit title drifted: {row.get('title')!r}", errors)
        require(row.get("year") == bib_entry_field_value(entry, "year"), f"{key} reference audit year drifted: {row.get('year')!r}", errors)
        require(row.get("verification_status") == "verified", f"{key} reference verification is not verified", errors)
        require(row.get("metadata_status") == "verified", f"{key} reference metadata is not verified", errors)
        require(bool(row.get("metadata_source", "").strip()), f"{key} reference audit missing metadata_source", errors)
        require(bool(row.get("metadata_note", "").strip()), f"{key} reference audit missing metadata_note", errors)
        require(row.get("identifier_kind") in REFERENCE_IDENTIFIER_KINDS, f"{key} has invalid reference identifier_kind: {row.get('identifier_kind')!r}", errors)
        require(bool(row.get("identifier_value", "").strip()), f"{key} reference audit missing identifier_value", errors)
        require(row.get("verification_url", "").startswith("https://"), f"{key} reference audit missing https verification_url", errors)
        require(bool(re.fullmatch(r"\d{3}", row.get("http_status", ""))), f"{key} reference audit has invalid http_status: {row.get('http_status')!r}", errors)
        require(bool(row.get("checked_at_utc", "").strip()), f"{key} reference audit missing checked_at_utc", errors)

        doi = bib_entry_field_value(entry, "doi")
        eprint = bib_entry_field_value(entry, "eprint")
        archive_prefix = bib_entry_field_value(entry, "archivePrefix").lower()
        url = bib_entry_field_value(entry, "url")
        if eprint and archive_prefix == "arxiv" and doi.lower().startswith("10.48550/arxiv."):
            require(row.get("identifier_kind") == "arxiv_abs", f"{key} arXiv-backed reference must use arxiv_abs audit", errors)
            require(row.get("identifier_value") == eprint, f"{key} reference audit arXiv id drifted: {row.get('identifier_value')!r}", errors)
        elif doi:
            require(row.get("identifier_kind") == "doi_handle", f"{key} DOI-backed reference must use doi_handle audit", errors)
            require(row.get("identifier_value") == doi, f"{key} reference audit DOI drifted: {row.get('identifier_value')!r}", errors)
        elif eprint and archive_prefix == "arxiv":
            require(row.get("identifier_kind") == "arxiv_abs", f"{key} arXiv-backed reference must use arxiv_abs audit", errors)
            require(row.get("identifier_value") == eprint, f"{key} reference audit arXiv id drifted: {row.get('identifier_value')!r}", errors)
        else:
            require(bool(url), f"{key} has no DOI, arXiv eprint, or URL for reference verification", errors)
            require(row.get("identifier_kind") == "url", f"{key} URL-backed reference must use url audit", errors)
            require(row.get("identifier_value") == url, f"{key} reference audit URL drifted: {row.get('identifier_value')!r}", errors)


def validate_optional_supplement_zip(paper: Path, manifest: dict, errors: list[str]) -> None:
    build_dir = paper / "build"
    zip_path = build_dir / SUPPLEMENT_ZIP
    if not zip_path.exists():
        return

    manifest_path = build_dir / SUPPLEMENT_MANIFEST
    sha_path = build_dir / f"{SUPPLEMENT_ZIP}.sha256"
    require(manifest_path.exists(), f"{SUPPLEMENT_MANIFEST} is missing next to supplement ZIP", errors)
    require(sha_path.exists(), f"{SUPPLEMENT_ZIP}.sha256 is missing", errors)
    if not manifest_path.exists():
        return

    rows = read_csv(manifest_path)
    expected_rows = expected_supplement_rows(paper, manifest, errors)
    require(rows == expected_rows, "supplement manifest does not match current asset_manifest inputs", errors)
    expected_entries = {row.get("archive_name", "") for row in rows}
    expected_entries.add(f"{SUPPLEMENT_ROOT}/SUPPLEMENT_MANIFEST.csv")
    require("" not in expected_entries, f"{SUPPLEMENT_MANIFEST} has an empty archive_name", errors)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive_entries = set(archive.namelist())
        require(archive_entries == expected_entries, "supplement ZIP entries do not match supplement manifest", errors)
        for row in rows:
            archive_name = row["archive_name"]
            payload = archive.read(archive_name)
            require(str(len(payload)) == row["size_bytes"], f"{archive_name} size does not match supplement manifest", errors)
            require(sha256_bytes(payload) == row["sha256"], f"{archive_name} sha256 does not match supplement manifest", errors)
        require(
            archive.read(f"{SUPPLEMENT_ROOT}/SUPPLEMENT_MANIFEST.csv") == manifest_path.read_bytes(),
            "ZIP SUPPLEMENT_MANIFEST.csv does not match local supplement manifest",
            errors,
        )

    if sha_path.exists():
        expected_sha = sha_path.read_text(encoding="utf-8").split()[0]
        require(sha256_file(zip_path) == expected_sha, f"{SUPPLEMENT_ZIP}.sha256 does not match ZIP bytes", errors)


def discover_c14_reviewer_files(paper: Path) -> list[Path]:
    review_dir = paper / "build" / C14_REVIEW_DIR
    if not review_dir.exists():
        return []
    files: list[Path] = []
    for pattern in C14_REVIEW_FILE_GLOBS:
        files.extend(review_dir.glob(pattern))
    return sorted(path for path in set(files) if path.is_file())


def parse_int_field(row: dict[str, str], field: str, errors: list[str]) -> int | None:
    value = row.get(field, "")
    try:
        return int(value)
    except ValueError:
        require(False, f"C14 status field {field} is not an integer: {value!r}", errors)
        return None


def read_sha256_sidecar(path: Path, errors: list[str], label: str) -> str:
    require(path.exists(), f"{label} sha256 sidecar is missing: {path}", errors)
    if not path.exists():
        return ""
    tokens = path.read_text(encoding="utf-8", errors="replace").split()
    require(bool(tokens), f"{label} sha256 sidecar is empty: {path}", errors)
    if not tokens:
        return ""
    first_token = tokens[0].lower()
    require(bool(re.fullmatch(r"[0-9a-f]{64}", first_token)), f"{label} sha256 sidecar has invalid SHA-256: {first_token!r}", errors)
    return first_token


def validate_c14_dispatch_note(paper: Path, repo_root: Path, errors: list[str]) -> None:
    """Keep the reviewer dispatch note aligned with the current C14 ZIP bytes."""

    dispatch_path = repo_root / C14_DISPATCH_NOTE
    review_zip = paper / C14_REVIEW_BUNDLE_ZIP
    post_label_zip = paper / C14_POST_LABEL_KEY_ZIP
    review_sha_path = review_zip.with_name(f"{review_zip.name}.sha256")
    post_label_sha_path = post_label_zip.with_name(f"{post_label_zip.name}.sha256")

    require(dispatch_path.exists(), f"{C14_DISPATCH_NOTE} is missing", errors)
    require(review_zip.exists(), f"{C14_REVIEW_BUNDLE_ZIP} is missing", errors)
    require(post_label_zip.exists(), f"{C14_POST_LABEL_KEY_ZIP} is missing", errors)
    if not dispatch_path.exists():
        return

    review_sidecar_sha = read_sha256_sidecar(review_sha_path, errors, "C14 review bundle")
    post_label_sidecar_sha = read_sha256_sidecar(post_label_sha_path, errors, "C14 post-label key")
    review_zip_sha = sha256_file(review_zip) if review_zip.exists() else ""
    post_label_zip_sha = sha256_file(post_label_zip) if post_label_zip.exists() else ""

    if review_sidecar_sha and review_zip_sha:
        require(review_sidecar_sha == review_zip_sha, "C14 review bundle sha256 sidecar does not match ZIP bytes", errors)
    if post_label_sidecar_sha and post_label_zip_sha:
        require(post_label_sidecar_sha == post_label_zip_sha, "C14 post-label key sha256 sidecar does not match ZIP bytes", errors)

    expected_review_sha = review_zip_sha or review_sidecar_sha
    expected_post_label_sha = post_label_zip_sha or post_label_sidecar_sha
    text = dispatch_path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()

    for phrase in C14_DISPATCH_REQUIRED_PHRASES:
        require(phrase in text, f"{C14_DISPATCH_NOTE} lost dispatch phrase: {phrase}", errors)
    if expected_review_sha:
        require(expected_review_sha in lowered, f"{C14_DISPATCH_NOTE} missing current review bundle SHA-256", errors)
    if expected_post_label_sha:
        require(expected_post_label_sha in lowered, f"{C14_DISPATCH_NOTE} missing current post-label key SHA-256", errors)

    allowed_hashes = {hash_value for hash_value in [expected_review_sha, expected_post_label_sha] if hash_value}
    observed_hashes = set(re.findall(r"\b[0-9a-f]{64}\b", lowered))
    stale_hashes = sorted(observed_hashes - allowed_hashes)
    for hash_value in stale_hashes:
        require(False, f"{C14_DISPATCH_NOTE} contains stale or unexpected SHA-256: {hash_value}", errors)


def validate_c14_external_review_status(
    paper: Path,
    errors: list[str],
    *,
    review_state: str = "pre-label",
) -> None:
    """Keep the C14 release packet honest before or after reviewer labels."""

    build_dir = paper / "build"
    status_path = build_dir / C14_PACKET_STATUS
    markdown_path = build_dir / C14_AGGREGATION_MD
    reviewer_files = discover_c14_reviewer_files(paper)

    require(status_path.exists(), f"{C14_PACKET_STATUS} is missing", errors)
    require(markdown_path.exists(), f"{C14_AGGREGATION_MD} is missing", errors)
    if not status_path.exists() or not markdown_path.exists():
        return

    header, rows = read_csv_with_header(status_path)
    require(header == C14_PACKET_STATUS_FIELDS, f"{C14_PACKET_STATUS} header drifted: {header}", errors)
    require(len(rows) == 1, f"{C14_PACKET_STATUS} must contain exactly one status row", errors)
    if not rows:
        return

    row = rows[0]
    for field in [
        "completed_external_adjudication_allowed",
        "reliability_claim_allowed",
        "compute_release_allowed",
    ]:
        require(row.get(field) == "0", f"C14 status must keep {field}=0", errors)

    text = markdown_path.read_text(encoding="utf-8", errors="replace")
    require(
        "not external adjudication" in text or "not completed external adjudication" in text,
        f"{C14_AGGREGATION_MD} lost external-adjudication boundary text",
        errors,
    )

    if review_state == "pre-label":
        require(
            not reviewer_files,
            "C14 reviewer CSVs are not allowed in the current packet_ready_only release",
            errors,
        )
        for field, expected in C14_NO_REVIEWER_STATUS.items():
            require(
                row.get(field) == expected,
                f"C14 no-reviewer status drifted for {field}: {row.get(field)!r}",
                errors,
            )
        for filename in C14_LABEL_DEPENDENT_OUTPUTS:
            require(
                not (build_dir / filename).exists(),
                f"C14 label-dependent output exists without reviewer CSVs: {filename}",
                errors,
            )
        require(
            "No reviewer CSVs were loaded" in text,
            f"{C14_AGGREGATION_MD} lost no-reviewer boundary text",
            errors,
        )
        return

    require(review_state == "post-label", f"unknown C14 review state: {review_state}", errors)
    if review_state != "post-label":
        return

    n_reviewers = parse_int_field(row, "n_reviewers", errors)
    min_reviewers = parse_int_field(row, "min_reviewers", errors)
    require(bool(reviewer_files), "C14 post-label release requires reviewer CSVs", errors)
    if n_reviewers is not None and min_reviewers is not None:
        require(n_reviewers >= min_reviewers, "C14 post-label release requires n_reviewers >= min_reviewers", errors)
        require(
            len(reviewer_files) == n_reviewers,
            f"C14 reviewer CSV count {len(reviewer_files)} does not match n_reviewers={n_reviewers}",
            errors,
        )
    require(row.get("packet_label_readiness") == "review_csvs_available", "C14 post-label status must be review_csvs_available", errors)
    require(row.get("external_label_aggregation_available") == "1", "C14 post-label release requires external_label_aggregation_available=1", errors)
    require(row.get("declaration_status") == "valid_independence_attestation", "C14 post-label release requires valid independence declarations", errors)
    require(
        any(row.get("allowed_claim_scope", "").startswith(prefix) for prefix in C14_POST_LABEL_ALLOWED_CLAIM_SCOPE_PREFIXES),
        f"C14 post-label allowed_claim_scope is not selected-row bounded: {row.get('allowed_claim_scope')!r}",
        errors,
    )
    for filename in C14_LABEL_DEPENDENT_OUTPUTS:
        require(
            (build_dir / filename).exists(),
            f"C14 post-label release is missing label-dependent output: {filename}",
            errors,
        )
    require(
        "Reviewers loaded:" in text,
        f"{C14_AGGREGATION_MD} lost post-label reviewer summary",
        errors,
    )
    require(
        "Majority labels can support a future external-label statement only for the supplied reviewers and the selected rows" in text,
        f"{C14_AGGREGATION_MD} lost selected-row reporting boundary",
        errors,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--c14-review-state",
        choices=["pre-label", "post-label"],
        default="pre-label",
        help=(
            "pre-label keeps the current packet_ready_only release gate; "
            "post-label permits completed reviewer CSV inputs only as a "
            "selected-row external-label aggregation with adjudication, "
            "reliability, and compute-release claim switches still disabled"
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    paper = repo_root / "papers" / "diffaudit-evidence-paper"
    errors: list[str] = []

    manifest = validate_manifest(paper, errors)
    validate_claim_trace(paper, repo_root, errors)
    validate_review_snapshot_manifest(paper, repo_root, manifest, errors)
    validate_mofit_gate_status(paper, errors)
    validate_stl10_route_summary(paper, errors)
    validate_report_correctness_fault_matrix(paper, errors)
    validate_manuscript_claim_audit(paper, errors)
    validate_citation_context_audit(paper, errors)
    validate_false_promotion_gate_summary(paper, errors)
    validate_pdf(paper, errors)
    validate_latex_log(paper, errors)
    validate_release_docs(paper, errors)
    validate_generated_text_boundaries(paper, errors)
    validate_manuscript_claim_boundaries(paper, errors)
    validate_bibliography(paper, errors)
    validate_reference_integrity_audit(paper, errors)
    validate_optional_supplement_zip(paper, manifest, errors)
    validate_c14_dispatch_note(paper, repo_root, errors)
    validate_c14_external_review_status(paper, errors, review_state=args.c14_review_state)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Paper release packet check passed.")


if __name__ == "__main__":
    main()
