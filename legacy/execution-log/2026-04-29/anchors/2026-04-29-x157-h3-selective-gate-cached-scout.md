# X-157: H3 Selective-Gate Cached Scout

## Question

Before implementing a gated runtime, does a cached score-level mix of existing `PIA` baseline and dropout surfaces suggest that selective routing can preserve low-FPR defended behavior while perturbing fewer samples?

## Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x157_h3_selective_gate_cached_scout.py`

Cached inputs:

- baseline: `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive`
- all-steps dropout: `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive`
- late-steps dropout: `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-latesteps-adaptive`

Artifacts:

- `workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-20260429-r1/summary.json`
- `workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-20260429-r2-allsteps-primary/summary.json`

## Findings

### Late-step selective route

The `late_steps_only` primary route did not clear the release gate. It lowered `TPR@1%FPR` against baseline, but failed to match all-steps dropout at the strict adaptive tail because `TPR@0.1%FPR` stayed at `0.011719` versus all-steps `0.009766`.

### All-steps selective route

The `all_steps` primary route cleared the cache-level release gate:

- selected route: gate fraction about `20%`
- adaptive selective metrics: `AUC = 0.839802 / ASR = 0.786133 / TPR@1%FPR = 0.052734 / TPR@0.1%FPR = 0.009766`
- adaptive all-steps comparator: `AUC = 0.828075 / ASR = 0.767578 / TPR@1%FPR = 0.052734 / TPR@0.1%FPR = 0.009766`

Interpretation:

- low-FPR tail can be matched while routing only the risk tail
- AUC/ASR remain worse than full all-steps dropout
- the value proposition is quality/cost/selectivity, not stronger privacy

## Verdict

`positive GPU-candidate release / no admitted change`

The result authorizes exactly one small X-158 gated runtime GPU scout. It does not promote H3 and does not authorize a larger sweep.

## Control State After X-157

- `active_gpu_question = one bounded X-158 H3 gated runtime GPU scout`
- `next_gpu_candidate = none beyond X-158`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change unless X-158 also passes and a deployable runner contract is frozen.
- `Docs/materials`: no public claim change.
