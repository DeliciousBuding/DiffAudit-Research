# X-162: H3 Budget-Fixed Adaptive-Attacker GPU Scout

## Question

Under the X161 fixed-query-budget contract, does H3 selective all-steps gating still match the full all-steps low-FPR tail on one fresh GPU packet?

## Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x162_h3_budget_fixed_gpu_scout.py`

Environment:

- `conda run -n diffaudit-research`
- device: `cuda:0`

Command:

```powershell
conda run -n diffaudit-research python -X utf8 legacy/execution-log/2026-04-29/scripts/run_x162_h3_budget_fixed_gpu_scout.py --run-root workspaces\gray-box\runs\x162-h3-budget-fixed-gpu-scout-20260429-r1 --packet-size 64 --batch-size 2 --device cuda:0
```

Artifacts:

- `workspaces/gray-box/runs/x162-h3-budget-fixed-gpu-scout-20260429-r1/summary.json`
- `workspaces/gray-box/runs/x162-h3-budget-fixed-gpu-scout-20260429-r1/scores.json`

## Result

Fresh `64 / 64` packet, fixed total query budget `3`:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| baseline budget | `0.781250` | `0.773438` | `0.078125` | `0.078125` |
| all-steps budget | `0.769531` | `0.765625` | `0.031250` | `0.031250` |
| fixed-budget selective | `0.778320` | `0.773438` | `0.031250` | `0.031250` |
| gate-leak falsifier | `0.779053` | `0.773438` | `0.046875` | `0.046875` |
| oracle-route escape | `0.781250` | `0.773438` | `0.078125` | `0.078125` |

Gate:

- threshold: `-7.82414`
- gate fraction: `0.21875`
- member gate fraction: `0.296875`
- nonmember gate fraction: `0.140625`

Runtime:

- wall clock: `562.750823s`

## Interpretation

The fixed-budget defended-policy result is positive: selective gating exactly matches full all-steps dropout at both low-FPR metrics while routing about `21.875%` of samples.

The bounded part is decisive:

- `AUC / ASR` remain privacy-weaker than full all-steps.
- If the internal gate score leaks into the attack score, low-FPR weakens from `0.031250 / 0.031250` to `0.046875 / 0.046875`.
- If an oracle route escape can recover the undefended route for routed samples, low-FPR fully returns to baseline `0.078125 / 0.078125`.

So this is not a validated privacy defense. It is a candidate audit-time selectivity / perturbation-exposure result under a non-oracle defended-policy attacker.

## Verdict

`positive but bounded`

No admitted table, Runtime endpoint, Platform view, or public claim should change.

## Control State After X-162

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `next live lane = X-163 H3 post-fixed-budget review / freeze-or-reselect decision`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change.
- `Docs/materials`: do not advertise H3 as validated privacy; at most internal candidate evidence.
