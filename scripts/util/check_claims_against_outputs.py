#!/usr/bin/env python3
"""
Evidence Gate — Claim Matrix vs Outputs Cross-Validator.

Reads frozen-claim-matrix.md, extracts the Phase G unified comparison table,
and verifies each AUC claim against summary.json files in outputs/.

Usage:
    python scripts/util/check_claims_against_outputs.py

Exit codes:
    0 — all claims verified PASS
    1 — one or more FAIL or MISSING
    2 — script error (bad paths, malformed JSON, parse failure)
"""

import json
import sys
from pathlib import Path
from datetime import date

# -------------------------------------------------------
# 1.  Locate repo root relative to this script
# -------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # scripts/util -> scripts -> repo root

CLAIM_MATRIX_PATH = REPO_ROOT / "docs" / "paper1" / "frozen-claim-matrix.md"
OUTPUTS_DIR = REPO_ROOT / "outputs"

# -------------------------------------------------------
# 2.  Mapping: claim-matrix label -> output directory name
# -------------------------------------------------------
# These map the Phase G unified comparison table rows (as they appear in the
# markdown) to the corresponding subdirectory under outputs/.
PHASE_G_MAPPING = {
    "DDPM-750k":                    "h1-scout-750k",
    "DDPM-750k seed43":             "h1-scout-seed43-750k",
    "DDPM-800k same-trajectory":   "h1-scout-800k-same-trajectory",
    "DDPM-800k seed43":             "h1-scout-seed43-800k",
    "DDPM-800k independent":        "h1-scout-800k-v2",
    "DDIM-750k":                    "h1-scout-ddim-750k",
}

FLOAT_TOLERANCE = 0.002


# -------------------------------------------------------
# 3.  Parse claim matrix
# -------------------------------------------------------

def parse_phase_g_table(md_path: Path) -> list[dict]:
    """Extract rows from the Phase G unified comparison table.

    Returns a list of dicts with keys: label, auc, tpr_1pct, shuffle_auc.
    """
    if not md_path.exists():
        print(f"ERROR: claim matrix not found: {md_path}", file=sys.stderr)
        sys.exit(2)

    text = md_path.read_text(encoding="utf-8")

    # Locate the Phase G table: it starts after "**Phase G unified comparison:**"
    # and consists of pipe-table rows.
    marker = "**Phase G unified comparison:**"
    idx = text.find(marker)
    if idx == -1:
        print("ERROR: 'Phase G unified comparison' marker not found in claim matrix.",
              file=sys.stderr)
        sys.exit(2)

    # Slice from marker to next blank-line-separated block end
    tail = text[idx + len(marker):]
    lines = tail.splitlines()

    rows = []
    in_table = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_table:
                break  # blank line after table
            continue
        if line.startswith("|") and "Checkpoint" in line:
            in_table = True
            continue  # header row
        if line.startswith("|---"):
            continue  # separator row
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            # Expected: ["", label, auc, tpr, shuffle_auc, ""]
            cells = [c for c in cells if c]  # drop empty first/last from split
            if len(cells) >= 2:
                try:
                    rows.append({
                        "label": cells[0],
                        "auc": float(cells[1]),
                        "tpr_1pct": float(cells[2]) if len(cells) > 2 and cells[2] else None,
                        "shuffle_auc": float(cells[3]) if len(cells) > 3 and cells[3] else None,
                    })
                except ValueError:
                    print(f"WARNING: could not parse row: {line}", file=sys.stderr)
        elif in_table:
            # Table ended (non-pipe line after table rows)
            break

    return rows


# -------------------------------------------------------
# 4.  Parse summary.json (Schema A & B compatible)
# -------------------------------------------------------

