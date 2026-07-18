# Exploratory fault injection E4–E5 (2026-07-18)

- Class: **exploratory / non-confirmatory**
- Claim ceiling: **unchanged** (Route C audit-failure / non-reproduction only)
- Formal: **hold**
- Never merge into confirmatory main Results tables

## Scripts

| Script | Role |
|--------|------|
| `scripts/paper/run_faultinj_e5_offline.py` | E5 positive/noise offline assay |
| `scripts/paper/run_faultinj_e4_proxy_offline.py` | E4 invalid-label proxy on sealed features |
| `scripts/paper/run_faultinj_e4_gpu_micro.py` | E4 short-train GPU micro (cuDNN-hardened) |

## Outcomes (public-safe summary)

| Run | Result |
|-----|--------|
| E5 positive leak | PASS (AUC point ≥ 0.99 on eval) |
| E5 pure noise | PASS (CI covers 0.50; near-chance point) |
| E4 proxy / GPU 800 / GPU 1500 | pathology mark **false** under short budget |
| E4 GPU 2500 | incomplete (cuDNN engineering failure); **no AUCs invented** |

## Interpretation (allowed)

- E5: sealed near-chance H1/PIA are not explained by a totally dead offline scoring pipeline.
- E4 short budgets: invalid-GT micro-demo did **not** clear the illustrative pathology mark.
- Route C remains contract discipline + non-reproduction.

## Forbidden

- Confirmatory promotion
- Invented incomplete-run AUCs
- Threshold edits / formal resume from these runs
- Venue strategy or private manuscript paths in this public note

## Local receipts

Machine receipts and logs live under the local ignored `outputs/paper1-corrected-evidence/fault-injection/` tree when present. Public git tracks scripts + this summary only.
