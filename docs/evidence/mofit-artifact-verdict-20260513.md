# MoFit Artifact Verdict

> Date: 2026-05-13
> Status: mechanism-relevant / code-TBW / artifact-incomplete / no GPU release

## Question

Can `No Caption, No Problem: Caption-Free Membership Inference via
Model-Fitted Embeddings` / MoFit become the next Lane B mechanism task or Lane
A asset for DiffAudit?

This is an entry-gate verdict, not an implementation attempt. No models,
datasets, captions, or generated responses were downloaded.

## Evidence Checked

| Source | Finding |
| --- | --- |
| Local paper report | The existing report classifies MoFit as a gray-box text-to-image diffusion MIA that removes the ground-truth caption assumption by optimizing a model-fitted surrogate and model-fitted condition embedding. |
| Paper setting from local report | Main experiments use Stable Diffusion v1.4 fine-tuned on Pokemon, MS-COCO, and Flickr, with `500/500` splits for MS-COCO/Flickr and all Pokemon samples. The method reports strong caption-free results, but needs internal loss access and per-image optimization. |
| Reproduction assessment from local report | Required assets include target LDM weights, member/nonmember splits, conditional/unconditional loss access with backpropagation, VLM caption initialization, and calibration data. |
| `https://github.com/JoonsungJeon/MoFit` README | Public README describes MoFit as the official ICLR 2026 implementation and links the paper and project page. |
| Raw README | The repository's code instruction section is `TBW`, so public runnable code is not currently exposed from the main README. |
| GitHub API | A live API metadata request was rate-limited, so repo state was verified from the browser page and raw README rather than REST metadata. |

## Gate Result

| Gate | Result |
| --- | --- |
| Mechanism delta | Pass. Model-fitted surrogate plus model-fitted condition embedding is distinct from final-layer gradient, raw denoising MSE, pixel/CLIP distance, MIDST nearest/marginal scoring, and midfreq same-contract repeat. |
| Runnable code | Fail. The public README still marks code instructions as `TBW`; no runnable script, config, or cache contract is available from the checked surface. |
| Target identity | Fail for DiffAudit execution. The paper names SD-v1.4 fine-tuning settings, but this cycle did not find released checkpoints or hashable targets. |
| Split manifest | Fail. The local report records member/hold-out counts, but no public per-sample split manifest was found in the checked public surface. |
| Cost/stop condition | Blocked. The method requires per-image optimization with backpropagation, which should not be reimplemented from scratch without released code and exact assets. |
| Consumer boundary | No change. MoFit remains a gray-box mechanism watch candidate, not admitted Platform/Runtime evidence. |

## Decision

`mechanism-relevant / code-TBW / artifact-incomplete / no GPU release`.

MoFit is scientifically relevant because it attacks the exact caption-free
gap that CLiD-style routes leave open. It is not currently executable inside
DiffAudit because the public implementation surface is still incomplete and
the target checkpoint/split artifacts are not exposed.

Do not:

- implement the two-stage surrogate/embedding optimization from scratch;
- fine-tune SD-v1.4 on Pokemon/MS-COCO/Flickr to recreate the paper target;
- run per-image optimization or GPU jobs;
- promote MoFit into Platform/Runtime admitted rows;
- use MoFit to reopen CLiD or final-layer-gradient adjacent variants.

Smallest valid reopen condition:

- The upstream repository publishes runnable code plus configs; and
- exact target checkpoint or deterministic target recreation plus per-sample
  member/nonmember split manifests are available; and
- a bounded `25/25` or `50/50` smoke can be defined with a frozen metric and
  stop condition.

## Reflection

This is a useful Lane B/A gate because the mechanism is genuinely different,
but the artifact surface is not ready. The correction is to keep MoFit as a
watch candidate instead of spending GPU and engineering time on a high-cost
from-scratch reproduction.

## Platform and Runtime Impact

None. MoFit is not admitted evidence, not a product row, and not a Runtime
schema input.
