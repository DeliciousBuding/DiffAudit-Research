# H2 Image-to-Image Portability Contract

This note records the CPU contract that reopens H2 response-strength as a
bounded cross-asset candidate. It does not promote H2 and does not authorize an
unbounded GPU sweep.

## Verdict

```text
eligible CPU contract; next GPU candidate is a micro image-to-image packet
```

The previous SD/CelebA check was negative because a prompt-only text-to-image
endpoint cannot instantiate H2 response-strength. The image-to-image contract is
different: it supplies a query image, controlled stochastic repeats, and
observable response images. Under those conditions the local assets are ready.

The frozen 10/10 micro-packet has now been run. Its verdict is recorded in
[h2-img2img-micro-result.md](h2-img2img-micro-result.md): H2 remains
candidate-only because the multi-strength logistic curve does not beat the
same-cache simple distance comparator.

## CPU Probe

Command:

```powershell
python -X utf8 scripts/probe_h2_cross_asset_contract.py `
  --endpoint-mode image_to_image `
  --controlled-repeats `
  --response-images-observable
```

Result on 2026-05-01:

| Check | Result |
| --- | --- |
| Endpoint mode | `image_to_image` |
| SD1.5 local assets | ready |
| CelebA image and annotation assets | ready |
| Recon CelebA public splits and target LoRA | ready |
| Controlled repeats | ready |
| Response images observable | ready |
| Status | `eligible_cpu_contract` |

The default text-to-image probe remains blocked and should not be used for H2
portability claims.

## Frozen Micro-Packet

The next GPU task, if scheduled, should be deliberately small:

| Field | Value |
| --- | --- |
| Track | black-box |
| Method | H2 response-strength |
| Asset family | Stable Diffusion v1.5 + CelebA-style image-to-image |
| Split source | Recon CelebA `derived-public-10` target member/nonmember |
| Packet size | 10 member / 10 nonmember |
| Repeats | 2 |
| Strength schedule | 2 or 3 fixed image-to-image strengths, predeclared |
| Primary scorer | response-distance logistic over the fixed strength curve |
| Secondary scorer | best simple same-cache low-FPR scorer |
| Release gate | nonzero `TPR@0.1%FPR` plus better low-FPR tail than simple same-cache comparator |

This packet is a protocol scout, not an admitted evidence run. The target split
has only 10 nonmembers, so any strict-tail result must be reported as a
zero-false-positive empirical tail, not calibrated sub-percent FPR.

## Blocked Claims

- Do not claim H2 transfers from DDPM/CIFAR10 to conditional diffusion.
- Do not compare this packet against the admitted recon row as a replacement.
- Do not run a larger GPU packet until the micro-packet produces a coherent
  response cache and a reviewed summary schema.
- Do not use prompt-only text-to-image outputs as H2 response-strength evidence.

## Next Action

The response-cache collector now exists as a guarded runner. It defaults to a
dry-run plan and only collects GPU responses when `--execute` is passed:

```powershell
python -X utf8 scripts/collect_h2_img2img_response_cache.py
```

The frozen GPU micro-packet command is:

```powershell
python -X utf8 scripts/collect_h2_img2img_response_cache.py `
  --execute `
  --packet-size 10 `
  --strengths 0.35 0.55 0.75 `
  --repeats 2 `
  --device cuda:0
```

The collector writes ignored local artifacts under
`workspaces/black-box/runs/<run-id>/` and must not be used for a larger packet
until the 10/10 cache has been evaluated and reviewed.

The CPU evaluator accepts the generated image-to-image cache with a `strengths`
axis:

```powershell
python -X utf8 scripts/evaluate_h2_response_cache.py `
  --response-cache workspaces/black-box/runs/<run-id>/response-cache.npz `
  --output workspaces/black-box/runs/<run-id>/summary.json
```

The cache schema is frozen as `labels`, `strengths`, `inputs`, `responses`, and
`min_distances_rmse`, with optional `lowpass_min_distances_rmse`. The canonical
Git evidence should be a compact summary and verdict, not generated images or
raw caches.
