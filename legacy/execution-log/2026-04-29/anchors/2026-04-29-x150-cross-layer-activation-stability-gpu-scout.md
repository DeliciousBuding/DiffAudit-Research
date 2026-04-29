# X-150: Cross-Layer Activation-Stability GPU Scout

## Question

After `X-148` showed that single-layer validation-regularized activation-subspace selection is still weak, can a stricter same-attention-block cross-projection stability gate produce a more reliable held-out white-box second-family signal?

## Contract

- script: `legacy/execution-log/2026-04-29/scripts/run_x150_cross_layer_activation_stability_gpu_scout.py`
- run anchor: `workspaces/white-box/runs/x150-cross-layer-activation-stability-scout-20260429-r1/summary.json`
- device: `cuda:0`
- assets: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1`
- checkpoint: `checkpoints/target/checkpoint-9600`
- primary layer: `mid_block.attentions.0.to_v`
- comparator layers:
  - `mid_block.attentions.0.to_q`
  - `mid_block.attentions.0.to_k`
- timesteps: `[250, 500, 750, 999]`
- packet: `16 member / 16 nonmember`
- split per role: `8 selector / 4 validation / 4 holdout`
- selector:
  - select candidates from primary `to_v` selector-split delta
  - require same-sign primary `to_v` validation delta
  - require same-sign support from at least one comparator projection on validation split
  - rank survivors by the minimum of primary selector delta, primary validation delta, and strongest comparator validation delta
  - score holdout without using holdout for selection
- admitted change: none

## Result

Canonical run anchor:

- `workspaces/white-box/runs/x150-cross-layer-activation-stability-scout-20260429-r1/summary.json`

Selection diagnostics:

- candidate channels: `64`
- primary-validation-stable channels: `12`
- cross-layer-stable channels: `8`
- selected channels: `8`

Holdout metrics:

- primary `to_v` holdout verdict:
  - `AUC = 0.5625`
  - `ASR = 0.5625`
  - `TPR@1%FPR = 0.0`
  - `TPR@0.1%FPR = 0.0`
- primary-validation-stable baseline holdout:
  - `AUC = 0.625`
  - `ASR = 0.625`
  - `TPR@1%FPR = 0.25`
  - `TPR@0.1%FPR = 0.25`
- cross-projection mean diagnostic:
  - `AUC = 0.5`
  - `ASR = 0.5`
  - `TPR@1%FPR = 0.0`
  - `TPR@0.1%FPR = 0.0`
- comparator diagnostics:
  - `to_q` holdout `AUC = 0.375`
  - `to_k` holdout `AUC = 0.6875`

## Interpretation

The cross-layer gate is real and executable, but it does not improve the held-out verdict surface. It reduces the candidate set from `12` primary-validation-stable channels to `8` cross-layer-stable channels, yet the primary holdout drops from the same-split baseline `AUC = 0.625` to `AUC = 0.5625`, and the cross-projection mean diagnostic is random.

The useful part is the mechanism filter outcome:

1. same-block `to_q/to_k/to_v` stability is not enough to rescue the activation-subspace family;
2. `to_k` contains a small positive diagnostic read, but it is not a verdict because it was not the predeclared primary surface and the packet is only `4 / 4` holdout;
3. further same-family activation work now needs a genuinely different observable, such as per-timestep trajectory shape or independent-noise stability, not another mean-profile channel selector.

## Verdict

`negative but useful`

`03-H1 activation-subspace` remains a medium-horizon white-box distinct-family gap, but the current mean-profile channel-selector route should not receive another immediate GPU release.

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X-151 non-graybox reselection`
- `current_cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- next live lane: `X-151 non-graybox next-lane reselection after X-150`
- Platform / Runtime handoff: none
- Materials handoff: none
