# X-145 / X-146: Activation-Subspace GPU Scout

## Question

Can the `03-H1 activation-subspace` gap be turned into a small GPU-safe scout on admitted `GSA / DDPM / CIFAR10` assets, and does the first selected activation subspace survive a held-out read?

## Contract

- script: `legacy/execution-log/2026-04-29/scripts/run_x145_activation_subspace_gpu_scout.py`
- device: `cuda:0`
- assets: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1`
- checkpoint: `checkpoints/target/checkpoint-9600`
- layer selector: `mid_block.attentions.0.to_v`
- timesteps: `[250, 500, 750, 999]`
- profile: mean channel profile across timesteps
- subspace: top-`16` absolute member-vs-nonmember activation-profile deltas
- scoring rule: select top channels on the first half of the packet, evaluate signed projection on the held-out half
- admitted change: none

This is intentionally separate from the older CPU-only Finding NeMo canary. It is a GPU-safe preflight scout only.

## X-145 Result: 8 / 8 Packet

Canonical run anchor:

- `workspaces/white-box/runs/x145-activation-subspace-gpu-scout-20260429-r1/summary.json`

Held-out metrics on `4 / 4`:

- `AUC = 0.625`
- `ASR = 0.625`
- `TPR@1%FPR = 0.0`
- `TPR@0.1%FPR = 0.0`

Training-half metrics were perfect (`AUC = 1.0`), so the honest read is execution-positive but not evidence-positive.

## X-146 Result: 16 / 16 Packet

Canonical run anchor:

- `workspaces/white-box/runs/x146-activation-subspace-gpu-scout-16x16-20260429-r1/summary.json`

Held-out metrics on `8 / 8`:

- `AUC = 0.3125`
- `ASR = 0.6875`
- `TPR@1%FPR = 0.0`
- `TPR@0.1%FPR = 0.0`

Training-half metrics again stayed perfect (`AUC = 1.0`), while held-out performance inverted. This is a clear overfit signal for the current top-k activation-subspace selection rule.

## Verdict

`negative but useful`

The GPU-safe activation-subspace scout is now real and reusable, but the current `mid_block.attentions.0.to_v` top-delta selection rule does not survive held-out evaluation. It should not be promoted as a white-box second family, and it should not receive another same-rule GPU expansion without a genuinely new selector, regularization, or validation hypothesis.

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `current_cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance plus fresh non-graybox candidate expansion`
- Platform / Runtime handoff: none
- Materials handoff: none
