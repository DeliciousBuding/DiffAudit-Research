# H2 Image-to-Image Simple-Distance Stability Result

This note records the non-overlapping stability packet for the simple
image-to-image response-distance signal. It is candidate evidence for a
standalone simple-distance black-box signal, not H2 response-strength promotion.

## Verdict

```text
positive-but-bounded simple-distance stability; not admitted evidence
```

The high-strength simple-distance signal survived a non-overlapping 10/10
packet. It cleared the frozen AUC and zero-false-positive gates with a stronger
tail than the first packet. The result is still bounded by one asset family,
small finite splits, and proxy recon-derived public subsets.

## Packet

| Field | Value |
| --- | --- |
| Run | `h2-img2img-simple-distance-stability-20260501-r1` |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split source | Recon `derived-public-25` |
| Sample positions | `[10, 20)` for members and nonmembers |
| Relationship to prior packet | no overlapping member or nonmember prompts with `h2-img2img-micro-20260501-r1` |
| Size | 10 member / 10 nonmember |
| Strength | `0.75` |
| Repeats | 2 |
| Inference steps | 30 |
| LoRA load mode | `unet_attn_procs` |

The raw cache, generated responses, and JSON run reviews are ignored local
artifacts under `workspaces/black-box/runs/`. This note is the canonical Git
evidence anchor.

## Metrics

| Packet | AUC | ASR | 0-FP TP | Empirical 0-FP TPR | Bootstrap 95% AUC |
| --- | ---: | ---: | ---: | ---: | --- |
| First micro packet, `derived-public-10` positions `[0, 10)` | 0.92 | 0.90 | 4/10 | 0.40 | 0.784875-1.0 |
| Stability packet, `derived-public-25` positions `[10, 20)` | 0.99 | 0.95 | 9/10 | 0.90 | 0.93-1.0 |

The finite-sample low-FPR fields mean zero false positives on 10 nonmembers.
They are not calibrated sub-percent FPR estimates.

## Same-Cache Context

The same cache evaluated with the H2 response-strength evaluator gives:

| Scorer | AUC | ASR | 0-FP TP |
| --- | ---: | ---: | ---: |
| Simple distance, strength 0.75 | 0.99 | 0.95 | 9/10 |
| Raw H2 logistic, one strength | 0.99 | 0.95 | 9/10 |
| Lowpass H2 logistic, one strength | 0.97 | 0.95 | 9/10 |

Because this packet has only one strength, H2 logistic is not evidence for the
multi-strength H2 hypothesis. It is effectively a learned monotone transform of
the same simple-distance feature.

## Decision

- The simple image-to-image response-distance signal is now a live black-box
  candidate, separate from H2 response-strength.
- Do not call it admitted evidence yet. Admission needs a larger, predeclared
  packet or a second asset-family check with the same finite-sample reporting
  discipline.
- Do not scale H2 response-strength as-is.
- The next CPU step should choose between a `25/25` simple-distance admission
  contract on `derived-public-50` and returning to recon product-consumable
  strengthening.
- No Platform or Runtime schema change is warranted from this result alone.

## Reproduction

Collect the ignored local cache:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --execute `
  --split-name derived-public-25 `
  --sample-offset 10 `
  --packet-size 10 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1 `
  --device cuda:0
```

Review the cache:

```powershell
python -X utf8 scripts/review_h2_img2img_simple_distance.py `
  --response-cache workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/response-cache.npz `
  --evaluation-summary workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/summary.json `
  --output workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/simple-distance-review.json `
  --bootstrap-iters 200
```
