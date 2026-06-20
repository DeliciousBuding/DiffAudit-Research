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
    ("collaborator alias 惊鸿", re.compile(r"惊鸿")),
    ("collaborator alias 师兄", re.compile(r"师兄")),
    ("internal relative path in public doc", re.compile(r"\.\./internal/")),
    ("ask-gpt relative path in public doc", re.compile(r"\.\./ask-gpt/")),
)

TEXT_SCAN_EXCLUDE = {"scripts/check_public_surface.py"}

REPORT_LANGUAGE_SCAN_PATHS = {
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/main.tex",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/versions/direction-d-audit-systems.md",
    "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/versions/drafts/direction-d-audit-systems-paper.md",
    "D:/Code/DiffAudit/Research/workspaces/implementation/artifacts/admitted-risk-card.md",
}

TRACING_ROOTS_NAME = r"Tracing\s+(?:the\s+)?Roots"

CANDIDATE_PROMOTION_SUBJECTS: tuple[tuple[str, str], ...] = (
    ("H2", r"H2(?:\s+(?:output-cloud|response-cloud|candidate|geometry))*"),
    ("Tracing Roots", TRACING_ROOTS_NAME),
    ("ReDiffuse", r"ReDiffuse"),
    ("CommonCanvas", r"CommonCanvas"),
    ("MIDST", r"MIDST"),
    ("CLiD", r"CLiD"),
    ("weak scouts", r"weak\s+scouts?"),
    ("source-confounded packets", r"source-confounded\s+packets?"),
)

PROMOTION_TERMS = (
    r"admitted|reportable|consumer-ready|consumer ready|platform-runtime|Platform/Runtime"
)
PROMOTION_VERBS = (
    r"is|are|becomes|become|as|treated\s+as|promoted\s+to|described\s+as|reported\s+as"
)
METADATA_SURFACE_TERMS = (
    r"metadata(?:-only)?|DOI|arXiv(?:\s+API)?|GitHub(?:\s+(?:repository|repo|tree|metadata))?|"
    r"repository\s+metadata|public\s+metadata|metadata\s+refresh|README|OpenReview\s+metadata|"
    r"Zenodo\s+metadata|live\s+(?:repo|repository|DOI)"
)
METADATA_PROMOTION_TERMS = (
    r"admitted(?:\s+evidence)?|N50\s+(?:external\s+)?denominator|external\s+denominator|"
    r"compute\s+release|external\s+adjudication|reviewer\s+reliability|field[-\s]?wide\s+prevalence|"
    r"second\s+(?:independent\s+)?public\s+asset|row[-\s]?bound\s+(?:score|response|packet|evidence)"
)
METADATA_PROMOTION_VERBS = (
    r"proves?|establish(?:es)?|supports?|justif(?:y|ies)|unblocks?|upgrades?|makes?|turns?|promotes?|admits?"
)

CANDIDATE_PROMOTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (
        f"{label} described as admitted/reportable",
        re.compile(
            rf"\b{subject}\b\s+(?:{PROMOTION_VERBS})\s+(?:an?\s+)?(?:{PROMOTION_TERMS})\b",
            re.IGNORECASE,
        ),
    )
    for label, subject in CANDIDATE_PROMOTION_SUBJECTS
) + tuple(
    (
        f"{label} described as admitted/reportable",
        re.compile(
            rf"\b(?:{PROMOTION_TERMS})\s+{subject}\b",
            re.IGNORECASE,
        ),
    )
    for label, subject in CANDIDATE_PROMOTION_SUBJECTS
)

METADATA_PROMOTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "metadata-only surface described as admission/release",
        re.compile(
            rf"\b(?:{METADATA_SURFACE_TERMS})\b[\w\s,;:/.-]{{0,100}}\b(?:{METADATA_PROMOTION_VERBS})\b[\w\s,;:/.-]{{0,100}}\b(?:{METADATA_PROMOTION_TERMS})\b",
            re.IGNORECASE,
        ),
    ),
    (
        "metadata-only surface described as admission/release",
        re.compile(
            rf"\b(?:{METADATA_PROMOTION_TERMS})\b[\w\s,;:/.-]{{0,100}}\b(?:because\s+of|from|based\s+on|via|through)\b[\w\s,;:/.-]{{0,100}}\b(?:{METADATA_SURFACE_TERMS})\b",
            re.IGNORECASE,
        ),
    ),
)

CANDIDATE_PROMOTION_NEGATORS = re.compile(
    r"\b(?:not|non-admitted|candidate-only|failed-admission|refuses|refused|block|blocks|blocked|forbid|forbids|forbidden|no)\b",
    re.IGNORECASE,
)


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


def candidate_promotion_violations_from_text(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text)
    violations: list[str] = []
    for label, pattern in CANDIDATE_PROMOTION_PATTERNS + METADATA_PROMOTION_PATTERNS:
        for match in pattern.finditer(compact):
            snippet = match.group(0)
            if CANDIDATE_PROMOTION_NEGATORS.search(snippet):
                continue
            violations.append(f"{label}: {snippet[:160]}")
    return violations


def report_language_violations(path: str) -> list[str]:
    data = (ROOT / path).read_bytes()
    text = data.decode("utf-8", errors="ignore")
    return candidate_promotion_violations_from_text(text)


def main() -> int:
    violations: list[str] = []
    scanned_report_language_paths: set[str] = set()
    for path in tracked_ignored_files():
        normalized = path.replace("\\", "/")
        violations.append(f"tracked file hidden by .gitignore: {normalized}")

    for path in tracked_files():
        normalized = path.replace("\\", "/")
        if is_forbidden_path(normalized):
            violations.append(f"forbidden tracked artifact: {normalized}")
            continue
        file_path = ROOT / path
        if not file_path.exists():
            continue
        size = file_path.stat().st_size
        if size > MAX_TRACKED_FILE_BYTES:
            violations.append(
                f"oversized tracked file ({size} bytes): {normalized}"
            )
            continue
        if normalized in TEXT_SCAN_EXCLUDE:
            continue
        for label in text_violations(normalized):
            violations.append(f"{label}: {normalized}")
        if normalized in REPORT_LANGUAGE_SCAN_PATHS:
            scanned_report_language_paths.add(normalized)
            for label in report_language_violations(normalized):
                violations.append(f"{label}: {normalized}")

    for normalized in sorted(REPORT_LANGUAGE_SCAN_PATHS - scanned_report_language_paths):
        file_path = ROOT / normalized
        if not file_path.exists():
            continue
        size = file_path.stat().st_size
        if size > MAX_TRACKED_FILE_BYTES:
            violations.append(
                f"oversized report-language file ({size} bytes): {normalized}"
            )
            continue
        for label in text_violations(normalized):
            violations.append(f"{label}: {normalized}")
        for label in report_language_violations(normalized):
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
