# X-154: Per-Timestep Activation-Trajectory GPU Scout

## Question

Does a per-timestep activation-trajectory observable rescue the exhausted `03-H1 activation-subspace` route better than the averaged mean-profile baseline?

## Contract

This packet executed the `X-153` frozen contract:

- assets: admitted `GSA / DDPM / CIFAR10`
- checkpoint: `checkpoint-9600`
- layer: `mid_block.attentions.0.to_v`
- timesteps: `[250, 500, 750, 999]`
- packet: `16 member / 16 nonmember`
- split: `8 selector / 4 validation / 4 holdout`
- features: `mean_profile`, `late_minus_early`, `linear_slope`, `early_late_gap`, `trajectory_energy`
- selection: feature family and channels selected only from selector plus validation splits
- holdout: verdict-only

## Run Anchor

- run summary: `workspaces/white-box/runs/x154-per-timestep-activation-trajectory-scout-20260429-r1/summary.json`
- local artifacts:
  - `records.jsonl`
  - `per-timestep-activation-trajectories.pt`

## Result

Validation selected `late_minus_early`:

- selector: `AUC = 1.0 / ASR = 1.0 / TPR@1%FPR = 1.0 / TPR@0.1%FPR = 1.0`
- validation: `AUC = 0.8125 / ASR = 0.8125 / TPR@1%FPR = 0.25 / TPR@0.1%FPR = 0.25`
- holdout verdict: `AUC = 0.375 / ASR = 0.625 / TPR@1%FPR = 0.0 / TPR@0.1%FPR = 0.0`

Mean-profile validation-stable baseline holdout:

- `AUC = 0.375 / ASR = 0.625 / TPR@1%FPR = 0.0 / TPR@0.1%FPR = 0.0`

Diagnostic only:

- `trajectory_energy` holdout reached `AUC = 0.5 / TPR@1%FPR = 0.25`, but it was not selected by the validation policy and therefore cannot be promoted post-hoc.

## Verdict

`negative but useful`

The per-timestep feature contract was executable and materially different from averaging, but it did not clear the predeclared fire gate:

- selected feature was not better than the mean-profile baseline on holdout `AUC`
- selected feature had `TPR@1%FPR = 0.0`
- the only nonzero holdout low-FPR diagnostic would require post-hoc feature promotion

## Control State After X-154

- `active_gpu_question = none`
- `next_gpu_candidate = none until post-trajectory reselection`
- `current_execution_lane = X-155 post-trajectory non-graybox reselection`
- `cpu_sidecar = I-A boundary maintenance plus 04-defense successor-hypothesis watch`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no runner or endpoint change.
- `Docs/materials`: do not add this as a public result; if mentioned internally, call it an activation-trajectory falsifier.
