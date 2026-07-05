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
    repo_root = Path(__file__).resolve().parents[2]
    python_executable = sys.executable

    run([python_executable, "scripts/util/check_public_surface.py"], repo_root)
    run([python_executable, "scripts/util/check_markdown_links.py"], repo_root)
    run([python_executable, "scripts/util/check_stale_docs.py", "--max-age-days", "90"], repo_root)
    run([python_executable, "scripts/paper/validate_attack_defense_table.py"], repo_root)
    run([python_executable, "scripts/paper/export_recon_product_evidence_card.py", "--check"], repo_root)


if __name__ == "__main__":
    main()
