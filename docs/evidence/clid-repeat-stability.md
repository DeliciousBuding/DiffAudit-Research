# CLiD Repeat Stability

This note records the independent repeat of the CLiD 100/100 score packet under
the same frozen score-summary gate. It is still candidate evidence, not admitted
evidence.

## Verdict

```text
repeat-stable positive bounded candidate; perturb before admission
```

The repeat was run as `clid-local-bridge-100-repeat-20260501-r2`.

| Metric | First 100/100 packet | Repeat packet |
| --- | ---: | ---: |
| AUC | 1.0 | 1.0 |
| ASR | 1.0 | 1.0 |
| TPR@1%FPR | 1.0 | 1.0 |
| TPR@0.1%FPR | 1.0 | 1.0 |
| Feature 0 AUC | 0.9072 | 0.9084 |
| Feature 0 TPR@0.1%FPR | 0.41 | 0.3 |
| CLiD auxiliary AUC | 1.0 | 1.0 |
| CLiD auxiliary TPR@0.1%FPR | 1.0 | 1.0 |

Across the two packets, row-wise feature correlations were:

| Surface | Correlation |
| --- | ---: |
| Member feature 0 | 0.986877 |
| Member CLiD auxiliary | 0.931874 |
| Nonmember feature 0 | 0.980435 |
| Nonmember CLiD auxiliary | 0.759068 |

## Interpretation

The signal is stable across an independent repeat with fresh runtime noise. The
candidate is now strong enough for prompt perturbation or stricter held-out
review.

This still does not admit CLiD as product evidence because the repeat uses the
same member/nonmember split. The next review should perturb prompts or otherwise
stress whether the CLiD auxiliary separation survives beyond the exact bridge
setup.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw scores and repeat run payloads stay ignored under `workspaces/black-box/runs/`.
