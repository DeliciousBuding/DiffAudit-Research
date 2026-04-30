"""Argument parser construction for the DiffAudit CLI."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="diffaudit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke_parser = subparsers.add_parser("run-smoke", help="run the smoke pipeline")
    smoke_parser.add_argument("--config", required=True, help="path to audit yaml")
    smoke_parser.add_argument(
        "--workspace",
        default=".",
        help="workspace root used to resolve output paths",
    )

    secmi_parser = subparsers.add_parser(
        "plan-secmi",
        help="build a SecMI integration plan from audit config",
    )
    secmi_parser.add_argument("--config", required=True, help="path to audit yaml")

    pia_parser = subparsers.add_parser(
        "plan-pia",
        help="build a PIA integration plan from audit config",
    )
    pia_parser.add_argument("--config", required=True, help="path to audit yaml")

    clid_parser = subparsers.add_parser(
        "plan-clid",
        help="build a CLiD integration plan from audit config",
    )
    clid_parser.add_argument("--config", required=True, help="path to audit yaml")

    recon_parser = subparsers.add_parser(
        "plan-recon",
        help="build a reconstruction-based black-box integration plan from audit config",
    )
    recon_parser.add_argument("--config", required=True, help="path to audit yaml")

    variation_parser = subparsers.add_parser(
        "plan-variation",
        help="build an API-only variation attack plan from audit config",
    )
    variation_parser.add_argument("--config", required=True, help="path to audit yaml")

    asset_probe_parser = subparsers.add_parser(
        "probe-secmi-assets",
        help="inspect SecMI asset readiness without importing the full runtime",
    )
    asset_probe_parser.add_argument("--config", required=True, help="path to audit yaml")
    asset_probe_parser.add_argument(
        "--member-split-root",
        default="external/SecMI/mia_evals/member_splits",
        help="path to SecMI member split npz files",
    )

    pia_asset_probe_parser = subparsers.add_parser(
        "probe-pia-assets",
        help="inspect PIA DDPM asset readiness without importing the full runtime",
    )
    pia_asset_probe_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_asset_probe_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )

    clid_asset_probe_parser = subparsers.add_parser(
        "probe-clid-assets",
        help="inspect CLiD asset readiness without importing the runtime",
    )
    clid_asset_probe_parser.add_argument("--config", required=True, help="path to audit yaml")

    recon_asset_probe_parser = subparsers.add_parser(
        "probe-recon-assets",
        help="inspect reconstruction-based black-box asset readiness without importing the runtime",
    )
    recon_asset_probe_parser.add_argument("--config", required=True, help="path to audit yaml")

    recon_score_probe_parser = subparsers.add_parser(
        "probe-recon-score-artifacts",
        help="inspect reconstruction score artifact readiness for artifact-driven mainline runs",
    )
    recon_score_probe_parser.add_argument(
        "--artifact-dir",
        required=True,
        help="directory containing target/shadow member and non-member score artifacts",
    )

    recon_runtime_probe_parser = subparsers.add_parser(
        "probe-recon-runtime-assets",
        help="inspect reconstruction dataset/model assets for runtime artifact generation",
    )
    recon_runtime_probe_parser.add_argument("--target-member-dataset", required=True)
    recon_runtime_probe_parser.add_argument("--target-nonmember-dataset", required=True)
    recon_runtime_probe_parser.add_argument("--shadow-member-dataset", required=True)
    recon_runtime_probe_parser.add_argument("--shadow-nonmember-dataset", required=True)
    recon_runtime_probe_parser.add_argument("--target-model-dir", required=True)
    recon_runtime_probe_parser.add_argument("--shadow-model-dir", required=True)
    recon_runtime_probe_parser.add_argument("--backend", default="stable_diffusion")
    recon_runtime_probe_parser.add_argument("--target-decoder-dir", default=None)
    recon_runtime_probe_parser.add_argument("--target-prior-dir", default=None)
    recon_runtime_probe_parser.add_argument("--shadow-decoder-dir", default=None)
    recon_runtime_probe_parser.add_argument("--shadow-prior-dir", default=None)
    recon_runtime_probe_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )

    recon_public_subset_parser = subparsers.add_parser(
        "prepare-recon-public-subset",
        help="materialize a runnable subset from the public recon asset bundle",
    )
    recon_public_subset_parser.add_argument("--bundle-root", required=True)
    recon_public_subset_parser.add_argument("--output-dir", required=True)
    recon_public_subset_parser.add_argument("--target-count", type=int, default=1)
    recon_public_subset_parser.add_argument("--shadow-count", type=int, default=1)

    recon_public_bundle_audit_parser = subparsers.add_parser(
        "audit-recon-public-bundle",
        help="audit public recon bundle semantics and derived mapping-note consistency",
    )
    recon_public_bundle_audit_parser.add_argument("--bundle-root", required=True)

    recon_stage0_gate_parser = subparsers.add_parser(
        "check-recon-stage0-paper-gate",
        help="block strict Recon Attack-I starts unless the public bundle is paper-aligned",
    )
    recon_stage0_gate_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )
    recon_stage0_gate_parser.add_argument("--bundle-root", required=True)
    recon_stage0_gate_parser.add_argument("--attack-scenario", default="attack-i")

    dit_asset_probe_parser = subparsers.add_parser(
        "probe-dit-assets",
        help="inspect official DiT sampling workspace and optional checkpoint readiness",
    )
    dit_asset_probe_parser.add_argument(
        "--repo-root",
        default="external/DiT",
        help="path to local official DiT repository root",
    )
    dit_asset_probe_parser.add_argument(
        "--model",
        default="DiT-XL/2",
        help="DiT model name passed to the official sample script",
    )
    dit_asset_probe_parser.add_argument(
        "--image-size",
        type=int,
        default=256,
        help="image size passed to the official sample script",
    )
    dit_asset_probe_parser.add_argument(
        "--ckpt",
        default=None,
        help="optional local DiT checkpoint path; omitted means the official auto-download path",
    )

    variation_asset_probe_parser = subparsers.add_parser(
        "probe-variation-assets",
        help="inspect API-only variation attack readiness without remote calls",
    )
    variation_asset_probe_parser.add_argument("--config", required=True, help="path to audit yaml")

    h2_asset_probe_parser = subparsers.add_parser(
        "probe-h2-assets",
        help="inspect 04-H2 privacy-aware adapter asset readiness on local DDPM checkpoints and image roots",
    )
    h2_asset_probe_parser.add_argument("--checkpoint-root", required=True)
    h2_asset_probe_parser.add_argument("--checkpoint-dir", default=None)
    h2_asset_probe_parser.add_argument("--member-dataset-dir", required=True)
    h2_asset_probe_parser.add_argument("--nonmember-dataset-dir", required=True)
    h2_asset_probe_parser.add_argument("--packet-cap", type=int, default=1000)
    h2_asset_probe_parser.add_argument(
        "--max-layout-checks",
        type=int,
        default=0,
        help="maximum images per split used for layout validation; 0 means scan all images",
    )
    h2_asset_probe_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
        help="provenance label recorded in the probe summary",
    )

    h2_prepare_parser = subparsers.add_parser(
        "prepare-h2-contract",
        help="freeze the first canonical workspace contract for 04-H2 privacy-aware adapter",
    )
    h2_prepare_parser.add_argument("--workspace", required=True)
    h2_prepare_parser.add_argument("--checkpoint-root", required=True)
    h2_prepare_parser.add_argument("--checkpoint-dir", default=None)
    h2_prepare_parser.add_argument("--member-dataset-dir", required=True)
    h2_prepare_parser.add_argument("--nonmember-dataset-dir", required=True)
    h2_prepare_parser.add_argument("--packet-cap", type=int, default=1000)
    h2_prepare_parser.add_argument("--max-layout-checks", type=int, default=0)
    h2_prepare_parser.add_argument("--rank", type=int, default=4)
    h2_prepare_parser.add_argument("--alpha", type=float, default=1.0)
    h2_prepare_parser.add_argument("--lambda-coeff", type=float, default=0.5)
    h2_prepare_parser.add_argument("--delta", type=float, default=1e-4)
    h2_prepare_parser.add_argument("--lora-lr", type=float, default=1e-4)
    h2_prepare_parser.add_argument("--proxy-lr", type=float, default=1e-3)
    h2_prepare_parser.add_argument(
        "--optimizer",
        default="adam",
        choices=["adam", "adamw", "sgd"],
    )
    h2_prepare_parser.add_argument("--sgd-momentum", type=float, default=0.9)
    h2_prepare_parser.add_argument("--proxy-hidden-dim", type=int, default=256)
    h2_prepare_parser.add_argument("--proxy-steps", type=int, default=5)
    h2_prepare_parser.add_argument("--num-epochs", type=int, default=10)
    h2_prepare_parser.add_argument("--batch-size", type=int, default=8)
    h2_prepare_parser.add_argument("--num-workers", type=int, default=0)
    h2_prepare_parser.add_argument("--method", default="smp", choices=["smp", "mp"])
    h2_prepare_parser.add_argument("--device", default="cpu")
    h2_prepare_parser.add_argument("--provenance-status", default="workspace-verified")

    h2_run_parser = subparsers.add_parser(
        "run-h2-defense-pilot",
        help="execute one bounded 04-H2 privacy-aware adapter training pilot under a prepared contract",
    )
    h2_run_parser.add_argument("--workspace", required=True)
    h2_run_parser.add_argument("--manifest", required=True)
    h2_run_parser.add_argument("--member-limit", type=int, default=1)
    h2_run_parser.add_argument("--nonmember-limit", type=int, default=1)
    h2_run_parser.add_argument("--seed", type=int, default=None)

    h2_review_parser = subparsers.add_parser(
        "review-h2-defense-pilot",
        help="run one same-packet attack-side review for baseline vs defended 04-H2 checkpoints",
    )
    h2_review_parser.add_argument("--workspace", required=True)
    h2_review_parser.add_argument("--run-summary", required=True)
    h2_review_parser.add_argument(
        "--shadow-reference-summary",
        default="workspaces/white-box/runs/gsa-loss-score-export-bounded-actual-20260418-r1/summary.json",
    )
    h2_review_parser.add_argument("--device", default="cpu")
    h2_review_parser.add_argument("--noise-seed", type=int, default=None)
    h2_review_parser.add_argument("--provenance-status", default="workspace-verified")

    prepare_parser = subparsers.add_parser(
        "prepare-secmi",
        help="prepare adapter context for a local SecMI workspace",
    )
    prepare_parser.add_argument("--config", required=True, help="path to audit yaml")
    prepare_parser.add_argument(
        "--repo-root",
        default="third_party/secmi",
        help="path to vendored or local SecMI repository root",
    )

    dry_run_parser = subparsers.add_parser(
        "dry-run-secmi",
        help="validate SecMI adapter readiness without executing the attack",
    )
    dry_run_parser.add_argument("--config", required=True, help="path to audit yaml")
    dry_run_parser.add_argument(
        "--repo-root",
        default="third_party/secmi",
        help="path to vendored or local SecMI repository root",
    )

    pia_dry_run_parser = subparsers.add_parser(
        "dry-run-pia",
        help="validate PIA DDPM readiness without executing the attack",
    )
    pia_dry_run_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_dry_run_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_dry_run_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )

    clid_dry_run_parser = subparsers.add_parser(
        "dry-run-clid",
        help="validate CLiD readiness without executing the attack",
    )
    clid_dry_run_parser.add_argument("--config", required=True, help="path to audit yaml")
    clid_dry_run_parser.add_argument(
        "--repo-root",
        default="external/CLiD",
        help="path to local CLiD repository root",
    )

    recon_dry_run_parser = subparsers.add_parser(
        "dry-run-recon",
        help="validate reconstruction-based black-box readiness without executing the attack",
    )
    recon_dry_run_parser.add_argument("--config", required=True, help="path to audit yaml")
    recon_dry_run_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )

    variation_dry_run_parser = subparsers.add_parser(
        "dry-run-variation",
        help="validate API-only variation attack readiness without remote calls",
    )
    variation_dry_run_parser.add_argument("--config", required=True, help="path to audit yaml")

    clid_dry_run_smoke_parser = subparsers.add_parser(
        "run-clid-dry-run-smoke",
        help="run a synthetic dry-run smoke for CLiD",
    )
    clid_dry_run_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for CLiD dry-run smoke artifacts",
    )
    clid_dry_run_smoke_parser.add_argument(
        "--repo-root",
        default="external/CLiD",
        help="path to local CLiD repository root",
    )

    clid_artifact_summary_parser = subparsers.add_parser(
        "summarize-clid-artifacts",
        help="summarize upstream CLiD inter_output artifacts into a repository summary",
    )
    clid_artifact_summary_parser.add_argument(
        "--artifact-dir",
        required=True,
        help="directory containing CLiD inter_output artifact txt files",
    )
    clid_artifact_summary_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for the CLiD artifact summary",
    )

    recon_eval_smoke_parser = subparsers.add_parser(
        "run-recon-eval-smoke",
        help="run a synthetic evaluation smoke for the reconstruction-based black-box line",
    )
    recon_eval_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for reconstruction eval smoke artifacts",
    )

    recon_artifact_summary_parser = subparsers.add_parser(
        "summarize-recon-artifacts",
        help="summarize reconstruction score artifacts into a repository summary",
    )
    recon_artifact_summary_parser.add_argument(
        "--artifact-dir",
        required=True,
        help="directory containing target/shadow member and non-member score artifacts",
    )
    recon_artifact_summary_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for the reconstruction artifact summary",
    )

    recon_upstream_eval_smoke_parser = subparsers.add_parser(
        "run-recon-upstream-eval-smoke",
        help="run the upstream reconstruction evaluation script with synthetic score artifacts",
    )
    recon_upstream_eval_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for reconstruction upstream eval smoke artifacts",
    )
    recon_upstream_eval_smoke_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )
    recon_upstream_eval_smoke_parser.add_argument(
        "--method",
        default="threshold",
        help="evaluation method passed to the upstream script",
    )

    recon_mainline_smoke_parser = subparsers.add_parser(
        "run-recon-mainline-smoke",
        help="run the unified reconstruction black-box smoke mainline and emit a single summary",
    )
    recon_mainline_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for reconstruction mainline smoke artifacts",
    )
    recon_mainline_smoke_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )
    recon_mainline_smoke_parser.add_argument(
        "--method",
        default="threshold",
        help="evaluation method passed to the upstream script",
    )

    recon_artifact_mainline_parser = subparsers.add_parser(
        "run-recon-artifact-mainline",
        help="run the reconstruction black-box mainline with provided score artifacts",
    )
    recon_artifact_mainline_parser.add_argument(
        "--artifact-dir",
        required=True,
        help="directory containing target/shadow member and non-member score artifacts",
    )
    recon_artifact_mainline_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for reconstruction artifact mainline outputs",
    )
    recon_artifact_mainline_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )
    recon_artifact_mainline_parser.add_argument(
        "--method",
        default="threshold",
        help="evaluation method passed to the upstream script",
    )

    recon_runtime_mainline_parser = subparsers.add_parser(
        "run-recon-runtime-mainline",
        help="generate reconstruction score artifacts from dataset payloads and run the artifact mainline",
    )
    recon_runtime_mainline_parser.add_argument("--target-member-dataset", required=True)
    recon_runtime_mainline_parser.add_argument("--target-nonmember-dataset", required=True)
    recon_runtime_mainline_parser.add_argument("--shadow-member-dataset", required=True)
    recon_runtime_mainline_parser.add_argument("--shadow-nonmember-dataset", required=True)
    recon_runtime_mainline_parser.add_argument("--target-model-dir", required=True)
    recon_runtime_mainline_parser.add_argument("--shadow-model-dir", required=True)
    recon_runtime_mainline_parser.add_argument("--target-decoder-dir", default=None)
    recon_runtime_mainline_parser.add_argument("--target-prior-dir", default=None)
    recon_runtime_mainline_parser.add_argument("--shadow-decoder-dir", default=None)
    recon_runtime_mainline_parser.add_argument("--shadow-prior-dir", default=None)
    recon_runtime_mainline_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for runtime reconstruction artifacts and summaries",
    )
    recon_runtime_mainline_parser.add_argument(
        "--repo-root",
        default="external/Reconstruction-based-Attack",
        help="path to local reconstruction-based attack repository root",
    )
    recon_runtime_mainline_parser.add_argument(
        "--pretrained-model-name-or-path",
        default="runwayml/stable-diffusion-v1-5",
        help="base pretrained model identifier used by the upstream inference script",
    )
    recon_runtime_mainline_parser.add_argument(
        "--num-validation-images",
        type=int,
        default=3,
        help="number of images generated per query sample",
    )
    recon_runtime_mainline_parser.add_argument(
        "--inference-steps",
        type=int,
        default=30,
        help="number of diffusion steps used by the upstream inference script",
    )
    recon_runtime_mainline_parser.add_argument(
        "--gpu",
        type=int,
        default=0,
        help="GPU index passed to the embedding script",
    )
    recon_runtime_mainline_parser.add_argument(
        "--backend",
        default="stable_diffusion",
        help="runtime backend used to generate reconstruction images",
    )
    recon_runtime_mainline_parser.add_argument(
        "--scheduler",
        default="default",
        help="stable diffusion scheduler used by the upstream inference script",
    )
    recon_runtime_mainline_parser.add_argument(
        "--method",
        default="threshold",
        help="evaluation method passed to the upstream script",
    )
    recon_runtime_mainline_parser.add_argument(
        "--similarity-method",
        default="cosine",
        help="similarity method passed to cal_embedding.py",
    )
    recon_runtime_mainline_parser.add_argument(
        "--image-encoder",
        default="deit",
        help="image encoder passed to cal_embedding.py",
    )

    dit_sample_smoke_parser = subparsers.add_parser(
        "run-dit-sample-smoke",
        help="run the official DiT sample script and capture the generated sample image",
    )
    dit_sample_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for DiT sample smoke artifacts",
    )
    dit_sample_smoke_parser.add_argument(
        "--repo-root",
        default="external/DiT",
        help="path to local official DiT repository root",
    )
    dit_sample_smoke_parser.add_argument(
        "--model",
        default="DiT-XL/2",
        help="DiT model name passed to the official sample script",
    )
    dit_sample_smoke_parser.add_argument(
        "--image-size",
        type=int,
        default=256,
        help="image size passed to the official sample script",
    )
    dit_sample_smoke_parser.add_argument(
        "--num-sampling-steps",
        type=int,
        default=2,
        help="number of diffusion sampling steps",
    )
    dit_sample_smoke_parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="random seed passed to the official sample script",
    )
    dit_sample_smoke_parser.add_argument(
        "--ckpt",
        default=None,
        help="optional local DiT checkpoint path; omitted means the official auto-download path",
    )

    variation_synth_smoke_parser = subparsers.add_parser(
        "run-variation-synth-smoke",
        help="run a synthetic smoke for the API-only variation attack line",
    )
    variation_synth_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for variation synthetic smoke artifacts",
    )

    blackbox_status_parser = subparsers.add_parser(
        "summarize-blackbox-results",
        help="aggregate black-box experiment summaries into a single machine-readable report",
    )
    blackbox_status_parser.add_argument(
        "--experiments-root",
        required=True,
        help="root directory containing experiment summary subdirectories",
    )
    blackbox_status_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for the aggregated black-box status report",
    )

    mainline_audit_parser = subparsers.add_parser(
        "summarize-mainline-audit",
        help="build a mainline attack-defense audit report with actionable suggestions and next GPU guidance",
    )
    mainline_audit_parser.add_argument(
        "--research-root",
        default=".",
        help="root directory of the Research workspace",
    )
    mainline_audit_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for the aggregated mainline audit report",
    )
    mainline_audit_parser.add_argument(
        "--attack-defense-table",
        default=None,
        help="optional path to the admitted unified attack-defense table JSON",
    )

    pia_runtime_probe_parser = subparsers.add_parser(
        "runtime-probe-pia",
        help="validate PIA runtime readiness by loading modules, checkpoint and attacker",
    )
    pia_runtime_probe_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_runtime_probe_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_runtime_probe_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )
    pia_runtime_probe_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the runtime probe",
    )

    pia_runtime_preview_parser = subparsers.add_parser(
        "runtime-preview-pia",
        help="run a real-data PIA preview using member/non-member batches from the configured dataset root",
    )
    pia_runtime_preview_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_runtime_preview_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_runtime_preview_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )
    pia_runtime_preview_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the runtime preview",
    )
    pia_runtime_preview_parser.add_argument(
        "--preview-batch-size",
        type=int,
        default=2,
        help="number of member and non-member samples loaded for the runtime preview",
    )

    pia_packet_export_parser = subparsers.add_parser(
        "export-pia-packet-scores",
        help="export one CPU-first matched member/non-member PIA packet score scaffold",
    )
    pia_packet_export_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_packet_export_parser.add_argument("--workspace", required=True)
    pia_packet_export_parser.add_argument("--repo-root", default="external/PIA")
    pia_packet_export_parser.add_argument("--member-split-root", default="external/PIA/DDPM")
    pia_packet_export_parser.add_argument("--device", default="cpu")
    pia_packet_export_parser.add_argument("--packet-size", type=int, default=4)
    pia_packet_export_parser.add_argument("--member-offset", type=int, default=0)
    pia_packet_export_parser.add_argument("--nonmember-offset", type=int, default=0)
    pia_packet_export_parser.add_argument("--member-index-file", default=None)
    pia_packet_export_parser.add_argument("--nonmember-index-file", default=None)
    pia_packet_export_parser.add_argument("--batch-size", type=int, default=4)
    pia_packet_export_parser.add_argument("--adaptive-query-repeats", type=int, default=1)
    pia_packet_export_parser.add_argument("--provenance-status", default="workspace-verified")

    sima_packet_export_parser = subparsers.add_parser(
        "export-sima-packet-scores",
        help="export one CPU-first matched member/non-member SimA packet score scaffold",
    )
    sima_packet_export_parser.add_argument("--config", required=True, help="path to audit yaml")
    sima_packet_export_parser.add_argument("--workspace", required=True)
    sima_packet_export_parser.add_argument("--repo-root", default="external/PIA")
    sima_packet_export_parser.add_argument("--member-split-root", default="external/PIA/DDPM")
    sima_packet_export_parser.add_argument("--device", default="cpu")
    sima_packet_export_parser.add_argument("--packet-size", type=int, default=4)
    sima_packet_export_parser.add_argument("--member-offset", type=int, default=0)
    sima_packet_export_parser.add_argument("--nonmember-offset", type=int, default=0)
    sima_packet_export_parser.add_argument("--member-index-file", default=None)
    sima_packet_export_parser.add_argument("--nonmember-index-file", default=None)
    sima_packet_export_parser.add_argument("--batch-size", type=int, default=4)
    sima_packet_export_parser.add_argument("--timestep", type=int, default=20)
    sima_packet_export_parser.add_argument("--p-norm", type=float, default=4.0)
    sima_packet_export_parser.add_argument("--noise-seed", type=int, default=0)
    sima_packet_export_parser.add_argument("--provenance-status", default="workspace-verified")

    pia_translated_alias_parser = subparsers.add_parser(
        "export-pia-translated-alias-probe",
        help="export one CPU-first translated-contract alias probe on a frozen PIA member/non-member pair",
    )
    pia_translated_alias_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_translated_alias_parser.add_argument("--workspace", required=True)
    pia_translated_alias_parser.add_argument("--repo-root", default="external/PIA")
    pia_translated_alias_parser.add_argument("--member-split-root", default="external/PIA/DDPM")
    pia_translated_alias_parser.add_argument("--device", default="cpu")
    pia_translated_alias_parser.add_argument("--member-index", type=int, required=True)
    pia_translated_alias_parser.add_argument("--nonmember-index", type=int, required=True)
    pia_translated_alias_parser.add_argument("--batch-size", type=int, default=1)
    pia_translated_alias_parser.add_argument("--adaptive-query-repeats", type=int, default=1)
    pia_translated_alias_parser.add_argument("--alias-selector", default="middleblocks.0.attn.proj_v")
    pia_translated_alias_parser.add_argument("--translated-from", default="mid_block.attentions.0.to_v")
    pia_translated_alias_parser.add_argument("--channel-dim", type=int, default=1)
    pia_translated_alias_parser.add_argument("--mask-kind", default="top_abs_delta_k")
    pia_translated_alias_parser.add_argument("--k", type=int, default=8)
    pia_translated_alias_parser.add_argument("--alpha", type=float, default=0.5)
    pia_translated_alias_parser.add_argument("--mask-seed", type=int, default=0)
    pia_translated_alias_parser.add_argument("--alias-timestep", type=int, default=0)
    pia_translated_alias_parser.add_argument("--provenance-status", default="workspace-verified")

    runtime_probe_parser = subparsers.add_parser(
        "runtime-probe-secmi",
        help="validate SecMI runtime readiness by loading flags and model",
    )
    runtime_probe_parser.add_argument("--config", required=True, help="path to audit yaml")
    runtime_probe_parser.add_argument(
        "--repo-root",
        default="third_party/secmi",
        help="path to vendored or local SecMI repository root",
    )

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-secmi-smoke-assets",
        help="create synthetic SecMI smoke assets for local runtime probes",
    )
    bootstrap_parser.add_argument(
        "--target-dir",
        required=True,
        help="directory where smoke assets should be written",
    )
    bootstrap_parser.add_argument(
        "--flagfile-source",
        default="external/SecMI/config/CIFAR10.txt",
        help="path to the reference SecMI flagfile template",
    )

    pia_bootstrap_parser = subparsers.add_parser(
        "bootstrap-pia-smoke-assets",
        help="create synthetic PIA smoke assets for local runtime probes",
    )
    pia_bootstrap_parser.add_argument(
        "--target-dir",
        required=True,
        help="directory where smoke assets should be written",
    )
    pia_bootstrap_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )

    synth_smoke_parser = subparsers.add_parser(
        "run-secmi-synth-smoke",
        help="run a synthetic SecMI stat smoke execution",
    )
    synth_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for synthetic smoke artifacts",
    )
    synth_smoke_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the synthetic smoke run",
    )

    pia_synth_smoke_parser = subparsers.add_parser(
        "run-pia-synth-smoke",
        help="run a synthetic PIA smoke execution",
    )
    pia_synth_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for synthetic smoke artifacts",
    )
    pia_synth_smoke_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_synth_smoke_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the synthetic smoke run",
    )

    pia_runtime_smoke_parser = subparsers.add_parser(
        "run-pia-runtime-smoke",
        help="run a config-driven PIA runtime smoke with synthetic assets",
    )
    pia_runtime_smoke_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for runtime smoke artifacts",
    )
    pia_runtime_smoke_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_runtime_smoke_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the runtime smoke run",
    )

    pia_runtime_mainline_parser = subparsers.add_parser(
        "run-pia-runtime-mainline",
        help="run the canonical PIA DDPM path on real local assets and emit a reproducible summary",
    )
    pia_runtime_mainline_parser.add_argument("--config", required=True, help="path to audit yaml")
    pia_runtime_mainline_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for runtime mainline artifacts",
    )
    pia_runtime_mainline_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    pia_runtime_mainline_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )
    pia_runtime_mainline_parser.add_argument(
        "--device",
        default="cpu",
        help="device used for the runtime mainline run",
    )
    pia_runtime_mainline_parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="optional cap on member and non-member samples consumed per split",
    )
    pia_runtime_mainline_parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="batch size used while scoring member and non-member batches",
    )
    pia_runtime_mainline_parser.add_argument(
        "--stochastic-dropout-defense",
        action="store_true",
        help="enable stochastic dropout at inference time as a minimal gray-box defense prototype",
    )
    pia_runtime_mainline_parser.add_argument(
        "--dropout-activation-schedule",
        default="off",
        choices=["off", "all_steps", "late_steps_only"],
        help="when stochastic dropout is enabled, choose whether it stays on for all attack steps or only late steps",
    )
    pia_runtime_mainline_parser.add_argument(
        "--adaptive-query-repeats",
        type=int,
        default=1,
        help="repeat the same score query this many times and aggregate by mean for adaptive attacker review",
    )
    pia_runtime_mainline_parser.add_argument(
        "--epsilon-precision-bins",
        type=int,
        default=None,
        help="optional epsilon-output quantization bin count for precision-throttling defense review",
    )
    pia_runtime_mainline_parser.add_argument(
        "--late-step-threshold",
        type=int,
        default=None,
        help="optional timestep threshold used by late_steps_only dropout activation",
    )
    pia_runtime_mainline_parser.add_argument(
        "--provenance-status",
        default="source-retained-unverified",
        help="provenance label recorded in the emitted summary",
    )

    gsa_asset_probe_parser = subparsers.add_parser(
        "probe-gsa-assets",
        help="inspect white-box GSA dataset buckets, manifests and checkpoint-* readiness",
    )
    gsa_asset_probe_parser.add_argument(
        "--repo-root",
        default="external/GSA",
        help="path to local GSA repository root",
    )
    gsa_asset_probe_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa",
        help="path to the canonical white-box GSA assets root",
    )

    gsa_observability_probe_parser = subparsers.add_parser(
        "probe-gsa-observability-contract",
        help="validate the Finding NeMo migrated DDPM observability contract without exporting activations",
    )
    gsa_observability_probe_parser.add_argument(
        "--repo-root",
        default="external/GSA",
        help="path to local GSA repository root",
    )
    gsa_observability_probe_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
        help="path to the admitted GSA assets root used for observability planning",
    )
    gsa_observability_probe_parser.add_argument(
        "--checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
        help="path to the admitted target checkpoint root",
    )
    gsa_observability_probe_parser.add_argument(
        "--split",
        default="target-member",
        help="dataset split to resolve the sample binding against",
    )
    gsa_observability_probe_parser.add_argument(
        "--sample-id",
        required=True,
        help="sample id or compatibility alias resolved against the requested split",
    )
    gsa_observability_probe_parser.add_argument(
        "--layer-selector",
        default="mid_block.attentions.0.to_v",
        help="exact GSA/DDPM module selector used by the contract",
    )
    gsa_observability_probe_parser.add_argument(
        "--signal-type",
        default="activations",
        choices=["activations", "grad_norm"],
        help="signal type being validated by the contract",
    )
    gsa_observability_probe_parser.add_argument(
        "--resolution",
        type=int,
        default=32,
        help="UNet resolution used to reconstruct the module naming graph",
    )
    gsa_observability_probe_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
        help="provenance label recorded in the emitted payload",
    )

    gsa_observability_export_parser = subparsers.add_parser(
        "export-gsa-observability-canary",
        help="export one CPU-only sample-pair activation canary without authorizing any run release",
    )
    gsa_observability_export_parser.add_argument("--workspace", required=True)
    gsa_observability_export_parser.add_argument(
        "--repo-root",
        default="external/GSA",
        help="path to local GSA repository root",
    )
    gsa_observability_export_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
        help="path to the admitted GSA assets root used for observability planning",
    )
    gsa_observability_export_parser.add_argument(
        "--checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
        help="path to the admitted target checkpoint root",
    )
    gsa_observability_export_parser.add_argument("--checkpoint-dir", default=None)
    gsa_observability_export_parser.add_argument("--split", required=True)
    gsa_observability_export_parser.add_argument("--sample-id", required=True)
    gsa_observability_export_parser.add_argument("--control-split", required=True)
    gsa_observability_export_parser.add_argument("--control-sample-id", required=True)
    gsa_observability_export_parser.add_argument(
        "--layer-selector",
        default="mid_block.attentions.0.to_v",
        help="exact GSA/DDPM module selector used by the contract",
    )
    gsa_observability_export_parser.add_argument(
        "--signal-type",
        default="activations",
        choices=["activations"],
        help="signal type exported by the canary",
    )
    gsa_observability_export_parser.add_argument("--timestep", type=int, default=999)
    gsa_observability_export_parser.add_argument("--noise-seed", type=int, default=0)
    gsa_observability_export_parser.add_argument("--prediction-type", default="epsilon")
    gsa_observability_export_parser.add_argument("--device", default="cpu")
    gsa_observability_export_parser.add_argument("--resolution", type=int, default=32)
    gsa_observability_export_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
        help="provenance label recorded in the emitted payload",
    )

    gsa_masked_packet_parser = subparsers.add_parser(
        "export-gsa-observability-masked-packet",
        help="export one CPU-first masked white-box packet scaffold without authorizing any GPU release",
    )
    gsa_masked_packet_parser.add_argument("--workspace", required=True)
    gsa_masked_packet_parser.add_argument("--repo-root", default="external/GSA")
    gsa_masked_packet_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
    )
    gsa_masked_packet_parser.add_argument(
        "--checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
    )
    gsa_masked_packet_parser.add_argument("--checkpoint-dir", default=None)
    gsa_masked_packet_parser.add_argument("--split", required=True)
    gsa_masked_packet_parser.add_argument("--sample-id", required=True)
    gsa_masked_packet_parser.add_argument("--control-split", required=True)
    gsa_masked_packet_parser.add_argument("--control-sample-id", required=True)
    gsa_masked_packet_parser.add_argument("--layer-selector", default="mid_block.attentions.0.to_v")
    gsa_masked_packet_parser.add_argument(
        "--mask-kind",
        default="top_abs_delta_k",
        choices=["top_abs_delta_k", "random_k_seeded", "bottom_abs_delta_k"],
    )
    gsa_masked_packet_parser.add_argument("--k", type=int, default=8)
    gsa_masked_packet_parser.add_argument("--alpha", type=float, default=0.5)
    gsa_masked_packet_parser.add_argument("--timestep", type=int, default=999)
    gsa_masked_packet_parser.add_argument("--noise-seed", type=int, default=0)
    gsa_masked_packet_parser.add_argument("--mask-seed", type=int, default=0)
    gsa_masked_packet_parser.add_argument("--prediction-type", default="epsilon")
    gsa_masked_packet_parser.add_argument("--device", default="cpu")
    gsa_masked_packet_parser.add_argument("--resolution", type=int, default=32)
    gsa_masked_packet_parser.add_argument("--provenance-status", default="workspace-verified")

    gsa_inmodel_packet_parser = subparsers.add_parser(
        "export-gsa-observability-inmodel-packet",
        help="export one CPU-first in-model white-box packet canary without authorizing any GPU release",
    )
    gsa_inmodel_packet_parser.add_argument("--workspace", required=True)
    gsa_inmodel_packet_parser.add_argument("--repo-root", default="external/GSA")
    gsa_inmodel_packet_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
    )
    gsa_inmodel_packet_parser.add_argument(
        "--checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
    )
    gsa_inmodel_packet_parser.add_argument("--checkpoint-dir", default=None)
    gsa_inmodel_packet_parser.add_argument("--split", required=True)
    gsa_inmodel_packet_parser.add_argument("--sample-id", required=True)
    gsa_inmodel_packet_parser.add_argument("--control-split", required=True)
    gsa_inmodel_packet_parser.add_argument("--control-sample-id", required=True)
    gsa_inmodel_packet_parser.add_argument("--layer-selector", default="mid_block.attentions.0.to_v")
    gsa_inmodel_packet_parser.add_argument(
        "--mask-kind",
        default="top_abs_delta_k",
        choices=["top_abs_delta_k", "random_k_seeded", "bottom_abs_delta_k"],
    )
    gsa_inmodel_packet_parser.add_argument("--k", type=int, default=8)
    gsa_inmodel_packet_parser.add_argument("--alpha", type=float, default=0.5)
    gsa_inmodel_packet_parser.add_argument("--timestep", type=int, default=999)
    gsa_inmodel_packet_parser.add_argument("--noise-seed", type=int, default=0)
    gsa_inmodel_packet_parser.add_argument("--mask-seed", type=int, default=0)
    gsa_inmodel_packet_parser.add_argument("--prediction-type", default="epsilon")
    gsa_inmodel_packet_parser.add_argument("--device", default="cpu")
    gsa_inmodel_packet_parser.add_argument("--resolution", type=int, default=32)
    gsa_inmodel_packet_parser.add_argument("--provenance-status", default="workspace-verified")

    gsa_runtime_mainline_parser = subparsers.add_parser(
        "run-gsa-runtime-mainline",
        help="run the canonical white-box GSA DDPM closed loop against real local assets",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for white-box GSA runtime mainline artifacts",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--repo-root",
        default="external/GSA",
        help="path to local GSA repository root",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa",
        help="path to the canonical white-box GSA assets root",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--resolution",
        type=int,
        default=32,
        help="image resolution passed to the official GSA DDPM gradient extractor",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--ddpm-num-steps",
        type=int,
        default=20,
        help="DDPM steps passed to the official GSA DDPM gradient extractor",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--sampling-frequency",
        type=int,
        default=2,
        help="sampling frequency passed to the official GSA DDPM gradient extractor",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--attack-method",
        type=int,
        default=1,
        help="GSA attack method passed to the official DDPM gradient extractor",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--prediction-type",
        default="epsilon",
        help="prediction type passed to the official GSA DDPM gradient extractor",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="optional per-side evaluation cap applied to target/shadow member and nonmember gradients",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--paper-aligned",
        action="store_true",
        help="use stronger GSA defaults closer to the upstream paper path",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="device hint for GSA gradient extraction subprocesses",
    )
    gsa_runtime_mainline_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
        help="provenance label recorded in the emitted summary",
    )

    gsa_loss_score_export_parser = subparsers.add_parser(
        "export-gsa-loss-score-packet",
        help="export a bounded same-asset white-box loss-score packet without mutating admitted gradient mainline semantics",
    )
    gsa_loss_score_export_parser.add_argument("--workspace", required=True)
    gsa_loss_score_export_parser.add_argument(
        "--repo-root",
        default="external/GSA",
    )
    gsa_loss_score_export_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
    )
    gsa_loss_score_export_parser.add_argument("--resolution", type=int, default=32)
    gsa_loss_score_export_parser.add_argument("--ddpm-num-steps", type=int, default=20)
    gsa_loss_score_export_parser.add_argument("--sampling-frequency", type=int, default=2)
    gsa_loss_score_export_parser.add_argument("--attack-method", type=int, default=1)
    gsa_loss_score_export_parser.add_argument("--prediction-type", default="epsilon")
    gsa_loss_score_export_parser.add_argument("--extraction-max-samples", type=int, default=None)
    gsa_loss_score_export_parser.add_argument(
        "--sample-id-file",
        default=None,
        help="optional path to a text or JSON file listing sample IDs to export from each split",
    )
    gsa_loss_score_export_parser.add_argument(
        "--device",
        default="cpu",
        choices=["auto", "cpu", "cuda"],
    )
    gsa_loss_score_export_parser.add_argument("--provenance-status", default="workspace-verified")

    gsa_loss_score_eval_parser = subparsers.add_parser(
        "evaluate-gsa-loss-score-packet",
        help="evaluate a bounded threshold-style white-box packet from exported loss-score artifacts",
    )
    gsa_loss_score_eval_parser.add_argument("--workspace", required=True)
    gsa_loss_score_eval_parser.add_argument(
        "--packet-summary",
        required=True,
        help="path to a ready export-gsa-loss-score-packet summary.json artifact",
    )
    gsa_loss_score_eval_parser.add_argument(
        "--evaluation-style",
        default="threshold-transfer",
        choices=["threshold-transfer", "gaussian-likelihood-ratio-transfer"],
        help="score-evaluation surface to apply on the frozen exported packet",
    )
    gsa_loss_score_eval_parser.add_argument("--provenance-status", default="workspace-verified")

    crossbox_pairboard_parser = subparsers.add_parser(
        "analyze-crossbox-pairboard",
        help="build a shared-score pairboard from two cross-box score surfaces",
    )
    crossbox_pairboard_parser.add_argument("--workspace", required=True)
    crossbox_pairboard_parser.add_argument(
        "--surface-a",
        required=True,
        help="path to the first score surface JSON or GSA loss-score-export summary",
    )
    crossbox_pairboard_parser.add_argument(
        "--surface-b",
        required=True,
        help="path to the second score surface JSON or GSA loss-score-export summary",
    )
    crossbox_pairboard_parser.add_argument("--surface-a-name", default=None)
    crossbox_pairboard_parser.add_argument("--surface-b-name", default=None)
    crossbox_pairboard_parser.add_argument(
        "--surface-a-family",
        default=None,
        help="optional nested family key for family-scores style JSON payloads",
    )
    crossbox_pairboard_parser.add_argument(
        "--surface-b-family",
        default=None,
        help="optional nested family key for family-scores style JSON payloads",
    )
    crossbox_pairboard_parser.add_argument(
        "--calibration-fraction",
        type=float,
        default=0.5,
        help="fraction of each label bucket reserved for calibration",
    )
    crossbox_pairboard_parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="random seed used for calibration/test partitioning",
    )
    crossbox_pairboard_parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="number of stratified repeated holdout runs to evaluate",
    )
    crossbox_pairboard_parser.add_argument(
        "--tail-gated-cascade",
        action="store_true",
        help="enable bounded H4 tail-gated cascade on top of the pairboard candidates",
    )
    crossbox_pairboard_parser.add_argument("--cascade-anchor-name", default=None)
    crossbox_pairboard_parser.add_argument("--cascade-candidate-name", default="logistic_2feature")
    crossbox_pairboard_parser.add_argument("--cascade-route-fractions", default=None)
    crossbox_pairboard_parser.add_argument("--cascade-gammas", default=None)
    crossbox_pairboard_parser.add_argument("--cascade-secondary-cost-ratio", type=float, default=0.25)

    risk_targeted_unlearning_parser = subparsers.add_parser(
        "prepare-risk-targeted-unlearning-pilot",
        help="aggregate aligned GSA/PIA-style risk scores and export bounded forget/control lists for 04-H1",
    )
    risk_targeted_unlearning_parser.add_argument("--workspace", required=True)
    risk_targeted_unlearning_parser.add_argument(
        "--surface-a",
        required=True,
        help="path to the first score surface JSON or GSA loss-score-export summary",
    )
    risk_targeted_unlearning_parser.add_argument(
        "--surface-b",
        required=True,
        help="path to the second score surface JSON or GSA loss-score-export summary",
    )
    risk_targeted_unlearning_parser.add_argument("--surface-a-name", default=None)
    risk_targeted_unlearning_parser.add_argument("--surface-b-name", default=None)
    risk_targeted_unlearning_parser.add_argument("--surface-a-family", default=None)
    risk_targeted_unlearning_parser.add_argument("--surface-b-family", default=None)
    risk_targeted_unlearning_parser.add_argument("--weight-a", type=float, default=0.5)
    risk_targeted_unlearning_parser.add_argument("--weight-b", type=float, default=0.5)
    risk_targeted_unlearning_parser.add_argument("--top-fraction", type=float, default=0.1)
    risk_targeted_unlearning_parser.add_argument(
        "--top-k",
        default="16,32,64",
        help="comma-separated forget-set sizes to export",
    )
    risk_targeted_unlearning_parser.add_argument("--provenance-status", default="workspace-verified")

    risk_targeted_unlearning_pilot_parser = subparsers.add_parser(
        "run-risk-targeted-unlearning-pilot",
        help="run one bounded retain+forget training pilot on current DDPM/CIFAR10 admitted assets",
    )
    risk_targeted_unlearning_pilot_parser.add_argument("--workspace", required=True)
    risk_targeted_unlearning_pilot_parser.add_argument(
        "--member-dataset-dir",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/datasets/target-member",
    )
    risk_targeted_unlearning_pilot_parser.add_argument("--forget-member-index-file", required=True)
    risk_targeted_unlearning_pilot_parser.add_argument("--matched-nonmember-index-file", default=None)
    risk_targeted_unlearning_pilot_parser.add_argument(
        "--checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
    )
    risk_targeted_unlearning_pilot_parser.add_argument("--checkpoint-dir", default=None)
    risk_targeted_unlearning_pilot_parser.add_argument(
        "--random-init",
        action="store_true",
        help="use a random DDPM initialization instead of loading a target checkpoint",
    )
    risk_targeted_unlearning_pilot_parser.add_argument("--retain-max-samples", type=int, default=None)
    risk_targeted_unlearning_pilot_parser.add_argument("--forget-max-samples", type=int, default=None)
    risk_targeted_unlearning_pilot_parser.add_argument("--num-steps", type=int, default=100)
    risk_targeted_unlearning_pilot_parser.add_argument("--batch-size", type=int, default=4)
    risk_targeted_unlearning_pilot_parser.add_argument("--num-workers", type=int, default=0)
    risk_targeted_unlearning_pilot_parser.add_argument("--lr", type=float, default=1e-5)
    risk_targeted_unlearning_pilot_parser.add_argument("--alpha", type=float, default=0.5)
    risk_targeted_unlearning_pilot_parser.add_argument("--mixture-lambda", type=float, default=0.5)
    risk_targeted_unlearning_pilot_parser.add_argument("--grad-clip", type=float, default=1.0)
    risk_targeted_unlearning_pilot_parser.add_argument("--resolution", type=int, default=32)
    risk_targeted_unlearning_pilot_parser.add_argument("--ddpm-num-train-timesteps", type=int, default=1000)
    risk_targeted_unlearning_pilot_parser.add_argument("--device", default="cuda")
    risk_targeted_unlearning_pilot_parser.add_argument("--seed", type=int, default=0)
    risk_targeted_unlearning_pilot_parser.add_argument("--provenance-status", default="workspace-verified")

    risk_targeted_unlearning_review_parser = subparsers.add_parser(
        "review-risk-targeted-unlearning-pilot",
        help="run one attack-side subset review for baseline vs defended 04-H1 target checkpoints",
    )
    risk_targeted_unlearning_review_parser.add_argument("--workspace", required=True)
    risk_targeted_unlearning_review_parser.add_argument(
        "--shadow-reference-summary",
        required=True,
        help="ready undefended GSA loss-score-export summary used only for borrowed shadow threshold transfer",
    )
    risk_targeted_unlearning_review_parser.add_argument(
        "--target-member-dataset-dir",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/datasets/target-member",
    )
    risk_targeted_unlearning_review_parser.add_argument(
        "--target-nonmember-dataset-dir",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/datasets/target-nonmember",
    )
    risk_targeted_unlearning_review_parser.add_argument(
        "--baseline-checkpoint-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target",
    )
    risk_targeted_unlearning_review_parser.add_argument("--baseline-checkpoint-dir", default=None)
    risk_targeted_unlearning_review_parser.add_argument("--defended-checkpoint-dir", required=True)
    risk_targeted_unlearning_review_parser.add_argument("--forget-member-index-file", default=None)
    risk_targeted_unlearning_review_parser.add_argument("--matched-nonmember-index-file", default=None)
    risk_targeted_unlearning_review_parser.add_argument("--resolution", type=int, default=32)
    risk_targeted_unlearning_review_parser.add_argument("--ddpm-num-steps", type=int, default=20)
    risk_targeted_unlearning_review_parser.add_argument("--sampling-frequency", type=int, default=2)
    risk_targeted_unlearning_review_parser.add_argument("--attack-method", type=int, default=1)
    risk_targeted_unlearning_review_parser.add_argument("--prediction-type", default="epsilon")
    risk_targeted_unlearning_review_parser.add_argument("--device", default="cuda")
    risk_targeted_unlearning_review_parser.add_argument("--noise-seed", type=int, default=None)
    risk_targeted_unlearning_review_parser.add_argument("--provenance-status", default="workspace-verified")

    temporal_surrogate_export_parser = subparsers.add_parser(
        "export-temporal-surrogate-feature-packet",
        help="export one target-only temporal feature packet for 06-H1 teacher-calibrated surrogate scoping",
    )
    temporal_surrogate_export_parser.add_argument("--config", required=True, help="path to audit yaml")
    temporal_surrogate_export_parser.add_argument("--workspace", required=True)
    temporal_surrogate_export_parser.add_argument(
        "--repo-root",
        default="external/PIA",
        help="path to local PIA repository root",
    )
    temporal_surrogate_export_parser.add_argument(
        "--member-split-root",
        default="external/PIA/DDPM",
        help="path to PIA DDPM member split npz files",
    )
    temporal_surrogate_export_parser.add_argument("--device", default="cpu")
    temporal_surrogate_export_parser.add_argument("--max-samples", type=int, default=None)
    temporal_surrogate_export_parser.add_argument("--batch-size", type=int, default=8)
    temporal_surrogate_export_parser.add_argument("--scan-timesteps", nargs="+", type=int, default=None)
    temporal_surrogate_export_parser.add_argument("--noise-seed", type=int, default=0)
    temporal_surrogate_export_parser.add_argument("--timestep-jitter-radius", type=int, default=0)
    temporal_surrogate_export_parser.add_argument("--timestep-stride", type=int, default=1)
    temporal_surrogate_export_parser.add_argument("--provenance-status", default="workspace-verified")

    temporal_surrogate_eval_parser = subparsers.add_parser(
        "evaluate-temporal-surrogate-packets",
        help="fit and evaluate one teacher-calibrated temporal surrogate packet for 06-H1",
    )
    temporal_surrogate_eval_parser.add_argument("--workspace", required=True)
    temporal_surrogate_eval_parser.add_argument("--teacher-feature-packet", required=True)
    temporal_surrogate_eval_parser.add_argument("--teacher-score-surface", required=True)
    temporal_surrogate_eval_parser.add_argument("--teacher-score-family", default=None)
    temporal_surrogate_eval_parser.add_argument("--transfer-feature-packet", default=None)
    temporal_surrogate_eval_parser.add_argument("--bag-count", type=int, default=8)
    temporal_surrogate_eval_parser.add_argument(
        "--quantiles",
        nargs="+",
        type=float,
        default=[0.2, 0.35, 0.5, 0.65, 0.8],
    )
    temporal_surrogate_eval_parser.add_argument("--l2-alpha", type=float, default=0.01)
    temporal_surrogate_eval_parser.add_argument("--cv-splits", type=int, default=4)
    temporal_surrogate_eval_parser.add_argument("--cv-repeats", type=int, default=2)
    temporal_surrogate_eval_parser.add_argument("--random-seed", type=int, default=0)
    temporal_surrogate_eval_parser.add_argument("--provenance-status", default="workspace-verified")

    temporal_lr_eval_parser = subparsers.add_parser(
        "evaluate-temporal-lr-packets",
        help="evaluate one fixed temporal likelihood-ratio fallback packet for 06-H2",
    )
    temporal_lr_eval_parser.add_argument("--workspace", required=True)
    temporal_lr_eval_parser.add_argument("--calibration-feature-packet", required=True)
    temporal_lr_eval_parser.add_argument("--transfer-feature-packet", default=None)
    temporal_lr_eval_parser.add_argument("--primary-candidate", default="eps_abs_mean_late")
    temporal_lr_eval_parser.add_argument("--sensitivity-candidate", default="eps_abs_late_over_early")
    temporal_lr_eval_parser.add_argument("--cv-splits", type=int, default=4)
    temporal_lr_eval_parser.add_argument("--cv-repeats", type=int, default=2)
    temporal_lr_eval_parser.add_argument("--random-seed", type=int, default=0)
    temporal_lr_eval_parser.add_argument("--provenance-status", default="workspace-verified")

    gsa_runtime_intervention_review_parser = subparsers.add_parser(
        "run-gsa-runtime-intervention-review",
        help="run a bounded baseline/intervened white-box GSA review with one frozen target-anchored mask",
    )
    gsa_runtime_intervention_review_parser.add_argument("--workspace", required=True)
    gsa_runtime_intervention_review_parser.add_argument(
        "--repo-root",
        default="external/GSA",
    )
    gsa_runtime_intervention_review_parser.add_argument(
        "--assets-root",
        default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
    )
    gsa_runtime_intervention_review_parser.add_argument(
        "--mask-summary",
        required=True,
        help="path to the frozen target-anchored in-model packet summary containing mask channel indices",
    )
    gsa_runtime_intervention_review_parser.add_argument("--resolution", type=int, default=32)
    gsa_runtime_intervention_review_parser.add_argument("--ddpm-num-steps", type=int, default=20)
    gsa_runtime_intervention_review_parser.add_argument("--sampling-frequency", type=int, default=2)
    gsa_runtime_intervention_review_parser.add_argument("--attack-method", type=int, default=1)
    gsa_runtime_intervention_review_parser.add_argument("--prediction-type", default="epsilon")
    gsa_runtime_intervention_review_parser.add_argument("--max-samples", type=int, default=None)
    gsa_runtime_intervention_review_parser.add_argument("--extraction-max-samples", type=int, default=None)
    gsa_runtime_intervention_review_parser.add_argument(
        "--paper-aligned",
        action="store_true",
        help="use stronger GSA defaults closer to the upstream paper path",
    )
    gsa_runtime_intervention_review_parser.add_argument(
        "--device",
        default="cpu",
        choices=["auto", "cpu", "cuda"],
    )
    gsa_runtime_intervention_review_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
    )

    dpdm_w1_target_only_parser = subparsers.add_parser(
        "run-dpdm-w1-target-only",
        help="run a defense-native target-only white-box comparator for a DPDM W-1 checkpoint",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--workspace",
        required=True,
        help="workspace directory for DPDM W-1 comparator artifacts",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--checkpoint-path",
        required=True,
        help="path to the DPDM checkpoint file",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--member-dataset-dir",
        required=True,
        help="path to member images used for target-only comparison",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--nonmember-dataset-dir",
        required=True,
        help="path to non-member images used for target-only comparison",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--dpdm-root",
        default="external/DPDM",
        help="path to the local DPDM repository root",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--config-path",
        default="external/DPDM/configs/cifar10_32/train_eps_10.0.yaml",
        help="path to the DPDM config used to instantiate the model",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--device",
        default="cuda",
        choices=["cpu", "cuda"],
        help="device used for DPDM target-only comparison",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--sigma-points",
        type=int,
        default=8,
        help="number of deterministic sigma points used per sample",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--max-samples",
        type=int,
        default=128,
        help="optional cap on member and non-member sample counts",
    )
    dpdm_w1_target_only_parser.add_argument(
        "--provenance-status",
        default="workspace-verified",
        help="provenance label recorded in the emitted summary",
    )

    dpdm_w1_shadow_parser = subparsers.add_parser(
        "run-dpdm-w1-shadow-comparator",
        help="run a defended shadow-trained white-box comparator for DPDM W-1 checkpoints",
    )
    dpdm_w1_shadow_parser.add_argument("--workspace", required=True)
    dpdm_w1_shadow_parser.add_argument("--target-checkpoint-path", required=True)
    dpdm_w1_shadow_parser.add_argument("--shadow-checkpoint-path", required=True)
    dpdm_w1_shadow_parser.add_argument("--target-member-dataset-dir", required=True)
    dpdm_w1_shadow_parser.add_argument("--target-nonmember-dataset-dir", required=True)
    dpdm_w1_shadow_parser.add_argument("--shadow-member-dataset-dir", required=True)
    dpdm_w1_shadow_parser.add_argument("--shadow-nonmember-dataset-dir", required=True)
    dpdm_w1_shadow_parser.add_argument("--dpdm-root", default="external/DPDM")
    dpdm_w1_shadow_parser.add_argument(
        "--config-path",
        default="external/DPDM/configs/cifar10_32/train_eps_10.0.yaml",
    )
    dpdm_w1_shadow_parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    dpdm_w1_shadow_parser.add_argument("--sigma-points", type=int, default=8)
    dpdm_w1_shadow_parser.add_argument("--max-samples", type=int, default=128)
    dpdm_w1_shadow_parser.add_argument("--provenance-status", default="workspace-verified")

    dpdm_w1_multi_shadow_parser = subparsers.add_parser(
        "run-dpdm-w1-multi-shadow-comparator",
        help="run a defended multi-shadow white-box comparator for DPDM W-1 checkpoints",
    )
    dpdm_w1_multi_shadow_parser.add_argument("--workspace", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--target-checkpoint-path", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--shadow-checkpoint-paths", nargs="+", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--target-member-dataset-dir", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--target-nonmember-dataset-dir", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--shadow-member-dataset-dirs", nargs="+", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--shadow-nonmember-dataset-dirs", nargs="+", required=True)
    dpdm_w1_multi_shadow_parser.add_argument("--dpdm-root", default="external/DPDM")
    dpdm_w1_multi_shadow_parser.add_argument(
        "--config-path",
        default="external/DPDM/configs/cifar10_32/train_eps_10.0.yaml",
    )
    dpdm_w1_multi_shadow_parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    dpdm_w1_multi_shadow_parser.add_argument("--sigma-points", type=int, default=8)
    dpdm_w1_multi_shadow_parser.add_argument("--max-samples", type=int, default=128)
    dpdm_w1_multi_shadow_parser.add_argument("--provenance-status", default="workspace-verified")

    return parser
