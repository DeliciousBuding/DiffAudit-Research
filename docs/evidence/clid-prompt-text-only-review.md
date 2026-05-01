# CLiD Prompt-Text-Only Review

This note records a prompt-text-only nuisance baseline for the CLiD 100/100
bridge. It does not use images, generated score matrices, or CLiD outputs.

## Verdict

```text
prompt text alone is moderately separable but does not explain the original
CLiD strict-tail signal
```

The review used binary token features from `metadata.jsonl` prompts and a
split-centroid scorer. This is a nuisance baseline, not an admission method.

| Metric | Prompt-text-only baseline | Original CLiD repeat |
| --- | ---: | ---: |
| AUC | 0.70715 | 1.0 |
| ASR | 0.66 | 1.0 |
| TPR@1%FPR | 0.02 | 1.0 |
| TPR@0.1%FPR | 0.02 | 1.0 |
| Text-length AUC | 0.55545 | n/a |
| Token-count AUC | 0.55425 | n/a |

The selected prompt vocabulary had 105 features with `min_count = 2`. There
were 100 member prompts, 100 nonmember prompts, and no exact cross-split prompt
duplicates.

## Interpretation

Prompt text alone carries moderate split information. That is an important
nuisance factor and supports keeping CLiD candidate-only.

However, prompt text alone does not recover the original strict-tail signal:
`TPR@0.1%FPR` is `0.02`, matching the fixed-prompt failure level rather than the
original CLiD repeat. Combined with the swapped-prompt and within-split shuffle
controls, the current best interpretation is that CLiD depends on the tested
prompt-image contract and auxiliary scoring path, not prompt text alone.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw review JSON remains ignored under `workspaces/black-box/runs/`.
- Next CLiD work should be CPU-first unless a new GPU packet can isolate image
  identity, prompt-image pairing, or auxiliary-score behavior more cleanly.
