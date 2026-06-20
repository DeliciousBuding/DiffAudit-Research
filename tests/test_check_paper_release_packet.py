from __future__ import annotations

import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import check_paper_release_packet as release_check


def write_status_row(paper: Path, row: dict[str, str] | None = None) -> None:
    build_dir = paper / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(release_check.C14_NO_REVIEWER_STATUS)
    if row:
        payload.update(row)
    with (build_dir / release_check.C14_PACKET_STATUS).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.C14_PACKET_STATUS_FIELDS)
        writer.writeheader()
        writer.writerow(payload)


def write_no_label_markdown(paper: Path) -> None:
    path = paper / "build" / release_check.C14_AGGREGATION_MD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "No reviewer CSVs were loaded. This is not external adjudication.",
        encoding="utf-8",
    )


def write_post_label_markdown(paper: Path) -> None:
    path = paper / "build" / release_check.C14_AGGREGATION_MD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# C14 False-Promotion External Review Aggregation",
                "",
                "> Boundary: not N50 denominator evidence, not field prevalence, not completed external adjudication, not compute release.",
                "",
                "Reviewers loaded: `fpr-r01, fpr-r02`.",
                "",
                "Majority labels can support a future external-label statement only for the supplied reviewers and the selected rows.",
            ]
        ),
        encoding="utf-8",
    )


def write_reviewer_file(paper: Path, reviewer_id: str = "fpr-r01") -> None:
    review_dir = paper / "build" / release_check.C14_REVIEW_DIR
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / f"false_promotion_external_review_{reviewer_id}.csv").write_text(
        "reviewer,source_row_id\n",
        encoding="utf-8",
    )


def write_label_dependent_outputs(paper: Path) -> None:
    build_dir = paper / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    for filename in release_check.C14_LABEL_DEPENDENT_OUTPUTS:
        (build_dir / filename).write_text("placeholder\n", encoding="utf-8")


def write_c14_dispatch_artifacts(paper: Path) -> tuple[str, str]:
    build_dir = paper / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    review_zip = paper / release_check.C14_REVIEW_BUNDLE_ZIP
    post_label_zip = paper / release_check.C14_POST_LABEL_KEY_ZIP
    review_zip.write_bytes(b"review bundle bytes\n")
    post_label_zip.write_bytes(b"post-label key bytes\n")
    review_sha = release_check.sha256_file(review_zip)
    post_label_sha = release_check.sha256_file(post_label_zip)
    review_zip.with_name(f"{review_zip.name}.sha256").write_text(
        f"{review_sha}  {review_zip.name}\n",
        encoding="utf-8",
    )
    post_label_zip.with_name(f"{post_label_zip.name}.sha256").write_text(
        f"{post_label_sha}  {post_label_zip.name}\n",
        encoding="utf-8",
    )
    return review_sha, post_label_sha


def write_c14_dispatch_note(repo_root: Path, review_sha: str, post_label_sha: str) -> None:
    path = repo_root / release_check.C14_DISPATCH_NOTE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# C14 external-review dispatch note",
                "",
                "This dispatch note is an internal aid.",
                "",
                "- Packet status: `prepared_no_reviewer_csvs`",
                "- Reviewer count: `0`",
                "- Allowed claim scope: `packet_ready_only`",
                "",
                "Send each independent reviewer exactly these two files:",
                "",
                "Current review bundle SHA-256:",
                review_sha,
                "",
                "Do not send these files before that reviewer's labels and declaration are final:",
                "",
                "Current post-label key SHA-256, for maintainer verification only:",
                post_label_sha,
                "",
                "python -X utf8 scripts\\aggregate_false_promotion_external_review.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_mofit_gate_status(
    paper: Path,
    row_updates: dict[str, dict[str, str]] | None = None,
    omit_gate: str | None = None,
) -> None:
    path = paper / release_check.MOFIT_GATE_STATUS
    path.parent.mkdir(parents=True, exist_ok=True)
    (paper / release_check.MOFIT_SCORE_METRICS).write_text(
        json.dumps(
            {
                "best": {
                    "auc": 0.941948,
                    "best_asr": 0.883,
                    "tpr_at_1fpr": 0.488,
                    "tpr_at_01fpr": 0.324,
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    rows = [
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "target_identity",
            "status": "Partial",
            "observed_surface": "Public score-file headers reference the COCO target by local checkpoint path.",
            "first_blocker": "No immutable public checkpoint identity or checkpoint hash.",
            "allowed_claim": "support-only public score-surface replay only",
            "forbidden_claim": "admitted evidence; N50 denominator; second public asset; compute release",
        },
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "split_identity",
            "status": "Partial",
            "observed_surface": "Public score files expose train/test rows.",
            "first_blocker": "Score rows do not embed public row IDs.",
            "allowed_claim": "support-only caption-order anchor",
            "forbidden_claim": "manifest-certified row binding",
        },
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "score_or_response_coverage",
            "status": "Partial",
            "observed_surface": "Four compact public text files expose score-like rows.",
            "first_blocker": "Rows are numeric arrays without explicit row IDs.",
            "allowed_claim": "support-only public score-file replay",
            "forbidden_claim": "row-bound admitted score packet",
        },
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "metric_provenance",
            "status": "Partial",
            "observed_surface": "DiffAudit replay mirrors public evaluation script and obtains AUC 0.941948, ASR 0.883, TPR@1%FPR 0.488, and TPR@0.1%FPR 0.324.",
            "first_blocker": "Official metric JSON and verifier packet were not observed.",
            "allowed_claim": "support-only DiffAudit-side metric replay from public text files",
            "forbidden_claim": "official upstream metric packet",
        },
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "consumer_boundary",
            "status": "Fail",
            "observed_surface": "Replay outputs are useful for paper-side audit inspection.",
            "first_blocker": "Consumer lacks immutable target identity and certified row binding.",
            "allowed_claim": "support-only evidence for claim-boundary discussion",
            "forbidden_claim": "consumer-admitted audit row",
        },
        {
            "surface": release_check.MOFIT_GATE_SURFACE,
            "gate": "surface_delta",
            "status": "Fail",
            "observed_surface": "The current check is one COCO public score-file surface.",
            "first_blocker": "No non-adjacent second response or score asset is present.",
            "allowed_claim": "support-only single public score-surface lead",
            "forbidden_claim": "completed second independent public asset",
        },
    ]
    if row_updates:
        for row in rows:
            row.update(row_updates.get(row["gate"], {}))
    if omit_gate:
        rows = [row for row in rows if row["gate"] != omit_gate]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.MOFIT_GATE_STATUS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_stl10_route_summary(
    paper: Path,
    row_updates: dict[str, dict[str, str]] | None = None,
    omit_setting: str | None = None,
) -> None:
    path = paper / release_check.STL10_ROUTE_SUMMARY
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("strict-300k", "SecMI", "1", "0.5035539034733632", "0.5040500164031982", "0.010700000450015068"),
        ("strict-300k", "PIA", "1", "0.5084503898567155", "0.5068874955177307", "0.01205000001937151"),
        ("strict-300k", "ReDiffuse", "10", "0.5048453949019043", "0.5049625039100647", "0.01054999977350235"),
        ("strict-300k", "ReDiffuse", "2", "0.5025378516572625", "0.5029625296592712", "0.011075000278651714"),
        ("strict-500k", "SecMI", "1", "0.5111869032879086", "0.5088499784469604", "0.009875000454485416"),
        ("strict-500k", "PIA", "1", "0.5140272781590328", "0.5111500024795532", "0.012400000356137753"),
        ("strict-500k", "ReDiffuse", "10", "0.5106860568790765", "0.5085124969482422", "0.011549999937415123"),
        ("strict-500k", "ReDiffuse", "2", "0.5073744603621688", "0.5060250163078308", "0.01145000010728836"),
        ("overfit-m1000-cont20k", "SecMI", "1", "0.9987007526319299", "0.9987499713897705", "1.0"),
        ("overfit-m1000-cont20k", "PIA", "1", "0.9987499713897705", "1.0", "1.0"),
        ("overfit-m1000-cont20k", "ReDiffuse", "10", "1.0", "1.0", "1.0"),
        ("overfit-m1000-cont20k", "ReDiffuse", "2", "1.0", "1.0", "1.0"),
    ]
    payload = []
    for setting, attacker, average, auc, asr, tpr in rows:
        if setting == omit_setting:
            continue
        strict = setting.startswith("strict-")
        row = {
            "route": "stl10-ddim-rediffuse",
            "setting": setting,
            "surface": "strict 50k/50k STL-10 DDIM reproduction" if strict else "fixed-subset m1000/n1000 overfit sanity",
            "attacker": attacker,
            "average": average,
            "auc": auc,
            "asr": asr,
            "tpr_at_1pct_fpr": tpr,
            "claim_role": "bounded_negative" if strict else "support_only_memorization_sanity",
            "first_blocker": (
                "strict 300K/500K aggregate metrics are random-level"
                if strict
                else "target, split, and training surface are intentionally changed"
            ),
            "allowed_claim": (
                "strict STL-10 300K/500K route remained random-level in the retained aggregate CSV"
                if strict
                else "fixed-subset overfit detects memorization under an intentionally changed 1000/1000 setting"
            ),
            "forbidden_claim": (
                "general ReDiffuse refutation; admitted row; second public asset; strict reproduction success"
                if strict
                else "strict STL-10 reproduction success; admitted row; second public asset; field-level method validity"
            ),
            "evidence_source": (
                "Download/shared/supplementary/collaborator-ddim-stl10-20260527/code/result.csv"
                if strict
                else "Download/shared/supplementary/collaborator-ddim-stl10-20260527/code/result_overfit_m1000_cont20k.csv"
            ),
        }
        if row_updates:
            row.update(row_updates.get(setting, {}))
            row.update(row_updates.get(f"{setting}:{attacker}:{average}", {}))
        payload.append(row)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.STL10_ROUTE_SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(payload)


