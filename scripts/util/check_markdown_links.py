"""Validate local Markdown links in first-party, non-legacy docs."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CHECKED_EVIDENCE_FILES = {
    "docs/evidence/README.md",
    "docs/evidence/innovation-evidence-map.md",
    "docs/evidence/reproduction-status.md",
}

SKIP_PREFIXES = (
    "legacy/",
    "external/",
    "third_party/",
    "docs/internal/",
    "workspaces/",
    "src/",
    "references/materials/",
)
SKIP_SCHEMES = (
    "http://",
    "https://",
    "mailto:",
    "data:",
)


def tracked_markdown_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    files = []
    for path in proc.stdout.splitlines():
        normalized = path.replace("\\", "/")
        if normalized.startswith("docs/evidence/") and normalized not in CHECKED_EVIDENCE_FILES:
            continue
        if normalized.startswith(SKIP_PREFIXES):
            continue
        files.append(normalized)
    return files


def normalize_target(raw: str) -> str | None:
    target = raw.strip().strip("<>")
    if not target or target.startswith("#"):
        return None
    if target.startswith("$(") or target.startswith("(") or "<" in target or ">" in target:
        return None
    lower = target.lower()
    if lower.startswith(SKIP_SCHEMES):
        return None
    if "://" in target:
        return None
    if " " in target and not target.startswith("<"):
        target = target.split()[0]
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    target = unquote(target)
    if not target:
        return None
    return target.replace("\\", "/")


def main() -> int:
    violations: list[str] = []
    for path in tracked_markdown_files():
        source = ROOT / path
        text = source.read_text(encoding="utf-8", errors="ignore")
        for match in LINK_RE.finditer(text):
            target = normalize_target(match.group(1))
            if target is None:
                continue
            resolved = (source.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                violations.append(f"{path}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                violations.append(f"{path}: broken local link: {target}")

    if violations:
        print("Markdown link check failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Markdown link check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
