# I-B Risk-Targeted Unlearning Successor Scope

> Date: 2026-05-10
> Status: hold; no GPU release

## Question

Can the existing risk-targeted unlearning packets reopen I-B as a bounded
successor lane after recent ReDiffuse, tri-score, and response-contract
closures?

## Method

Review the existing full-split paired-noise attack-side summaries under
`workspaces/defense/runs/` without launching a new training or attack run.

The reviewed summaries compare baseline vs defended checkpoints using frozen
shadow-derived threshold transfer. They do not retrain defended shadows, and
each summary carries the same caveat:

> attack-side readable, but not defense-aware; provisional until defended
> shadows are retrained.

Provenance note: `workspaces/**/runs/**` is ignored by Git. The snapshot below
comes from local generated `summary.json` files, not from portable checked-in
artifacts. A fresh checkout should treat this document as the reviewed evidence
anchor. To regenerate the same class of deltas, rerun the risk-targeted
unlearning review pipeline and compare each run's
`baseline.threshold_eval.target_transfer.metrics` against
`defended.threshold_eval.target_transfer.metrics`.

## Evidence Snapshot

| Run | Delta AUC | Delta TPR@1%FPR | Delta TPR@0.1%FPR |
| --- | ---: | ---: | ---: |
| `risk-targeted-unlearning-review-fullsplit-k16-pairednoise-20260418-r1` | `-0.001190` | `-0.001000` | `0.000000` |
| `risk-targeted-unlearning-review-fullsplit-k32-pairednoise-20260418-r1` | `-0.005635` | `-0.001000` | `0.000000` |
| `risk-targeted-unlearning-review-fullsplit-k8-pairednoise-20260418-r1` | `-0.002326` | `-0.002000` | `0.000000` |
| `risk-targeted-unlearning-review-fullsplit-k16-alpha075-pairednoise-20260418-r1` | `-0.000400` | `-0.003000` | `0.000000` |
| `risk-targeted-unlearning-review-fullsplit-k16-lambda04375-pairednoise-20260418-r1` | `+0.000893` | `-0.006000` | `0.000000` |
| `risk-targeted-unlearning-review-fullsplit-k32-20260418-r1` | `-0.021347` | `-0.007000` | `-0.003000` |

## Interpretation

There is a weak attack-metric reduction trend in several full-split reviews,
but it is not enough to release a model task:

- The largest AUC reduction is `-0.021347`, but it comes from a diagnostic
  threshold-transfer setup.
- TPR@1%FPR reductions are small and not paired with a defended-shadow
  attacker.
- TPR@0.1%FPR is flat in most variants, so there is no strict-tail defense
  claim.
- The current evidence does not answer the adaptive attacker question.

## Verdict

`hold`.

I-B should not reopen as a GPU lane from the existing packets. The next
scientifically valid successor is a CPU preflight for a defended-shadow or
adaptive-attacker review contract.

The hold boundary is now machine-guarded by
[`ib-adaptive-defense-contract-20260511.md`](ib-adaptive-defense-contract-20260511.md)
and `scripts/validate_ib_adaptive_defense_contract.py`.

## Reopen Gate

Before any GPU run, freeze:

- defended-shadow training or attacker adaptation protocol,
- same member/nonmember identity contract,
- low-FPR primary gate,
- retained-utility or collateral-damage metric,
- stop condition for no strict-tail improvement.

If those cannot be specified, keep I-B as bounded falsifier/support-only.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. This is not product-facing
defense evidence.
