# CLiD Swapped-Prompt Control

This note records the swapped-prompt control for the CLiD 100/100 bridge. It is
candidate evidence, not admitted evidence.

## Verdict

```text
swapped-prompt control remains positive but degraded; CLiD is not prompt-only,
but still not admitted
```

The control used the same 100 member and 100 nonmember images as the original
CLiD bridge. Member and nonmember prompt text were swapped by row before running
the CLiD local bridge scorer.

| Metric | Prompt-conditioned repeat | Fixed prompt control | Swapped-prompt control |
| --- | ---: | ---: | ---: |
| AUC | 1.0 | 0.5862 | 0.72885 |
| ASR | 1.0 | 0.585 | 0.67 |
| TPR@1%FPR | 1.0 | 0.02 | 0.21 |
| TPR@0.1%FPR | 1.0 | 0.02 | 0.21 |
| Feature 0 AUC | 0.9084 | 0.5848 | 0.6376 |
| CLiD auxiliary AUC | 1.0 | 0.57175 | 0.7218 |

Integrity review on the swapped-prompt packet found:

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

The fixed-prompt control showed that removing prompt variation collapses the
strict-tail signal. The swapped-prompt control shows a different boundary:
strict-tail signal remains nonzero after prompt text is moved across splits,
but the result is much weaker than the original prompt-conditioned packet.

That means the current CLiD evidence should not be described as a pure
prompt-only shortcut. It is better described as a prompt-conditioned candidate
whose signal depends on the tested prompt/image contract.

This still does not admit CLiD as general black-box evidence because the control
uses the same 100/100 split identity, one local bridge, and one prompt-swap
policy. Admission would require an independent control repeat or a stricter
held-out prompt/image contract.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw score files and generated bridge payloads remain ignored under
  `workspaces/black-box/runs/`.
- Next CLiD work should compare whether the remaining signal comes from image
  identity, prompt-image mismatch, or another CLiD auxiliary scoring artifact.
