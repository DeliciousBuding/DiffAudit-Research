# CLiD Candidate Integrity Review

This note records the first CPU integrity review for the CLiD 100/100 score
packet. It is a review gate, not admitted evidence.

## Verdict

```text
candidate survives first integrity review; repeat before admission
```

The review was run on `clid-local-bridge-100-20260501-r1`.

| Check | Result |
| --- | --- |
| Metadata rows align with score rows | pass |
| Balanced split rows | pass, 100 member / 100 nonmember |
| Cross-split image SHA-256 duplicates | 0 |
| Cross-split prompt text duplicates | 0 |
| Text-length nuisance AUC | 0.55545 |
| Score-summary gate | pass |
| CLiD auxiliary permutation p-value | 0.001949 over 512 permutations |

Feature sanity:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Feature 0 | 0.9072 | 0.835 | 0.41 | 0.41 |
| CLiD auxiliary feature | 1.0 | 1.0 | 1.0 | 1.0 |

## Interpretation

The first review does not find an obvious row-alignment, duplicate-image,
duplicate-prompt, or text-length leakage explanation. The candidate is strong
enough to justify one independent repeat or perturbation run.

This still does not admit CLiD as product evidence. Admission requires the
signal to survive repeat or perturbation under the same score-summary gate.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw scores and review JSON stay ignored under `workspaces/black-box/runs/`.
