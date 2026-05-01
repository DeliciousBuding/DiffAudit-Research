# H2 Image-to-Image Simple-Distance Admission Result

This note records the 25 member / 25 nonmember admission-scale packet for the
simple image-to-image response-distance signal. It is evidence for a bounded
single-asset black-box signal, not H2 response-strength promotion.

## Verdict

```text
positive bounded single-asset evidence; not a conditional-diffusion generalization
```

The frozen admission packet passed its predeclared AUC and zero-false-positive
gates. The result is materially weaker than the prior 10/10 stability packet
but still clears the admission-scale contract on a non-overlapping sample
window. The line should now be treated as a real black-box candidate with
bounded evidence on this Stable Diffusion v1.5 + CelebA-style image-to-image
asset family.

It should not replace the recon product row yet. Recon remains the strongest
product-consumable black-box evidence because it is already integrated into the
unified attack-defense table and product handoff.

## Packet

| Field | Value |
| --- | --- |
| Run | `h2-img2img-simple-distance-admission-20260501-r1` |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split source | Recon `derived-public-50` |
| Sample positions | `[20, 45)` for members and nonmembers |
| Relationship to prior packets | non-overlapping with prior `[0, 10)` and `[10, 20)` packets |
| Size | 25 member / 25 nonmember |
| Strength | `0.75` |
| Repeats | 2 |
| Inference steps | 30 |
| LoRA load mode | `unet_attn_procs` |
| Collection wall clock | 271.097571 seconds |

The raw cache, generated responses, and JSON run reviews are ignored local
artifacts under `workspaces/black-box/runs/`. This note is the canonical Git
evidence anchor.

## Gate Result

| Gate | Requirement | Result |
| --- | ---: | ---: |
| AUC floor | `>= 0.85` | `0.8768` |
| Zero-FP floor | `>= 8/25` TP at 0 FP | `11/25` |
| Sample count | 25 member / 25 nonmember | passed |
| Strength axis | exactly `0.75` | passed |
| H2 promotion boundary | no H2 promotion | passed |

The finite low-FPR fields are zero-false-positive empirical tails over 25
nonmembers. They are not calibrated sub-percent false-positive-rate estimates.

## Metrics

| Packet | AUC | ASR | 0-FP TP | Empirical 0-FP TPR | Bootstrap 95% AUC |
| --- | ---: | ---: | ---: | ---: | --- |
| First micro packet, `derived-public-10` positions `[0, 10)` | 0.92 | 0.90 | 4/10 | 0.40 | 0.784875-1.0 |
| Stability packet, `derived-public-25` positions `[10, 20)` | 0.99 | 0.95 | 9/10 | 0.90 | 0.93-1.0 |
| Admission packet, `derived-public-50` positions `[20, 45)` | 0.8768 | 0.84 | 11/25 | 0.44 | 0.76914-0.95642 |

The larger packet lowers the effect estimate but does not erase the signal. The
bootstrap interval remains wide, so the correct interpretation is bounded
single-asset evidence rather than a broad method claim.

## Same-Cache Context

| Scorer | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Simple distance, strength 0.75 | 0.8768 | 0.84 | 0.44 | 0.44 |
| Raw H2 logistic, one strength | 0.8656 | 0.84 | 0.40 | 0.40 |
| Lowpass H2 logistic, one strength | 0.8656 | 0.84 | 0.40 | 0.40 |

The one-strength logistic references are same-cache context only. They do not
support H2 response-strength promotion because the multi-strength curve
hypothesis is not tested here.

## Decision

- The simple image-to-image response-distance signal has passed the frozen
  admission-scale packet as bounded single-asset black-box evidence.
- Do not present it as conditional-diffusion-general evidence.
- Do not merge it into H2 response-strength claims.
- Do not replace the recon product row until a product bridge maps this signal
  into a stable artifact schema and compares it against recon under the same
  consumer-facing evidence standard.
- The next CPU task should design either a second-asset portability contract or
  a recon-vs-simple-distance product bridge comparison. No next GPU task is
  selected from this result alone.

## Reproduction

Collect the ignored local cache:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --execute `
  --split-name derived-public-50 `
  --sample-offset 20 `
  --packet-size 25 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1 `
  --device cuda:0
```

Review the cache:

```powershell
python -X utf8 scripts/evaluate_h2_response_cache.py `
  --response-cache workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/response-cache.npz `
  --output workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/summary.json `
  --bootstrap-iters 500 `
  --holdout-repeats 7
```

```powershell
python -X utf8 scripts/review_h2_img2img_simple_distance.py `
  --response-cache workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/response-cache.npz `
  --evaluation-summary workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/summary.json `
  --output workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/simple-distance-review.json `
  --bootstrap-iters 500
```
