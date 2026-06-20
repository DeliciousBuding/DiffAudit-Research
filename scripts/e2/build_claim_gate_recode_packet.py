"""Build the C1-C15 claim-gate recode packet.

The packet is prepared reviewer material only. It never creates reviewer
labels, agreement rates, or reliability claims; it exports a shuffled blank
template so an independent reviewer can re-code the claim trace later.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "diffaudit-evidence-paper"
CLAIM_TRACE = PAPER / "data" / "claim_trace.csv"
OUT_TEMPLATE = PAPER / "data" / "claim_gate_recode_template.csv"
OUT_MANIFEST = PAPER / "data" / "claim_gate_recode_packet_manifest.csv"

PACKET_ID = "claim-gate-recode-c1-c15-20260609"
SHUFFLE_SEED = "DiffAudit claim-gate recode packet v1"
GATE_ALLOWED_VALUES = "Pass|Partial|Fail|N/A"
STATE_ALLOWED_VALUES = (
    "reportable mixed-strength bundle|role-separated reportable inventory|"
    "candidate failed-admission stress test|same-family stability support|"
    "support/negative route-selection evidence|claim-support taxonomy evidence|"
    "metadata process trace|claim-control summary|same-team taxonomy evidence|"
    "internal label hygiene|uncertainty sidecar|metadata-screening query hygiene|"
    "non-pooled L1 artifact inspection|pre-label stress-control object|"
    "release-wording sanity packet"
)

TEMPLATE_FIELDS = [
    "packet_id",
    "packet_row_id",
    "claim_id",
    "claim_summary",
    "source_artifact",
    "provenance_ids",
    "replay_tier",
    "availability_tier",
    "trace_type",
    "reviewer",
    "gate_allowed_values",
    "evidence_state_allowed_values",
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
    "evidence_state",
    "first_blocker",
    "allowed_wording",
    "notes",
]

MANIFEST_FIELDS = [
    "packet_id",
    "artifact_role",
    "path",
    "sha256",
    "row_count",
    "boundary",
]

BLANK_FIELDS = [
    "reviewer",
    "target_gate",
    "split_gate",
    "evidence_gate",
    "metric_gate",
    "boundary_gate",
    "delta_gate",
    "evidence_state",
    "first_blocker",
    "allowed_wording",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def render_csv(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def shuffle_key(claim_id: str) -> str:
    return hashlib.sha256(f"{SHUFFLE_SEED}|{claim_id}".encode("utf-8")).hexdigest()


def selected_claim_rows() -> list[dict[str, str]]:
    rows = [row for row in read_csv(CLAIM_TRACE) if row["claim_id"].startswith("C")]
    rows.sort(key=lambda row: shuffle_key(row["claim_id"]))
    if len(rows) != 15:
        raise SystemExit(f"expected 15 C-claims in claim_trace, found {len(rows)}")
    return rows


def build_template_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, claim in enumerate(selected_claim_rows(), start=1):
        row = {
            "packet_id": PACKET_ID,
            "packet_row_id": f"CGRC-{index:03d}",
            "claim_id": claim["claim_id"],
            "claim_summary": claim["claim_summary"],
            "source_artifact": claim["source_artifact"],
            "provenance_ids": claim["provenance_ids"],
            "replay_tier": claim["replay_tier"],
            "availability_tier": claim["availability_tier"],
            "trace_type": claim["trace_type"],
            "gate_allowed_values": GATE_ALLOWED_VALUES,
            "evidence_state_allowed_values": STATE_ALLOWED_VALUES,
        }
        for field in BLANK_FIELDS:
            row[field] = ""
        rows.append(row)
    return rows


def build_manifest_rows(template_payload: str, row_count: int) -> list[dict[str, str]]:
    return [
        {
            "packet_id": PACKET_ID,
            "artifact_role": "blank_recode_template",
            "path": "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_gate_recode_template.csv",
            "sha256": sha256_bytes(template_payload.encode("utf-8")),
            "row_count": str(row_count),
            "boundary": "prepared blank template only; no reviewer labels or reliability result",
        },
        {
            "packet_id": PACKET_ID,
            "artifact_role": "author_trace_source",
            "path": "D:/Code/DiffAudit/Research/papers/diffaudit-evidence-paper/data/claim_trace.csv",
            "sha256": sha256_file(CLAIM_TRACE),
            "row_count": str(len(read_csv(CLAIM_TRACE))),
            "boundary": "author-coded trace source; use only after independent labels are frozen",
        },
    ]


def render_outputs() -> tuple[str, str]:
    template_rows = build_template_rows()
    template_payload = render_csv(template_rows, TEMPLATE_FIELDS)
    manifest_payload = render_csv(build_manifest_rows(template_payload, len(template_rows)), MANIFEST_FIELDS)
    return template_payload, manifest_payload


def write_outputs() -> None:
    template_payload, manifest_payload = render_outputs()
    OUT_TEMPLATE.write_text(template_payload, encoding="utf-8")
    OUT_MANIFEST.write_text(manifest_payload, encoding="utf-8")
    print(f"Wrote {OUT_TEMPLATE}")
    print(f"Wrote {OUT_MANIFEST}")


def check_outputs() -> None:
    expected_template, expected_manifest = render_outputs()
    if not OUT_TEMPLATE.exists() or OUT_TEMPLATE.read_text(encoding="utf-8") != expected_template:
        raise SystemExit(f"{OUT_TEMPLATE} is stale; run scripts/build_claim_gate_recode_packet.py")
    if not OUT_MANIFEST.exists() or OUT_MANIFEST.read_text(encoding="utf-8") != expected_manifest:
        raise SystemExit(f"{OUT_MANIFEST} is stale; run scripts/build_claim_gate_recode_packet.py")
    print("Claim-gate recode packet check passed (prepared template only; no labels).")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated outputs without writing")
    args = parser.parse_args()
    if args.check:
        check_outputs()
    else:
        write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
