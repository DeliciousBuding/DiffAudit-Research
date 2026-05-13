# Noise as a Probe Asset Verdict

> Date: 2026-05-13
> Status: mechanism-relevant / reproduction-incomplete / no download / no GPU release

## Taste Check

This is a Lane A clean-asset search verdict after the Zenodo fine-tuned
diffusion line reached a split-manifest blocker. The candidate is not LAION-mi
live URLs, CommonCanvas, MIDST, Beans, MNIST, Fashion-MNIST, Kohaku/Danbooru,
or a final-layer gradient variant.

The question is whether `Noise as a Probe: Membership Inference Attacks on
Diffusion Models Leveraging Initial Noise` can provide either a cleaner second
membership asset or a directly runnable next packet.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `Noise as a Probe: Membership Inference Attacks on Diffusion Models Leveraging Initial Noise` |
| Primary source checked | arXiv `2601.21628` source archive |
| Mechanism | DDIM inversion with a pre-trained diffusion model to obtain semantic initial noise, then target-model generation and reconstruction-distance membership scoring |
| Target model family | Stable Diffusion-v1-4 fine-tuning, per paper |
| Reported datasets | Pokémon, text-to-image-2M, MS-COCO, Flickr |

No model weights, dataset payloads, responses, or code repository were
downloaded. Only the arXiv source archive was inspected.

## Primary-Source Evidence

The arXiv source gives enough detail to classify the method as a genuinely new
mechanism relative to the currently closed lines:

- It fine-tunes Stable Diffusion-v1-4 with Hugging Face Diffusers scripts.
- It constructs member/hold-out datasets with reported counts:
  `416/417` Pokémon, `500/500` T-to-I, `2500/2500` MS-COCO, and `1000/1000`
  Flickr.
- The attack obtains semantic initial noise through DDIM inversion on the
  target image and prompt, then feeds that noise and prompt into the target
  model and scores reconstruction distance.
- The paper reports AUC and TPR at `1%` FPR, matching the strict-tail metric
  style already used by DiffAudit.

This is not another pixel/CLIP distance on generated outputs alone, nor raw
denoising MSE, final-layer gradient, nearest-neighbor tabular scoring, or
same-contract residual replay.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial pass: paper specifies Stable Diffusion-v1-4 fine-tuning, but no released checkpoint or exact training artifact was found in this cycle. |
| Exact member/nonmember split | Fail: the paper reports dataset counts, but no per-sample member/hold-out manifest is exposed by the arXiv source. |
| Query/response coverage | Fail: no generated response package, inversion cache, or runnable query/response contract is provided. |
| Code availability | Fail for release: no public code repository was found during this cycle. The arXiv source contains paper TeX and figures, not an executable artifact. |
| Mechanism delta | Pass for intake: semantic-initial-noise reconstruction is a genuinely different observable family. |
| GPU release | Fail: target artifacts, split identities, code, and stop condition are not frozen. |

## Decision

`mechanism-relevant / reproduction-incomplete / no download / no GPU release`.

Noise as a Probe should be retained as a Lane B mechanism idea and Lane A watch
candidate, but it is not a `next_gpu_candidate`. Its value is conceptual: if a
clean same-contract target appears later, semantic-initial-noise reconstruction
is a better new observable family than repeating CommonCanvas, Beans, MIDST,
MNIST, Fashion-MNIST, final-layer-gradient, or midfreq variants.

Smallest valid reopen condition:

- A public code repository or artifact release appears; and
- A per-sample member/hold-out manifest or deterministic split recreation
  policy is available; and
- The exact SD-v1-4 fine-tuning checkpoint or reproducible training recipe is
  available; and
- A bounded `25/25` or `50/50` semantic-initial-noise reconstruction scorer can
  be frozen with an `AUC < 0.60` or near-zero strict-tail stop condition.

Stop condition:

- Do not download datasets, fine-tune SD-v1-4, or implement DDIM-inversion
  tooling from scratch for this paper alone. Without released code/split
  artifacts, that would become another expensive reproduction project rather
  than a ROADMAP execution cycle.

## Reflection

This cycle found a genuinely different mechanism family but did not find a
runnable asset contract. The correct outcome is to preserve it as a future
mechanism hook and keep the active GPU slots empty.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
