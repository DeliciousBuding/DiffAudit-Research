# CLiD Tiny Score Bridge

This note records the first local CLiD score bridge on the prepared
member/nonmember prompt-conditioned split. It is a GPU smoke-scale result, not
admitted benchmark evidence.

## Verdict

```text
tiny bridge produced a reusable score schema but is not promotable
```

Why:

- The local bridge successfully generated member and nonmember score outputs.
- The score-summary schema validator passed.
- The strict-tail metric was nonzero on this tiny split.
- Promotion is blocked because the split has only 8 member and 8 nonmember rows,
  below the configured minimum of 100 per split.

## Run

| Field | Value |
| --- | --- |
| Run | `clid-local-bridge-preflight-20260501-r1` |
| Mode | `local-bridge-pair-summary` |
| Member rows | 8 |
| Nonmember rows | 8 |
| Best alpha | 0.3 |
| AUC | 1.0 |
| ASR | 1.0 |
| TPR@1%FPR | 1.0 |
| TPR@0.1%FPR | 1.0 |
| Schema status | `ready` |
| Promotion status | `not_eligible` |
| Promotion blocker | `minimum_sample_gate` |

## Boundary

- This does not change admitted evidence.
- This does not change Platform or Runtime schemas.
- This does not establish CLiD as better than `recon`.
- This only justifies the next bounded packet: collect at least 100 member and
  100 nonmember rows under the same score-summary gate.

Run payloads, generated images, raw scores, and schema-review JSON stay ignored
under `workspaces/black-box/runs/`.
