# E2Q-020 LAION-MI Dataset-Surface Follow-Up

> Date: 2026-06-08  
> Mode: Hugging Face dataset API + Dataset Viewer first-row API + arXiv API; no parquet/body download  
> Decision: L1 split-artifact support only; not a second public score/response asset; no compute release

## Scope

This follow-up rechecks the current public surface for LAION-MI from:

`Towards More Realistic Membership Inference Attacks on Large Diffusion Models`
(`arXiv:2306.12983`).

It covers the duplicated preflight entries `E2Q-016` and `E2Q-020`. `E2Q-020`
is the stronger artifact row because it points to the Hugging Face dataset
surface (`antoniaaa/laion_mi`) rather than only to arXiv metadata.

No parquet body, image payload, Stable Diffusion weight, generated response,
score packet, or GPU/DCU job was downloaded or run.

Sources checked:

- `https://huggingface.co/datasets/antoniaaa/laion_mi`
- `https://huggingface.co/api/datasets/antoniaaa/laion_mi`
- `https://huggingface.co/api/datasets/antoniaaa/laion_mi/tree/main?recursive=true`
- `https://datasets-server.huggingface.co/splits?dataset=antoniaaa/laion_mi`
- `https://datasets-server.huggingface.co/first-rows?dataset=antoniaaa/laion_mi&config=default&split=members`
- `https://datasets-server.huggingface.co/first-rows?dataset=antoniaaa/laion_mi&config=default&split=nonmembers`
- `https://export.arxiv.org/api/query?id_list=2306.12983`

## Current Public Surface

Hugging Face dataset API currently reports:

| Field | Current observation |
| --- | --- |
| dataset id | `antoniaaa/laion_mi` |
| repo SHA | `194fe331b99016a85381d9d9d20a65b3edbd76c9` |
| last modified | `2023-07-13T10:00:28Z` |
| gated/private/disabled | `false / false / false` |
| task/tag surface | `text-to-image`, `membership`, `latent diffusion`, `arxiv:2306.12983` |
| features | `url`, `caption` |
| splits | `members`, `nonmembers` |
| member rows | `13,396` |
| nonmember rows | `26,874` |
| download size | `5,044,720` bytes |
| dataset size | `6,588,117` bytes |

The current repo tree exposes only:

| Path | Current observation |
| --- | --- |
| `README.md` | dataset card, `1,254` bytes |
| `data/members-00000-of-00001-fca6668d831b14d2.parquet` | LFS object size `1,674,882`; LFS SHA-256 `2c25579bf52328625e6e6b35692a8340f3e84bfd70ece6b269f02dadf26db8d2` |
| `data/nonmembers-00000-of-00001-5513038636e047f1.parquet` | LFS object size `3,369,838`; LFS SHA-256 `88c110384229b4d85661bef76bfbe3c5a3668aa40071163a1c83e098ddcf7446` |

Dataset Viewer first-row API confirms the split schema: rows expose only
`url` and `caption`, with integer `row_idx` assigned by the viewer. It does not
expose a score, response id, generated image id, target checkpoint id, ROC row,
metric record, or verifier output.

The arXiv API currently resolves `2306.12983` to version `v2`, updated
`2023-11-16T14:57:58Z`, with the same title.

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | The paper is about Stable Diffusion and the HF dataset card links the paper, but the dataset repo itself does not publish an immutable target checkpoint hash. | `Partial` |
| Split semantics | Public `members` and `nonmembers` split files exist, with explicit URL/caption rows. | `Pass` |
| Score/response coverage | No score rows, generated responses, ROC arrays, metric JSON, or verifier artifacts are in the current repo tree or dataset API surface. | `Fail` |
| Metric provenance | The dataset card and paper describe an evaluation setup, but the current dataset package does not include a metric replay packet. | `Fail` |
| Semantic boundary | The row is directly about image-diffusion membership inference. | `Pass` |
| Consumer/delta boundary | There is no downstream audit packet or surface-delta control. | `Fail` |

## Decision

`L1 split-artifact support only /
row_bound_score_response_packet_missing / no_compute_release`.

LAION-MI remains useful for Direction C and for the false-promotion thesis:
it exposes an unusually clean public member/nonmember split, and weak
artifact-availability rules could over-promote it. The evidence contract still
blocks admission because no public score/response packet, metric JSON/ROC
artifact, target checkpoint hash, or no-training verifier is published.

Do not count `E2Q-016` or `E2Q-020` as a second public response/score asset,
N50 denominator row, admitted evidence, C14 extension, reviewer-reliability
evidence, prevalence evidence, or compute-release target.

Reopen only if the authors publish at least one compact artifact surface:

- immutable target checkpoint/model identity;
- row-bound score or generated response packet tied to the public split rows;
- ROC/metric JSON or a no-training verifier command;
- label-shuffle/permutation or surface-delta control packet; or
- a small manifest that certifies row ids beyond Dataset Viewer ordering.
