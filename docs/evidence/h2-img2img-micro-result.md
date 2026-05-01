# H2 Image-to-Image Micro-Packet Result

This note records the first frozen SD/CelebA image-to-image H2 micro-packet. It
is a protocol scout, not admitted black-box evidence.

## Verdict

```text
negative-but-useful for H2 curve promotion; positive simple-distance signal
```

The image-to-image contract is runnable and produces a valid response cache, but
the primary H2 logistic curve does not beat the same-cache simple low-FPR
comparator. The packet therefore does not promote H2 portability beyond
`DDPM/CIFAR10`.

## Packet

| Field | Value |
| --- | --- |
| Run | `h2-img2img-micro-20260501-r1` |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split | Recon `derived-public-10` |
| Size | 10 member / 10 nonmember |
| Strengths | `0.35`, `0.55`, `0.75` |
| Repeats | 2 |
| Inference steps | 30 |
| LoRA load mode | `unet_attn_procs` |
| Cache schema | `labels`, `strengths`, `inputs`, `responses`, `min_distances_rmse`, `lowpass_min_distances_rmse` |

The raw response cache and generated responses are local ignored artifacts under
`workspaces/black-box/runs/` and are not Git evidence.

## Metrics

| Scorer | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Raw H2 logistic | 0.84 | 0.80 | 0.40 | 0.40 | 4/10 TP at 0 FP on this finite split |
| Lowpass H2 logistic | 0.85 | 0.85 | 0.40 | 0.40 | 4/10 TP at 0 FP on this finite split |
| Best simple raw distance, strength 0.75 | 0.92 | 0.90 | 0.40 | 0.40 | 4/10 TP at 0 FP on this finite split |
| Best simple lowpass distance, strength 0.75 | 0.92 | 0.90 | 0.40 | 0.40 | 4/10 TP at 0 FP on this finite split |

With only 10 nonmembers, `TPR@1%FPR` and `TPR@0.1%FPR` both mean a zero-false
positive empirical tail. They are not calibrated sub-percent FPR estimates.

## Decision

- H2 image-to-image is protocol-runnable on the local SD/CelebA assets.
- H2 response-strength remains candidate-only and is not promoted.
- The strongest signal in this packet is simple image-to-image response
  distance at high strength, not the H2 multi-strength logistic curve.
- Do not scale this H2 packet as-is. The next black-box research question should
  either test whether the simple distance signal is a stable recon-adjacent
  baseline, or return to recon product-consumable strengthening.

## Reproduction Commands

Collect the ignored local cache:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --execute `
  --packet-size 10 `
  --strengths 0.35 0.55 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-micro-20260501-r1 `
  --device cuda:0
```

Evaluate the cache:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/evaluate_h2_response_cache.py `
  --response-cache workspaces/black-box/runs/h2-img2img-micro-20260501-r1/response-cache.npz `
  --output workspaces/black-box/runs/h2-img2img-micro-20260501-r1/summary.json `
  --bootstrap-iters 200 `
  --holdout-repeats 7
```
