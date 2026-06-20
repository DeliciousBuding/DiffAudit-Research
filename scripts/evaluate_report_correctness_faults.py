"""Evaluate selected report-correctness fault injections.

This script reuses the existing risk-card renderer and public-surface language
guard. It does not introduce a new admission framework; it records whether the
current release path rejects or flags a small hand-authored set of
public-material-compatible report faults.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from check_public_surface import candidate_promotion_violations_from_text
from render_admitted_risk_card import render_risk_card


DEFAULT_BUNDLE = Path("workspaces/implementation/artifacts/admitted-evidence-bundle.json")
DEFAULT_CSV = Path("papers/diffaudit-evidence-paper/data/report_correctness_fault_injection.csv")
DEFAULT_MD = Path(
    "papers/diffaudit-evidence-paper/versions/direction-d-report-correctness-fault-injection.md"
)


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    fault_class: str
    checked_surface: str
    expected: str
    observed: str
    passed: bool
    evidence: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_bundle(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mutate_candidate_replacement(bundle: dict[str, Any]) -> dict[str, Any]:
    bad = copy.deepcopy(bundle)
    row = bad["rows"][0]
    row["id"] = "candidate::H2 output-cloud geometry::none::research-only"
    row["status"] = "candidate"
    row["audience"] = "research-only"
    row["required_access"] = "black-box"
    row["report_role"] = "candidate-stress-test"
    row["track"] = "black-box"
    row["method"] = {
        "attack": "H2 output-cloud geometry",
        "defense": "none",
        "model": "candidate response-cache packet",
    }
    row["evidence_level"] = "candidate-only"
    return bad


def _mutate_missing_denominator(bundle: dict[str, Any]) -> dict[str, Any]:
    bad = copy.deepcopy(bundle)
    bad["rows"][1]["low_fpr_interpretation"].pop("nonmember_denominator", None)
    return bad


def _mutate_private_source(bundle: dict[str, Any]) -> dict[str, Any]:
    bad = copy.deepcopy(bundle)
    bad["rows"][1].setdefault("provenance", {})["source"] = (
        r"D:\Code\DiffAudit\private-source.csv"
    )
    return bad


def _mutate_row_count_drift(bundle: dict[str, Any]) -> dict[str, Any]:
    bad = copy.deepcopy(bundle)
    bad["row_count"] = int(bad["row_count"]) + 1
    return bad


def _render_case(
    case_id: str,
    fault_class: str,
    bundle: dict[str, Any],
    bundle_path: Path,
    root: Path,
    mutator: Callable[[dict[str, Any]], dict[str, Any]] | None,
    expected: str,
    expected_substring: str | None = None,
) -> CaseResult:
    candidate = mutator(bundle) if mutator is not None else copy.deepcopy(bundle)
    try:
        rendered = render_risk_card(candidate, bundle_path=bundle_path, root=root)
        observed = "accepted"
        evidence = f"rendered {len(rendered.splitlines())} markdown lines"
    except Exception as exc:  # noqa: BLE001 - the failure text is the evidence.
        observed = "rejected"
        evidence = str(exc)

    if expected == "accept":
        passed = observed == "accepted"
    elif expected == "reject":
        passed = observed == "rejected" and (
            expected_substring is None or expected_substring in evidence
        )
    else:
        raise ValueError(f"unknown expected action: {expected}")

    return CaseResult(
        case_id=case_id,
        fault_class=fault_class,
        checked_surface="risk card renderer",
        expected=expected,
        observed=observed,
        passed=passed,
        evidence=evidence,
    )


def _language_case(
    case_id: str,
    fault_class: str,
    text: str,
    expected: str,
) -> CaseResult:
    hits = candidate_promotion_violations_from_text(text)
    observed = "flagged" if hits else "clean"
    if expected == "flag":
        passed = bool(hits)
    elif expected == "clean":
        passed = not hits
    else:
        raise ValueError(f"unknown expected action: {expected}")
    return CaseResult(
        case_id=case_id,
        fault_class=fault_class,
        checked_surface="direct phrase scan",
        expected=expected,
        observed=observed,
        passed=passed,
        evidence="; ".join(hits) if hits else "no candidate-promotion hit",
    )


def _generated_language_cases() -> list[CaseResult]:
    candidate_promotions = [
        ("H2 output-cloud geometry", "H2 output-cloud geometry is admitted evidence."),
        ("Tracing Roots", "Tracing the Roots becomes consumer-ready."),
        ("ReDiffuse", "ReDiffuse is reportable Platform/Runtime evidence."),
        ("CommonCanvas", "CommonCanvas becomes consumer-ready."),
        ("MIDST", "MIDST is platform-runtime evidence."),
        ("CLiD", "CLiD is admitted evidence."),
        ("weak scouts", "weak scouts are reportable rows."),
        ("source-confounded packets", "source-confounded packets are admitted evidence."),
    ]
    metadata_promotions = [
        ("GitHub repository metadata", "GitHub repository metadata proves compute release."),
        ("OpenReview metadata", "OpenReview metadata supports N50 external denominator."),
        ("Zenodo metadata", "Zenodo metadata establishes external adjudication."),
        ("DOI metadata", "DOI metadata justifies reviewer reliability."),
        ("README", "README turns into a row-bound score packet."),
        ("arXiv API metadata", "arXiv API metadata unblocks a second public asset."),
    ]
    clean_controls = [
        ("negated H2", "H2 output-cloud geometry is not admitted evidence."),
        (
            "negated metadata release",
            "GitHub repository metadata does not prove compute release.",
        ),
        (
            "candidate-only Tracing Roots",
            "Tracing the Roots remains candidate-only and not reportable.",
        ),
        (
            "metadata boundary",
            "Public metadata is recorded only as discovery provenance.",
        ),
    ]

    cases: list[CaseResult] = []
    for index, (label, text) in enumerate(candidate_promotions, start=1):
        cases.append(
            _language_case(
                f"RCF-CAND-{index:03d}",
                "candidate/support promotion mutation",
                text,
                "flag",
            )
        )
    for index, (label, text) in enumerate(metadata_promotions, start=1):
        cases.append(
            _language_case(
                f"RCF-META-{index:03d}",
                "metadata-only promotion mutation",
                text,
                "flag",
            )
        )
    for index, (label, text) in enumerate(clean_controls, start=1):
        cases.append(
            _language_case(
                f"RCF-CLEAN-{index:03d}",
                f"clean boundary phrase control: {label}",
                text,
                "clean",
            )
        )
    return cases


def evaluate(bundle_path: Path, root: Path) -> list[CaseResult]:
    bundle = _load_bundle(bundle_path)
    current_card = render_risk_card(bundle, bundle_path=bundle_path, root=root)
    cases = [
        _render_case(
            "RCF-001",
            "current admitted bundle",
            bundle,
            bundle_path,
            root,
            None,
            "accept",
        ),
        _render_case(
            "RCF-002",
            "candidate row promoted into report card",
            bundle,
            bundle_path,
            root,
            _mutate_candidate_replacement,
            "reject",
            "non-admitted row",
        ),
        _render_case(
            "RCF-003",
            "finite-tail denominator removed",
            bundle,
            bundle_path,
            root,
            _mutate_missing_denominator,
            "reject",
            "missing nonmember denominator",
        ),
        _render_case(
            "RCF-004",
            "private source path injected",
            bundle,
            bundle_path,
            root,
            _mutate_private_source,
            "reject",
            "private surface",
        ),
        _render_case(
            "RCF-005",
            "row-count drift",
            bundle,
            bundle_path,
            root,
            _mutate_row_count_drift,
            "reject",
            "row_count drift",
        ),
        _language_case(
            "RCF-006",
            "direct H2 promotion language",
            "H2 output-cloud geometry is an admitted black-box row.",
            "flag",
        ),
        _language_case(
            "RCF-007",
            "direct Tracing Roots promotion language",
            "Tracing the Roots is reportable Platform/Runtime evidence.",
            "flag",
        ),
        _language_case(
            "RCF-008",
            "negated H2 boundary language",
            "H2 output-cloud geometry is not an admitted result.",
            "clean",
        ),
        _language_case(
            "RCF-009",
            "generated current risk card language",
            current_card,
            "clean",
        ),
        _language_case(
            "RCF-010",
            "metadata drift promoted to release language",
            (
                "Current arXiv DOI metadata and a live GitHub repository prove "
                "compute release for a withdrawn DLM row."
            ),
            "flag",
        ),
    ]
    cases.extend(_generated_language_cases())
    return cases


def _write_csv(path: Path, cases: list[CaseResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "fault_class",
                "checked_surface",
                "expected",
                "observed",
                "passed",
                "evidence",
            ],
        )
        writer.writeheader()
        for case in cases:
            public_evidence = case.evidence.replace("risk-card", "risk card")
            writer.writerow(
                {
                    "case_id": case.case_id,
                    "fault_class": case.fault_class,
                    "checked_surface": case.checked_surface,
                    "expected": case.expected,
                    "observed": case.observed,
                    "passed": int(case.passed),
                    "evidence": public_evidence,
                }
            )


def _write_md(path: Path, cases: list[CaseResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(case.passed for case in cases)
    renderer_rejections = sum(
        1
        for case in cases
        if case.checked_surface == "risk card renderer" and case.observed == "rejected"
    )
    direct_phrase_flags = sum(
        1
        for case in cases
        if case.checked_surface == "direct phrase scan" and case.observed == "flagged"
    )
    lines = [
        "# Release-Wording Fault-Injection Matrix",
        "",
        "> Generated by `scripts/evaluate_report_correctness_faults.py`.",
        "",
        "## Verdict",
        "",
        f"- Cases checked: `{len(cases)}`",
        f"- Expected outcomes passed: `{passed}/{len(cases)}`",
        f"- Renderer mutations rejected: `{renderer_rejections}`",
        f"- Direct-promotion phrases flagged: `{direct_phrase_flags}`",
        f"- Phrase mutation grid rows: `{sum(case.case_id.startswith(('RCF-CAND-', 'RCF-META-', 'RCF-CLEAN-')) for case in cases)}`",
        "- Claim boundary: release renderer and phrase-guard checks only; not report-drift reduction, external-use, deployment, or user-impact evidence.",
        "",
        "## Cases",
        "",
        "| Case | Fault class | Surface | Expected | Observed | Passed | Evidence |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for case in cases:
        evidence = case.evidence.replace("risk-card", "risk card").replace("|", "/")
        lines.append(
            f"| {case.case_id} | {case.fault_class} | {case.checked_surface} | "
            f"{case.expected} | {case.observed} | {int(case.passed)} | {evidence} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The matrix checks whether the current admitted-only report path rejects or flags selected unsupported states: candidate insertion, missing finite-tail denominator, private source leakage, row-count drift, direct candidate-promotion language, and metadata-drift language that turns a live DOI or repository surface into release status. It also runs a small phrase mutation grid over candidate/support subjects, metadata-only surfaces, and clean boundary statements. The generated current risk card text is scanned as the guarded output.",
            "",
            "These rows show that the selected release renderer and phrase-guard cases behaved as expected. They do not prove broad natural-language safety or that the contract reduces report drift in external use.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _check_output(path: Path, expected_text: str) -> None:
    if not path.exists():
        raise SystemExit(f"missing output: {path}")
    current = path.read_text(encoding="utf-8")
    if current != expected_text:
        raise SystemExit(f"out-of-sync output: {path}")


def main() -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="Evaluate selected report-correctness fault injections."
    )
    parser.add_argument("--bundle", type=Path, default=root / DEFAULT_BUNDLE)
    parser.add_argument("--csv", type=Path, default=root / DEFAULT_CSV)
    parser.add_argument("--md", type=Path, default=root / DEFAULT_MD)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    bundle_path = args.bundle.resolve()
    cases = evaluate(bundle_path, root=root)
    if not all(case.passed for case in cases):
        failed = ", ".join(case.case_id for case in cases if not case.passed)
        raise SystemExit(f"report-correctness fault cases failed: {failed}")

    csv_path = args.csv.resolve()
    md_path = args.md.resolve()

    if args.check:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            expected_csv_path = Path(tmp) / "expected.csv"
            expected_md_path = Path(tmp) / "expected.md"
            _write_csv(expected_csv_path, cases)
            _write_md(expected_md_path, cases)
            expected_csv = expected_csv_path.read_text(encoding="utf-8")
            expected_md = expected_md_path.read_text(encoding="utf-8")

        _check_output(csv_path, expected_csv)
        _check_output(md_path, expected_md)
    else:
        _write_csv(csv_path, cases)
        _write_md(md_path, cases)

    print(
        "Report-correctness fault-injection check passed "
        f"({sum(case.passed for case in cases)}/{len(cases)} cases)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
