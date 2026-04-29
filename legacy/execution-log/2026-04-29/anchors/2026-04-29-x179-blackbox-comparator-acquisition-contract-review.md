# X-179 Black-Box Comparator-Acquisition Contract Review

Date: 2026-04-29
Status: `positive contract review / no GPU release`

## Question

After `X-178` proved that direct same-packet admitted `recon` comparison is protocol-blocked, is there any compatible comparator-acquisition path that should release a new GPU task now?

## Inputs

- X176 H2 validation summary:
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/summary.json`
- X178 comparator feasibility review:
  - `workspaces/implementation/2026-04-29-x178-same-packet-recon-comparator-feasibility-review.md`
- H2 scripts:
  - `legacy/execution-log/2026-04-29/scripts/run_x168_blackbox_h2_strength_response_gpu_scout.py`
  - `legacy/execution-log/2026-04-29/scripts/run_x172_blackbox_h2_strength_response_validation_gpu.py`
- PIA/DDPM helpers:
  - `src/diffaudit/attacks/pia_adapter.py`
  - `external/PIA/DDPM/components.py`
- SD-style structural reconstruction smoke:
  - `scripts/run_structural_memorization_smoke.py`

## Candidate Acquisition Paths

| Path | Contract fit | GPU release now? | Decision |
| --- | --- | --- | --- |
| DDPM/CIFAR10 simple reconstruction-distance comparator from X176 cache | Same packet and same labels; already available as simple baselines inside X176 | no | Use as internal sanity comparator only; already evaluated and clearly weaker than H2. |
| New DDPM/CIFAR10 reconstruction-distance baseline beyond X176 simple baselines | Same asset family, but not admitted `recon`; risks becoming H2 feature engineering under another name | no | Hold unless a genuinely different score contract is frozen first. |
| Stable Diffusion/CelebA H2 response-surface adapter | Closer to admitted `recon` asset family, but not same packet and requires a new adapter, split contract, and expensive SD generation path | no | Future-surface only; not an immediate GPU task. |
| Direct admitted `recon` rerun | Admitted black-box line, but not compatible with X176 DDPM/CIFAR10 identity packet | no | Already blocked by X178. |
| Cross-protocol summary comparison | Cheap, but invalid for admission | no | Reject. |

## Existing Compatible Sanity Comparator

The only currently available same-packet comparator is the simple reconstruction-distance family already computed in X176:

| X176 score family | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| raw H2 logistic | `0.913940` | `0.851562` | `0.171875` | `0.062500` | primary candidate |
| lowpass H2 logistic | `0.898392` | `0.816406` | `0.140625` | `0.050781` | mandatory secondary |
| raw best simple low-FPR, `single_timestep_120` | `0.754715` | `0.687500` | `0.039062` | `0.000000` | compatible but weak sanity comparator |
| raw `mean_min_distance` | `0.739090` | `0.667969` | `0.015625` | `0.000000` | compatible but weak sanity comparator |
| raw `negative_slope` | `0.839172` | `0.769531` | `0.027344` | `0.003906` | better AUC, weak low-FPR |
| lowpass best simple low-FPR, `single_timestep_120` | `0.769394` | `0.697266` | `0.042969` | `0.000000` | compatible but weak sanity comparator |

This strengthens the claim that H2 is not merely a single-timestep reconstruction-distance artifact. It still does not create admitted black-box evidence because the comparator is not the admitted `recon` method and does not resolve the Stable Diffusion/CelebA versus DDPM/CIFAR10 protocol mismatch.

## Verdict

`positive contract review / no GPU release`

No GPU task is honest to release immediately:

- H2 already dominates the only currently compatible same-packet simple reconstruction-distance baselines.
- A new DDPM/CIFAR10 comparator would be a new candidate method, not admitted `recon`.
- A Stable Diffusion H2 adapter would be a new cross-surface acquisition project and needs CPU preflight before any GPU budget.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X180 nongraybox reselection after H2 comparator block`
- `current_execution_lane = X180 nongraybox reselection after H2 comparator block`
- `cpu_sidecar = I-A / cross-box boundary maintenance`
- `H2 status = strong validated candidate-only`
- no Platform / Runtime / materials handoff

## Next Lane

`X-180` should not be another H2 expansion by default. It should do a fresh nongraybox reselection after the H2 comparator block and decide among:

1. a CPU-first `I-A / cross-box` boundary maintenance pass if overclaim risk is now the main issue,
2. a new black-box surface-acquisition hypothesis only if it is not another H2 feature-engineering variant,
3. a genuinely new `I-B / I-C / I-D` successor hypothesis if one has a bounded contract and low-FPR gate,
4. continued GPU hold if no candidate has a fresh hypothesis, host-fit budget, and kill gate.
