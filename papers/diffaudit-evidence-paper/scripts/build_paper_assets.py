from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import re
import subprocess

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


plt.rcParams.update(
    {
        "pdf.use14corefonts": True,
        "ps.useafm": True,
        "font.family": "serif",
        "mathtext.fontset": "cm",
    }
)

ROOT = Path(__file__).resolve().parents[3]
PAPER = Path(__file__).resolve().parents[1]
DATA = PAPER / "data"
FIGURES = PAPER / "figures"

GATE_COLUMNS = [
    ("target_gate", "Target"),
    ("split_gate", "Split"),
    ("evidence_gate", "Evidence"),
    ("metric_gate", "Metric"),
    ("boundary_gate", "Boundary"),
    ("delta_gate", "Surface delta"),
]
GATE_PLOT_LABELS = {
    "Target": "Target",
    "Split": "Split",
    "Evidence": "Rows",
    "Metric": "Metric",
    "Boundary": "Boundary",
    "Surface delta": "Delta",
}
GATE_OUTCOMES = ["Pass", "Partial", "Fail"]
CLAIM_SUPPORT_LEVELS = ["L0", "L1", "L2", "L3"]
V1_STRATUM_SUPPORT_LEVEL = {
    "metadata-only-no-artifact": "L0",
    "withdrawn-no-artifact": "L0",
    "code-public-no-packet": "L1",
    "artifact-rich-partial": "L1",
    "mechanism-candidate": "L2",
    "boundary-negative": "L2",
    "bounded-negative": "L2",
    "positive-non-admitted": "L2",
    "source-confounded": "L2",
    "support-only": "L2",
    "positive-control": "L3",
}
FIXED_SEARCH_SUPPORT_LEVEL = {
    "excluded_no_result": "L0",
    "excluded_query_noise": "L0",
    "included_metadata_only": "L0",
    "included_existing_watch": "L0",
    "included_existing_gate": "L1",
    "included_new_metadata": "L1",
}
CLAIM_SUPPORT_LABELS = {
    "L0": "metadata/search discovery",
    "L1": "artifact inspection without row-bound metrics",
    "L2": "scoreable or replayed research-side packet",
    "L3": "consumer-admitted/reportable control",
}
TRACE_GATE_COLUMNS = [
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
]
TRACE_GATE_OUTCOMES = {"Pass", "Partial", "Fail", "N/A"}
PDF_METADATA = {
    "Creator": "DiffAudit build_paper_assets.py",
    "CreationDate": datetime(2026, 5, 26, tzinfo=timezone.utc),
    "ModDate": datetime(2026, 5, 26, tzinfo=timezone.utc),
}
REPORT_ROLE_LABELS = {
    "primary-risk-evidence": "primary risk",
    "defense-comparator": "defense comparator",
    "upper-bound-comparator": "upper-bound comparator",
    "defense-bridge": "defense bridge",
}
REPLAY_TIER_LABELS = {
    "row-score-replay": "row replay",
    "target-score-replay": "target-row replay",
    "source-documented-point-estimate": "point estimate",
}


def paper_evidence_level(item: dict) -> str:
    """Return paper-facing evidence wording while preserving raw provenance elsewhere."""
    if item.get("report_role") == "defense-bridge":
        return "target-score-defense-bridge"
    if item.get("evidence_level") == "runtime-mainline":
        return "reportable-mainline"
    return item["evidence_level"]


def paper_quality_cost(value: str) -> str:
    raw_recon_threshold_phrase = " ".join(("unified", "artifact", "threshold", "replay"))
    if raw_recon_threshold_phrase in value:
        return (
            "100 public samples per split; DDIM step30; "
            "source-documented public-100 threshold readout; "
            "no row-score array retained; cuda"
        )
    return value.replace("runtime mainline plus ", "").replace("; cuda runtime", "; cuda")


