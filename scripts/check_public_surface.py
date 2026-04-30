"""Fail CI when private paths or generated assets enter the public tree."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_FILE_BYTES = 1_000_000

FORBIDDEN_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^references/materials/.*\.(?:pdf|docx)$", re.IGNORECASE),
    re.compile(r"^docs/internal/paper-reports/(?:ocr|markdown)/", re.IGNORECASE),
    re.compile(r"^experiments/.*/(?:generated-images|score-artifacts)/", re.IGNORECASE),
    re.compile(r"^experiments/.*/sample\.png$", re.IGNORECASE),
    re.compile(r"^workspaces/runtime/jobs/", re.IGNORECASE),
    re.compile(
        r"\.(?:bin|pt|pth|ckpt|safetensors|npy|npz|zip|tar|tar\.gz|tgz|7z|rar)$",
        re.IGNORECASE,
    ),
)

FORBIDDEN_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local DiffAudit D: path", re.compile(r"D:(?:\\+|/+)+Code(?:\\+|/+)+DiffAudit")),
    ("local Ding user path", re.compile(r"C:(?:\\+|/+)+Users(?:\\+|/+)+Ding")),
    ("WSL Ding user path", re.compile(r"/mnt/c/Users/Ding", re.IGNORECASE)),
    ("signed OCR URL", re.compile(r"authorization=bce-auth", re.IGNORECASE)),
    ("OCR service host", re.compile(r"pplines-online", re.IGNORECASE)),
)

TEXT_SCAN_EXCLUDE = {"scripts/check_public_surface.py"}


def tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [item for item in proc.stdout.decode("utf-8").split("\0") if item]


def tracked_ignored_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-c", "-i", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [item for item in proc.stdout.decode("utf-8").split("\0") if item]


def is_forbidden_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(pattern.search(normalized) for pattern in FORBIDDEN_PATH_PATTERNS)


def text_violations(path: str) -> list[str]:
    data = (ROOT / path).read_bytes()
    text = data.decode("utf-8", errors="ignore")
    return [label for label, pattern in FORBIDDEN_TEXT_PATTERNS if pattern.search(text)]


def main() -> int:
    violations: list[str] = []
    for path in tracked_ignored_files():
        normalized = path.replace("\\", "/")
        violations.append(f"tracked file hidden by .gitignore: {normalized}")

    for path in tracked_files():
        normalized = path.replace("\\", "/")
        if is_forbidden_path(normalized):
            violations.append(f"forbidden tracked artifact: {normalized}")
            continue
        size = (ROOT / path).stat().st_size
        if size > MAX_TRACKED_FILE_BYTES:
            violations.append(
                f"oversized tracked file ({size} bytes): {normalized}"
            )
            continue
        if normalized in TEXT_SCAN_EXCLUDE:
            continue
        for label in text_violations(normalized):
            violations.append(f"{label}: {normalized}")

    if violations:
        print("Public surface guard failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Public surface guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
