"""Command-line interface for research audit workflows."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from diffaudit.config import load_audit_config
from diffaudit.cli._parser import build_parser


CommandHandler = Callable[[Any], int]


def _handle_foundation(args: Any) -> int:
    if args.command == "run-smoke":
        from diffaudit.pipelines.smoke import run_smoke_pipeline

        config = load_audit_config(args.config)
        summary_path = run_smoke_pipeline(config, Path(args.workspace))
        print(f"Smoke summary written to {summary_path}")
        return 0


    if args.command == "plan-secmi":
        from diffaudit.attacks.secmi import build_secmi_plan

        config = load_audit_config(args.config)
        plan = build_secmi_plan(config)
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=True))
        return 0


    if args.command == "plan-pia":
        from diffaudit.attacks.pia import build_pia_plan

        config = load_audit_config(args.config)
        plan = build_pia_plan(config)
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=True))
        return 0


    if args.command == "plan-clid":
        from diffaudit.attacks.clid import build_clid_plan

        config = load_audit_config(args.config)
        plan = build_clid_plan(config)
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=True))
        return 0


    if args.command == "plan-recon":
        from diffaudit.attacks.recon import build_recon_plan

        config = load_audit_config(args.config)
        plan = build_recon_plan(config)
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=True))
        return 0


    if args.command == "plan-variation":
        from diffaudit.attacks.variation import build_variation_plan

        config = load_audit_config(args.config)
        plan = build_variation_plan(config)
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=True))
        return 0


    raise RuntimeError(f"Unsupported foundation command: {args.command}")


def _handle_asset_probes(args: Any) -> int:
    if args.command == "probe-secmi-assets":
        from diffaudit.attacks.secmi import explain_secmi_assets

        config = load_audit_config(args.config)
        payload = explain_secmi_assets(config, member_split_root=args.member_split_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-pia-assets":
        from diffaudit.attacks.pia import explain_pia_assets

        config = load_audit_config(args.config)
        payload = explain_pia_assets(config, member_split_root=args.member_split_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-rediffuse-assets":
        from diffaudit.attacks.rediffuse import explain_rediffuse_assets

        payload = explain_rediffuse_assets(
            bundle_root=args.bundle_root,
            checkpoint_path=args.checkpoint_path,
            dataset_root=args.dataset_root,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-clid-assets":
        from diffaudit.attacks.clid import explain_clid_assets

        config = load_audit_config(args.config)
        payload = explain_clid_assets(config)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-recon-assets":
        from diffaudit.attacks.recon import explain_recon_assets

        config = load_audit_config(args.config)
        payload = explain_recon_assets(config)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-recon-score-artifacts":
        from diffaudit.attacks.recon import probe_recon_score_artifacts

        payload = probe_recon_score_artifacts(args.artifact_dir)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-recon-runtime-assets":
        from diffaudit.attacks.recon import probe_recon_runtime_assets

        payload = probe_recon_runtime_assets(
            target_member_dataset=args.target_member_dataset,
            target_nonmember_dataset=args.target_nonmember_dataset,
            shadow_member_dataset=args.shadow_member_dataset,
            shadow_nonmember_dataset=args.shadow_nonmember_dataset,
            target_model_dir=args.target_model_dir,
            shadow_model_dir=args.shadow_model_dir,
            backend=args.backend,
            target_decoder_dir=args.target_decoder_dir,
            target_prior_dir=args.target_prior_dir,
            shadow_decoder_dir=args.shadow_decoder_dir,
            shadow_prior_dir=args.shadow_prior_dir,
            repo_root=args.repo_root,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "prepare-recon-public-subset":
        from diffaudit.attacks.recon import prepare_recon_public_subset

        payload = prepare_recon_public_subset(
            bundle_root=args.bundle_root,
            output_dir=args.output_dir,
            target_count=args.target_count,
            shadow_count=args.shadow_count,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "audit-recon-public-bundle":
        from diffaudit.attacks.recon import audit_recon_public_bundle

        payload = audit_recon_public_bundle(bundle_root=args.bundle_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "check-recon-stage0-paper-gate":
        from diffaudit.attacks.recon import check_recon_stage0_paper_gate

        payload = check_recon_stage0_paper_gate(
            repo_root=args.repo_root,
            bundle_root=args.bundle_root,
            attack_scenario=args.attack_scenario,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-dit-assets":
        from diffaudit.attacks.dit import probe_dit_assets

        payload = probe_dit_assets(
            repo_root=args.repo_root,
            ckpt=args.ckpt,
            model=args.model,
            image_size=args.image_size,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-variation-assets":
        from diffaudit.attacks.variation import explain_variation_assets

        config = load_audit_config(args.config)
        payload = explain_variation_assets(config)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-h2-assets":
        from diffaudit.defenses.h2_adapter import probe_h2_assets

        payload = probe_h2_assets(
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            member_dataset_dir=args.member_dataset_dir,
            nonmember_dataset_dir=args.nonmember_dataset_dir,
            packet_cap=args.packet_cap,
            max_layout_checks=args.max_layout_checks,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "prepare-h2-contract":
        from diffaudit.defenses.h2_adapter import prepare_h2_contract

        payload = prepare_h2_contract(
            workspace=args.workspace,
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            member_dataset_dir=args.member_dataset_dir,
            nonmember_dataset_dir=args.nonmember_dataset_dir,
            packet_cap=args.packet_cap,
            max_layout_checks=args.max_layout_checks,
            rank=args.rank,
            alpha=args.alpha,
            lambda_coeff=args.lambda_coeff,
            delta=args.delta,
            lora_lr=args.lora_lr,
            proxy_lr=args.proxy_lr,
            optimizer=args.optimizer,
            sgd_momentum=args.sgd_momentum,
            proxy_hidden_dim=args.proxy_hidden_dim,
            proxy_steps=args.proxy_steps,
            num_epochs=args.num_epochs,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
            method=args.method,
            device=args.device,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported asset_probes command: {args.command}")


def _handle_gsa_observability(args: Any) -> int:
    if args.command == "probe-gsa-assets":
        from diffaudit.attacks.gsa import probe_gsa_assets

        payload = probe_gsa_assets(
            assets_root=args.assets_root,
            repo_root=args.repo_root,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "probe-gsa-observability-contract":
        from diffaudit.attacks.gsa_observability import probe_gsa_observability_contract

        payload = probe_gsa_observability_contract(
            repo_root=args.repo_root,
            assets_root=args.assets_root,
            checkpoint_root=args.checkpoint_root,
            split=args.split,
            sample_id=args.sample_id,
            layer_selector=args.layer_selector,
            signal_type=args.signal_type,
            resolution=args.resolution,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-gsa-observability-canary":
        from diffaudit.attacks.gsa_observability import export_gsa_observability_canary

        payload = export_gsa_observability_canary(
            workspace=args.workspace,
            repo_root=args.repo_root,
            assets_root=args.assets_root,
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            split=args.split,
            sample_id=args.sample_id,
            control_split=args.control_split,
            control_sample_id=args.control_sample_id,
            layer_selector=args.layer_selector,
            signal_type=args.signal_type,
            timestep=args.timestep,
            noise_seed=args.noise_seed,
            prediction_type=args.prediction_type,
            device=args.device,
            resolution=args.resolution,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-gsa-observability-masked-packet":
        from diffaudit.attacks.gsa_observability import export_gsa_observability_masked_packet

        payload = export_gsa_observability_masked_packet(
            workspace=args.workspace,
            repo_root=args.repo_root,
            assets_root=args.assets_root,
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            split=args.split,
            sample_id=args.sample_id,
            control_split=args.control_split,
            control_sample_id=args.control_sample_id,
            layer_selector=args.layer_selector,
            mask_kind=args.mask_kind,
            k=args.k,
            alpha=args.alpha,
            timestep=args.timestep,
            noise_seed=args.noise_seed,
            mask_seed=args.mask_seed,
            prediction_type=args.prediction_type,
            device=args.device,
            resolution=args.resolution,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-gsa-observability-inmodel-packet":
        from diffaudit.attacks.gsa_observability import export_gsa_observability_inmodel_packet

        payload = export_gsa_observability_inmodel_packet(
            workspace=args.workspace,
            repo_root=args.repo_root,
            assets_root=args.assets_root,
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            split=args.split,
            sample_id=args.sample_id,
            control_split=args.control_split,
            control_sample_id=args.control_sample_id,
            layer_selector=args.layer_selector,
            mask_kind=args.mask_kind,
            k=args.k,
            alpha=args.alpha,
            timestep=args.timestep,
            noise_seed=args.noise_seed,
            mask_seed=args.mask_seed,
            prediction_type=args.prediction_type,
            device=args.device,
            resolution=args.resolution,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported gsa_observability command: {args.command}")


def _handle_h2_defense(args: Any) -> int:
    if args.command == "run-h2-defense-pilot":
        from diffaudit.defenses.h2_adapter import run_h2_defense_pilot

        payload = run_h2_defense_pilot(
            workspace=args.workspace,
            manifest_path=args.manifest,
            member_limit=args.member_limit,
            nonmember_limit=args.nonmember_limit,
            seed=args.seed,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "review-h2-defense-pilot":
        from diffaudit.defenses.h2_adapter import review_h2_defense_pilot

        payload = review_h2_defense_pilot(
            workspace=args.workspace,
            run_summary_path=args.run_summary,
            shadow_reference_summary=args.shadow_reference_summary,
            device=args.device,
            noise_seed=args.noise_seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported h2_defense command: {args.command}")


def _handle_dry_runs(args: Any) -> int:
    if args.command == "prepare-secmi":
        from diffaudit.attacks.secmi_adapter import prepare_secmi_adapter, summarize_secmi_adapter

        config = load_audit_config(args.config)
        context = prepare_secmi_adapter(config, args.repo_root)
        print(json.dumps(summarize_secmi_adapter(context), indent=2, ensure_ascii=True))
        return 0


    if args.command == "dry-run-secmi":
        from diffaudit.attacks.secmi_adapter import probe_secmi_dry_run

        config = load_audit_config(args.config)
        exit_code, payload = probe_secmi_dry_run(config, args.repo_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "dry-run-pia":
        from diffaudit.attacks.pia import probe_pia_dry_run

        config = load_audit_config(args.config)
        exit_code, payload = probe_pia_dry_run(
            config,
            args.repo_root,
            member_split_root=args.member_split_root,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "dry-run-clid":
        from diffaudit.attacks.clid import probe_clid_dry_run

        config = load_audit_config(args.config)
        exit_code, payload = probe_clid_dry_run(config, args.repo_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "dry-run-recon":
        from diffaudit.attacks.recon import probe_recon_dry_run

        config = load_audit_config(args.config)
        exit_code, payload = probe_recon_dry_run(config, args.repo_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "dry-run-variation":
        from diffaudit.attacks.variation import probe_variation_dry_run

        config = load_audit_config(args.config)
        exit_code, payload = probe_variation_dry_run(config)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "run-clid-dry-run-smoke":
        from diffaudit.attacks.clid import run_clid_dry_run_smoke

        payload = run_clid_dry_run_smoke(
            args.workspace,
            repo_root=args.repo_root,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "summarize-clid-artifacts":
        from diffaudit.attacks.clid import summarize_clid_artifacts

        payload = summarize_clid_artifacts(
            artifact_dir=args.artifact_dir,
            workspace=args.workspace,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    raise RuntimeError(f"Unsupported dry_runs command: {args.command}")


def _handle_recon_and_synthetic(args: Any) -> int:
    if args.command == "run-recon-eval-smoke":
        from diffaudit.attacks.recon import run_recon_eval_smoke

        payload = run_recon_eval_smoke(args.workspace)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "summarize-recon-artifacts":
        from diffaudit.attacks.recon import summarize_recon_artifacts

        payload = summarize_recon_artifacts(
            artifact_dir=args.artifact_dir,
            workspace=args.workspace,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "run-recon-upstream-eval-smoke":
        from diffaudit.attacks.recon import run_recon_upstream_eval_smoke

        payload = run_recon_upstream_eval_smoke(
            args.workspace,
            repo_root=args.repo_root,
            method=args.method,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-recon-mainline-smoke":
        from diffaudit.attacks.recon import run_recon_mainline_smoke

        payload = run_recon_mainline_smoke(
            args.workspace,
            repo_root=args.repo_root,
            method=args.method,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-recon-artifact-mainline":
        from diffaudit.attacks.recon import run_recon_artifact_mainline

        payload = run_recon_artifact_mainline(
            artifact_dir=args.artifact_dir,
            workspace=args.workspace,
            repo_root=args.repo_root,
            method=args.method,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-recon-runtime-mainline":
        from diffaudit.attacks.recon import run_recon_runtime_mainline

        payload = run_recon_runtime_mainline(
            target_member_dataset=args.target_member_dataset,
            target_nonmember_dataset=args.target_nonmember_dataset,
            shadow_member_dataset=args.shadow_member_dataset,
            shadow_nonmember_dataset=args.shadow_nonmember_dataset,
            target_model_dir=args.target_model_dir,
            shadow_model_dir=args.shadow_model_dir,
            workspace=args.workspace,
            repo_root=args.repo_root,
            pretrained_model_name_or_path=args.pretrained_model_name_or_path,
            num_validation_images=args.num_validation_images,
            inference_steps=args.inference_steps,
            gpu=args.gpu,
            backend=args.backend,
            scheduler=args.scheduler,
            target_decoder_dir=args.target_decoder_dir,
            target_prior_dir=args.target_prior_dir,
            shadow_decoder_dir=args.shadow_decoder_dir,
            shadow_prior_dir=args.shadow_prior_dir,
            method=args.method,
            similarity_method=args.similarity_method,
            image_encoder=args.image_encoder,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-dit-sample-smoke":
        from diffaudit.attacks.dit import run_dit_sample_smoke

        payload = run_dit_sample_smoke(
            workspace=args.workspace,
            repo_root=args.repo_root,
            model=args.model,
            image_size=args.image_size,
            num_sampling_steps=args.num_sampling_steps,
            seed=args.seed,
            ckpt=args.ckpt,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-variation-synth-smoke":
        from diffaudit.attacks.variation import run_variation_synthetic_smoke

        payload = run_variation_synthetic_smoke(args.workspace)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    raise RuntimeError(f"Unsupported recon_and_synthetic command: {args.command}")


def _handle_reports(args: Any) -> int:
    if args.command == "summarize-blackbox-results":
        from diffaudit.reports.blackbox_status import build_blackbox_status_report

        payload = build_blackbox_status_report(
            experiments_root=args.experiments_root,
            workspace=args.workspace,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "summarize-mainline-audit":
        from diffaudit.reports.mainline_audit import build_mainline_audit_report

        payload = build_mainline_audit_report(
            research_root=args.research_root,
            workspace=args.workspace,
            attack_defense_table_path=args.attack_defense_table,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    raise RuntimeError(f"Unsupported reports command: {args.command}")


def _handle_pia_runtime(args: Any) -> int:
    if args.command == "runtime-probe-pia":
        from diffaudit.attacks.pia_adapter import probe_pia_runtime

        config = load_audit_config(args.config)
        exit_code, payload = probe_pia_runtime(
            config,
            args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "runtime-probe-rediffuse":
        from diffaudit.attacks.rediffuse_adapter import probe_rediffuse_runtime

        exit_code, payload = probe_rediffuse_runtime(
            bundle_root=args.bundle_root,
            checkpoint_path=args.checkpoint_path,
            dataset_root=args.dataset_root,
            device=args.device,
            attack_num=args.attack_num,
            interval=args.interval,
            average=args.average,
            k=args.k,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "runtime-preview-pia":
        from diffaudit.attacks.pia_adapter import probe_pia_runtime_preview

        config = load_audit_config(args.config)
        exit_code, payload = probe_pia_runtime_preview(
            config,
            args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            preview_batch_size=args.preview_batch_size,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "export-pia-packet-scores":
        from diffaudit.attacks.pia_adapter import export_pia_packet_scores

        config = load_audit_config(args.config)
        payload = export_pia_packet_scores(
            config,
            workspace=args.workspace,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            packet_size=args.packet_size,
            member_offset=args.member_offset,
            nonmember_offset=args.nonmember_offset,
            member_index_file=args.member_index_file,
            nonmember_index_file=args.nonmember_index_file,
            batch_size=args.batch_size,
            adaptive_query_repeats=args.adaptive_query_repeats,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-sima-packet-scores":
        from diffaudit.attacks.sima_adapter import export_sima_packet_scores

        config = load_audit_config(args.config)
        payload = export_sima_packet_scores(
            config,
            workspace=args.workspace,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            packet_size=args.packet_size,
            member_offset=args.member_offset,
            nonmember_offset=args.nonmember_offset,
            member_index_file=args.member_index_file,
            nonmember_index_file=args.nonmember_index_file,
            batch_size=args.batch_size,
            timestep=args.timestep,
            p_norm=args.p_norm,
            noise_seed=args.noise_seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-pia-translated-alias-probe":
        from diffaudit.attacks.pia_adapter import export_pia_translated_alias_probe

        config = load_audit_config(args.config)
        payload = export_pia_translated_alias_probe(
            config,
            workspace=args.workspace,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            member_index=args.member_index,
            nonmember_index=args.nonmember_index,
            batch_size=args.batch_size,
            adaptive_query_repeats=args.adaptive_query_repeats,
            alias_selector=args.alias_selector,
            translated_from=args.translated_from,
            channel_dim=args.channel_dim,
            mask_kind=args.mask_kind,
            k=args.k,
            alpha=args.alpha,
            mask_seed=args.mask_seed,
            alias_timestep=args.alias_timestep,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported pia_runtime command: {args.command}")


def _handle_secmi_pia_smokes(args: Any) -> int:
    if args.command == "runtime-probe-secmi":
        from diffaudit.attacks.secmi_adapter import probe_secmi_runtime

        config = load_audit_config(args.config)
        exit_code, payload = probe_secmi_runtime(config, args.repo_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code


    if args.command == "bootstrap-secmi-smoke-assets":
        from diffaudit.attacks.secmi_adapter import bootstrap_secmi_smoke_assets

        payload = bootstrap_secmi_smoke_assets(args.target_dir, args.flagfile_source)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "bootstrap-pia-smoke-assets":
        from diffaudit.attacks.pia_adapter import bootstrap_pia_smoke_assets

        payload = bootstrap_pia_smoke_assets(args.target_dir, args.repo_root)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "run-secmi-synth-smoke":
        from diffaudit.attacks.secmi_adapter import run_synthetic_secmi_stat_smoke

        payload = run_synthetic_secmi_stat_smoke(args.workspace, device=args.device)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "run-pia-synth-smoke":
        from diffaudit.attacks.pia_adapter import run_synthetic_pia_smoke

        payload = run_synthetic_pia_smoke(
            args.workspace,
            repo_root=args.repo_root,
            device=args.device,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0


    if args.command == "run-pia-runtime-smoke":
        from diffaudit.attacks.pia_adapter import run_pia_runtime_smoke

        payload = run_pia_runtime_smoke(
            args.workspace,
            repo_root=args.repo_root,
            device=args.device,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-rediffuse-runtime-smoke":
        from diffaudit.attacks.rediffuse_adapter import run_rediffuse_runtime_smoke

        payload = run_rediffuse_runtime_smoke(
            workspace=args.workspace,
            bundle_root=args.bundle_root,
            checkpoint_path=args.checkpoint_path,
            dataset_root=args.dataset_root,
            device=args.device,
            max_samples=args.max_samples,
            batch_size=args.batch_size,
            attack_num=args.attack_num,
            interval=args.interval,
            average=args.average,
            k=args.k,
            norm=args.norm,
            scoring_mode=args.scoring_mode,
            scorer_train_portion=args.scorer_train_portion,
            scorer_epochs=args.scorer_epochs,
            scorer_lr=args.scorer_lr,
            scorer_batch_size=args.scorer_batch_size,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-rediffuse-runtime-packet":
        from diffaudit.attacks.rediffuse_adapter import run_rediffuse_runtime_packet

        payload = run_rediffuse_runtime_packet(
            workspace=args.workspace,
            bundle_root=args.bundle_root,
            checkpoint_path=args.checkpoint_path,
            dataset_root=args.dataset_root,
            device=args.device,
            max_samples=args.max_samples,
            batch_size=args.batch_size,
            attack_num=args.attack_num,
            interval=args.interval,
            average=args.average,
            k=args.k,
            norm=args.norm,
            scoring_mode=args.scoring_mode,
            scorer_train_portion=args.scorer_train_portion,
            scorer_epochs=args.scorer_epochs,
            scorer_lr=args.scorer_lr,
            scorer_batch_size=args.scorer_batch_size,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-midfreq-residual-tiny-cache":
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_tiny_cache

        payload = run_midfreq_residual_tiny_cache(
            workspace=args.workspace,
            member_count=args.member_count,
            nonmember_count=args.nonmember_count,
            batch_size=args.batch_size,
            timestep=args.timestep,
            seed=args.seed,
            cutoff=args.cutoff,
            cutoff_high=args.cutoff_high,
            image_size=args.image_size,
            channels=args.channels,
            device=args.device,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1

    if args.command == "run-midfreq-residual-real-asset-preflight":
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_real_asset_preflight

        payload = run_midfreq_residual_real_asset_preflight(
            workspace=args.workspace,
            bundle_root=args.bundle_root,
            checkpoint_path=args.checkpoint_path,
            dataset_root=args.dataset_root,
            sample_count_per_split=args.sample_count_per_split,
            batch_size=args.batch_size,
            timestep=args.timestep,
            seed=args.seed,
            cutoff=args.cutoff,
            cutoff_high=args.cutoff_high,
            device=args.device,
            weights_key=args.weights_key,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-pia-runtime-mainline":
        from diffaudit.attacks.pia_adapter import run_pia_runtime_mainline

        config = load_audit_config(args.config)
        payload = run_pia_runtime_mainline(
            config,
            workspace=args.workspace,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            max_samples=args.max_samples,
            batch_size=args.batch_size,
            stochastic_dropout_defense=args.stochastic_dropout_defense,
            dropout_activation_schedule=args.dropout_activation_schedule,
            adaptive_query_repeats=args.adaptive_query_repeats,
            epsilon_precision_bins=args.epsilon_precision_bins,
            late_step_threshold=args.late_step_threshold,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported secmi_pia_smokes command: {args.command}")


def _handle_gsa_runtime(args: Any) -> int:
    if args.command == "run-gsa-runtime-mainline":
        from diffaudit.attacks.gsa import run_gsa_runtime_mainline

        ddpm_num_steps = args.ddpm_num_steps
        sampling_frequency = args.sampling_frequency
        if args.paper_aligned:
            ddpm_num_steps = 1000
            sampling_frequency = 10
        payload = run_gsa_runtime_mainline(
            workspace=args.workspace,
            assets_root=args.assets_root,
            repo_root=args.repo_root,
            resolution=args.resolution,
            ddpm_num_steps=ddpm_num_steps,
            sampling_frequency=sampling_frequency,
            attack_method=args.attack_method,
            prediction_type=args.prediction_type,
            max_samples=args.max_samples,
            device=args.device,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "export-gsa-loss-score-packet":
        from diffaudit.attacks.gsa import export_gsa_loss_score_packet

        sample_id_allowlist = None
        if args.sample_id_file is not None:
            sample_id_file = Path(args.sample_id_file)
            raw_text = sample_id_file.read_text(encoding="utf-8").strip()
            if raw_text:
                if raw_text.startswith("["):
                    sample_id_allowlist = [int(value) for value in json.loads(raw_text)]
                else:
                    sample_id_allowlist = [int(line.strip()) for line in raw_text.splitlines() if line.strip()]
            else:
                sample_id_allowlist = []

        payload = export_gsa_loss_score_packet(
            workspace=args.workspace,
            assets_root=args.assets_root,
            repo_root=args.repo_root,
            resolution=args.resolution,
            ddpm_num_steps=args.ddpm_num_steps,
            sampling_frequency=args.sampling_frequency,
            attack_method=args.attack_method,
            prediction_type=args.prediction_type,
            extraction_max_samples=args.extraction_max_samples,
            sample_id_allowlist=sample_id_allowlist,
            device=args.device,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "evaluate-gsa-loss-score-packet":
        from diffaudit.attacks.gsa import evaluate_gsa_loss_score_packet

        payload = evaluate_gsa_loss_score_packet(
            workspace=args.workspace,
            packet_summary=args.packet_summary,
            evaluation_style=args.evaluation_style,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "analyze-crossbox-pairboard":
        from diffaudit.attacks.crossbox_pairboard import run_crossbox_pairboard

        payload = run_crossbox_pairboard(
            workspace=args.workspace,
            surface_a_path=args.surface_a,
            surface_b_path=args.surface_b,
            surface_a_name=args.surface_a_name,
            surface_b_name=args.surface_b_name,
            surface_a_family=args.surface_a_family,
            surface_b_family=args.surface_b_family,
            calibration_fraction=args.calibration_fraction,
            seed=args.seed,
            repeats=args.repeats,
            enable_tail_gated_cascade=args.tail_gated_cascade,
            cascade_anchor_name=args.cascade_anchor_name,
            cascade_candidate_name=args.cascade_candidate_name,
            cascade_route_fractions=args.cascade_route_fractions,
            cascade_gammas=args.cascade_gammas,
            cascade_secondary_cost_ratio=args.cascade_secondary_cost_ratio,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported gsa_runtime command: {args.command}")


def _handle_defenses(args: Any) -> int:
    if args.command == "prepare-risk-targeted-unlearning-pilot":
        from diffaudit.defenses.risk_targeted_unlearning import run_risk_targeted_unlearning_prep

        top_k_values = [int(value.strip()) for value in str(args.top_k).split(",") if value.strip()]
        payload = run_risk_targeted_unlearning_prep(
            workspace=args.workspace,
            surface_a_path=args.surface_a,
            surface_b_path=args.surface_b,
            surface_a_name=args.surface_a_name,
            surface_b_name=args.surface_b_name,
            surface_a_family=args.surface_a_family,
            surface_b_family=args.surface_b_family,
            weight_a=args.weight_a,
            weight_b=args.weight_b,
            top_fraction=args.top_fraction,
            top_k_values=top_k_values,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-risk-targeted-unlearning-pilot":
        from diffaudit.defenses.risk_targeted_unlearning import run_risk_targeted_unlearning_pilot

        payload = run_risk_targeted_unlearning_pilot(
            workspace=args.workspace,
            member_dataset_dir=args.member_dataset_dir,
            forget_member_index_file=args.forget_member_index_file,
            checkpoint_root=args.checkpoint_root,
            checkpoint_dir=args.checkpoint_dir,
            matched_nonmember_index_file=args.matched_nonmember_index_file,
            random_init=args.random_init,
            retain_max_samples=args.retain_max_samples,
            forget_max_samples=args.forget_max_samples,
            num_steps=args.num_steps,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
            lr=args.lr,
            alpha=args.alpha,
            mixture_lambda=args.mixture_lambda,
            grad_clip=args.grad_clip,
            resolution=args.resolution,
            ddpm_num_train_timesteps=args.ddpm_num_train_timesteps,
            device=args.device,
            seed=args.seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "review-risk-targeted-unlearning-pilot":
        from diffaudit.defenses.risk_targeted_unlearning import review_risk_targeted_unlearning_pilot

        payload = review_risk_targeted_unlearning_pilot(
            workspace=args.workspace,
            shadow_reference_summary=args.shadow_reference_summary,
            target_member_dataset_dir=args.target_member_dataset_dir,
            target_nonmember_dataset_dir=args.target_nonmember_dataset_dir,
            baseline_checkpoint_root=args.baseline_checkpoint_root,
            baseline_checkpoint_dir=args.baseline_checkpoint_dir,
            defended_checkpoint_dir=args.defended_checkpoint_dir,
            forget_member_index_file=args.forget_member_index_file,
            matched_nonmember_index_file=args.matched_nonmember_index_file,
            resolution=args.resolution,
            ddpm_num_steps=args.ddpm_num_steps,
            sampling_frequency=args.sampling_frequency,
            attack_method=args.attack_method,
            prediction_type=args.prediction_type,
            device=args.device,
            noise_seed=args.noise_seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported defenses command: {args.command}")


def _handle_temporal_dpdm(args: Any) -> int:
    if args.command == "export-temporal-surrogate-feature-packet":
        from diffaudit.attacks.temporal_surrogate import export_temporal_surrogate_feature_packet

        config = load_audit_config(args.config)
        payload = export_temporal_surrogate_feature_packet(
            config=config,
            workspace=args.workspace,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
            max_samples=args.max_samples,
            batch_size=args.batch_size,
            scan_timesteps=args.scan_timesteps,
            noise_seed=args.noise_seed,
            timestep_jitter_radius=args.timestep_jitter_radius,
            timestep_stride=args.timestep_stride,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "evaluate-temporal-surrogate-packets":
        from diffaudit.attacks.temporal_surrogate import evaluate_temporal_surrogate_packets

        payload = evaluate_temporal_surrogate_packets(
            workspace=args.workspace,
            teacher_feature_packet=args.teacher_feature_packet,
            teacher_score_surface=args.teacher_score_surface,
            teacher_score_family=args.teacher_score_family,
            transfer_feature_packet=args.transfer_feature_packet,
            bag_count=args.bag_count,
            quantiles=args.quantiles,
            l2_alpha=args.l2_alpha,
            cv_splits=args.cv_splits,
            cv_repeats=args.cv_repeats,
            random_seed=args.random_seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "evaluate-temporal-lr-packets":
        from diffaudit.attacks.temporal_lr import evaluate_temporal_lr_packets

        payload = evaluate_temporal_lr_packets(
            workspace=args.workspace,
            calibration_feature_packet=args.calibration_feature_packet,
            transfer_feature_packet=args.transfer_feature_packet,
            primary_candidate=args.primary_candidate,
            sensitivity_candidate=args.sensitivity_candidate,
            cv_splits=args.cv_splits,
            cv_repeats=args.cv_repeats,
            random_seed=args.random_seed,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-gsa-runtime-intervention-review":
        from diffaudit.attacks.gsa import run_gsa_runtime_intervention_review

        ddpm_num_steps = args.ddpm_num_steps
        sampling_frequency = args.sampling_frequency
        if args.paper_aligned:
            ddpm_num_steps = 1000
            sampling_frequency = 10
        payload = run_gsa_runtime_intervention_review(
            workspace=args.workspace,
            assets_root=args.assets_root,
            repo_root=args.repo_root,
            mask_summary=args.mask_summary,
            resolution=args.resolution,
            ddpm_num_steps=ddpm_num_steps,
            sampling_frequency=sampling_frequency,
            attack_method=args.attack_method,
            prediction_type=args.prediction_type,
            max_samples=args.max_samples,
            extraction_max_samples=args.extraction_max_samples,
            device=args.device,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-dpdm-w1-target-only":
        from diffaudit.defenses.dpdm_w1 import run_dpdm_w1_target_only_comparator

        payload = run_dpdm_w1_target_only_comparator(
            workspace=args.workspace,
            checkpoint_path=args.checkpoint_path,
            member_dataset_dir=args.member_dataset_dir,
            nonmember_dataset_dir=args.nonmember_dataset_dir,
            dpdm_root=args.dpdm_root,
            config_path=args.config_path,
            device=args.device,
            sigma_points=args.sigma_points,
            max_samples=args.max_samples,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-dpdm-w1-shadow-comparator":
        from diffaudit.defenses.dpdm_w1 import run_dpdm_w1_shadow_comparator

        payload = run_dpdm_w1_shadow_comparator(
            workspace=args.workspace,
            target_checkpoint_path=args.target_checkpoint_path,
            shadow_checkpoint_path=args.shadow_checkpoint_path,
            target_member_dataset_dir=args.target_member_dataset_dir,
            target_nonmember_dataset_dir=args.target_nonmember_dataset_dir,
            shadow_member_dataset_dir=args.shadow_member_dataset_dir,
            shadow_nonmember_dataset_dir=args.shadow_nonmember_dataset_dir,
            dpdm_root=args.dpdm_root,
            config_path=args.config_path,
            device=args.device,
            sigma_points=args.sigma_points,
            max_samples=args.max_samples,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    if args.command == "run-dpdm-w1-multi-shadow-comparator":
        from diffaudit.defenses.dpdm_w1 import run_dpdm_w1_multi_shadow_comparator

        payload = run_dpdm_w1_multi_shadow_comparator(
            workspace=args.workspace,
            target_checkpoint_path=args.target_checkpoint_path,
            shadow_checkpoint_paths=args.shadow_checkpoint_paths,
            target_member_dataset_dir=args.target_member_dataset_dir,
            target_nonmember_dataset_dir=args.target_nonmember_dataset_dir,
            shadow_member_dataset_dirs=args.shadow_member_dataset_dirs,
            shadow_nonmember_dataset_dirs=args.shadow_nonmember_dataset_dirs,
            dpdm_root=args.dpdm_root,
            config_path=args.config_path,
            device=args.device,
            sigma_points=args.sigma_points,
            max_samples=args.max_samples,
            provenance_status=args.provenance_status,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["status"] == "ready" else 1


    raise RuntimeError(f"Unsupported temporal_dpdm command: {args.command}")


_COMMAND_HANDLERS: dict[str, CommandHandler] = {
    "run-smoke": _handle_foundation,
    "plan-secmi": _handle_foundation,
    "plan-pia": _handle_foundation,
    "plan-clid": _handle_foundation,
    "plan-recon": _handle_foundation,
    "plan-variation": _handle_foundation,
    "probe-secmi-assets": _handle_asset_probes,
    "probe-pia-assets": _handle_asset_probes,
    "probe-rediffuse-assets": _handle_asset_probes,
    "probe-clid-assets": _handle_asset_probes,
    "probe-recon-assets": _handle_asset_probes,
    "probe-recon-score-artifacts": _handle_asset_probes,
    "probe-recon-runtime-assets": _handle_asset_probes,
    "prepare-recon-public-subset": _handle_asset_probes,
    "audit-recon-public-bundle": _handle_asset_probes,
    "check-recon-stage0-paper-gate": _handle_asset_probes,
    "probe-dit-assets": _handle_asset_probes,
    "probe-variation-assets": _handle_asset_probes,
    "probe-h2-assets": _handle_asset_probes,
    "prepare-h2-contract": _handle_asset_probes,
    "probe-gsa-assets": _handle_gsa_observability,
    "probe-gsa-observability-contract": _handle_gsa_observability,
    "export-gsa-observability-canary": _handle_gsa_observability,
    "export-gsa-observability-masked-packet": _handle_gsa_observability,
    "export-gsa-observability-inmodel-packet": _handle_gsa_observability,
    "run-h2-defense-pilot": _handle_h2_defense,
    "review-h2-defense-pilot": _handle_h2_defense,
    "prepare-secmi": _handle_dry_runs,
    "dry-run-secmi": _handle_dry_runs,
    "dry-run-pia": _handle_dry_runs,
    "dry-run-clid": _handle_dry_runs,
    "dry-run-recon": _handle_dry_runs,
    "dry-run-variation": _handle_dry_runs,
    "run-clid-dry-run-smoke": _handle_dry_runs,
    "summarize-clid-artifacts": _handle_dry_runs,
    "run-recon-eval-smoke": _handle_recon_and_synthetic,
    "summarize-recon-artifacts": _handle_recon_and_synthetic,
    "run-recon-upstream-eval-smoke": _handle_recon_and_synthetic,
    "run-recon-mainline-smoke": _handle_recon_and_synthetic,
    "run-recon-artifact-mainline": _handle_recon_and_synthetic,
    "run-recon-runtime-mainline": _handle_recon_and_synthetic,
    "run-dit-sample-smoke": _handle_recon_and_synthetic,
    "run-variation-synth-smoke": _handle_recon_and_synthetic,
    "summarize-blackbox-results": _handle_reports,
    "summarize-mainline-audit": _handle_reports,
    "runtime-probe-pia": _handle_pia_runtime,
    "runtime-probe-rediffuse": _handle_pia_runtime,
    "runtime-preview-pia": _handle_pia_runtime,
    "export-pia-packet-scores": _handle_pia_runtime,
    "export-sima-packet-scores": _handle_pia_runtime,
    "export-pia-translated-alias-probe": _handle_pia_runtime,
    "runtime-probe-secmi": _handle_secmi_pia_smokes,
    "bootstrap-secmi-smoke-assets": _handle_secmi_pia_smokes,
    "bootstrap-pia-smoke-assets": _handle_secmi_pia_smokes,
    "run-secmi-synth-smoke": _handle_secmi_pia_smokes,
    "run-pia-synth-smoke": _handle_secmi_pia_smokes,
    "run-pia-runtime-smoke": _handle_secmi_pia_smokes,
    "run-pia-runtime-mainline": _handle_secmi_pia_smokes,
    "run-rediffuse-runtime-smoke": _handle_secmi_pia_smokes,
    "run-rediffuse-runtime-packet": _handle_secmi_pia_smokes,
    "run-midfreq-residual-tiny-cache": _handle_secmi_pia_smokes,
    "run-midfreq-residual-real-asset-preflight": _handle_secmi_pia_smokes,
    "run-gsa-runtime-mainline": _handle_gsa_runtime,
    "export-gsa-loss-score-packet": _handle_gsa_runtime,
    "evaluate-gsa-loss-score-packet": _handle_gsa_runtime,
    "analyze-crossbox-pairboard": _handle_gsa_runtime,
    "prepare-risk-targeted-unlearning-pilot": _handle_defenses,
    "run-risk-targeted-unlearning-pilot": _handle_defenses,
    "review-risk-targeted-unlearning-pilot": _handle_defenses,
    "export-temporal-surrogate-feature-packet": _handle_temporal_dpdm,
    "evaluate-temporal-surrogate-packets": _handle_temporal_dpdm,
    "evaluate-temporal-lr-packets": _handle_temporal_dpdm,
    "run-gsa-runtime-intervention-review": _handle_temporal_dpdm,
    "run-dpdm-w1-target-only": _handle_temporal_dpdm,
    "run-dpdm-w1-shadow-comparator": _handle_temporal_dpdm,
    "run-dpdm-w1-multi-shadow-comparator": _handle_temporal_dpdm,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.error(f"Unsupported command: {args.command}")
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
