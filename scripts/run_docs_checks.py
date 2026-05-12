"""Run the lightweight documentation and evidence guard suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    completed = subprocess.run(cmd, cwd=str(cwd), check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    python_executable = sys.executable

    run([python_executable, "scripts/check_public_surface.py"], repo_root)
    run([python_executable, "scripts/check_markdown_links.py"], repo_root)
    run([python_executable, "scripts/validate_attack_defense_table.py"], repo_root)
    run([python_executable, "scripts/export_recon_product_evidence_card.py", "--check"], repo_root)


if __name__ == "__main__":
    main()