PLOT_METHOD_LABELS = {
    "recon DDIM public-100 step30": "recon\nBB point",
    "PIA GPU512 baseline": "PIA\nGB row",
    "PIA + G-1 dropout": "dropout\nGB row",
    "GSA 1k-3shadow": "GSA\nWB point",
}
PLOT_DEFENSE_LABELS = {
    "provisional G-1 = stochastic-dropout (all_steps)": "dropout\nGB row",
    "W-1 strong-v3 full-scale": "DPDM W-1\ntarget-row",
}
FALSE_PROMOTION_RULES = [
    ("code_availability_would_promote", "code"),
    ("artifact_availability_would_promote", "artifact"),
    ("paper_claim_artifact_link_would_promote", "paper-link"),
    ("metric_code_split_would_promote", "metric/split"),
    ("score_only_would_promote", "score-only"),
]
FALSE_PROMOTION_ROW_LABELS = {
    "E2SCT-004": "STROLL",
    "E2SCT-012": "Shake",
    "E2SCT-016": "HOLD++",
    "E2SCT-021": "ELSA",
    "E2SCT-002": "DMin",
    "E2SCT-005": "Diffence",
    "E2SCT-013": "DCR",
    "E2SCT-009": "Aniso",
    "E2SCT-014": "CDI",
    "E2SCT-011": "VAE2",
    "E2SCT-020": "LSA",
    "E2SCT-019": "VidLeaks",
    "E2SCT-024": "DME",
}
FALSE_PROMOTION_REVIEW_GATES = [
    "target_gate",
    "split_gate",
    "score_or_response_gate",
    "metric_gate",
    "semantic_boundary_gate",
    "provenance_gate",
    "consumer_boundary_gate",
]
FALSE_PROMOTION_REVIEW_VALUES = "Pass|Partial|Fail|N/A"
FALSE_PROMOTION_VERDICT_VALUES = (
    "false_promotion_control|semantic_boundary_block|artifact_surface_block|"
    "needs_external_adjudication|invalid_row"
)
FALSE_PROMOTION_COMPUTE_RELEASE_VALUES = "no|yes_with_full_contract"
FALSE_PROMOTION_AUTHOR_VERDICT = {
    "E2SCT-004": "artifact_surface_block",
    "E2SCT-012": "artifact_surface_block",
    "E2SCT-016": "artifact_surface_block",
    "E2SCT-021": "artifact_surface_block",
    "E2SCT-002": "semantic_boundary_block",
    "E2SCT-005": "semantic_boundary_block",
    "E2SCT-013": "semantic_boundary_block",
    "E2SCT-009": "semantic_boundary_block",
    "E2SCT-014": "semantic_boundary_block",
    "E2SCT-011": "artifact_surface_block",
    "E2SCT-020": "artifact_surface_block",
    "E2SCT-019": "artifact_surface_block",
    "E2SCT-024": "artifact_surface_block",
}
FALSE_PROMOTION_AUTHOR_GATE_LABELS = {
    "E2SCT-004": {
        "target_gate": "Partial",
        "split_gate": "Pass",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Pass",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "score_or_response_gate",
        "gate_rationale": "Public STROLL member/nonmember annotations are visible, but generated outputs, DreamSim scores, metric JSON, and verifier are absent.",
    },
    "E2SCT-012": {
        "target_gate": "Fail",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Pass",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "target_gate",
        "gate_rationale": "Runnable leakage code is visible, but the private set, checkpoints, responses, scores, and metrics are runtime products.",
    },
    "E2SCT-016": {
        "target_gate": "Partial",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Partial",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "score_or_response_gate",
        "gate_rationale": "Defense code and split/config hints are public, but checkpoint-bound scores, responses, ROC arrays, metric JSON/CSV, and verifier are absent.",
    },
    "E2SCT-021": {
        "target_gate": "Fail",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "target_gate",
        "gate_rationale": "The public starter package exposes examples and metrics, but real challenge targets, labels, predictions, datasets, and participant artifacts are gated.",
    },
    "E2SCT-002": {
        "target_gate": "Partial",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "semantic_boundary_gate",
        "gate_rationale": "The public surface supports attribution/influence inspection, not row-bound member/nonmember MIA scores or verifier artifacts.",
    },
    "E2SCT-005": {
        "target_gate": "Fail",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "semantic_boundary_gate",
        "gate_rationale": "The protected target is classifier membership privacy with diffusion purification, not a diffusion-generator membership score/response packet.",
    },
    "E2SCT-013": {
        "target_gate": "Partial",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "semantic_boundary_gate",
        "gate_rationale": "Copying and retrieval artifacts are public, but they are not pointwise member/nonmember MIA labels, scores, ROC arrays, or verifier packets.",
    },
    "E2SCT-009": {
        "target_gate": "Partial",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "semantic_boundary_gate",
        "gate_rationale": "Prompt mem/nmem files and a memorization metric are visible, but prompt memorization is not immutable image-row membership evidence.",
    },
    "E2SCT-014": {
        "target_gate": "Partial",
        "split_gate": "Partial",
        "score_or_response_gate": "Fail",
        "metric_gate": "Partial",
        "semantic_boundary_gate": "Fail",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "semantic_boundary_gate",
        "gate_rationale": "CDI exposes dataset-level identification workflows, but not per-sample diffusion-generator membership evidence.",
    },
    "E2SCT-011": {
        "target_gate": "Fail",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Pass",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "target_gate",
        "gate_rationale": "The latent-space MIA claim and code are public, but split manifests, target checkpoints, caches, scores, ROC arrays, and verifier are absent.",
    },
    "E2SCT-020": {
        "target_gate": "Fail",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Partial",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "score_or_response_gate",
        "gate_rationale": "The demo exposes score-like JSON arrays, but they are mock visualization data without target, split, score provenance, metric packet, or verifier.",
    },
    "E2SCT-019": {
        "target_gate": "Fail",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Partial",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "target_gate",
        "gate_rationale": "The Zenodo code snapshot is public, but no hashable T2V target, exact video split, generated-video packet, score/ROC/metric artifact, or verifier is public.",
    },
    "E2SCT-024": {
        "target_gate": "Fail",
        "split_gate": "Fail",
        "score_or_response_gate": "Fail",
        "metric_gate": "Fail",
        "semantic_boundary_gate": "Pass",
        "provenance_gate": "Partial",
        "consumer_boundary_gate": "Fail",
        "first_blocking_gate": "target_gate",
        "gate_rationale": "The official repo is public, but it is a README-only stub with no implementation code, target/split packet, checkpoint, scores, ROC/metric artifact, or verifier.",
    },
}
FALSE_PROMOTION_ROW_SOURCES = {
    "E2SCT-004": {
        "observed_at": "2026-06-06",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct004_genai_confessions_public_surface_check_2026_06_06.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct004_genai_confessions_public_surface_check_2026_06_06.md",
        "public_urls": "https://github.com/hanyfarid/MembershipInference;https://zenodo.org/records/14573149;https://huggingface.co/datasets/faridlab/stroll;https://export.arxiv.org/api/query?id_list=2501.06399",
    },
    "E2SCT-012": {
        "observed_at": "2026-06-06",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct012_shake_to_leak_public_surface_check_2026_06_06.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct012_shake_to_leak_public_surface_check_2026_06_06.md",
        "public_urls": "https://github.com/VITA-Group/Shake-to-Leak;https://github.com/VITA-Group/Shake-to-Leak/releases",
    },
    "E2SCT-016": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct016_miahold_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct016_miahold_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/bensterl15/MIAHOLD;https://github.com/bensterl15/MIAHOLDCIFAR",
    },
    "E2SCT-021": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/PMBio/Health-Privacy-Challenge",
    },
    "E2SCT-002": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct002_dmin_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct002_dmin_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/huawei-lin/DMin",
    },
    "E2SCT-005": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct005_diffence_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct005_diffence_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/SPIN-UMass/Diffence;https://zenodo.org/records/13706131",
    },
    "E2SCT-013": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct013_dcr_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct013_dcr_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/somepago/DCR",
    },
    "E2SCT-009": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/rohanasthana/memorization-anisotropy",
    },
    "E2SCT-014": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct014_cdi_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct014_cdi_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/sprintml/copyrighted_data_identification",
    },
    "E2SCT-011": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct011_vae2diffusion_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct011_vae2diffusion_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/mx-ethan-rao/VAE2Diffusion;https://arxiv.org/abs/2511.20592;https://github.com/mx-ethan-rao/VAE2Diffusion/releases",
    },
    "E2SCT-020": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct020_lsa_probe_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct020_lsa_probe_public_surface_check_2026_06_07.md",
        "public_urls": "https://github.com/kaslim/LSA-Probe;https://raw.githubusercontent.com/kaslim/LSA-Probe/HEAD/README.md;https://github.com/kaslim/LSA-Probe/releases;https://kaslim.github.io/lsa-probe/;https://raw.githubusercontent.com/kaslim/kaslim.github.io/main/lsa-probe/generate_demo_data.py;https://export.arxiv.org/api/query?id_list=2602.01645",
    },
    "E2SCT-019": {
        "observed_at": "2026-06-07",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.md",
        "public_urls": "https://zenodo.org/records/17972831;https://zenodo.org/api/records/17972831;https://github.com/wangli-codes/T2V_MIA/tree/v1.0.1",
    },
    "E2SCT-024": {
        "observed_at": "2026-06-08",
        "check_csv": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct024_dme_public_surface_check_2026_06_08.csv",
        "check_md": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct024_dme_public_surface_check_2026_06_08.md",
        "public_urls": "https://github.com/F-YaNG1/DME;https://raw.githubusercontent.com/F-YaNG1/DME/main/README.md",
    },
}
GENERATOR_COMMAND = "python -X utf8 papers/diffaudit-evidence-paper/scripts/build_paper_assets.py"
GENERATED_MANIFEST_PATHS = [
    "data/admitted_rows.csv",
    "data/h2_output_cloud_rows.csv",
    "data/negative_support_rows.csv",
    "data/stl10_rediffuse_route_summary.csv",
    "data/mofit_public_score_metrics.json",
    "data/mofit_public_score_alpha_sweep.csv",
    "data/mofit_public_score_file_manifest.csv",
    "data/mofit_public_score_roc.csv",
    "data/mofit_public_score_position_manifest.csv",
    "data/mofit_public_gate_status.csv",
    "data/mofit_public_caption_position_manifest.csv",
    "data/metric_uncertainty.csv",
    "data/artifact_gate_summary.csv",
    "data/artifact_strata_summary.csv",
    "data/artifact_claim_support_rows.csv",
    "data/artifact_claim_support_summary.csv",
    "data/false_promotion_exemplars.csv",
    "data/false_promotion_rule_summary.csv",
    "data/false_promotion_external_review_packet.csv",
    "data/false_promotion_blinded_review_packet.csv",
    "data/false_promotion_adjudication_key.csv",
    "data/false_promotion_external_review_template.csv",
    "data/false_promotion_row_trace.csv",
    "data/false_promotion_author_gate_matrix.csv",
    "data/false_promotion_gate_summary.csv",
    "data/claim_trace.csv",
    "data/claim_transition_examples.csv",
    "data/manuscript_claim_audit.csv",
    "data/citation_context_audit.csv",
    "data/reference_integrity_audit.csv",
    "data/claim_gate_recode_template.csv",
    "data/claim_gate_recode_packet_manifest.csv",
    "data/report_correctness_fault_injection.csv",
    "data/source_provenance.csv",
    "data/review_snapshot_manifest.csv",
    "figures/admitted_rows_metrics.pdf",
    "figures/h2_output_cloud_controls.pdf",
    "figures/evidence_contract_pipeline.pdf",
    "figures/artifact_gate_summary.pdf",
    "figures/artifact_claim_support_summary.pdf",
    "figures/false_promotion_exemplars.pdf",
    "figures/false_promotion_gate_matrix.pdf",
]
ANONYMOUS_SUPPLEMENT_EXCLUDED_PATHS = [
    "data/false_promotion_external_review_packet.csv",
    "data/false_promotion_adjudication_key.csv",
    "data/false_promotion_author_gate_matrix.csv",
    "data/false_promotion_gate_summary.csv",
    "figures/false_promotion_gate_matrix.pdf",
]
REVIEWER_PACKET_ALLOWED_PRELABEL_PATHS = [
    "data/false_promotion_blinded_review_packet.csv",
    "data/false_promotion_external_review_template.csv",
    "data/false_promotion_row_trace.csv",
    "versions/direction-a-false-promotion-audit-codebook.md",
    "versions/direction-a-c14-external-review-launch-protocol.md",
]
MAINTAINER_ONLY_AUTHOR_KEY_PATHS = [
    "data/false_promotion_external_review_packet.csv",
    "data/false_promotion_adjudication_key.csv",
    "data/false_promotion_author_gate_matrix.csv",
    "data/false_promotion_gate_summary.csv",
    "figures/false_promotion_gate_matrix.pdf",
]
REVIEW_SNAPSHOT_SCHEMA_VERSION = "review-snapshot-v1"
REVIEW_SNAPSHOT_KIND = "local_review_snapshot"
REVIEW_SNAPSHOT_SCOPE = "paper_release_packet_inputs_only"
REVIEW_SNAPSHOT_BOUNDARY_NOTE = "local review snapshot only; not clean public release provenance"
REVIEW_SNAPSHOT_EXCLUDED_PUBLIC_CLAIMS = (
    "dirty tree is not public provenance;"
    "candidate/support/support-only rows are not admitted evidence;"
    "permission-bound artifacts are not public replay evidence"
)
CURATED_MANIFEST_PATHS = [
    "data/negative_support_curated_metrics.csv",
    "data/artifact_corpus_v1.csv",
    "data/artifact_corpus_fixed_search_20260526.csv",
    "data/artifact_corpus_broader_source_20260527.csv",
    "data/artifact_corpus_targeted_artifact_links_20260527.csv",
    "data/artifact_second_pass_label_review_20260526.csv",
    "versions/direction-c-corpus-v1.md",
    "versions/direction-c-fixed-search-batch-20260526.md",
    "versions/direction-c-broader-source-pass-20260527.md",
    "versions/direction-c-targeted-artifact-link-pass-20260527.md",
    "versions/direction-c-second-pass-label-review-20260526.md",
]
PAPER_SOURCE_MANIFEST_PATHS = [
    "README.md",
    "BUILD.md",
    "main.tex",
    "refs.bib",
    "scripts/build_paper_assets.py",
    "scripts/build_reference_integrity_audit.py",
    "claim_register.md",
    "source_map.md",
    "evidence_bank.md",
    "versions/README.md",
    "versions/direction-a-false-promotion-audit-codebook.md",
    "versions/direction-a-c14-external-review-launch-protocol.md",
    "versions/direction-a-claim-gate-recode-protocol.md",
    "versions/direction-d-report-correctness-fault-injection.md",
    "versions/direction-a-mofit-public-score-surface.md",
    "versions/drafts/direction-a-evidence-contract-paper.md",
]
REVIEW_SNAPSHOT_REPO_SOURCE_PATHS = [
    "docs/internal/c14-e2-external-adjudication-preregistration-2026-06-09.md",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.md",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_watchlist_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_late_2026_06_09.md",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_late_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_gate_queue_late_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_public_source_freeze_ledger_2026_06_09.md",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_public_source_freeze_ledger_2026_06_09.csv",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md",
    "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.csv",
]
PROVENANCE_SOURCE_ITEMS = [
    {
        "provenance_id": "admitted-summary",
        "path": "docs/evidence/admitted-results-summary.md",
        "source_kind": "evidence-note",
        "availability_tier": "research-workspace",
        "note": "Human-readable source summary; used only with bundle/score provenance.",
    },
    {
        "provenance_id": "admitted-bundle",
        "path": "workspaces/implementation/artifacts/admitted-evidence-bundle.json",
        "source_kind": "machine-readable-bundle",
        "availability_tier": "research-workspace",
        "note": "Reportable rows, roles, metrics, costs, and finite-tail semantics.",
    },
    {
        "provenance_id": "pia-row-scores",
        "path": "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/adaptive-scores.json",
        "source_kind": "row-score-array",
        "availability_tier": "research-workspace",
        "note": "Direct row scores for PIA metric replay and bootstrap sidecar.",
    },
    {
        "provenance_id": "pia-dropout-row-scores",
        "path": "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/adaptive-scores.json",
        "source_kind": "row-score-array",
        "availability_tier": "research-workspace",
        "note": "Direct row scores for the stochastic-dropout comparator sidecar.",
    },
    {
        "provenance_id": "dpdm-target-scores",
        "path": "workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/scores.json",
        "source_kind": "target-score-array",
        "availability_tier": "research-workspace",
        "note": "Target member/nonmember score arrays for the DPDM W-1 bridge sidecar.",
    },
    {
        "provenance_id": "h2-main",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Main H2 output-cloud candidate metrics and recorded aggregate interval.",
    },
    {
        "provenance_id": "h2-label-shuffle",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "H2 label-shuffle sanity artifact.",
    },
    {
        "provenance_id": "h2-shared-position",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Shared-position seed-offset control for H2.",
    },
    {
        "provenance_id": "h2-shared-position-shuffle",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Shared-position label-shuffle sanity artifact.",
    },
    {
        "provenance_id": "h2-seed177-shared-position",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Seed-177 shared-position stability artifact.",
    },
    {
        "provenance_id": "h2-seed177-shuffle",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Seed-177 label-shuffle sanity artifact.",
    },
    {
        "provenance_id": "h2-transfer",
        "path": "workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Same-family cache-reuse stability artifact.",
    },
    {
        "provenance_id": "h2-img2img-portability",
        "path": "workspaces/black-box/artifacts/h2-img2img-output-cloud-portability-20260525.json",
        "source_kind": "response-metric-artifact",
        "availability_tier": "research-workspace",
        "note": "Negative img2img portability/admission boundary artifact.",
    },
    {
        "provenance_id": "commoncanvas-denoising",
        "path": "workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json",
        "source_kind": "score-packet-artifact",
        "availability_tier": "research-workspace",
        "note": "CommonCanvas 50/50 conditional denoising-loss negative row.",
    },
    {
        "provenance_id": "rediffuse-stl10-bounded-scout",
        "path": "docs/evidence/rediffuse-stl10-bounded-scout-20260525.md",
        "source_kind": "evidence-note",
        "availability_tier": "research-workspace",
        "note": "ReDiffuse STL-10 denoising-loss bounded negative scout.",
    },
    {
        "provenance_id": "rediffuse-stl10-score-norm",
        "path": "docs/evidence/rediffuse-stl10-sima-score-norm-20260525.md",
        "source_kind": "evidence-note",
        "availability_tier": "research-workspace",
        "note": "ReDiffuse STL-10 score-norm bounded negative scout.",
    },
    {
        "provenance_id": "stl10-rediffuse-route-summary",
        "path": "papers/diffaudit-evidence-paper/data/stl10_rediffuse_route_summary.csv",
        "source_kind": "generated-route-summary-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated STL-10 DDIM/ReDiffuse strict-vs-overfit route summary; support/negative only.",
    },
    {
        "provenance_id": "tracing-roots-feature-packet",
        "path": "workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json",
        "source_kind": "feature-packet-artifact",
        "availability_tier": "research-workspace",
        "note": "Positive feature-packet support row with raw-image consumer caveat.",
    },
    {
        "provenance_id": "midst-blending-scout",
        "path": "docs/evidence/midst-blending-plus-plus-scout-20260515.md",
        "source_kind": "evidence-note",
        "availability_tier": "research-workspace",
        "note": "MIDST Blending++ related negative route note.",
    },
    {
        "provenance_id": "sd-rediffuse-collaborator",
        "path": "docs/evidence/stable-diffusion-rediffuse-collaborator-artifact-20260517.md",
        "source_kind": "evidence-note",
        "availability_tier": "research-workspace",
        "note": "Separately supplied Stable Diffusion ReDiffuse packet with source-confounding caveat.",
    },
    {
        "provenance_id": "mofit-public-score-preflight",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_mofit_public_score_surface_preflight_2026_06_08.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "MoFit public COCO score replay and admission-boundary note; support-only and all six gates non-Pass.",
    },
    {
        "provenance_id": "mofit-public-replay-script",
        "path": "scripts/replay_mofit_public_coco_scores.py",
        "source_kind": "network-replay-verifier",
        "availability_tier": "research-workspace",
        "note": "Small-file public MoFit verifier; fetches four official COCO score text files plus two caption JSONL files, recomputes metrics, and can emit audit outputs.",
    },
    {
        "provenance_id": "mofit-public-score-metrics",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_score_metrics.json",
        "source_kind": "generated-score-audit-json",
        "availability_tier": "paper-workspace",
        "note": "MoFit best metrics, low-FPR denominator note, bootstrap CI, permutation null, and file metadata; support-only and all six gates non-Pass.",
    },
    {
        "provenance_id": "mofit-public-score-alpha-sweep",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_score_alpha_sweep.csv",
        "source_kind": "generated-score-audit-csv",
        "availability_tier": "paper-workspace",
        "note": "MoFit alpha sweep with finite low-FPR denominator columns; support-only and all six gates non-Pass.",
    },
    {
        "provenance_id": "mofit-public-score-file-manifest",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_score_file_manifest.csv",
        "source_kind": "generated-public-file-manifest",
        "availability_tier": "paper-workspace",
        "note": "MoFit public score-file size/hash/shape and row-order anchor hashes with sanitized header preview.",
    },
    {
        "provenance_id": "mofit-public-score-roc",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_score_roc.csv",
        "source_kind": "generated-score-audit-csv",
        "availability_tier": "paper-workspace",
        "note": "MoFit best-alpha threshold/ROC rows; support-only and all six gates non-Pass.",
    },
    {
        "provenance_id": "mofit-public-score-position-manifest",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_score_position_manifest.csv",
        "source_kind": "generated-position-manifest",
        "availability_tier": "paper-workspace",
        "note": "Implicit file-position manifest for MoFit train/test rows; not explicit public row IDs or admitted row binding.",
    },
    {
        "provenance_id": "mofit-public-gate-status",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_gate_status.csv",
        "source_kind": "generated-gate-status",
        "availability_tier": "paper-workspace",
        "note": "Machine-readable six-gate status for the MoFit public score-surface replay; support-only and all six gates non-Pass.",
    },
    {
        "provenance_id": "mofit-public-caption-position-manifest",
        "path": "papers/diffaudit-evidence-paper/data/mofit_public_caption_position_manifest.csv",
        "source_kind": "generated-support-position-manifest",
        "availability_tier": "paper-workspace",
        "note": "Support-only caption-order anchors for MoFit score positions; not certified row binding or admitted evidence.",
    },
    {
        "provenance_id": "c14-e2-external-adjudication-preregistration",
        "path": "docs/internal/c14-e2-external-adjudication-preregistration-2026-06-09.md",
        "source_kind": "internal-preregistration",
        "availability_tier": "research-workspace",
        "note": "C14/E2 pre-label preregistration; pre_label_preregistered, prepared_no_reviewer_csvs, n_reviewers=0, packet_ready_only, reviewer ZIP 105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4, post-label key path and sha256 sidecar frozen outside self-referential source_provenance hashing, not external label result, and not report completed external adjudication.",
    },
    {
        "provenance_id": "sama-dlm-public-surface-check",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct031_sama_dlm_public_surface_check_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "SAMA DLM public-code route check; support-only, no_compute_release, not a second public score/response asset, and outside the image-diffusion denominator lane.",
    },
    {
        "provenance_id": "miaept-tabular-public-surface-check",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct032_miaept_tabular_public_surface_check_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "MIA-EPT tabular public-result-page route check; support-only, no_compute_release, not a second public score/response asset, and missing row-bound score/prediction packet.",
    },
    {
        "provenance_id": "diffusion-mia-public-surface-check",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct033_diffusion_mia_public_surface_check_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "Diffusion MIA public code-and-split route check; support-only, no_compute_release, not a second public score/response asset, and missing row-bound result/verifier packet.",
    },
    {
        "provenance_id": "remia-tabular-public-result-archive-check",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "ReMIA tabular public result-archive route check; support-only, no_compute_release, not a second public score/response asset, and aggregate JSON only.",
    },
    {
        "provenance_id": "e2-high-value-delta-refresh",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "High-value public asset delta refresh with git-tree fallback; identity_matched for 9/9 rows, priority_gate_review for all rows, filename_hint_manual_gate_review_needed for CopyMark and MoFit, and no C14/N50 update, no admitted evidence, no second public score/response asset, and no compute release.",
    },
    {
        "provenance_id": "e2-high-value-delta-refresh-csv",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.csv",
        "source_kind": "internal-preflight-table",
        "availability_tier": "research-workspace",
        "note": "Machine-readable high-value public asset delta refresh; 9/9 identity_matched rows, priority_gate_review rows, filename_hint_manual_gate_review_needed rows, and no_compact_reopen_surface_hint rows remain manual-review metadata only.",
    },
    {
        "provenance_id": "e2-high-value-delta-watchlist",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_watchlist_2026_06_09.csv",
        "source_kind": "internal-preflight-watchlist",
        "availability_tier": "research-workspace",
        "note": "Watchlist input for the high-value public asset delta refresh; source-refresh hygiene only, not prevalence, denominator, admitted-evidence, or compute-release evidence.",
    },
    {
        "provenance_id": "e2-high-value-delta-gate-queue",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv",
        "source_kind": "internal-preflight-queue",
        "availability_tier": "research-workspace",
        "note": "Follow-up queue for priority_gate_review rows; check whether public surfaces expose row-bound packets, with support-only and C14-v2 candidate only rows still outside admitted evidence.",
    },
    {
        "provenance_id": "openlvlm-vlm-public-surface-check",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md",
        "source_kind": "internal-preflight-note",
        "availability_tier": "research-workspace",
        "note": "OpenLVLM-MIA VLM controlled-benchmark scout; future VLM stratum only, not current Direction A image-diffusion evidence, not C14/N50, not a second public score/response asset, no_compute_release.",
    },
    {
        "provenance_id": "openlvlm-vlm-public-surface-csv",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.csv",
        "source_kind": "internal-preflight-table",
        "availability_tier": "research-workspace",
        "note": "Machine-readable OpenLVLM-MIA gate readout; public labels/model/code with runtime score outputs only, wrong current consumer lane, no C14/N50/admitted-evidence/second-public-asset/compute-release upgrade.",
    },
    {
        "provenance_id": "negative-support-curated",
        "path": "papers/diffaudit-evidence-paper/data/negative_support_curated_metrics.csv",
        "source_kind": "curated-metric-csv",
        "availability_tier": "paper-workspace",
        "note": "Curated metric constants mirrored from frozen evidence notes.",
    },
    {
        "provenance_id": "artifact-corpus-v1",
        "path": "papers/diffaudit-evidence-paper/data/artifact_corpus_v1.csv",
        "source_kind": "curated-corpus-csv",
        "availability_tier": "paper-workspace",
        "note": "Selected v1 evidence-note corpus; not a prevalence sample.",
    },
    {
        "provenance_id": "artifact-fixed-search",
        "path": "papers/diffaudit-evidence-paper/data/artifact_corpus_fixed_search_20260526.csv",
        "source_kind": "curated-corpus-csv",
        "availability_tier": "paper-workspace",
        "note": "Small fixed-source metadata/search batch; not a field-wide denominator.",
    },
    {
        "provenance_id": "artifact-broader-source",
        "path": "papers/diffaudit-evidence-paper/data/artifact_corpus_broader_source_20260527.csv",
        "source_kind": "curated-corpus-csv",
        "availability_tier": "paper-workspace",
        "note": "No-download HF/Zenodo/OpenReview metadata-screening/query pass; does not support source-completeness or prevalence claims.",
    },
    {
        "provenance_id": "artifact-targeted-link",
        "path": "papers/diffaudit-evidence-paper/data/artifact_corpus_targeted_artifact_links_20260527.csv",
        "source_kind": "curated-corpus-csv",
        "availability_tier": "paper-workspace",
        "note": "Targeted L1 artifact-link pass; not score replay or a pooled denominator.",
    },
    {
        "provenance_id": "artifact-second-pass",
        "path": "papers/diffaudit-evidence-paper/data/artifact_second_pass_label_review_20260526.csv",
        "source_kind": "curated-review-csv",
        "availability_tier": "paper-workspace",
        "note": "Same-team label-hygiene review and resolution record.",
    },
    {
        "provenance_id": "e2-false-promotion-summary",
        "path": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_false_promotion_exemplar_summary_2026_06_07.csv",
        "source_kind": "internal-preflight-csv",
        "availability_tier": "research-workspace",
        "note": "Thirteen no-download E2 false-promotion exemplars; not N50 denominator or admitted evidence.",
    },
    {
        "provenance_id": "admitted-rows-csv",
        "path": "papers/diffaudit-evidence-paper/data/admitted_rows.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated role/replay-tier inventory for reportable rows.",
    },
    {
        "provenance_id": "metric-uncertainty-csv",
        "path": "papers/diffaudit-evidence-paper/data/metric_uncertainty.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated AUC uncertainty sidecar with replay/recording provenance.",
    },
    {
        "provenance_id": "h2-output-cloud-rows-csv",
        "path": "papers/diffaudit-evidence-paper/data/h2_output_cloud_rows.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated H2 candidate/control metric rows used by the H2 figure.",
    },
    {
        "provenance_id": "negative-support-rows-csv",
        "path": "papers/diffaudit-evidence-paper/data/negative_support_rows.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated negative/support rows for route-selection evidence.",
    },
    {
        "provenance_id": "artifact-gate-summary-csv",
        "path": "papers/diffaudit-evidence-paper/data/artifact_gate_summary.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated selected-corpus gate counts for claim-control drafting.",
    },
    {
        "provenance_id": "artifact-claim-support-csv",
        "path": "papers/diffaudit-evidence-paper/data/artifact_claim_support_summary.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated L0-L3 claim-support counts for selected-corpus drafting.",
    },
    {
        "provenance_id": "false-promotion-exemplars-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_exemplars.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated weak-rule C14 stress-control rows derived from E2 preflight.",
    },
    {
        "provenance_id": "false-promotion-summary-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_rule_summary.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated weak-rule counts across the thirteen C14 stress-control rows.",
    },
    {
        "provenance_id": "false-promotion-review-packet-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_external_review_packet.csv",
        "source_kind": "generated-review-packet",
        "availability_tier": "paper-workspace",
        "note": "Generated author-keyed external-style row packet for audit/reconciliation; not completed external adjudication.",
    },
    {
        "provenance_id": "false-promotion-blinded-packet-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_blinded_review_packet.csv",
        "source_kind": "generated-review-packet",
        "availability_tier": "paper-workspace",
        "note": "Generated blocker-blinded packet for independent false-promotion labeling.",
    },
    {
        "provenance_id": "false-promotion-adjudication-key-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_adjudication_key.csv",
        "source_kind": "generated-review-key",
        "availability_tier": "paper-workspace",
        "note": "Generated author adjudication key for post-label comparison; not provided as evidence of external labels.",
    },
    {
        "provenance_id": "false-promotion-review-template-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_external_review_template.csv",
        "source_kind": "generated-review-template",
        "availability_tier": "paper-workspace",
        "note": "Blank review-format template for future independent E2 false-promotion recoding.",
    },
    {
        "provenance_id": "false-promotion-row-trace-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_row_trace.csv",
        "source_kind": "generated-review-trace",
        "availability_tier": "paper-workspace",
        "note": "Generated row-level trace from C14 review IDs to public URLs and no-download evidence notes.",
    },
    {
        "provenance_id": "false-promotion-author-gate-matrix-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_author_gate_matrix.csv",
        "source_kind": "generated-author-key",
        "availability_tier": "paper-workspace",
        "note": "Generated author-keyed C14 gate matrix for post-label comparison; not external reviewer labels.",
    },
    {
        "provenance_id": "false-promotion-gate-summary-csv",
        "path": "papers/diffaudit-evidence-paper/data/false_promotion_gate_summary.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated C14 author-gate outcome counts for matrix QA; not prevalence evidence.",
    },
    {
        "provenance_id": "manuscript-claim-audit-csv",
        "path": "papers/diffaudit-evidence-paper/data/manuscript_claim_audit.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated manuscript claim-anchor audit tying high-risk paper statements to data sidecars.",
    },
    {
        "provenance_id": "citation-context-audit-csv",
        "path": "papers/diffaudit-evidence-paper/data/citation_context_audit.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated citation-context inventory tying every main.tex citation command to expected source support; metadata-verified context audit only, not full-text L3 adjudication.",
    },
    {
        "provenance_id": "report-correctness-fault-csv",
        "path": "papers/diffaudit-evidence-paper/data/report_correctness_fault_injection.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated release-wording fault matrix for selected renderer and phrase-guard checks.",
    },
    {
        "provenance_id": "report-correctness-fault-md",
        "path": "papers/diffaudit-evidence-paper/versions/direction-d-report-correctness-fault-injection.md",
        "source_kind": "paper-source-note",
        "availability_tier": "paper-workspace",
        "note": "Version note describing the release-wording fault matrix and its non-deployment claim boundary.",
    },
    {
        "provenance_id": "false-promotion-codebook-md",
        "path": "papers/diffaudit-evidence-paper/versions/direction-a-false-promotion-audit-codebook.md",
        "source_kind": "paper-source-codebook",
        "availability_tier": "paper-workspace",
        "note": "External-style false-promotion audit codebook; protocol only, not completed adjudication.",
    },
    {
        "provenance_id": "claim-trace-csv",
        "path": "papers/diffaudit-evidence-paper/data/claim_trace.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated per-claim trace records used to operationalize the measurement task.",
    },
    {
        "provenance_id": "claim-transition-examples-csv",
        "path": "papers/diffaudit-evidence-paper/data/claim_transition_examples.csv",
        "source_kind": "generated-csv",
        "availability_tier": "paper-workspace",
        "note": "Generated reader-facing slice of representative claim-state transitions derived from claim_trace.csv.",
    },
]
CLAIM_TRACE_ROWS = [
    {
        "claim_id": "C1",
        "claim_summary": "Five heterogeneous diffusion privacy audit rows can be reported under one evidence contract with explicit replay strength.",
        "source_artifact": "admitted-results-summary; admitted-evidence-bundle; admitted_rows.csv",
        "provenance_ids": "admitted-summary;admitted-bundle;admitted-rows-csv",
        "replay_tier": "mixed: row-score-replay; target-score-replay; source-documented-point-estimate",
        "availability_tier": "research-workspace + paper-workspace",
        "trace_type": "bundle",
        "target_gate": "Pass",
        "split_gate": "Pass",
        "evidence_gate": "Pass",
        "metric_gate": "Pass",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "",
        "gate_note": "Mixed replay strength; source-documented point rows support only exact point wording.",
        "evidence_state": "reportable mixed-strength bundle",
        "allowed_wording": "Five rows are reportable only under their stated access modes, roles, and replay tiers; point estimates are not replay-admitted.",
    },
    {
        "claim_id": "C2",
        "claim_summary": "The reportable bundle separates evidence roles and does not rank access modes.",
        "source_artifact": "admitted-evidence-bundle; admitted_rows.csv",
        "provenance_ids": "admitted-bundle;admitted-rows-csv",
        "replay_tier": "mixed by row",
        "availability_tier": "research-workspace + paper-workspace",
        "trace_type": "bundle",
        "target_gate": "Pass",
        "split_gate": "Pass",
        "evidence_gate": "Pass",
        "metric_gate": "Pass",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "",
        "gate_note": "Role-separated reportability; point rows do not support intervals or dominance.",
        "evidence_state": "role-separated reportable inventory",
        "allowed_wording": "Use as access/role inventory; do not rank access modes or claim statistical dominance.",
    },
    {
        "claim_id": "C3",
        "claim_summary": "H2 output-cloud is a candidate-only admission stress test, not an admitted attack.",
        "source_artifact": "H2 main, controls, cache-robustness, and img2img portability artifacts",
        "provenance_ids": "h2-main;h2-label-shuffle;h2-shared-position;h2-seed177-shared-position;h2-transfer;h2-img2img-portability;h2-output-cloud-rows-csv",
        "replay_tier": "response/feature replay from frozen aggregate artifacts",
        "availability_tier": "research-workspace",
        "trace_type": "packet",
        "target_gate": "Pass",
        "split_gate": "Pass",
        "evidence_gate": "Pass",
        "metric_gate": "Pass",
        "boundary_gate": "Fail",
        "delta_gate": "Fail",
        "first_blocker": "consumer boundary and img2img portability",
        "gate_note": "H2-family metrics are recorded, but the packet is not admitted for consumer reporting or portability.",
        "evidence_state": "candidate failed-admission stress test",
        "allowed_wording": "Same-family H2 candidate evidence only; not admitted for consumer reporting or portability by default.",
    },
    {
        "claim_id": "C4",
        "claim_summary": "H2 same-family controls support stability evidence but not cross-model portability.",
        "source_artifact": "H2 shared-position, seed-stability, and cache-robustness artifacts",
        "provenance_ids": "h2-shared-position;h2-shared-position-shuffle;h2-seed177-shared-position;h2-seed177-shuffle;h2-transfer;h2-output-cloud-rows-csv",
        "replay_tier": "response/feature replay from frozen aggregate artifacts",
        "availability_tier": "research-workspace",
        "trace_type": "packet",
        "target_gate": "Pass",
        "split_gate": "Pass",
        "evidence_gate": "Pass",
        "metric_gate": "Pass",
        "boundary_gate": "Partial",
        "delta_gate": "Fail",
        "first_blocker": "non-adjacent model/data response asset",
        "gate_note": "Same-family controls support within-family stability, not cross-model portability.",
        "evidence_state": "same-family stability support",
        "allowed_wording": "Same-family stability evidence only; no cross-model or cross-dataset portability claim.",
    },
    {
        "claim_id": "C5",
        "claim_summary": "Blocked second-asset and public-surface routes are route-selection evidence, not universal negative claims.",
        "source_artifact": "negative_support_rows.csv, source-provenance sidecars, and evidence notes",
        "provenance_ids": "negative-support-curated;negative-support-rows-csv;rediffuse-stl10-bounded-scout;rediffuse-stl10-score-norm;stl10-rediffuse-route-summary;commoncanvas-denoising;tracing-roots-feature-packet;midst-blending-scout;sd-rediffuse-collaborator;mofit-public-score-preflight;mofit-public-replay-script;mofit-public-score-metrics;mofit-public-gate-status;mofit-public-caption-position-manifest;c14-e2-external-adjudication-preregistration;sama-dlm-public-surface-check;miaept-tabular-public-surface-check;diffusion-mia-public-surface-check;remia-tabular-public-result-archive-check;openlvlm-vlm-public-surface-check;openlvlm-vlm-public-surface-csv;e2-high-value-delta-refresh;e2-high-value-delta-refresh-csv;e2-high-value-delta-watchlist;e2-high-value-delta-gate-queue;artifact-corpus-v1;artifact-fixed-search",
        "replay_tier": "mixed: metadata, support, scoreable, or negative",
        "availability_tier": "paper-workspace + research-workspace",
        "trace_type": "aggregate",
        "target_gate": "Partial",
        "split_gate": "Partial",
        "evidence_gate": "Partial",
        "metric_gate": "Partial",
        "boundary_gate": "Partial",
        "delta_gate": "Partial",
        "first_blocker": "route-specific target, split, metric, consumer, or delta gate",
        "gate_note": "Aggregate route-selection claim; score-bearing rows, source-provenance sidecars, and evidence notes retain separate gates.",
        "evidence_state": "support/negative route-selection and public-surface boundary evidence",
        "allowed_wording": "Use to explain route decisions and public-surface blockers; do not claim all such methods fail or promote sidecars into metric rows.",
    },
    {
        "claim_id": "C6",
        "claim_summary": "Direction C v1 structures 21 selected evidence-note surfaces into artifact strata and gate labels.",
        "source_artifact": "artifact_corpus_v1.csv; direction-c-corpus-v1.md",
        "provenance_ids": "artifact-corpus-v1",
        "replay_tier": "selected-corpus metadata and mixed evidence levels",
        "availability_tier": "paper-workspace",
        "trace_type": "selected-corpus",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "N/A",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "selected corpus, not prevalence sample",
        "gate_note": "Trace covers corpus structure, not admission of every row.",
        "evidence_state": "claim-support taxonomy evidence",
        "allowed_wording": "Structured selected starter corpus; not field-wide prevalence.",
    },
    {
        "claim_id": "C7",
        "claim_summary": "The fixed-search batch is metadata-only selection-process evidence.",
        "source_artifact": "artifact_corpus_fixed_search_20260526.csv; direction-c-fixed-search-batch-20260526.md",
        "provenance_ids": "artifact-fixed-search",
        "replay_tier": "metadata-only",
        "availability_tier": "paper-workspace",
        "trace_type": "metadata-batch",
        "target_gate": "Fail",
        "split_gate": "Fail",
        "evidence_gate": "Fail",
        "metric_gate": "Fail",
        "boundary_gate": "Fail",
        "delta_gate": "N/A",
        "first_blocker": "target/split/evidence/metric surfaces absent",
        "gate_note": "No metadata-only fixed-search row is promoted into an admitted audit row.",
        "evidence_state": "metadata process trace",
        "allowed_wording": "No new admitted row in this frozen batch; no field-wide prevalence or reliability claim.",
    },
    {
        "claim_id": "C8",
        "claim_summary": "Selected corpora can be summarized as gate-label counts for claim-control drafting.",
        "source_artifact": "artifact_gate_summary.csv; artifact_gate_summary.pdf",
        "provenance_ids": "artifact-gate-summary-csv",
        "replay_tier": "generated selected-corpus summary",
        "availability_tier": "paper-workspace",
        "trace_type": "summary",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "N/A",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "selected-corpus denominator",
        "gate_note": "Summary counts inherit selected-corpus boundaries.",
        "evidence_state": "claim-control summary",
        "allowed_wording": "Counts describe only coded rows in selected corpora.",
    },
    {
        "claim_id": "C9",
        "claim_summary": "Direction C rows support different L0-L3 claim-support levels.",
        "source_artifact": "direction-c brief and manuscript draft",
        "provenance_ids": "artifact-corpus-v1;artifact-fixed-search;artifact-gate-summary-csv;artifact-claim-support-csv",
        "replay_tier": "taxonomy over selected-corpus evidence levels",
        "availability_tier": "paper-workspace",
        "trace_type": "taxonomy",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "N/A",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "mixed strata cannot be pooled",
        "gate_note": "Taxonomy claim; individual corpus rows retain their own gate labels.",
        "evidence_state": "same-team taxonomy evidence",
        "allowed_wording": "Separate metadata, artifact inspection, score/replay, and admitted evidence; no pooled reproducibility denominator.",
    },
    {
        "claim_id": "C10",
        "claim_summary": "The bounded second-pass review found no admitted-like fixed-search row and adopted two tightenings.",
        "source_artifact": "direction-c-second-pass-label-review-20260526.md; artifact_second_pass_label_review_20260526.csv",
        "provenance_ids": "artifact-second-pass",
        "replay_tier": "same-team label-hygiene review",
        "availability_tier": "paper-workspace",
        "trace_type": "review-trace",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "N/A",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "not independent human reliability",
        "gate_note": "Internal QA trace; not a coding-reliability protocol.",
        "evidence_state": "internal label hygiene",
        "allowed_wording": "Use as QA/resolution trace; not inter-rater reliability or prevalence evidence.",
    },
    {
        "claim_id": "C11",
        "claim_summary": "AUC uncertainty is reported only for rows with direct score arrays or recorded H2 aggregate intervals.",
        "source_artifact": "metric_uncertainty.csv",
        "provenance_ids": "metric-uncertainty-csv;pia-row-scores;pia-dropout-row-scores;dpdm-target-scores;h2-main;h2-shared-position;h2-seed177-shared-position;h2-transfer",
        "replay_tier": "row-score bootstrap; target-score bootstrap; recorded candidate aggregate interval",
        "availability_tier": "paper-workspace + research-workspace",
        "trace_type": "uncertainty-sidecar",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "Pass",
        "boundary_gate": "Pass",
        "delta_gate": "N/A",
        "first_blocker": "no direct score array or only candidate aggregate interval",
        "gate_note": "Intervals apply only to eligible uncertainty claims, not every reportable row.",
        "evidence_state": "uncertainty sidecar",
        "allowed_wording": "Intervals are sidecar provenance only; no p-values, dominance, or admission upgrade.",
    },
    {
        "claim_id": "C12",
        "claim_summary": "The broader source pass adds no-download HF, Zenodo, and OpenReview metadata-screening/query hygiene without adding admitted rows.",
        "source_artifact": "artifact_corpus_broader_source_20260527.csv; direction-c-broader-source-pass-20260527.md",
        "provenance_ids": "artifact-broader-source",
        "replay_tier": "metadata-only query hygiene",
        "availability_tier": "paper-workspace",
        "trace_type": "metadata-batch",
        "target_gate": "Fail",
        "split_gate": "Fail",
        "evidence_gate": "Fail",
        "metric_gate": "Fail",
        "boundary_gate": "Fail",
        "delta_gate": "Partial",
        "first_blocker": "no new row-bound public score or response packet",
        "gate_note": "API metadata pass; titled OpenReview hit duplicates a fixed-search arXiv row.",
        "evidence_state": "metadata-screening query hygiene",
        "allowed_wording": "Use as no-download metadata-screening/query hygiene only; not field prevalence, replayability, or reliability evidence.",
    },
    {
        "claim_id": "C13",
        "claim_summary": "The targeted artifact-link pass recovers three non-pooled L1 public artifact surfaces from existing metadata-only rows.",
        "source_artifact": "artifact_corpus_targeted_artifact_links_20260527.csv; direction-c-targeted-artifact-link-pass-20260527.md",
        "provenance_ids": "artifact-targeted-link",
        "replay_tier": "L1 artifact inspection; no score replay",
        "availability_tier": "paper-workspace",
        "trace_type": "targeted-artifact-link",
        "target_gate": "Partial",
        "split_gate": "Partial",
        "evidence_gate": "Partial",
        "metric_gate": "Fail",
        "boundary_gate": "Partial",
        "delta_gate": "Pass",
        "first_blocker": "no row-score, response/feature packet, ROC, metric JSON, checkpoint hash, or verifier packet",
        "gate_note": "Targeted pass recovered one HF dataset split artifact, one official SecMI code/split tree, and one official MIDM code/protocol surface; no downloads or clones.",
        "evidence_state": "non-pooled L1 artifact inspection",
        "allowed_wording": "Use as targeted L1 inspection evidence only; not score replay, metric reproduction, admission, prevalence, or pooled denominator.",
    },
    {
        "claim_id": "C14",
        "claim_summary": "Thirteen E2 public surfaces form a pre-label stress-control packet for weak-rule comparison.",
        "source_artifact": (
            "e2_false_promotion_exemplar_summary_2026_06_07.csv; false_promotion_exemplars.csv; "
            "false_promotion_external_review_packet.csv; false_promotion_blinded_review_packet.csv; "
            "false_promotion_adjudication_key.csv; false_promotion_external_review_template.csv; "
            "false_promotion_row_trace.csv; "
            "false_promotion_author_gate_matrix.csv; false_promotion_gate_summary.csv; "
            "direction-a-false-promotion-audit-codebook.md"
        ),
        "provenance_ids": (
            "e2-false-promotion-summary;false-promotion-exemplars-csv;false-promotion-summary-csv;"
            "false-promotion-review-packet-csv;false-promotion-blinded-packet-csv;"
            "false-promotion-adjudication-key-csv;false-promotion-review-template-csv;"
            "false-promotion-row-trace-csv;false-promotion-author-gate-matrix-csv;"
            "false-promotion-gate-summary-csv;false-promotion-codebook-md"
        ),
        "replay_tier": "no-download public-surface classification; no score replay",
        "availability_tier": "research-workspace + paper-workspace",
        "trace_type": "prelabel-stress-control",
        "target_gate": "Partial",
        "split_gate": "Partial",
        "evidence_gate": "Partial",
        "metric_gate": "Partial",
        "boundary_gate": "Fail",
        "delta_gate": "N/A",
        "first_blocker": "weak public surfaces lack the target-bound response/score packet, metric packet, or per-sample membership consumer boundary required for the promoted claim",
        "gate_note": "Rows test weak promotion rules plus semantic and consumer-boundary errors; none becomes N50 denominator, admitted evidence, or compute release.",
        "evidence_state": "pre-label stress-control object",
        "allowed_wording": "Use as weak-rule, semantic-boundary, and consumer-boundary stress-control examples only; not external adjudication evidence, admitted response/score evidence, or a denominator.",
    },
    {
        "claim_id": "C15",
        "claim_summary": "The release-wording regression matrix checks selected renderer and phrase-guard failure modes.",
        "source_artifact": "report_correctness_fault_injection.csv; direction-d-report-correctness-fault-injection.md",
        "provenance_ids": "report-correctness-fault-csv;report-correctness-fault-md;manuscript-claim-audit-csv",
        "replay_tier": "release-packet regression checks; no deployment evidence",
        "availability_tier": "paper-workspace",
        "trace_type": "release-wording-check",
        "target_gate": "N/A",
        "split_gate": "N/A",
        "evidence_gate": "Pass",
        "metric_gate": "N/A",
        "boundary_gate": "Partial",
        "delta_gate": "N/A",
        "first_blocker": "no external-use, deployment, report-drift, or reviewer-reliability evidence",
        "gate_note": "Twenty-eight selected renderer and direct phrase-scan cases matched their specified rule labels; this is release-packet QA, not systems effectiveness evidence.",
        "evidence_state": "release-wording sanity packet",
        "allowed_wording": "Use as selected release renderer and phrase-guard QA only; not report-drift reduction, external-use, deployment, user-impact, or reviewer-reliability evidence.",
    },
]