def write_report_correctness_fault_matrix(
    paper: Path,
    rcf010_updates: dict[str, str] | None = None,
    omit_rcf010: bool = False,
    omit_prefix: str | None = None,
) -> None:
    path = paper / release_check.REPORT_CORRECTNESS_FAULT_MATRIX
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "case_id": "RCF-001",
            "fault_class": "current admitted bundle",
            "checked_surface": "risk card renderer",
            "expected": "accept",
            "observed": "accepted",
            "passed": "1",
            "evidence": "rendered 26 markdown lines",
        },
        {
            "case_id": "RCF-002",
            "fault_class": "candidate row promoted into report card",
            "checked_surface": "risk card renderer",
            "expected": "reject",
            "observed": "rejected",
            "passed": "1",
            "evidence": "risk card refuses non-admitted row",
        },
        {
            "case_id": "RCF-003",
            "fault_class": "finite-tail denominator removed",
            "checked_surface": "risk card renderer",
            "expected": "reject",
            "observed": "rejected",
            "passed": "1",
            "evidence": "missing nonmember denominator",
        },
        {
            "case_id": "RCF-004",
            "fault_class": "private source path injected",
            "checked_surface": "risk card renderer",
            "expected": "reject",
            "observed": "rejected",
            "passed": "1",
            "evidence": "contains private surface",
        },
        {
            "case_id": "RCF-005",
            "fault_class": "row-count drift",
            "checked_surface": "risk card renderer",
            "expected": "reject",
            "observed": "rejected",
            "passed": "1",
            "evidence": "row_count drift",
        },
        {
            "case_id": "RCF-006",
            "fault_class": "direct H2 promotion language",
            "checked_surface": "direct phrase scan",
            "expected": "flag",
            "observed": "flagged",
            "passed": "1",
            "evidence": "H2 described as admitted/reportable",
        },
        {
            "case_id": "RCF-007",
            "fault_class": "direct Tracing Roots promotion language",
            "checked_surface": "direct phrase scan",
            "expected": "flag",
            "observed": "flagged",
            "passed": "1",
            "evidence": "Tracing Roots described as admitted/reportable",
        },
        {
            "case_id": "RCF-008",
            "fault_class": "negated H2 boundary language",
            "checked_surface": "direct phrase scan",
            "expected": "clean",
            "observed": "clean",
            "passed": "1",
            "evidence": "no candidate-promotion hit",
        },
        {
            "case_id": "RCF-009",
            "fault_class": "generated current risk card language",
            "checked_surface": "direct phrase scan",
            "expected": "clean",
            "observed": "clean",
            "passed": "1",
            "evidence": "no candidate-promotion hit",
        },
        {
            "case_id": "RCF-010",
            "fault_class": "metadata drift promoted to release language",
            "checked_surface": "direct phrase scan",
            "expected": "flag",
            "observed": "flagged",
            "passed": "1",
            "evidence": "metadata-only surface described as admission/release: arXiv DOI metadata and a live GitHub repository prove compute release",
        },
    ]
    rows.extend(
        {
            "case_id": f"RCF-CAND-{index:03d}",
            "fault_class": "candidate/support promotion mutation",
            "checked_surface": "direct phrase scan",
            "expected": "flag",
            "observed": "flagged",
            "passed": "1",
            "evidence": "candidate/support subject described as admitted/reportable",
        }
        for index in range(1, 9)
    )
    rows.extend(
        {
            "case_id": f"RCF-META-{index:03d}",
            "fault_class": "metadata-only promotion mutation",
            "checked_surface": "direct phrase scan",
            "expected": "flag",
            "observed": "flagged",
            "passed": "1",
            "evidence": "metadata-only surface described as admission/release",
        }
        for index in range(1, 7)
    )
    rows.extend(
        {
            "case_id": f"RCF-CLEAN-{index:03d}",
            "fault_class": "clean boundary phrase control",
            "checked_surface": "direct phrase scan",
            "expected": "clean",
            "observed": "clean",
            "passed": "1",
            "evidence": "no candidate-promotion hit",
        }
        for index in range(1, 5)
    )
    if rcf010_updates:
        for row in rows:
            if row["case_id"] == "RCF-010":
                row.update(rcf010_updates)
    if omit_rcf010:
        rows = [row for row in rows if row["case_id"] != "RCF-010"]
    if omit_prefix:
        rows = [row for row in rows if not row["case_id"].startswith(omit_prefix)]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.REPORT_CORRECTNESS_FAULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_manuscript_claim_audit_fixture(
    paper: Path,
    row_updates: dict[str, dict[str, str]] | None = None,
    manuscript_text: str | None = None,
) -> None:
    data = paper / "data"
    data.mkdir(parents=True, exist_ok=True)
    with (data / "admitted_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["replay_tier"])
        writer.writeheader()
        writer.writerows(
            [
                {"replay_tier": "row-score-replay"},
                {"replay_tier": "row-score-replay"},
                {"replay_tier": "target-score-replay"},
                {"replay_tier": "source-documented-point-estimate"},
                {"replay_tier": "source-documented-point-estimate"},
            ]
        )
    with (data / "h2_output_cloud_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "label", "auc"])
        writer.writeheader()
        writer.writerow({"source": "h2-main", "label": "output-cloud 512/512", "auc": "0.961529"})
    (data / "mofit_public_score_metrics.json").write_text(
        json.dumps(
            {
                "best": {
                    "auc": 0.941948,
                    "best_asr": 0.883,
                    "tpr_at_1fpr": 0.488,
                    "tpr_at_01fpr": 0.324,
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with (data / "false_promotion_rule_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["weak_rule", "plot_label", "would_promote_rows", "selected_row_count", "boundary_note"],
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "weak_rule": "code_availability_would_promote",
                    "plot_label": "code",
                    "would_promote_rows": "12",
                    "selected_row_count": "13",
                    "boundary_note": "weak-rule count over selected stress rows; not denominator or prevalence evidence",
                },
                {
                    "weak_rule": "paper_claim_artifact_link_would_promote",
                    "plot_label": "paper-link",
                    "would_promote_rows": "12",
                    "selected_row_count": "13",
                    "boundary_note": "weak-rule count over selected stress rows; not denominator or prevalence evidence",
                },
            ]
        )
    write_false_promotion_gate_summary(paper)
    write_report_correctness_fault_matrix(paper)
    if manuscript_text is None:
        manuscript_text = """
        three replay-backed rows reportable under bounded wording, two source-documented point rows.
        one repeated-response candidate with AUC 0.9615.
        AUC 0.941948, ASR 0.883, TPR@1\\%FPR 0.488, and TPR@0.1\\%FPR 0.324.
        weak public-surface rules would select 12/13 rows by code and paper-artifact links.
        all selected rows are non-Pass at the score/response and consumer-boundary gates.
        selected renderer/phrase-guard regression cases.
        """
    (paper / "main.tex").write_text(manuscript_text, encoding="utf-8")
    rows = [
        {
            "anchor_id": "MCA-001",
            "paper_section": "abstract/contributions",
            "manuscript_required_text": "three replay-backed rows reportable under bounded wording, two source-documented point rows",
            "source_paths": "data/admitted_rows.csv",
            "source_values": "total=5; replay_admitted=3; source_point=2",
            "audit_status": "pass",
            "boundary_note": "composition anchor only; point estimates remain point-worded and are not replay-admitted",
        },
        {
            "anchor_id": "MCA-002",
            "paper_section": "abstract/H2",
            "manuscript_required_text": "one repeated-response candidate with AUC 0.9615",
            "source_paths": "data/h2_output_cloud_rows.csv",
            "source_values": "h2_candidate_auc=0.961529",
            "audit_status": "pass",
            "boundary_note": "metric anchor only; H2 remains candidate-only and non-admitted",
        },
        {
            "anchor_id": "MCA-003",
            "paper_section": "MoFit",
            "manuscript_required_text": "AUC 0.941948, ASR 0.883, TPR@1%FPR 0.488, and TPR@0.1%FPR 0.324",
            "source_paths": "data/mofit_public_score_metrics.json",
            "source_values": "auc=0.941948; asr=0.883; tpr1=0.488; tpr01=0.324",
            "audit_status": "pass",
            "boundary_note": "metric anchor only; MoFit remains support-only with all gates non-Pass",
        },
        {
            "anchor_id": "MCA-004",
            "paper_section": "abstract/C14",
            "manuscript_required_text": "weak public-surface rules would select 12/13 rows by code and paper-artifact links",
            "source_paths": "data/false_promotion_rule_summary.csv",
            "source_values": "code=12; paper_link=12; selected=13",
            "audit_status": "pass",
            "boundary_note": "author-keyed preparation packet only; not prevalence, reliability, or adjudication evidence",
        },
        {
            "anchor_id": "MCA-005",
            "paper_section": "C14",
            "manuscript_required_text": "all selected rows are non-Pass at the score/response and consumer-boundary gates",
            "source_paths": "data/false_promotion_gate_summary.csv",
            "source_values": "score_or_response_pass=0; consumer_boundary_pass=0",
            "audit_status": "pass",
            "boundary_note": "author-keyed gate-count anchor only; no external reviewer labels",
        },
            {
                "anchor_id": "MCA-006",
                "paper_section": "contributions/report-correctness",
                "manuscript_required_text": "selected renderer/phrase-guard regression cases",
                "source_paths": "data/report_correctness_fault_injection.csv",
                "source_values": "cases=28; passed=28",
            "audit_status": "pass",
            "boundary_note": "fault-injection sanity cases for release wording, not a deployed system effectiveness claim",
        },
    ]
    if row_updates:
        for row in rows:
            row.update(row_updates.get(row["anchor_id"], {}))
    with (data / "manuscript_claim_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.MANUSCRIPT_CLAIM_AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_false_promotion_gate_summary(
    paper: Path,
    row_updates: dict[tuple[str, str], dict[str, str]] | None = None,
    omit_key: tuple[str, str] | None = None,
) -> None:
    path = paper / release_check.FALSE_PROMOTION_GATE_SUMMARY
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "gate": gate,
            "outcome": outcome,
            "count": str(count),
            "selected_row_count": "13",
            "boundary_note": "author-keyed C14 gate count over selected stress rows; not external reliability or prevalence evidence",
        }
        for (gate, outcome), count in release_check.FALSE_PROMOTION_REQUIRED_GATE_COUNTS.items()
    ]
    if row_updates:
        for row in rows:
            row.update(row_updates.get((row["gate"], row["outcome"]), {}))
    if omit_key:
        rows = [row for row in rows if (row["gate"], row["outcome"]) != omit_key]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.FALSE_PROMOTION_GATE_SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_false_promotion_author_gate_matrix(
    paper: Path,
    row_updates: dict[int, dict[str, str]] | None = None,
) -> None:
    path = paper / release_check.FALSE_PROMOTION_AUTHOR_GATE_MATRIX
    path.parent.mkdir(parents=True, exist_ok=True)
    outcomes_by_gate: dict[str, list[str]] = {}
    for gate in release_check.FALSE_PROMOTION_AUTHOR_GATES:
        values: list[str] = []
        for outcome in release_check.FALSE_PROMOTION_GATE_OUTCOMES:
            values.extend([outcome] * release_check.FALSE_PROMOTION_REQUIRED_GATE_COUNTS[(gate, outcome)])
        assert len(values) == release_check.FALSE_PROMOTION_EXPECTED_SELECTED_ROW_COUNT
        outcomes_by_gate[gate] = values

    rows = []
    for index in range(release_check.FALSE_PROMOTION_EXPECTED_SELECTED_ROW_COUNT):
        row = {"review_id": f"FPR-TEST-{index + 1:03d}"}
        for gate in release_check.FALSE_PROMOTION_AUTHOR_GATES:
            row[gate] = outcomes_by_gate[gate][index]
        if row_updates:
            row.update(row_updates.get(index, {}))
        rows.append(row)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["review_id", *release_check.FALSE_PROMOTION_AUTHOR_GATES])
        writer.writeheader()
        writer.writerows(rows)


def write_manuscript(paper: Path, text: str | None = None) -> None:
    if text is None:
        text = """
        We apply the instrument to a set of frozen boundary cases as protocol checks.
        The selected rows validate fixed claim wordings. Their role is boundary checking; frequency estimation requires separate corpus sampling.
        This release-scope consistency check covers selected boundary cases.
        General gate sufficiency and independent-coding reliability require broader corpora and independent labels.
        The current status is \\texttt{n\\_reviewers=0},
        \\texttt{packet\\_ready\\_only}, and pre-label stress-control.
        Reviewer agreement and prevalence require independent labels and a larger sampled corpus.
        MoFit COCO is support-only: all six gates remain non-Pass.
        C14, N50-denominator, admitted-evidence, second-public-asset,
        and compute-release claims stay outside the packet.
        The current MoFit packet supplies stress coverage.
        The fixed-subset overfit setting is support-only; strict STL-10 reproduction success is outside that setting.
        In the current packet, the provenance table is a local packet-identity snapshot;
        dirty tree state and local paths identify the review snapshot, and the
        public-release provenance gate remains unresolved.
        """
    (paper / "main.tex").write_text(text, encoding="utf-8")


def current_pdf_text() -> str:
    return "\n".join(
        [
            "C14 tests whether weak public-surface rules over-promote rows before reviewer labels.",
            "The packet contains thirteen selected no-download E2 public-surface checks.",
            "Table V summarizes the weak rules and gate blockers.",
            "Pre-label stress-control.",
            "paper-artifact-link in 12 rows.",
            "The current status is n_reviewers=0.",
            "n_reviewers=0.",
            "packet_ready_only.",
            "Each row records a weak-admission trigger and a first-blocker label.",
            "code in 12.",
            "metric/split in 9.",
            "artifact in 7.",
            "Every selected row is non-Pass at the score/response and consumer-boundary gates.",
            "Target and metric gates remain author-keyed non-Pass.",
            "28-case release-wording regression matrix.",
            "release QA for wording boundaries.",
            "Report drift, compute-release gate validity, and external-use estimates are unexamined.",
            "reviewer agreement and prevalence require independent labels and a larger sampled corpus.",
            "C1-C15 claim state.",
            "C1-C15 claim-gate recode template.",
            "maps each headline claim.",
            "availability tier.",
            "Public Score-File Boundary: MoFit.",
            "C14, N50-denominator, admitted-evidence, second-public-asset, and compute-release claims stay outside the packet.",
        ]
    )


def write_review_snapshot_fixture(paper: Path, repo_root: Path, manifest: dict[str, object]) -> None:
    (paper / "data").mkdir(parents=True, exist_ok=True)
    (paper / "scripts").mkdir(parents=True, exist_ok=True)
    (paper / "data" / "public.csv").write_text("id,value\nr1,1\n", encoding="utf-8")
    (paper / "README.md").write_text("review packet\n", encoding="utf-8")
    (paper / "paper.pdf").write_text("pdf bytes\n", encoding="utf-8")
    (paper / "scripts" / "build_paper_assets.py").write_text("print('build')\n", encoding="utf-8")
    (paper / "data" / "claim_trace.csv").write_text("claim_id\nC1\n", encoding="utf-8")
    (paper / "data" / "source_provenance.csv").write_text(
        "provenance_id,repo_tree_state\np1,dirty\n",
        encoding="utf-8",
    )
    (paper / "asset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    common = {
        "schema_version": "review-snapshot-v1",
        "snapshot_kind": "local_review_snapshot",
        "scope": "paper_release_packet_inputs_only",
        "generated_at_utc": "2026-06-08T00:00:00Z",
        "repo_head": release_check.run_text(["git", "rev-parse", "HEAD"], repo_root).strip(),
        "repo_tree_state": "dirty",
        "generator_command": "python -X utf8 papers/diffaudit-evidence-paper/scripts/build_paper_assets.py",
        "generator_script_sha256": release_check.sha256_file(paper / "scripts" / "build_paper_assets.py"),
        "release_checker_script_sha256": release_check.sha256_file(repo_root / "scripts" / "check_paper_release_packet.py"),
        "asset_manifest_sha256": release_check.sha256_file(paper / "asset_manifest.json"),
        "source_provenance_sha256": release_check.sha256_file(paper / "data" / "source_provenance.csv"),
        "claim_trace_sha256": release_check.sha256_file(paper / "data" / "claim_trace.csv"),
        "paper_pdf_sha256": release_check.sha256_file(paper / "paper.pdf"),
        "excluded_public_claims": (
            "dirty tree is not public provenance;"
            "candidate/support/support-only rows are not admitted evidence;"
            "permission-bound artifacts are not public replay evidence"
        ),
        "snapshot_role": "local-review-packet-identity",
        "boundary_note": "local review snapshot only; not clean public release provenance",
    }
    rows = []
    for category, rel_path in [
        ("generated", "data/public.csv"),
        ("paper_sources", "README.md"),
        ("release_file", "asset_manifest.json"),
        ("release_file", "paper.pdf"),
    ]:
        source = paper / rel_path
        rows.append(
            {
                **common,
                "manifest_category": category,
                "relative_path": rel_path,
                "exists": "true",
                "git_status": "not-reported-by-git-status",
                "size_bytes": str(source.stat().st_size),
                "sha256": release_check.sha256_file(source),
            }
        )
    with (paper / release_check.REVIEW_SNAPSHOT_MANIFEST).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=release_check.REVIEW_SNAPSHOT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class C14ReleaseStatusTests(unittest.TestCase):
    def test_dispatch_note_passes_with_current_zip_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            paper = repo_root / "papers" / "diffaudit-evidence-paper"
            review_sha, post_label_sha = write_c14_dispatch_artifacts(paper)
            write_c14_dispatch_note(repo_root, review_sha, post_label_sha)
            errors: list[str] = []

            release_check.validate_c14_dispatch_note(paper, repo_root, errors)

        self.assertEqual(errors, [])

    def test_dispatch_note_rejects_stale_post_label_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            paper = repo_root / "papers" / "diffaudit-evidence-paper"
            review_sha, _post_label_sha = write_c14_dispatch_artifacts(paper)
            stale_post_label_sha = "c53727db85e840a9312cec71fb2c0b13f3aef11373d978e78c58801763c6b241"
            write_c14_dispatch_note(repo_root, review_sha, stale_post_label_sha)
            errors: list[str] = []

            release_check.validate_c14_dispatch_note(paper, repo_root, errors)

        self.assertIn(f"{release_check.C14_DISPATCH_NOTE} missing current post-label key SHA-256", errors)
        self.assertIn(
            f"{release_check.C14_DISPATCH_NOTE} contains stale or unexpected SHA-256: {stale_post_label_sha}",
            errors,
        )

    def test_no_reviewer_status_passes_with_status_only_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_status_row(paper)
            write_no_label_markdown(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        self.assertEqual(errors, [])

    def test_no_reviewer_status_rejects_stale_label_dependent_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_status_row(paper)
            write_no_label_markdown(paper)
            for filename in release_check.C14_LABEL_DEPENDENT_OUTPUTS:
                (paper / "build" / filename).write_text("stale\n", encoding="utf-8")
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        for filename in release_check.C14_LABEL_DEPENDENT_OUTPUTS:
            with self.subTest(filename=filename):
                self.assertIn(f"C14 label-dependent output exists without reviewer CSVs: {filename}", errors)

    def test_no_reviewer_status_rejects_claim_switch_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_status_row(paper, {"reliability_claim_allowed": "1"})
            write_no_label_markdown(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        self.assertIn("C14 status must keep reliability_claim_allowed=0", errors)

    def test_reviewer_files_are_rejected_for_current_no_reviewer_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper)
            write_status_row(paper)
            write_no_label_markdown(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        self.assertIn("C14 reviewer CSVs are not allowed in the current packet_ready_only release", errors)

    def test_reviewer_present_status_is_rejected_for_current_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper)
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "min_2_external_label_aggregation_available",
                    "n_reviewers": "2",
                    "majority_resolution_status": "resolved",
                    "external_label_aggregation_available": "1",
                    "allowed_claim_scope": "external_label_aggregation_selected_13_rows_only_reliability_claim_not_allowed",
                },
            )
            write_no_label_markdown(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        self.assertIn("C14 reviewer CSVs are not allowed in the current packet_ready_only release", errors)
        self.assertIn("C14 no-reviewer status drifted for packet_label_readiness: 'review_csvs_available'", errors)

    def test_reviewer_present_status_rejects_claim_switch_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper)
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "min_2_external_label_aggregation_available",
                    "reliability_claim_allowed": "1",
                },
            )
            write_no_label_markdown(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors)

        self.assertIn("C14 status must keep reliability_claim_allowed=0", errors)

    def test_post_label_status_accepts_selected_row_external_label_aggregation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper, "fpr-r01")
            write_reviewer_file(paper, "fpr-r02")
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "min_2_external_label_aggregation_available",
                    "n_reviewers": "2",
                    "majority_resolution_status": "resolved",
                    "declaration_status": "valid_independence_attestation",
                    "external_label_aggregation_available": "1",
                    "allowed_claim_scope": "external_label_aggregation_selected_13_rows_only_reliability_claim_not_allowed",
                },
            )
            write_post_label_markdown(paper)
            write_label_dependent_outputs(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors, review_state="post-label")

        self.assertEqual(errors, [])

    def test_post_label_status_rejects_too_few_reviewers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper, "fpr-r01")
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "below_min_2",
                    "n_reviewers": "1",
                    "majority_resolution_status": "resolved",
                    "declaration_status": "valid_independence_attestation",
                    "external_label_aggregation_available": "0",
                    "allowed_claim_scope": "packet_ready_only_below_min_reviewers",
                },
            )
            write_post_label_markdown(paper)
            write_label_dependent_outputs(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors, review_state="post-label")

        self.assertIn("C14 post-label release requires n_reviewers >= min_reviewers", errors)
        self.assertIn("C14 post-label release requires external_label_aggregation_available=1", errors)

    def test_post_label_status_rejects_invalid_declarations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper, "fpr-r01")
            write_reviewer_file(paper, "fpr-r02")
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "min_2_external_label_aggregation_available",
                    "n_reviewers": "2",
                    "majority_resolution_status": "resolved",
                    "declaration_status": "missing_declaration",
                    "external_label_aggregation_available": "1",
                    "allowed_claim_scope": "external_label_aggregation_selected_13_rows_only_reliability_claim_not_allowed",
                },
            )
            write_post_label_markdown(paper)
            write_label_dependent_outputs(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors, review_state="post-label")

        self.assertIn("C14 post-label release requires valid independence declarations", errors)

    def test_post_label_status_rejects_claim_switch_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_reviewer_file(paper, "fpr-r01")
            write_reviewer_file(paper, "fpr-r02")
            write_status_row(
                paper,
                {
                    "packet_label_readiness": "review_csvs_available",
                    "reviewer_count_status": "min_2_external_label_aggregation_available",
                    "n_reviewers": "2",
                    "majority_resolution_status": "resolved",
                    "declaration_status": "valid_independence_attestation",
                    "external_label_aggregation_available": "1",
                    "completed_external_adjudication_allowed": "1",
                    "allowed_claim_scope": "external_label_aggregation_selected_13_rows_only_reliability_claim_not_allowed",
                },
            )
            write_post_label_markdown(paper)
            write_label_dependent_outputs(paper)
            errors: list[str] = []

            release_check.validate_c14_external_review_status(paper, errors, review_state="post-label")

        self.assertIn("C14 status must keep completed_external_adjudication_allowed=0", errors)


