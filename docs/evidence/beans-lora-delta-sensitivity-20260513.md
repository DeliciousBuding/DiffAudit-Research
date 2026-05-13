# Beans LoRA Delta-Sensitivity Scout

> Date: 2026-05-13
> Status: negative_or_weak / close parameter-delta sensitivity / no expansion

## Question

Does a member-only Beans LoRA perturb the SD1.5 UNet noise prediction more
strongly on exact LoRA training members than on held-out Beans nonmembers?

This is a Lane B mechanism verdict, not another denoising-loss rerun. It uses
the exact target created by the Beans member-LoRA scout:

- target model: `stable-diffusion-v1-5` plus bounded Beans member-only UNet LoRA
- members: first `25` query/member PNGs used for LoRA training
- nonmembers: first `25` query/nonmember PNGs held out from LoRA training
- observable: relative L2 size of the LoRA-induced UNet noise-prediction delta
  against the base SD1.5 UNet on identical noisy latents, prompt, timesteps,
  and noise seeds

This is deliberately not raw denoising MSE, `x0` residual, pixel/CLIP distance,
final-layer gradient norm/cosine, midfreq cutoff, or a train-step/rank/timestep
matrix.

## Command

Run from `Research/` with the CUDA-capable `diffaudit-research` environment:

```powershell
python -X utf8 scripts/run_beans_lora_delta_sensitivity.py `
  --dataset-root ../Download/black-box/datasets/response-contract-beans-sd15-20260512 `
  --sd15-model-dir ../Download/shared/weights/stable-diffusion-v1-5 `
  --lora-state ../Download/black-box/weights/beans-lora-member-denoising-loss-20260513/unet_lora_peft_state.pt `
  --output workspaces/black-box/artifacts/beans-lora-delta-sensitivity-20260513.json `
  --samples-per-split 25 `
  --image-size 256 `
  --score-timesteps 100,300,600 `
  --device cuda
```

## Result

Primary score:
`mean_relative_unet_prediction_delta_l2_after_member_lora`, higher means more
member-like.

| Packet | AUC | Reverse AUC | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Beans LoRA delta sensitivity `25/25` | `0.512000` | `0.488000` | `0.600000` | `0.040000` | `0.040000` |

Secondary score:
`mean_base_minus_lora_denoising_loss_delta`, higher means the LoRA improves
denoising loss more.

| Packet | AUC | Reverse AUC | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Beans LoRA loss delta `25/25` | `0.468800` | `0.531200` | `0.540000` | `0.000000` | `0.000000` |

The primary score means are effectively identical:

- member mean relative delta: `0.199573`
- nonmember mean relative delta: `0.199563`

The zero-FP threshold recovers only `1 / 25` members. The secondary loss-delta
direction is worse than random and has no zero-FP member recovery.

## Artifacts

- JSON summary:
  `workspaces/black-box/artifacts/beans-lora-delta-sensitivity-20260513.json`
- Runner:
  `scripts/run_beans_lora_delta_sensitivity.py`
- LoRA state dict used as input, stored outside Git:
  `<DOWNLOAD_ROOT>/black-box/weights/beans-lora-member-denoising-loss-20260513/unet_lora_peft_state.pt`
- LoRA state SHA256:
  `ea917e662387bfe8841edcfa832dcd56b4aef7dcb2ad78791930d12e8aa0c654`

## Verdict

`negative_or_weak / close parameter-delta sensitivity / no expansion`.

This bounded mechanism scout tested whether the member-only adapter has a
stronger architecture-local effect on its own training members. It does not:
AUC is near random, low-FPR recovery is one sample, and score means overlap.

Do not expand this into layer/block, timestep, prompt, rank, train-step,
resolution, scheduler, or loss-delta matrices. Beans LoRA has now failed both
conditional denoising-loss and parameter-delta sensitivity under the repaired
known-split membership semantics.

## Reflection

This cycle tested a genuinely different observable on an already clean local
target. It produced a metric verdict rather than another artifact audit, and
the result closes this Beans LoRA mechanism family instead of creating a new
ablation surface.

## Platform and Runtime Impact

None. This is a Research-only known-split internal mechanism scout. It is not
admitted evidence, not a black-box product row, and not a replacement for
`recon`, PIA, GSA, or DPDM evidence.