def read_summary_metrics(summary_path: Path) -> dict | None:
    """Read a summary.json and return a flat metrics dict.

    Handles two schemas:
      Schema A: metrics.auc, metrics.tpr_1pct, metrics.label_shuffle_auc
      Schema B: metrics.auc, metrics.tpr_at_1pct_fpr, metrics.shuffle_auc

    Returns None if the file cannot be read or is malformed.
    """
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"WARNING: cannot parse {summary_path}: {exc}", file=sys.stderr)
        return None

    metrics = data.get("metrics", {})
    checkpoint = data.get("checkpoint", "?")

    auc = metrics.get("auc")
    tpr = metrics.get("tpr_1pct") or metrics.get("tpr_at_1pct_fpr")
    shuffle = metrics.get("label_shuffle_auc") or metrics.get("shuffle_auc")

    if auc is None:
        print(f"WARNING: {summary_path} has no metrics.auc", file=sys.stderr)
        return None

    return {
        "checkpoint": checkpoint,
        "auc": float(auc),
        "tpr": float(tpr) if tpr is not None else None,
        "shuffle_auc": float(shuffle) if shuffle is not None else None,
    }


# -------------------------------------------------------
# 5.  Cross-validate
# -------------------------------------------------------

def fmt_float(value: float | None, default: str = "—") -> str:
    """Format a float for display, trimming trailing zeros."""
    if value is None:
        return default
    return f"{value:g}"


def main() -> int:
    print(f"Evidence Gate Check — {date.today().isoformat()}")
    print("=" * 72)

    # --- Parse claims ---
    claim_rows = parse_phase_g_table(CLAIM_MATRIX_PATH)
    if not claim_rows:
        print("ERROR: no Phase G table rows parsed.", file=sys.stderr)
        return 2

    # --- Validate outputs directory exists ---
    if not OUTPUTS_DIR.exists():
        print(f"ERROR: outputs directory not found: {OUTPUTS_DIR}", file=sys.stderr)
        return 2

    # --- Cross-validate each claim (lazy summary.json reads) ---
    total = len(claim_rows)
    passed = 0
    failed = 0
    missing = 0

    for claim in claim_rows:
        label = claim["label"]
        expected_auc = claim["auc"]
        dir_name = PHASE_G_MAPPING.get(label)

        if dir_name is None:
            print(f"{label:<30s} {expected_auc:>8g}  →  ???                              UNMAPPED")
            failed += 1
            continue

        out_dir = OUTPUTS_DIR / dir_name
        summary_path = out_dir / "summary.json"

        # Format path for display (relative if possible)
        try:
            display_path = str(out_dir.relative_to(REPO_ROOT.parent))
        except ValueError:
            display_path = str(out_dir)

        # Lazily read summary.json only for mapped directories
        metrics = None
        if summary_path.exists():
            metrics = read_summary_metrics(summary_path)

        if metrics is None:
            reason = "FAIL (unreadable)" if summary_path.exists() else "MISSING (no summary.json)"
            if not summary_path.exists():
                missing += 1
            else:
                failed += 1
            print(f"{label:<30s} {expected_auc:>8g}  →  {display_path:<35s} {reason}")
            continue

        actual_auc = metrics["auc"]
        delta = abs(actual_auc - expected_auc)
        ok = delta <= FLOAT_TOLERANCE

        if ok:
            status = "PASS"
            passed += 1
        else:
            status = f"FAIL (Δ={delta:.6f})"
            failed += 1

        # Build detail string
        detail = status
        if metrics["checkpoint"] and metrics["checkpoint"] != "?":
            detail += f"  ckpt={metrics['checkpoint']}"

        print(f"{label:<30s} {expected_auc:>8g}  →  {display_path:<35s} {detail}")

    # --- Summary ---
    print()
    claim_word = "claim" if total == 1 else "claims"
    summary_parts = [f"{passed}/{total} {claim_word} verified"]
    if missing:
        summary_parts.append(f"{missing} missing summary.json")
    if failed:
        summary_parts.append(f"{failed} mismatches")
    print(f"Summary: {', '.join(summary_parts)}")

    if failed > 0 or missing > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
