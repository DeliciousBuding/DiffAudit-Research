# CLiD Image-Identity Boundary Contract

This note freezes the current CLiD boundary as a repository-level contract. It
does not run CLiD again and does not promote CLiD into admitted evidence.

## Verdict

```text
CLiD remains a prompt-conditioned diagnostic candidate, not admitted
image-identity black-box membership evidence.
```

The stable machine-readable anchor is
[`workspaces/black-box/artifacts/clid-image-identity-boundary-20260511.json`](../../workspaces/black-box/artifacts/clid-image-identity-boundary-20260511.json).
`scripts/validate_clid_identity_boundary.py` validates that the artifact cannot
silently become admitted evidence, release GPU work, or lose the prompt-control
promotion blockers.

## Evidence Summary

| Contract | AUC | TPR@1%FPR | TPR@0.1%FPR | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Prompt-conditioned repeat | 1.0 | 1.0 | 1.0 | Strong under the original prompt-image contract. |
| Fixed prompt | 0.5862 | 0.02 | 0.02 | Removing prompt variation collapses strict-tail signal. |
| Swapped prompt | 0.72885 | 0.21 | 0.21 | Residual signal exists but is much weaker. |
| Within-split shuffle seed 0 | 0.64105 | 0.12 | 0.12 | Split-level prompt distribution is not enough. |
| Within-split shuffle seed 1 | 0.59425 | 0.08 | 0.08 | Residual is weaker and seed-sensitive. |
| Prompt text only | 0.70715 | 0.02 | 0.02 | Text nuisance is real but does not explain original strict-tail signal. |

The strict-tail maximum across controls is `0.21`, versus `1.0` for the original
prompt-conditioned repeat. The best current explanation is not a stable
image-identity membership score; it is a prompt-conditioned auxiliary path.

## Allowed Claim

- CLiD is a useful black-box diagnostic for studying prompt contracts.
- The original CLiD packet is strong only under the tested prompt-image pairing.
- Prompt text alone is a nuisance factor but does not recover the original
  strict-tail signal.
- Any future CLiD packet must include matched prompt controls and low-FPR
  metrics.

## Blocked Claim

- CLiD is admitted black-box evidence.
- CLiD is an image-identity membership signal.
- CLiD replaces the admitted `recon` row.
- CLiD generalizes to conditional diffusion or commercial settings.

## Next Gate

No GPU task is selected. Reopen CLiD only with a new CPU-first protocol that can
separate image identity from prompt-image pairing and auxiliary-score behavior.
Repeating the current prompt-conditioned packet would not change the verdict.
