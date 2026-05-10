# GSA Loss-Score Shadow Stability Review

> Date: 2026-05-10
> Status: negative-but-useful; no GPU release

## Question

Can the existing GSA loss-score Gaussian likelihood-ratio scorer be treated as
a stable distinct white-box scorer, rather than a same-packet pooled-shadow
artifact?

## Hypothesis

Gaussian likelihood-ratio transfer should beat threshold transfer in at least
`2/3` leave-one-shadow-out folds on both held-out shadow transfer and target
transfer, while preserving `TPR@1%FPR` and `TPR@0.1%FPR`.

## CPU Review

Command:

```powershell
python -X utf8 scripts/review_gsa_loss_score_shadow_stability.py `
  --packet-summary workspaces/white-box/runs/gsa-loss-score-export-bounded-bm0-gpu-20260417-r1/summary.json
```

Output:

```text
workspaces/white-box/runs/gsa-loss-score-shadow-stability-20260510-cpu/summary.json
```

The review uses the existing frozen loss-score export:

```text
workspaces/white-box/runs/gsa-loss-score-export-bounded-bm0-gpu-20260417-r1/summary.json
```

That export is a local generated run artifact, not a Git-tracked public file.
The evidence below records the canonical review result; rerunning the command
requires the local export packet to be present.

No GPU task was released.

## Result

| Board | Threshold AUC | LR AUC | Threshold TPR@1%FPR | LR TPR@1%FPR | Threshold TPR@0.1%FPR | LR TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Held-out shadow macro | 0.582682 | 0.574056 | 0.015625 | 0.026042 | 0.015625 | 0.026042 |
| Target-transfer macro | 0.671143 | 0.564697 | 0.015625 | 0.010417 | 0.015625 | 0.010417 |

Release gate:

| Gate | Value |
| --- | ---: |
| Held-out LR beats threshold folds | 1 / 3 |
| Target LR beats threshold folds | 0 / 3 |
| Required folds | 2 / 3 |
| Fold rule | LR AUC must beat threshold and preserve TPR@1%FPR plus TPR@0.1%FPR |
| Passed | false |

## Verdict

`negative-but-useful`.

The LR scorer does not generalize well enough across leave-one-shadow-out folds
to reopen white-box GPU work. It improves the held-out-shadow low-FPR macro in
aggregate, but loses AUC there and fails all target-transfer fold comparisons.
This falsifies the immediate "distinct scorer" rescue path for existing
loss-score exports.

## Boundary

Allowed:

- Use this as CPU evidence that the existing GSA loss-score LR scorer is not a
  stable successor by itself.
- Keep historical LR packet summaries as diagnostic evidence.

Not allowed:

- Do not promote Gaussian LR transfer as an admitted white-box method.
- Do not schedule a larger GPU loss-score packet from this result alone.
- Do not treat target self-diagnostics from older LR summaries as verdicts.

## Next Action

White-box remains on hold until a genuinely different observable appears. The
highest-value next discovery target remains a second black-box response-contract
asset/protocol, because it can test portability without replaying a closed
white-box observable.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
