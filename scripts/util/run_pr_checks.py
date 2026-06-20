"""Run the fast pull-request gate.

This intentionally avoids installing PyTorch or executing runtime tests. The
full suite remains available through ``scripts/run_local_checks.py --fast`` and
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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    python_executable = sys.executable

    run([python_executable, "scripts/run_docs_checks.py"], repo_root)
    run([python_executable, "scripts/build_claim_gate_recode_packet.py", "--check"], repo_root)
    run([python_executable, "scripts/render_admitted_risk_card.py", "--check"], repo_root)
    run([python_executable, "scripts/evaluate_report_correctness_faults.py", "--check"], repo_root)
    run([python_executable, "scripts/aggregate_e2q005_external_review.py", "--min-reviewers", "3"], repo_root)
    run([python_executable, "scripts/aggregate_false_promotion_external_review.py", "--check"], repo_root)
    run([python_executable, "scripts/build_e2_public_freeze_ledger.py", "--check"], repo_root)
    run([python_executable, "scripts/build_e2_false_promotion_expansion_queue.py", "--check"], repo_root)
    run([python_executable, "scripts/check_e2_freeze_preflight.py"], repo_root)
    run([python_executable, "scripts/check_paper_release_packet.py"], repo_root)
    run([python_executable, "scripts/export_paper_supplement.py", "--check"], repo_root)
    run([python_executable, "scripts/export_paper_supplement.py", "--check-output"], repo_root)
    run([python_executable, "scripts/export_false_promotion_review_bundle.py", "--check"], repo_root)
    run([python_executable, "scripts/export_false_promotion_review_bundle.py", "--check-output"], repo_root)
    run(
        [
            python_executable,
            "-c",
            (
                "from scripts.check_public_surface import candidate_promotion_violations_from_text as f; "
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
                "from scripts.check_public_surface import candidate_promotion_violations_from_text as f; "
                "card=Path('D:/Code/DiffAudit/Research/workspaces/implementation/artifacts/admitted-risk-card.md').read_text(encoding='utf-8'); "
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
                "from scripts.render_admitted_risk_card import render_risk_card; "
                "path=Path('D:/Code/DiffAudit/Research/workspaces/implementation/artifacts/admitted-evidence-bundle.json'); "
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
    run([python_executable, "-m", "compileall", "-q", "src", "scripts", "tests"], repo_root)
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
