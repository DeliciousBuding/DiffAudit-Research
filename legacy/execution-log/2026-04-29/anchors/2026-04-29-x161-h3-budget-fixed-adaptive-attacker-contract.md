# X-161: H3 Budget-Fixed Adaptive-Attacker Contract Freeze

## Question

Can H3 selective all-steps gating be tested under a stricter fixed-query-budget attacker without leaking same-packet labels or relying on a post-hoc same-packet quantile threshold?

## Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x161_h3_budget_fixed_contract.py`

Command:

```powershell
python -X utf8 legacy/execution-log/2026-04-29/scripts/run_x161_h3_budget_fixed_contract.py
```

Artifact:

- `workspaces/gray-box/runs/x161-h3-budget-fixed-contract-20260429-r1/summary.json`

## Frozen Contract

- `packet_size = 64 / 64`
- `fixed_total_query_budget = 3`
- `gate_probe_queries = 1`
- `route_score_queries = 2`
- gate threshold is frozen from X157 cached all-steps primary adaptive threshold: `-7.82414`
- no same-packet top-quantile threshold
- no membership labels in the gate
- no `128 / 128` expansion
- X162 must report both:
  - fixed-budget defended-policy attacker
  - oracle-route escape falsifier

## Preflight Evidence

Using X158 cached fresh scores with the X157 fixed threshold:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| baseline | `0.781250` | `0.773438` | `0.078125` | `0.078125` |
| all-steps | `0.769775` | `0.765625` | `0.046875` | `0.046875` |
| fixed-threshold selective | `0.778076` | `0.773438` | `0.046875` | `0.046875` |
| oracle-route escape | `0.781250` | `0.773438` | `0.078125` | `0.078125` |

Gate:

- gate fraction: `0.21875`
- member gate fraction: `0.296875`
- nonmember gate fraction: `0.140625`
- max allowed fraction: `0.22`

## Interpretation

The fixed threshold removes the most obvious same-packet quantile leakage from X158 while preserving the low-FPR tail match on cached scores. That is enough to release one stricter GPU scout.

The oracle-route escape is equally important: if an attacker has oracle access to recover the undefended route for routed samples, the low-FPR tail returns to baseline. Therefore X162 cannot promote H3 into a validated defense even if the fixed-budget defended-policy attacker passes.

## Verdict

`positive contract freeze / one bounded GPU scout released`

## Control State After X-161

- `active_gpu_question = one bounded X162 H3 budget-fixed adaptive-attacker scout`
- `next_gpu_candidate = none beyond X162`
- `next live lane = X162 H3 budget-fixed adaptive-attacker GPU scout`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change.
- `Docs/materials`: no public claim change; H3 remains candidate-only.
