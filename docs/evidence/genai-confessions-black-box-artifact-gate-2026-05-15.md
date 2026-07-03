# GenAI Confessions Black-Box Artifact Gate

> Date: 2026-05-15
> Status: data-public / response-and-checkpoint-missing / semantic-boundary / no dataset download / no GPU release / no admitted row

## Question

Does `GenAI Confessions: Black-box Membership Inference for Generative Image
Models` provide a ready DiffAudit black-box execution packet or admitted
second-asset benchmark?

This gate inspected public repository metadata, Git tree metadata, CSV headers,
Zenodo metadata, Hugging Face dataset metadata, and the paper text. The Zenodo
data ZIP and HF image files were not downloaded.

## Candidate

| Field | Value |
| --- | --- |
| GitHub repository | `https://github.com/hanyfarid/MembershipInference` |
| Repo description | `Has an AI model been trained on your images?` |
| Default branch inspected | `main` |
| Latest repo push observed | `2024-12-29T22:11:01Z` |
| GitHub license field | none exposed |
| GitHub release | `datarelease`, no release assets |
| Zenodo record | `https://zenodo.org/records/14573149` |
| Zenodo DOI | `10.5281/zenodo.14573149` |
| Zenodo file | `hanyfarid/MembershipInference-datarelease.zip`, `133,599,324` bytes, `md5:6ec572d777fd04ef6cdedc712d2b086e` |
| Paper | arXiv `2501.06399v2`, ICCV-W 2025 |
| HF dataset | `faridlab/stroll`, public, non-gated, `size_categories=n<1K` |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Paper text | Method is black-box image-to-image membership inference using seed image, caption, controllable strength, generated outputs, DreamSim distances, and logistic regression. It reports STROLL average accuracy `85%` with `TPR@1%FPR = 74%`, and Carlini transfer average accuracy `93%` with `TPR@1%FPR = 90%`. |
| Paper text | STROLL uses a custom derivative of Stable Diffusion v2.1 fine-tuned on the `100` in-training images for `100` steps, with a second `1000`-step memorization variant. The public artifact does not ship either checkpoint. |
| GitHub tree | Repository is data-only: `Carlini/intraining/images-and-captions.csv`, `Carlini/outoftraining/*.png`, `Midjourney/intraining/images-and-captions.csv`, `Midjourney/outoftraining/*.png`, and `STROLL/download.py`. |
| Carlini CSV | In-training rows provide `file-name`, `caption`, and source `url` for Stable Diffusion v1.4 memorization examples. |
| Midjourney CSV | In-training rows provide `file-name`, `caption`, and source `url` for Midjourney v6 memorization examples. |
| `STROLL/download.py` | Delegates to `datasets.load_dataset("faridlab/stroll", trust_remote_code=True)`. |
| HF dataset metadata | `faridlab/stroll` is public and non-gated, with `100` in-training/out-of-training image pairs and captions. |
| Zenodo metadata | Publishes a single datarelease ZIP. The record is open under `cc-by-4.0`, but it is a data snapshot, not a verifier or generated-response packet. |

## What Is Present

The public release has real member/nonmember-style raw inputs:

- STROLL: `100` paired in-training/out-of-training smartphone image pairs with
  detailed captions and explicit in-training/out-of-training annotation.
- Carlini: `74` Stable Diffusion v1.4 memorization-derived in-training images
  plus semantically matched out-of-training images.
- Midjourney: `10` Midjourney v6 memorization-derived in-training images plus
  semantically matched out-of-training images.

This is stronger than a paper-only watch item because the raw evaluation images
and captions are public or public-loadable.

## What Is Missing

The release does not provide:

- the STROLL fine-tuned Stable Diffusion v2.1 checkpoint for either `100` or
  `1000` training steps;
- generated image-to-image response grids for any strength setting;
- DreamSim distance vectors, logistic-regression inputs, ROC CSVs, metric JSON,
  or ready verifier outputs;
- Midjourney Discord query logs or generated outputs;
- code implementing the DreamSim scorer and logistic-regression replay in the
  GitHub repository;
- a product-bridge decision that admits image-to-image commercial/black-box
  generated-image membership as equivalent to the current DiffAudit per-sample
  diffusion audit rows.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial pass. The paper names SD2.1 fine-tuned STROLL, SD1.4, and Midjourney v6 settings, but the fine-tuned SD2.1 checkpoint and commercial Midjourney state are not public artifacts. |
| Exact member split | Pass for raw inputs. STROLL/HF and the GitHub CSVs expose member-style image identities. |
| Exact nonmember split | Pass for raw inputs. STROLL/HF and out-of-training folders expose paired nonmember-style images. |
| Query/response coverage | Fail. No generated image-to-image outputs or DreamSim feature packets are released. |
| Metric contract | Partial pass. Paper defines DreamSim distance vectors and logistic regression, but no runnable replay or metric artifact is shipped. |
| Current DiffAudit fit | Boundary watch. The method is relevant and black-box, but it is image-to-image response similarity over model services or a missing fine-tuned checkpoint, not a ready DiffAudit response/score packet. |
| Download justification | Fail for this cycle. Downloading the `133,599,324` byte ZIP or HF images would not produce the missing model responses, checkpoint, distance vectors, or verifier. |
| GPU release | Fail. Any execution would require fine-tuning or querying external services before scoring. |

## Decision

`data-public / response-and-checkpoint-missing / semantic-boundary / no dataset
download / no GPU release / no admitted row`.

GenAI Confessions is a high-value black-box related-method watch item. It is
not a current execution target because the public release gives raw seed images
and captions, not the target model artifacts or generated response packet needed
to replay the reported membership metrics.

Smallest valid reopen condition:

- A public STROLL fine-tuned SD2.1 checkpoint with size/hash/training binding,
  or a public generated-response package for the paper's strength grid;
- DreamSim distance vectors, ROC/metric artifacts, or a verifier script that
  reproduces the reported STROLL/Carlini metrics from public files; and
- A consumer-boundary decision that admits image-to-image black-box service
  membership as a DiffAudit lane distinct from the current admitted
  `recon / PIA / GSA / DPDM` rows.

Stop condition:

- Do not download the Zenodo ZIP or HF image payload in the current cycle.
- Do not fine-tune STROLL SD2.1 checkpoints, query Midjourney manually, or
  rebuild DreamSim/logistic-regression replay from scratch.
- Do not promote GenAI Confessions into Platform/Runtime admitted rows,
  schemas, recommendation logic, or product copy.

## Reflection

This candidate is closer to a real black-box membership benchmark than many
paper-only assets because raw member/nonmember images are public. It still does
not change the current route decision: no ready response packet, checkpoint,
feature packet, or consumer-boundary handoff exists. Current slots remain
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after GenAI Confessions black-box artifact gate`.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted
`recon / PIA baseline / PIA defended / GSA / DPDM W-1` set.
