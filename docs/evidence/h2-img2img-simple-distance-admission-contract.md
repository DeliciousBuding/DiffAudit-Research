# H2 Image-to-Image Simple-Distance Admission Contract

This note freezes the next bounded GPU candidate for the simple
image-to-image response-distance signal. It is not an H2 response-strength
promotion contract.

## Verdict

```text
eligible admission-scale candidate; next GPU task is frozen but not yet run
```

The simple high-strength response-distance signal has survived two small
packets on non-overlapping sample positions. The next useful step is not another
10/10 stability probe. It is a larger predeclared packet that tests whether the
same one-feature scorer keeps a usable finite-tail signal under a 25 member /
25 nonmember split.

This is still one asset family and one query surface. Passing this contract can
promote the method from live candidate to stronger bounded black-box evidence,
but it cannot establish portability to conditional diffusion in general.

## Packet Identity

| Field | Value |
| --- | --- |
| Track | black-box |
| Method under test | simple image-to-image response distance |
| Not under test | H2 multi-strength logistic response-strength |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split source | Recon `derived-public-50` |
| Sample range | positions `[20, 45)` for members and nonmembers |
| Relationship to prior packets | non-overlapping with prior `[0, 10)` and `[10, 20)` packets under prefix-order split construction |
| Size | 25 member / 25 nonmember |
| Strength | `0.75` |
| Repeats | 2 |
| Inference steps | 30 |
| Primary scorer | simple negative minimum response RMSE at strength `0.75` |
| Secondary check | H2 cache evaluator for same-cache comparator context only |

The contract reserves `derived-public-50` positions `[0, 20)` for the two
already-reviewed packets. The selected `[20, 45)` window uses a larger split
without overlapping those reviewed positions.

## Gate

The packet can support admission as bounded black-box evidence only if all
checks hold:

| Check | Requirement |
| --- | --- |
| Cache schema | `labels`, `strengths`, `inputs`, `responses`, `min_distances_rmse` |
| Strength axis | exactly `0.75` |
| Sample count | exactly 25 member and 25 nonmember samples |
| Empirical low-FPR boundary | report 0-FP TP count; do not report calibrated sub-percent FPR |
| AUC floor | `AUC >= 0.85` |
| Zero-FP floor | at least `8/25` member true positives at 0 false positives |
| Stability floor | no contradiction with prior two positive packets under the same scorer |
| Comparator boundary | H2 logistic outputs are context only, not H2 promotion evidence |
| Promotion boundary | no Platform or Runtime schema change unless the product bridge later admits a new result row |

If the packet fails either the AUC floor or zero-FP floor, close the
simple-distance escalation as negative-but-useful and return to recon
product-consumable strengthening.

## Frozen Commands

Dry-run the packet:

```powershell
python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --split-name derived-public-50 `
  --sample-offset 20 `
  --packet-size 25 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1
```

Collect the packet only after confirming GPU availability:

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

Review the generated cache:

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

## Boundary

- Run no other GPU task concurrently.
- Commit only the verdict note and compact summaries after execution.
- Keep response caches and generated images ignored under `workspaces/black-box/runs/`.
- Do not call a passing result conditional-diffusion evidence.
- Do not merge this line into H2 response-strength claims.
