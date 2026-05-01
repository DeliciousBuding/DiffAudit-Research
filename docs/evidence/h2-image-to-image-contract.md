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

The CPU evaluator already accepts image-to-image caches with a `strengths`
axis:

```powershell
python -X utf8 scripts/evaluate_h2_response_cache.py `
  --response-cache workspaces/black-box/runs/<run-id>/response-cache.npz `
  --output workspaces/black-box/runs/<run-id>/summary.json
```

The missing piece is only the thin image-to-image response collector that writes
an ignored cache with `labels`, `strengths`, `inputs`, `responses`, and
`min_distances_rmse`. After that exists, run only the frozen 10/10 packet if GPU
memory is available. The canonical Git evidence should be a compact summary and
verdict, not generated images or raw caches.
