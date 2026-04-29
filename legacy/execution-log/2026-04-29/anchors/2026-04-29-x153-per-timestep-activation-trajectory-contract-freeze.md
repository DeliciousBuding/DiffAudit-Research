# X-153: Per-Timestep Activation-Trajectory Contract Freeze

## Question

After the mean-profile activation-subspace route failed across `X-145 / X-146 / X-148 / X-150`, is there one genuinely different activation observable that is honest enough to receive a bounded GPU scout?

## Decision

Freeze one bounded `per-timestep activation-trajectory` scout contract.

This is not another mean-profile channel selector. The observable keeps the timestep dimension until feature construction and tests whether the shape of a channel trajectory across timesteps separates members from nonmembers better than the averaged activation profile.

## Contract

- assets: admitted `GSA / DDPM / CIFAR10` surface
- checkpoint: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1/checkpoints/target/checkpoint-9600`
- layer: `mid_block.attentions.0.to_v`
- timesteps: `[250, 500, 750, 999]`
- packet: same bounded `16 member / 16 nonmember` target packet used by `X-150`
- split: `8 selector / 4 validation / 4 holdout`
- feature families:
  - `mean_profile`: timestep average baseline
  - `late_minus_early`: final minus first timestep channel profile
  - `linear_slope`: least-squares slope over normalized timestep index
  - `early_late_gap`: late-window mean minus early-window mean
  - `trajectory_energy`: mean absolute first difference over timesteps
- selection:
  - select feature family and channels using selector and validation splits only
  - require selector/validation sign consistency
  - rank by the minimum of selector and validation absolute deltas
  - use validation metrics only for choosing the feature family
  - holdout must remain blind until final verdict
- baselines:
  - same split `mean_profile` validation-stable baseline
  - report all candidate feature holdouts for diagnostics, but do not promote post-hoc winners selected by holdout

## Budget

- one GPU scout only
- no training
- no additional sample expansion
- no comparator layers
- single-sample activation capture loop
- stop after one summary packet

## Kill Gate

The scout is not promotable if any of these holds:

- selected trajectory feature holdout does not beat the `mean_profile` baseline on `AUC`
- selected trajectory feature has `TPR@1%FPR = 0.0`
- feature choice is only justified by holdout, not by validation
- result only supports same-family mean-profile salvage language

Because holdout is only `4 / 4`, any positive result is still preflight-only and must not be written as a white-box second-family promotion.

## Verdict

`positive / bounded GPU scout released`

This contract is materially different from the exhausted mean-profile route and has a strict no-leak selector/validation/holdout boundary. It is honest to run exactly one `X-154` GPU scout under this contract.

## Control State After X-153

- `active_gpu_question = X-154 per-timestep activation-trajectory GPU scout`
- `next_gpu_candidate = none until X-154 verdict`
- `cpu_sidecar = I-A boundary maintenance plus 04-defense successor-hypothesis watch`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no runner or endpoint change.
- `Docs/materials`: no wording change unless `X-154` produces a result strong enough to update candidate-boundary language.
