"""Build the internal E2 false-promotion pilot tables.

This is a protocol-calibration pilot, not external adjudication evidence.
It uses existing Direction C rows as proxy labels to test the measurement
pipeline before freezing the final N=50 corpus.
"""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAPER_DATA = ROOT / "papers" / "diffaudit-evidence-paper" / "data"
# GONE - docs/internal/ directory not found
# OUT = ROOT / "docs" / "internal" / "e2-pilot-2026-06-06"
OUT = ROOT / "outputs" / "e2-pilot-2026-06-06"  # relocated

GATES = [
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
]

PILOT_IDS = {
    "artifact_corpus_v1.csv": [
        "v0-01",
        "v0-02",
        "v0-04",
        "v0-06",
        "v0-07",
        "v0-10",
        "v1-03",
        "v1-10",
    ],
    "artifact_corpus_fixed_search_20260526.csv": [
        "fs20260526-github-02",
        "fs20260526-github-03",
        "fs20260526-arxiv-02",
        "fs20260526-arxiv-05",
    ],
    "artifact_corpus_targeted_artifact_links_20260527.csv": [
        "ta20260527-hf-01",
        "ta20260527-github-02",
        "ta20260527-github-03",
    ],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def source_id(row: dict[str, str]) -> str:
    return row.get("id") or row.get("batch_id") or row.get("claim_id") or ""


def present(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() not in {"", "n/a", "no result", "none"}


def gate(row: dict[str, str], name: str) -> str:
    return (row.get(name) or "N/A").strip() or "N/A"


def gate_is(row: dict[str, str], name: str, *values: str) -> bool:
    return gate(row, name) in values


def joined_text(row: dict[str, str], fields: list[str]) -> str:
    return " ".join(row.get(field, "") for field in fields).lower()


def final_proxy_wording(row: dict[str, str]) -> str:
    target = gate(row, "target_gate")
    split = gate(row, "split_gate")
    evidence = gate(row, "evidence_gate")
    metric = gate(row, "metric_gate")
    boundary = gate(row, "boundary_gate")
    delta = gate(row, "delta_gate")

    if all(value == "Pass" for value in [target, split, evidence, metric]) and boundary != "Fail" and delta != "Fail":
        if any(value == "Partial" for value in [boundary, delta]):
            return "bounded-support"
        return "admitted"
    if evidence in {"Pass", "Partial"} and metric in {"Pass", "Partial"} and target != "Fail" and split != "Fail":
        return "candidate-only"
    return "blocked"


def diff_audit_decision(row: dict[str, str]) -> str:
    wording = final_proxy_wording(row)
    if wording == "admitted":
        return "admit"
    if wording == "bounded-support":
        return "bounded-support"
    return "block"


def code_available(row: dict[str, str]) -> bool:
    text = joined_text(
        row,
        [
            "paper_or_repo_url",
            "source_url",
            "artifact_url",
            "public_surface",
            "observed_public_files",
            "surface_type",
            "inclusion_reason",
            "first_blocker",
            "artifact_surface",
            "artifact_type",
            "stratum",
        ],
    )
    if any(token in text for token in ["github.com", "gitlab.com", "bitbucket.org", "source code"]):
        return True
    if any(
        phrase in text
        for phrase in ["no official code", "no public code", "without code", "no code", "no pdf or official code"]
    ):
        return False
    return any(token in text for token in ["official implementation", "repository tree", "scripts/", "readme.md", ".py"])


def artifact_available(row: dict[str, str]) -> bool:
    text = joined_text(
        row,
        [
            "artifact_url",
            "observed_public_files",
            "public_surface",
            "artifact_surface",
            "artifact_type",
            "surface_type",
            "inclusion_reason",
            "first_blocker",
        ],
    )
    if any(
        phrase in text
        for phrase in [
            "metadata only",
            "withdrawn",
            "no artifact",
            "no artifacts",
            "no pdf or official code",
            "no row-bound public replay surface",
        ]
    ):
        return False
    artifact_tokens = [
        "score",
        "scores",
        "score files",
        "row-score",
        "roc",
        "metric json",
        "metric bundle",
        "response cache",
        "response packet",
        "split",
        "member",
        "nonmember",
        "checkpoint",
        "ckpt",
        "pre-trained",
        "pretrained",
        "dataset",
        "parquet",
        "npz",
        "tensor",
        "tensors",
        "image log",
        "image logs",
        "generated",
        "feature packet",
        "values of all samples",
        "huggingface.co/datasets",
        "zenodo",
    ]
    return any(token in text for token in artifact_tokens)


def paper_source_available(row: dict[str, str]) -> bool:
    return (
        present(row.get("source_url"))
        or present(row.get("paper_or_repo_url"))
        or present(row.get("paper_url"))
        or present(row.get("source_note"))
    )


def baseline_decisions(row: dict[str, str]) -> dict[str, str]:
    score_only = "admit" if gate_is(row, "metric_gate", "Pass") else "block"
    code_rule = "admit" if code_available(row) else "block"
    artifact_rule = "admit" if artifact_available(row) else "block"
    paper_claim_artifact = "admit" if paper_source_available(row) and artifact_available(row) else "block"
    metric_code_split = (
        "admit"
        if gate_is(row, "metric_gate", "Pass", "Partial") and code_available(row) and gate_is(row, "split_gate", "Pass", "Partial")
        else "block"
    )
    reproducibility_checklist = (
        "admit"
        if all(gate_is(row, name, "Pass") for name in ["target_gate", "split_gate", "evidence_gate", "metric_gate"])
        and not gate_is(row, "boundary_gate", "Fail")
        else "block"
    )
    return {
        "score_only": score_only,
        "code_availability": code_rule,
        "artifact_availability": artifact_rule,
        "paper_claim_artifact_link": paper_claim_artifact,
        "metric_code_split": metric_code_split,
        "reproducibility_checklist": reproducibility_checklist,
        "diffaudit_contract": diff_audit_decision(row),
    }


def false_promotion(decision: str, final_wording: str) -> int:
    return int(decision == "admit" and final_wording in {"candidate-only", "blocked"})


def bounded_mismatch(decision: str, final_wording: str) -> int:
    return int(decision == "admit" and final_wording == "bounded-support")


def false_block(decision: str, final_wording: str) -> int:
    return int(decision == "block" and final_wording == "admitted")


def load_pilot_rows() -> list[dict[str, str]]:
    by_id: dict[str, tuple[str, dict[str, str]]] = {}
    for file_name in PILOT_IDS:
        path = PAPER_DATA / file_name
        for row in read_csv(path):
            by_id[source_id(row)] = (file_name, row)

    selected: list[dict[str, str]] = []
    missing: list[str] = []
    for file_name, ids in PILOT_IDS.items():
        for wanted in ids:
            if wanted not in by_id:
                missing.append(wanted)
                continue
            actual_file, row = by_id[wanted]
            if actual_file != file_name:
                missing.append(f"{wanted} from {file_name}")
                continue
            selected.append(normalize_row(actual_file, row, len(selected) + 1))
    if missing:
        raise SystemExit(f"Missing pilot rows: {', '.join(missing)}")
    return selected


def normalize_row(source_table: str, row: dict[str, str], pilot_index: int) -> dict[str, str]:
    title = row.get("candidate") or row.get("title") or ""
    source_url = row.get("paper_or_repo_url") or row.get("paper_url") or row.get("source_note") or ""
    artifact_url = row.get("artifact_url") or row.get("public_surface") or ""
    observed = row.get("observed_public_files") or row.get("artifact_surface") or row.get("artifact_type") or ""
    return {
        "pilot_id": f"E2P-{pilot_index:03d}",
        "source_table": source_table,
        "source_id": source_id(row),
        "title": title,
        "source_url": source_url,
        "artifact_url": artifact_url,
        "surface_type": row.get("stratum") or row.get("claim_support_level") or row.get("inclusion_decision") or "",
        "inclusion_reason": row.get("paper_role") or row.get("inclusion_decision") or row.get("exclusion_reason") or "",
        "observed_public_files": observed,
        "first_blocker": row.get("primary_failure") or row.get("exclusion_reason") or "",
        **{name: gate(row, name) for name in GATES},
    }


def add_decisions(row: dict[str, str]) -> dict[str, object]:
    decisions = baseline_decisions(row)
    final_wording = final_proxy_wording(row)
    enriched: dict[str, object] = {
        **row,
        "pilot_scope": "internal_proxy_not_external_adjudication",
        "final_proxy_wording": final_wording,
    }
    for rule, decision in decisions.items():
        enriched[f"{rule}_decision"] = decision
        enriched[f"{rule}_false_promotion"] = false_promotion(decision, final_wording)
        enriched[f"{rule}_bounded_mismatch"] = bounded_mismatch(decision, final_wording)
        enriched[f"{rule}_false_block"] = false_block(decision, final_wording)
    return enriched


def bootstrap_delta(rows: list[dict[str, object]], rule: str, baseline: str = "diffaudit_contract", n: int = 2000) -> tuple[float, float]:
    rng = random.Random(20260606)
    deltas = []
    for _ in range(n):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        rule_rate = sum(int(r[f"{rule}_false_promotion"]) for r in sample) / len(sample)
        base_rate = sum(int(r[f"{baseline}_false_promotion"]) for r in sample) / len(sample)
        deltas.append(rule_rate - base_rate)
    deltas.sort()
    return deltas[int(0.025 * n)], deltas[int(0.975 * n)]


def summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rules = [
        "score_only",
        "code_availability",
        "artifact_availability",
        "paper_claim_artifact_link",
        "metric_code_split",
        "reproducibility_checklist",
        "diffaudit_contract",
    ]
    total = len(rows)
    summary: list[dict[str, object]] = []
    base_fp = sum(int(r["diffaudit_contract_false_promotion"]) for r in rows) / total
    for rule in rules:
        admits = sum(1 for r in rows if r[f"{rule}_decision"] == "admit")
        bounded = sum(1 for r in rows if r[f"{rule}_decision"] == "bounded-support")
        false_promotions = sum(int(r[f"{rule}_false_promotion"]) for r in rows)
        false_blocks = sum(int(r[f"{rule}_false_block"]) for r in rows)
        mismatches = sum(int(r[f"{rule}_bounded_mismatch"]) for r in rows)
        fp_rate = false_promotions / total
        lo, hi = bootstrap_delta(rows, rule)
        summary.append(
            {
                "rule": rule,
                "pilot_scope": "internal_proxy_not_external_adjudication",
                "n_rows": total,
                "admit_count": admits,
                "bounded_support_count": bounded,
                "false_promotion_count": false_promotions,
                "false_promotion_rate": round(fp_rate, 4),
                "false_block_count": false_blocks,
                "bounded_mismatch_count": mismatches,
                "proxy_pilot_delta_vs_diffaudit_false_promotion": round(fp_rate - base_fp, 4),
                "proxy_pilot_paired_bootstrap_delta_ci_low": round(lo, 4),
                "proxy_pilot_paired_bootstrap_delta_ci_high": round(hi, 4),
            }
        )
    return summary


def validate_pilot_sanity(rows: list[dict[str, object]]) -> None:
    source_artifact_rows = [
        row
        for row in rows
        if present(str(row.get("source_url", "")))
        and (
            present(str(row.get("artifact_url", "")))
            or present(str(row.get("observed_public_files", "")))
            or str(row.get("evidence_gate", "")) in {"Pass", "Partial"}
        )
    ]
    admits = sum(1 for row in rows if row["paper_claim_artifact_link_decision"] == "admit")
    if source_artifact_rows and admits == 0:
        raise SystemExit(
            "Sanity check failed: paper_claim_artifact_link has no admits despite normalized "
            "source/artifact rows. Check normalized baseline fields."
        )


def blind_template_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    template: list[dict[str, object]] = []
    for row in rows:
        template.append(
            {
                "pilot_id": row["pilot_id"],
                "title": row["title"],
                "source_url": row["source_url"],
                "artifact_url": row["artifact_url"],
                "observed_public_files": row["observed_public_files"],
                "consumer_question": "Can this public evidence support the source claim as an audit/report statement? If not, which artifact is missing?",
                "reviewer": "",
                "target_gate": "",
                "split_gate": "",
                "score_or_response_gate": "",
                "metric_gate": "",
                "provenance_gate": "",
                "consumer_or_delta_gate": "",
                "allowed_wording": "",
                "first_blocker": "",
                "notes": "",
            }
        )
    return template


def write_readme(rows: list[dict[str, object]], summary: list[dict[str, object]]) -> None:
    final_counts = Counter(str(row["final_proxy_wording"]) for row in rows)
    worst = sorted(summary, key=lambda item: float(item["false_promotion_rate"]), reverse=True)[:3]
    text = [
        "# E2 False-Promotion Internal Pilot",
        "",
        "> Date: 2026-06-06",
        "> Scope: internal proxy pilot only; not external adjudication evidence.",
        "",
        "This pilot validates the E2 measurement pipeline on 15 existing Direction C surfaces.",
        "It is used to harden the blind review template, stronger baselines, and paired statistics before freezing the final N=50 corpus.",
        "",
        "## Outputs",
        "",
        "- `e2_false_promotion_pilot_rows.csv`",
        "- `e2_false_promotion_pilot_summary.csv`",
        "- `e2_blind_review_template.csv`",
        "",
        "## Proxy Wording Distribution",
        "",
    ]
    for label, count in sorted(final_counts.items()):
        text.append(f"- `{label}`: {count}")
    text.extend(["", "## Highest False-Promotion Proxy Rules", ""])
    for item in worst:
        text.append(
            f"- `{item['rule']}`: {item['false_promotion_count']}/{item['n_rows']} "
            f"(rate `{item['false_promotion_rate']}`, proxy-pilot paired delta CI "
            f"`[{item['proxy_pilot_paired_bootstrap_delta_ci_low']}, "
            f"{item['proxy_pilot_paired_bootstrap_delta_ci_high']}]`)"
        )
    text.extend(
        [
            "",
            "## Proxy Limitation",
            "",
            "`paper_claim_artifact_link` is a pilot stress rule here. Some pilot rows use local `docs/evidence/...` notes as reviewer-facing source summaries rather than external paper or official artifact pages. The final N=50 run must evaluate this baseline only against frozen public source links and blind adjudicated wording.",
            "",
            "## Stop Boundary",
            "",
            "Do not use this pilot as a paper result. The next step is blind internal review calibration and public-source/N50 freeze preflight; external adjudication is allowed only after a real frozen denominator exists.",
            "",
        ]
    )
    (OUT / "README.md").write_text("\n".join(text), encoding="utf-8")


def main() -> int:
    rows = [add_decisions(row) for row in load_pilot_rows()]
    validate_pilot_sanity(rows)
    summary = summary_rows(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "e2_false_promotion_pilot_rows.csv", rows)
    write_csv(OUT / "e2_false_promotion_pilot_summary.csv", summary)
    write_csv(OUT / "e2_blind_review_template.csv", blind_template_rows(rows))
    write_readme(rows, summary)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
