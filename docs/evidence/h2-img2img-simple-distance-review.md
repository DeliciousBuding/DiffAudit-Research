# H2 Image-to-Image Simple-Distance Review

This note reviews the strongest signal from the frozen SD/CelebA image-to-image
micro-packet: simple response distance at high image-to-image strength. It does
not reopen H2 response-strength promotion.

## Verdict

```text
candidate simple-distance signal; needs independent split or seed stability
```

The simple high-strength response-distance score is stronger than the H2
multi-strength logistic curve on the frozen 10/10 cache. The result is still too
small and too cache-local for promotion.

## Reviewed Cache

| Field | Value |
| --- | --- |
| Run | `h2-img2img-micro-20260501-r1` |
| Samples | 10 member / 10 nonmember |
| Strengths | `0.35`, `0.55`, `0.75` |
| Review script | `scripts/review_h2_img2img_simple_distance.py` |
| Output | `workspaces/black-box/runs/h2-img2img-micro-20260501-r1/simple-distance-review.json` |

The JSON output is a local ignored artifact. This note is the canonical Git
evidence anchor.

## Result

| Strength | AUC | ASR | 0-FP TP | Empirical 0-FP TPR | Bootstrap 95% AUC |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.35 | 0.67 | 0.70 | 2/10 | 0.20 | 0.394625-0.8755 |
| 0.55 | 0.85 | 0.85 | 3/10 | 0.30 | 0.634875-0.98 |
| 0.75 | 0.92 | 0.90 | 4/10 | 0.40 | 0.784875-1.0 |

The best simple score is `strength = 0.75`. It beats both H2 logistic references
on AUC:

| Scorer | AUC | ASR | 0-FP TP |
| --- | ---: | ---: | ---: |
| Best simple distance, strength 0.75 | 0.92 | 0.90 | 4/10 |
| Raw H2 logistic | 0.84 | 0.80 | 4/10 |
| Lowpass H2 logistic | 0.85 | 0.85 | 4/10 |

Because the split has only 10 nonmembers, the low-FPR fields mean zero false
positives on this finite split. They are not calibrated sub-percent FPR
estimates.

## Stability Check

| Strength Pair | Spearman |
| --- | ---: |
| 0.35 vs 0.55 | 0.73985 |
| 0.35 vs 0.75 | 0.47218 |
| 0.55 vs 0.75 | 0.781955 |

The high-strength score is promising, but cross-strength rank stability is not
strong enough to justify scale-up without a new stability contract.

## Decision

- Do not scale H2 response-strength as-is.
- Treat simple image-to-image response distance as a separate black-box
  candidate, not as H2 portability evidence.
- Next step should be CPU-first: freeze a stability contract that tests either
  an independent seed on the same 10/10 split or a non-overlapping split before
  any further GPU packet.
- No Platform or Runtime schema change is warranted.

## Reproduction

```powershell
python -X utf8 scripts/review_h2_img2img_simple_distance.py `
  --response-cache workspaces/black-box/runs/h2-img2img-micro-20260501-r1/response-cache.npz `
  --evaluation-summary workspaces/black-box/runs/h2-img2img-micro-20260501-r1/summary.json `
  --output workspaces/black-box/runs/h2-img2img-micro-20260501-r1/simple-distance-review.json `
  --bootstrap-iters 200
```
