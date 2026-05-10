# Gray-Box Tri-Score Consolidation Review

> Date: 2026-05-10
> Status: positive-but-bounded internal candidate; no admitted promotion

## Question

After ReDiffuse closed as candidate-only and black-box second response-contract
discovery closed as `needs-assets`, is there an existing gray-box result that is
strong enough to become the next internal Research mainline candidate without
claiming a new admitted row?

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `workspaces/gray-box/artifacts/graybox-triscore-consolidation-summary.json` | Curated tracked summary of the first aligned canary and two larger matched-surface repeats. |
| [admitted-results-summary.md](admitted-results-summary.md) | Current admitted gray-box boundary. |
| [pia-stochastic-dropout-truth-hardening-review.md](pia-stochastic-dropout-truth-hardening-review.md) | Current PIA boundary and finite-tail caveats. |

The tri-score contract itself states:

- `feature_mode = paired-pia-tmiadm-zscore-triscore`
- `component_reporting_required = true`
- `headline_use_allowed = false`
- `external_evidence_allowed = false`

That contract is decisive: this line can guide Research, but cannot replace the
admitted PIA gray-box row without a separate promotion gate.

## Results

| Packet | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| X-88 tri-score canary | `0.854515` | `0.790039` | `0.130859` | `0.048828` | Positive internal canary on the first aligned packet. |
| X-141 larger surface seed 1 | `0.849247` | `0.782226` | `0.069336` | `0.022461` | Positive but weaker strict-tail lift. |
| X-142 larger surface seed 2 | `0.859043` | `0.786133` | `0.118164` | `0.023438` | Positive repeat with stronger 1% tail. |

The tracked artifact preserves the source run ids for traceability, but this
review cites the curated summary rather than treating ignored run directories as
the public evidence source.

The admitted PIA GPU512 baseline remains:

- `AUC = 0.841339`
- `ASR = 0.786133`
- `TPR@1%FPR = 0.058594`
- `TPR@0.1%FPR = 0.011719`

Compared with that admitted row, the tri-score packets are consistently useful
for internal ranking and low-FPR scouting. The strongest repeat, X-142, improves
macro AUC and `TPR@1%FPR` over the admitted PIA baseline. The stricter
`TPR@0.1%FPR` remains small and seed-sensitive, so this is not admission-grade
low-FPR evidence.

## Interpretation

This line is scientifically useful because it is not another threshold switch
between PIA and TMIA-DM. It is an internal evidence-aggregation scorer that
keeps component reporting and identity alignment explicit.

It should be treated as:

```text
positive-but-bounded internal gray-box evidence aggregation
```

It should not be treated as:

- an admitted gray-box replacement for PIA,
- a product-facing result,
- paper-faithful CDI,
- a conditional-diffusion or commercial-model claim,
- a low-FPR robustness claim.

## Verdict

`positive-but-bounded`.

The next selected CPU-first task should be a tri-score truth-hardening preflight:

1. freeze the exact two-seed evidence set,
2. define the promotion blocker that keeps it internal-only,
3. test whether its low-FPR gains survive a simple uncertainty or leave-one-surface
   review,
4. only then decide whether any GPU expansion is justified.

No GPU task is released by this review.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. Product-facing consumers should
continue to use the admitted PIA gray-box row, not the internal tri-score
candidate.
