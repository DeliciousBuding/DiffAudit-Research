# CLiD Control Attribution

This note compares the CLiD prompt-control packets against the prompt-conditioned
repeat. It uses already generated score matrices under ignored run storage and
does not run a model.

## Verdict

```text
controls degrade CLiD strict-tail signal; no control admits CLiD
```

The strict-tail retention pattern is:

| Control | AUC | TPR@0.1%FPR | Strict-tail retention vs repeat |
| --- | ---: | ---: | ---: |
| Prompt-conditioned repeat | 1.0 | 1.0 | 1.0 |
| Fixed prompt | 0.5862 | 0.02 | 0.02 |
| Swapped prompt | 0.72885 | 0.21 | 0.21 |
| Within-split prompt shuffle seed 0 | 0.64105 | 0.12 | 0.12 |
| Within-split prompt shuffle seed 1 | 0.59425 | 0.08 | 0.08 |

The feature-correlation pattern against the prompt-conditioned repeat is:

| Control | Member feature 0 Pearson | Member CLiD auxiliary Pearson | Nonmember feature 0 Pearson | Nonmember CLiD auxiliary Pearson |
| --- | ---: | ---: | ---: | ---: |
| Fixed prompt | 0.893234 | 0.033173 | 0.948928 | 0.308893 |
| Swapped prompt | 0.816335 | 0.008105 | 0.930595 | 0.24798 |
| Within-split prompt shuffle seed 0 | 0.797516 | 0.086773 | 0.92794 | 0.211426 |
| Within-split prompt shuffle seed 1 | 0.768709 | 0.024058 | 0.913797 | 0.18218 |

## Interpretation

Feature 0 remains fairly correlated with the prompt-conditioned repeat across
controls, especially on nonmembers. The CLiD auxiliary feature does not: member
auxiliary correlations are near zero under all prompt controls, and nonmember
auxiliary correlations are weak.

That is the strongest current evidence that the original `1.0` strict-tail
signal is not a stable image-identity score. It depends on the prompt-conditioned
auxiliary path. The controls do not fully collapse every signal, but they
degrade strict-tail performance enough to block admission. The second
within-split shuffle seed further weakens the residual signal, so CLiD should
not receive another same-protocol GPU packet.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw score files and generated run payloads remain ignored under
  `workspaces/black-box/runs/`.
- The next GPU run is not selected. A future CLiD run must answer a new control
  question, not repeat the same prompt-conditioned packet.
