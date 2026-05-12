# I-B Defense Reopen Protocol Audit

Date: 2026-05-12

## Verdict

`hold-structural`; no GPU task is released.

The audit asked whether the current risk-targeted unlearning implementation can
serve as an executable defended-shadow or adaptive-attacker reopen protocol for
I-B. It cannot. The code path is useful for attack-side threshold-transfer
diagnostics, but it still borrows an undefended shadow reference and does not
define defended-shadow training, adaptive attacker behavior, retained utility,
or an executable low-FPR gate.

## Inspected Surfaces

| Surface | Current role | Protocol read |
| --- | --- | --- |
| `prepare-risk-targeted-unlearning-pilot` | Builds bounded forget/control lists from existing score surfaces. | Prep-only; does not define defense-aware review. |
| `run-risk-targeted-unlearning-pilot` | Runs one retain/forget pilot on target assets. | Produces a defended checkpoint candidate, not defended shadows. |
| `review-risk-targeted-unlearning-pilot` | Compares baseline vs defended target subsets through GSA loss-score threshold transfer. | Explicitly borrows an undefended shadow reference. |
| `scripts/validate_ib_adaptive_defense_contract.py` | Guards the current I-B hold contract. | Correctly blocks admission and GPU release. |
| `workspaces/defense/README.md` | Active workspace status. | Current workspace has no separate `plan.md`; README is the active defense status surface. |

## Code-Level Falsifier

The review function requires `shadow_reference_summary`. The CLI describes it
as a ready undefended GSA loss-score-export summary used only for borrowed
shadow threshold transfer. The packet writer also records that shadow exports
are borrowed from an existing undefended packet and that the packet is
target-subset-only, not defense-aware.

That is the decisive blocker. A defended-shadow/adaptive protocol cannot be
claimed when the thresholding reference remains undefended.

## Current Best Anchor

The strongest reviewed I-B anchor remains:

```text
workspaces/defense/runs/risk-targeted-unlearning-review-fullsplit-k32-20260418-r1/summary.json
```

| Field | Value |
| --- | ---: |
| Delta AUC | `-0.021347` |
| Delta TPR@1%FPR | `-0.007000` |
| Delta TPR@0.1%FPR | `-0.003000` |

These reductions are not enough for a defense claim because they are measured
through attack-side threshold transfer, not through defended shadows or an
adaptive attacker.

## Required Reopen Protocol

The next valid I-B task is not another GPU packet. It is a CPU-first protocol
freeze that defines all of the following before execution:

- defended-shadow training entrypoint and budget,
- adaptive attacker scoring or thresholding rule,
- same member/nonmember identity and target checkpoint identity,
- retained utility or collateral-damage metric,
- low-FPR primary gate with finite-tail denominators,
- stop condition that closes the line when strict-tail improvement is absent.

## Product Boundary

No Platform or Runtime handoff is needed. I-B remains internal Research hold
evidence and must not be listed as admitted defense evidence, adaptive
robustness evidence, or a product-facing defense row.

## GPU State

`active_gpu_question = none`; `next_gpu_candidate = none`.
