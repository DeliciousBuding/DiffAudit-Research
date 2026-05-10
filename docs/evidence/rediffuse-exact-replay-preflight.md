# ReDiffuse Exact Replay Preflight

> Date: 2026-05-10
> Status: CPU preflight passed; no GPU release

## Question

Can Research express the collaborator ReDiffuse ResNet checkpoint-selection
contract without treating the older `resnet` mode as exact replay?

## Implementation

Added scoring mode:

```text
resnet_collaborator_replay
```

This mode keeps the existing ReDiffuse residual-feature flow, but switches the
second-stage ResNet checkpoint policy to the collaborator counter contract:
`test_acc_best` starts at zero and is not updated, so every epoch with
`test_acc > 0` can overwrite the stored checkpoint.

The output scores remain raw logits under Research metrics because raw logits
with higher-is-member ranking are metric-equivalent to the collaborator flow
that negates logits and then uses member-lower ROC. This preserves comparable
Research metric helpers without hiding the collaborator orientation convention.

## CPU Validation

Unit characterization:

```powershell
python -m unittest tests.test_rediffuse_adapter
```

Real-asset tiny smoke:

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-smoke `
  --workspace workspaces/gray-box/runs/rediffuse-exact-replay-preflight-20260510-cpu-4 `
  --device cpu `
  --max-samples 4 `
  --batch-size 2 `
  --attack-num 1 `
  --interval 1 `
  --average 1 `
  --k 1 `
  --scoring-mode resnet_collaborator_replay `
  --scorer-train-portion 0.5 `
  --scorer-epochs 1 `
  --scorer-batch-size 2
```

Tiny smoke result:

| Field | Value |
| --- | --- |
| Status | `ready` |
| Checkpoint step | `750000` |
| Split hash | matched |
| Scoring mode | `resnet_collaborator_replay` |
| Checkpoint policy | `collaborator_counter` |
| Samples per split | `2` |
| AUC | `0.5` |
| ASR | `0.75` |
| TPR@1%FPR | `0.5` |
| TPR@0.1%FPR | `0.5` |

The tiny metrics are a runtime sanity check only. They are not admitted evidence
and should not be compared with the 64/64 candidate packets.

## Verdict

`CPU preflight passed`.

Research can now express the collaborator checkpoint-selection contract as a
separate scoring mode. This removes the implementation blocker found by the
ResNet contract scout, but it does not release GPU by itself. The next GPU gate
would need a bounded exact-replay packet contract with fixed sample count,
epochs, scorer seed handling, and low-FPR reporting.

## Next Action

Either run one bounded 750k exact-replay GPU packet under the new mode, or close
ReDiffuse if the collaborator counter contract is judged too bug-compatible to
be scientifically useful.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
