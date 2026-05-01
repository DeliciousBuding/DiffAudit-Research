# Recon Product Validation Result

This note records the bounded GPU rerun for the selected recon strengthening
lane. It is a validation result, not a new admitted row.

## Verdict

```text
strict-tail signal confirmed; product-row promotion blocked by metric-source mismatch
```

The rerun produced a complete metric set for the frozen
`recon DDIM public-100 step30` packet:

| Metric source | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Runtime mainline combined summary | 0.837 | 0.74 | 1.0 | 0.2 |
| Artifact-summary target score path | 0.7463 | 0.505 | 1.0 | 0.2 |

The strict-tail value is nonzero and stable across the combined summary and
artifact-summary path. That is useful progress: the recon black-box line now has
a concrete `TPR@0.1%FPR` value for the product-validation packet.

The result should not replace the admitted black-box row yet. The AUC and ASR
come from different metric sources:

- `upstream_eval` reports `AUC = 0.837` and `ASR = 0.74`.
- `artifact-summary` reports `target_auc = 0.7463` and `target_asr = 0.505`.
- `artifact-summary` is the source for both low-FPR tail metrics:
  `TPR@1%FPR = 1.0` and `TPR@0.1%FPR = 0.2`.

## Run Identity

| Field | Value |
| --- | --- |
| Run | `recon-product-validation-public100-step30-20260501-r1` |
| Method | `recon` |
| Dataset size | 100 target member, 100 target nonmember, 100 shadow member proxy, 100 shadow nonmember |
| Model family | Stable Diffusion v1.5 + DDIM |
| Scheduler | `ddim` |
| Inference steps | `30` |
| Validation images per query | `1` |
| Evaluation method | `threshold` |
| Runtime status | ready |

Generated images and score artifacts remain ignored under
`workspaces/black-box/runs/`.

## Interpretation

The old blocker, missing `TPR@0.1%FPR`, is resolved for new recon summaries. The
new blocker is semantic: Platform/Runtime should not consume a row until the
headline metric source is unambiguous.

Allowed claim:

- `recon` has a validated nonzero strict-tail signal on the public-100 step30
  product-validation packet.
- The packet remains bounded by controlled public-subset and proxy-shadow-member
  semantics.

Blocked claim:

- Do not present this as a new admitted black-box row.
- Do not replace the existing admitted row until the metric-source mismatch is
  reconciled.
- Do not claim paper-complete reproduction or broader conditional-diffusion
  generality.

## Next Action

CPU-first metric-source reconciliation:

- Decide whether product-facing AUC/ASR should come from upstream eval,
  artifact-summary target scores, or a single unified metric path.
- Add a review packet that exposes both sources and explains the chosen
  product-facing source.
- Promote only after the selected source is stable and all four headline metrics
  come from a coherent contract.
