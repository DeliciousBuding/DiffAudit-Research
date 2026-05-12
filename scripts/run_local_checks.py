"""Run the repository's standard local quality gates."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    completed = subprocess.run(cmd, cwd=str(cwd), check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def resolve_python(explicit_python: str | None) -> str:
    if explicit_python:
        return explicit_python
    env_python = os.environ.get("DIFFAUDIT_RESEARCH_PYTHON", "").strip()
    if env_python:
        return env_python
    return sys.executable


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fast",
        action="store_true",
        help="run the minimal fast check suite",
    )
    parser.add_argument(
        "--python",
        default=None,
        help="python executable used for all local checks; defaults to DIFFAUDIT_RESEARCH_PYTHON or the current interpreter",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    python_executable = resolve_python(args.python)

    run([python_executable, "scripts/bootstrap_research_env.py"], repo_root)
    run([python_executable, "scripts/check_public_surface.py"], repo_root)
    run([python_executable, "scripts/check_markdown_links.py"], repo_root)
    run([python_executable, "scripts/validate_attack_defense_table.py"], repo_root)
    run([python_executable, "scripts/validate_secmi_supporting_contract.py"], repo_root)
    run([python_executable, "scripts/validate_clid_identity_boundary.py"], repo_root)
    run([python_executable, "scripts/validate_ib_adaptive_defense_contract.py"], repo_root)
    run([python_executable, "scripts/validate_ib_defended_shadow_reopen_protocol.py"], repo_root)
    run([python_executable, "scripts/validate_ib_defended_shadow_training_manifest.py"], repo_root)
    run([python_executable, "scripts/validate_ib_shadow_local_identity_scout.py"], repo_root)
    run([python_executable, "scripts/validate_whitebox_influence_curvature_contract.py"], repo_root)
    run([python_executable, "scripts/export_recon_product_evidence_card.py", "--check"], repo_root)
    run([python_executable, "scripts/export_admitted_evidence_bundle.py", "--check"], repo_root)
    run(
        [
            python_executable,
            "-m",
            "unittest",
            "tests.test_audit_variation_query_contract",
            "tests.test_review_semantic_aux_low_fpr",
            "tests.test_review_recon_tail_confidence",
            "tests.test_midfreq_residual",
            "tests.test_run_pr_checks",
            "tests.test_risk_targeted_unlearning",
            "tests.test_validate_ib_defended_shadow_reopen_protocol",
            "tests.test_validate_ib_defended_shadow_training_manifest",
            "tests.test_validate_ib_shadow_local_identity_scout",
        ],
        repo_root,
    )
    run([python_executable, "-m", "diffaudit", "--help"], repo_root)
    run([python_executable, "-m", "unittest", "tests.test_attack_registry", "tests.test_smoke_pipeline"], repo_root)
    run([python_executable, "-m", "pytest", "tests/test_variation_attack.py", "tests/test_render_team_local_configs.py", "tests/test_init_variation_query_set.py", "tests/test_monitor_gsa_sequence.py", "-q"], repo_root)

    if not args.fast:
        run(
            [
                python_executable,
                "scripts/render_team_local_configs.py",
                "--team-local",
                "configs/assets/team.local.template.yaml",
                "--output-dir",
                "tmp/configs/rendered-checks",
            ],
            repo_root,
        )


if __name__ == "__main__":
    main()
