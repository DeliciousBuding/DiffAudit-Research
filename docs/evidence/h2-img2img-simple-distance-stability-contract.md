# H2 Image-to-Image Simple-Distance Stability Contract

This note freezes the next decision for the simple image-to-image response
distance signal. It is a contract for a bounded stability packet, not an
authorization to scale H2 response-strength.

## Verdict

```text
eligible CPU contract; next GPU candidate is one non-overlapping simple-distance stability packet
```

The previous micro-packet found a high-strength simple-distance signal, but the
result is cache-local. The next valid test is a non-overlapping packet that
keeps the scoring surface minimal: one strength, fixed repeats, same local
assets, and the same finite-sample reporting boundary.

## Packet Identity

| Field | Value |
| --- | --- |
| Track | black-box |
| Method under test | simple image-to-image response distance |
| Not under test | H2 multi-strength logistic promotion |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split source | Recon `derived-public-25` |
| Sample range | positions `[10, 20)` for members and nonmembers |
| Relationship to prior packet | non-overlapping with the `derived-public-10` first-10 packet |
| Size | 10 member / 10 nonmember |
| Strength | `0.75` |
| Repeats | 2 |
| Inference steps | 30 |
| Primary scorer | simple negative minimum response RMSE at strength `0.75` |
| Secondary check | H2 cache evaluator for same-cache comparator context only |

The non-overlap claim relies on the local recon derived-public bundles being
prefix subsets from the same source ordering. The contract uses
`derived-public-25` with offset 10 so the selected positions are outside the
previous `derived-public-10` prefix.

## Gate

The packet is a stability check. It can only support a candidate simple-distance
claim if all checks hold:

| Check | Requirement |
| --- | --- |
| Cache schema | `labels`, `strengths`, `inputs`, `responses`, `min_distances_rmse` |
| Strength axis | exactly `0.75` |
| Empirical low-FPR boundary | report 0-FP TP count, not calibrated sub-percent FPR |
| AUC floor | `AUC >= 0.80` |
| Zero-FP floor | at least `2/10` member true positives at 0 false positives |
| Comparator boundary | do not claim H2 portability even if simple distance repeats |
| Promotion boundary | no Platform or Runtime schema change from this packet alone |

If the packet fails, close the simple-distance branch as negative-but-useful and
return to recon product-consumable strengthening.

## Frozen Commands

Dry-run the packet:

```powershell
python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --split-name derived-public-25 `
  --sample-offset 10 `
  --packet-size 10 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1
```

Collect the packet only after confirming GPU availability:

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

Review the generated cache:

```powershell
python -X utf8 scripts/review_h2_img2img_simple_distance.py `
  --response-cache workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/response-cache.npz `
  --output workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/simple-distance-review.json `
  --bootstrap-iters 200
```

## Boundary

- Do not run a larger packet before this stability packet has a verdict.
- Do not report `TPR@0.1%FPR` as calibrated with only 10 nonmembers.
- Do not merge the simple-distance signal into H2 response-strength claims.
- Commit only the verdict and compact summaries; keep response caches and
  generated images ignored.