def read_json(path: str) -> dict:
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def metric_row(source: str, label: str, role: str, metrics: dict) -> dict:
    return {
        "source": source,
        "label": label,
        "role": role,
        "auc": metrics["auc"],
        "asr": metrics["asr"],
        "tpr_at_1pct_fpr": metrics["tpr_at_1pct_fpr"],
        "tpr_at_0_1pct_fpr": metrics["tpr_at_0_1pct_fpr"],
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def git_tree_state() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return "dirty" if result.stdout.strip() else "clean"


def git_status_for_path(rel_path: str) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", rel_path],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    lines = [line[:2].strip() or "tracked-clean" for line in result.stdout.splitlines() if line.strip()]
    return "|".join(lines) if lines else "not-reported-by-git-status"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_source_provenance_rows() -> list[dict]:
    commit = git_head()
    tree_state = git_tree_state()
    rows = []
    for item in PROVENANCE_SOURCE_ITEMS:
        path = ROOT / item["path"]
        exists = path.exists()
        rows.append(
            {
                "provenance_id": item["provenance_id"],
                "path": item["path"],
                "source_kind": item["source_kind"],
                "availability_tier": item["availability_tier"],
                "sha256": sha256_file(path) if exists else "",
                "repo_commit": commit,
                "repo_tree_state": tree_state,
                "generator_command": GENERATOR_COMMAND,
                "exists": str(exists).lower(),
                "note": item["note"],
            }
        )
    return rows


def build_review_snapshot_rows(asset_manifest_sha256: str) -> list[dict]:
    """Record local review-packet identity without upgrading it to clean provenance."""

    commit = git_head()
    tree_state = git_tree_state()
    generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    generator_script = "papers/diffaudit-evidence-paper/scripts/build_paper_assets.py"
    release_checker_script = "scripts/check_paper_release_packet.py"
    source_provenance = DATA / "source_provenance.csv"
    claim_trace = DATA / "claim_trace.csv"
    paper_pdf = PAPER / "paper.pdf"
    shared_metadata = {
        "schema_version": REVIEW_SNAPSHOT_SCHEMA_VERSION,
        "snapshot_kind": REVIEW_SNAPSHOT_KIND,
        "scope": REVIEW_SNAPSHOT_SCOPE,
        "generated_at_utc": generated_at_utc,
        "repo_head": commit,
        "repo_tree_state": tree_state,
        "generator_command": GENERATOR_COMMAND,
        "generator_script_sha256": sha256_file(ROOT / generator_script),
        "release_checker_script_sha256": sha256_file(ROOT / release_checker_script),
        "asset_manifest_sha256": asset_manifest_sha256,
        "source_provenance_sha256": sha256_file(source_provenance),
        "claim_trace_sha256": sha256_file(claim_trace),
        "paper_pdf_sha256": sha256_file(paper_pdf) if paper_pdf.exists() else "",
        "excluded_public_claims": REVIEW_SNAPSHOT_EXCLUDED_PUBLIC_CLAIMS,
    }
    requested: list[tuple[str, str]] = []
    for category, paths in [
        ("generated", GENERATED_MANIFEST_PATHS),
        ("curated", CURATED_MANIFEST_PATHS),
        ("paper_sources", PAPER_SOURCE_MANIFEST_PATHS),
        ("repo_sources", REVIEW_SNAPSHOT_REPO_SOURCE_PATHS),
    ]:
        requested.extend(
            (category, path)
            for path in paths
            if path != "data/review_snapshot_manifest.csv" and path not in ANONYMOUS_SUPPLEMENT_EXCLUDED_PATHS
        )
    requested.extend(
        [
            ("release_file", "asset_manifest.json"),
            ("release_file", "paper.pdf"),
        ]
    )

    rows: list[dict] = []
    seen: set[str] = set()
    for category, rel_path in requested:
        if rel_path in seen:
            continue
        seen.add(rel_path)
        if category == "repo_sources":
            path = ROOT / rel_path
            status_path = rel_path
        else:
            path = ROOT / "papers" / "diffaudit-evidence-paper" / rel_path
            if category == "curated" and not path.exists():
                path = PAPER / rel_path
            status_path = f"papers/diffaudit-evidence-paper/{rel_path}"
        exists = path.exists()
        rows.append(
            {
                **shared_metadata,
                "manifest_category": category,
                "relative_path": rel_path,
                "exists": str(exists).lower(),
                "git_status": git_status_for_path(status_path),
                "size_bytes": str(path.stat().st_size) if exists else "",
                "sha256": sha256_file(path) if exists else "",
                "snapshot_role": "local-review-packet-identity",
                "boundary_note": REVIEW_SNAPSHOT_BOUNDARY_NOTE,
            }
        )
    return rows


def build_claim_trace_rows() -> list[dict]:
    return CLAIM_TRACE_ROWS


def build_claim_transition_examples(claim_rows: list[dict]) -> list[dict]:
    selected_claims = ("C1", "C3", "C11", "C14", "C15")
    rows_by_id = {row["claim_id"]: row for row in claim_rows}
    examples: list[dict] = []
    for claim_id in selected_claims:
        row = rows_by_id[claim_id]
        examples.append(
            {
                "claim_id": row["claim_id"],
                "trace_type": row["trace_type"],
                "evidence_state": row["evidence_state"],
                "first_blocker": row["first_blocker"],
                "replay_tier": row["replay_tier"],
                "allowed_wording": row["allowed_wording"],
                "provenance_ids": row["provenance_ids"],
            }
        )
    return examples


def extract_main_tex_citation_contexts() -> list[tuple[int, str]]:
    contexts: list[tuple[int, str]] = []
    cite_re = re.compile(r"\\cite[a-zA-Z*]*\{([^}]*)\}")
    tex_text = (PAPER / "main.tex").read_text(encoding="utf-8")
    for line_no, line in enumerate(tex_text.splitlines(), start=1):
        for match in cite_re.finditer(line):
            keys = ";".join(key.strip() for key in match.group(1).split(",") if key.strip())
            contexts.append((line_no, keys))
    return contexts


def build_citation_context_audit_rows() -> list[dict]:
    """Inventory every manuscript citation command and its intended support role.

    This is a citation-context audit, not a full-text L3 adjudication. It gives
    reviewers a deterministic map from cited prose to the source role that must
    be checked against the reference text.
    """

    source_status = "metadata_verified; full-text L3 pending"
    status = "pass_context_inventory"
    rows = [
        {
            "citation_id": "CCA-001",
            "main_tex_line": 47,
            "paper_section": "Introduction",
            "cited_keys": "carlini2023extracting;somepalli2023replication",
            "claim_text_anchor": "Diffusion models can memorize or replicate training examples in ways that enable membership inference attacks",
            "expected_source_support": "Diffusion memorization, extraction, and replication risk in generated outputs.",
            "manuscript_claim_role": "background-risk-motivation",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Background support only; does not establish DiffAudit row admission or field-wide prevalence.",
        },
        {
            "citation_id": "CCA-002",
            "main_tex_line": 52,
            "paper_section": "Introduction",
            "cited_keys": "duan2023secmi;kong2024pia;zha2024clid;reconstruction2025blackbox;gsa2025whitebox",
            "claim_text_anchor": "black-box, gray-box, and white-box signals",
            "expected_source_support": "Representative diffusion MIA access surfaces and score/gradient/reconstruction signal families.",
            "manuscript_claim_role": "related-work-taxonomy",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Taxonomy support only; not an attack leaderboard or completeness claim.",
        },
        {
            "citation_id": "CCA-003",
            "main_tex_line": 65,
            "paper_section": "Introduction",
            "cited_keys": "herley2017sokscience;vanderkouwe2020benchmarking;pineau2021reproducibility",
            "claim_text_anchor": "security-measurement and reproducibility norms",
            "expected_source_support": "Security-science, benchmarking, and reproducibility work motivate explicit evidence units, assumptions, and repeatable comparisons.",
            "manuscript_claim_role": "measurement-norm-framing",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Normative framing; does not turn DiffAudit sidecars into external reliability evidence.",
        },
        {
            "citation_id": "CCA-004",
            "main_tex_line": 113,
            "paper_section": "Related Work / Membership Inference and Evidence",
            "cited_keys": "shokri2017membership",
            "claim_text_anchor": "Membership inference asks whether a record was used during training",
            "expected_source_support": "Foundational membership-inference formulation.",
            "manuscript_claim_role": "definition-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Definition support only; no diffusion-specific admission claim.",
        },
        {
            "citation_id": "CCA-005",
            "main_tex_line": 115,
            "paper_section": "Related Work / Membership Inference and Evidence",
            "cited_keys": "yeom2018privacy;carlini2022firstprinciples",
            "claim_text_anchor": "risk to overfitting and to the statistical meaning of membership scores",
            "expected_source_support": "Connections between membership risk, overfitting, base rates, and attack-score interpretation.",
            "manuscript_claim_role": "metric-interpretation-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Metric interpretation support only; finite-tail packet claims remain bounded.",
        },
        {
            "citation_id": "CCA-006",
            "main_tex_line": 117,
            "paper_section": "Related Work / Membership Inference and Evidence",
            "cited_keys": "zhang2025cannotprove",
            "claim_text_anchor": "Training-data-use claims need evidence beyond MIA scores",
            "expected_source_support": "Position claim separating MIA evidence from proof that a specific datum trained a model.",
            "manuscript_claim_role": "claim-boundary-source",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Supports wording boundary; not an empirical validation of DiffAudit gates.",
        },
        {
            "citation_id": "CCA-007",
            "main_tex_line": 121,
            "paper_section": "Related Work / Membership Inference and Evidence",
            "cited_keys": "das2025blind",
            "claim_text_anchor": "blind baselines can outperform MIA attacks when member and nonmember sources differ",
            "expected_source_support": "Foundation-model baseline confounding and source-difference caution.",
            "manuscript_claim_role": "confounding-warning",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Confounding caution only; does not report DiffAudit source-confounding rates.",
        },
        {
            "citation_id": "CCA-008",
            "main_tex_line": 132,
            "paper_section": "Related Work / Security Measurement and Audit Claims",
            "cited_keys": "herley2017sokscience;vanderkouwe2020benchmarking",
            "claim_text_anchor": "scientific security claims require explicit evidence units, denominators, measurement assumptions, and reproducible comparisons",
            "expected_source_support": "Security measurement and benchmarking quality requirements.",
            "manuscript_claim_role": "measurement-validity-framing",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Framing support; DiffAudit claim labels remain same-team protocol labels.",
        },
        {
            "citation_id": "CCA-009",
            "main_tex_line": 135,
            "paper_section": "Related Work / Security Measurement and Audit Claims",
            "cited_keys": "carlini2022firstprinciples",
            "claim_text_anchor": "accuracy and tail rates require careful base-rate and threshold interpretation",
            "expected_source_support": "First-principles treatment of membership attack metrics and low-FPR interpretation.",
            "manuscript_claim_role": "metric-validity-framing",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Metric validity support; does not certify finite-packet calibrated risk.",
        },
        {
            "citation_id": "CCA-010",
            "main_tex_line": 137,
            "paper_section": "Related Work / Security Measurement and Audit Claims",
            "cited_keys": "zhang2025cannotprove",
            "claim_text_anchor": "separate membership evidence from proof of training-data use",
            "expected_source_support": "Audit-oriented distinction between membership inference evidence and training-data-use proof.",
            "manuscript_claim_role": "claim-boundary-source",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Boundary support only; no external adjudication of DiffAudit wording.",
        },
        {
            "citation_id": "CCA-011",
            "main_tex_line": 146,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "ho2020ddpm;rombach2022ldm",
            "claim_text_anchor": "Diffusion models",
            "expected_source_support": "DDPM and latent diffusion model background.",
            "manuscript_claim_role": "model-family-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Architecture background only; no privacy-risk measurement claim.",
        },
        {
            "citation_id": "CCA-012",
            "main_tex_line": 147,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "carlini2023extracting;somepalli2023replication",
            "claim_text_anchor": "memorized generations and membership signals",
            "expected_source_support": "Empirical memorization, extraction, and replication evidence in diffusion outputs.",
            "manuscript_claim_role": "privacy-risk-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Motivates privacy risk; no field-wide leakage estimate.",
        },
        {
            "citation_id": "CCA-013",
            "main_tex_line": 149,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "duan2023secmi;kong2024pia;zha2024clid;tracingroots2025",
            "claim_text_anchor": "gray-box posterior, trajectory, and likelihood surrogates",
            "expected_source_support": "Gray-box diffusion MIA and origin-attribution mechanisms.",
            "manuscript_claim_role": "access-surface-taxonomy",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Taxonomy support; Tracing Roots remains feature-packet support in this paper.",
        },
        {
            "citation_id": "CCA-014",
            "main_tex_line": 150,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "rediffuse2025;reconstruction2025blackbox",
            "claim_text_anchor": "black-box response or reconstruction methods",
            "expected_source_support": "Black-box diffusion MIA methods based on responses or reconstruction comparisons.",
            "manuscript_claim_role": "access-surface-taxonomy",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Taxonomy support; current ReDiffuse rows are route-local, not method refutations.",
        },
        {
            "citation_id": "CCA-015",
            "main_tex_line": 151,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "jeon2026mofit",
            "claim_text_anchor": "caption-free fitted-embedding scores",
            "expected_source_support": "MoFit caption-free fitted-embedding membership-inference setup.",
            "manuscript_claim_role": "support-only-boundary-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "MoFit is cited as a method/background surface; public score-file replay remains support-only.",
        },
        {
            "citation_id": "CCA-016",
            "main_tex_line": 152,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "gsa2025whitebox",
            "claim_text_anchor": "white-box gradient attacks",
            "expected_source_support": "White-box gradient membership inference against diffusion models.",
            "manuscript_claim_role": "access-surface-taxonomy",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "White-box comparator support; no black-box admission follows from this citation.",
        },
        {
            "citation_id": "CCA-017",
            "main_tex_line": 154,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "lian2026noiseprobe",
            "claim_text_anchor": "noise-schedule surfaces",
            "expected_source_support": "Initial-noise probing as an additional diffusion MIA surface.",
            "manuscript_claim_role": "taxonomy-expansion-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Taxonomy expansion only; not included as current admitted evidence.",
        },
        {
            "citation_id": "CCA-018",
            "main_tex_line": 156,
            "paper_section": "Related Work / Diffusion Memorization and MIA",
            "cited_keys": "dockhorn2023private;liang2024copymark;midst2026challenge;dubinski2025cdi",
            "claim_text_anchor": "defense, benchmark, and dataset-level contracts change what a result can mean",
            "expected_source_support": "Examples where defense settings, benchmark contracts, tabular challenge setup, or dataset-level identification alter claim semantics.",
            "manuscript_claim_role": "contract-boundary-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Boundary framing; CopyMark, MIDST, and CDI remain support/route evidence unless row-bound gates pass.",
        },
        {
            "citation_id": "CCA-019",
            "main_tex_line": 161,
            "paper_section": "Related Work / Reporting and Reproducibility Artifacts",
            "cited_keys": "pineau2021reproducibility;gebru2021datasheets;mitchell2019modelcards",
            "claim_text_anchor": "Reproducibility checklists, datasheets, and model cards document data, code, conditions, origins, limitations, and intended use",
            "expected_source_support": "Reproducibility checklist, datasheet, and model-card reporting norms.",
            "manuscript_claim_role": "artifact-reporting-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Reporting-norm support; DiffAudit gates are a project protocol, not an external standard.",
        },
        {
            "citation_id": "CCA-020",
            "main_tex_line": 187,
            "paper_section": "Audit Surfaces",
            "cited_keys": "duan2023secmi;kong2024pia;zha2024clid;rediffuse2025;reconstruction2025blackbox;gsa2025whitebox",
            "claim_text_anchor": "group prior diffusion MIA artifacts by access surface",
            "expected_source_support": "Representative prior artifacts for gray-box, black-box, and white-box grouping.",
            "manuscript_claim_role": "taxonomy-operationalization",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Grouping support only; not a complete literature census.",
        },
        {
            "citation_id": "CCA-021",
            "main_tex_line": 246,
            "paper_section": "Claim-Admission Protocol",
            "cited_keys": "carlini2022firstprinciples",
            "claim_text_anchor": "Low-FPR metrics are reported as finite empirical packet readouts",
            "expected_source_support": "Metric and tail-rate interpretation caution for membership inference.",
            "manuscript_claim_role": "finite-tail-caution",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Supports finite empirical wording; no calibrated population-risk claim.",
        },
        {
            "citation_id": "CCA-022",
            "main_tex_line": 373,
            "paper_section": "Claim-Admission Protocol",
            "cited_keys": "carlini2022firstprinciples",
            "claim_text_anchor": "calibrated-risk language would overstate the measurement resolution",
            "expected_source_support": "Base-rate, threshold, and low-FPR caution motivates bounded packet wording.",
            "manuscript_claim_role": "finite-tail-caution",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Supports cautionary wording only; no new empirical claim.",
        },
        {
            "citation_id": "CCA-023",
            "main_tex_line": 638,
            "paper_section": "Admitted Rows Table",
            "cited_keys": "reconstruction2025blackbox",
            "claim_text_anchor": "recon DDIM public-100 step30",
            "expected_source_support": "Source for the black-box reconstruction row name and method context.",
            "manuscript_claim_role": "row-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Table citation identifies row family; local packet controls the exact reported point wording.",
        },
        {
            "citation_id": "CCA-024",
            "main_tex_line": 641,
            "paper_section": "Admitted Rows Table",
            "cited_keys": "gsa2025whitebox",
            "claim_text_anchor": "GSA 1k-3shadow",
            "expected_source_support": "Source for the white-box GSA row family.",
            "manuscript_claim_role": "row-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "White-box upper-bound comparator; not black-box report evidence.",
        },
        {
            "citation_id": "CCA-025",
            "main_tex_line": 642,
            "paper_section": "Admitted Rows Table",
            "cited_keys": "gsa2025whitebox;dockhorn2023private",
            "claim_text_anchor": "GSA against DPDM W-1",
            "expected_source_support": "Sources for the white-box GSA attack family and the DPDM target/defense setting.",
            "manuscript_claim_role": "row-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Defense bridge row; does not imply defended black-box product readiness.",
        },
        {
            "citation_id": "CCA-026",
            "main_tex_line": 667,
            "paper_section": "Metric-Strength Boundary Case: H2 Output-Cloud",
            "cited_keys": "rediffuse2025;reconstruction2025blackbox",
            "claim_text_anchor": "black-box variation and reconstruction attacks that compare a query with returned or averaged outputs",
            "expected_source_support": "Contrast sources for query-to-output and response/reconstruction black-box attacks.",
            "manuscript_claim_role": "method-contrast-background",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Contrast only; H2 remains candidate-only and non-admitted.",
        },
        {
            "citation_id": "CCA-027",
            "main_tex_line": 724,
            "paper_section": "Negative and Support Evidence",
            "cited_keys": "rediffuse2025",
            "claim_text_anchor": "The routes cover ReDiffuse",
            "expected_source_support": "Source for the ReDiffuse route family.",
            "manuscript_claim_role": "route-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Route-local evidence only; no general ReDiffuse refutation.",
        },
        {
            "citation_id": "CCA-028",
            "main_tex_line": 725,
            "paper_section": "Negative and Support Evidence",
            "cited_keys": "liang2024copymark",
            "claim_text_anchor": "surface associated with CopyMark materials",
            "expected_source_support": "Source for CopyMark/CommonCanvas route materials.",
            "manuscript_claim_role": "route-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Support/route context only; no second admitted public asset.",
        },
        {
            "citation_id": "CCA-029",
            "main_tex_line": 725,
            "paper_section": "Negative and Support Evidence",
            "cited_keys": "midst2026challenge",
            "claim_text_anchor": "MIDST",
            "expected_source_support": "Source for the MIDST tabular synthetic-data challenge route surface.",
            "manuscript_claim_role": "route-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "Tabular route context only; no image-diffusion admitted evidence.",
        },
        {
            "citation_id": "CCA-030",
            "main_tex_line": 726,
            "paper_section": "Negative and Support Evidence",
            "cited_keys": "tracingroots2025",
            "claim_text_anchor": "the Roots",
            "expected_source_support": "Source for the Tracing the Roots feature-packet route.",
            "manuscript_claim_role": "route-source-label",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "feature-packet support only; not raw image-level admitted evidence.",
        },
        {
            "citation_id": "CCA-031",
            "main_tex_line": 727,
            "paper_section": "Negative and Support Evidence",
            "cited_keys": "jeon2026mofit",
            "claim_text_anchor": "score-like text files as a support boundary check",
            "expected_source_support": "Source for MoFit method identity; the public-score-file check is local support-only evidence.",
            "manuscript_claim_role": "support-only-boundary-source",
            "source_content_status": source_status,
            "audit_status": status,
            "boundary_note": "MoFit citation supports method identity only; support-only public score-file check with all admission gates non-Pass in this packet.",
        },
    ]
    contexts = extract_main_tex_citation_contexts()
    if len(contexts) != len(rows):
        raise ValueError(f"citation context row count drifted: {len(rows)} != {len(contexts)}")
    for row, (line_no, cited_keys) in zip(rows, contexts):
        if row["cited_keys"] != cited_keys:
            raise ValueError(
                f"{row['citation_id']} cited_keys drifted: {row['cited_keys']!r} != {cited_keys!r}"
            )
        row["main_tex_line"] = line_no
    return rows


def build_manuscript_claim_audit_rows(
    admitted_rows: list[dict],
    h2_rows: list[dict],
    false_promotion_summary: list[dict],
    false_promotion_gate_summary: list[dict],
) -> list[dict]:
    """Tie high-risk manuscript claims to data sidecars without adding new claims."""

    replay_admitted = sum(row["replay_tier"] in {"row-score-replay", "target-score-replay"} for row in admitted_rows)
    point_estimates = sum(row["replay_tier"] == "source-documented-point-estimate" for row in admitted_rows)
    h2_candidate = next(row for row in h2_rows if row["source"] == "h2-main" and row["label"] == "output-cloud 512/512")
    mofit_best = json.loads((DATA / "mofit_public_score_metrics.json").read_text(encoding="utf-8"))["best"]
    weak_rules = {row["weak_rule"]: row for row in false_promotion_summary}
    gate_counts = {(row["gate"], row["outcome"]): row for row in false_promotion_gate_summary}
    report_correctness_rows = read_csv(DATA / "report_correctness_fault_injection.csv")
    report_correctness_passed = sum(row.get("passed") == "1" for row in report_correctness_rows)

    c14_selected = int(weak_rules["code_availability_would_promote"]["selected_row_count"])
    code_rows = int(weak_rules["code_availability_would_promote"]["would_promote_rows"])
    paper_link_rows = int(weak_rules["paper_claim_artifact_link_would_promote"]["would_promote_rows"])
    score_pass = int(gate_counts[("score_or_response_gate", "Pass")]["count"])
    consumer_pass = int(gate_counts[("consumer_boundary_gate", "Pass")]["count"])

    return [
        {
            "anchor_id": "MCA-001",
            "paper_section": "abstract/contributions",
            "manuscript_required_text": (
                f"three replay-backed rows reportable under bounded wording, two source-documented point rows"
                if replay_admitted == 3 and point_estimates == 2 and len(admitted_rows) == 5
                else "admitted row composition drift"
            ),
            "source_paths": "data/admitted_rows.csv",
            "source_values": f"total={len(admitted_rows)}; replay_admitted={replay_admitted}; source_point={point_estimates}",
            "audit_status": "pass",
            "boundary_note": "composition anchor only; point estimates remain point-worded and are not replay-admitted",
        },
        {
            "anchor_id": "MCA-002",
            "paper_section": "abstract/H2",
            "manuscript_required_text": f"one repeated-response candidate with AUC {float(h2_candidate['auc']):.4f}",
            "source_paths": "data/h2_output_cloud_rows.csv",
            "source_values": f"h2_candidate_auc={float(h2_candidate['auc']):.6f}",
            "audit_status": "pass",
            "boundary_note": "metric anchor only; H2 remains candidate-only and non-admitted",
        },
        {
            "anchor_id": "MCA-003",
            "paper_section": "MoFit",
            "manuscript_required_text": (
                f"AUC {float(mofit_best['auc']):.6f}, ASR {float(mofit_best['best_asr']):.3f}, "
                f"TPR@1%FPR {float(mofit_best['tpr_at_1fpr']):.3f}, and "
                f"TPR@0.1%FPR {float(mofit_best['tpr_at_01fpr']):.3f}"
            ),
            "source_paths": "data/mofit_public_score_metrics.json",
            "source_values": (
                f"auc={float(mofit_best['auc']):.6f}; asr={float(mofit_best['best_asr']):.3f}; "
                f"tpr1={float(mofit_best['tpr_at_1fpr']):.3f}; tpr01={float(mofit_best['tpr_at_01fpr']):.3f}"
            ),
            "audit_status": "pass",
            "boundary_note": "metric anchor only; MoFit remains support-only with all gates non-Pass",
        },
        {
            "anchor_id": "MCA-004",
            "paper_section": "abstract/C14",
            "manuscript_required_text": (
                f"weak public-surface rules would select {code_rows}/{c14_selected} rows by code and paper-artifact links"
            ),
            "source_paths": "data/false_promotion_rule_summary.csv",
            "source_values": f"code={code_rows}; paper_link={paper_link_rows}; selected={c14_selected}",
            "audit_status": "pass",
            "boundary_note": "author-keyed preparation packet only; not prevalence, reliability, or adjudication evidence",
        },
        {
            "anchor_id": "MCA-005",
            "paper_section": "C14",
            "manuscript_required_text": "all selected rows are non-Pass at the score/response and consumer-boundary gates",
            "source_paths": "data/false_promotion_gate_summary.csv",
            "source_values": f"score_or_response_pass={score_pass}; consumer_boundary_pass={consumer_pass}",
            "audit_status": "pass",
            "boundary_note": "author-keyed gate-count anchor only; no external reviewer labels",
        },
        {
            "anchor_id": "MCA-006",
            "paper_section": "contributions/report-correctness",
            "manuscript_required_text": "phrase-guard regression wording",
            "source_paths": "data/report_correctness_fault_injection.csv",
            "source_values": f"cases={len(report_correctness_rows)}; passed={report_correctness_passed}",
            "audit_status": "pass",
            "boundary_note": "fault-injection sanity cases for release wording, not a deployed system effectiveness claim",
        },
    ]


def validate_claim_trace_rows(claim_rows: list[dict], provenance_rows: list[dict]) -> None:
    provenance_ids = {row["provenance_id"] for row in provenance_rows}
    errors: list[str] = []

    for row in claim_rows:
        claim_id = row.get("claim_id", "<missing>")
        for column in TRACE_GATE_COLUMNS:
            value = row.get(column, "")
            if value not in TRACE_GATE_OUTCOMES:
                errors.append(f"{claim_id}: {column}={value!r} is not one of {sorted(TRACE_GATE_OUTCOMES)}")
        for provenance_id in row.get("provenance_ids", "").split(";"):
            provenance_id = provenance_id.strip()
            if provenance_id and provenance_id not in provenance_ids:
                errors.append(f"{claim_id}: missing source_provenance row for {provenance_id!r}")

    for row in provenance_rows:
        if row.get("exists") != "true":
            errors.append(f"{row['provenance_id']}: source path does not exist: {row['path']}")
        if not row.get("sha256"):
            errors.append(f"{row['provenance_id']}: missing sha256 for {row['path']}")
        if not row.get("generator_command"):
            errors.append(f"{row['provenance_id']}: missing generator_command")

    if errors:
        shown = "\n".join(errors[:25])
        if len(errors) > 25:
            shown += f"\n... {len(errors) - 25} more errors"
        raise ValueError(f"claim trace/provenance validation failed:\n{shown}")


def auc_from_scores(member_scores: list[float], nonmember_scores: list[float]) -> float:
    ranked = [(score, 1) for score in member_scores] + [(score, 0) for score in nonmember_scores]
    ranked.sort(key=lambda item: item[0])
    rank_sum = 0.0
    idx = 0
    while idx < len(ranked):
        end = idx + 1
        while end < len(ranked) and ranked[end][0] == ranked[idx][0]:
            end += 1
        avg_rank = (idx + 1 + end) / 2.0
        for row in ranked[idx:end]:
            if row[1] == 1:
                rank_sum += avg_rank
        idx = end
    n_pos = len(member_scores)
    n_neg = len(nonmember_scores)
    return (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot compute percentile of empty values")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return ordered[low]
    weight = pos - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def bootstrap_auc_ci(
    member_scores: list[float],
    nonmember_scores: list[float],
    *,
    seed: int,
    iterations: int = 2000,
) -> tuple[float, float]:
    rng = random.Random(seed)
    n_member = len(member_scores)
    n_nonmember = len(nonmember_scores)
    boot = []
    for _ in range(iterations):
        member_sample = [member_scores[rng.randrange(n_member)] for _ in range(n_member)]
        nonmember_sample = [nonmember_scores[rng.randrange(n_nonmember)] for _ in range(n_nonmember)]
        boot.append(auc_from_scores(member_sample, nonmember_sample))
    return percentile(boot, 0.025), percentile(boot, 0.975)


def uncertainty_row(
    label: str,
    role: str,
    source: str,
    point: float,
    p025: float,
    p975: float,
    method: str,
    member_count: int | str,
    nonmember_count: int | str,
    uncertainty_source: str,
    recomputed_or_recorded: str,
    bootstrap_unit: str,
    score_array_hash: str,
    eligible_claims: str,
    note: str,
) -> dict:
    return {
        "label": label,
        "role": role,
        "metric": "auc",
        "point": round(float(point), 6),
        "p025": round(float(p025), 6),
        "p975": round(float(p975), 6),
        "ci_method": method,
        "member_count": member_count,
        "nonmember_count": nonmember_count,
        "evidence_source": source,
        "uncertainty_source": uncertainty_source,
        "recomputed_or_recorded": recomputed_or_recorded,
        "bootstrap_unit": bootstrap_unit,
        "score_array_hash": score_array_hash,
        "eligible_claims": eligible_claims,
        "note": note,
    }


def build_admitted_rows() -> list[dict]:
    bundle = read_json("workspaces/implementation/artifacts/admitted-evidence-bundle.json")
    rows = []
    for item in bundle["rows"]:
        attack = item["method"]["attack"]
        defense = item["method"]["defense"]
        if item["track"] == "gray-box":
            replay_tier = "row-score-replay"
        elif attack == "GSA 1k-3shadow" and defense != "none":
            replay_tier = "target-score-replay"
        else:
            replay_tier = "source-documented-point-estimate"
        rows.append(
            {
                "label": f"{item['track']}: {item['method']['attack']} / {item['method']['defense']}",
                "track": item["track"],
                "required_access": item.get("required_access", item["track"]),
                "report_role": item.get("report_role", ""),
                "report_role_label": REPORT_ROLE_LABELS.get(item.get("report_role", ""), item.get("report_role", "")),
                "replay_tier": replay_tier,
                "replay_tier_label": REPLAY_TIER_LABELS[replay_tier],
                "attack": item["method"]["attack"],
                "defense": item["method"]["defense"],
                "model": item["method"]["model"],
                "auc": item["metrics"]["auc"],
                "asr": item["metrics"]["asr"],
                "tpr_at_1pct_fpr": item["metrics"]["tpr_at_1pct_fpr"],
                "tpr_at_0_1pct_fpr": item["metrics"]["tpr_at_0_1pct_fpr"],
                "evidence_level": paper_evidence_level(item),
                "quality_cost": paper_quality_cost(item["quality_cost"]),
            }
        )
    return rows


def build_metric_uncertainty_rows() -> list[dict]:
    rows: list[dict] = []

    score_sources = [
        (
            "gray-box PIA",
            "admitted",
            "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/adaptive-scores.json",
            False,
            2026052601,
            "row-score bootstrap over adaptive mean scores; other reportable rows remain point estimates unless direct score arrays are available",
        ),
        (
            "PIA + G-1 dropout",
            "admitted",
            "workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/adaptive-scores.json",
            False,
            2026052602,
            "row-score bootstrap over adaptive mean scores; defense-comparator interval only",
        ),
        (
            "DPDM W-1",
            "admitted",
            "workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/scores.json",
            True,
            2026052603,
            "row-score bootstrap over target scores with orientation matching the recorded admitted AUC",
        ),
    ]
    for label, role, source, invert_scores, seed, note in score_sources:
        data = read_json(source)
        if "target_member_scores" in data:
            member_scores = [float(value) for value in data["target_member_scores"]]
            nonmember_scores = [float(value) for value in data["target_nonmember_scores"]]
        else:
            member_scores = [float(value) for value in data["member_scores"]]
            nonmember_scores = [float(value) for value in data["nonmember_scores"]]
        if invert_scores:
            member_scores = [-value for value in member_scores]
            nonmember_scores = [-value for value in nonmember_scores]
        point = auc_from_scores(member_scores, nonmember_scores)
        p025, p975 = bootstrap_auc_ci(member_scores, nonmember_scores, seed=seed)
        source_hash = sha256_file(ROOT / source)
        rows.append(
            uncertainty_row(
                label,
                role,
                source,
                point,
                p025,
                p975,
                "stratified row bootstrap, 2000 iterations",
                len(member_scores),
                len(nonmember_scores),
                "direct score array",
                "recomputed",
                "stratified member/nonmember rows",
                source_hash,
                "AUC interval for this row and role only",
                note,
            )
        )

    h2_sources = [
        (
            "H2 output-cloud 512/512",
            "candidate",
            "workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json",
            "logistic",
        ),
        (
            "H2 shared-position seed176",
            "control",
            "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json",
            "logistic",
        ),
        (
            "H2 shared-position seed177",
            "stability",
            "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json",
            "logistic",
        ),
    ]
    for label, role, source, block in h2_sources:
        data = read_json(source)
        metrics = data[block]["aggregate_metrics"]
        ci95 = data[block]["aggregate_ci95"]["auc"]
        inputs = data["inputs"]
        rows.append(
            uncertainty_row(
                label,
                role,
                source,
                metrics["auc"],
                ci95["p025"],
                ci95["p975"],
                "recorded artifact aggregate_ci95",
                inputs["member_count"],
                inputs["nonmember_count"],
                "artifact aggregate_ci95",
                "recorded",
                "not available in paper workspace",
                "",
                "candidate/control interval only",
                "candidate-side interval; does not change admission state",
            )
        )

    transfer = read_json("workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json")
    for item in transfer["primary_transfer"]:
        metrics = item["aggregate_metrics"]
        ci95 = item["aggregate_ci95"]["auc"]
        rows.append(
            uncertainty_row(
                f"H2 cache-reuse stability {item['source']} to {item['target']}",
                "cache-robustness",
                "workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json",
                metrics["auc"],
                ci95["p025"],
                ci95["p975"],
                "recorded artifact aggregate_ci95",
                "256",
                "256",
                "artifact aggregate_ci95",
                "recorded",
                "not available in paper workspace",
                "",
                "same-family candidate cache-reuse stability interval only",
                "same-family cache-reuse stability interval; not cross-model portability",
            )
        )

    return rows


def build_h2_rows() -> list[dict]:
    main = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json")
    shuffle = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json")
    shared = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json")
    shared_shuffle = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json"
    )
    seed177 = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json"
    )
    seed177_shuffle = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json"
    )
    transfer = read_json("workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json")
    img2img = read_json("workspaces/black-box/artifacts/h2-img2img-output-cloud-portability-20260525.json")

    rows = [
        metric_row("h2-main", "output-cloud 512/512", "candidate", main["logistic"]["aggregate_metrics"]),
        metric_row("h2-main", "raw H2 logistic", "baseline", main["comparison"]["raw_h2_logistic"]),
        metric_row("h2-main", "lowpass H2 logistic", "baseline", main["comparison"]["lowpass_h2_logistic"]),
        metric_row("h2-main", "label shuffle", "sanity", shuffle["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position seed 176", "control", shared["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position label shuffle", "sanity", shared_shuffle["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position seed 177", "stability", seed177["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "seed 177 label shuffle", "sanity", seed177_shuffle["logistic"]["aggregate_metrics"]),
    ]
    for item in transfer["primary_transfer"]:
        rows.append(
            metric_row(
                "h2-cache-robustness",
                f"{item['source']} to {item['target']}",
                "cache-robustness",
                item["aggregate_metrics"],
            )
        )
    for packet in img2img["packets"]:
        rows.append(metric_row("h2-img2img", packet["name"], "portability", packet["logistic"]["aggregate_metrics"]))
    return rows


def build_negative_rows() -> list[dict]:
    curated_rows = []
    for row in read_csv(DATA / "negative_support_curated_metrics.csv"):
        curated_rows.append(
            {
                "source": row["source"],
                "label": row["label"],
                "role": row["role"],
                "auc": float(row["auc"]),
                "asr": float(row["asr"]),
                "tpr_at_1pct_fpr": float(row["tpr_at_1pct_fpr"]),
                "tpr_at_0_1pct_fpr": float(row["tpr_at_0_1pct_fpr"]),
                "evidence_source": row["evidence_source"],
            }
        )
    commoncanvas = read_json("workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json")["metric"]
    tracing = read_json("workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json")["eval"]
    return curated_rows + [
        {
            **metric_row("commoncanvas", "conditional denoising loss", "negative", commoncanvas),
            "evidence_source": "workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json",
        },
        {
            "source": "tracing-roots",
            "label": "feature-packet replay",
            "role": "support",
            "auc": tracing["auc"],
            "asr": tracing["accuracy"],
            "tpr_at_1pct_fpr": tracing["tpr_at_1pct_fpr"],
            "tpr_at_0_1pct_fpr": tracing["tpr_at_0_1pct_fpr"],
            "evidence_source": "workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json",
        },
        {
            "source": "mofit-coco",
            "label": "public COCO score replay",
            "role": "support-only",
            "auc": 0.941948,
            "asr": 0.883,
            "tpr_at_1pct_fpr": 0.488,
            "tpr_at_0_1pct_fpr": 0.324,
            "evidence_source": "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_mofit_public_score_surface_preflight_2026_06_08.md",
        },
    ]


def build_stl10_rediffuse_route_summary_rows() -> list[dict]:
    """Summarize STL-10 route evidence without upgrading it to admitted evidence."""

    strict_rows = [
        ("strict-300k", "SecMI", 1, 0.5035539034733632, 0.5040500164031982, 0.010700000450015068),
        ("strict-300k", "PIA", 1, 0.5084503898567155, 0.5068874955177307, 0.01205000001937151),
        ("strict-300k", "ReDiffuse", 10, 0.5048453949019043, 0.5049625039100647, 0.01054999977350235),
        ("strict-300k", "ReDiffuse", 2, 0.5025378516572625, 0.5029625296592712, 0.011075000278651714),
        ("strict-500k", "SecMI", 1, 0.5111869032879086, 0.5088499784469604, 0.009875000454485416),
        ("strict-500k", "PIA", 1, 0.5140272781590328, 0.5111500024795532, 0.012400000356137753),
        ("strict-500k", "ReDiffuse", 10, 0.5106860568790765, 0.5085124969482422, 0.011549999937415123),
        ("strict-500k", "ReDiffuse", 2, 0.5073744603621688, 0.5060250163078308, 0.01145000010728836),
    ]
    overfit_rows = [
        ("overfit-m1000-cont20k", "SecMI", 1, 0.9987007526319299, 0.9987499713897705, 1.0),
        ("overfit-m1000-cont20k", "PIA", 1, 0.9987499713897705, 1.0, 1.0),
        ("overfit-m1000-cont20k", "ReDiffuse", 10, 1.0, 1.0, 1.0),
        ("overfit-m1000-cont20k", "ReDiffuse", 2, 1.0, 1.0, 1.0),
    ]
    rows: list[dict] = []
    for setting, attacker, average, auc, asr, tpr in strict_rows:
        rows.append(
            {
                "route": "stl10-ddim-rediffuse",
                "setting": setting,
                "surface": "strict 50k/50k STL-10 DDIM reproduction",
                "attacker": attacker,
                "average": average,
                "auc": auc,
                "asr": asr,
                "tpr_at_1pct_fpr": tpr,
                "claim_role": "bounded_negative",
                "first_blocker": "strict 300K/500K aggregate metrics are random-level and current checkpoint identity is not retained in the paper packet",
                "allowed_claim": "strict STL-10 300K/500K route remained random-level in the retained aggregate CSV",
                "forbidden_claim": "general ReDiffuse refutation; admitted row; second public asset; strict reproduction success",
                "evidence_source": "Download/shared/supplementary/collaborator-ddim-stl10-20260527/code/result.csv",
            }
        )
    for setting, attacker, average, auc, asr, tpr in overfit_rows:
        rows.append(
            {
                "route": "stl10-ddim-rediffuse",
                "setting": setting,
                "surface": "fixed-subset m1000/n1000 overfit sanity",
                "attacker": attacker,
                "average": average,
                "auc": auc,
                "asr": asr,
                "tpr_at_1pct_fpr": tpr,
                "claim_role": "support_only_memorization_sanity",
                "first_blocker": "target, split, and training surface are intentionally changed from the strict reproduction contract",
                "allowed_claim": "fixed-subset overfit detects memorization under an intentionally changed 1000/1000 setting",
                "forbidden_claim": "strict STL-10 reproduction success; admitted row; second public asset; field-level method validity",
                "evidence_source": "Download/shared/supplementary/collaborator-ddim-stl10-20260527/code/result_overfit_m1000_cont20k.csv",
            }
        )
    return rows


def build_artifact_gate_summaries() -> tuple[list[dict], list[dict]]:
    corpora = [
        ("v1 evidence-note corpus", DATA / "artifact_corpus_v1.csv"),
        ("fixed-search batch", DATA / "artifact_corpus_fixed_search_20260526.csv"),
    ]
    gate_rows: list[dict] = []
    strata_rows: list[dict] = []

    for corpus, path in corpora:
        rows = read_csv(path)
        for gate_col, gate_label in GATE_COLUMNS:
            counts = {outcome: 0 for outcome in GATE_OUTCOMES}
            for row in rows:
                outcome = row.get(gate_col, "").strip()
                if outcome not in counts:
                    counts[outcome] = 0
                counts[outcome] += 1
            for outcome in GATE_OUTCOMES:
                gate_rows.append(
                    {
                        "corpus": corpus,
                        "gate": gate_label,
                        "outcome": outcome,
                        "count": counts[outcome],
                    }
                )

        group_col = "stratum" if "stratum" in rows[0] else "inclusion_decision"
        group_counts: dict[str, int] = {}
        for row in rows:
            group = row[group_col].strip()
            group_counts[group] = group_counts.get(group, 0) + 1
        for group, count in sorted(group_counts.items()):
            strata_rows.append(
                {
                    "corpus": corpus,
                    "group_type": group_col,
                    "group": group,
                    "count": count,
                }
            )

    return gate_rows, strata_rows


def claim_support_level_for_row(row: dict, corpus: str) -> str:
    if corpus == "v1 evidence-note corpus":
        stratum = row["stratum"].strip()
        if stratum not in V1_STRATUM_SUPPORT_LEVEL:
            raise ValueError(f"unknown v1 stratum for claim-support level: {stratum}")
        return V1_STRATUM_SUPPORT_LEVEL[stratum]

    if corpus == "fixed-search batch":
        decision = row["inclusion_decision"].strip()
        if decision not in FIXED_SEARCH_SUPPORT_LEVEL:
            raise ValueError(f"unknown fixed-search decision for claim-support level: {decision}")
        return FIXED_SEARCH_SUPPORT_LEVEL[decision]

    raise ValueError(f"unknown corpus for claim-support level: {corpus}")


def build_claim_support_summaries() -> tuple[list[dict], list[dict]]:
    corpora = [
        ("v1 evidence-note corpus", DATA / "artifact_corpus_v1.csv"),
        ("fixed-search batch", DATA / "artifact_corpus_fixed_search_20260526.csv"),
    ]
    row_records: list[dict] = []
    summary_rows: list[dict] = []

    for corpus, path in corpora:
        rows = read_csv(path)
        counts = {level: 0 for level in CLAIM_SUPPORT_LEVELS}
        for row in rows:
            level = claim_support_level_for_row(row, corpus)
            counts[level] += 1
            row_records.append(
                {
                    "corpus": corpus,
                    "row_id": row.get("id", row.get("batch_id", "")),
                    "candidate": row.get("candidate", row.get("title", "")),
                    "group_type": "stratum" if "stratum" in row else "inclusion_decision",
                    "group": row.get("stratum", row.get("inclusion_decision", "")),
                    "claim_support_level": level,
                    "claim_support_label": CLAIM_SUPPORT_LABELS[level],
                    "paper_role": row.get("paper_role", row.get("artifact_surface", "")),
                    "boundary_note": row.get("primary_failure", row.get("exclusion_reason", "")),
                }
            )

        for level in CLAIM_SUPPORT_LEVELS:
            summary_rows.append(
                {
                    "corpus": corpus,
                    "claim_support_level": level,
                    "claim_support_label": CLAIM_SUPPORT_LABELS[level],
                    "count": counts[level],
                    "denominator": len(rows),
                    "boundary_note": (
                        "selected-corpus taxonomy only"
                        if corpus == "v1 evidence-note corpus"
                        else "no-download fixed-search metadata protocol"
                    ),
                }
            )

    return row_records, summary_rows


def build_false_promotion_summaries() -> tuple[list[dict], list[dict]]:
    source_path = ROOT / "docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_false_promotion_exemplar_summary_2026_06_07.csv"
    source_rows = read_csv(source_path)
    exemplar_rows: list[dict] = []
    rule_counts = {rule: 0 for rule, _ in FALSE_PROMOTION_RULES}

    for row in source_rows:
        weak_rules = {rule.strip() for rule in row["weak_rules_that_would_promote"].split(";")}
        for rule in rule_counts:
            if rule in weak_rules:
                rule_counts[rule] += 1
        exemplar_rows.append(
            {
                "row_id": row["row_id"],
                "title": row["title"],
                "exemplar_type": row["exemplar_type"],
                "weak_rules_that_would_promote": row["weak_rules_that_would_promote"],
                "weak_rule_count": sum(1 for rule in rule_counts if rule in weak_rules),
                "public_surface_that_looks_strong": row["public_surface_that_looks_strong"],
                "contract_blocker": row["contract_blocker"],
                "allowed_wording": row["allowed_wording"],
                "no_compute_release": row["no_compute_release"],
                "paper_role": "pre-label stress-control row",
            }
        )

    summary_rows = [
        {
            "weak_rule": rule,
            "plot_label": label,
            "would_promote_rows": rule_counts[rule],
            "selected_row_count": len(exemplar_rows),
            "boundary_note": "weak-rule count over selected stress rows; not denominator or prevalence evidence",
        }
        for rule, label in FALSE_PROMOTION_RULES
    ]
    return exemplar_rows, summary_rows


def build_false_promotion_row_trace(rows: list[dict]) -> list[dict]:
    trace_rows: list[dict] = []
    for row in rows:
        row_id = row["row_id"]
        source = FALSE_PROMOTION_ROW_SOURCES.get(row_id)
        if source is None:
            raise ValueError(f"missing false-promotion row source mapping: {row_id}")
        check_csv = ROOT / source["check_csv"]
        check_md = ROOT / source["check_md"]
        if not check_csv.exists():
            raise FileNotFoundError(check_csv)
        if not check_md.exists():
            raise FileNotFoundError(check_md)
        digest_payload = json.dumps(
            {
                "row_id": row_id,
                "title": row["title"],
                "weak_rules_that_would_promote": row["weak_rules_that_would_promote"],
                "public_surface_that_looks_strong": row["public_surface_that_looks_strong"],
                "contract_blocker": row["contract_blocker"],
                "allowed_wording": row["allowed_wording"],
                "no_compute_release": row["no_compute_release"],
            },
            sort_keys=True,
        )
        trace_rows.append(
            {
                "review_id": f"FPR-{row_id}",
                "source_row_id": row_id,
                "title": row["title"],
                "observed_at": source["observed_at"],
                "public_urls": source["public_urls"],
                "source_check_csv": source["check_csv"],
                "source_check_csv_sha256": sha256_file(check_csv),
                "source_check_md": source["check_md"],
                "source_check_md_sha256": sha256_file(check_md),
                "source_summary_row_sha256": sha256_text(digest_payload),
                "trace_status": "no-download public-surface trace",
                "review_boundary": "for reviewer navigation and row identity only; not external adjudication, denominator evidence, or compute release",
            }
        )
    return trace_rows


def build_false_promotion_review_materials(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    packet_rows: list[dict] = []
    blinded_packet_rows: list[dict] = []
    adjudication_key_rows: list[dict] = []
    template_rows: list[dict] = []

    for row in rows:
        review_id = f"FPR-{row['row_id']}"
        weak_rules = row["weak_rules_that_would_promote"]
        review_question = (
            "Using only the packet facts and codebook, assign gates and decide whether weak-rule promotion "
            "would exceed the evidence-contract boundary."
        )
        packet_rows.append(
            {
                "review_id": review_id,
                "source_row_id": row["row_id"],
                "title": row["title"],
                "exemplar_type": row["exemplar_type"],
                "weak_rules_under_test": weak_rules,
                "public_surface_that_looks_strong": row["public_surface_that_looks_strong"],
                "contract_blocker_claimed": row["contract_blocker"],
                "source_allowed_wording": row["allowed_wording"],
                "source_no_compute_release": row["no_compute_release"],
                "review_question": review_question,
                "packet_status": "prepared_not_adjudicated",
                "reviewer": "",
                "external_decision": "",
                "external_notes": "",
            }
        )
        blinded_packet_rows.append(
            {
                "review_id": review_id,
                "source_row_id": row["row_id"],
                "title": row["title"],
                "weak_surface_family": row["exemplar_type"].replace(" false-promotion", ""),
                "weak_rules_under_test": weak_rules,
                "public_surface_observation": row["public_surface_that_looks_strong"],
                "review_question": review_question,
                "packet_status": "blocker_blinded_prepared_not_adjudicated",
            }
        )
        adjudication_key_rows.append(
            {
                "review_id": review_id,
                "source_row_id": row["row_id"],
                "title": row["title"],
                "author_false_promotion_verdict": FALSE_PROMOTION_AUTHOR_VERDICT[row["row_id"]],
                "author_contract_blocker": row["contract_blocker"],
                "author_allowed_wording": row["allowed_wording"],
                "author_compute_release": "no",
                "author_no_compute_release": row["no_compute_release"],
                "key_status": "author_key_not_external_label",
            }
        )

        template_row = {
            "review_id": review_id,
            "source_row_id": row["row_id"],
            "title": row["title"],
            "reviewer": "",
            "gate_allowed_values": FALSE_PROMOTION_REVIEW_VALUES,
            "verdict_allowed_values": FALSE_PROMOTION_VERDICT_VALUES,
            "compute_release_allowed_values": FALSE_PROMOTION_COMPUTE_RELEASE_VALUES,
        }
        for gate in FALSE_PROMOTION_REVIEW_GATES:
            template_row[gate] = ""
        template_row.update(
            {
                "false_promotion_verdict": "",
                "first_blocker": "",
                "allowed_wording": "",
                "compute_release": "",
                "notes": "",
            }
        )
        template_rows.append(template_row)

    return packet_rows, blinded_packet_rows, adjudication_key_rows, template_rows


def build_false_promotion_gate_matrix(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    matrix_rows: list[dict] = []
    summary_counts = {
        gate: {outcome: 0 for outcome in ["Pass", "Partial", "Fail", "N/A"]}
        for gate in FALSE_PROMOTION_REVIEW_GATES
    }
    for row in rows:
        row_id = row["row_id"]
        labels = FALSE_PROMOTION_AUTHOR_GATE_LABELS.get(row_id)
        if labels is None:
            raise ValueError(f"missing false-promotion author gate labels: {row_id}")
        matrix_row = {
            "review_id": f"FPR-{row_id}",
            "source_row_id": row_id,
            "title": row["title"],
            "label_source": "author_key_not_external_label",
        }
        for gate in FALSE_PROMOTION_REVIEW_GATES:
            value = labels[gate]
            if value not in {"Pass", "Partial", "Fail", "N/A"}:
                raise ValueError(f"invalid {gate}={value!r} for {row_id}")
            matrix_row[gate] = value
            summary_counts[gate][value] += 1
        matrix_row.update(
            {
                "author_false_promotion_verdict": FALSE_PROMOTION_AUTHOR_VERDICT[row_id],
                "first_blocking_gate": labels["first_blocking_gate"],
                "gate_rationale": labels["gate_rationale"],
                "compute_release": "no",
                "matrix_boundary": "author-keyed post-label comparison only; not external adjudication, denominator evidence, or compute release",
            }
        )
        matrix_rows.append(matrix_row)

    summary_rows: list[dict] = []
    for gate in FALSE_PROMOTION_REVIEW_GATES:
        for outcome in ["Pass", "Partial", "Fail", "N/A"]:
            summary_rows.append(
                {
                    "gate": gate,
                    "outcome": outcome,
                    "count": summary_counts[gate][outcome],
                    "selected_row_count": len(rows),
                    "boundary_note": "author-keyed C14 gate count over selected stress rows; not external reliability or prevalence evidence",
                }
            )
    return matrix_rows, summary_rows


def metric_plot_label(row: dict) -> str:
    label = row.get("label", row.get("attack", "row"))
    source = row.get("source", "")

    admitted_labels = {
        "black-box: recon DDIM public-100 step30 / none": "black-box recon",
        "gray-box: PIA GPU512 baseline / none": "gray-box PIA",
        "gray-box: PIA GPU512 baseline / provisional G-1 = stochastic-dropout (all_steps)": "PIA + G-1 dropout",
        "white-box: GSA 1k-3shadow / none": "white-box GSA",
        "white-box: GSA 1k-3shadow / W-1 strong-v3 full-scale": "DPDM W-1",
    }
    if label in admitted_labels:
        return admitted_labels[label]

    if source == "rediffuse-stl10" and label == "denoising-loss scout":
        return "ReDiffuse loss"
    if source == "rediffuse-stl10" and label == "score-norm scout":
        return "ReDiffuse norm"
    if source == "commoncanvas":
        return "CommonCanvas loss"
    if source == "tracing-roots":
        return "Tracing Roots features"

    h2_labels = {
        "output-cloud 512/512": "output-cloud",
        "raw H2 logistic": "raw H2",
        "lowpass H2 logistic": "lowpass H2",
        "label shuffle": "label shuffle",
        "shared-position seed 176": "seed176 control",
        "shared-position label shuffle": "seed176 shuffle",
        "shared-position seed 177": "seed177 control",
        "seed 177 label shuffle": "seed177 shuffle",
        "shared_position_seed176 to shared_position_seed177": "176 -> 177 cache",
        "shared_position_seed177 to shared_position_seed176": "177 -> 176 cache",
    }
    return h2_labels.get(label, label.replace("_", " "))


def plot_metric_bars(rows: list[dict], path: Path, title: str, figsize: tuple[float, float]) -> None:
    labels = [metric_plot_label(row) for row in rows]
    auc = [float(row["auc"]) for row in rows]
    tpr = [float(row["tpr_at_1pct_fpr"]) for row in rows]

    fig, ax = plt.subplots(figsize=figsize)
    y = list(range(len(rows)))
    height = 0.32
    ax.barh([i - height / 2 for i in y], auc, height, label="AUC", color="#376da6")
    ax.barh([i + height / 2 for i in y], tpr, height, label="TPR@1%", color="#d58f2f")
    ax.axvline(0.5, color="#666666", linewidth=0.8, linestyle="--", label="random")
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("metric value")
    ax.set_title(title, pad=12)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.4)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)
    ax.legend(
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        borderaxespad=0,
        fontsize=7.6,
    )
    fig.tight_layout(pad=0.6)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_h2_output_cloud_controls(rows: list[dict], path: Path) -> None:
    main_rows = [
        row
        for row in rows
        if row["role"] in {"candidate", "baseline", "sanity", "control", "stability", "cache-robustness"}
    ]
    portability_rows = [row for row in rows if row["role"] == "portability"]

    labels = [metric_plot_label(row) for row in main_rows]
    auc = [float(row["auc"]) for row in main_rows]
    tpr = [float(row["tpr_at_1pct_fpr"]) for row in main_rows]

    fig, (ax, inset) = plt.subplots(
        1,
        2,
        figsize=(7.1, 3.55),
        gridspec_kw={"width_ratios": [3.2, 1.18], "wspace": 0.45},
    )
    y = list(range(len(main_rows)))
    height = 0.32
    ax.barh([i - height / 2 for i in y], auc, height, label="AUC", color="#376da6")
    ax.barh([i + height / 2 for i in y], tpr, height, label="TPR@1%", color="#d58f2f")
    ax.axvline(0.5, color="#666666", linewidth=0.8, linestyle="--", label="random")
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("metric value")
    ax.set_title("H2 output-cloud controls", pad=12)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.2)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)
    ax.legend(
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        borderaxespad=0,
        fontsize=7.4,
    )

    port_labels = []
    for row in portability_rows:
        if "admission_25_25" in row["label"]:
            port_labels.append("img2img 25/25\nadmission boundary")
        else:
            port_labels.append("img2img 10/10\ndiagnostic")
    port_y = list(range(len(portability_rows)))
    port_auc = [float(row["auc"]) for row in portability_rows]
    port_tpr = [float(row["tpr_at_1pct_fpr"]) for row in portability_rows]
    inset.barh([i - height / 2 for i in port_y], port_auc, height, color="#7895b2")
    inset.barh([i + height / 2 for i in port_y], port_tpr, height, color="#e0aa5a")
    inset.axvline(0.5, color="#666666", linewidth=0.8, linestyle="--")
    inset.set_xlim(0, 1.05)
    inset.set_title("Portability-boundary\ninset", pad=8, fontsize=8.0)
    inset.set_yticks(port_y)
    inset.set_yticklabels(port_labels, fontsize=7.1)
    inset.invert_yaxis()
    inset.grid(axis="x", alpha=0.2)
    inset.tick_params(axis="x", labelsize=7.0)
    inset.set_xlabel("not admitted", fontsize=7.2)
    inset.text(
        0.5,
        -0.24,
        "25/25 exposes no admission path;\n10/10 is diagnostic only.",
        transform=inset.transAxes,
        ha="center",
        va="top",
        fontsize=6.9,
        color="#4b5965",
    )

    fig.subplots_adjust(left=0.18, right=0.96, top=0.82, bottom=0.24, wspace=0.50)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_admitted_bundle(rows: list[dict], path: Path) -> None:
    labels = [
        PLOT_METHOD_LABELS.get(
            row["attack"],
            f"{metric_plot_label(row)}\n{row['replay_tier_label']}",
        )
        if row["defense"] == "none"
        else PLOT_DEFENSE_LABELS.get(row["defense"], f"{row['defense']}\n{row['replay_tier_label']}")
        for row in rows
    ]
    auc = [float(row["auc"]) for row in rows]
    tpr = [float(row["tpr_at_1pct_fpr"]) for row in rows]

    role_backgrounds = {
        "primary-risk-evidence": "#eaf3f8",
        "defense-comparator": "#fff2de",
        "upper-bound-comparator": "#f0edf7",
        "defense-bridge": "#e9f3e5",
    }

    fig, ax = plt.subplots(figsize=(4.05, 2.85))
    y = list(range(len(rows)))
    height = 0.32
    for i, row in enumerate(rows):
        ax.axhspan(i - 0.46, i + 0.46, color=role_backgrounds.get(row["report_role"], "#f4f4f4"), zorder=0)

    ax.barh([i - height / 2 for i in y], auc, height, label="AUC", color="#376da6", zorder=2)
    ax.barh([i + height / 2 for i in y], tpr, height, label="TPR@1%", color="#d58f2f", zorder=2)
    ax.axvline(0.5, color="#666666", linewidth=0.8, linestyle="--", label="random", zorder=1)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("finite packet metric value")
    ax.set_title("Evidence packets by role", pad=16)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.2)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.18, zorder=1)
    ax.legend(
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        borderaxespad=0,
        fontsize=8,
    )
    fig.tight_layout(pad=0.6)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def draw_box(
    ax,
    center: tuple[float, float],
    text: str,
    width: float,
    height: float,
    facecolor: str,
    *,
    fontsize: float = 9,
    edgecolor: str = "#25303b",
    linewidth: float = 1.05,
    rounding: float = 0.045,
) -> None:
    x = center[0] - width / 2
    y = center[1] - height / 2
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.045",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(center[0], center[1], text, ha="center", va="center", fontsize=fontsize, color="#16202a", linespacing=1.15)


def draw_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#4b5965",
    *,
    connectionstyle: str = "arc3,rad=0.0",
    linewidth: float = 1.05,
    zorder: int = 2,
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=linewidth,
        color=color,
        connectionstyle=connectionstyle,
        zorder=zorder,
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arrow)