class MoFitGateStatusTests(unittest.TestCase):
    def test_mofit_gate_status_passes_for_support_only_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper)
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertEqual(errors, [])

    def test_mofit_gate_status_rejects_consumer_boundary_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"consumer_boundary": {"status": "Partial"}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit consumer_boundary status drifted: 'Partial'", errors)
        self.assertIn("MoFit consumer_boundary must remain Fail", errors)

    def test_mofit_gate_status_rejects_pass_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"surface_delta": {"status": "Pass"}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit surface_delta row must not be Pass", errors)
        self.assertIn("MoFit surface_delta status drifted: 'Pass'", errors)

    def test_mofit_gate_status_rejects_allowed_claim_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(
                paper,
                {"score_or_response_coverage": {"allowed_claim": "admitted N50 compute release row-bound evidence"}},
            )
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertTrue(
            any(error.startswith("MoFit score_or_response_coverage allowed_claim crosses support-only boundary") for error in errors),
            errors,
        )

    def test_mofit_gate_status_rejects_allowed_claim_without_support_only_frame(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"metric_provenance": {"allowed_claim": "usable evidence"}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit metric_provenance allowed_claim lacks support-only framing", errors)

    def test_mofit_gate_status_rejects_missing_forbidden_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"target_identity": {"forbidden_claim": "admitted evidence; N50 denominator"}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit forbidden_claims lost required boundary: compute\\s+release", errors)

    def test_mofit_gate_status_rejects_missing_gate_local_forbidden_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(
                paper,
                {"metric_provenance": {"forbidden_claim": "workspace replay metric packet"}},
            )
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit metric_provenance forbidden_claim lost gate boundary: official\\s+(?:metric|upstream)", errors)

    def test_mofit_gate_status_rejects_missing_required_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, omit_gate="surface_delta")
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("data/mofit_public_gate_status.csv must contain exactly 6 gate rows", errors)
        self.assertIn("MoFit gate status missing gates: surface_delta", errors)

    def test_mofit_gate_status_rejects_wrong_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"target_identity": {"surface": "other-surface"}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit gate row has unexpected surface: 'other-surface'", errors)

    def test_mofit_gate_status_rejects_empty_required_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(paper, {"target_identity": {"first_blocker": ""}})
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit target_identity row missing first_blocker", errors)

    def test_mofit_gate_status_rejects_metric_value_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_mofit_gate_status(
                paper,
                {"metric_provenance": {"observed_surface": "AUC 0.900000, ASR 0.883, TPR@1%FPR 0.488, and TPR@0.1%FPR 0.324."}},
            )
            errors: list[str] = []

            release_check.validate_mofit_gate_status(paper, errors)

        self.assertIn("MoFit metric_provenance observed_surface missing frozen AUC=0.941948", errors)


