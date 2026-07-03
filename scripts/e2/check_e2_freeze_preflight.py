"""Validate the E2 freeze-preflight boundary tables.

This is a fast, offline guard. It prevents the current 2026-06-06 E2 preflight
state from being accidentally described as a frozen external denominator.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
PAPER = ROOT / "papers" / "diffaudit-evidence-paper"

REVIEW_DECISION_FIELDS = {
    "review_id",
    "source_queue_id",
    "source_seed_id",
    "source_kind",
    "title",
    "surface_family",
    "modality",
    "canonical_source_url",
    "artifact_access_mode",
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "provenance_gate",
    "consumer_or_delta_gate",
    "duplicate_policy",
    "adjudication_readiness",
    "verdict",
    "first_blocker",
    "next_artifact_check",
    "allowed_wording",
}

VALID_GATES = {"Pass", "Partial", "Fail", "N/A"}
CURRENT_NON_DENOMINATOR_VERDICTS = {
    "backup_artifact_followup",
    "backup_only",
    "backup_support",
    "bounded_cross_domain_support",
    "bounded_support",
    "exclude_backup",
    "exclude_related_method",
    "package_work_candidate_not_denominator",
}

REVIEW_TEMPLATE_FIELDS = [
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

FALSE_PROMOTION_PACKET_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "exemplar_type",
    "weak_rules_under_test",
    "public_surface_that_looks_strong",
    "contract_blocker_claimed",
    "source_allowed_wording",
    "source_no_compute_release",
    "review_question",
    "packet_status",
    "reviewer",
    "external_decision",
    "external_notes",
]

FALSE_PROMOTION_BLINDED_PACKET_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "weak_surface_family",
    "weak_rules_under_test",
    "public_surface_observation",
    "review_question",
    "packet_status",
]

FALSE_PROMOTION_ADJUDICATION_KEY_FIELDS = [
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

FALSE_PROMOTION_TEMPLATE_FIELDS = [
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

FALSE_PROMOTION_ROW_TRACE_FIELDS = [
    "review_id",
    "source_row_id",
    "title",
    "observed_at",
    "public_urls",
    "source_check_csv",
    "source_check_csv_sha256",
    "source_check_md",
    "source_check_md_sha256",
    "source_summary_row_sha256",
    "trace_status",
    "review_boundary",
]

FALSE_PROMOTION_AUTHOR_GATE_MATRIX_FIELDS = [
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

FALSE_PROMOTION_AUTHOR_GATE_SUMMARY_FIELDS = [
    "gate",
    "outcome",
    "count",
    "selected_row_count",
    "boundary_note",
]

FALSE_PROMOTION_AUTHOR_GATE_FIELDS = [
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
]

FALSE_PROMOTION_VERDICT_VALUES = {
    "false_promotion_control",
    "semantic_boundary_block",
    "artifact_surface_block",
    "needs_external_adjudication",
    "invalid_row",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing required E2 preflight file: {path}")
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def require_fields(rows: list[dict[str, str]], required: set[str], name: str) -> None:
    fields = set(rows[0].keys()) if rows else set()
    missing = sorted(required - fields)
    require(not missing, f"{name} missing required fields: {', '.join(missing)}")


def main() -> int:
    review_rows = read_csv(PREFLIGHT / "e2_n50_freeze_review_decisions_v1.csv")
    require_fields(review_rows, REVIEW_DECISION_FIELDS, "e2_n50_freeze_review_decisions_v1.csv")
    require(len(review_rows) == 16, f"Expected 16 reviewed E2 rows, got {len(review_rows)}")

    verdicts = {row["verdict"] for row in review_rows}
    unexpected_verdicts = sorted(verdicts - CURRENT_NON_DENOMINATOR_VERDICTS)
    require(
        not unexpected_verdicts,
        "Unexpected denominator-like E2 review verdicts: " + ", ".join(unexpected_verdicts),
    )
    for row in review_rows:
        for field in [
            "target_gate",
            "split_gate",
            "score_or_response_gate",
            "metric_gate",
            "provenance_gate",
            "consumer_or_delta_gate",
        ]:
            require(row[field] in VALID_GATES, f"Invalid {field}={row[field]!r} for {row['source_queue_id']}")

    e2q005 = [row for row in review_rows if row["source_queue_id"] == "E2Q-005"]
    require(len(e2q005) == 1, "Expected exactly one E2Q-005 review row")
    require(
        e2q005[0]["verdict"] == "package_work_candidate_not_denominator",
        "E2Q-005 must remain package_work_candidate_not_denominator in this preflight",
    )
    require(
        e2q005[0]["adjudication_readiness"] == "priority_package_check_not_denominator",
        "E2Q-005 adjudication_readiness must remain priority_package_check_not_denominator",
    )

    package_rows = read_csv(PREFLIGHT / "e2q005_tracing_roots_package_check_2026_06_06.csv")
    package_items = {row["item"]: row for row in package_rows}
    require("replay_metric_json" in package_items, "E2Q-005 package check missing replay_metric_json")
    require(
        package_items["replay_metric_json"]["status"] == "pass",
        "E2Q-005 replay_metric_json package check must pass",
    )

    template_rows = read_csv(PREFLIGHT / "e2q005_external_style_review_template_2026_06_06.csv")
    require(list(template_rows[0].keys()) == REVIEW_TEMPLATE_FIELDS, "E2Q-005 review template header drifted")
    require(len(template_rows) == 1, "E2Q-005 review template must contain exactly one review row")
    require(template_rows[0]["pilot_id"] == "E2Q-005", "E2Q-005 review template pilot_id drifted")
    require(
        "feature-packet-only" in template_rows[0]["consumer_question"],
        "E2Q-005 consumer question must keep feature-packet-only boundary",
    )

    reviewer_rows: list[dict[str, str]] = []
    for reviewer in ["G", "H", "I"]:
        path = PREFLIGHT / f"e2q005_external_style_review_{reviewer}_2026_06_06.csv"
        rows = read_csv(path)
        require(len(rows) == 1, f"{path.name} must contain exactly one row")
        row = rows[0]
        require(row["reviewer"] == reviewer, f"{path.name} reviewer drifted")
        require(row["pilot_id"] == "E2Q-005", f"{path.name} pilot_id drifted")
        require(row["allowed_wording"] == "bounded-support", f"{path.name} must keep bounded-support")
        require(row["target_gate"] == "Partial", f"{path.name} target gate must remain Partial")
        require(row["provenance_gate"] == "Partial", f"{path.name} provenance gate must remain Partial")
        reviewer_rows.append(row)

    aggregation = read_csv(PREFLIGHT / "e2q005_external_style_review_aggregation_2026_06_06.csv")
    aggregation_by_field = {row["field"]: row for row in aggregation}
    require(
        aggregation_by_field["allowed_wording"]["majority"] == "bounded-support",
        "E2Q-005 aggregation must keep bounded-support majority",
    )
    require(
        aggregation_by_field["allowed_wording"]["all_agree"] == "1",
        "E2Q-005 allowed wording must have all-reviewer agreement",
    )
    require(
        aggregation_by_field["target_gate"]["majority"] == "Partial",
        "E2Q-005 target gate majority must remain Partial",
    )
    require(
        aggregation_by_field["provenance_gate"]["majority"] == "Partial",
        "E2Q-005 provenance gate majority must remain Partial",
    )
    aggregation_md = (PREFLIGHT / "e2q005_external_style_review_aggregation_2026_06_06.md").read_text(
        encoding="utf-8"
    )
    require("accept_feature_packet_review_row" in aggregation_md, "E2Q-005 aggregation decision missing")
    require("Do not call this N50 evidence" in aggregation_md, "E2Q-005 aggregation lost no-N50 boundary")

    challenger_rows = read_csv(PREFLIGHT / "e2_row_bound_challenger_scout_2026_06_06.csv")
    require(challenger_rows[0]["candidate_id"] == "E2Q-005", "E2Q-005 must remain top challenger row")
    require(
        "not call it N50" in challenger_rows[0]["next_action"],
        "Top challenger next_action must preserve the no-N50 boundary",
    )
    copymark_challenger = [row for row in challenger_rows if row["candidate_id"] == "E2Q-006"]
    require(len(copymark_challenger) == 1, "Expected one E2Q-006 challenger row")
    require(
        "Authenticated no-download recheck" in copymark_challenger[0]["main_blocker"],
        "E2Q-006 challenger row must record the authenticated no-download recheck",
    )

    copymark_rows = read_csv(PREFLIGHT / "e2q006_copymark_compact_manifest_gate_2026_06_06.csv")
    copymark_by_item = {row["item"]: row for row in copymark_rows}
    require(
        copymark_by_item["github_repo_identity"]["status"] == "pass",
        "CopyMark GitHub identity check must pass",
    )
    require(
        copymark_by_item["github_manifest_search"]["status"] == "fail",
        "CopyMark manifest search must remain failed until a compact manifest appears",
    )
    require(
        copymark_by_item["hf_dataset_tree"]["status"] == "fail",
        "CopyMark HF dataset tree must remain failed until manifest-level files appear",
    )
    require(
        copymark_by_item["admission_decision"]["status"] == "fail",
        "CopyMark admission decision must remain fail for the current preflight",
    )

    readme = (PREFLIGHT / "README.md").read_text(encoding="utf-8")
    require(
        "For each row, the next reviewer must decide" not in readme,
        "E2 README still contains the stale pre-v1 row-review instruction",
    )
    require("directly freezable external denominator rows: `0`" in readme, "E2 README lost denominator=0 statement")
    require(
        "e2q005_external_style_review_aggregation_2026_06_06.md" in readme,
        "E2 README must link the E2Q-005 single-row feature-packet review aggregation",
    )
    require(
        "e2q006_copymark_compact_manifest_gate_2026_06_06.md" in readme,
        "E2 README must link the CopyMark compact-manifest gate",
    )
    require(
        "e2_next_route_decision_2026_06_06.md" in readme,
        "E2 README must link the CLiD/MT-MIA next-route decision",
    )
    require(
        "e2_measurement_route_gap_board_2026_06_06.md" in readme,
        "E2 README must link the measurement-route gap board",
    )
    require(
        "e2_false_promotion_expansion_queue_2026_06_07.md" in readme,
        "E2 README must link the post-C14 false-promotion expansion queue",
    )
    require(
        "e2sct029_mia_sd_public_surface_check_2026_06_08.md" in readme
        and "C14-v2 candidate public-result-surface rows" in readme,
        "E2 README must record the E2SCT-029 C14-v2 candidate boundary",
    )
    require(
        "e2sct030_frequency_components_public_surface_check_2026_06_08.md" in readme
        and "support-only" in readme
        and "code-and-split-manifest watch-plus" in readme
        and "not a second public response/score asset" in readme,
        "E2 README must record the E2SCT-030 support-only/no-second-asset boundary",
    )
    require(
        "older `E2SCT-008` scout surface, not a new independent public-surface candidate" in readme,
        "E2 README must record that E2SCT-030 is a current-date recheck, not a new independent candidate",
    )
    require(
        "e2_targeted_public_artifact_discovery_2026_06_08_e.md" in readme
        and "additional current arXiv/GitHub primary-source refresh rows checked in pass E: `5`" in readme,
        "E2 README must list pass E and preserve its five-row current-source refresh count",
    )
    require(
        "e2sct031_sama_dlm_public_surface_check_2026_06_09.md" in readme
        and "Boundary: support-only DLM/text" in readme
        and "public-code surface" in readme
        and "excluded from C14, external denominator, admitted evidence" in readme
        and "second public score/response asset, and compute release" in readme,
        "E2 README must record the E2SCT-031 SAMA support-only/no-second-asset boundary",
    )
    require(
        "e2sct032_miaept_tabular_public_surface_check_2026_06_09.md" in readme
        and "Boundary: support-only tabular-diffusion result-page surface" in readme
        and "result-page surface" in readme
        and "excluded from C14, external denominator, admitted evidence" in readme
        and "second public score/response asset, and compute release" in readme,
        "E2 README must record the E2SCT-032 MIA-EPT support-only/no-second-asset boundary",
    )
    require(
        "additional 2026-06-09 public-code/result-page/code-and-split/aggregate-archive support surfaces checked after pass E: `4`"
        in readme,
        "E2 README must preserve the four-row 2026-06-09 support-check count",
    )
    require(
        "e2sct033_diffusion_mia_public_surface_check_2026_06_09.md" in readme
        and "Boundary: support-only black-box diffusion MIA" in readme
        and "code-and-split surface" in readme
        and "excluded from C14, external denominator, admitted" in readme
        and "second public score/response asset, and compute release" in readme,
        "E2 README must record the E2SCT-033 Diffusion MIA support-only/no-second-asset boundary",
    )
    require(
        "e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md" in readme
        and "Boundary: support-only tabular synthetic-data" in readme
        and "aggregate-result archive" in readme
        and "excluded from C14, external denominator, admitted" in readme
        and "second public score/response asset, and compute release" in readme,
        "E2 README must record the E2SCT-034 ReMIA aggregate-only/no-second-asset boundary",
    )
    require(
        "e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md" in readme
        and "OpenLVLM-MIA status: future VLM controlled-benchmark scout" in readme
        and "excluded from current Direction A, C14/N50, admitted evidence" in readme
        and "second public score/response asset, and compute release" in readme,
        "E2 README must record the E2SCT-035 VLM-scout/no-current-asset boundary",
    )
    require(
        "e2_high_value_public_asset_delta_watchlist_2026_06_09.csv" in readme
        and "e2_high_value_public_asset_delta_refresh_2026_06_09.md" in readme
        and "high-value public asset delta watchlist rows checked on 2026-06-09: `9`" in readme
        and "high-value public asset delta identity matches: `9 / 9`; compact reopen hints: `0`" in readme
        and "new row-bound score/response artifacts found in the high-value public asset delta refresh: `0`" in readme,
        "E2 README must record the high-value delta refresh no-upgrade boundary",
    )
    require(
        "e2_public_source_freeze_ledger_2026_06_09.md" in readme
        and "public-source freeze ledger rows: `11`" in readme
        and "bounded_support=1" in readme
        and "packet_ready_only=1" in readme
        and "no_current_upgrade=9" in readme
        and "compute-release rows: `0`" in readme,
        "E2 README must record the public-source freeze ledger handoff state",
    )
    require(
        "post-C14 expansion queue candidates after" in readme
        and "E2SCT-019" in readme
        and "E2SCT-028" in readme
        and "E2SCT-003" in readme
        and "E2SCT-025" in readme
        and "E2SCT-024" in readme
        and ": `0`" in readme,
        "E2 README must record the empty post-C14 expansion queue count after detailed row checks",
    )
    require(
        "Decide separately whether to open a tabular/relational stratum" not in readme,
        "E2 README still contains the stale MT-MIA decision-needed instruction",
    )
    require(
        "current_cycle_package_status" in readme,
        "E2 README must explain current-cycle package status columns for seed queues",
    )
    require(
        "current_cycle_external_package_no_go" in readme,
        "E2 README must record current-cycle external package No-Go",
    )

    ledger_rows = read_csv(PREFLIGHT / "e2_public_source_freeze_ledger_2026_06_09.csv")
    ledger_by_id = {row["ledger_id"]: row for row in ledger_rows}
    require(len(ledger_rows) == 11, "E2 public-source freeze ledger must contain 11 rows")
    require(len(ledger_by_id) == len(ledger_rows), "E2 public-source freeze ledger has duplicate row IDs")
    require(ledger_by_id["E2Q-005"]["evidence_state"] == "bounded_support", "E2Q-005 ledger state drifted")
    require(
        ledger_by_id["C14-PACKET"]["evidence_state"] == "packet_ready_only",
        "C14 ledger state must remain packet_ready_only",
    )
    require(
        sum(row["evidence_state"] == "no_current_upgrade" for row in ledger_rows) == 9,
        "E2 public-source freeze ledger must keep nine no-current-upgrade rows",
    )
    require(
        all(row["compute_release"] == "no" for row in ledger_rows),
        "E2 public-source freeze ledger must keep compute_release=no for every row",
    )
    high_value_snapshots = {
        row.get("source_refreshed_at_utc", "")
        for row in ledger_rows
        if row.get("evidence_state") == "no_current_upgrade"
    }
    require(
        len(high_value_snapshots) == 1 and all(value.startswith("2026-06-09T") for value in high_value_snapshots),
        "E2 public-source freeze ledger must record one current 2026-06-09 high-value refresh snapshot",
    )
    high_value_snapshot = next(iter(high_value_snapshots), "")
    require(
        high_value_snapshot in readme,
        "E2 README must carry the current late high-value refresh timestamp",
    )
    ledger_md = (PREFLIGHT / "e2_public_source_freeze_ledger_2026_06_09.md").read_text(encoding="utf-8")
    require("ledger rows: `11`" in ledger_md, "E2 public-source freeze ledger markdown lost row count")
    require("high-value refresh snapshot:" in ledger_md, "E2 public-source freeze ledger markdown lost refresh snapshot")
    require(
        high_value_snapshot in ledger_md,
        "E2 public-source freeze ledger markdown timestamp must match the CSV snapshot",
    )
    late_refresh_md = (PREFLIGHT / "e2_high_value_public_asset_delta_refresh_late_2026_06_09.md").read_text(encoding="utf-8")
    require(
        high_value_snapshot in late_refresh_md,
        "E2 late high-value refresh markdown timestamp must match the ledger CSV snapshot",
    )
    require(
        "Current paper-facing state: the C14 packet stays pre-label" in ledger_md,
        "E2 public-source freeze ledger markdown lost paper-facing state",
    )

    actionable_rows = read_csv(PREFLIGHT / "e2_n50_actionable_queue.csv")
    require(actionable_rows, "E2 actionable queue must not be empty")
    for row in actionable_rows:
        queue_id = row["queue_id"]
        require(
            row.get("current_cycle_package_status") == "current_cycle_external_package_no_go",
            f"{queue_id} actionable row must preserve current-cycle package No-Go",
        )
        require(
            "do not package" in row.get("current_cycle_next_action", ""),
            f"{queue_id} actionable row must warn against current-cycle external packaging",
        )
        require(
            row.get("current_cycle_source") == "v1_review_and_post_c14_expansion_queue_2026_06_07",
            f"{queue_id} actionable row must cite the current-cycle source",
        )
    stale_ready_rows = [
        row["queue_id"]
        for row in actionable_rows
        if row.get("freeze_state") == "ready_for_package_after_duplicate_review"
    ]
    require(
        not stale_ready_rows or all(
            row.get("current_cycle_package_status") == "current_cycle_external_package_no_go"
            for row in actionable_rows
            if row["queue_id"] in stale_ready_rows
        ),
        "Seed-preflight ready_for_package rows must be overridden by current-cycle No-Go",
    )

    route_decision = (PREFLIGHT / "e2_next_route_decision_2026_06_06.md").read_text(encoding="utf-8")
    require("CLiD 仍是 identity-missing bounded support" in route_decision, "Route decision lost CLiD no-go")
    require(
        "MT-MIA 不在当前 image-diffusion" in route_decision,
        "Route decision lost MT-MIA current-cycle no-stratum boundary",
    )
    require("Day 5 small run gate 不触发" in route_decision, "Route decision lost no-compute boundary")

    gap_board = (PREFLIGHT / "e2_measurement_route_gap_board_2026_06_06.md").read_text(encoding="utf-8")
    require("denominator 指" in gap_board, "Gap board must define denominator semantics")
    require("不是\n“已 admitted row”" in gap_board, "Gap board must not define denominator as admitted rows")
    require("This\nboard does not admit rows and does not release compute" in readme, "E2 README lost gap-board boundary")

    e2sct004_rows = read_csv(PREFLIGHT / "e2sct004_genai_confessions_public_surface_check_2026_06_06.csv")
    e2sct004_by_item = {row["item"]: row for row in e2sct004_rows}
    require(
        e2sct004_by_item["hf_stroll_annotations"]["status"] == "pass",
        "E2SCT-004 must preserve the public STROLL annotation finding",
    )
    require(
        e2sct004_by_item["generated_outputs_or_dreamsim_scores"]["status"] == "fail",
        "E2SCT-004 must remain blocked without public generated outputs or DreamSim scores",
    )
    require(
        e2sct004_by_item["metric_verifier"]["status"] == "fail",
        "E2SCT-004 must remain blocked without a public metric verifier",
    )
    require(
        "clean false-promotion exemplar candidate only" in e2sct004_by_item["admission_decision"]["evidence"],
        "E2SCT-004 admission decision must stay false-promotion-only",
    )
    require(
        "external-audit denominator" in e2sct004_by_item["admission_decision"]["evidence"],
        "E2SCT-004 admission decision must preserve the no-denominator boundary",
    )
    e2sct004_md = (PREFLIGHT / "e2sct004_genai_confessions_public_surface_check_2026_06_06.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct004_md, "E2SCT-004 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-004` as admitted evidence" in e2sct004_md,
        "E2SCT-004 markdown decision lost no-admission boundary",
    )
    require(
        "does not claim the Zenodo ZIP lacks those files internally" in e2sct004_md,
        "E2SCT-004 markdown must preserve the no-ZIP-content-claim boundary",
    )

    e2sct012_rows = read_csv(PREFLIGHT / "e2sct012_shake_to_leak_public_surface_check_2026_06_06.csv")
    e2sct012_by_item = {row["item"]: row for row in e2sct012_rows}
    require(
        e2sct012_by_item["repo_readme"]["status"] == "pass",
        "E2SCT-012 must preserve the runnable-code public-surface finding",
    )
    require(
        e2sct012_by_item["synthetic_private_set_generation"]["status"] == "fail",
        "E2SCT-012 must remain blocked because the private set is generated at runtime",
    )
    require(
        e2sct012_by_item["finetune_checkpoint_surface"]["status"] == "fail",
        "E2SCT-012 must remain blocked without public fixed checkpoints",
    )
    require(
        e2sct012_by_item["secmi_attack_surface"]["status"] == "fail",
        "E2SCT-012 must remain blocked without public SecMI score artifacts",
    )
    require(
        e2sct012_by_item["score_metric_artifacts"]["status"] == "fail",
        "E2SCT-012 must remain blocked without public score or metric artifacts",
    )
    require(
        "code-availability false-promotion exemplar only" in e2sct012_by_item["admission_decision"]["evidence"],
        "E2SCT-012 admission decision must stay code-availability false-promotion only",
    )
    require(
        "compute release" in e2sct012_by_item["admission_decision"]["evidence"],
        "E2SCT-012 admission decision must preserve the no-compute boundary",
    )
    e2sct012_md = (PREFLIGHT / "e2sct012_shake_to_leak_public_surface_check_2026_06_06.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct012_md, "E2SCT-012 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-012` as admitted evidence" in e2sct012_md,
        "E2SCT-012 markdown decision lost no-admission boundary",
    )
    require(
        "not\nadmitted response/score evidence" in e2sct012_md,
        "E2SCT-012 allowed wording must preserve response/score non-admission",
    )
    require(
        "Do\nnot download Stable Diffusion weights" in e2sct012_md,
        "E2SCT-012 reopen condition must preserve the no-large-download boundary",
    )

    e2sct016_rows = read_csv(PREFLIGHT / "e2sct016_miahold_public_surface_check_2026_06_07.csv")
    e2sct016_by_item = {row["item"]: row for row in e2sct016_rows}
    require(
        e2sct016_by_item["main_readme"]["status"] == "pass",
        "E2SCT-016 must preserve the public HOLD++ codebase finding",
    )
    require(
        e2sct016_by_item["audio_split_filelists"]["status"] == "pass",
        "E2SCT-016 must preserve the public audio split-file finding",
    )
    require(
        e2sct016_by_item["audio_attack_scores"]["status"] == "fail",
        "E2SCT-016 must remain blocked without public audio score artifacts",
    )
    require(
        e2sct016_by_item["cifar_hold_config"]["status"] == "pass",
        "E2SCT-016 must preserve the CIFAR HOLD configuration finding",
    )
    require(
        e2sct016_by_item["cifar_pia_score_artifacts"]["status"] == "fail",
        "E2SCT-016 must remain blocked without public CIFAR PIA score artifacts",
    )
    require(
        e2sct016_by_item["score_metric_artifacts"]["status"] == "fail",
        "E2SCT-016 must remain blocked without public score or metric artifacts",
    )
    require(
        "mixed-modality defense and metric-code false-promotion exemplar only"
        in e2sct016_by_item["admission_decision"]["evidence"],
        "E2SCT-016 admission decision must stay mixed-modality defense false-promotion only",
    )
    require(
        "compute release" in e2sct016_by_item["admission_decision"]["evidence"],
        "E2SCT-016 admission decision must preserve the no-compute boundary",
    )
    e2sct016_md = (PREFLIGHT / "e2sct016_miahold_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct016_md, "E2SCT-016 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-016` as admitted evidence" in e2sct016_md,
        "E2SCT-016 markdown decision lost no-admission boundary",
    )
    require(
        "not admitted response/score or defense-effectiveness\nevidence" in e2sct016_md,
        "E2SCT-016 allowed wording must preserve response/score and defense-effectiveness non-admission",
    )
    require(
        "Do not download Grad-TTS" in e2sct016_md,
        "E2SCT-016 reopen condition must preserve the no-large-download boundary",
    )

    e2sct021_rows = read_csv(PREFLIGHT / "e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.csv")
    e2sct021_by_item = {row["item"]: row for row in e2sct021_rows}
    require(
        e2sct021_by_item["starter_repo"]["status"] == "pass",
        "E2SCT-021 must preserve the public starter-package finding",
    )
    require(
        e2sct021_by_item["root_readme"]["status"] == "pass",
        "E2SCT-021 must preserve the platform-gated dataset finding",
    )
    require(
        e2sct021_by_item["red_team_mia_readme"]["status"] == "pass",
        "E2SCT-021 must preserve the public MIA metric-code finding",
    )
    require(
        e2sct021_by_item["public_example_packet"]["status"] == "pass",
        "E2SCT-021 must preserve the public example-packet finding",
    )
    require(
        e2sct021_by_item["score_metric_artifacts"]["status"] == "partial",
        "E2SCT-021 must remain partial because only starter/example metrics are public",
    )
    require(
        "gated-benchmark and starter-metric false-promotion exemplar only"
        in e2sct021_by_item["admission_decision"]["evidence"],
        "E2SCT-021 admission decision must stay gated-benchmark false-promotion only",
    )
    require(
        "compute release" in e2sct021_by_item["admission_decision"]["evidence"],
        "E2SCT-021 admission decision must preserve the no-compute boundary",
    )
    e2sct021_md = (PREFLIGHT / "e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct021_md, "E2SCT-021 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-021` as admitted evidence" in e2sct021_md,
        "E2SCT-021 markdown decision lost no-admission boundary",
    )
    require(
        "not current image-diffusion E2\ndenominator or admitted response/score evidence" in e2sct021_md,
        "E2SCT-021 allowed wording must preserve image-diffusion and admitted-evidence boundaries",
    )
    require(
        "Do not register for the platform" in e2sct021_md,
        "E2SCT-021 reopen condition must preserve the no-platform-registration boundary",
    )

    e2sct002_rows = read_csv(PREFLIGHT / "e2sct002_dmin_public_surface_check_2026_06_07.csv")
    e2sct002_by_item = {row["item"]: row for row in e2sct002_rows}
    require(
        e2sct002_by_item["repo_readme"]["status"] == "pass",
        "E2SCT-002 must preserve the attribution/influence README finding",
    )
    require(
        e2sct002_by_item["hf_dataset"]["status"] == "pass",
        "E2SCT-002 must preserve the public HF dataset finding",
    )
    require(
        e2sct002_by_item["membership_score_or_roc"]["status"] == "fail",
        "E2SCT-002 must remain blocked without public MIA score or ROC artifacts",
    )
    require(
        "attribution-vs-membership semantic false-promotion exemplar only"
        in e2sct002_by_item["admission_decision"]["evidence"],
        "E2SCT-002 admission decision must stay attribution-vs-membership false-promotion only",
    )
    e2sct002_md = (PREFLIGHT / "e2sct002_dmin_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct002_md, "E2SCT-002 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-002` as admitted evidence" in e2sct002_md,
        "E2SCT-002 markdown decision lost no-admission boundary",
    )
    require(
        "Do not download HF parquet" in e2sct002_md,
        "E2SCT-002 reopen condition must preserve the no-large-download boundary",
    )

    e2sct005_rows = read_csv(PREFLIGHT / "e2sct005_diffence_public_surface_check_2026_06_07.csv")
    e2sct005_by_item = {row["item"]: row for row in e2sct005_rows}
    require(
        e2sct005_by_item["repo_readme"]["status"] == "pass",
        "E2SCT-005 must preserve the public DIFFENCE README finding",
    )
    require(
        e2sct005_by_item["diffusion_checkpoint_dependency"]["status"] == "partial",
        "E2SCT-005 must preserve the external diffusion-checkpoint dependency boundary",
    )
    require(
        e2sct005_by_item["classifier_model_dependency"]["status"] == "partial",
        "E2SCT-005 must preserve the classifier-target dependency boundary",
    )
    require(
        e2sct005_by_item["mia_evaluation_script"]["status"] == "pass",
        "E2SCT-005 must preserve the public MIA evaluation-script finding",
    )
    require(
        e2sct005_by_item["score_metric_artifacts"]["status"] == "fail",
        "E2SCT-005 must remain blocked without public score or metric artifacts",
    )
    require(
        e2sct005_by_item["semantic_boundary"]["status"] == "fail",
        "E2SCT-005 must remain blocked by the classifier-defense consumer boundary",
    )
    require(
        "classifier-defense consumer-boundary false-promotion exemplar only"
        in e2sct005_by_item["admission_decision"]["evidence"],
        "E2SCT-005 admission decision must stay classifier-defense false-promotion only",
    )
    e2sct005_md = (PREFLIGHT / "e2sct005_diffence_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct005_md, "E2SCT-005 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-005` as admitted evidence" in e2sct005_md,
        "E2SCT-005 markdown decision lost no-admission boundary",
    )
    require(
        "not admitted\ndiffusion-generator response/score evidence" in e2sct005_md,
        "E2SCT-005 allowed wording must preserve diffusion-generator non-admission",
    )
    require(
        "Do not download Google Drive" in e2sct005_md,
        "E2SCT-005 reopen condition must preserve the no-large-download boundary",
    )

    e2sct013_rows = read_csv(PREFLIGHT / "e2sct013_dcr_public_surface_check_2026_06_07.csv")
    e2sct013_by_item = {row["item"]: row for row in e2sct013_rows}
    require(
        e2sct013_by_item["repo_readme"]["status"] == "pass",
        "E2SCT-013 must preserve the copying/retrieval README finding",
    )
    require(
        e2sct013_by_item["caption_manifest"]["status"] == "partial",
        "E2SCT-013 must preserve the caption-manifest metadata finding",
    )
    require(
        e2sct013_by_item["membership_score_or_roc"]["status"] == "fail",
        "E2SCT-013 must remain blocked without public MIA score or ROC artifacts",
    )
    require(
        "copying-vs-membership semantic false-promotion exemplar only"
        in e2sct013_by_item["admission_decision"]["evidence"],
        "E2SCT-013 admission decision must stay copying-vs-membership false-promotion only",
    )
    e2sct013_md = (PREFLIGHT / "e2sct013_dcr_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct013_md, "E2SCT-013 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-013` as admitted evidence" in e2sct013_md,
        "E2SCT-013 markdown decision lost no-admission boundary",
    )
    require(
        "Do not download LAION" in e2sct013_md,
        "E2SCT-013 reopen condition must preserve the no-large-download boundary",
    )

    e2sct009_rows = read_csv(PREFLIGHT / "e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.csv")
    e2sct009_by_item = {row["item"]: row for row in e2sct009_rows}
    require(
        e2sct009_by_item["openreview_note"]["status"] == "pass",
        "E2SCT-009 must preserve the OpenReview note finding",
    )
    require(
        e2sct009_by_item["prompt_surface"]["status"] == "partial",
        "E2SCT-009 must preserve the public prompt-surface finding",
    )
    require(
        e2sct009_by_item["membership_score_or_roc"]["status"] == "fail",
        "E2SCT-009 must remain blocked without public MIA score or ROC artifacts",
    )
    require(
        "prompt-memorization false-promotion exemplar only"
        in e2sct009_by_item["admission_decision"]["evidence"],
        "E2SCT-009 admission decision must stay prompt-memorization false-promotion only",
    )
    e2sct009_md = (PREFLIGHT / "e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct009_md, "E2SCT-009 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-009` as admitted evidence" in e2sct009_md,
        "E2SCT-009 markdown decision lost no-admission boundary",
    )
    require(
        "download prompt files" in e2sct009_md,
        "E2SCT-009 reopen condition must preserve the no-download boundary",
    )

    e2sct014_rows = read_csv(PREFLIGHT / "e2sct014_cdi_public_surface_check_2026_06_07.csv")
    e2sct014_by_item = {row["item"]: row for row in e2sct014_rows}
    require(
        e2sct014_by_item["repo_readme"]["status"] == "pass",
        "E2SCT-014 must preserve the dataset-level CDI README finding",
    )
    require(
        e2sct014_by_item["metric_code"]["status"] == "pass",
        "E2SCT-014 must preserve the public metric-code finding",
    )
    require(
        e2sct014_by_item["membership_score_or_roc"]["status"] == "fail",
        "E2SCT-014 must remain blocked without public per-sample MIA score artifacts",
    )
    require(
        "dataset-level-vs-per-sample false-promotion exemplar only"
        in e2sct014_by_item["admission_decision"]["evidence"],
        "E2SCT-014 admission decision must stay dataset-level false-promotion only",
    )
    e2sct014_md = (PREFLIGHT / "e2sct014_cdi_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct014_md, "E2SCT-014 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-014` as admitted evidence" in e2sct014_md,
        "E2SCT-014 markdown decision lost no-admission boundary",
    )
    require(
        "Do not download\nImageNet/COCO" in e2sct014_md,
        "E2SCT-014 reopen condition must preserve the no-large-download boundary",
    )

    exemplar_rows = read_csv(PREFLIGHT / "e2_false_promotion_exemplar_summary_2026_06_07.csv")
    require(len(exemplar_rows) == 13, "False-promotion exemplar summary must contain exactly thirteen rows")
    exemplar_by_id = {row["row_id"]: row for row in exemplar_rows}
    require(
        "E2SCT-028" not in exemplar_by_id,
        "SD-MIA/E2SCT-028 must not be added to the C14 false-promotion exemplar set",
    )
    require(
        "E2SCT-003" not in exemplar_by_id,
        "DurMI/E2SCT-003 must not be added to the C14 false-promotion exemplar set",
    )
    require(
        "E2SCT-025" not in exemplar_by_id,
        "Hyperparameter-Free SecMI/E2SCT-025 must not be added to the C14 false-promotion exemplar set",
    )
    require(
        "E2SCT-029" not in exemplar_by_id,
        "MIA_SD/E2SCT-029 must not be added to the current C14 false-promotion exemplar set",
    )
    require(
        "E2SCT-030" not in exemplar_by_id,
        "FMIA/Frequency/E2SCT-030 must not be added to the current C14 false-promotion exemplar set",
    )
    recent_support_only_ids = {
        "E2SCT-031": "SAMA/E2SCT-031",
        "E2SCT-032": "MIA-EPT/E2SCT-032",
        "E2SCT-033": "Diffusion MIA/E2SCT-033",
        "E2SCT-034": "ReMIA/E2SCT-034",
        "E2SCT-035": "OpenLVLM-MIA/E2SCT-035",
    }
    for row_id, label in recent_support_only_ids.items():
        require(
            row_id not in exemplar_by_id,
            f"{label} must not be added to the current C14 false-promotion exemplar set",
        )
    for row_id in ["E2SCT-004", "E2SCT-012", "E2SCT-016", "E2SCT-021", "E2SCT-002", "E2SCT-005", "E2SCT-013", "E2SCT-009", "E2SCT-014", "E2SCT-011", "E2SCT-020", "E2SCT-019", "E2SCT-024"]:
        require(row_id in exemplar_by_id, f"False-promotion exemplar summary missing {row_id}")
        require(exemplar_by_id[row_id]["no_compute_release"] == "1", f"{row_id} must preserve no_compute_release")
        require("not" in exemplar_by_id[row_id]["allowed_wording"], f"{row_id} wording lost non-admission boundary")
    require(
        "artifact_availability_would_promote" in exemplar_by_id["E2SCT-004"]["weak_rules_that_would_promote"],
        "E2SCT-004 must stay artifact-availability false-promotion example",
    )
    require(
        "code_availability_would_promote" in exemplar_by_id["E2SCT-012"]["weak_rules_that_would_promote"],
        "E2SCT-012 must stay code-availability false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-016"]["weak_rules_that_would_promote"],
        "E2SCT-016 must stay metric-code/split false-promotion example",
    )
    require(
        "artifact_availability_would_promote" in exemplar_by_id["E2SCT-021"]["weak_rules_that_would_promote"],
        "E2SCT-021 must stay gated-starter artifact false-promotion example",
    )
    require(
        "artifact_availability_would_promote" in exemplar_by_id["E2SCT-002"]["weak_rules_that_would_promote"],
        "E2SCT-002 must stay attribution artifact false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-005"]["weak_rules_that_would_promote"],
        "E2SCT-005 must stay classifier-defense metric-code false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-013"]["weak_rules_that_would_promote"],
        "E2SCT-013 must stay copying metric-code false-promotion example",
    )
    require(
        "artifact_availability_would_promote" in exemplar_by_id["E2SCT-009"]["weak_rules_that_would_promote"],
        "E2SCT-009 must stay prompt-list artifact false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-014"]["weak_rules_that_would_promote"],
        "E2SCT-014 must stay dataset-level metric-code false-promotion example",
    )
    require(
        "code_availability_would_promote" in exemplar_by_id["E2SCT-011"]["weak_rules_that_would_promote"],
        "E2SCT-011 must stay code-availability false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-011"]["weak_rules_that_would_promote"],
        "E2SCT-011 must stay metric/split visibility false-promotion example",
    )
    require(
        "artifact_availability_would_promote" in exemplar_by_id["E2SCT-020"]["weak_rules_that_would_promote"],
        "E2SCT-020 must stay demo-artifact false-promotion example",
    )
    require(
        "metric_code_split_would_promote" in exemplar_by_id["E2SCT-020"]["weak_rules_that_would_promote"],
        "E2SCT-020 must stay mock-demo-score false-promotion example",
    )
    require(
        "code_availability_would_promote" in exemplar_by_id["E2SCT-019"]["weak_rules_that_would_promote"],
        "E2SCT-019 must stay T2V code-snapshot false-promotion example",
    )
    require(
        "paper_claim_artifact_link_would_promote" in exemplar_by_id["E2SCT-019"]["weak_rules_that_would_promote"],
        "E2SCT-019 must stay paper-link false-promotion example",
    )
    require(
        "code_availability_would_promote" in exemplar_by_id["E2SCT-024"]["weak_rules_that_would_promote"],
        "E2SCT-024 must stay official-repo-stub code-availability false-promotion example",
    )
    e2sct011_rows = read_csv(PREFLIGHT / "e2sct011_vae2diffusion_public_surface_check_2026_06_07.csv")
    e2sct011_by_item = {row["item"]: row for row in e2sct011_rows}
    require(
        e2sct011_by_item["github_head"]["status"] == "pass",
        "E2SCT-011 must preserve the current GitHub head finding",
    )
    require(
        "d530fbb7e0aca488e63637167b4d64539397bcf7" in e2sct011_by_item["github_head"]["evidence"],
        "E2SCT-011 GitHub head must record the current checked commit",
    )
    require(
        e2sct011_by_item["repo_readme"]["status"] == "partial",
        "E2SCT-011 README surface must remain partial with an empty asset link",
    )
    require(
        e2sct011_by_item["github_releases"]["status"] == "fail",
        "E2SCT-011 must remain blocked without GitHub release assets",
    )
    require(
        e2sct011_by_item["github_tree"]["status"] == "fail",
        "E2SCT-011 must remain blocked without visible split/checkpoint/score artifacts in the tree",
    )
    require(
        e2sct011_by_item["score_metric_artifacts"]["status"] == "fail",
        "E2SCT-011 must remain blocked without public score or metric artifacts",
    )
    require(
        "code-and-empty-asset-link false-promotion exemplar only"
        in e2sct011_by_item["admission_decision"]["evidence"],
        "E2SCT-011 admission decision must stay false-promotion-only",
    )
    e2sct011_md = (PREFLIGHT / "e2sct011_vae2diffusion_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct011_md, "E2SCT-011 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-011` as admitted evidence" in e2sct011_md,
        "E2SCT-011 markdown decision lost no-admission boundary",
    )
    require(
        "Do not launch GPU/DCU work from this row" in e2sct011_md,
        "E2SCT-011 reopen condition must preserve the no-compute boundary",
    )
    e2sct020_rows = read_csv(PREFLIGHT / "e2sct020_lsa_probe_public_surface_check_2026_06_07.csv")
    e2sct020_by_item = {row["item"]: row for row in e2sct020_rows}
    require(
        e2sct020_by_item["project_readme"]["status"] == "partial",
        "E2SCT-020 README surface must remain partial because implementation is withheld",
    )
    require(
        "a3ea7ebf72e5855490206266a8ef176f553037a8c609ca43829a2b77e9eb9089"
        in e2sct020_by_item["project_readme"]["evidence"],
        "E2SCT-020 README hash must record the current raw README",
    )
    require(
        e2sct020_by_item["github_releases"]["status"] == "fail",
        "E2SCT-020 must remain blocked without release assets",
    )
    require(
        e2sct020_by_item["demo_generator"]["status"] == "fail",
        "E2SCT-020 must keep the mock generator blocker",
    )
    require(
        "Generate mock data" in e2sct020_by_item["demo_generator"]["evidence"],
        "E2SCT-020 generator evidence must preserve mock-data wording",
    )
    require(
        e2sct020_by_item["demo_score_like_json"]["status"] == "fail",
        "E2SCT-020 score-like demo JSON must remain blocked",
    )
    require(
        "mock-demo-score false-promotion exemplar only"
        in e2sct020_by_item["admission_decision"]["evidence"],
        "E2SCT-020 admission decision must stay false-promotion-only",
    )
    e2sct020_md = (PREFLIGHT / "e2sct020_lsa_probe_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct020_md, "E2SCT-020 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-020` as admitted evidence" in e2sct020_md,
        "E2SCT-020 markdown decision lost no-admission boundary",
    )
    require(
        "Do not download MAESTRO" in e2sct020_md,
        "E2SCT-020 reopen condition must preserve the no-large-download boundary",
    )
    e2sct019_rows = read_csv(PREFLIGHT / "e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.csv")
    e2sct019_by_item = {row["item"]: row for row in e2sct019_rows}
    require(
        e2sct019_by_item["zenodo_record"]["status"] == "pass",
        "E2SCT-019 must preserve the Zenodo record finding",
    )
    require(
        "d1fdb76b2d3d145333ba3e9c35fadad4d77cb2e5bc84a0e53d230f60557a8b7e"
        in e2sct019_by_item["zenodo_record"]["evidence"],
        "E2SCT-019 Zenodo HTML hash must record the current checked surface",
    )
    require(
        e2sct019_by_item["related_github"]["status"] == "fail",
        "E2SCT-019 related GitHub URL must remain failed in this check",
    )
    require(
        e2sct019_by_item["target_split_binding"]["status"] == "fail",
        "E2SCT-019 must remain blocked without T2V target/split binding",
    )
    require(
        e2sct019_by_item["score_metric_artifacts"]["status"] == "fail",
        "E2SCT-019 must remain blocked without score/metric artifacts",
    )
    require(
        "t2v-code-snapshot false-promotion exemplar only"
        in e2sct019_by_item["admission_decision"]["evidence"],
        "E2SCT-019 admission decision must stay false-promotion-only",
    )
    e2sct019_md = (PREFLIGHT / "e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct019_md, "E2SCT-019 markdown decision lost no-compute boundary")
    require(
        "Do not count it as admitted evidence" in e2sct019_md,
        "E2SCT-019 markdown decision lost no-admission boundary",
    )
    require(
        "Do not download WebVid-10M" in e2sct019_md,
        "E2SCT-019 reopen condition must preserve the no-large-download boundary",
    )
    e2sct022_rows = read_csv(
        PREFLIGHT / "e2sct022_tabular_privacy_leakage_tdm_public_surface_check_2026_06_07.csv"
    )
    e2sct022_by_item = {row["item"]: row for row in e2sct022_rows}
    require(
        e2sct022_by_item["toolkit_readme"]["status"] == "partial",
        "E2SCT-022 must preserve the public toolkit support surface",
    )
    require(
        "ced52d8e52fa1e4b44c91290d42b8daac589ff45978bd641f6451ce3129fdb4f"
        in e2sct022_by_item["toolkit_readme"]["evidence"],
        "E2SCT-022 README hash must record the current raw README",
    )
    require(
        e2sct022_by_item["paper_bound_replay_packet"]["status"] == "fail",
        "E2SCT-022 must remain blocked without a paper-bound replay packet",
    )
    require(
        "support-only / tabular-lane watch-plus" in e2sct022_by_item["admission_decision"]["evidence"],
        "E2SCT-022 admission decision must stay support-only/tabular-lane",
    )
    e2sct022_md = (
        PREFLIGHT / "e2sct022_tabular_privacy_leakage_tdm_public_surface_check_2026_06_07.md"
    ).read_text(encoding="utf-8")
    require("no_compute_release" in e2sct022_md, "E2SCT-022 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-022` as a C14 false-promotion exemplar" in e2sct022_md,
        "E2SCT-022 markdown decision lost no-C14 boundary",
    )
    require(
        "Do not clone `midst-toolkit`" in e2sct022_md,
        "E2SCT-022 markdown decision lost no-clone boundary",
    )
    e2sct023_rows = read_csv(PREFLIGHT / "e2sct023_fermi_public_surface_check_2026_06_07.csv")
    e2sct023_by_item = {row["item"]: row for row in e2sct023_rows}
    require(
        e2sct023_by_item["arxiv_atom"]["status"] == "partial",
        "E2SCT-023 must preserve the arXiv metadata support surface",
    )
    require(
        "8ec292871e572236590fb3f1cc66f997c7a8214062201ee52cad2d337635a0cd"
        in e2sct023_by_item["arxiv_atom"]["evidence"],
        "E2SCT-023 arXiv Atom hash must record the current checked surface",
    )
    require(
        e2sct023_by_item["official_artifact_search"]["status"] == "fail",
        "E2SCT-023 must remain blocked without official public artifacts",
    )
    require(
        e2sct023_by_item["target_split_score_packet"]["status"] == "fail",
        "E2SCT-023 must remain blocked without target/split/score packet",
    )
    require(
        "paper-source-only / reported-metric support-only watch"
        in e2sct023_by_item["admission_decision"]["evidence"],
        "E2SCT-023 admission decision must stay support-only",
    )
    e2sct023_md = (PREFLIGHT / "e2sct023_fermi_public_surface_check_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct023_md, "E2SCT-023 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-023` as a C14 false-promotion exemplar" in e2sct023_md,
        "E2SCT-023 markdown decision lost no-C14 boundary",
    )
    require(
        "Do not download arXiv source or PDF payloads" in e2sct023_md,
        "E2SCT-023 markdown decision lost no-download boundary",
    )
    e2sct003_rows = read_csv(PREFLIGHT / "e2sct003_durmi_tts_public_surface_check_2026_06_08.csv")
    e2sct003_by_item = {row["item"]: row for row in e2sct003_rows}
    require(
        e2sct003_by_item["openreview_submission"]["status"] == "partial",
        "E2SCT-003 must preserve the public OpenReview support surface",
    )
    require(
        e2sct003_by_item["zenodo_record"]["status"] == "partial",
        "E2SCT-003 must preserve the public Zenodo support surface",
    )
    require(
        e2sct003_by_item["zenodo_dataset_checkpoint_metadata"]["status"] == "partial",
        "E2SCT-003 must preserve dataset/checkpoint metadata as support-only",
    )
    require(
        e2sct003_by_item["ready_score_response_packet"]["status"] == "fail",
        "E2SCT-003 must remain blocked without ready duration-loss score artifacts",
    )
    require(
        "row_bound_duration_loss_score_packet_missing" in e2sct003_by_item["ready_score_response_packet"]["boundary"],
        "E2SCT-003 score/response blocker must remain explicit",
    )
    require(
        e2sct003_by_item["consumer_modality_boundary"]["status"] == "fail",
        "E2SCT-003 must remain blocked by the TTS/audio modality boundary",
    )
    require(
        e2sct003_by_item["admission_decision"]["status"] == "fail",
        "E2SCT-003 admission decision must stay fail",
    )
    require(
        "support-only TTS/audio cross-modal watch" in e2sct003_by_item["admission_decision"]["evidence"],
        "E2SCT-003 admission decision must stay TTS/audio support-only",
    )
    require(
        "not C14; not admitted; not external denominator; no_compute_release"
        in e2sct003_by_item["admission_decision"]["evidence"],
        "E2SCT-003 admission decision lost no-C14/no-admission/no-denominator/no-compute boundary",
    )
    e2sct003_md = (PREFLIGHT / "e2sct003_durmi_tts_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct003_md, "E2SCT-003 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-003` as a C14 false-promotion exemplar" in e2sct003_md,
        "E2SCT-003 markdown decision lost no-C14 boundary",
    )
    require(
        "row_bound_duration_loss_score_packet_missing" in e2sct003_md,
        "E2SCT-003 markdown decision lost row-bound score packet blocker",
    )
    require(
        "Do not download Zenodo audio datasets" in e2sct003_md
        and "GPU/DCU jobs" in e2sct003_md
        and "DurMI attacks" in e2sct003_md,
        "E2SCT-003 markdown decision lost no-download/no-execution boundary",
    )
    e2sct028_rows = read_csv(PREFLIGHT / "e2sct028_sdmia_public_surface_check_2026_06_08.csv")
    e2sct028_by_item = {row["item"]: row for row in e2sct028_rows}
    require(
        e2sct028_by_item["cvf_paper"]["status"] == "partial",
        "E2SCT-028 must preserve the public CVF paper support surface",
    )
    require(
        e2sct028_by_item["repo_tree"]["status"] == "fail",
        "E2SCT-028 must remain blocked without committed row-bound artifacts",
    )
    require(
        "no committed `data/`, `res/`, score rows" in e2sct028_by_item["repo_tree"]["evidence"],
        "E2SCT-028 repo-tree finding must preserve missing artifact details",
    )
    require(
        e2sct028_by_item["process_notebook"]["status"] == "partial",
        "E2SCT-028 must preserve process-notebook metric-code support status",
    )
    require(
        e2sct028_by_item["admission_decision"]["status"] == "fail",
        "E2SCT-028 admission decision must stay fail",
    )
    require(
        "support-only code-public pre-training T2I MIA reference"
        in e2sct028_by_item["admission_decision"]["evidence"],
        "E2SCT-028 admission decision must stay support-only/code-public",
    )
    require(
        "not C14; not admitted; not external denominator; no_compute_release"
        in e2sct028_by_item["admission_decision"]["evidence"],
        "E2SCT-028 admission decision lost no-C14/no-admission/no-denominator/no-compute boundary",
    )
    e2sct028_md = (PREFLIGHT / "e2sct028_sdmia_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct028_md, "E2SCT-028 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-028` as a C14 false-promotion exemplar" in e2sct028_md,
        "E2SCT-028 markdown decision lost no-C14 boundary",
    )
    require(
        "row_bound_score_response_packet_missing" in e2sct028_md,
        "E2SCT-028 markdown decision lost row-bound packet blocker",
    )
    require(
        "Do not download LAION-mi" in e2sct028_md,
        "E2SCT-028 markdown decision lost no-large-download boundary",
    )
    e2sct025_rows = read_csv(PREFLIGHT / "e2sct025_hyperfree_secmi_public_surface_check_2026_06_08.csv")
    e2sct025_by_item = {row["item"]: row for row in e2sct025_rows}
    require(
        e2sct025_by_item["repo_identity"]["status"] == "partial",
        "E2SCT-025 must preserve the public branch identity finding",
    )
    require(
        e2sct025_by_item["readme_surface"]["status"] == "partial",
        "E2SCT-025 must preserve the aggregate README metric finding",
    )
    require(
        "AUC 0.984" in e2sct025_by_item["readme_surface"]["evidence"],
        "E2SCT-025 README finding must preserve the aggregate AUC pressure",
    )
    require(
        e2sct025_by_item["raw_source_sampling"]["status"] == "partial",
        "E2SCT-025 must preserve public raw-source support status",
    )
    require(
        e2sct025_by_item["dependency_surface"]["status"] == "fail",
        "E2SCT-025 must remain blocked by external/local execution dependencies",
    )
    require(
        e2sct025_by_item["ready_score_response_packet"]["status"] == "fail",
        "E2SCT-025 must remain blocked without a ready score/response packet",
    )
    require(
        "row_bound_score_metric_packet_missing" in e2sct025_by_item["ready_score_response_packet"]["boundary"],
        "E2SCT-025 score/metric packet blocker must remain explicit",
    )
    require(
        e2sct025_by_item["duplicate_family_boundary"]["status"] == "fail",
        "E2SCT-025 must remain blocked as duplicate SecMI-family support",
    )
    require(
        "same-family SecMI support" in e2sct025_by_item["duplicate_family_boundary"]["boundary"],
        "E2SCT-025 duplicate-family boundary must remain explicit",
    )
    require(
        e2sct025_by_item["admission_decision"]["status"] == "fail",
        "E2SCT-025 admission decision must stay fail",
    )
    require(
        "support-only third-party SecMI-family code/report surface"
        in e2sct025_by_item["admission_decision"]["evidence"],
        "E2SCT-025 admission decision must stay support-only/SecMI-family",
    )
    require(
        "not C14; not admitted; not external denominator; no_compute_release"
        in e2sct025_by_item["admission_decision"]["evidence"],
        "E2SCT-025 admission decision lost no-C14/no-admission/no-denominator/no-compute boundary",
    )
    e2sct025_md = (PREFLIGHT / "e2sct025_hyperfree_secmi_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct025_md, "E2SCT-025 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-025` as a C14 false-promotion exemplar" in e2sct025_md,
        "E2SCT-025 markdown decision lost no-C14 boundary",
    )
    require(
        "row_bound_score_metric_packet_missing" in e2sct025_md,
        "E2SCT-025 markdown decision lost row-bound score/metric packet blocker",
    )
    require(
        "Do not clone the full repository" in e2sct025_md
        and "Do not download CIFAR-10/CIFAR-100" in e2sct025_md
        and "Do not run `python run.py" in e2sct025_md
        and "GPU/DCU jobs" in e2sct025_md,
        "E2SCT-025 markdown decision lost no-download/no-run/no-GPU boundary",
    )
    e2sct029_rows = read_csv(PREFLIGHT / "e2sct029_mia_sd_public_surface_check_2026_06_08.csv")
    e2sct029_by_surface = {row["surface"]: row for row in e2sct029_rows}
    require(
        e2sct029_by_surface["root_readme"]["decision"] == "Fail",
        "E2SCT-029 must preserve the unpublished-images blocker",
    )
    require(
        "not published" in e2sct029_by_surface["root_readme"]["observation"],
        "E2SCT-029 root README finding must preserve unpublished image evidence",
    )
    require(
        e2sct029_by_surface["results_pickle"]["decision"] == "Partial"
        and "y_true" in e2sct029_by_surface["results_pickle"]["observation"],
        "E2SCT-029 must preserve public pickle label/prediction pressure",
    )
    require(
        e2sct029_by_surface["roc_pgf"]["decision"] == "Partial"
        and "Mean ROC AUC = 0.86" in e2sct029_by_surface["roc_pgf"]["observation"],
        "E2SCT-029 must preserve public PGF metric pressure",
    )
    require(
        e2sct029_by_surface["overall"]["decision"] == "candidate-only",
        "E2SCT-029 overall decision must remain candidate-only",
    )
    require(
        "not admitted" in e2sct029_by_surface["overall"]["boundary"]
        and "not current C14 baseline" in e2sct029_by_surface["overall"]["boundary"]
        and "not second public response/score asset" in e2sct029_by_surface["overall"]["boundary"]
        and "no compute release" in e2sct029_by_surface["overall"]["boundary"],
        "E2SCT-029 overall boundary lost no-admission/no-C14/no-second-asset/no-compute language",
    )
    e2sct029_md = (PREFLIGHT / "e2sct029_mia_sd_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require(
        "C14-v2 candidate only; not admitted evidence, not external denominator, no compute release" in e2sct029_md,
        "E2SCT-029 markdown decision lost candidate-only boundary",
    )
    require(
        "not a second public response/score asset" in e2sct029_md
        and "Do not update the current main paper's C14 selected-row count" in e2sct029_md,
        "E2SCT-029 markdown lost no-second-asset/no-C14-update boundary",
    )
    e2sct030_rows = read_csv(PREFLIGHT / "e2sct030_frequency_components_public_surface_check_2026_06_08.csv")
    e2sct030_by_item = {row["item"]: row for row in e2sct030_rows}
    require(
        e2sct030_by_item["openreview_note"]["status"] == "partial"
        and "version `2`" in e2sct030_by_item["openreview_note"]["evidence"]
        and "Rejected_Submission" in e2sct030_by_item["openreview_note"]["evidence"],
        "E2SCT-030 must preserve current OpenReview rejected/version-2 metadata",
    )
    require(
        e2sct030_by_item["supplement_head"]["status"] == "partial"
        and "Content-Length: 1783018" in e2sct030_by_item["supplement_head"]["evidence"],
        "E2SCT-030 must preserve current supplement HEAD size evidence",
    )
    require(
        e2sct030_by_item["prior_local_inventory"]["status"] == "partial"
        and "567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045"
        in e2sct030_by_item["prior_local_inventory"]["evidence"],
        "E2SCT-030 must preserve prior ZIP inventory hash as prior local evidence",
    )
    require(
        e2sct030_by_item["checkpoint_dependency"]["status"] == "fail",
        "E2SCT-030 must remain blocked by missing checkpoint/model artifacts",
    )
    require(
        e2sct030_by_item["score_metric_artifacts"]["status"] == "fail"
        and e2sct030_by_item["score_metric_artifacts"]["boundary"] == "row_bound_score_response_packet_missing",
        "E2SCT-030 must remain blocked by missing row-bound score/response packets",
    )
    require(
        e2sct030_by_item["second_asset_gate"]["status"] == "fail"
        and "not a second public response/score asset" in e2sct030_by_item["second_asset_gate"]["boundary"],
        "E2SCT-030 must remain blocked from second-asset status",
    )
    require(
        e2sct030_by_item["admission_decision"]["status"] == "fail"
        and "support-only code-and-split-manifest watch-plus" in e2sct030_by_item["admission_decision"]["evidence"]
        and "not C14; not admitted; not external denominator; no_compute_release"
        in e2sct030_by_item["admission_decision"]["evidence"],
        "E2SCT-030 admission decision lost support-only/no-C14/no-admission/no-denominator/no-compute boundary",
    )
    e2sct030_md = (PREFLIGHT / "e2sct030_frequency_components_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct030_md, "E2SCT-030 markdown decision lost no-compute boundary")
    require(
        "Do not count `E2SCT-030` as a C14 false-promotion exemplar" in e2sct030_md,
        "E2SCT-030 markdown decision lost no-C14 boundary",
    )
    require(
        "row_bound_score_response_packet_missing" in e2sct030_md
        and "second public response/score" in e2sct030_md
        and "asset" in e2sct030_md,
        "E2SCT-030 markdown decision lost row-bound/no-second-asset blocker",
    )
    require(
        "not a new independent public-surface candidate" in e2sct030_md,
        "E2SCT-030 markdown lost current-date-recheck boundary",
    )
    require(
        "Do not download datasets" in e2sct030_md
        and "Do not train DDIM targets" in e2sct030_md
        and "GPU/DCU jobs" in e2sct030_md,
        "E2SCT-030 markdown decision lost no-download/no-training/no-GPU boundary",
    )
    e2sct031_rows = read_csv(PREFLIGHT / "e2sct031_sama_dlm_public_surface_check_2026_06_09.csv")
    e2sct031_by_item = {row["item"]: row for row in e2sct031_rows}
    require(
        e2sct031_by_item["repository_commit"]["status"] == "partial"
        and "5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd" in e2sct031_by_item["repository_commit"]["evidence"],
        "E2SCT-031 must preserve the SAMA public commit identity",
    )
    require(
        e2sct031_by_item["score_metric_gate"]["status"] == "fail"
        and "not a second public score/response asset" in e2sct031_by_item["score_metric_gate"]["boundary"],
        "E2SCT-031 must remain blocked from second-asset status",
    )
    require(
        e2sct031_by_item["admission_decision"]["status"] == "fail"
        and "support-only DLM public-code artifact" in e2sct031_by_item["admission_decision"]["evidence"]
        and "no_compute_release" in e2sct031_by_item["admission_decision"]["evidence"],
        "E2SCT-031 admission decision lost support-only/no-compute boundary",
    )
    e2sct031_md = (PREFLIGHT / "e2sct031_sama_dlm_public_surface_check_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct031_md, "E2SCT-031 markdown decision lost no-compute boundary")
    require(
        "not a second public score/response asset" in e2sct031_md
        and "image-diffusion denominator evidence" in e2sct031_md
        and "outside the current image-diffusion denominator lane" in e2sct031_md,
        "E2SCT-031 markdown lost no-second-asset/no-image-denominator boundary",
    )
    require(
        "Do not release GPU/DCU compute from this gate" in e2sct031_md,
        "E2SCT-031 markdown lost no-compute-release stop rule",
    )
    e2sct032_rows = read_csv(PREFLIGHT / "e2sct032_miaept_tabular_public_surface_check_2026_06_09.csv")
    e2sct032_by_item = {row["item"]: row for row in e2sct032_rows}
    require(
        e2sct032_by_item["main_commit"]["status"] == "partial"
        and "6890ee833ad90b9fd8b3b3b06abd41613a4b316d" in e2sct032_by_item["main_commit"]["evidence"],
        "E2SCT-032 must preserve the MIA-EPT main commit identity",
    )
    require(
        e2sct032_by_item["project_page_metrics"]["status"] == "partial"
        and "best AUC-ROC `0.599`" in e2sct032_by_item["project_page_metrics"]["evidence"],
        "E2SCT-032 must preserve public project-page metric pressure",
    )
    require(
        e2sct032_by_item["main_tree"]["status"] == "fail"
        and e2sct032_by_item["main_tree"]["boundary"] == "row_bound_score_prediction_packet_missing",
        "E2SCT-032 must remain blocked by missing row-bound score/prediction packet",
    )
    require(
        e2sct032_by_item["admission_decision"]["status"] == "fail"
        and "support-only tabular-diffusion public-result-page artifact" in e2sct032_by_item["admission_decision"]["evidence"]
        and "no_compute_release" in e2sct032_by_item["admission_decision"]["evidence"],
        "E2SCT-032 admission decision lost support-only/no-compute boundary",
    )
    e2sct032_md = (PREFLIGHT / "e2sct032_miaept_tabular_public_surface_check_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct032_md, "E2SCT-032 markdown decision lost no-compute boundary")
    require(
        "not a second public" in e2sct032_md and "score/response asset" in e2sct032_md,
        "E2SCT-032 markdown lost no-second-asset boundary",
    )
    require("Do not release compute from this gate" in e2sct032_md, "E2SCT-032 markdown lost no-compute stop rule")
    e2sct033_rows = read_csv(PREFLIGHT / "e2sct033_diffusion_mia_public_surface_check_2026_06_09.csv")
    e2sct033_by_item = {row["item"]: row for row in e2sct033_rows}
    require(
        e2sct033_by_item["repository_commit"]["status"] == "partial"
        and "26e6471c15472bf89ee49ff3057f66a5407dae00" in e2sct033_by_item["repository_commit"]["evidence"],
        "E2SCT-033 must preserve the Diffusion MIA public commit identity",
    )
    require(
        e2sct033_by_item["ddim_split_files"]["status"] == "partial"
        and "CIFAR10_train_ratio0.5.npz" in e2sct033_by_item["ddim_split_files"]["evidence"]
        and "STL10_train_ratio0.5.npz" in e2sct033_by_item["ddim_split_files"]["evidence"],
        "E2SCT-033 must preserve DDIM split-file finding and missing STL-10 split caveat",
    )
    require(
        e2sct033_by_item["score_metric_gate"]["status"] == "fail"
        and "not a second public score/response asset" in e2sct033_by_item["score_metric_gate"]["boundary"],
        "E2SCT-033 must remain blocked from second-asset status",
    )
    require(
        e2sct033_by_item["admission_decision"]["status"] == "fail"
        and "support-only black-box diffusion MIA code-and-split surface" in e2sct033_by_item["admission_decision"]["evidence"]
        and "no_compute_release" in e2sct033_by_item["admission_decision"]["evidence"],
        "E2SCT-033 admission decision lost support-only/no-compute boundary",
    )
    e2sct033_md = (PREFLIGHT / "e2sct033_diffusion_mia_public_surface_check_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct033_md, "E2SCT-033 markdown decision lost no-compute boundary")
    require(
        "not a second public score/response asset" in e2sct033_md
        and "no-training verifier" in e2sct033_md,
        "E2SCT-033 markdown lost no-second-asset/no-verifier boundary",
    )
    require(
        "Do not release GPU/DCU compute from this gate" in e2sct033_md,
        "E2SCT-033 markdown lost no-compute-release stop rule",
    )
    e2sct034_rows = read_csv(PREFLIGHT / "e2sct034_remia_tabular_public_result_archive_check_2026_06_09.csv")
    e2sct034_by_item = {row["item"]: row for row in e2sct034_rows}
    require(
        e2sct034_by_item["repository_commit"]["status"] == "partial"
        and "84da2feee749b56639f8c8d9a6bbfffdbc0e87b3" in e2sct034_by_item["repository_commit"]["evidence"],
        "E2SCT-034 must preserve the ReMIA public commit identity",
    )
    require(
        e2sct034_by_item["archive_manifest"]["status"] == "partial"
        and "2,879" in e2sct034_by_item["archive_manifest"]["evidence"]
        and "26F903EEE3355912BEA3AE8D80E3C066F19556D46A06F374789EF992B2ED1C3E"
        in e2sct034_by_item["archive_manifest"]["evidence"],
        "E2SCT-034 must preserve the ReMIA archive inventory and hash",
    )
    require(
        e2sct034_by_item["json_schema"]["status"] == "fail"
        and e2sct034_by_item["json_schema"]["boundary"] == "row_bound_score_label_packet_missing",
        "E2SCT-034 must remain blocked by missing row-bound score/label arrays",
    )
    require(
        e2sct034_by_item["admission_decision"]["status"] == "fail"
        and "support-only tabular synthetic-data aggregate-result archive" in e2sct034_by_item["admission_decision"]["evidence"]
        and "no_compute_release" in e2sct034_by_item["admission_decision"]["evidence"],
        "E2SCT-034 admission decision lost support-only/no-compute boundary",
    )
    e2sct034_md = (PREFLIGHT / "e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct034_md, "E2SCT-034 markdown decision lost no-compute boundary")
    require(
        "not a second public" in e2sct034_md
        and "score/response asset" in e2sct034_md
        and "aggregate JSON summaries" in e2sct034_md,
        "E2SCT-034 markdown lost aggregate-only/no-second-asset boundary",
    )
    require("Do not release compute from this gate" in e2sct034_md, "E2SCT-034 markdown lost no-compute stop rule")
    e2sct035_rows = read_csv(PREFLIGHT / "e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.csv")
    e2sct035_by_item = {row["item"]: row for row in e2sct035_rows}
    require(
        e2sct035_by_item["repository_commit"]["status"] == "partial"
        and "879265f7a17cdf616bad90b9d1ba29b213eccd4d" in e2sct035_by_item["repository_commit"]["evidence"],
        "E2SCT-035 must preserve the OpenLVLM-MIA public code commit identity",
    )
    require(
        e2sct035_by_item["dataset_identity"]["status"] == "partial"
        and "a4656ebdf1e0ba8c04fae43acd8022e6cc699bbb" in e2sct035_by_item["dataset_identity"]["evidence"],
        "E2SCT-035 must preserve the OpenLVLM-MIA HF dataset identity",
    )
    require(
        e2sct035_by_item["dataset_schema"]["status"] == "partial"
        and "image" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "label" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "parent_dataset" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "vision_encoder_pretrain" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "projector_pretrain" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "instruction_tuning" in e2sct035_by_item["dataset_schema"]["evidence"]
        and "`2,000` examples" in e2sct035_by_item["dataset_schema"]["evidence"],
        "E2SCT-035 must preserve the VLM dataset schema and three 2,000-example splits",
    )
    require(
        e2sct035_by_item["model_identity"]["status"] == "partial"
        and "8c57a060bd4f2fe6cfe403cbf673f693ff00da26" in e2sct035_by_item["model_identity"]["evidence"],
        "E2SCT-035 must preserve the OpenLVLM-MIA HF model identity",
    )
    require(
        e2sct035_by_item["runtime_score_path"]["status"] == "fail"
        and "evaluation_results_<timestamp>.pkl" in e2sct035_by_item["runtime_score_path"]["evidence"]
        and "runtime outputs" in e2sct035_by_item["runtime_score_path"]["boundary"],
        "E2SCT-035 must remain blocked by runtime-only score outputs",
    )
    require(
        e2sct035_by_item["consumer_boundary"]["status"] == "fail"
        and e2sct035_by_item["consumer_boundary"]["boundary"] == "wrong current consumer lane",
        "E2SCT-035 must remain outside the current image-diffusion consumer lane",
    )
    require(
        e2sct035_by_item["admission_decision"]["status"] == "fail"
        and "future VLM controlled-benchmark scout only" in e2sct035_by_item["admission_decision"]["evidence"]
        and "no_compute_release" in e2sct035_by_item["admission_decision"]["evidence"]
        and "do not add to C14/N50" in e2sct035_by_item["admission_decision"]["boundary"]
        and "do not count as second public score/response asset" in e2sct035_by_item["admission_decision"]["boundary"]
        and "do not release compute" in e2sct035_by_item["admission_decision"]["boundary"],
        "E2SCT-035 admission decision lost VLM-scout/no-C14/no-N50/no-second-asset/no-compute boundary",
    )
    e2sct035_md = (PREFLIGHT / "e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("6,000" in e2sct035_md and "2,000` per split" in e2sct035_md, "E2SCT-035 markdown lost dataset-size boundary")
    require("no_compute_release" in e2sct035_md, "E2SCT-035 markdown decision lost no-compute boundary")
    require(
        "not enter current Direction A" in e2sct035_md
        and "not a C14 row" in e2sct035_md
        and "N50 denominator row" in e2sct035_md
        and "not admitted evidence" in e2sct035_md
        and "not the second public" in e2sct035_md
        and "score/response asset" in e2sct035_md,
        "E2SCT-035 markdown lost no-current-direction/no-C14-no-N50/no-second-asset boundary",
    )
    require("Do not release compute from this gate" in e2sct035_md, "E2SCT-035 markdown lost no-compute stop rule")
    delta_watchlist = read_csv(PREFLIGHT / "e2_high_value_public_asset_delta_watchlist_2026_06_09.csv")
    delta_rows = read_csv(PREFLIGHT / "e2_high_value_public_asset_delta_refresh_2026_06_09.csv")
    expected_delta_ids = {
        "E1-NDSS-324",
        "E2Q-006",
        "E2-MOFIT",
        "E2SCT-029",
        "E2SCT-031",
        "E2SCT-032",
        "E2SCT-033",
        "E2SCT-034",
        "E2SCT-035",
    }
    require({row["queue_id"] for row in delta_watchlist} == expected_delta_ids, "High-value delta watchlist row set drifted")
    require({row["queue_id"] for row in delta_rows} == expected_delta_ids, "High-value delta refresh row set drifted")
    require(
        all(row["identity_delta_status"] == "identity_matched" for row in delta_rows),
        "High-value delta refresh must keep all nine source identities matched",
    )
    require(
        all(
            row["compact_reopen_surface_hint"]
            in {
                "compact_artifact_filename_hint_only",
                "filename_hint_manual_gate_review_needed",
                "no_compact_reopen_surface_hint",
            }
            for row in delta_rows
        ),
        "High-value delta refresh has an unexpected compact reopen hint category",
    )
    delta_by_id = {row["queue_id"]: row for row in delta_rows}
    require(
        "py85252876/Reconstruction-based-Attack@93ee8dd4d12697354cd182461a9aa268b8de63e6"
        in delta_by_id["E1-NDSS-324"]["github_head_shas"]
        and "13371475:extra_data-20240825T145405Z-001.zip|size=736366195|checksum=md5:a52e197025c54c197b00674d398f2f6a"
        in delta_by_id["E1-NDSS-324"]["zenodo_file_fingerprints"],
        "High-value delta refresh lost NDSS-324 GitHub/Zenodo identity",
    )
    require(
        "caradryanl/CopyMark@069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea"
        in delta_by_id["E2Q-006"]["github_head_shas"]
        and "chumengl/copymark@331cd0010f8b638922f184cad0e6f5ccd8db78d4" in delta_by_id["E2Q-006"]["hf_shas"],
        "High-value delta refresh lost CopyMark GitHub/HF identity",
    )
    require(
        "JoonsungJeon/MoFit@91e4b5edc153bac84b0b4209f70d1b2b94e653b2"
        in delta_by_id["E2-MOFIT"]["github_head_shas"]
        and "zsf/COCO_MIA_ori_split1@4af0207c955c893a49b7c2970db5ada414b37ed2"
        in delta_by_id["E2-MOFIT"]["hf_shas"],
        "High-value delta refresh lost MoFit GitHub/HF identity",
    )
    require(
        "osquera/MIA_SD@513084a3fbde7ad8e51500711346dd892cacdff2"
        in delta_by_id["E2SCT-029"]["github_head_shas"],
        "High-value delta refresh lost MIA_SD GitHub identity",
    )
    require(
        "paper-2229/openlvlm-mia@a4656ebdf1e0ba8c04fae43acd8022e6cc699bbb"
        in delta_by_id["E2SCT-035"]["hf_shas"]
        and "paper-2229/openclip-llava@8c57a060bd4f2fe6cfe403cbf673f693ff00da26"
        in delta_by_id["E2SCT-035"]["hf_shas"],
        "High-value delta refresh lost OpenLVLM-MIA HF dataset/model identity",
    )
    delta_md = (PREFLIGHT / "e2_high_value_public_asset_delta_refresh_2026_06_09.md").read_text(
        encoding="utf-8"
    )
    require("`identity_matched`: 9" in delta_md, "High-value delta markdown lost identity-matched count")
    require(
        "`priority_gate_review`: 9" in delta_md,
        "High-value delta markdown must keep all refreshed rows in manual gate review after git-tree fallback",
    )
    require(
        "no C14/N50 update, no admitted evidence, no second public score/response asset, and no compute release"
        in delta_md,
        "High-value delta markdown lost no-upgrade boundary",
    )
    delta_gate_queue = read_csv(PREFLIGHT / "e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv")
    require(
        {row["scout_queue_id"] for row in delta_gate_queue} == expected_delta_ids,
        "High-value delta gate queue must contain all nine high-value manual-review rows",
    )
    e2sct024_rows = read_csv(PREFLIGHT / "e2sct024_dme_public_surface_check_2026_06_08.csv")
    e2sct024_by_item = {row["item"]: row for row in e2sct024_rows}
    require(
        e2sct024_by_item["repo_identity"]["status"] == "partial",
        "E2SCT-024 must preserve the public branch identity finding",
    )
    require(
        "ae0cc48476746945720bf24b42d4f9dfecb6de31" in e2sct024_by_item["repo_identity"]["evidence"],
        "E2SCT-024 repo identity must preserve the current public commit",
    )
    require(
        e2sct024_by_item["github_html_surface"]["status"] == "partial",
        "E2SCT-024 must preserve the README-only GitHub surface finding",
    )
    require(
        "1 Commit" in e2sct024_by_item["github_html_surface"]["evidence"],
        "E2SCT-024 GitHub HTML finding must preserve the one-commit pressure",
    )
    require(
        e2sct024_by_item["readme_surface"]["status"] == "partial",
        "E2SCT-024 must preserve the raw README support status",
    )
    require(
        "b0d1cf04d92d47577a830e6d57477d10d3909ee138ef10b7dea6ed02ecedd225"
        in e2sct024_by_item["readme_surface"]["evidence"],
        "E2SCT-024 README finding must preserve the raw README hash",
    )
    require(
        e2sct024_by_item["artifact_surface"]["status"] == "fail",
        "E2SCT-024 must remain blocked without public implementation/artifacts",
    )
    require(
        "row_bound_score_response_metric_packet_missing" in e2sct024_by_item["artifact_surface"]["boundary"],
        "E2SCT-024 artifact blocker must remain explicit",
    )
    require(
        e2sct024_by_item["admission_decision"]["status"] == "fail",
        "E2SCT-024 admission decision must stay fail",
    )
    require(
        "official-repo-stub false-promotion exemplar only"
        in e2sct024_by_item["admission_decision"]["evidence"],
        "E2SCT-024 admission decision must stay official-repo-stub false-promotion only",
    )
    require(
        "not admitted; not response/score evidence; not external denominator; no_compute_release"
        in e2sct024_by_item["admission_decision"]["evidence"],
        "E2SCT-024 admission decision lost no-admission/no-denominator/no-compute boundary",
    )
    e2sct024_md = (PREFLIGHT / "e2sct024_dme_public_surface_check_2026_06_08.md").read_text(
        encoding="utf-8"
    )
    require("no_compute_release" in e2sct024_md, "E2SCT-024 markdown decision lost no-compute boundary")
    require(
        "Count `E2SCT-024` only as a selected false-promotion stress row" in e2sct024_md,
        "E2SCT-024 markdown decision lost selected-stress-row boundary",
    )
    require(
        "Do not clone the repository" in e2sct024_md
        and "Do not implement DME" in e2sct024_md
        and "GPU/DCU jobs" in e2sct024_md,
        "E2SCT-024 markdown decision lost no-clone/no-implementation/no-GPU boundary",
    )
    exemplar_md = (PREFLIGHT / "e2_false_promotion_exemplar_summary_2026_06_07.md").read_text(encoding="utf-8")
    require(
        "not external adjudication evidence" in exemplar_md,
        "False-promotion summary must preserve external-adjudication boundary",
    )
    require(
        "attribution versus membership" in exemplar_md,
        "False-promotion summary must preserve semantic-boundary row purpose",
    )
    require(
        "classifier defense versus diffusion-generator" in exemplar_md,
        "False-promotion summary must preserve classifier-defense consumer-boundary row purpose",
    )
    require(
        "not compute release" in exemplar_md,
        "False-promotion summary must preserve no-compute boundary",
    )
    require(
        "mock visualization data" in exemplar_md,
        "False-promotion summary must preserve the LSA-Probe mock-demo boundary",
    )

    expansion_rows = read_csv(PREFLIGHT / "e2_false_promotion_expansion_queue_2026_06_07.csv")
    expected_expansion_ids: list[str] = []
    require(
        [row["row_id"] for row in expansion_rows] == expected_expansion_ids,
        "Post-C14 false-promotion expansion queue row order drifted",
    )
    for row in expansion_rows:
        row_id = row["row_id"]
        require(row_id not in exemplar_by_id, f"{row_id} must not duplicate the completed C14 exemplar set")
        require(
            row["admission_status"] == "not_admitted",
            f"{row_id} expansion queue admission_status must remain not_admitted",
        )
        require(
            row["denominator_status"] == "not_denominator_pending_detailed_check",
            f"{row_id} expansion queue denominator_status must remain pending detailed check",
        )
        require(row["compute_release"] == "no", f"{row_id} expansion queue must preserve compute_release=no")
        require(
            row["paper_action"] == "do_not_update_C14_until_row_check_passes",
            f"{row_id} expansion queue must not update C14 before row checks",
        )
        require(
            "paper_claim_artifact_link_would_promote" in row["weak_rules_pressure"],
            f"{row_id} expansion queue must preserve weak-rule pressure framing",
        )
        require(
            "Detailed row-level public-surface check not yet completed" in row["first_blocker"],
            f"{row_id} expansion queue must preserve row-level check blocker",
        )
    expansion_md = (PREFLIGHT / "e2_false_promotion_expansion_queue_2026_06_07.md").read_text(
        encoding="utf-8"
    )
    require(
        "不是 admitted evidence，不是 N50 external denominator，也不释放 GPU/DCU" in expansion_md,
        "Post-C14 expansion queue must preserve no-admission/no-denominator/no-compute boundary",
    )
    require(
        "Do not update the paper C14 selected-row count from `13`" in expansion_md,
        "Post-C14 expansion queue must preserve the C14 no-update boundary",
    )
    require(
        "E2SCT-028" in expansion_md,
        "Post-C14 expansion queue markdown must explain the SD-MIA/E2SCT-028 closure",
    )
    for row_id in expected_expansion_ids:
        require(row_id in expansion_md, f"Post-C14 expansion queue markdown missing {row_id}")

    rule_summary = read_csv(PAPER / "data" / "false_promotion_rule_summary.csv")
    expected_rule_counts = {
        "code_availability_would_promote": 12,
        "artifact_availability_would_promote": 7,
        "paper_claim_artifact_link_would_promote": 12,
        "metric_code_split_would_promote": 9,
        "score_only_would_promote": 0,
    }
    require(
        len(rule_summary) == len(expected_rule_counts),
        "False-promotion rule summary must keep exactly five weak-rule rows",
    )
    rule_summary_by_rule = {row["weak_rule"]: row for row in rule_summary}
    require(
        set(rule_summary_by_rule) == set(expected_rule_counts),
        "False-promotion rule summary weak-rule set drifted",
    )
    for rule, expected_count in expected_rule_counts.items():
        row = rule_summary_by_rule[rule]
        require(
            row["would_promote_rows"] == str(expected_count),
            f"False-promotion rule summary count drifted for {rule}",
        )
        require(
            row["selected_row_count"] == "13",
            f"False-promotion rule summary selected row count drifted for {rule}",
        )
        require(
            row["boundary_note"] == "weak-rule count over selected stress rows; not denominator or prevalence evidence",
            f"False-promotion rule summary boundary note drifted for {rule}",
        )

    admitted_text = (PAPER / "data" / "admitted_rows.csv").read_text(encoding="utf-8")
    require(
        "E2SCT-003" not in admitted_text and "DurMI" not in admitted_text,
        "DurMI/E2SCT-003 must not enter admitted_rows.csv",
    )
    require(
        "E2SCT-025" not in admitted_text and "Hyperparameter-Free SecMI" not in admitted_text,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter admitted_rows.csv",
    )
    require(
        "E2SCT-029" not in admitted_text and "MIA_SD" not in admitted_text,
        "MIA_SD/E2SCT-029 must not enter admitted_rows.csv",
    )
    require(
        "E2SCT-030" not in admitted_text and "Frequency Components" not in admitted_text,
        "FMIA/Frequency/E2SCT-030 must not enter admitted_rows.csv",
    )
    for row_id, label in recent_support_only_ids.items():
        require(row_id not in admitted_text, f"{label} must not enter admitted_rows.csv")

    negative_support_text = (PAPER / "data" / "negative_support_rows.csv").read_text(encoding="utf-8")
    recent_support_only_negative_tokens = {
        "E2SCT-031": ["E2SCT-031", "SAMA", "sama-dlm-public-surface-check"],
        "E2SCT-032": ["E2SCT-032", "MIA-EPT", "miaept-tabular-public-surface-check"],
        "E2SCT-033": ["E2SCT-033", "Diffusion MIA", "diffusion-mia-public-surface-check"],
        "E2SCT-034": ["E2SCT-034", "ReMIA", "remia-tabular-public-result-archive-check"],
        "E2SCT-035": ["E2SCT-035", "OpenLVLM-MIA", "openlvlm-mia-vlm-public-surface-check"],
    }
    for row_id, tokens in recent_support_only_negative_tokens.items():
        label = recent_support_only_ids[row_id]
        for token in tokens:
            require(
                token not in negative_support_text,
                f"{label} must not enter metric-bearing negative_support_rows.csv",
            )

    false_promotion_packet = read_csv(PAPER / "data" / "false_promotion_external_review_packet.csv")
    require(
        list(false_promotion_packet[0].keys()) == FALSE_PROMOTION_PACKET_FIELDS,
        "False-promotion external review packet header drifted",
    )
    require(len(false_promotion_packet) == 13, "False-promotion external review packet must contain thirteen rows")
    packet_ids = {row["source_row_id"] for row in false_promotion_packet}
    require(packet_ids == set(exemplar_by_id), "False-promotion external review packet row IDs drifted")
    require(
        "E2SCT-028" not in packet_ids,
        "SD-MIA/E2SCT-028 must not enter the false-promotion external review packet",
    )
    require(
        "E2SCT-003" not in packet_ids,
        "DurMI/E2SCT-003 must not enter the false-promotion external review packet",
    )
    require(
        "E2SCT-025" not in packet_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion external review packet",
    )
    require(
        "E2SCT-029" not in packet_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion external review packet",
    )
    require(
        "E2SCT-030" not in packet_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion external review packet",
    )
    for row_id, label in recent_support_only_ids.items():
        require(
            row_id not in packet_ids,
            f"{label} must not enter the current false-promotion external review packet",
        )
    for row in false_promotion_packet:
        require(
            row["packet_status"] == "prepared_not_adjudicated",
            f"{row['source_row_id']} review packet must remain prepared_not_adjudicated",
        )
        require(row["reviewer"] == "", f"{row['source_row_id']} review packet reviewer must stay blank")
        require(
            row["external_decision"] == "",
            f"{row['source_row_id']} review packet external_decision must stay blank",
        )
        require(row["external_notes"] == "", f"{row['source_row_id']} review packet notes must stay blank")
        require(
            row["source_no_compute_release"] == "1",
            f"{row['source_row_id']} review packet lost no-compute source flag",
        )
        require(
            "weak-rule promotion" in row["review_question"],
            f"{row['source_row_id']} review question lost false-promotion framing",
        )
        require(
            "not" in row["source_allowed_wording"],
            f"{row['source_row_id']} review packet lost non-admission wording",
        )

    false_promotion_blinded_packet = read_csv(PAPER / "data" / "false_promotion_blinded_review_packet.csv")
    require(
        list(false_promotion_blinded_packet[0].keys()) == FALSE_PROMOTION_BLINDED_PACKET_FIELDS,
        "False-promotion blinded review packet header drifted",
    )
    require(
        len(false_promotion_blinded_packet) == 13,
        "False-promotion blinded review packet must contain thirteen rows",
    )
    blinded_ids = {row["source_row_id"] for row in false_promotion_blinded_packet}
    require(blinded_ids == set(exemplar_by_id), "False-promotion blinded packet row IDs drifted")
    require(
        "E2SCT-028" not in blinded_ids,
        "SD-MIA/E2SCT-028 must not enter the false-promotion blinded packet",
    )
    require(
        "E2SCT-003" not in blinded_ids,
        "DurMI/E2SCT-003 must not enter the false-promotion blinded packet",
    )
    require(
        "E2SCT-025" not in blinded_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion blinded packet",
    )
    require(
        "E2SCT-029" not in blinded_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion blinded packet",
    )
    require(
        "E2SCT-030" not in blinded_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion blinded packet",
    )
    for row_id, label in recent_support_only_ids.items():
        require(
            row_id not in blinded_ids,
            f"{label} must not enter the current false-promotion blinded packet",
        )
    for row in false_promotion_blinded_packet:
        require(
            row["packet_status"] == "blocker_blinded_prepared_not_adjudicated",
            f"{row['source_row_id']} blinded packet status drifted",
        )
        require(
            "weak-rule promotion" in row["review_question"],
            f"{row['source_row_id']} blinded review question lost weak-rule framing",
        )

    false_promotion_key = read_csv(PAPER / "data" / "false_promotion_adjudication_key.csv")
    require(
        list(false_promotion_key[0].keys()) == FALSE_PROMOTION_ADJUDICATION_KEY_FIELDS,
        "False-promotion adjudication key header drifted",
    )
    require(len(false_promotion_key) == 13, "False-promotion adjudication key must contain thirteen rows")
    key_ids = {row["source_row_id"] for row in false_promotion_key}
    require(key_ids == set(exemplar_by_id), "False-promotion adjudication key row IDs drifted")
    require(
        "E2SCT-028" not in key_ids,
        "SD-MIA/E2SCT-028 must not enter the false-promotion author key",
    )
    require(
        "E2SCT-003" not in key_ids,
        "DurMI/E2SCT-003 must not enter the false-promotion author key",
    )
    require(
        "E2SCT-025" not in key_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion author key",
    )
    require(
        "E2SCT-029" not in key_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion author key",
    )
    require(
        "E2SCT-030" not in key_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion author key",
    )
    for row_id, label in recent_support_only_ids.items():
        require(row_id not in key_ids, f"{label} must not enter the current false-promotion author key")
    for row in false_promotion_key:
        require(
            row["author_false_promotion_verdict"] in FALSE_PROMOTION_VERDICT_VALUES,
            f"{row['source_row_id']} adjudication key verdict drifted",
        )
        require(row["author_compute_release"] == "no", f"{row['source_row_id']} key compute release drifted")
        require(row["author_no_compute_release"] == "1", f"{row['source_row_id']} key lost no-compute source flag")
        require(row["key_status"] == "author_key_not_external_label", f"{row['source_row_id']} key status drifted")

    false_promotion_template = read_csv(PAPER / "data" / "false_promotion_external_review_template.csv")
    require(
        list(false_promotion_template[0].keys()) == FALSE_PROMOTION_TEMPLATE_FIELDS,
        "False-promotion external review template header drifted",
    )
    require(len(false_promotion_template) == 13, "False-promotion external review template must contain thirteen rows")
    template_ids = {row["source_row_id"] for row in false_promotion_template}
    require(template_ids == set(exemplar_by_id), "False-promotion external review template row IDs drifted")
    require(
        "E2SCT-025" not in template_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion review template",
    )
    require(
        "E2SCT-029" not in template_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion review template",
    )
    require(
        "E2SCT-030" not in template_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion review template",
    )
    for row_id, label in recent_support_only_ids.items():
        require(
            row_id not in template_ids,
            f"{label} must not enter the current false-promotion review template",
        )
    blank_review_fields = [
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
    for row in false_promotion_template:
        require(
            row["gate_allowed_values"] == "Pass|Partial|Fail|N/A",
            f"{row['source_row_id']} review template gate_allowed_values drifted",
        )
        require(
            set(row["verdict_allowed_values"].split("|")) == FALSE_PROMOTION_VERDICT_VALUES,
            f"{row['source_row_id']} review template verdict_allowed_values drifted",
        )
        require(
            row["compute_release_allowed_values"] == "no|yes_with_full_contract",
            f"{row['source_row_id']} review template compute_release_allowed_values drifted",
        )
        for field in blank_review_fields:
            require(row[field] == "", f"{row['source_row_id']} review template {field} must stay blank")

    false_promotion_trace = read_csv(PAPER / "data" / "false_promotion_row_trace.csv")
    require(
        list(false_promotion_trace[0].keys()) == FALSE_PROMOTION_ROW_TRACE_FIELDS,
        "False-promotion row trace header drifted",
    )
    require(len(false_promotion_trace) == 13, "False-promotion row trace must contain thirteen rows")
    trace_ids = {row["source_row_id"] for row in false_promotion_trace}
    require(trace_ids == set(exemplar_by_id), "False-promotion row trace IDs drifted")
    require(
        "E2SCT-025" not in trace_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion row trace",
    )
    require(
        "E2SCT-029" not in trace_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion row trace",
    )
    require(
        "E2SCT-030" not in trace_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion row trace",
    )
    for row_id, label in recent_support_only_ids.items():
        require(row_id not in trace_ids, f"{label} must not enter the current false-promotion row trace")
    for row in false_promotion_trace:
        require(row["trace_status"] == "no-download public-surface trace", f"{row['source_row_id']} trace status drifted")
        require("http" in row["public_urls"], f"{row['source_row_id']} trace lost public URL")
        for field in ("source_check_csv_sha256", "source_check_md_sha256", "source_summary_row_sha256"):
            value = row[field]
            require(
                len(value) == 64 and all(char in "0123456789abcdef" for char in value),
                f"{row['source_row_id']} invalid {field}",
            )

    false_promotion_gate_matrix = read_csv(PAPER / "data" / "false_promotion_author_gate_matrix.csv")
    require(
        list(false_promotion_gate_matrix[0].keys()) == FALSE_PROMOTION_AUTHOR_GATE_MATRIX_FIELDS,
        "False-promotion author gate matrix header drifted",
    )
    require(
        len(false_promotion_gate_matrix) == 13,
        "False-promotion author gate matrix must contain thirteen rows",
    )
    matrix_ids = {row["source_row_id"] for row in false_promotion_gate_matrix}
    require(matrix_ids == set(exemplar_by_id), "False-promotion author gate matrix row IDs drifted")
    require(
        "E2SCT-025" not in matrix_ids,
        "Hyperparameter-Free SecMI/E2SCT-025 must not enter the false-promotion author gate matrix",
    )
    require(
        "E2SCT-029" not in matrix_ids,
        "MIA_SD/E2SCT-029 must not enter the current false-promotion author gate matrix",
    )
    require(
        "E2SCT-030" not in matrix_ids,
        "FMIA/Frequency/E2SCT-030 must not enter the current false-promotion author gate matrix",
    )
    for row_id, label in recent_support_only_ids.items():
        require(
            row_id not in matrix_ids,
            f"{label} must not enter the current false-promotion author gate matrix",
        )
    matrix_counts = {
        gate: {outcome: 0 for outcome in VALID_GATES}
        for gate in FALSE_PROMOTION_AUTHOR_GATE_FIELDS
    }
    for row in false_promotion_gate_matrix:
        row_id = row["source_row_id"]
        require(row["label_source"] == "author_key_not_external_label", f"{row_id} matrix label source drifted")
        require(row["compute_release"] == "no", f"{row_id} matrix compute_release must remain no")
        require(row["first_blocking_gate"] in FALSE_PROMOTION_AUTHOR_GATE_FIELDS, f"{row_id} first blocker gate drifted")
        require(row["gate_rationale"], f"{row_id} matrix gate rationale is empty")
        require(
            "not external adjudication" in row["matrix_boundary"],
            f"{row_id} matrix lost no-external-adjudication boundary",
        )
        require(
            "denominator evidence" in row["matrix_boundary"],
            f"{row_id} matrix lost no-denominator-evidence boundary",
        )
        for gate in FALSE_PROMOTION_AUTHOR_GATE_FIELDS:
            value = row[gate]
            require(value in VALID_GATES, f"{row_id} matrix {gate} has invalid value {value!r}")
            matrix_counts[gate][value] += 1

    false_promotion_gate_summary = read_csv(PAPER / "data" / "false_promotion_gate_summary.csv")
    require(
        list(false_promotion_gate_summary[0].keys()) == FALSE_PROMOTION_AUTHOR_GATE_SUMMARY_FIELDS,
        "False-promotion gate summary header drifted",
    )
    require(
        len(false_promotion_gate_summary) == len(FALSE_PROMOTION_AUTHOR_GATE_FIELDS) * len(VALID_GATES),
        "False-promotion gate summary must contain seven gates x four outcomes",
    )
    summary_keys = set()
    for row in false_promotion_gate_summary:
        gate = row["gate"]
        outcome = row["outcome"]
        summary_keys.add((gate, outcome))
        require(gate in FALSE_PROMOTION_AUTHOR_GATE_FIELDS, f"False-promotion gate summary unknown gate {gate!r}")
        require(outcome in VALID_GATES, f"False-promotion gate summary unknown outcome {outcome!r}")
        require(row["count"] == str(matrix_counts[gate][outcome]), f"False-promotion gate summary count drifted for {gate}/{outcome}")
        require(row["selected_row_count"] == "13", f"False-promotion gate summary selected row count drifted for {gate}/{outcome}")
        require(
            "not external reliability or prevalence evidence" in row["boundary_note"],
            f"False-promotion gate summary boundary note drifted for {gate}/{outcome}",
        )
    require(
        summary_keys == {
            (gate, outcome)
            for gate in FALSE_PROMOTION_AUTHOR_GATE_FIELDS
            for outcome in VALID_GATES
        },
        "False-promotion gate summary grid drifted",
    )

    codebook = (PAPER / "versions" / "direction-a-false-promotion-audit-codebook.md").read_text(
        encoding="utf-8"
    )
    require(
        "not completed external adjudication" in codebook,
        "False-promotion codebook lost no-external-adjudication boundary",
    )
    require(
        "not inter-rater reliability evidence" in codebook,
        "False-promotion codebook lost no-reliability boundary",
    )
    require("not an N50 denominator result" in codebook, "False-promotion codebook lost no-N50 boundary")
    require("blocker-blinded packet" in codebook, "False-promotion codebook lost blocker-blinded packet protocol")
    require("thirteen rows" in codebook, "False-promotion codebook lost thirteen-row scope")
    require(
        "Leave `compute_release` as `no` unless" in codebook,
        "False-promotion codebook lost compute-release gate",
    )
    require(
        "paper_claim_artifact_link_would_promote` | `12 of 13 selected rows`" in codebook,
        "False-promotion codebook lost 12-of-13 paper-link count",
    )
    require(
        "code_availability_would_promote` | `12 of 13 selected rows`" in codebook,
        "False-promotion codebook lost 12-of-13 code count",
    )
    require(
        "metric_code_split_would_promote` | `9 of 13 selected rows`" in codebook,
        "False-promotion codebook lost 9-of-13 metric/split count",
    )
    require(
        "artifact_availability_would_promote` | `7 of 13 selected rows`" in codebook,
        "False-promotion codebook lost 7-of-13 artifact count",
    )
    require(
        "score_only_would_promote` | `0 of 13 selected rows`" in codebook,
        "False-promotion codebook lost 0-of-13 score-only count",
    )

    print("E2 freeze preflight boundary check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
