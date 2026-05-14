# Diffusion Memorization Asset Gate

> Date: 2026-05-15
> Status: memorization-detection prompt set / semantic-shift / large GDrive assets / no MIA release / no GPU release

## Question

Does `YuxinWenRick/diffusion_memorization`, the official code for
`Detecting, Explaining, and Mitigating Memorization in Diffusion Models`, provide
a clean DiffAudit Lane A execution asset with target model identity, exact
member/nonmember split, query/response or score coverage, and a bounded MIA
metric contract?

This is an asset gate only. It checks the public repository, the small prompt
manifest, and public download surfaces. No Stable Diffusion checkpoint, 2.60GB
ground-truth image archive, fine-tuned model folder, memorized image folder, or
SSCD checkpoint was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Detecting, Explaining, and Mitigating Memorization in Diffusion Models` |
| Venue | ICLR 2024 |
| OpenReview | `https://openreview.net/forum?id=84n3UwkH7b` |
| Repository | `https://github.com/YuxinWenRick/diffusion_memorization` |
| Repository pushed at | `2024-04-03T15:09:16Z` |
| Default model in code | `CompVis/stable-diffusion-v1-4` |
| Public prompt manifest | `examples/sdv1_500_memorized.jsonl` |
| Manifest size | `116,357` bytes |
| Manifest SHA256 | `8eb16c6ff1c7195cddf26b3207bdc7c6a905a20162c6070d79fe60336a525c60` |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub README | The repo provides detection, explanation, and mitigation code for Stable Diffusion memorization, not a direct member-vs-nonmember MIA packet. |
| `detect_mem.py` | Runs `CompVis/stable-diffusion-v1-4`, generates images for prompts, and writes `uncond_noise_norm` / `text_noise_norm` tracks. It does not ship a ready ROC/low-FPR MIA score packet. |
| `examples/sdv1_500_memorized.jsonl` | Public small manifest has `500` rows with keys `caption`, `index`, and `url`; all `500` `index` values and all `500` URLs are unique. |
| Hugging Face cache scan | Local cache has `runwayml/stable-diffusion-v1-5` and `common-canvas/CommonCanvas-XL-C`, but not `CompVis/stable-diffusion-v1-4`. |
| Hugging Face dataset/model search | Searches for `diffusion membership inference`, `membership inference diffusion`, `diffusion memorization`, `stable diffusion memorization`, and `laion membership inference` did not find a labeled ready dataset/model packet. |
| Google Drive ground-truth image link | `gdown` reported a `2.60G` file for the `sdv1_500_mem_groundtruth` archive before the probe was stopped and the partial `.part` file was removed. |
| Google Drive fine-tuned/checkpoint surfaces | README points to pre-fine-tuned checkpoint, memorized image, and SSCD checkpoint links, but the gate did not find a small hashable member/nonmember MIA score packet. |
| Local duplicate check | No existing Research evidence entry for `YuxinWenRick/diffusion_memorization`, `sdv1_500_memorized`, or the ICLR 2024 memorization repo was found. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial. Code defaults to `CompVis/stable-diffusion-v1-4`, but the model is not currently cached locally and the repo does not ship a frozen target checkpoint for a DiffAudit MIA packet. |
| Exact member split | Fail for DiffAudit MIA. The public JSONL is a memorized-prompt list, not a per-sample training-member manifest for a target model. |
| Exact nonmember split | Fail. The README uses `Gustavosta/Stable-Diffusion-Prompts` as non-memorized prompts, but does not ship a frozen nonmember manifest paired to the `500` memorized prompts. |
| Query/response or score coverage | Fail. No generated response cache, noise-norm output packet, ROC CSV, low-FPR metric artifact, or DiffAudit-compatible score JSON is released. |
| Metric contract | Semantic shift. The code measures memorization-related noise norm tracks and mitigation behavior, not direct member-vs-nonmember MIA evidence. |
| Asset size boundary | Fail for default acquisition. The ground-truth image archive is `2.60G`; downloading it before a consumer-boundary decision would repeat large-asset watch behavior without a MIA gate. |
| Mechanism delta | Watch only. Memorization detection is related to diffusion privacy and distinct from ReDiffuse/Tracing Roots, but it is not a current admitted or executable MIA lane. |
| GPU release | Fail. Running this would require downloading SD-v1-4 and/or multi-GB GDrive assets, then constructing a new semantic benchmark rather than replaying a released DiffAudit score packet. |

## Decision

`memorization-detection prompt set / semantic-shift / large GDrive assets / no
MIA release / no GPU release`.

The repo is useful as a related memorization reference and has a real small
prompt manifest, but it does not satisfy the current DiffAudit Lane A gates. It
does not provide a frozen target checkpoint, exact member/nonmember MIA splits,
generated responses, score files, ROC artifacts, or a low-FPR MIA metric
packet.

Do not download the `2.60G` ground-truth archive, the fine-tuned checkpoint
folder, the memorized image folder, SSCD weights, or `CompVis/stable-diffusion-v1-4`
by default. Do not run `detect_mem.py` as a substitute for membership inference.
Reopen only if a public-safe package appears with:

- a frozen target model identity or small hashable checkpoint,
- exact member and nonmember manifests for a MIA claim,
- generated response/noise-track outputs or score packets,
- and a bounded low-FPR metric contract that separates memorization detection
  from per-sample membership inference.

## Platform and Runtime Impact

None. This is Research-only related-method/watch evidence. It does not change
admitted Platform/Runtime rows, schemas, or recommendation logic.
