# X-148: Activation-Subspace Validation-Regularized GPU Scout

## Question

Can the `03-H1 activation-subspace` line avoid the `X-145 / X-146` overfit by requiring a candidate channel to survive an independent validation split before holdout scoring?

## Contract

- script: `legacy/execution-log/2026-04-29/scripts/run_x148_activation_subspace_regularized_gpu_scout.py`
- run anchor: `workspaces/white-box/runs/x148-activation-subspace-regularized-scout-20260429-r1/summary.json`
- device: `cuda:0`
- assets: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1`
- checkpoint: `checkpoints/target/checkpoint-9600`
- layer selector: `mid_block.attentions.0.to_v`
- timesteps: `[250, 500, 750, 999]`
- packet: `16 member / 16 nonmember`
- split per role: `8 selector / 4 validation / 4 holdout`
- selection rule:
  - take top selector-delta candidates
  - keep only channels whose validation mean delta has the same sign
  - rank survivors by the smaller of selector and validation absolute deltas
  - report verdict on holdout only
- admitted change: none

## Result

Canonical run anchor:

- `workspaces/white-box/runs/x148-activation-subspace-regularized-scout-20260429-r1/summary.json`

Holdout metrics on `4 / 4`:

- `AUC = 0.625`
- `ASR = 0.625`
- `TPR@1%FPR = 0.25`
- `TPR@0.1%FPR = 0.25`

Diagnostics:

- selector split remains perfect: `AUC = 1.0`
- validation split is weak: `AUC = 0.625`
- same-split baseline top-delta holdout is worse: `AUC = 0.4375`
- pooled metrics are stronger (`AUC = 0.8125`) but are diagnostic only and not the verdict surface
- selected validation-stable channels: `12 / 64` candidates survived sign consistency

## Verdict

`negative but useful`

The validation-stable selector fixes the most obvious failure mode from `X-146`: it no longer inverts on held-out samples, and it beats the same-split top-delta baseline on the tiny holdout. That is not enough for promotion or for another same-contract GPU expansion. The holdout is still only `AUC = 0.625`, the validation read is also weak, and the apparent low-FPR values are too coarse at `4 / 4` scale.

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `current_cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- next `03-H1` work must be CPU-first selector/mechanism review, not GPU scaling:
  - cross-layer stability hypothesis
  - independent seed validation
  - stricter held-out packet design
  - or a different activation observable
- Platform / Runtime handoff: none
- Materials handoff: none
