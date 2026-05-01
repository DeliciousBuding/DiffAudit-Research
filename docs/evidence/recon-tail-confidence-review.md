# Recon Tail Confidence Review

> Status: active evidence hardening result as of 2026-05-01.

## Verdict

```text
recon remains admitted, but strict-tail wording must stay finite-sample
```

The admitted recon product card reports a nonzero strict-tail signal on the
public-100 target split. This CPU-only review adds confidence bounds around the
finite counts so downstream consumers do not overread the tail metric.

```powershell
python -X utf8 scripts/review_recon_tail_confidence.py
```

## Result

| Gate | Count estimate | Wilson 95% FPR interval | Wilson 95% TPR interval | Calibration verdict |
| --- | ---: | ---: | ---: | --- |
| `TPR@1%FPR` | `22/100 TP`, `1/100 FP` | `[0.001767, 0.054486]` | `[0.150013, 0.310704]` | Not calibrated to `1%` at 95% confidence. |
| `TPR@0.1%FPR` | `11/100 TP`, `0/100 FP` | `[0.000000, 0.036993]` | `[0.062542, 0.186313]` | Not calibrated to `0.1%` at 95% confidence. |

The result does not weaken the admitted recon row. It tightens the claim:
`TPR@0.1%FPR = 0.11` is a zero-false-positive empirical tail on 100 target
nonmembers, not a continuous sub-percent calibration statement.

## Decision

- Keep recon as the admitted black-box Platform/Runtime row.
- Keep the product card's finite-tail wording.
- Do not claim calibrated sub-percent FPR from public-100.
- Do not schedule a new GPU packet solely for wording cleanup.
- Reopen a recon scale-up GPU contract only if a product or paper claim needs
  calibrated low-FPR confidence rather than finite-count evidence.

## Boundary

This review is a statistical interpretation pass over the committed product
evidence card:
`workspaces/implementation/artifacts/recon-product-evidence-card.json`.

It does not create images, rerun the model, or change the artifact schema.
