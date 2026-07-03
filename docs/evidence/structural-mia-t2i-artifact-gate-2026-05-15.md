# Structural MIA T2I Artifact Gate

> Date: 2026-05-15
> Status: paper-source-only structural T2I MIA watch / OpenReview supplement PDF-only / no code-score artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2407.13252` / `Unveiling Structural Memorization: Structural
Membership Inference Attack for Text-to-Image Diffusion Models` expose a
non-duplicate text-to-image diffusion MIA artifact that should change
DiffAudit's active execution slots or admitted Platform/Runtime boundary?

This gate was opened because the mechanism is structurally different from
pixel-loss, SecMI, PIA, CLiD likelihood, CopyMark benchmark-score, and
Rectified Flow vector-field routes. The check used arXiv API metadata, the
arXiv source tarball, exact-title GitHub repository/code searches, and the
OpenReview supplementary attachment. It did not download LAION/COCO image
payloads, Stable Diffusion or Latent Diffusion weights, generated images, or
run DDIM inversion / SSIM scoring.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Unveiling Structural Memorization: Structural Membership Inference Attack for Text-to-Image Diffusion Models` |
| arXiv | `https://arxiv.org/abs/2407.13252v1` |
| Published / updated | `2024-07-18T08:07:28Z` |
| OpenReview supplement | `https://openreview.net/attachment?id=GQkPMFUWVf&name=supplementary_material` |
| Supplement payload | `1,923,114` byte ZIP with one entry: `supplementary.pdf` (`2,016,750` bytes), no code/data/results files |
| arXiv source tarball | `4,327,174` bytes, `38` entries, TeX plus figure PDFs |
| GitHub exact-title search | No official repository found for exact title or `2407.13252`; code search found only unrelated paper-index metadata |

The public paper source contains rendered ROC/log-ROC figures and table values,
but no machine-readable score rows, ROC arrays, metric JSON, image manifests,
checkpoint hashes, generated response packets, or verifier.

## Mechanism Signal

The proposed attack uses structure-level memorization in text-to-image models.
Given an input image, it encodes the image into the T2I latent space, performs
DDIM inversion/noising, decodes the corrupted latent back to pixel space, and
uses structural similarity between the original and corrupted output as the
membership signal. The paper argues that member image structures are preserved
better than nonmember image structures during early diffusion steps.

This is mechanism-relevant because it is not another raw denoising-loss,
reverse-denoise distance, prompt likelihood, final-layer gradient, frequency
filter, or Flow Matching vector-field statistic. It is also closer to a
practical text-to-image model setting than small unconditional DDPM-only
probes.

## Reported Metrics

These are paper-source metrics read from the arXiv source, not locally
replayed.

| Target | Resolution | Method | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Latent Diffusion | `512x512` | Structural MIA | `0.930` | `0.860` | `0.575` | `0.245` |
| Latent Diffusion | `256x256` | Structural MIA | `0.841` | `0.763` | `0.368` | `0.173` |
| Stable Diffusion v1-1 | `512x512` | Structural MIA | `0.920` | `0.852` | `0.512` | `0.234` |
| Stable Diffusion v1-1 | `256x256` | Structural MIA | `0.811` | `0.750` | `0.302` | `0.107` |

The paper states that the hold-out set is `5,000` COCO2017-Val images; member
sets are randomly sampled from LAION-400M for Latent Diffusion and LAION2B-en
for Stable Diffusion v1-1. Those sample identities are described but not
released as public machine-readable manifests.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Partial. The paper names Latent Diffusion and Stable Diffusion v1-1, but no checkpoint hashes, exact model revisions, or executable target bundles are public. |
| Exact member split | Fail. The paper describes random LAION member sampling, but no immutable LAION member image IDs, URLs, captions, or split manifest are public. |
| Exact nonmember split | Partial/fail. COCO2017-Val is named as hold-out, but no exact row order, filtered image IDs, or evaluation manifest is public. |
| Query/response or score coverage | Fail. Public artifacts have tables and figure PDFs only, not score rows, ROC arrays, metric JSON, generated packets, or verifier output. |
| Mechanism delta | Pass for watch. Structure-level forward-diffusion SSIM is non-duplicate and relevant to T2I membership. |
| Download justification | Fail. Downloading LAION/COCO/model payloads or implementing SSIM scoring would not evaluate a released artifact; it would create a new reproduction. |
| GPU release | Fail. Missing public artifacts, not local compute, are the blocker. |

## Decision

`paper-source-only structural T2I MIA watch / OpenReview supplement PDF-only /
no code-score artifact / no download / no GPU release / no admitted row`.

Structural MIA should remain a Research-only watch item. It is a useful
mechanism reference because it attacks structural memorization in text-to-image
models and reports strong low-FPR table metrics. It is not an execution target
because the public surface lacks the concrete row identity and score artifacts
that DiffAudit needs for a bounded replay or product row.

Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and
`CPU sidecar = none selected after Structural MIA T2I artifact gate`.

Smallest valid reopen condition:

- authors publish official code plus exact LAION/COCO member/nonmember
  manifests, target model revisions or hashes, generated/corrupted response
  packets, score rows, ROC arrays, metric JSON, and a verifier; or
- an independent public artifact package exposes the same row-bound structural
  scores without requiring LAION crawling, Stable Diffusion downloads, or local
  reproduction from the paper.

Stop condition:

- Do not download LAION-400M, LAION2B-en, COCO2017-Val images, Stable
  Diffusion, Latent Diffusion, BLIP, generated images, or checkpoint payloads
  from this gate.
- Do not implement DDIM inversion, structure-level SSIM scoring, prompt
  variants, distortion robustness, or guidance-scale sweeps from the paper.
- Do not launch GPU work, add Platform/Runtime rows, change schemas, or change
  product copy until row-bound public artifacts exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
