# Gray-Box Tri-Score Truth-Hardening Review

> Date: 2026-05-10
> Status: positive-but-bounded; no GPU release

## Question

Does the consolidated CDI/TMIA-DM/PIA tri-score candidate survive a CPU-only
truth-hardening gate strongly enough to remain the next internal Research
candidate?

## Inputs

- Curated packet summary:
  `workspaces/gray-box/artifacts/graybox-triscore-consolidation-summary.json`
- Machine-readable review:
  `workspaces/gray-box/artifacts/graybox-triscore-truth-hardening-review.json`
- Consolidation review:
  [graybox-triscore-consolidation-review.md](graybox-triscore-consolidation-review.md)
- Admitted comparator:
  [admitted-results-summary.md](admitted-results-summary.md)

Command:

```powershell
python -X utf8 scripts/review_graybox_triscore_truth_hardening.py `
  --output workspaces\gray-box\artifacts\graybox-triscore-truth-hardening-review.json
```

## Gate

The CPU-only gate is intentionally conservative:

- `AUC` must beat the admitted PIA GPU512 baseline in at least `2 / 3` frozen
  packets.
- `TPR@1%FPR` must beat the admitted PIA GPU512 baseline in at least `2 / 3`
  frozen packets.
- `TPR@0.1%FPR` must be reported, but it cannot promote the candidate by
  itself.
- The internal-only contract must remain preserved:
  `headline_use_allowed = false`, no admitted row replacement, and no product
  promotion.

## Result

| Field | Value |
| --- | ---: |
| Packet count | `3` |
| Mean AUC | `0.854268` |
| Mean ASR | `0.786133` |
| Mean TPR@1%FPR | `0.106120` |
| Mean TPR@0.1%FPR | `0.031576` |
| AUC beats admitted PIA | `3 / 3` |
| TPR@1%FPR beats admitted PIA | `3 / 3` |
| TPR@0.1%FPR beats admitted PIA | `3 / 3` |

The weakest delta against admitted PIA remains positive for AUC and both
low-FPR fields:

| Metric | Minimum delta |
| --- | ---: |
| AUC | `+0.007908` |
| TPR@1%FPR | `+0.010742` |
| TPR@0.1%FPR | `+0.010742` |

ASR is not stable enough to be used as the support claim: it beats admitted PIA
in only `1 / 3` packets.

## Verdict

`positive-but-bounded`.

The tri-score line survives CPU truth-hardening as an internal candidate for
Research planning. It does not become an admitted gray-box row, a product-facing
result, or a GPU release candidate.

The strongest honest claim is:

> Across the frozen X-88/X-141/X-142 packet set, CDI/TMIA-DM/PIA tri-score
> aggregation consistently improves AUC and strict-tail fields over the
> admitted PIA GPU512 comparator, while remaining internal-only and
> contract-bound.

## Next Action

Do not run a larger same-contract tri-score packet. The next useful step is
either:

- design a genuinely story-changing tri-score expansion with a separate CPU
  preflight, or
- switch to black-box response-contract package acquisition when assets exist.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. Product-facing consumers should
continue using the admitted PIA row.
