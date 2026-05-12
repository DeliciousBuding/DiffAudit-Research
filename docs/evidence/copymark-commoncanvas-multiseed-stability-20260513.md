# CopyMark CommonCanvas Multi-Seed Stability Scout

Date: 2026-05-13

## Question

After CommonCanvas pixel distance, CLIP query-response image similarity, and
prompt-response consistency all failed, does a different response-distribution
mechanism recover membership? Specifically, do member prompts produce more
stable generated images across fixed seeds than nonmember prompts?

## Contract

- Asset: `response-contract-copymark-commoncanvas-20260512`.
- Model: `common-canvas/CommonCanvas-XL-C`.
- Endpoint: `text_to_image`.
- Subset: first `4` member queries and first `4` nonmember queries from the
  fixed CommonCanvas/CommonCatalog query split.
- Seeds: `20260613` and `20260614`.
- Generation: `512x512`, `20` steps, `guidance_scale = 7.5`.
- Device: local CUDA, RTX 4070.
- Score: `clip_vit_l14_response_seed_stability_cosine`, the mean pairwise
  CLIP ViT-L/14 image-embedding cosine between the same prompt's generated
  responses. Higher means more member-like.

Generated images stay outside Git under
`<DOWNLOAD_ROOT>/black-box/supplementary/response-contract-copymark-commoncanvas-20260512/stability_responses_20260513/`.

Artifact:

`workspaces/black-box/artifacts/copymark-commoncanvas-multiseed-stability-20260513.json`

## Result

| Metric | Value |
| --- | ---: |
| AUC | `0.5625` |
| ASR | `0.625` |
| TPR@1%FPR | `0.25` |
| TPR@0.1%FPR | `0.25` |
| Member mean score | `0.843675` |
| Nonmember mean score | `0.832792` |

The zero-false-positive recovery is only `1 / 4` member samples. The weak
separation is also visible in the per-sample scores: `nonmember_001` scores
`0.936580`, higher than two of the four member samples.

## Decision

Close this stability mechanism by default.

The `1 / 1` smoke was positive, but the smallest balanced packet immediately
collapsed to a weak result. This does not justify expanding to larger subsets,
more seeds, or alternate embedding metrics. CommonCanvas remains
`ready-but-weak / not admitted`; do not continue mining this packet with
multi-seed stability variants.

## Platform and Runtime Impact

None. No admitted result, schema change, or downstream consumer change.
