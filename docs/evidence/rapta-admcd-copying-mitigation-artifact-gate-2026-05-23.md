# RAPTA / ADMCD Copying-Mitigation Artifact Gate

> Date: 2026-05-23
> Status: paper-source-only copying / memorization mitigation watch / no
> official code / no score artifacts / no download / no GPU release

## Question

Can arXiv `2603.13070` / `Mitigating Memorization in Text-to-Image
Diffusion via Region-Aware Prompt Augmentation and Multimodal Copy Detection`
become a bounded DiffAudit execution target, or should it remain Research-only
copying / memorization-mitigation context?

This was a metadata gate only. I checked arXiv HTML, arXiv source `HEAD`, exact
title / arXiv-id / method-name GitHub repository and code searches, and the
visible public code/data/media surface. No arXiv source tarball, PDF, GitHub
archive, dataset, model weight, generated image packet, checkpoint, score file,
ROC artifact, metric JSON, or verifier output was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `Mitigating Memorization in Text-to-Image Diffusion via Region-Aware Prompt Augmentation and Multimodal Copy Detection` |
| arXiv | `2603.13070v1` |
| Submitted | `2026-03-13T15:16:27Z` |
| Authors | Yunzhuo Chen, Jordan Vice, Naveed Akhtar, Nur Al Hasan Haldar, Ajmal Mian |
| Methods | Region-Aware Prompt Augmentation (`RAPTA`) and Attention-Driven Multimodal Copy Detection (`ADMCD`) |
| arXiv source `HEAD` | `application/gzip`, `Content-Length = 4,172,177`, SHA-256 ETag `f44be31acedbcb98485527bb56c4c1e7e02c96d646b7f09e36edf356280fe059` |
| Official repository | none found in checked public searches |

## Public Surface Checked

| Source | Finding |
| --- | --- |
| arXiv HTML | The paper frames the problem as text-to-image memorization / copying risk, not the current per-sample membership audit contract. RAPTA augments prompts from object-detected salient regions during training; ADMCD fuses local patch, global semantic, and texture cues for copying detection. |
| arXiv metadata | The visible submission has one version, submitted `2026-03-13`, with full-text links for PDF, HTML, and TeX source. |
| arXiv source `HEAD` | Source is available as a `4,172,177` byte gzip with SHA-256 ETag `f44be31acedbcb98485527bb56c4c1e7e02c96d646b7f09e36edf356280fe059`; it was not downloaded because HTML/source metadata is enough to decide this cycle. |
| GitHub repository search | Searches for `2603.13070`, `RAPTA ADMCD`, exact title, and `Region-Aware Prompt Augmentation` found no official implementation repository. |
| GitHub code search | Searches for `2603.13070`, `ADMCD RAPTA`, and exact method/title phrases returned only arXiv/paper-index aggregators or no hits, not artifact-bearing implementation code. |
| Code/data/media surface | No official code, dataset, score packet, ROC array, metric JSON, generated response packet, checkpoint, or verifier was visible through the checked public surface. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail. The public page does not expose checkpoint-bound target model identities, scheduler/config hashes, or defended/undefended packages. |
| Exact member/nonmember split | Fail. The claim is copying / memorization mitigation and detection; no immutable member/nonmember or copied/non-copied row manifest is public. |
| Query/response or score coverage | Fail. No generated image packet, ADMCD per-row score file, ROC array, metric JSON, retained-utility table, or verifier output is public. |
| Mechanism delta | Pass as related context. RAPTA and ADMCD are distinct prompt-augmentation / multimodal-copy-detection mechanisms, not another LoRA-weight BAF, GUARD attention mitigation, denoising-loss, CLIP/pixel, CommonCanvas, MIDST, or SecMI repeat. |
| Consumer fit | Fail for current admission. Copying / memorization mitigation would need a reviewed consumer boundary with pre/post copying metrics before Platform/Runtime can consume it. |
| Download justification | Fail. The visible public surface is enough to close this cycle; execution would require source/PDF interpretation, target training assets, generated images, and metric reconstruction. |
| GPU release | Fail. No public row-bound score packet or verifier exists. |

## Decision

`paper-source-only copying / memorization mitigation watch / no official code /
no score artifacts / no download / no GPU release / no admitted row`.

RAPTA / ADMCD is relevant related work because it addresses memorization and
copying in text-to-image diffusion, but it is not a DiffAudit execution target.
The public surface exposes paper metadata and source availability only. It does
not ship official code, target identities, immutable row manifests, generated
response packets, per-row ADMCD scores, ROC arrays, metric JSON, retained-utility
artifacts, or a no-training verifier.

Smallest valid reopen condition:

- Official public code or an immutable artifact repository;
- Checkpoint-bound target and defended/undefended identities with sizes and
  hashes;
- Immutable copied/non-copied or member/nonmember row manifest;
- Generated image or internal-score packets bound to those identities;
- Pre/post RAPTA / ADMCD score rows, ROC arrays, metric JSON, and retained
  utility / prompt-alignment metrics; and
- A bounded verifier command that reads those artifacts without training,
  downloading large datasets, or rerunning image generation.

Stop condition:

- Do not download the arXiv source tarball, PDF, generated images, training
  data, detector assets, Stable Diffusion weights, checkpoints, or any inferred
  code archive in this cycle.
- Do not implement RAPTA or ADMCD from the paper, train/fine-tune targets, run
  object detection, generate images, fit copy detectors, or launch CPU/GPU
  sidecars.
- Do not promote RAPTA / ADMCD into Platform/Runtime rows until public
  row-bound pre/post copying or memorization artifacts and a reviewed
  copying/memorization consumer boundary exist.

## Platform and Runtime Impact

None. RAPTA / ADMCD remains Research-only copying / memorization mitigation
watch evidence. Platform and Runtime should continue consuming only the admitted
`recon / PIA baseline / PIA defended / GSA / DPDM W-1` set.
