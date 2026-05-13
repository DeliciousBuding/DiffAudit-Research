# Fashion-MNIST DDPM Score-Jacobian Sensitivity Scout

> Date: 2026-05-14
> Status: weak / close Fashion-MNIST score-Jacobian sensitivity / no expansion

## Question

On the same clean Fashion-MNIST train/test split used by the weak PIA-loss and
SimA score-norm scouts, does local UNet score-field sensitivity under a fixed
input perturbation direction separate members from nonmembers?

This is a Lane B metric verdict. It tests a local score-Jacobian observable,
not denoising MSE, not `x0` residual, not score norm, not final-layer gradient,
not pixel/CLIP distance, and not a mid-frequency repeat.

## Contract

- Target model: `ynwag9/fashion_mnist_ddpm_32`.
- Target type: diffusers `DDPMPipeline` with gray-box access to UNet denoiser
  output.
- Member split: torchvision Fashion-MNIST train split, first `64` samples.
- Nonmember split: torchvision Fashion-MNIST test split, first `64` samples.
- Score: `negative_l2_unet_epsilon_directional_derivative_norm_t100_delta0.01`;
  higher means more member-like.
- Fixed timestep: `100`.
- Fixed perturbation scale: `0.01`.
- Fixed norm: `L2`.
- Device: local CUDA, RTX 4070.

Boundary: the Hugging Face repo still has no README/model card, so this assumes
standard Fashion-MNIST train/test semantics from the repository identity. It is
a scout, not admitted provenance.

## Command

Run from `Research/` with the CUDA-capable `diffaudit-research` environment:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/run_fashion_mnist_score_jacobian_sensitivity.py `
  --dataset-root ..\Download\shared\datasets\fashion-mnist `
  --output workspaces\gray-box\artifacts\fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.json `
  --samples-per-split 64 `
  --batch-size 8 `
  --timestep 100 `
  --p-norm 2 `
  --perturbation-scale 0.01 `
  --noise-seed-base 20260514 `
  --perturbation-seed-base 20260515 `
  --device cuda `
  --local-files-only
```

## Result

Artifact:

`workspaces/gray-box/artifacts/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.json`

| Metric | Value |
| --- | ---: |
| AUC | `0.511719` |
| ASR | `0.546875` |
| TPR@1%FPR | `0.000000` |
| TPR@0.1%FPR | `0.000000` |

Score means:

- member mean score: `-5.463405`
- nonmember mean score: `-5.466835`
- member mean directional derivative norm: `5.463405`
- nonmember mean directional derivative norm: `5.466835`

The member/nonmember score gap is negligible and strict-tail recovery is zero.

## Verdict

`weak / close Fashion-MNIST score-Jacobian sensitivity / no expansion`.

This local score-field sensitivity observable does not rescue the
Fashion-MNIST DDPM line after prior weak fixed-timestep PIA-loss and SimA
score-norm scouts. Do not expand this into timestep, perturbation-scale, seed,
packet-size, scheduler, or norm sweeps.

## Reflection

This was a useful one-shot check because it tested the denoiser local response
surface rather than another absolute prediction norm or reconstruction error.
The result is decision-changing in the negative direction: the clean
Fashion-MNIST DDPM split now has weak results from loss, score-norm, and
score-Jacobian observables.

## Platform and Runtime Impact

None. This is Research-only weak gray-box evidence. It is not an admitted row
and does not change Platform/Runtime schemas, product copy, or the admitted
bundle.
