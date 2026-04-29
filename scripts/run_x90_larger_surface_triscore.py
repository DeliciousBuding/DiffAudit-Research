from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from diffaudit.attacks.graybox_triscore import run_graybox_triscore_canary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run X-90 larger shared-surface tri-score evaluation.")
    parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Optional explicit run root. Defaults to timestamped x90 directory.",
    )
    parser.add_argument(
        "--contract-reference",
        type=Path,
        default=Path("workspaces/gray-box/runs/cdi-paired-canary-20260417-r3-contract/audit_summary.json"),
    )
    parser.add_argument(
        "--pia-undefended-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive"),
    )
    parser.add_argument(
        "--pia-defended-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive"),
    )
    parser.add_argument(
        "--tmiadm-undefended-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/tmiadm-cifar10-late-window-protocol-probe-20260429-r1-gpu-512"),
    )
    parser.add_argument(
        "--tmiadm-defended-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/tmiadm-cifar10-late-window-temporal-striding-defense-20260429-r1-gpu-512"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/gray-box/runs/x90-larger-surface-triscore-{timestamp}")

    # Use 512-sample surfaces (larger than X-89's 256)
    summary = run_graybox_triscore_canary(
        run_root=run_root,
        contract_reference_path=args.contract_reference,
        surfaces=[
            {
                "name": "gpu512_undefended",
                "pia_scores_path": args.pia_undefended_run / "scores.json",
                "pia_summary_path": args.pia_undefended_run / "summary.json",
                "tmiadm_family_scores_path": args.tmiadm_undefended_run / "family-scores.json",
                "tmiadm_summary_path": args.tmiadm_undefended_run / "summary.json",
                "tmiadm_family": "long_window",
            },
            {
                "name": "gpu512_defended",
                "pia_scores_path": args.pia_defended_run / "scores.json",
                "pia_summary_path": args.pia_defended_run / "summary.json",
                "tmiadm_family_scores_path": args.tmiadm_defended_run / "family-scores.json",
                "tmiadm_summary_path": args.tmiadm_defended_run / "summary.json",
                "tmiadm_family": "long_window",
            },
        ],
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
