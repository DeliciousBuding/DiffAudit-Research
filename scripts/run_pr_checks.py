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