class ClaimTraceBoundaryTests(unittest.TestCase):
    def test_h2_claim_trace_boundaries_pass_for_current_rows(self) -> None:
        c3 = {
            "claim_id": "C3",
            "evidence_state": "candidate failed-admission stress test",
            "allowed_wording": "Same-family H2 candidate evidence only; not admitted for consumer reporting or portability by default.",
            "replay_tier": "response/feature replay from frozen aggregate artifacts",
            "first_blocker": "consumer boundary and img2img portability",
            "target_gate": "Pass",
            "split_gate": "Pass",
            "evidence_gate": "Pass",
            "metric_gate": "Pass",
            "boundary_gate": "Fail",
            "delta_gate": "Fail",
        }
        c4 = {
            "claim_id": "C4",
            "evidence_state": "same-family stability support",
            "allowed_wording": "Same-family stability evidence only; no cross-model or cross-dataset portability claim.",
            "replay_tier": "response/feature replay from frozen aggregate artifacts",
            "first_blocker": "non-adjacent model/data response asset",
            "target_gate": "Pass",
            "split_gate": "Pass",
            "evidence_gate": "Pass",
            "metric_gate": "Pass",
            "boundary_gate": "Partial",
            "delta_gate": "Fail",
        }
        errors: list[str] = []

        release_check.validate_claim_trace_gate_consistency(c3, errors)
        release_check.validate_claim_trace_gate_consistency(c4, errors)

        self.assertEqual(errors, [])

    def test_h2_claim_trace_rejects_promotion_drift(self) -> None:
        row = {
            "claim_id": "C3",
            "evidence_state": "reportable H2 row",
            "allowed_wording": "Strong H2 evidence admitted for reporting.",
            "replay_tier": "response/feature replay from frozen aggregate artifacts",
            "first_blocker": "",
            "target_gate": "Pass",
            "split_gate": "Pass",
            "evidence_gate": "Pass",
            "metric_gate": "Pass",
            "boundary_gate": "Pass",
            "delta_gate": "Pass",
        }
        errors: list[str] = []

        release_check.validate_claim_trace_gate_consistency(row, errors)

        self.assertIn("C3 H2 must remain candidate-only", errors)
        self.assertIn("C3 H2 boundary_gate must remain Fail: 'Pass'", errors)
        self.assertIn("C3 H2 delta_gate must remain Fail: 'Pass'", errors)
        self.assertIn("C3 H2 allowed_wording must not use strong-signal promotion wording", errors)


