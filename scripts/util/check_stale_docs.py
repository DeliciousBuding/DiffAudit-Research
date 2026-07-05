#!/usr/bin/env python3
"""
Stale documentation detector for DiffAudit workspace.

Scans active documentation directories and flags files that haven't been
updated in a configurable number of days. Excludes archive/ and frozen/
directories by design — those are expected to be stale.

Usage:
    python scripts/util/check_stale_docs.py [--max-age-days 90] [--json]

Exit codes:
    0 — no stale docs found (or all within threshold)
    1 — stale docs found (prints list)
    2 — script error

CI integration:
    Run weekly via .github/workflows/weekly-docs-check.yml
    or as a pre-commit hook for awareness (non-blocking).
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Directories to scan for staleness
SCAN_DIRS = [
    "docs/",
    "docs/start-here/",
    "docs/evidence/",
    "docs/paper1/",
    "docs/progress/",
    "docs/internal/",
]

# Directories explicitly excluded (archives, frozen, sanitized copies)
EXCLUDE_PATTERNS = [
    "archive/",
    "legacy/",
    "clean/",
    "frozen",
    "third_party/",
    "external/",
]

# Files that are allowed to be old (governance docs, reference tables)
ALLOWLIST_FILES = [
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "CITATION.cff",
    "GLOSSARY.md",
    "NAMING_CONVENTIONS.md",
    "frozen-claim-matrix.md",
    "experiment-master-log.md",
]


def is_excluded(file_path: Path) -> bool:
    """Check if path matches any exclude pattern."""
    path_str = str(file_path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def is_allowlisted(file_path: Path) -> bool:
    """Check if file is in the permanent-document allowlist."""
    return file_path.name in ALLOWLIST_FILES


def get_mtime_days_ago(file_path: Path) -> int:
    """Return file's age in days (based on mtime)."""
    mtime = os.path.getmtime(file_path)
    mtime_date = date.fromtimestamp(mtime)
    return (date.today() - mtime_date).days


def scan_docs(max_age_days: int) -> list[dict]:
    """Scan SCAN_DIRS for files older than max_age_days."""
    stale_files = []

    for scan_dir in SCAN_DIRS:
        full_dir = REPO_ROOT / scan_dir
        if not full_dir.is_dir():
            continue

        for md_file in full_dir.rglob("*.md"):
            rel_path = md_file.relative_to(REPO_ROOT)

            if is_excluded(rel_path):
                continue
            if is_allowlisted(md_file):
                continue

            age_days = get_mtime_days_ago(md_file)
            if age_days > max_age_days:
                stale_files.append({
                    "path": str(rel_path),
                    "age_days": age_days,
                    "last_modified": date.fromtimestamp(
                        os.path.getmtime(md_file)
                    ).isoformat(),
                })

    # Sort by age descending (oldest first)
    stale_files.sort(key=lambda f: f["age_days"], reverse=True)
    return stale_files


def main():
    parser = argparse.ArgumentParser(
        description="Detect stale documentation files in active directories."
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=90,
        help="Maximum age in days before a doc is flagged as stale (default: 90)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for CI consumption)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit 0 if only warnings, exit 1 if stale files found",
    )
    args = parser.parse_args()

    stale = scan_docs(args.max_age_days)

    if args.json:
        print(json.dumps({
            "scan_date": date.today().isoformat(),
            "max_age_days": args.max_age_days,
            "stale_count": len(stale),
            "stale_files": stale,
        }, indent=2))
    else:
        if not stale:
            print(f"No stale docs found (> {args.max_age_days} days)")
        else:
            print(f"=== Stale Docs (> {args.max_age_days} days): {len(stale)} files ===\n")
            for f in stale:
                print(f"  [{f['age_days']:4d}d ago] {f['path']}")
            print(f"\nTip: review these files for accuracy or move to archive/ if superseded.")

    if args.ci and stale:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
