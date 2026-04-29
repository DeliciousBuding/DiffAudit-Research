from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.tmiadm_adapter import run_tmiadm_protocol_probe
from diffaudit.config import load_audit_config


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _surface_payload_or_run(
    *,
    name: str,
    workspace: Path,
    config_path: Path,
    repo_root: Path,
    member_split_root: Path,
    device: str,
    max_samples: int,
    batch_size: int,
    scan_timesteps: list[int],
    noise_seed: int,
    timestep_stride: int,
    overwrite: bool,
) -> dict[str, Any]:
    summary_path = workspace / "summary.json"
    family_scores_path = workspace / "family-scores.json"
    if summary_path.exists() and family_scores_path.exists() and not overwrite:
        payload = _read_json(summary_path)
        payload["reused_existing"] = True
        return payload
    if workspace.exists() and not overwrite and any(workspace.iterdir()):
        raise FileExistsError(
            f"{name} workspace exists but is incomplete: {workspace}. "
            "Pass --overwrite to replace it."
        )

    config = load_audit_config(config_path)
    payload = run_tmiadm_protocol_probe(
        config=config,
        workspace=workspace,
        repo_root=repo_root,
        member_split_root=member_split_root,
        device=device,
        max_samples=max_samples,
        batch_size=batch_size,
        scan_timesteps=scan_timesteps,
        aggregation_p_norm=2,
        noise_seed=noise_seed,
        timestep_stride=timestep_stride,
        provenance_status="workspace-verified",
    )
    payload["reused_existing"] = False
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the missing TMIA-DM 512-sample surfaces needed by the "
            "X-90 larger shared-surface tri-score review."
        )
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--workspace-root", type=Path, default=Path("workspaces/gray-box/runs"))
    parser.add_argument("--run-suffix", default="20260429-r1")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--max-samples", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--noise-seed", type=int, default=1)
    parser.add_argument("--scan-timesteps", nargs="+", type=int, default=[80, 100, 120])
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_root = args.workspace_root / f"x141-tmiadm512-asset-generation-{args.run_suffix}"
    manifest_summary_path = manifest_root / "summary.json"
    if manifest_summary_path.exists() and not args.overwrite:
        summary = _read_json(manifest_summary_path)
        summary["reused_existing_manifest"] = True
        print(json.dumps(summary, indent=2, ensure_ascii=True))
        return 0
    if manifest_root.exists() and not args.overwrite and any(manifest_root.iterdir()):
        raise FileExistsError(
            f"Manifest workspace exists but has no summary: {manifest_root}. "
            "Pass --overwrite to replace it."
        )
    manifest_root.mkdir(parents=True, exist_ok=True)

    undefended_workspace = (
        args.workspace_root / f"tmiadm-cifar10-late-window-protocol-probe-{args.run_suffix}-gpu-512"
    )
    defended_workspace = (
        args.workspace_root / f"tmiadm-cifar10-late-window-temporal-striding-defense-{args.run_suffix}-gpu-512"
    )

    undefended = _surface_payload_or_run(
        name="gpu512_undefended",
        workspace=undefended_workspace,
        config_path=args.config,
        repo_root=args.repo_root,
        member_split_root=args.member_split_root,
        device=args.device,
        max_samples=args.max_samples,
        batch_size=args.batch_size,
        scan_timesteps=args.scan_timesteps,
        noise_seed=args.noise_seed,
        timestep_stride=1,
        overwrite=args.overwrite,
    )
    defended = _surface_payload_or_run(
        name="gpu512_temporal_striding_defended",
        workspace=defended_workspace,
        config_path=args.config,
        repo_root=args.repo_root,
        member_split_root=args.member_split_root,
        device=args.device,
        max_samples=args.max_samples,
        batch_size=args.batch_size,
        scan_timesteps=args.scan_timesteps,
        noise_seed=args.noise_seed,
        timestep_stride=2,
        overwrite=args.overwrite,
    )

    summary = {
        "status": "ready",
        "track": "gray-box",
        "method": "tmiadm",
        "mode": "x90-missing-asset-generation",
        "run_id": manifest_root.name,
        "gpu_question": "X-141 / X-90 TMIA-DM 512-sample asset generation for matched tri-score review",
        "device": args.device,
        "contract": {
            "max_samples": args.max_samples,
            "scan_timesteps": args.scan_timesteps,
            "noise_seed": args.noise_seed,
            "batch_size": args.batch_size,
            "undefended_timestep_stride": 1,
            "defended_timestep_stride": 2,
        },
        "surfaces": {
            "gpu512_undefended": {
                "summary": str((undefended_workspace / "summary.json").as_posix()),
                "family_scores": str((undefended_workspace / "family-scores.json").as_posix()),
                "metrics": undefended["metrics"],
                "best_family": undefended["best_family"],
                "reused_existing": undefended["reused_existing"],
            },
            "gpu512_temporal_striding_defended": {
                "summary": str((defended_workspace / "summary.json").as_posix()),
                "family_scores": str((defended_workspace / "family-scores.json").as_posix()),
                "metrics": defended["metrics"],
                "best_family": defended["best_family"],
                "reused_existing": defended["reused_existing"],
            },
        },
        "notes": [
            "This generates only the missing TMIA-DM score surfaces; it does not by itself promote G1-A.",
            "The follow-up X-90 tri-score review must still enforce identity alignment against matched PIA 512 surfaces.",
        ],
        "artifacts": {
            "summary": str(manifest_summary_path.as_posix()),
        },
    }
    manifest_summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
