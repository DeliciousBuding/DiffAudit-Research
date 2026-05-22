# Broken Memories Artifact Gate

> Date: 2026-05-23
> Status: memorization detection/mitigation semantic-shift watch / paper-source-only / no official code / no score artifacts / no download / no GPU release / no admitted row

## Question

Does arXiv `2605.22050` /
`Broken Memories: Detecting and Mitigating Memorization in Diffusion Models with Degraded Generations`
expose a public DiffAudit-ready target, split, score packet, mitigation
packet, or verifier that should change the active Research slots?

This was selected as a single Lane A metadata gate because it is a fresh
Stable Diffusion memorization detection/mitigation paper with very strong
reported numbers. The check used arXiv API metadata, arXiv HTML text, arXiv
source `HEAD` metadata, GitHub repository search, and GitHub code search. It
did not download the arXiv source tarball, Stable Diffusion weights, LAION
prompts or images, Webster memorized-image assets, generated images, or
baseline repositories.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Broken Memories: Detecting and Mitigating Memorization in Diffusion Models with Degraded Generations` |
| arXiv | `https://arxiv.org/abs/2605.22050v1` |
| Published / updated | `2026-05-21T06:36:59Z` / `2026-05-21T06:36:59Z` |
| Authors | Yuanmin Huang; Mi Zhang; Chen Chen; Feifei Li; Geng Hong; Xiaoyu You; Min Yang |
| Venue note | `KDD 2026, extended version` |
| Primary category | `cs.CV` |
| Official code | none found in arXiv metadata, exact-title GitHub repository search, arXiv-id repository search, or exact-title/code search |
| arXiv source surface | `HEAD https://arxiv.org/e-print/2605.22050` returned `200`, `Content-Type: application/gzip`, `Content-Length: 24,383,310`, `Last-Modified: Fri, 22 May 2026 00:48:00 GMT`, and `ETag: "sha256:e860fea66b3b44ecaa80f001c8443740443711151958005fe11ae82ec1d70c9d"` |

The arXiv HTML is enough to classify the public surface without downloading
the `24.38` MB source package. It reports Stable Diffusion `1.4` experiments
with `AUC > 0.999`, a post-mitigation memorization rate of `0.0%`, and about
`0.01` seconds overhead per image. The evaluation uses `500` memorized prompts
from known duplicated LAION images constructed by Webster, `500`
non-memorized evaluation prompts from Lexica, COCO-2017 validation captions,
and GPT-4 construction, plus `50` reference prompts sampled from a `500` prompt
LAION-400M reference pool for stability-region estimation. The mitigation
section also evaluates pretrained SD `1.4` and SD `1.4` fine-tuned on a LAION
subset with `200` duplicated points and `120,000` distinct points, following a
prior memorization setup.

No official Broken Memories repository, score packet, prompt manifest,
generated image packet, mitigation trace, ROC array, metric JSON, or ready
verifier was found in the checked public metadata. GitHub searches for the
exact title, `2605.22050`, and title-plus-`Diffusion Models` code strings
returned no official repository or code hits.

## Claim Boundary

The paper is relevant privacy evidence because it targets memorized
generations in Stable Diffusion and reports strong detection and mitigation
numbers. The mechanism observes internal denoising instability, not another
raw reconstruction-loss repeat.

The boundary still does not match the current DiffAudit admitted row contract.
The paper evaluates prompt-level memorized-generation detection and online
mitigation; DiffAudit's current consumer contract is row-bound per-sample
membership evidence with immutable target identity, member/nonmember split,
query/response or score coverage, and replayable metric artifacts. The public
surface is paper-source-only: the checked metadata does not expose the prompt
rows, generated images, internal norm traces, score arrays, ROC arrays,
mitigation decisions, or verifier outputs needed to consume the result without
reimplementing the paper.

## Gate Result

| Gate | Result |
| --- | --- |
| Current image/latent-image fit | Partial. The target model family is Stable Diffusion, but the claim is memorized-generation detection/mitigation rather than current row-bound membership inference. |
| Target identity | Fail for replay. SD `1.4` is named, but no paper-bound model hash, scheduler/config manifest, or fine-tuned checkpoint identity packet is public. |
| Exact member split | Fail. Memorized prompts are described via Webster duplicated-image prompts, but no immutable prompt/image row manifest is public in the checked surface. |
| Exact nonmember split | Fail. Evaluation and reference prompt sources are described, but no exact nonmember prompt manifest is public. |
| Query/response or score coverage | Fail. No generated image packet, latent/update-norm trace, per-prompt detection score, ROC array, metric JSON, mitigation decision file, or verifier is public. |
| Mechanism delta | Pass as watch. The degraded-generation/internal-instability signal is non-duplicate and useful to monitor. |
| Download justification | Fail. Reproduction would require Stable Diffusion assets, LAION/Webster prompt/image setup, generated outputs, and likely baseline code reconstruction without a public replay packet. |
| GPU release | Fail. The blocker is missing public row-bound artifacts and consumer-boundary mismatch, not local compute. |

## Decision

`memorization detection/mitigation semantic-shift watch / paper-source-only /
no official code / no score artifacts / no download / no GPU release / no
admitted row`.

Keep Broken Memories as Research-only memorization watch evidence. It is useful
for tracking stronger memorized-generation detection mechanisms, but it does
not reopen the current Lane A asset path and does not justify Stable Diffusion
weight downloads, LAION/Webster asset acquisition, arXiv source download,
implementation-from-paper, baseline reconstruction, CPU sidecars, or GPU
release.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after Broken Memories artifact gate`.

Smallest valid reopen condition:

- authors publish official code plus compact prompt/image manifests, model and
  scheduler identity, generated image packets, internal trace or score files,
  ROC/metric JSON, mitigation-decision artifacts, and a no-training verifier;
  or
- DiffAudit explicitly opens a memorized-generation detection/mitigation
  consumer boundary separate from current per-sample membership rows.

Stop condition:

- Do not download the `24,383,310` byte arXiv source tarball from this gate.
- Do not download Stable Diffusion weights, fine-tuned checkpoints, LAION
  prompts/images, Webster memorized-image assets, generated image packets, or
  baseline repositories from this gate.
- Do not implement the latent update-norm detector, mitigation thresholds, or
  baseline comparisons from the paper in this cycle.
- Do not add Platform/Runtime rows, schemas, product copy, or recommendation
  logic until row-bound public artifacts or a reviewed memorization consumer
  boundary exists.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