class SupportOnlyRouteProvenanceTests(unittest.TestCase):
    def support_only_provenance_rows(self) -> dict[str, dict[str, str]]:
        return {
            provenance_id: {
                "path": expected["path"],
                "source_kind": expected.get("source_kind", "internal-preflight-note"),
                "note": "; ".join(expected["required_note_tokens"]),
            }
            for provenance_id, expected in release_check.SUPPORT_ONLY_ROUTE_PROVENANCE.items()
        }

    def test_support_only_route_provenance_passes_as_c5_only_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            (paper / "data").mkdir(parents=True)
            (paper / "data" / "negative_support_rows.csv").write_text(
                "source,label,role\nrediffuse-stl10,denoising-loss scout,negative\n",
                encoding="utf-8",
            )
            trace_rows = [
                {
                    "claim_id": "C5",
                    "provenance_ids": ";".join(release_check.SUPPORT_ONLY_ROUTE_PROVENANCE),
                }
            ]
            errors: list[str] = []

            release_check.validate_support_only_route_provenance(
                paper,
                trace_rows,
                self.support_only_provenance_rows(),
                errors,
            )

        self.assertEqual(errors, [])

    def test_support_only_route_provenance_rejects_claim_or_metric_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            (paper / "data").mkdir(parents=True)
            (paper / "data" / "negative_support_rows.csv").write_text(
                "source,label,role\nSAMA,E2SCT031 support-only route,support\n",
                encoding="utf-8",
            )
            trace_rows = [
                {
                    "claim_id": "C5",
                    "provenance_ids": "miaept-tabular-public-surface-check",
                },
                {
                    "claim_id": "C14",
                    "provenance_ids": "sama-dlm-public-surface-check",
                },
            ]
            errors: list[str] = []

            release_check.validate_support_only_route_provenance(
                paper,
                trace_rows,
                self.support_only_provenance_rows(),
                errors,
            )

        self.assertIn("C5 missing support-only route provenance: sama-dlm-public-surface-check", errors)
        self.assertIn(
            "sama-dlm-public-surface-check must not be referenced by C14; support-only route checks belong only to C5",
            errors,
        )
        self.assertIn("sama-dlm-public-surface-check must not enter metric-bearing negative_support_rows.csv", errors)