def plot_evidence_contract_pipeline(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.1, 3.05))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    top_y = 0.74
    centers = [0.09, 0.27, 0.45, 0.63, 0.82]
    labels = [
        "Claim +\npacket\np,c",
        "Ordered\ngate vector\ng(p,c)",
        "First\nnon-Pass\nblocker",
        "State +\nallowed\nwording",
        "Release\nsidecars",
    ]
    colors = ["#e8eef7", "#e8eef7", "#fff1d6", "#fff1d6", "#e3f1e6"]
    width = 0.145
    height = 0.24
    for x, label, color in zip(centers, labels, colors):
        draw_box(ax, (x, top_y), label, width, height, color, fontsize=8.2)
    for left, right in zip(centers[:-1], centers[1:]):
        draw_arrow(ax, (left + width / 2, top_y), (right - width / 2, top_y))

    gate_labels = [
        ("gT", "target"),
        ("gS", "split"),
        ("gO", "observable"),
        ("gM", "metric"),
        ("gC", "consumer"),
        ("gDelta", "delta"),
    ]
    gate_x0 = 0.12
    gate_w = 0.115
    state_specs = [
        ("Reportable\nreplay-admitted\nor point-worded", 0.16, "#dcefdc", "#3f6f45"),
        ("Candidate\nmissing consumer\nor delta", 0.39, "#fff1d6", "#8a6d2b"),
        ("Support-only /\nwatch\nrelated surface", 0.62, "#e8eef7", "#49637d"),
        ("Negative\nbounded route\nstop", 0.84, "#f4e4e4", "#8a5b5b"),
    ]
    for _, x, _, edge in state_specs:
        draw_arrow(
            ax,
            (0.63, top_y - height / 2),
            (x, 0.30),
            edge,
            connectionstyle=f"arc3,rad={0.18 if x < 0.55 else -0.12}",
            linewidth=0.9,
            zorder=1,
        )

    gate_y = 0.48
    for idx, (math_label, text_label) in enumerate(gate_labels):
        x = gate_x0 + idx * 0.128
        draw_box(
            ax,
            (x, gate_y),
            f"{math_label}\n{text_label}",
            gate_w,
            0.12,
            "#f7f9fb",
            fontsize=6.9,
            edgecolor="#6d7680",
            linewidth=0.75,
            rounding=0.025,
        )

    ax.text(
        0.49,
        0.34,
        "first required non-Pass gate fixes the narrowest state",
        ha="center",
        va="center",
        fontsize=7.4,
        color="#4b5965",
    )

    for text, x, color, edge in state_specs:
        draw_box(ax, (x, 0.20), text, 0.19, 0.16, color, fontsize=7.2, edgecolor=edge, linewidth=0.95)

    ax.text(
        0.5,
        0.94,
        "Claim-admission protocol",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#16202a",
    )
    ax.text(
        0.5,
        0.035,
        "Sidecars bind each headline sentence to claim_trace.csv, source_provenance.csv, and metric_uncertainty.csv.",
        ha="center",
        va="center",
        fontsize=6.9,
        color="#4b5965",
    )
    fig.tight_layout(pad=0.25)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_artifact_gate_summary(rows: list[dict], path: Path) -> None:
    corpora = []
    for row in rows:
        if row["corpus"] not in corpora:
            corpora.append(row["corpus"])

    colors = {"Pass": "#2f7d4f", "Partial": "#d49a2f", "Fail": "#b84a4a"}
    fig, axes = plt.subplots(len(corpora), 1, figsize=(6.8, 2.45 * len(corpora)), sharex=True)
    if len(corpora) == 1:
        axes = [axes]

    for ax, corpus in zip(axes, corpora):
        corpus_rows = [row for row in rows if row["corpus"] == corpus]
        gates = [label for _, label in GATE_COLUMNS]
        x_positions = list(range(len(gates)))
        bottoms = [0] * len(gates)
        for outcome in GATE_OUTCOMES:
            values = []
            for gate in gates:
                match = next(row for row in corpus_rows if row["gate"] == gate and row["outcome"] == outcome)
                values.append(int(match["count"]))
            ax.bar(x_positions, values, bottom=bottoms, label=outcome, color=colors[outcome])
            bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
        ax.set_title(corpus)
        ax.set_ylabel("rows")
        ax.grid(axis="y", alpha=0.2)

    axes[-1].set_xlabel("evidence-contract gate")
    axes[-1].set_xticks(x_positions)
    axes[-1].set_xticklabels(
        [GATE_PLOT_LABELS.get(gate, gate) for gate in gates],
        rotation=0,
        ha="center",
        fontsize=8,
    )
    fig.suptitle("Selected-corpus gate labels", y=0.985, fontsize=12)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.945), frameon=False, ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.885), pad=0.5)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_artifact_claim_support_summary(rows: list[dict], path: Path) -> None:
    corpora = []
    by_corpus: dict[str, dict[str, dict]] = {}
    for row in rows:
        corpus = row["corpus"]
        if corpus not in corpora:
            corpora.append(corpus)
        by_corpus.setdefault(corpus, {})[row["claim_support_level"]] = row

    x = list(range(len(CLAIM_SUPPORT_LEVELS)))
    width = 0.34
    offsets = [-width / 2, width / 2]
    colors = ["#376da6", "#d58f2f"]

    fig, ax = plt.subplots(figsize=(5.85, 2.75))
    for corpus_idx, corpus in enumerate(corpora):
        values = [int(by_corpus[corpus][level]["count"]) for level in CLAIM_SUPPORT_LEVELS]
        denominator = by_corpus[corpus][CLAIM_SUPPORT_LEVELS[0]]["denominator"]
        label = f"{corpus} (n={denominator})"
        positions = [pos + offsets[corpus_idx] for pos in x]
        bars = ax.bar(positions, values, width, label=label, color=colors[corpus_idx])
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.2,
                str(value),
                ha="center",
                va="bottom",
                fontsize=7.2,
            )

    ax.set_title("Claim-support levels by declared denominator", pad=12)
    ax.set_ylabel("rows")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{level}\n{CLAIM_SUPPORT_LABELS[level].split(' ', 1)[0]}" for level in CLAIM_SUPPORT_LEVELS])
    ax.set_ylim(0, max(int(row["count"]) for row in rows) + 2.2)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=1, fontsize=7.6)
    ax.text(
        0.5,
        -0.30,
        "Denominators are not pooled; HF/Zenodo/OpenReview source-query controls are excluded from L0-L3 aggregation.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.2,
        color="#4b5965",
    )
    fig.tight_layout(pad=0.5)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_false_promotion_exemplars(rows: list[dict], path: Path) -> None:
    rule_keys = [rule for rule, _ in FALSE_PROMOTION_RULES]
    rule_labels = [label for _, label in FALSE_PROMOTION_RULES] + ["blocked"]
    matrix: list[list[int]] = []
    row_labels: list[str] = []
    for row in rows:
        weak_rules = {rule.strip() for rule in row["weak_rules_that_would_promote"].split(";")}
        matrix.append([1 if rule in weak_rules else 0 for rule in rule_keys] + [1])
        row_labels.append(f"{row['row_id'].replace('E2SCT-', '')}\n{FALSE_PROMOTION_ROW_LABELS.get(row['row_id'], row['title'])}")

    fig_height = max(2.35, 1.0 + 0.32 * len(rows))
    fig, ax = plt.subplots(figsize=(5.6, fig_height))
    ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(rule_labels)))
    ax.set_xticklabels(rule_labels, rotation=0, ha="center", fontsize=7.5)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7.0)
    ax.set_title("Weak-rule false promotion vs. evidence contract block", pad=10)
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, "1" if value else "", ha="center", va="center", fontsize=8, color="#12263a")
    ax.set_xticks([x - 0.5 for x in range(1, len(rule_labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(row_labels))], minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=1.0)
    ax.tick_params(which="both", length=0)
    ax.text(
        0.5,
        -0.22,
        "Cells mark author-modeled shortcut pressure; the final column records DiffAudit's contract block.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.1,
        color="#4b5965",
    )
    fig.tight_layout(pad=0.45)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_false_promotion_gate_matrix(rows: list[dict], path: Path) -> None:
    gates = FALSE_PROMOTION_REVIEW_GATES
    gate_labels = ["target", "split", "score/resp", "metric", "semantic", "prov.", "consumer"]
    value_map = {"Fail": 0, "Partial": 1, "Pass": 2, "N/A": 3}
    colors = ["#b84a4a", "#d49a2f", "#2f7d4f", "#d7dde5"]
    matrix: list[list[int]] = []
    row_labels: list[str] = []
    for row in rows:
        matrix.append([value_map[row[gate]] for gate in gates])
        row_labels.append(
            f"{row['source_row_id'].replace('E2SCT-', '')}\n"
            f"{FALSE_PROMOTION_ROW_LABELS.get(row['source_row_id'], row['title'])}"
        )

    from matplotlib.colors import ListedColormap, BoundaryNorm

    fig_height = max(2.5, 1.0 + 0.32 * len(rows))
    fig, ax = plt.subplots(figsize=(6.2, fig_height))
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(gate_labels)))
    ax.set_xticklabels(gate_labels, rotation=0, ha="center", fontsize=7.4)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7.0)
    ax.set_title("C14 author-keyed evidence-contract gate matrix", pad=10)
    label_by_value = {0: "F", 1: "Ptl", 2: "P", 3: "N/A"}
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, label_by_value[value], ha="center", va="center", fontsize=6.8, color="#111827")
    ax.set_xticks([x - 0.5 for x in range(1, len(gate_labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(row_labels))], minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=1.0)
    ax.tick_params(which="both", length=0)
    legend_handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=colors[2], markersize=7, label="Pass"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=colors[1], markersize=7, label="Partial"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=colors[0], markersize=7, label="Fail"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=colors[3], markersize=7, label="N/A"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, fontsize=7.2)
    ax.text(
        0.5,
        -0.29,
        "Author-keyed matrix for post-label comparison; not external adjudication, reliability, denominator, or compute-release evidence.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.0,
        color="#4b5965",
    )
    fig.tight_layout(pad=0.45)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    admitted = build_admitted_rows()
    h2 = build_h2_rows()
    negative = build_negative_rows()
    stl10_route_summary = build_stl10_rediffuse_route_summary_rows()
    uncertainty = build_metric_uncertainty_rows()
    artifact_gate_summary, artifact_strata_summary = build_artifact_gate_summaries()
    artifact_claim_support_rows, artifact_claim_support_summary = build_claim_support_summaries()
    false_promotion_rows, false_promotion_summary = build_false_promotion_summaries()
    (
        false_promotion_review_packet,
        false_promotion_blinded_review_packet,
        false_promotion_adjudication_key,
        false_promotion_review_template,
    ) = build_false_promotion_review_materials(false_promotion_rows)
    false_promotion_row_trace = build_false_promotion_row_trace(false_promotion_rows)
    false_promotion_gate_matrix, false_promotion_gate_summary = build_false_promotion_gate_matrix(false_promotion_rows)
    manuscript_claim_audit = build_manuscript_claim_audit_rows(
        admitted,
        h2,
        false_promotion_summary,
        false_promotion_gate_summary,
    )
    claim_trace = build_claim_trace_rows()
    claim_transition_examples = build_claim_transition_examples(claim_trace)
    citation_context_audit = build_citation_context_audit_rows()

    write_csv(DATA / "admitted_rows.csv", admitted)
    write_csv(DATA / "h2_output_cloud_rows.csv", h2)
    write_csv(DATA / "negative_support_rows.csv", negative)
    write_csv(DATA / "stl10_rediffuse_route_summary.csv", stl10_route_summary)
    write_csv(DATA / "metric_uncertainty.csv", uncertainty)
    write_csv(DATA / "artifact_gate_summary.csv", artifact_gate_summary)
    write_csv(DATA / "artifact_strata_summary.csv", artifact_strata_summary)
    write_csv(DATA / "artifact_claim_support_rows.csv", artifact_claim_support_rows)
    write_csv(DATA / "artifact_claim_support_summary.csv", artifact_claim_support_summary)
    write_csv(DATA / "false_promotion_exemplars.csv", false_promotion_rows)
    write_csv(DATA / "false_promotion_rule_summary.csv", false_promotion_summary)
    write_csv(DATA / "false_promotion_external_review_packet.csv", false_promotion_review_packet)
    write_csv(DATA / "false_promotion_blinded_review_packet.csv", false_promotion_blinded_review_packet)
    write_csv(DATA / "false_promotion_adjudication_key.csv", false_promotion_adjudication_key)
    write_csv(DATA / "false_promotion_external_review_template.csv", false_promotion_review_template)
    write_csv(DATA / "false_promotion_row_trace.csv", false_promotion_row_trace)
    write_csv(DATA / "false_promotion_author_gate_matrix.csv", false_promotion_gate_matrix)
    write_csv(DATA / "false_promotion_gate_summary.csv", false_promotion_gate_summary)
    write_csv(DATA / "claim_trace.csv", claim_trace)
    write_csv(DATA / "claim_transition_examples.csv", claim_transition_examples)
    write_csv(DATA / "manuscript_claim_audit.csv", manuscript_claim_audit)
    write_csv(DATA / "citation_context_audit.csv", citation_context_audit)
    source_provenance = build_source_provenance_rows()
    validate_claim_trace_rows(claim_trace, source_provenance)
    write_csv(DATA / "source_provenance.csv", source_provenance)

    plot_admitted_bundle(admitted, FIGURES / "admitted_rows_metrics.pdf")
    plot_h2_output_cloud_controls(h2, FIGURES / "h2_output_cloud_controls.pdf")
    plot_evidence_contract_pipeline(FIGURES / "evidence_contract_pipeline.pdf")
    plot_artifact_gate_summary(artifact_gate_summary, FIGURES / "artifact_gate_summary.pdf")
    plot_artifact_claim_support_summary(
        artifact_claim_support_summary,
        FIGURES / "artifact_claim_support_summary.pdf",
    )
    plot_false_promotion_exemplars(false_promotion_rows, FIGURES / "false_promotion_exemplars.pdf")
    plot_false_promotion_gate_matrix(false_promotion_gate_matrix, FIGURES / "false_promotion_gate_matrix.pdf")

    manifest = {
        "generated": GENERATED_MANIFEST_PATHS,
        "curated": CURATED_MANIFEST_PATHS,
        "paper_sources": PAPER_SOURCE_MANIFEST_PATHS,
        "repo_sources": REVIEW_SNAPSHOT_REPO_SOURCE_PATHS,
        "anonymous_supplement_excluded": ANONYMOUS_SUPPLEMENT_EXCLUDED_PATHS,
        "reviewer_packet_allowed_prelabel": REVIEWER_PACKET_ALLOWED_PRELABEL_PATHS,
        "maintainer_only_author_key": MAINTAINER_ONLY_AUTHOR_KEY_PATHS,
        "source_policy": "All numbers are read from existing DiffAudit Research JSON artifacts or frozen evidence notes.",
        "validation_policy": "claim_trace gate columns must use Pass/Partial/Fail/N/A and every provenance_id must resolve to a hashed source_provenance row.",
        "review_snapshot_policy": (
            "data/review_snapshot_manifest.csv records file-byte hashes and git-status identity for the local review packet. "
            "It is a review-snapshot identity aid, not clean public release provenance or a public redistributability claim."
        ),
        "anonymous_supplement_policy": (
            "An anonymous manuscript supplement should package generated, curated, and paper-source paths in this manifest plus paper.pdf, "
            "except paths listed in anonymous_supplement_excluded. C14 files listed in reviewer_packet_allowed_prelabel are pre-label reviewer navigation/preparation inputs; "
            "files listed in maintainer_only_author_key remain out of the anonymous supplement and maintainer-only until labels and declarations are final. "
            "Local source_provenance paths, dirty tree state, and generator commands identify the packet used for review; "
            "they do not by themselves claim public redistributability, clean-release provenance, or stronger replay availability."
        ),
        "excluded_from_public_claims": [
            "private local filesystem paths",
            "dirty repository state as public provenance",
            "permission-bound artifacts as public replay evidence",
            "candidate/support/support-only rows as admitted downstream audit rows",
            "C14 author-key/post-label files as anonymous reviewer material before labels are final",
        ],
    }
    (PAPER / "asset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(DATA / "review_snapshot_manifest.csv", build_review_snapshot_rows(sha256_file(PAPER / "asset_manifest.json")))


if __name__ == "__main__":
    main()
