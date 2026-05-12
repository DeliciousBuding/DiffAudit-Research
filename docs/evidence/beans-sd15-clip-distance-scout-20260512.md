# Beans SD1.5 CLIP-Distance Scout

> Date: 2026-05-12
> Status: weak; no GPU release

## Question

Pixel MSE/MAE was weak on the ready Beans/SD1.5 response contract. Does a
different observable, local CLIP image-embedding distance between query and
response, reveal a transferable membership signal?

This is a single CPU scorer check. It is not a new framework or ablation lane.

## Setup

- Asset id: `response-contract-beans-sd15-20260512`
- Member queries: `25`
- Nonmember queries: `25`
- Responses: one deterministic local SD1.5 image-to-image response per query
- Embedding model: local `clip-vit-large-patch14`
- Feature used: image `pooler_output`, L2-normalized
- Score: `1 - cosine(query_embedding, response_embedding)`
- Score convention: lower CLIP distance is more member-like

Local CLIP loaded offline. In this environment,
`CLIPModel.get_image_features(...)` returns a model output object, so the scout
used `pooler_output` rather than assuming a direct tensor return.

## Result

| Metric | Value |
| --- | ---: |
| member mean distance | `0.075180` |
| nonmember mean distance | `0.071585` |
| AUC, lower distance = member | `0.422400` |
| Best ASR | `0.540000` |
| TPR@1%FPR | `0.080000` |
| TPR@0.1%FPR | `0.080000` |

The expected direction is wrong: nonmembers are slightly closer on average.
Even if interpreted in the reverse direction, the AUC is only `0.577600`.

## Verdict

`weak; no GPU release`.

CLIP image-embedding distance is a genuinely different observable from raw
pixel distance, but it still does not provide a useful membership signal on the
ready Beans/SD1.5 package. Do not expand this into more embedding-distance
variants without a new mechanism.

## Next Action

Stop simple query-response distance scoring on this package for now. A next
step needs a different mechanism, not another distance polish:

- response residuals tied to the generation process,
- repeated-response instability if a repeat budget is deliberately acquired,
- a matched same-policy comparator with an explanation for why members should
  behave differently.

If none of those is selected, the honest state is: ready second-query response
contract, first two cheap scorers weak, no GPU candidate.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change product rows.
