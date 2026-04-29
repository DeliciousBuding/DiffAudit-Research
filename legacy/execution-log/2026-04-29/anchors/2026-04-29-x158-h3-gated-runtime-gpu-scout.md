# X-158: H3 Gated Runtime GPU Scout

## Question

Does the X-157 cached selective all-steps route preserve low-FPR defended behavior on one fresh GPU packet?

## Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x158_h3_gated_runtime_gpu_scout.py`

Environment:

- default `python` was CPU-only (`torch 2.11.0+cpu`, `torch.cuda.is_available() = false`)
- real GPU run used `conda run -n diffaudit-research`
- device: `cuda:0`

Command:

```powershell
conda run -n diffaudit-research python -X utf8 legacy/execution-log/2026-04-29/scripts/run_x158_h3_gated_runtime_gpu_scout.py --run-root workspaces\gray-box\runs\x158-h3-gated-runtime-gpu-scout-20260429-r1 --packet-size 64 --batch-size 2 --adaptive-query-repeats 3 --device cuda:0
```

Artifact:

- `workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-20260429-r1/summary.json`

## Result

Fresh `64 / 64` packet:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| baseline adaptive | `0.781250` | `0.773438` | `0.078125` | `0.078125` |
| all-steps dropout adaptive | `0.769775` | `0.765625` | `0.046875` | `0.046875` |
| selective gated adaptive | `0.778076` | `0.773438` | `0.046875` | `0.046875` |

Gate:

- requested gate fraction: `0.20`
- actual gate fraction: `0.203125`
- member gate fraction: `0.296875`
- nonmember gate fraction: `0.109375`

## Interpretation

The positive part is narrow: selective gating exactly matched full all-steps dropout on both low-FPR tail metrics for this fresh packet while routing only about one fifth of samples.

The negative part is also important: AUC and ASR are worse than full all-steps dropout and equal/near-equal to baseline on ASR. This is not a stronger privacy result. The branch is only a bounded candidate for reducing perturbation exposure while retaining tail suppression.

## Verdict

`positive but bounded`

H3 remains candidate-only. No admitted table, Platform schema, Runtime endpoint, or public claim should change.

## Control State After X-158

- `active_gpu_question = none`
- `next_gpu_candidate = none until X-159 review freezes a stronger implementation reason`
- `next live lane = X-159 04-H3 post-GPU review / implementation-hardening decision`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no endpoint change; only consider a candidate runner after X-159.
- `Docs/materials`: do not advertise H3 as a validated defense; at most internal candidate evidence.
