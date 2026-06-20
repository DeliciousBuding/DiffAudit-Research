# E2SCT-030 Frequency Components / FMIA Public-Surface Recheck

> Date: 2026-06-08
> Mode: current OpenReview API + attachment HEAD recheck, no archive body download
> Decision: support-only code-and-split-manifest watch-plus; not C14; not admitted; not denominator; no_compute_release

## Scope

This recheck revisits the OpenReview submission:

`Unveiling Impact of Frequency Components on Membership Inference Attacks for Diffusion Models`
(`p9uryyZ5bw`).

The trigger was the current E1/E2 search for a second row-bound public
score/response asset. This is a current-date recheck of the older FMIA scout
surface, not a new independent public-surface candidate. A prior local evidence
card already inspected the small OpenReview supplement in May 2026:
[`../../evidence/fmia-openreview-frequency-artifact-gate-20260515.md`](../../evidence/fmia-openreview-frequency-artifact-gate-20260515.md).

This 2026-06-08 pass does not download the ZIP body, datasets, checkpoints,
generated samples, score arrays, or model weights. It reads only OpenReview
metadata and attachment headers, then compares those public-surface facts with
the prior local inventory.

Sources checked:

- `https://openreview.net/forum?id=p9uryyZ5bw`
- `https://api2.openreview.net/notes?id=p9uryyZ5bw`
- `https://openreview.net/attachment?id=p9uryyZ5bw&name=supplementary_material`
- prior local evidence card:
  `docs/evidence/fmia-openreview-frequency-artifact-gate-20260515.md`

## Current Public Surface

OpenReview API currently reports:

| Field | Current observation |
| --- | --- |
| title | `Unveiling Impact of Frequency Components on Membership Inference Attacks for Diffusion Models` |
| id / forum | `p9uryyZ5bw` |
| version | `2` |
| venue | `Submitted to ICLR 2026` |
| venueid | `ICLR.cc/2026/Conference/Rejected_Submission` |
| license | `CC BY 4.0` |
| modified time | `2026-02-11T10:13:54.261Z` |
| PDF path | `/pdf/ce1ad6bcfcad7d1fa73461ed6a7e8ec817067b88.pdf` |
| supplementary path | `/attachment/74aa19564760102160f5bbd2d8691d92abf825cc.zip` |

The attachment metadata recheck returned:

| Field | Current observation |
| --- | --- |
| status | `200` |
| content type | `application/zip` |
| content length | `1,783,018` bytes |
| filename | `3274_Unveiling_Impact_of_Frequ_Supplementary Material.zip` |

The current HEAD result is metadata only. It matches the prior local evidence
card's recorded supplement size and filename, but it does not certify that the
current ZIP body has the same SHA-256 or entry inventory.

## Prior Local Inventory

The prior evidence card recorded a bounded 2026-05-23 ZIP inspection:

| Surface | Prior local finding |
| --- | --- |
| ZIP SHA-256 | `567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045` |
| ZIP entries | `79` |
| uncompressed size | `5,117,651` bytes |
| code root | `FMIA/` |
| present artifacts | official DDIM / Stable Diffusion attack code, frequency filters, training code, and member split manifests |
| absent artifacts | checkpoints, generated samples, `pos_result.npy`, `neg_result.npy`, row-level score exports, ROC CSVs, metric JSON, and ready verifier |

The prior card also records split manifests for CIFAR10, CIFAR100,
STL10_Unlabeled, and TINY-IN, each exposing member/nonmember index arrays. That
is a useful method-support surface, but it is not a row-bound score/response
asset because the corresponding target checkpoints and ready score packets are
not public.

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | The note and code are public, but the target checkpoints/model directories are not packaged. | `Fail` |
| Split semantics | Prior ZIP inventory includes exact member split manifests. | `Partial` |
| Score/response coverage | No public ready score arrays, ROC/metric JSON, generated response packet, or verifier is visible from the prior inventory or current metadata. | `Fail` |
| Metric provenance | Metric/attack code exists, but replay would require local checkpoints/data and would generate fresh runtime outputs. | `Partial` |
| Semantic boundary | The paper is directly about membership inference attacks for diffusion models and frequency filtering. | `Pass` |
| Provenance/consumer boundary | Current public surface is code + split manifests, not a downstream audit packet. | `Fail` |

## Decision

`support-only code-and-split-manifest watch-plus /
row_bound_score_response_packet_missing / no_compute_release`.

FMIA/Frequency is a useful mechanism reference for Direction A because it shows
that a strong-looking public supplement can still fail the evidence contract:
code and split manifests are public, but the target checkpoints and score
packets that would bind claims to rows are absent.

Do not count `E2SCT-030` as a C14 false-promotion exemplar, current C14 row,
admitted evidence, external-denominator evidence, second public response/score
asset, reviewer reliability evidence, prevalence evidence, or compute release.

Do not download datasets, model weights, generated samples, or the ZIP body from
this current gate. Do not train DDIM targets, fine-tune Stable Diffusion, run
FMIA attacks, sweep filters/timesteps/attacker matrices, or launch GPU/DCU jobs.

Reopen only if the authors publish a compact current row-bound package:

- immutable target checkpoint or model identity;
- member/nonmember row manifest tied to public rows;
- public score arrays, generated response packets, ROC/metric JSON, or verifier;
- a no-training replay command with the above artifacts; or
- a new attachment whose body inventory changes enough to justify a bounded
  small-archive inspection.
