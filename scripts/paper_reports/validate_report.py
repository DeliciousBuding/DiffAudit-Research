from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_METADATA = [
    "- Title:",
    "- Material index path:",
    "- Primary Track:",
    "- Venue / Year:",
    "- Threat Model Category:",
    "- Core Task:",
    "- Open-Source Implementation:",
    "- Report Status:",
]

REQUIRED_SECTIONS = [
    "## Executive Summary",
    "## Bibliographic Record",
    "## Research Question",
    "## Problem Setting and Assumptions",
    "## Method Overview",
    "## Method Flow",
    "## Key Technical Details",
    "## Experimental Setup",
    "## Main Results",
    "## Strengths",
    "## Limitations and Validity Threats",
    "## Reproducibility Assessment",
    "## Relevance to DiffAudit",
    "## Recommended Figure",
    "## Extracted Summary for `paper-index.md`",
]


def extract_section(markdown: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown, flags=re.S)
    return match.group(1).strip() if match else ""


def validate_report(path: Path, require_latex: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    if not text.startswith("# "):
        errors.append("missing top-level title")

    for item in REQUIRED_METADATA:
        if item not in text:
            errors.append(f"missing metadata field: {item}")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing section: {section}")

    if "```mermaid" not in text:
        errors.append("missing Mermaid flowchart")

    if "![Key Figure]" not in text:
        errors.append("missing key figure image link")

    if require_latex and "$$" not in text and not re.search(r"(?<!\$)\$[^$]+\$(?!\$)", text):
        errors.append("missing LaTeX math content")

    summary = extract_section(text, "## Extracted Summary for `paper-index.md`")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", summary) if part.strip()]
    if len(paragraphs) != 3:
        errors.append(f"expected 3 summary paragraphs, found {len(paragraphs)}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a paper report against the shared template.")
    parser.add_argument("report", type=Path, help="Markdown report path")
    parser.add_argument(
        "--require-latex",
        action="store_true",
        help="Require at least one LaTeX formula in the report",
    )
    args = parser.parse_args()

    errors = validate_report(args.report, args.require_latex)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print("ok")


if __name__ == "__main__":
    main()
