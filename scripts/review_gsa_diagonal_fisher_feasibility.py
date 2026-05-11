from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="review_gsa_diagonal_fisher_feasibility",
        description="Run the CPU-only selected-layer diagonal-Fisher feasibility micro-board.",
    )
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--repo-root", default="workspaces/white-box/external/GSA")
    parser.add_argument("--assets-root", default="workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1")
    parser.add_argument("--layer-selector", default="mid_block.attentions.0.to_v")
    parser.add_argument("--resolution", type=int, default=32)
    parser.add_argument("--ddpm-num-steps", type=int, default=20)
    parser.add_argument("--sampling-frequency", type=int, default=2)
    parser.add_argument("--attack-method", type=int, default=1)
    parser.add_argument("--prediction-type", default="epsilon")
    parser.add_argument("--max-samples-per-split", type=int, default=1)
    parser.add_argument("--fisher-damping", type=float, default=1e-6)
    parser.add_argument("--noise-seed", type=int, default=0)
    parser.add_argument("--device", default="cpu", choices=["cpu"])
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    src_root = repo_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from diffaudit.attacks.gsa_influence import run_gsa_diagonal_fisher_feasibility

    payload = run_gsa_diagonal_fisher_feasibility(
        workspace=args.workspace,
        repo_root=args.repo_root,
        assets_root=args.assets_root,
        layer_selector=args.layer_selector,
        resolution=args.resolution,
        ddpm_num_steps=args.ddpm_num_steps,
        sampling_frequency=args.sampling_frequency,
        attack_method=args.attack_method,
        prediction_type=args.prediction_type,
        max_samples_per_split=args.max_samples_per_split,
        fisher_damping=args.fisher_damping,
        noise_seed=args.noise_seed,
        device=args.device,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("status") == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
