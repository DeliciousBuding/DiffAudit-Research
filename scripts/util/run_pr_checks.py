"""Run the fast pull-request gate.

This intentionally avoids installing PyTorch or executing runtime tests. The
full suite remains available through ``scripts/util/run_local_checks.py --fast`` and
the GitHub ``full-checks`` job on ``main``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    src_path = str(cwd / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
    completed = subprocess.run(cmd, cwd=str(cwd), env=env, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run_optional(cmd: list[str], cwd: Path, required_path: Path, label: str) -> None:
    if required_path.exists():
        run(cmd, cwd)
        return
    print(f"SKIP {label}: missing private/local paper data at {required_path}")


def run_optional_min_files(cmd: list[str], cwd: Path, files: list[Path], min_files: int, label: str) -> None:
    if len(files) >= min_files:
        run(cmd, cwd)
        return
    print(f"SKIP {label}: found {len(files)} reviewer file(s), need {min_files}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    python_executable = sys.executable
    paper_root = Path(os.environ.get("DIFFAUDIT_EVIDENCE_PAPER_DIR", repo_root / "papers" / "diffaudit-evidence-paper")).resolve()
    paper_data = paper_root / "data"
    claim_trace = paper_data / "claim_trace.csv"
    preflight_dir = repo_root / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
    e2q005_review_files = sorted(preflight_dir.glob("e2q005_external_style_review_[A-Z]_2026_06_06.csv"))
    e2_freeze_ledger_input = preflight_dir / "e2_high_value_public_asset_delta_refresh_late_2026_06_09.csv"
    e2_false_promotion_queue_input = preflight_dir / "e2_n50_public_surface_metadata_refresh.csv"
    e2_freeze_preflight_input = preflight_dir / "e2_n50_freeze_review_decisions_v1.csv"
    false_promotion_bundle_input = preflight_dir / "e2sct004_genai_confessions_public_surface_check_2026_06_06.md"
    false_promotion_bundle_zip = paper_root / "build" / "diffaudit-false-promotion-review-bundle.zip"

    run([python_executable, "scripts/util/run_docs_checks.py"], repo_root)
    run([python_executable, "scripts/paper/render_admitted_risk_card.py", "--check"], repo_root)
    run_optional([python_executable, "scripts/e2/build_claim_gate_recode_packet.py", "--check"], repo_root, claim_trace, "claim-gate recode packet")
    run_optional([python_executable, "scripts/paper/evaluate_report_correctness_faults.py", "--check"], repo_root, claim_trace, "report-correctness faults")
    run_optional_min_files(
        [python_executable, "scripts/e2/aggregate_e2q005_external_review.py", "--min-reviewers", "3"],
        repo_root,
        e2q005_review_files,
        3,
        "E2Q-005 review aggregation",
    )
    run_optional([python_executable, "scripts/e2/aggregate_false_promotion_external_review.py", "--check"], repo_root, claim_trace, "false-promotion review aggregation")
    run_optional([python_executable, "scripts/e2/build_e2_public_freeze_ledger.py", "--check"], repo_root, e2_freeze_ledger_input, "E2 public freeze ledger")
    run_optional(
        [python_executable, "scripts/e2/build_e2_false_promotion_expansion_queue.py", "--check"],
        repo_root,
        e2_false_promotion_queue_input,
        "false-promotion expansion queue",
    )
    run_optional([python_executable, "scripts/e2/check_e2_freeze_preflight.py"], repo_root, e2_freeze_preflight_input, "E2 freeze preflight")
    run_optional([python_executable, "scripts/paper/check_paper_release_packet.py", "--profile", "phase-g"], repo_root, claim_trace, "paper release packet")
    run_optional([python_executable, "scripts/paper/export_paper_supplement.py", "--check"], repo_root, claim_trace, "paper supplement export")
    run_optional([python_executable, "scripts/paper/export_paper_supplement.py", "--check-output"], repo_root, claim_trace, "paper supplement output")
    run_optional(
        [python_executable, "scripts/e2/export_false_promotion_review_bundle.py", "--check"],
        repo_root,
        false_promotion_bundle_input,
        "false-promotion review bundle",
    )
    run_optional(
        [python_executable, "scripts/e2/export_false_promotion_review_bundle.py", "--check-output"],
        repo_root,
        false_promotion_bundle_zip,
        "false-promotion review bundle output",
    )
    run(
        [
            python_executable,
            "-c",
            (
                "from scripts.util.check_public_surface import candidate_promotion_violations_from_text as f; "
                "assert f('H2 is an admitted black-box row.'); "
                "assert f('Tracing the Roots is reportable evidence.'); "
                "assert f('CommonCanvas is reportable evidence.'); "
                "assert f('ReDiffuse is consumer-ready evidence.'); "
                "assert f('admitted H2 row.'); "
                "assert f('reportable Tracing Roots evidence.'); "
                "assert f('Current arXiv DOI metadata and a live GitHub repository prove compute release.'); "
                "assert f('Admitted evidence based on repository metadata.'); "
                "assert not f('H2 is not an admitted result.'); "
                "assert not f('Tracing the Roots is non-admitted feature-packet evidence.'); "
                "assert not f('CommonCanvas is not reportable evidence.'); "
                "assert not f('Current arXiv DOI metadata and a live GitHub repository do not prove compute release.')"
            ),
        ],
        repo_root,
    )
    run(
        [
            python_executable,
            "-c",
            (
                "from pathlib import Path; "
                "from scripts.util.check_public_surface import candidate_promotion_violations_from_text as f; "
                "card=Path('workspaces/implementation/artifacts/admitted-risk-card.md').read_text(encoding='utf-8'); "
                "assert f('H2 is an admitted black-box row.'); "
                "assert not f(card)"
            ),
        ],
        repo_root,
    )
    run(
        [
            python_executable,
            "-c",
            (
                "import copy,json; "
                "from pathlib import Path; "
                "from scripts.paper.render_admitted_risk_card import render_risk_card; "
                "path=Path('workspaces/implementation/artifacts/admitted-evidence-bundle.json'); "
                "bundle=json.loads(path.read_text(encoding='utf-8')); "
                "bad=copy.deepcopy(bundle); "
                r"bad['rows'][0].setdefault('provenance', {})['source']='D:' + '\\Code\\DiffAudit\\private-source.csv'; "
                "raised=False\n"
                "try:\n"
                "    render_risk_card(bad, bundle_path=path.resolve(), root=Path.cwd())\n"
                "except ValueError as exc:\n"
                "    raised='private surface' in str(exc)\n"
                "assert raised"
            ),
        ],
        repo_root,
    )
    run([python_executable, "-m", "compileall", "-q", "src", "scripts", "tests", "training"], repo_root)
    run(
        [
            python_executable,
            "-c",
            "from diffaudit.cli import build_parser; parser = build_parser(); assert parser.prog == 'diffaudit'",
        ],
        repo_root,
    )


if __name__ == "__main__":
    main()
