# ReDiffuse Checkpoint-Portability Gate

> Date: 2026-05-10
> Status: blocked-by-scoring-contract; no GPU release

## Question

Does 800k runtime compatibility justify a ReDiffuse metrics packet?

## Hypothesis

A ReDiffuse 800k packet is releasable only if both conditions hold:

- checkpoint/runtime portability is established,
- the ReDiffuse scorer contract is resolved.

## CPU Review

Command shape:

```powershell
python -X utf8 scripts/review_rediffuse_checkpoint_portability_gate.py `
  --collaborator-checkpoint <DIFFAUDIT_ROOT>\Download\shared\weights\ddim-cifar10-step750000\raw\DDIM-ckpt-step750000.pt `
  --comparison-checkpoint workspaces\gray-box\assets\pia\checkpoints\cifar10_ddpm\checkpoint.pt `
  --split-path <DIFFAUDIT_ROOT>\Download\shared\supplementary\collaborator-ddim-rediffuse-20260509\raw\DDIMrediffuse\CIFAR10_train_ratio0.5.npz
```

The command is CPU-only. It reads checkpoint metadata, verifies the collaborator
CIFAR10 split hash, and checks the current scoring-contract evidence boundary.
It does not score member/nonmember samples.

The default arguments assume the standard local `Download/` layout documented
for Research assets. A clean Git checkout without those local assets can still
run the unit tests, but cannot reproduce the real checkpoint metadata review.

## Result

| Gate | Value |
| --- | --- |
| 750k checkpoint step | `750000` |
| 800k checkpoint step | `800000` |
| State-dict key count match | `329 / 329` |
| Split hash match | true |
| Runtime/checkpoint compatible | true |
| Scoring contract resolved | false |
| Release gate passed | false |

## Verdict

`blocked-by-scoring-contract`.

The 800k checkpoint remains runtime-compatible with the ReDiffuse adapter, but
runtime compatibility is not enough to release a metrics packet. The existing
750k ResNet parity packet is negative, and the direct-distance boundary review
already blocks treating the proxy score as a paper-faithful ReDiffuse result.

This closes the immediate 800k checkpoint-portability shortcut:

- do not run an 800k direct-distance packet,
- do not run an 800k ResNet packet until the 750k scorer-contract ambiguity is
  resolved,
- keep 800k as runtime compatibility evidence only.

## Next Action

If ReDiffuse continues, the next CPU-first task should be exact ResNet contract
replay against the collaborator `nns_attack` semantics, not another direct
distance packet.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
