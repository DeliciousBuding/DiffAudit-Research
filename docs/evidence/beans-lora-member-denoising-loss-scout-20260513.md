# Beans LoRA Member Denoising-Loss Scout

> Date: 2026-05-13
> Status: weak; close this exact known-split LoRA route

## Question

If the local SD1.5 target is fine-tuned with a small UNet LoRA on the Beans
`member` split, does conditional denoising loss separate exact LoRA training
members from held-out Beans nonmembers?

This is a membership-semantics repair of the earlier Beans/SD1.5 response
contract. The older package treated Beans train/validation as a debug split for
base SD1.5 and therefore could not prove SD1.5 training membership. This scout
changes the target identity to a locally fine-tuned target:

- target model: `stable-diffusion-v1-5` plus a bounded Beans member-only UNet
  LoRA
- members: first `25` query/member PNGs used for LoRA training
- nonmembers: first `25` query/nonmember PNGs held out from LoRA training
- access: internal denoising-loss scoring, not a black-box response-contract
  result

## Command

Run from `Research/` with the CUDA-capable `diffaudit-research` environment:

```powershell
python -X utf8 scripts/run_beans_lora_member_scout.py `
  --dataset-root ../Download/black-box/datasets/response-contract-beans-sd15-20260512 `
  --sd15-model-dir ../Download/shared/weights/stable-diffusion-v1-5 `
  --download-root ../Download `
  --weights-output-dir ../Download/black-box/weights/beans-lora-member-denoising-loss-20260513 `
  --output workspaces/black-box/artifacts/beans-lora-member-denoising-loss-scout-20260513.json `
  --samples-per-split 25 `
  --train-steps 120 `
  --batch-size 1 `
  --image-size 256 `
  --score-timesteps 100,300,600 `
  --lora-rank 4 `
  --lora-alpha 4 `
  --learning-rate 1e-5 `
  --device cuda
```

The runner first passed a tiny `2/2` CUDA smoke after stabilizing LoRA training
with fp32 trainable adapter weights and gradient clipping. The smoke is not a
benchmark result.

## Result

| Packet | AUC | Reverse AUC | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Beans member-LoRA `25/25` | `0.414400` | `0.585600` | `0.540000` | `0.080000` | `0.080000` |

The score is `negative_mean_conditional_denoising_loss_after_member_lora`, so
higher should mean more member-like. The member mean loss is worse than the
nonmember mean loss:

- member mean loss: `0.322735`
- nonmember mean loss: `0.317327`

The zero-FP threshold recovers only `2 / 25` members. The reverse direction is
still below the `0.60` continuation gate, so this is not a hidden positive.

## Artifacts

- JSON summary:
  `workspaces/black-box/artifacts/beans-lora-member-denoising-loss-scout-20260513.json`
- LoRA state dict, stored outside Git:
  `<DOWNLOAD_ROOT>/black-box/weights/beans-lora-member-denoising-loss-20260513/unet_lora_peft_state.pt`
- LoRA state SHA256:
  `ea917e662387bfe8841edcfa832dcd56b4aef7dcb2ad78791930d12e8aa0c654`

## Verdict

`weak; close this exact Beans LoRA denoising-loss scout`.

This scout repaired the membership semantics by creating a target model with
known LoRA training members, but the tested conditional denoising-loss
observable does not separate members from held-out nonmembers. Do not expand
this into train-step, rank, resolution, prompt, scheduler, loss-weight, or
timestep matrices.

## Platform and Runtime Impact

None. This is not admitted evidence, not a black-box product row, and not a
replacement for `recon`, PIA, GSA, or DPDM evidence.
