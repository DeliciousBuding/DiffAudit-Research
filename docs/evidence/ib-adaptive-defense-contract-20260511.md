# I-B Adaptive Defense Contract

This note freezes the next valid gate for the risk-targeted unlearning defense
line. It does not train defended shadows, rerun attacks, or release GPU work.

## Verdict

```text
I-B remains on hold until a defended-shadow or adaptive-attacker review
contract exists.
```

The stable machine-readable anchor is
[`workspaces/defense/artifacts/ib-adaptive-defense-contract-20260511.json`](../../workspaces/defense/artifacts/ib-adaptive-defense-contract-20260511.json).
`scripts/validate_ib_adaptive_defense_contract.py` validates that the current
evidence cannot silently become admitted defense evidence, claim adaptive
robustness, or release GPU work.

## Evidence Boundary

Existing full-split reviews show only small attack-side threshold-transfer
reductions:

| Best observed value | Delta |
| --- | ---: |
| AUC reduction | `-0.021347` |
| TPR@1%FPR reduction | `-0.007` |
| TPR@0.1%FPR reduction | `-0.003` |

These values are not enough for a defense claim because the attacker was not
defense-aware: defended shadows were not retrained and no adaptive attacker was
specified. The strict-tail improvement is absent or too small, and retained
utility is not part of the current evidence.

## Required Reopen Contract

Before any GPU task can be released, the next I-B attempt must define:

- Defended-shadow training protocol.
- Adaptive attacker protocol.
- Same member/nonmember identity contract.
- Low-FPR primary gate.
- Retained-utility or collateral-damage metric.
- Stop condition for no strict-tail improvement.

## Blocked Claim

- Admitted defense evidence.
- Adaptive robustness.
- Low-FPR defense improvement.
- Platform/Runtime defense row.

## Next Gate

No GPU task is selected. Reopen only with a CPU-first protocol document that
specifies the adaptive attacker and utility metric before training or review.
