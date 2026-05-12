# I-B Defense-Aware Reopen Scout

Date: 2026-05-12

## Verdict

`hold`; no GPU task is released.

The scout asked whether I-B risk-targeted unlearning has moved from a
necessary-condition checklist to an executable defense-aware reopen contract.
It has not. The current evidence still supports only an attack-side
threshold-transfer diagnostic, not a defended-shadow or adaptive-attacker
review.

## Anchor Run

The strongest existing anchor remains:

```text
workspaces/defense/runs/risk-targeted-unlearning-review-fullsplit-k32-20260418-r1/summary.json
```

Snapshot:

| Field | Value |
| --- | ---: |
| Delta AUC | `-0.021347` |
| Delta TPR@1%FPR | `-0.007000` |
| Delta TPR@0.1%FPR | `-0.003000` |
| Sample scope | full-split target review |

This is the best observed attack-metric reduction in the current reviewed
set, but its own notes state that it reuses an undefended shadow export for
threshold-transfer diagnostics and is not defense-aware.

## Contract Check

| Requirement | Current state | Release read |
| --- | --- | --- |
| Same member/nonmember identity | Required by the existing contract; present in review subsets but not sufficient alone. | Not a blocker by itself. |
| Defended-shadow training protocol | Required, but no defended-shadow training run exists. | Blocks GPU. |
| Adaptive attacker protocol | Required, but no adaptive attacker is specified or executed. | Blocks GPU. |
| Retained utility or collateral-damage metric | Required, but not part of the current evidence. | Blocks defense claim. |
| Low-FPR primary gate | Required; current strict-tail deltas are small or absent. | Blocks promotion. |
| Stop condition for no strict-tail improvement | Required as a rule, but no executable defended-shadow packet is frozen. | Blocks execution. |

## Falsifier Triggered

The CPU scout triggers the hold falsifier:

```text
If I-B has only attack-side threshold-transfer deltas and cannot identify an
executable defended-shadow/adaptive-attacker entrypoint with retained utility
and low-FPR as primary gates, keep the lane on hold.
```

Current code has execution surfaces for risk-targeted prep, one bounded
unlearning pilot, retained companion subset export, and baseline-vs-defended
target review. The review path still borrows undefended shadow exports; it
does not train defended shadows or adapt the attacker to the defended model.

## Next Reopen Condition

Do not run another I-B packet until a CPU-first protocol document freezes all
of the following in one executable contract:

- defended-shadow training entrypoint and budget,
- adaptive attacker scoring or thresholding rule,
- same member/nonmember identity and target checkpoint identity,
- retained utility or collateral-damage metric,
- low-FPR primary gate with finite-tail denominators,
- stop condition that closes the run if strict-tail improvement is absent.

Until then, I-B remains a bounded falsifier/support-only lane and must not be
used as admitted defense evidence.

## GPU State

`active_gpu_question = none`; `next_gpu_candidate = none`.

