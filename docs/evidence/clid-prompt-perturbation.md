# CLiD Prompt Perturbation

This note records the prompt-neutral perturbation of the CLiD 100/100 candidate.
It is the current admission blocker for CLiD.

## Verdict

```text
prompt-conditioned positive; prompt-neutral perturbation fails admission
```

The perturbation used the same 100 member and 100 nonmember images, but rewrote
all prompts in both splits to the fixed prompt `a face`.

| Metric | Prompt-conditioned repeat | Prompt-neutral perturbation |
| --- | ---: | ---: |
| AUC | 1.0 | 0.5862 |
| ASR | 1.0 | 0.585 |
| TPR@1%FPR | 1.0 | 0.02 |
| TPR@0.1%FPR | 1.0 | 0.02 |
| Feature 0 AUC | 0.9084 | 0.5848 |
| CLiD auxiliary AUC | 1.0 | 0.57175 |
| CLiD auxiliary permutation p-value | 0.001949 | 0.046784 |

Integrity review on the prompt-neutral packet found:

| Check | Result |
| --- | --- |
| Metadata rows align with score rows | pass |
| Balanced split rows | pass |
| Cross-split image SHA-256 duplicates | 0 |
| Text-length nuisance AUC | 0.5 |
| Score-summary gate | pass |
| CLiD auxiliary permutation significance | warning |

The prompt overlap warning is expected because both splits intentionally use the
same fixed prompt.

## Interpretation

The original CLiD signal is strong and repeat-stable under the prompt-conditioned
bridge, but it does not survive prompt-neutral perturbation. That means the
current evidence supports a prompt-conditioned leakage claim, not an admitted
general black-box membership signal.

This is useful because it narrows the research claim and prevents overclaiming:
future CLiD work must state the prompt contract explicitly and compare against a
prompt-neutral or prompt-perturbed control.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- No additional CLiD GPU packet is selected until the next hypothesis separates
  prompt-conditioning from membership signal more cleanly.
