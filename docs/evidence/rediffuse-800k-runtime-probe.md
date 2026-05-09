# ReDiffuse 800k Runtime Probe

> Date: 2026-05-10
> Status: runtime-compatible; metrics not run

## Question

Can the collaborator `DDIMrediffuse` bundle load the existing PIA 800k CIFAR10
checkpoint and instantiate `ReDiffuseAttacker`?

This is a CPU runtime compatibility question, not an attack metric packet.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit runtime-probe-rediffuse `
  --checkpoint-path workspaces/gray-box/assets/pia/checkpoints/cifar10_ddpm/checkpoint.pt `
  --device cpu `
  --attack-num 1 `
  --interval 1 `
  --average 1 `
  --k 1
```

## Result

- `status = ready`
- `checkpoint_step = 800000`
- `weights_key = ema_model`
- `missing_keys = 0`
- `unexpected_keys = 0`
- `preview_forward = true`
- `intermediates_shape = [1, 1, 3, 32, 32]`
- `denoised_shape = [1, 1, 3, 32, 32]`

## Interpretation

The existing 800k PIA checkpoint is runtime-compatible with the collaborator
ReDiffuse UNet path. This means the 800k target can become a follow-up
ReDiffuse sanity packet after the 750k ResNet parity gate is resolved.

It does not establish ReDiffuse metrics on 800k, and it does not change the
admitted PIA/SecMI gray-box evidence.

## Verdict

Positive runtime probe. Hold metrics until the 750k `--scoring-mode resnet`
64/64 parity packet is documented.