class STL10RouteSummaryTests(unittest.TestCase):
    def test_stl10_route_summary_passes_for_bounded_negative_and_support_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_stl10_route_summary(paper)
            errors: list[str] = []

            release_check.validate_stl10_route_summary(paper, errors)

        self.assertEqual(errors, [])

    def test_stl10_route_summary_rejects_allowed_claim_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_stl10_route_summary(
                paper,
                {
                    "overfit-m1000-cont20k": {
                        "allowed_claim": "admitted second public asset with strict STL-10 reproduction success"
                    }
                },
            )
            errors: list[str] = []

            release_check.validate_stl10_route_summary(paper, errors)

        self.assertTrue(
            any(error.startswith("STL-10 overfit-m1000-cont20k allowed_claim crosses support boundary") for error in errors),
            errors,
        )
        self.assertIn(
            "STL-10 overfit-m1000-cont20k allowed_claim lost required boundary: fixed[-\\s]?subset\\s+overfit\\s+detects\\s+memorization",
            errors,
        )

    def test_stl10_route_summary_rejects_strict_route_metric_or_role_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_stl10_route_summary(
                paper,
                {
                    "strict-500k:PIA:1": {
                        "auc": "0.81",
                        "claim_role": "admitted",
                    }
                },
            )
            errors: list[str] = []

            release_check.validate_stl10_route_summary(paper, errors)

        self.assertIn("STL-10 strict-500k claim_role drifted: 'admitted'", errors)
        self.assertIn("STL-10 strict-500k strict route no longer random-level: 0.81", errors)

    def test_stl10_route_summary_rejects_missing_frozen_setting(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_stl10_route_summary(paper, omit_setting="strict-300k")
            errors: list[str] = []

            release_check.validate_stl10_route_summary(paper, errors)

        self.assertIn(f"{release_check.STL10_ROUTE_SUMMARY} must contain the frozen strict/overfit rows", errors)
        self.assertIn("STL-10 strict-300k row count drifted: 0", errors)


class ReportCorrectnessFaultMatrixTests(unittest.TestCase):
    def test_report_correctness_fault_matrix_passes_with_metadata_drift_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper)
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertEqual(errors, [])

    def test_report_correctness_fault_matrix_rejects_missing_rcf010(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper, omit_rcf010=True)
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn("report-correctness fault matrix lost RCF-010 metadata-drift guard", errors)

    def test_report_correctness_fault_matrix_rejects_extra_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper)
            path = paper / release_check.REPORT_CORRECTNESS_FAULT_MATRIX
            with path.open("a", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=release_check.REPORT_CORRECTNESS_FAULT_FIELDS)
                writer.writerow(
                    {
                        "case_id": "RCF-EXTRA-001",
                        "fault_class": "unexpected new row",
                        "checked_surface": "direct phrase scan",
                        "expected": "flag",
                        "observed": "flagged",
                        "passed": "1",
                        "evidence": "unexpected row should force wording and count review",
                    }
                )
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn("data/report_correctness_fault_injection.csv row count drifted: 29 != 28", errors)

    def test_report_correctness_fault_matrix_rejects_clean_rcf010(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(
                paper,
                {
                    "observed": "clean",
                    "evidence": "no candidate-promotion hit",
                },
            )
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn("RCF-010 observed drifted: 'clean'", errors)
        self.assertIn(
            "RCF-010 evidence lost required boundary: metadata-only\\s+surface\\s+described\\s+as\\s+admission/release",
            errors,
        )
        self.assertIn("RCF-010 evidence lost required boundary: compute\\s+release", errors)

    def test_report_correctness_fault_matrix_rejects_missing_candidate_grid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper, omit_prefix="RCF-CAND-")
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn(
            "report-correctness fault matrix lost candidate/support promotion mutation rows (RCF-CAND-)",
            errors,
        )

    def test_report_correctness_fault_matrix_rejects_missing_metadata_grid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper, omit_prefix="RCF-META-")
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn(
            "report-correctness fault matrix lost metadata-only promotion mutation rows (RCF-META-)",
            errors,
        )

    def test_report_correctness_fault_matrix_rejects_missing_clean_grid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_report_correctness_fault_matrix(paper, omit_prefix="RCF-CLEAN-")
            errors: list[str] = []

            release_check.validate_report_correctness_fault_matrix(paper, errors)

        self.assertIn(
            "report-correctness fault matrix lost clean boundary phrase control rows (RCF-CLEAN-)",
            errors,
        )


class ManuscriptClaimAuditTests(unittest.TestCase):
    def test_manuscript_claim_audit_passes_for_current_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript_claim_audit_fixture(paper)
            errors: list[str] = []

            release_check.validate_manuscript_claim_audit(paper, errors)

        self.assertEqual(errors, [])

    def test_manuscript_claim_audit_rejects_missing_text_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript_claim_audit_fixture(
                paper,
                manuscript_text="""
                three replay-backed rows reportable under bounded wording, two source-documented point rows.
                one repeated-response candidate with AUC 0.9615.
                weak public-surface rules would select 12/13 rows by code and paper-artifact links.
                all selected rows are non-Pass at the score/response and consumer-boundary gates.
                selected renderer/phrase-guard regression cases.
                """,
            )
            errors: list[str] = []

            release_check.validate_manuscript_claim_audit(paper, errors)

        self.assertIn("MCA-003 manuscript_required_text not found in main.tex", errors)

    def test_manuscript_claim_audit_rejects_source_value_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript_claim_audit_fixture(
                paper,
                {"MCA-004": {"source_values": "code=11; paper_link=12; selected=13"}},
            )
            errors: list[str] = []

            release_check.validate_manuscript_claim_audit(paper, errors)

        self.assertIn("MCA-004 source_values drifted: 'code=11; paper_link=12; selected=13'", errors)


