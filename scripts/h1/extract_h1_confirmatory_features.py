#!/usr/bin/env python
"""Extract protocol-bound H1 features without computing membership outcomes."""

from __future__ import annotations

import argparse
import hashlib
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
    validate_paper1_protocol_envelope,
)
from diffaudit.evidence.h1_extraction import (  # noqa: E402
    build_benchmark_summary,
    extract_locked_rows,
    read_h1_repository_state,
    validate_checkpoint_bundle,
    validate_h1_repository_state,
    write_h1_feature_packet,
)


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
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA device requested but CUDA is unavailable")
    model = _load_model(bundle.ema_state_dict, device)
    dataset = _load_dataset(args.dataset_root)
    if len(dataset) != 50_000:
        raise ValueError("CIFAR10 train dataset must contain exactly 50000 rows")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    extracted = extract_locked_rows(
        model,
        dataset,
        contract["evaluation"]["rows"],
        feature_definition=contract["h1"]["feature_definition"],
        protocol_namespace=contract["common_noise"]["namespace"],
        batch_size=args.batch_size,
        device=device,
    )
    total_seconds = time.perf_counter() - started
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
    }
    write_h1_feature_packet(
        args.output,
        packet_purpose=args.packet_purpose,
        provenance=provenance,
        rows=extracted.rows,
        pca_features=extracted.pca_features,
        scalar_features=extracted.scalar_features,
    )
    manifest_bytes = (args.output / "manifest.json").read_bytes()
    peak_allocated = 0
    peak_reserved = 0
    if device.type == "cuda":
        peak_allocated = int(torch.cuda.max_memory_allocated(device))
        peak_reserved = int(torch.cuda.max_memory_reserved(device))
    return build_benchmark_summary(
        rows=len(extracted.rows),
        queries=len(extracted.rows) * len(contract["h1"]["timesteps"]),
        total_seconds=total_seconds,
        peak_cuda_allocated_bytes=peak_allocated,
        peak_cuda_reserved_bytes=peak_reserved,
        packet_path=str(args.output),
        packet_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    summary = _execute(args)
    print(json.dumps(summary, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
