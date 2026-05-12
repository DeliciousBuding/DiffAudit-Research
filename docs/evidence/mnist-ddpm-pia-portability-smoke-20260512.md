# MNIST DDPM PIA Portability Smoke

> Date: 2026-05-12
> Status: weak / no GPU release

## Question

If we leave the old DDPM/CIFAR10 loop and score a second public DDPM dataset,
does the simplest PIA-style noise-prediction loss still separate members from
nonmembers?

This is a taste-check smoke, not a promoted benchmark. The goal is to decide
whether direct score transfer is promising enough to formalize before spending
more engineering or GPU time.

## Setup

- Model: `1aurent/ddpm-mnist`
- Dataset: Hugging Face `mnist`
- Member split: first `16` train images
- Nonmember split: first `16` test images
- Timesteps: `50`, `200`, `500`, `800`
- Device: CPU
- Score: mean noise-prediction MSE across the four timesteps
- Membership rule for AUC: lower loss is more member-like

The model and dataset loaded in the local Python environment with
`torch 2.11.0+cpu`, `diffusers 0.37.1`, and `datasets 4.8.4`.

## Command

This was run as a one-off inline CPU scout from the repository root. It did not
add a new script or validator.

```powershell
python -X utf8 - <<'PY'
# Load 1aurent/ddpm-mnist and Hugging Face mnist, score first 16 train and
# first 16 test images by noise-prediction MSE at timesteps 50/200/500/800.
PY
```

PowerShell execution used an equivalent here-string piped into
`python -X utf8 -`.

## Result

| Metric | Value |
| --- | ---: |
| member mean loss | `0.035238` |
| nonmember mean loss | `0.035915` |
| AUC, lower loss = member | `0.496094` |
| best ASR | `0.562500` |

The member and nonmember losses are almost overlapping at this tiny scale.

## Verdict

`weak / no GPU release`.

This scout does not prove that MNIST/DDPM has no privacy signal. It does show
that the most direct PIA-style loss transfer is not an obvious win on a second
public DDPM dataset. Treat this as a route decision:

- Do not formalize a larger MNIST/DDPM run unless there is a better scoring
  hypothesis than raw noise-prediction MSE.
- Do not turn this into another toolchain or ablation table.
- The higher-value next step remains a real second response-contract package,
  or a sharper second-model scorer that can plausibly change the portability
  decision.

## Per-Timestep Guard

To check whether the four-timestep average hid a local signal, a second CPU
scout reused the same `16 / 16` split and scored individual timesteps only. No
sample expansion, GPU run, or new script was added.

| Timestep | AUC, lower loss = member | Best ASR |
| ---: | ---: | ---: |
| `0` | `0.488281` | `0.562500` |
| `25` | `0.484375` | `0.562500` |
| `50` | `0.507812` | `0.625000` |
| `100` | `0.578125` | `0.625000` |
| `200` | `0.441406` | `0.531250` |
| `350` | `0.578125` | `0.656250` |
| `500` | `0.578125` | `0.625000` |
| `650` | `0.570312` | `0.625000` |
| `800` | `0.578125` | `0.625000` |
| `950` | `0.503906` | `0.562500` |

Best single-timestep AUC was `0.578125`. The weak average result was therefore
not hiding an obvious high-AUC timestep.

Decision: close MNIST/DDPM raw-loss portability unless a new scorer changes the
observable, such as a calibrated likelihood proxy, per-class conditioning, or a
residual feature that is not just raw noise-prediction MSE.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
