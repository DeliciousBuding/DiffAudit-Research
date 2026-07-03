"""Build the E2 public-source-first freeze ledger.

The ledger is a compact handoff surface for the current evidence upgrade route.
It summarizes the rows that can shape the next public-source freeze, external
review, or second-asset watch decision without promoting any row beyond its
current gate state.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
PAPER = ROOT / "papers" / "diffaudit-evidence-paper"

REFRESH_CSV = PREFLIGHT / "e2_high_value_public_asset_delta_refresh_late_2026_06_09.csv"
E2Q005_AGG_CSV = PREFLIGHT / "e2q005_external_style_review_aggregation_2026_06_06.csv"
C14_STATUS_CSV = PAPER / "build" / "false_promotion_external_review_packet_status.csv"
OUT_CSV = PREFLIGHT / "e2_public_source_freeze_ledger_2026_06_09.csv"
OUT_MD = PREFLIGHT / "e2_public_source_freeze_ledger_2026_06_09.md"

FIELDNAMES = [
    "ledger_id",
    "title",
    "lane",
    "source_inputs",
    "source_refreshed_at_utc",
    "identity_status",
    "evidence_state",
    "next_action",
    "missing_surfaces",
    "allowed_use",
    "excluded_claims",
    "compute_release",
    "review_status",
]


LANE_BY_ID = {
    "E1-NDSS-324": "second_asset_watch_compute_gated",
    "E2-MOFIT": "support_score_file_boundary",
    "E2Q-006": "compact_manifest_watch",
    "E2SCT-029": "c14_v2_candidate_result_surface",
    "E2SCT-031": "support_sidecar_dlm",
    "E2SCT-032": "support_sidecar_tabular",
    "E2SCT-033": "support_sidecar_image_code_split",
    "E2SCT-034": "support_sidecar_tabular_archive",
    "E2SCT-035": "future_vlm_stratum_scout",
}

MISSING_BY_ID = {
    "E1-NDSS-324": "row-bound score/response packet; metric verifier; immutable row identifiers",
    "E2-MOFIT": "target checkpoint identity; explicit row IDs; official metric JSON/ROC; surface-delta control",
    "E2Q-006": "compact row manifest; target hashes; no-training verifier",
    "E2SCT-029": "safe public row IDs; public input images; immutable checkpoint identity; verifier",
    "E2SCT-031": "target model identity; member/nonmember row manifest; score packet; metric artifact",
    "E2SCT-032": "row-bound predictions or scores; labels; metric JSON/CSV; verifier",
    "E2SCT-033": "result CSV; row-bound scores/responses; metric JSON; checkpoint-bound verifier",
    "E2SCT-034": "row-scale score arrays; row labels; metric verifier",
    "E2SCT-035": "row-bound attack scores or responses; metric JSON/CSV; no-training verifier; VLM consumer boundary",
}

ALLOWED_USE_BY_ID = {
    "E1-NDSS-324": "high-value second-asset watch row after manifest-level identity checks",
    "E2-MOFIT": "public score-file boundary case and support-only diagnostic",
    "E2Q-006": "official score-artifact support surface for compact-manifest watch",
    "E2SCT-029": "C14-v2 public-result-surface candidate",
    "E2SCT-031": "DLM public-code route closure",
    "E2SCT-032": "tabular result-page route closure",
    "E2SCT-033": "image-diffusion code-and-split route closure",
    "E2SCT-034": "tabular aggregate-archive route closure",
    "E2SCT-035": "future VLM controlled-benchmark scout",
}

EXCLUDED_DEFAULT = (
    "C14 update; N50 denominator; admitted evidence; second public score/response asset; compute release"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def e2q005_review_status() -> str:
    rows = read_csv(E2Q005_AGG_CSV)
    by_field = {row["field"]: row for row in rows}
    reviewers = by_field["target_gate"]["n_reviewers"]
    wording = by_field["allowed_wording"]["majority"]
    target = by_field["target_gate"]["majority"]
    provenance = by_field["provenance_gate"]["majority"]
    return (
        f"{reviewers} reviewers; allowed_wording={wording}; "
        f"target_gate={target}; provenance_gate={provenance}"
    )


def c14_status() -> dict[str, str]:
    rows = read_csv(C14_STATUS_CSV)
    if len(rows) != 1:
        raise ValueError(f"{C14_STATUS_CSV} must contain exactly one row")
    return rows[0]


def build_rows() -> list[dict[str, str]]:
    refresh_rows = read_csv(REFRESH_CSV)
    rows: list[dict[str, str]] = []

    rows.append(
        {
            "ledger_id": "E2Q-005",
            "title": "Tracing the Roots feature-packet review row",
            "lane": "single_row_feature_packet_review",
            "source_inputs": "e2q005_external_style_review_aggregation_2026_06_06.csv",
            "source_refreshed_at_utc": "review_aggregation_current",
            "identity_status": "reviewed_feature_packet",
            "evidence_state": "bounded_support",
            "next_action": "use as reviewer-calibration example; keep outside denominator counts",
            "missing_surfaces": "target checkpoint identity; raw sample IDs",
            "allowed_use": "provenance-limited feature-packet review row",
            "excluded_claims": "N50 denominator; admitted row; black-box response evidence; compute release",
            "compute_release": "no",
            "review_status": e2q005_review_status(),
        }
    )

    c14 = c14_status()
    rows.append(
        {
            "ledger_id": "C14-PACKET",
            "title": "C14 false-promotion hard-blind review packet",
            "lane": "pre_label_external_review_packet",
            "source_inputs": "false_promotion_external_review_packet_status.csv",
            "source_refreshed_at_utc": "packet_status_current",
            "identity_status": c14["packet_label_readiness"],
            "evidence_state": c14["allowed_claim_scope"],
            "next_action": "collect reviewer CSVs and declarations before aggregation",
            "missing_surfaces": "reviewer CSVs; independence declarations; majority labels; reliability thresholds",
            "allowed_use": "pre-label weak-rule stress-control packet",
            "excluded_claims": "completed external adjudication; reviewer reliability; compute release",
            "compute_release": "no",
            "review_status": (
                f"n_reviewers={c14['n_reviewers']}; "
                f"external_label_aggregation_available={c14['external_label_aggregation_available']}; "
                f"reliability_claim_allowed={c14['reliability_claim_allowed']}"
            ),
        }
    )

    for row in refresh_rows:
        queue_id = row["queue_id"]
        if queue_id not in LANE_BY_ID:
            raise ValueError(f"Unhandled high-value row: {queue_id}")
        rows.append(
            {
                "ledger_id": queue_id,
                "title": row["title"],
                "lane": LANE_BY_ID[queue_id],
                "source_inputs": "e2_high_value_public_asset_delta_refresh_late_2026_06_09.csv",
                "source_refreshed_at_utc": row["refreshed_at_utc"],
                "identity_status": row["identity_delta_status"],
                "evidence_state": "no_current_upgrade",
                "next_action": row["required_followup"],
                "missing_surfaces": MISSING_BY_ID[queue_id],
                "allowed_use": ALLOWED_USE_BY_ID[queue_id],
                "excluded_claims": "Direction A current upgrade; " + EXCLUDED_DEFAULT
                if queue_id == "E2SCT-035"
                else EXCLUDED_DEFAULT,
                "compute_release": "no",
                "review_status": (
                    f"compact_reopen_surface_hint={row['compact_reopen_surface_hint']}; "
                    f"artifact_surface_hint={row['artifact_surface_hint']}; "
                    f"followup_bucket={row['followup_bucket']}"
                ),
            }
        )
    return rows


def render_md(rows: list[dict[str, str]]) -> str:
    by_state: dict[str, int] = {}
    by_lane: dict[str, int] = {}
    high_value_snapshots = sorted(
        {
            row["source_refreshed_at_utc"]
            for row in rows
            if row["source_inputs"] == "e2_high_value_public_asset_delta_refresh_late_2026_06_09.csv"
        }
    )
    for row in rows:
        by_state[row["evidence_state"]] = by_state.get(row["evidence_state"], 0) + 1
        by_lane[row["lane"]] = by_lane.get(row["lane"], 0) + 1

    lines = [
        "# E2 Public-Source Freeze Ledger",
        "",
        "> Date: 2026-06-09",
        "> Scope: handoff ledger for the next public-source-first freeze cycle.",
        "",
        "This ledger gives the next reviewer one current entrypoint for the evidence",
        "upgrade route. It combines the feature-packet review row, the prepared C14",
        "review packet, and the high-value public-asset delta refresh. It records",
        "the current state of each row and the surface that must appear before a",
        "stronger claim can be made.",
        "",
        "## Counts",
        "",
        f"- ledger rows: `{len(rows)}`",
        f"- bounded-support feature-packet rows: `{by_state.get('bounded_support', 0)}`",
        f"- C14 pre-label packets: `{by_state.get('packet_ready_only', 0)}`",
        f"- high-value rows with no current upgrade: `{by_state.get('no_current_upgrade', 0)}`",
        f"- compute-release rows: `{sum(row['compute_release'] == 'yes' for row in rows)}`",
        f"- high-value refresh snapshot: `{';'.join(high_value_snapshots)}`",
        "",
        "## Lane Counts",
        "",
    ]
    for lane in sorted(by_lane):
        lines.append(f"- `{lane}`: `{by_lane[lane]}`")

    lines.extend(
        [
            "",
            "## Ledger",
            "",
            "| Row | Lane | State | Next action | Missing surfaces |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {ledger_id} | {lane} | `{evidence_state}` | {next_action} | {missing_surfaces} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Claim Rule",
            "",
            "Use this ledger as an execution table. The paper may cite a row only at",
            "the state recorded above. Stronger wording needs the missing surfaces in",
            "that row plus the existing release-packet checks.",
            "",
            "Current paper-facing state: the C14 packet stays pre-label, the N50",
            "denominator count stays at zero, admitted-row and second-asset states",
            "are unchanged, and compute release stays closed.",
            "",
        ]
    )
    return "\n".join(lines)


def assert_ledger(rows: list[dict[str, str]]) -> None:
    ids = [row["ledger_id"] for row in rows]
    expected_ids = [
        "E2Q-005",
        "C14-PACKET",
        "E1-NDSS-324",
        "E2Q-006",
        "E2-MOFIT",
        "E2SCT-029",
        "E2SCT-031",
        "E2SCT-032",
        "E2SCT-033",
        "E2SCT-034",
        "E2SCT-035",
    ]
    if ids != expected_ids:
        raise AssertionError(f"ledger row order drifted: {ids!r}")
    if any(row["compute_release"] != "no" for row in rows):
        raise AssertionError("ledger must keep compute_release=no for every row")
    if sum(row["evidence_state"] == "no_current_upgrade" for row in rows) != 9:
        raise AssertionError("ledger must keep nine high-value no-upgrade rows")
    if rows[0]["evidence_state"] != "bounded_support":
        raise AssertionError("E2Q-005 must remain bounded_support")
    if rows[1]["evidence_state"] != "packet_ready_only":
        raise AssertionError("C14 packet must remain packet_ready_only")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate output freshness")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_rows()
    assert_ledger(rows)
    markdown = render_md(rows)

    if args.check:
        current_csv_rows = read_csv(OUT_CSV)
        if current_csv_rows != rows:
            raise SystemExit(f"{OUT_CSV.relative_to(ROOT)} is stale")
        current_md = OUT_MD.read_text(encoding="utf-8")
        if current_md != markdown:
            raise SystemExit(f"{OUT_MD.relative_to(ROOT)} is stale")
        print("E2 public-source freeze ledger check passed")
        return 0

    write_csv(OUT_CSV, rows)
    OUT_MD.write_text(markdown, encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
