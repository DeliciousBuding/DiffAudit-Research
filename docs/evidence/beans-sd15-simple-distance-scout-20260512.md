# Beans SD1.5 Simple-Distance Scout

> Date: 2026-05-12
> Status: weak; no GPU release

## Question

On the ready `response-contract-beans-sd15-20260512` package, does the simplest
query-response pixel distance separate member queries from nonmember queries?

This is the smallest useful scoring check after package readiness. It should
not become a larger ablation table unless it changes direction.

## Package

- Asset id: `response-contract-beans-sd15-20260512`
- Member queries: `25`
- Nonmember queries: `25`
- Responses: one deterministic local SD1.5 image-to-image response per query
- Score convention: lower query-response distance is more member-like

## Scores

Two CPU-only scores were computed directly from the package images:

- RGB pixel MSE between query and response
- RGB pixel MAE between query and response

No new runner or validator was added.

## Result

| Score | Member mean | Nonmember mean | AUC | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSE | `0.005779` | `0.006423` | `0.508800` | `0.560000` | `0.040000` | `0.040000` |
| MAE | `0.053645` | `0.055435` | `0.499200` | `0.560000` | `0.040000` | `0.040000` |

The means move in the expected direction for MSE, but the ranking is nearly
random and the strict-tail recovery is one sample at this split size.

## Verdict

`weak; no GPU release`.

The ready Beans/SD1.5 response contract is useful because it removes the
asset-readiness blocker, but naive pixel distance is not a transferable signal
on this package. Do not enlarge this exact score into a bigger run.

## Next Action

Stop the naive pixel-distance route. A next scorer is only worth running if it
changes the observable, for example:

- a perceptual or embedding distance using already-local CLIP/BLIP weights,
- a response-residual feature that is not raw pixel MSE/MAE,
- a matched same-policy comparator that can explain why member responses should
  stay closer.

If no such scorer is selected, the correct state is `ready package / weak first
score`, not a GPU candidate.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change product rows.
