# CLiD Within-Split Prompt Shuffle Control

This note records the within-split prompt shuffle control for the CLiD 100/100
bridge. It is candidate evidence, not admitted evidence.

## Verdict

```text
within-split prompt shuffle remains weak-positive; CLiD depends on the
prompt-image contract and is still not admitted
```

The control used the same 100 member and 100 nonmember images as the original
CLiD bridge. Prompt text was shuffled inside each split with seed `0`, preserving
member and nonmember prompt distributions while breaking the original
image-prompt pairing.

| Metric | Prompt-conditioned repeat | Fixed prompt control | Swapped-prompt control | Within-split shuffle |
| --- | ---: | ---: | ---: | ---: |
| AUC | 1.0 | 0.5862 | 0.72885 | 0.64105 |
| ASR | 1.0 | 0.585 | 0.67 | 0.645 |
| TPR@1%FPR | 1.0 | 0.02 | 0.21 | 0.12 |
| TPR@0.1%FPR | 1.0 | 0.02 | 0.21 | 0.12 |
| Feature 0 AUC | 0.9084 | 0.5848 | 0.6376 | 0.6094 |
| CLiD auxiliary AUC | 1.0 | 0.57175 | 0.7218 | 0.63815 |

Integrity review on the within-split shuffle packet found:

| Check | Result |
| --- | --- |
| Metadata rows align with score rows | pass |
| Balanced split rows | pass, 100 member / 100 nonmember |
| Cross-split image SHA-256 duplicates | 0 |
| Cross-split prompt text duplicates | 0 |
| Text-length nuisance AUC | 0.55545 |
| Score-summary gate | pass |
| CLiD auxiliary permutation p-value | 0.001949 over 512 permutations |

## Interpretation

The sequence of controls now gives a sharper boundary:

| Contract | Strict-tail result | Interpretation |
| --- | ---: | --- |
| Original prompt-conditioned repeat | 1.0 | Strong under the original prompt/image pairing. |
| Fixed prompt | 0.02 | Removing prompt variation collapses the signal. |
| Swapped prompts across splits | 0.21 | Prompt text alone is not the whole signal, but the signal is degraded. |
| Shuffled prompts within each split | 0.12 | Preserving split-level prompt distribution is not enough to recover the original signal. |

The best current explanation is that CLiD is measuring a prompt-conditioned
interaction with the tested image/prompt contract, not a general black-box
membership signal. The residual strict-tail signal under shuffled prompts is
worth studying, but it is weaker than the original packet and still only uses
one local bridge and one 100/100 split.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw score files and generated bridge payloads remain ignored under
  `workspaces/black-box/runs/`.
- Next CLiD work should be CPU-first: define whether an image-only control or an
  independent prompt-control repeat would answer a genuinely new question.
