# Recon Product Validation Result

This note records the bounded GPU rerun for the selected recon strengthening
lane. It is a validation result, not a new admitted row.

## Verdict

```text
metric-source reconciled; coherent packet promoted as current black-box row
```

The rerun produced a complete metric set for the frozen
`recon DDIM public-100 step30` packet:

| Metric source | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Runtime mainline initial summary | 0.837 | 0.74 | 1.0 | 0.2 |
| Raw feature-0 artifact comparison | 0.7463 | 0.505 | 1.0 | 0.2 |
| Unified upstream-threshold reimplementation | 0.8372 | 0.745 | 0.22 | 0.11 |
| Combined artifact mainline | 0.837 | 0.74 | 0.22 | 0.11 |

The coherent packet uses the upstream threshold semantics: fit standardization on
shadow train features, transform target features with the same statistics, score
each row by the maximum standardized feature, select threshold on shadow train,
and evaluate on target. The raw feature-0 path is retained only as a comparison
field and is not the product-facing metric source.

This resolves the previous metric-source mismatch. The promoted packet now has
one coherent source for all four headline fields:

- `AUC = 0.837`
- `ASR = 0.74`
- `TPR@1%FPR = 0.22`
- `TPR@0.1%FPR = 0.11`

The result replaces the older admitted black-box row because it uses a stricter,
coherent metric contract and supplies all four product-facing fields. The older
row should not be used for product copy except as historical context.

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

The old blockers are resolved for the promoted packet: `TPR@0.1%FPR` is now
emitted, and all four headline metrics are computed from one coherent metric
source.

Allowed claim:

- `recon` has a validated coherent product packet on public-100 step30 with
  nonzero strict-tail signal.
- The packet remains bounded by controlled public-subset and proxy-shadow-member
  semantics.

Blocked claim:

- Do not compare against older recon rows without stating that the metric source
  changed.
- Do not claim paper-complete reproduction or broader conditional-diffusion
  generality.

## Next Action

CPU-first follow-up:

- Keep the admitted-results table and product-bridge handoff synchronized with
  the unified metric source and claim boundary.
- Do not schedule another recon GPU run unless the promotion review finds a
  concrete gap that cannot be resolved from existing score artifacts.
