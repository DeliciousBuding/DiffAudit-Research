# Fashion-MNIST DDPM SimA Score-Norm Scout

> Date: 2026-05-14
> Status: weak / close Fashion-MNIST SimA score-norm / no expansion

## Question

On the same clean Fashion-MNIST train/test split used by the weak PIA-loss
scout, does a single-query SimA denoiser prediction-norm score separate
members from nonmembers?

This is a Lane B metric verdict. It tests a score-norm observable, not another
PIA-style denoising-loss, final-layer gradient, pixel/CLIP, mid-frequency, or
seed-stability variant.

## Contract

- Target model: `ynwag9/fashion_mnist_ddpm_32`.
- Target type: diffusers `DDPMPipeline` with gray-box access to UNet denoiser
  output.
- Member split: torchvision Fashion-MNIST train split, first `64` samples.
- Nonmember split: torchvision Fashion-MNIST test split, first `64` samples.
- Score: `negative_l4_unet_epsilon_prediction_norm_t100`; higher means more
  member-like.
- Fixed timestep: `100`.
- Fixed norm: `L4`.
- Device: local CUDA, RTX 4070.

Boundary: the Hugging Face repo still has no README/model card, so this assumes
standard Fashion-MNIST train/test semantics from the repository identity. It is
a scout, not admitted provenance.

## Command

Run from `Research/` with the CUDA-capable `diffaudit-research` environment:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/run_fashion_mnist_sima_score_norm.py `
  --dataset-root ..\Download\shared\datasets\fashion-mnist `
  --output workspaces\gray-box\artifacts\fashion-mnist-ddpm-sima-score-norm-20260514.json `
  --samples-per-split 64 `
  --batch-size 16 `
  --timestep 100 `
  --p-norm 4 `
  --noise-seed-base 20260514 `
  --device cuda `
  --local-files-only
```

## Result

Artifact:

`workspaces/gray-box/artifacts/fashion-mnist-ddpm-sima-score-norm-20260514.json`

| Metric | Value |
| --- | ---: |
| AUC | `0.515137` |
| ASR | `0.562500` |
| TPR@1%FPR | `0.000000` |
| TPR@0.1%FPR | `0.000000` |

Score means:

- member mean score: `-6.981945`
- nonmember mean score: `-6.992203`
- member mean prediction norm: `6.981945`
- nonmember mean prediction norm: `6.992203`

The member/nonmember score gap is tiny and strict-tail recovery is zero.

## Verdict

`weak / close Fashion-MNIST SimA score-norm / no expansion`.

This single-query score-norm mechanism does not rescue the Fashion-MNIST DDPM
line after the prior weak PIA-loss scout. Do not expand this into timestep,
`p`-norm, seed, packet-size, or scheduler sweeps.

## Reflection

This was the smallest useful follow-up because SimA is a genuinely different
observable family and the required denoiser access was already available. The
result is decision-changing in the negative direction: Fashion-MNIST DDPM has
now failed both fixed-timestep PIA-loss and fixed-timestep SimA score-norm
scouts, so this asset should not stay active.

## Platform and Runtime Impact

None. This is Research-only weak gray-box evidence. It is not an admitted row
and does not change Platform/Runtime schemas, product copy, or the admitted
bundle.