class CitationContextAuditTests(unittest.TestCase):
    def write_context_fixture(
        self,
        paper: Path,
        *,
        main_text: str | None = None,
        row_updates: dict[str, dict[str, str]] | None = None,
    ) -> None:
        data = paper / "data"
        data.mkdir(parents=True, exist_ok=True)
        if main_text is None:
            main_text = "\n".join(
                [
                    "A claim uses prior work~\\cite{a2026,b2026}.",
                    "MoFit method identity~\\cite{jeon2026mofit}.",
                    "Tracing feature-packet route~\\cite{tracingroots2025}.",
                ]
            )
        (paper / "main.tex").write_text(main_text, encoding="utf-8")
        (paper / "refs.bib").write_text(
            "\n".join(
                [
                    "@article{a2026, author={A}, title={A Ref}, year={2026}, doi={10.1000/a}}",
                    "@article{b2026, author={B}, title={B Ref}, year={2026}, doi={10.1000/b}}",
                    "@article{jeon2026mofit, author={J}, title={MoFit}, year={2026}, doi={10.1000/mofit}}",
                    "@article{tracingroots2025, author={T}, title={Tracing}, year={2025}, doi={10.1000/tracing}}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        with (data / "reference_integrity_audit.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=release_check.REFERENCE_INTEGRITY_FIELDS)
            writer.writeheader()
            for key in ("a2026", "b2026", "jeon2026mofit", "tracingroots2025"):
                writer.writerow(
                    {
                        "bib_key": key,
                        "entry_type": "article",
                        "title": key,
                        "year": "2026",
                        "identifier_kind": "doi_handle",
                        "identifier_value": f"10.1000/{key}",
                        "verification_url": f"https://doi.org/api/handles/10.1000/{key}",
                        "http_status": "200",
                        "verification_status": "verified",
                        "verification_note": "verified: DOI handle exists",
                        "metadata_status": "verified",
                        "metadata_source": "doi_csl_json",
                        "metadata_note": "verified: title/year match",
                        "checked_at_utc": "2026-06-09T00:00:00Z",
                    }
                )
        rows = [
            {
                "citation_id": "CCA-001",
                "main_tex_line": "1",
                "paper_section": "fixture",
                "cited_keys": "a2026;b2026",
                "claim_text_anchor": "A claim uses prior work",
                "expected_source_support": "Fixture background support.",
                "manuscript_claim_role": "background",
                "source_content_status": "metadata_verified; full-text L3 pending",
                "audit_status": "pass_context_inventory",
                "boundary_note": "Background support only.",
            },
            {
                "citation_id": "CCA-002",
                "main_tex_line": "2",
                "paper_section": "fixture",
                "cited_keys": "jeon2026mofit",
                "claim_text_anchor": "MoFit method identity",
                "expected_source_support": "Fixture MoFit support.",
                "manuscript_claim_role": "support-only-boundary-background",
                "source_content_status": "metadata_verified; full-text L3 pending",
                "audit_status": "pass_context_inventory",
                "boundary_note": "MoFit remains support-only.",
            },
            {
                "citation_id": "CCA-003",
                "main_tex_line": "3",
                "paper_section": "fixture",
                "cited_keys": "tracingroots2025",
                "claim_text_anchor": "Tracing feature-packet route",
                "expected_source_support": "Fixture Tracing support.",
                "manuscript_claim_role": "route-source-label",
                "source_content_status": "metadata_verified; full-text L3 pending",
                "audit_status": "pass_context_inventory",
                "boundary_note": "Tracing Roots remains feature-packet support.",
            },
        ]
        if row_updates:
            for row in rows:
                row.update(row_updates.get(row["citation_id"], {}))
        with (data / "citation_context_audit.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=release_check.CITATION_CONTEXT_AUDIT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_citation_context_audit_passes_for_current_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_context_fixture(paper)
            errors: list[str] = []

            release_check.validate_citation_context_audit(paper, errors)

        self.assertEqual(errors, [])

    def test_citation_context_audit_rejects_cited_key_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_context_fixture(
                paper,
                main_text="\n".join(
                    [
                        "A claim uses prior work~\\cite{a2026}.",
                        "MoFit method identity~\\cite{jeon2026mofit}.",
                        "Tracing feature-packet route~\\cite{tracingroots2025}.",
                    ]
                ),
            )
            errors: list[str] = []

            release_check.validate_citation_context_audit(paper, errors)

        self.assertIn("CCA-001 cited_keys drifted: 'a2026;b2026' != 'a2026'", errors)

    def test_citation_context_audit_rejects_full_text_verification_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_context_fixture(paper, row_updates={"CCA-001": {"source_content_status": "full-text verified"}})
            errors: list[str] = []

            release_check.validate_citation_context_audit(paper, errors)

        self.assertIn("CCA-001 source_content_status must remain metadata_verified with full-text L3 pending", errors)


class PdfValidationTests(unittest.TestCase):
    def test_validate_pdf_accepts_relative_paper_path_with_current_c14_phrases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paper = root / "paper"
            (paper / "build").mkdir(parents=True)
            (paper / "paper.pdf").write_bytes(b"same pdf bytes")
            (paper / "build" / "main.pdf").write_bytes(b"same pdf bytes")

            def fake_run_text(cmd: list[str], cwd: Path) -> str:
                self.assertTrue(Path(cmd[1]).is_absolute())
                if cmd[0] == "pdfinfo":
                    return "Pages:           10\nPage size:       612 x 792 pts (letter)\n"
                if cmd[0] == "pdffonts":
                    return "name type emb sub uni object ID\nTimes Type 1 yes yes yes 1 0\n"
                if cmd[0] == "pdftotext":
                    return current_pdf_text()
                raise AssertionError(f"unexpected command: {cmd}")

            old_cwd = Path.cwd()
            os.chdir(root)
            try:
                errors: list[str] = []
                with patch.object(release_check, "run_text", side_effect=fake_run_text):
                    release_check.validate_pdf(Path("paper"), errors)
            finally:
                os.chdir(old_cwd)

        self.assertEqual(errors, [])

    def test_validate_pdf_rejects_stale_c14_gate_failure_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            (paper / "build").mkdir(parents=True)
            (paper / "paper.pdf").write_bytes(b"same pdf bytes")
            (paper / "build" / "main.pdf").write_bytes(b"same pdf bytes")
            stale_text = current_pdf_text().replace(
                "Every selected row is non-Pass at the score/response and consumer-boundary gates.",
                "score/response and consumer-boundary gates fail for all 13.",
            )

            def fake_run_text(cmd: list[str], cwd: Path) -> str:
                if cmd[0] == "pdfinfo":
                    return "Pages:           10\nPage size:       612 x 792 pts (letter)\n"
                if cmd[0] == "pdffonts":
                    return "name type emb sub uni object ID\nTimes Type 1 yes yes yes 1 0\n"
                if cmd[0] == "pdftotext":
                    return stale_text
                raise AssertionError(f"unexpected command: {cmd}")

            errors: list[str] = []
            with patch.object(release_check, "run_text", side_effect=fake_run_text):
                release_check.validate_pdf(paper, errors)

        self.assertIn(
            (
                "paper.pdf missing expected release/claim phrase: "
                r"Every\s+selected\s+row\s+is\s+non-?\s*Pass\s+at\s+the\s+score/response\s+and\s+consumer-?\s*boundary\s+gates"
            ),
            errors,
        )


class FalsePromotionGateSummaryTests(unittest.TestCase):
    def test_false_promotion_gate_summary_passes_for_frozen_author_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(paper)
            write_false_promotion_author_gate_matrix(paper)
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertEqual(errors, [])

    def test_false_promotion_gate_summary_rejects_core_fail_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(
                paper,
                {("score_or_response_gate", "Fail"): {"count": "12"}},
            )
            write_false_promotion_author_gate_matrix(paper)
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertIn("score_or_response_gate/Fail count drifted: '12'", errors)

    def test_false_promotion_gate_summary_rejects_non_core_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(
                paper,
                {("semantic_boundary_gate", "Pass"): {"count": "3"}},
            )
            write_false_promotion_author_gate_matrix(paper)
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertIn("semantic_boundary_gate/Pass count drifted: '3'", errors)

    def test_false_promotion_gate_summary_rejects_missing_required_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(paper, omit_key=("semantic_boundary_gate", "Pass"))
            write_false_promotion_author_gate_matrix(paper)
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertIn(
            "data/false_promotion_gate_summary.csv missing required rows: [('semantic_boundary_gate', 'Pass')]",
            errors,
        )

    def test_false_promotion_gate_summary_rejects_author_matrix_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(paper)
            write_false_promotion_author_gate_matrix(paper, {0: {"target_gate": "Fail"}})
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertIn("data/false_promotion_author_gate_matrix.csv target_gate/Partial count drifted: 5", errors)

    def test_false_promotion_gate_summary_rejects_scope_boundary_loss(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_false_promotion_gate_summary(
                paper,
                {("consumer_boundary_gate", "Fail"): {"boundary_note": "external reliability evidence"}},
            )
            write_false_promotion_author_gate_matrix(paper)
            errors: list[str] = []

            release_check.validate_false_promotion_gate_summary(paper, errors)

        self.assertIn(
            "consumer_boundary_gate/Fail boundary note lost non-reliability/prevalence scope",
            errors,
        )


class SupplementManifestTests(unittest.TestCase):
    def test_expected_supplement_rows_skip_manifest_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            reviewer_prelabel = sorted(release_check.REQUIRED_REVIEWER_PACKET_ALLOWED_PRELABEL)
            maintainer_only = sorted(release_check.REQUIRED_MAINTAINER_ONLY_AUTHOR_KEY)
            generated_paths = [
                "data/public.csv",
                *[path for path in reviewer_prelabel + maintainer_only if not path.startswith("versions/")],
            ]
            paper_source_paths = ["README.md", *[path for path in reviewer_prelabel if path.startswith("versions/")]]
            curated_paths = ["data/curated.csv"]
            for rel_path in sorted(set(generated_paths + curated_paths + paper_source_paths + ["asset_manifest.json", "paper.pdf"])):
                path = paper / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"{rel_path}\n", encoding="utf-8")
            manifest = {
                "generated": generated_paths,
                "curated": curated_paths,
                "paper_sources": paper_source_paths,
                "anonymous_supplement_excluded": maintainer_only,
                "reviewer_packet_allowed_prelabel": reviewer_prelabel,
                "maintainer_only_author_key": maintainer_only,
                "source_policy": "test",
                "validation_policy": "test",
                "review_snapshot_policy": "test",
                "anonymous_supplement_policy": "test",
                "excluded_from_public_claims": [],
            }
            (paper / "asset_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            errors: list[str] = []

            loaded_manifest = release_check.validate_manifest(paper, errors)
            rows = release_check.expected_supplement_rows(paper, loaded_manifest, errors)

        self.assertEqual(errors, [])
        self.assertEqual(
            {row["source_path"] for row in rows},
            {"data/public.csv", "data/curated.csv", "README.md", "asset_manifest.json", "paper.pdf", *reviewer_prelabel},
        )


class ReviewSnapshotManifestTests(unittest.TestCase):
    def test_review_snapshot_manifest_passes_for_dirty_local_packet_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            manifest: dict[str, object] = {
                "generated": ["data/public.csv", release_check.REVIEW_SNAPSHOT_MANIFEST],
                "curated": [],
                "paper_sources": ["README.md"],
                "anonymous_supplement_excluded": [],
            }
            write_review_snapshot_fixture(paper, Path.cwd(), manifest)
            errors: list[str] = []

            release_check.validate_review_snapshot_manifest(paper, Path.cwd(), manifest, errors)

        self.assertEqual(errors, [])

    def test_dirty_source_provenance_requires_review_snapshot_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            (paper / "data").mkdir(parents=True)
            (paper / "data" / "source_provenance.csv").write_text(
                "provenance_id,repo_tree_state\np1,dirty\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            release_check.validate_review_snapshot_manifest(paper, Path.cwd(), {}, errors)

        self.assertIn(
            f"{release_check.REVIEW_SNAPSHOT_MANIFEST} is required when source_provenance is dirty",
            errors,
        )

    def test_review_snapshot_manifest_rejects_stale_packet_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            manifest: dict[str, object] = {
                "generated": ["data/public.csv", release_check.REVIEW_SNAPSHOT_MANIFEST],
                "curated": [],
                "paper_sources": ["README.md"],
                "anonymous_supplement_excluded": [],
            }
            write_review_snapshot_fixture(paper, Path.cwd(), manifest)
            (paper / "data" / "public.csv").write_text("id,value\nr1,changed\n", encoding="utf-8")
            errors: list[str] = []

            release_check.validate_review_snapshot_manifest(paper, Path.cwd(), manifest, errors)

        self.assertIn("review snapshot manifest does not match current packet input bytes", errors)


class ManuscriptClaimBoundaryTests(unittest.TestCase):
    def test_generated_text_boundaries_reject_false_promotion_baseline_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            for rel_path in release_check.GENERATED_TEXT_SURFACES:
                path = paper / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                text = "claim_id,evidence_state\nC14,pre-label stress-control object\n"
                if rel_path == "data/claim_trace.csv":
                    text = (
                        "claim_id,evidence_state,allowed_wording\n"
                        "C14,false-promotion-baseline object,\n"
                        "C3,candidate failed-admission stress test,Strong same-family H2 candidate evidence\n"
                    )
                path.write_text(text, encoding="utf-8")
            errors: list[str] = []

            release_check.validate_generated_text_boundaries(paper, errors)

        self.assertIn(
            "data/claim_trace.csv forbidden stale generated wording hit: false-promotion[-\\s]+baseline",
            errors,
        )
        self.assertIn(
            "data/claim_trace.csv forbidden stale generated wording hit: Strong\\s+same-family\\s+H2\\s+candidate\\s+evidence",
            errors,
        )

    def test_manuscript_claim_boundaries_pass_for_current_required_framing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript(paper)
            errors: list[str] = []

            release_check.validate_manuscript_claim_boundaries(paper, errors)

        self.assertEqual(errors, [])

    def test_manuscript_claim_boundaries_reject_stale_stress_and_mofit_editorializing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript(
                paper,
                """
                We apply the instrument to a selected stress suite.
                The selected rows validate fixed claim wordings. Their role is boundary checking; frequency estimation requires separate corpus sampling.
                This release-scope consistency check covers selected boundary cases.
                General gate sufficiency and independent-coding reliability require broader corpora and independent labels.
                The current status is \\texttt{n\\_reviewers=0},
                \\texttt{packet\\_ready\\_only}, and pre-label stress-control.
                Reviewer agreement and prevalence require independent labels and a larger sampled corpus.
                The status artifact records \\texttt{n\\_reviewers=0} and
                \\texttt{allowed\\_claim\\_scope=packet\\_ready\\_only}.
                The routes include a high-scoring compact public score-file replay candidate.
                MoFit COCO is a blocked candidate: all six gates remain non-Pass.
                C14, N50-denominator, admitted-evidence, second-public-asset,
                and compute-release claims stay outside the packet.
                The current MoFit packet supplies stress coverage.
                In the current packet, the provenance table is a local packet-identity snapshot;
                dirty tree state and local paths identify the review snapshot, and the
                public-release provenance gate remains unresolved.
                """,
            )
            errors: list[str] = []

            release_check.validate_manuscript_claim_boundaries(paper, errors)

        self.assertIn("main.tex must frame the row set as frozen boundary cases used as protocol checks", errors)
        self.assertIn("main.tex must not frame the selected rows as a stress-suite empirical sample", errors)
        self.assertIn("main.tex must not editorialize MoFit as a high-scoring candidate", errors)

    def test_manuscript_claim_boundaries_reject_missing_dirty_provenance_caveat(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            write_manuscript(
                paper,
                """
                We apply the instrument to a set of frozen boundary cases as protocol checks.
                The selected rows validate fixed claim wordings. Their role is boundary checking; frequency estimation requires separate corpus sampling.
                This release-scope consistency check covers selected boundary cases.
                General gate sufficiency and independent-coding reliability require broader corpora and independent labels.
                The current status is \\texttt{n\\_reviewers=0},
                \\texttt{packet\\_ready\\_only}, and pre-label stress-control.
                Reviewer agreement and prevalence require independent labels and a larger sampled corpus.
                The status artifact records \\texttt{n\\_reviewers=0} and
                \\texttt{allowed\\_claim\\_scope=packet\\_ready\\_only}.
                MoFit COCO is a blocked candidate: all six gates remain non-Pass.
                C14, N50-denominator, admitted-evidence, second-public-asset,
                and compute-release claims stay outside the packet.
                The current MoFit packet supplies stress coverage.
                """,
            )
            errors: list[str] = []

            release_check.validate_manuscript_claim_boundaries(paper, errors)

        self.assertIn("main.tex must identify dirty provenance as a local packet snapshot", errors)
        self.assertIn("main.tex must reject clean-public-provenance interpretation", errors)


class ReferenceIntegrityAuditTests(unittest.TestCase):
    def write_reference_fixture(
        self,
        paper: Path,
        row_updates: dict[str, str] | None = None,
    ) -> None:
        (paper / "data").mkdir(parents=True, exist_ok=True)
        (paper / "refs.bib").write_text(
            "\n".join(
                [
                    "@inproceedings{verified2026,",
                    "  title = {Verified Diffusion Audit},",
                    "  author = {Example, Ada},",
                    "  booktitle = {Proceedings of the Test Conference},",
                    "  year = {2026},",
                    "  doi = {10.48550/arXiv.2601.00001}",
                    "}",
                    "",
                    "@misc{arxiv2026,",
                    "  title = {Arxiv Audit},",
                    "  author = {Example, Ben},",
                    "  year = {2026},",
                    "  eprint = {2601.00002},",
                    "  archivePrefix = {arXiv}",
                    "}",
                    "",
                    "@article{url2026,",
                    "  title = {URL Audit},",
                    "  author = {Example, Cy},",
                    "  journal = {Journal of Tests},",
                    "  year = {2026},",
                    "  url = {https://example.org/url-audit}",
                    "}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = [
            {
                "bib_key": "verified2026",
                "entry_type": "inproceedings",
                "title": "Verified Diffusion Audit",
                "year": "2026",
                "identifier_kind": "doi_handle",
                "identifier_value": "10.48550/arXiv.2601.00001",
                "verification_url": "https://doi.org/api/handles/10.48550/arXiv.2601.00001",
                "http_status": "200",
                "verification_status": "verified",
                "verification_note": "verified: DOI handle exists",
                "metadata_status": "verified",
                "metadata_source": "doi_csl_json",
                "metadata_note": "verified: title/year match via https://doi.org/10.48550/arXiv.2601.00001",
                "checked_at_utc": "2026-06-09T00:00:00Z",
            },
            {
                "bib_key": "arxiv2026",
                "entry_type": "misc",
                "title": "Arxiv Audit",
                "year": "2026",
                "identifier_kind": "arxiv_abs",
                "identifier_value": "2601.00002",
                "verification_url": "https://arxiv.org/abs/2601.00002",
                "http_status": "200",
                "verification_status": "verified",
                "verification_note": "verified: arXiv abstract resolved",
                "metadata_status": "verified",
                "metadata_source": "arxiv_api",
                "metadata_note": "verified: title/year match via https://export.arxiv.org/api/query?id_list=2601.00002",
                "checked_at_utc": "2026-06-09T00:00:00Z",
            },
            {
                "bib_key": "url2026",
                "entry_type": "article",
                "title": "URL Audit",
                "year": "2026",
                "identifier_kind": "url",
                "identifier_value": "https://example.org/url-audit",
                "verification_url": "https://example.org/url-audit",
                "http_status": "200",
                "verification_status": "verified",
                "verification_note": "verified: reference URL resolved",
                "metadata_status": "verified",
                "metadata_source": "url_payload",
                "metadata_note": "verified: title token coverage=1.00",
                "checked_at_utc": "2026-06-09T00:00:00Z",
            },
        ]
        if row_updates:
            rows[0].update(row_updates)
        with (paper / release_check.REFERENCE_INTEGRITY_AUDIT).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=release_check.REFERENCE_INTEGRITY_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_reference_integrity_audit_passes_for_verified_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_reference_fixture(paper)
            errors: list[str] = []

            release_check.validate_reference_integrity_audit(paper, errors)

        self.assertEqual(errors, [])

    def test_reference_integrity_audit_rejects_unverified_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_reference_fixture(paper, {"verification_status": "failed"})
            errors: list[str] = []

            release_check.validate_reference_integrity_audit(paper, errors)

        self.assertIn("verified2026 reference verification is not verified", errors)

    def test_reference_integrity_audit_rejects_identifier_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_reference_fixture(paper, {"identifier_value": "10.48550/arXiv.2601.99999"})
            errors: list[str] = []

            release_check.validate_reference_integrity_audit(paper, errors)

        self.assertIn("verified2026 reference audit DOI drifted: '10.48550/arXiv.2601.99999'", errors)

    def test_reference_integrity_audit_rejects_bib_metadata_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_reference_fixture(
                paper,
                {
                    "entry_type": "misc",
                    "title": "Stale Audit Title",
                    "year": "2025",
                },
            )
            errors: list[str] = []

            release_check.validate_reference_integrity_audit(paper, errors)

        self.assertIn("verified2026 reference audit entry_type drifted: 'misc'", errors)
        self.assertIn("verified2026 reference audit title drifted: 'Stale Audit Title'", errors)
        self.assertIn("verified2026 reference audit year drifted: '2025'", errors)

    def test_reference_integrity_audit_rejects_metadata_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper = Path(tmpdir)
            self.write_reference_fixture(paper, {"metadata_status": "failed"})
            errors: list[str] = []

            release_check.validate_reference_integrity_audit(paper, errors)

        self.assertIn("verified2026 reference metadata is not verified", errors)


if __name__ == "__main__":
    unittest.main()
