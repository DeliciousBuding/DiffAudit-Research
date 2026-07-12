#!/usr/bin/env python
"""Extract protocol-bound H1 features without computing membership outcomes."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

import torch

RESEARCH_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = RESEARCH_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from diffaudit.evidence.corrected_protocol import (  # noqa: E402
    canonical_protocol_hash,
    validate_paper1_protocol_envelope,
)
from diffaudit.evidence.h1_extraction import (  # noqa: E402
    build_benchmark_summary,
    extract_locked_rows,
    read_h1_repository_state,
    sha256_file,
    validate_checkpoint_bundle,
    validate_h1_extraction_runtime,
    validate_h1_repository_state,
    write_h1_feature_packet,
)
from diffaudit.training.corrected_ddpm import collect_environment  # noqa: E402
from diffaudit.training.exact_resume import configure_deterministic_torch  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--expected-protocol-hash", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--training-manifest", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--packet-purpose",
        choices=("corrected_evaluation", "preflight_benchmark"),
        required=True,
    )
    parser.add_argument("--scorer-code-commit", required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--preflight", action="store_true")
    return parser


def _load_model(ema_state_dict: object, device: torch.device) -> torch.nn.Module:
    material_root = RESEARCH_ROOT / "training" / "ddpm-cifar10"
    if str(material_root) not in sys.path:
        sys.path.insert(0, str(material_root))
    from model_unet import UNet

    model = UNet(
        T=1000,
        ch=128,
        ch_mult=[1, 2, 2, 2],
        attn=[1],
        num_res_blocks=2,
        dropout=0.1,
    )
    if not isinstance(ema_state_dict, dict):
        ema_state_dict = dict(ema_state_dict)
    model.load_state_dict(ema_state_dict, strict=True)
    betas = torch.linspace(0.0001, 0.02, 1000, dtype=torch.float32)
    model.alphas_cumprod = torch.cumprod(1.0 - betas, dim=0).to(device)
    return model.to(device).eval()


def _load_dataset(root: Path):
    from torchvision import datasets, transforms

    return datasets.CIFAR10(
        root=str(root),
        train=True,
        download=False,
        transform=transforms.ToTensor(),
    )


def _execute(args: argparse.Namespace) -> dict[str, object]:
    end_to_end_started = getattr(args, "_process_started", time.perf_counter())
    phase_timings: dict[str, float] = {}
    phase_started = time.perf_counter()
    configure_deterministic_torch()
    envelope = validate_paper1_protocol_envelope(
        args.protocol_manifest,
        expected_protocol_hash=args.expected_protocol_hash,
    )
    contract = envelope["contract"]
    head, tracked_status, relevant_untracked = read_h1_repository_state(RESEARCH_ROOT)
    validate_h1_repository_state(
        head,
        tracked_status,
        relevant_untracked,
        expected_scorer_commit=args.scorer_code_commit,
    )
    extraction_config = contract["h1"]["extraction"]
    evaluator_environment = collect_environment()
    validate_h1_extraction_runtime(
        extraction_config,
        batch_size=args.batch_size,
        device=args.device,
        evaluator_environment=evaluator_environment,
    )
    phase_timings["identity_protocol"] = time.perf_counter() - phase_started

    phase_started = time.perf_counter()
    bundle = validate_checkpoint_bundle(
        args.checkpoint,
        args.training_manifest,
        expected_protocol_hash=args.expected_protocol_hash,
        expected_split_sha256=contract["dataset"]["split"]["sha256"],
        expected_target_code_commit=contract["code_commit"],
        expected_training_config_hash=contract["training"]["training_config_hash"],
        packet_purpose=args.packet_purpose,
        preflight=args.preflight,
    )
    phase_timings["checkpoint_hash_load"] = time.perf_counter() - phase_started

    phase_started = time.perf_counter()
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA device requested but CUDA is unavailable")
    model = _load_model(bundle.ema_state_dict, device)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    phase_timings["model_to_device"] = time.perf_counter() - phase_started

    phase_started = time.perf_counter()
    dataset = _load_dataset(args.dataset_root)
    if len(dataset) != 50_000:
        raise ValueError("CIFAR10 train dataset must contain exactly 50000 rows")
    phase_timings["dataset_load"] = time.perf_counter() - phase_started

    phase_started = time.perf_counter()
    extracted = extract_locked_rows(
        model,
        dataset,
        contract["evaluation"]["rows"],
        feature_definition=contract["h1"]["feature_definition"],
        protocol_namespace=contract["common_noise"]["namespace"],
        batch_size=args.batch_size,
        device=device,
    )
    extraction_seconds = time.perf_counter() - phase_started
    phase_timings["extraction"] = extraction_seconds
    provenance = {
        "dataset_id": contract["dataset"]["name"],
        "run_seed": bundle.provenance.run_seed,
        "step": bundle.provenance.step,
        "attack": "H1",
        "checkpoint_sha256": bundle.provenance.checkpoint_sha256,
        "training_manifest_sha256": bundle.provenance.training_manifest_sha256,
        "target_code_commit": bundle.provenance.target_code_commit,
        "scorer_code_commit": head,
        "split_sha256": bundle.provenance.split_sha256,
        "protocol_hash": bundle.provenance.protocol_hash,
        "run_label": bundle.provenance.run_label,
        "extraction_config": extraction_config,
        "extraction_config_hash": canonical_protocol_hash(extraction_config),
        "evaluator_environment": evaluator_environment,
    }
    phase_started = time.perf_counter()
    write_h1_feature_packet(
        args.output,
        packet_purpose=args.packet_purpose,
        provenance=provenance,
        rows=extracted.rows,
        pca_features=extracted.pca_features,
        scalar_features=extracted.scalar_features,
    )
    packet_sha256 = sha256_file(args.output / "manifest.json")
    phase_timings["packet_write_hash"] = time.perf_counter() - phase_started
    peak_allocated = 0
    peak_reserved = 0
    if device.type == "cuda":
        peak_allocated = int(torch.cuda.max_memory_allocated(device))
        peak_reserved = int(torch.cuda.max_memory_reserved(device))
    end_to_end_seconds = time.perf_counter() - end_to_end_started
    return build_benchmark_summary(
        rows=len(extracted.rows),
        queries=len(extracted.rows) * len(contract["h1"]["timesteps"]),
        end_to_end_seconds=end_to_end_seconds,
        extraction_seconds=extraction_seconds,
        phase_timings=phase_timings,
        peak_cuda_allocated_bytes=peak_allocated,
        peak_cuda_reserved_bytes=peak_reserved,
        packet_path=str(args.output),
        packet_sha256=packet_sha256,
    )


def main(argv: Sequence[str] | None = None) -> int:
    process_started = time.perf_counter()
    args = _parser().parse_args(argv)
    args._process_started = process_started
    summary = _execute(args)
    print(json.dumps(summary, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
