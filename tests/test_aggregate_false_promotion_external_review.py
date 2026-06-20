from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import aggregate_false_promotion_external_review as aggregate


def make_synthetic_review_rows(
    reviewers: list[str],
    transform=None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    template_rows, _, key_rows = aggregate.load_packet_inputs(aggregate.PAPER)
    gate_rows = aggregate.read_csv(
        aggregate.PAPER / "data" / "false_promotion_author_gate_matrix.csv"
    )
    gate_by_review_id = {row["review_id"]: row for row in gate_rows}
    key_by_review_id = {row["review_id"]: row for row in key_rows}

    review_rows: list[dict[str, str]] = []
    for reviewer in reviewers:
        for row_index, template in enumerate(template_rows):
            review_id = template["review_id"]
            gate_row = gate_by_review_id[review_id]
            key_row = key_by_review_id[review_id]
            row = dict(template)
            row["reviewer"] = reviewer
            for field in aggregate.GATE_FIELDS:
                row[field] = gate_row[field]
            row["false_promotion_verdict"] = key_row["author_false_promotion_verdict"]
            row["first_blocker"] = key_row["author_contract_blocker"]
            row["allowed_wording"] = key_row["author_allowed_wording"]
            row["compute_release"] = "no"
            row["notes"] = "synthetic unit-test label; not evidence"
            if transform is not None:
                transform(row, reviewer, row_index)
            review_rows.append(row)
    return template_rows, key_rows, review_rows


def aggregate_synthetic(
    reviewers: list[str],
    transform=None,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    template_rows, key_rows, review_rows = make_synthetic_review_rows(reviewers, transform)
    combined, _, agreement, _ = aggregate.aggregate_reviews(
        template_rows,
        key_rows,
        review_rows,
        min_reviewers=2,
        reliability_min_reviewers=3,
        min_mean_kappa=0.6,
        min_field_kappa=0.5,
    )
    packet_status = aggregate.build_packet_status_rows(
        sorted(reviewers),
        combined,
        agreement,
        min_reviewers=2,
        reliability_min_reviewers=3,
        min_mean_kappa=0.6,
        min_field_kappa=0.5,
        require_no_majority_ties=True,
    )
    return combined, agreement, packet_status


class FalsePromotionExternalReviewAggregationTests(unittest.TestCase):
    def test_no_reviewer_status_is_packet_ready_only(self) -> None:
        packet_status = aggregate.build_packet_status_rows(
            [],
            [],
            [],
            min_reviewers=2,
            reliability_min_reviewers=3,
            min_mean_kappa=0.6,
            min_field_kappa=0.5,
            require_no_majority_ties=True,
            declaration_status="not_checked_no_reviewer_csvs",
        )
        packet = packet_status[0]

        self.assertEqual(packet["packet_label_readiness"], "prepared_no_reviewer_csvs")
        self.assertEqual(packet["reviewer_count_status"], "none")
        self.assertEqual(packet["allowed_claim_scope"], "packet_ready_only")
        self.assertEqual(packet["external_label_aggregation_available"], 0)
        self.assertEqual(packet["completed_external_adjudication_allowed"], 0)
        self.assertEqual(packet["reliability_claim_allowed"], 0)
        self.assertEqual(packet["compute_release_allowed"], 0)

    def test_no_label_outputs_write_status_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            stale_aggregation = output_dir / "false_promotion_external_review_aggregation.csv"
            stale_aggregation.write_text("stale\n", encoding="utf-8")
            packet_status = aggregate.write_no_label_outputs(
                output_dir,
                min_reviewers=2,
                reliability_min_reviewers=3,
                min_mean_kappa=0.6,
                min_field_kappa=0.5,
                require_no_majority_ties=True,
            )

            self.assertTrue((output_dir / "false_promotion_external_review_packet_status.csv").exists())
            self.assertTrue((output_dir / "false_promotion_external_review_aggregation.md").exists())
            self.assertFalse((output_dir / "false_promotion_external_review_aggregation.csv").exists())
            self.assertEqual(packet_status[0]["allowed_claim_scope"], "packet_ready_only")

    def test_missing_declaration_blocks_review_intake(self) -> None:
        errors: list[str] = []
        rows = aggregate.validate_declarations([], ["fpr-r01"], errors)

        self.assertEqual(rows, [])
        self.assertIn("reviewer declaration files are required when reviewer CSVs are present", errors)

    def test_main_rejects_declaration_without_matching_review_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "out"
            declaration = Path(tmpdir) / "REVIEWER_DECLARATION_fpr-r01.md"
            declaration.write_text(
                "\n".join(
                    [
                        "reviewer_id: fpr-r01",
                        "used_same_reviewer_id: yes",
                        "no_post_label_author_key_before_labels: yes",
                        "no_llm_ai_assistance: yes",
                        "no_reviewer_discussion: yes",
                        "did_not_create_c14_materials: yes",
                        "no_large_download_or_execution: yes",
                        "understands_no_post_submission_revision: yes",
                        "signature: Reviewer One",
                        "date: 2026-06-08",
                    ]
                ),
                encoding="utf-8",
            )

            with patch(
                "sys.argv",
                [
                    "aggregate_false_promotion_external_review.py",
                    "--declaration-file",
                    str(declaration),
                    "--output-dir",
                    str(output_dir),
                    "--check",
                ],
            ):
                exit_code = aggregate.main()

        self.assertEqual(exit_code, 1)
        self.assertFalse((output_dir / "false_promotion_external_review_packet_status.csv").exists())

    def test_valid_machine_readable_declaration_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "REVIEWER_DECLARATION_fpr-r01.md"
            path.write_text(
                "\n".join(
                    [
                        "reviewer_id: fpr-r01",
                        "used_same_reviewer_id: yes",
                        "no_post_label_author_key_before_labels: yes",
                        "no_llm_ai_assistance: yes",
                        "no_reviewer_discussion: yes",
                        "did_not_create_c14_materials: yes",
                        "no_large_download_or_execution: yes",
                        "understands_no_post_submission_revision: yes",
                        "signature: Reviewer One",
                        "date: 2026-06-08",
                    ]
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            rows = aggregate.validate_declarations([path], ["fpr-r01"], errors)

        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["reviewer"], "fpr-r01")
        self.assertEqual(rows[0]["declaration_status"], "valid_independence_attestation")

    def test_review_csv_rejects_filename_reviewer_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            template_rows, _, review_rows = make_synthetic_review_rows(["fpr-r01"])
            path = Path(tmpdir) / "false_promotion_external_review_fpr-r02.csv"
            aggregate.write_csv(path, review_rows, aggregate.TEMPLATE_FIELDS)
            errors: list[str] = []

            aggregate.validate_review_rows([path], template_rows, errors)

        self.assertIn(
            f"{path} filename reviewer 'fpr-r02' does not match CSV reviewer 'fpr-r01'",
            errors,
        )

    def test_review_csv_rejects_unstable_reviewer_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            template_rows, _, review_rows = make_synthetic_review_rows(["Reviewer One"])
            path = Path(tmpdir) / "false_promotion_external_review_Reviewer One.csv"
            aggregate.write_csv(path, review_rows, aggregate.TEMPLATE_FIELDS)
            errors: list[str] = []

            aggregate.validate_review_rows([path], template_rows, errors)

        self.assertIn(
            f"{path} filename reviewer 'Reviewer One' must match [a-z][a-z0-9-]{{2,31}}",
            errors,
        )
        self.assertIn(
            f"{path} CSV reviewer 'Reviewer One' must match [a-z][a-z0-9-]{{2,31}}",
            errors,
        )

    def test_declaration_rejects_filename_reviewer_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "REVIEWER_DECLARATION_fpr-r02.md"
            path.write_text(
                "\n".join(
                    [
                        "reviewer_id: fpr-r01",
                        "used_same_reviewer_id: yes",
                        "no_post_label_author_key_before_labels: yes",
                        "no_llm_ai_assistance: yes",
                        "no_reviewer_discussion: yes",
                        "did_not_create_c14_materials: yes",
                        "no_large_download_or_execution: yes",
                        "understands_no_post_submission_revision: yes",
                        "signature: Reviewer One",
                        "date: 2026-06-08",
                    ]
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            aggregate.validate_declarations([path], ["fpr-r01"], errors)

        self.assertIn(
            f"{path} filename reviewer 'fpr-r02' does not match declaration reviewer_id 'fpr-r01'",
            errors,
        )

    def test_review_csv_rejects_row_order_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            template_rows, _, review_rows = make_synthetic_review_rows(["fpr-r01"])
            path = Path(tmpdir) / "false_promotion_external_review_fpr-r01.csv"
            aggregate.write_csv(path, list(reversed(review_rows)), aggregate.TEMPLATE_FIELDS)
            errors: list[str] = []

            aggregate.validate_review_rows([path], template_rows, errors)

        self.assertIn(f"{path} row order changed at position 1", errors)

    def test_review_csv_rejects_compute_release_without_full_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            template_rows, _, review_rows = make_synthetic_review_rows(["fpr-r01"])
            review_rows[0]["compute_release"] = "yes_with_full_contract"
            review_rows[0]["score_or_response_gate"] = "Fail"
            path = Path(tmpdir) / "false_promotion_external_review_fpr-r01.csv"
            aggregate.write_csv(path, review_rows, aggregate.TEMPLATE_FIELDS)
            errors: list[str] = []

            aggregate.validate_review_rows([path], template_rows, errors)

        self.assertTrue(
            any(
                "fpr-r01/E2SCT-004 compute_release=yes_with_full_contract but contract gates are not all Pass"
                in error
                for error in errors
            )
        )

    def test_two_reviewers_allow_selected_row_aggregation_but_no_reliability(self) -> None:
        combined, agreement, packet_status = aggregate_synthetic(["fpr-r01", "fpr-r02"])
        packet = packet_status[0]

        self.assertEqual(packet["reviewer_count_status"], "min_2_external_label_aggregation_available")
        self.assertEqual(packet["majority_resolution_status"], "resolved")
        self.assertEqual(packet["reliability_threshold_status"], "not_applicable_below_3")
        self.assertEqual(packet["external_label_aggregation_available"], 1)
        self.assertEqual(packet["reliability_claim_allowed"], 0)
        self.assertEqual(packet["completed_external_adjudication_allowed"], 0)
        self.assertEqual(packet["compute_release_allowed"], 0)
        self.assertTrue(
            all(row["external_review_status"] == "unanimous_resolved_selected_rows_only" for row in combined)
        )
        self.assertTrue(
            all(row["reliability_threshold_status"] == "not_applicable_below_3" for row in agreement)
        )

    def test_three_reviewers_threshold_pass_is_not_an_adjudication_or_claim_switch(self) -> None:
        template_rows, key_rows, review_rows = make_synthetic_review_rows(["fpr-r01", "fpr-r02", "fpr-r03"])
        combined, _, agreement, _ = aggregate.aggregate_reviews(
            template_rows,
            key_rows,
            review_rows,
            min_reviewers=2,
            reliability_min_reviewers=3,
            min_mean_kappa=0.6,
            min_field_kappa=0.5,
        )
        packet_status = aggregate.build_packet_status_rows(
            ["fpr-r01", "fpr-r02", "fpr-r03"],
            combined,
            agreement,
            min_reviewers=2,
            reliability_min_reviewers=3,
            min_mean_kappa=0.6,
            min_field_kappa=0.5,
            require_no_majority_ties=True,
            declaration_status="valid_independence_attestation",
        )
        packet = packet_status[0]

        self.assertEqual(packet["reviewer_count_status"], "three_plus_reliability_protocol_available")
        self.assertEqual(packet["declaration_status"], "valid_independence_attestation")
        self.assertEqual(packet["reliability_threshold_status"], "passed")
        self.assertEqual(packet["reliability_threshold_met"], 1)
        self.assertEqual(
            packet["allowed_claim_scope"],
            "external_label_aggregation_selected_13_rows_only_reliability_thresholds_met_not_adjudication",
        )
        self.assertEqual(packet["reliability_claim_allowed"], 0)
        self.assertEqual(packet["completed_external_adjudication_allowed"], 0)
        self.assertTrue(all(row["reliability_threshold_status"] == "passed" for row in agreement))

    def test_three_reviewers_low_kappa_fails_reliability_thresholds(self) -> None:
        flip_gate = {"Pass": "Fail", "Fail": "Pass", "Partial": "N/A", "N/A": "Partial"}

        def noisy_third_reviewer(row: dict[str, str], reviewer: str, row_index: int) -> None:
            if reviewer != "fpr-r03":
                return
            for field in aggregate.GATE_FIELDS:
                row[field] = flip_gate[row[field]]
            row["false_promotion_verdict"] = (
                "invalid_row" if row_index % 2 == 0 else "needs_external_adjudication"
            )

        combined, agreement, packet_status = aggregate_synthetic(
            ["fpr-r01", "fpr-r02", "fpr-r03"],
            noisy_third_reviewer,
        )
        packet = packet_status[0]

        self.assertEqual(packet["reviewer_count_status"], "three_plus_reliability_protocol_available")
        self.assertEqual(packet["majority_resolution_status"], "resolved")
        self.assertEqual(packet["reliability_threshold_status"], "failed")
        self.assertEqual(packet["reliability_threshold_met"], 0)
        self.assertEqual(packet["reliability_claim_allowed"], 0)
        self.assertTrue(
            any(
                row["external_review_status"]
                == "majority_resolved_with_disagreements_selected_rows_only"
                for row in combined
            )
        )
        self.assertTrue(any(row["reliability_threshold_status"] == "failed" for row in agreement))

    def test_majority_tie_keeps_packet_unresolved_even_with_four_reviewers(self) -> None:
        def tie_first_row(row: dict[str, str], reviewer: str, row_index: int) -> None:
            if row_index == 0 and reviewer in {"fpr-r03", "fpr-r04"}:
                row["false_promotion_verdict"] = "semantic_boundary_block"

        combined, _, packet_status = aggregate_synthetic(
            ["fpr-r01", "fpr-r02", "fpr-r03", "fpr-r04"],
            tie_first_row,
        )
        packet = packet_status[0]

        self.assertEqual(packet["majority_resolution_status"], "unresolved_majority_tie")
        self.assertEqual(packet["reliability_threshold_status"], "failed_majority_ties")
        self.assertEqual(packet["reliability_threshold_met"], 0)
        self.assertEqual(packet["reliability_claim_allowed"], 0)
        self.assertEqual(combined[0]["external_review_status"], "unresolved_majority_tie")
        self.assertEqual(combined[0]["false_promotion_verdict_majority"], "UNRESOLVED_TIE")


if __name__ == "__main__":
    unittest.main()
