# E2SCT-023 FERMI Public-Surface Check

> Date: 2026-06-07
> Mode: no-download metadata/page check
> Decision: paper-source-only / reported-metric support-only watch; not C14; not admitted; not denominator; no_compute_release

## Scope

This check closes the first public-surface pass for `E2SCT-023` after the
post-C14 queue. It uses only arXiv metadata/pages and public search surfaces. It
does not download arXiv source or PDF payloads, reconstruct datasets, train
tabular diffusion models, run attack code, or launch compute.

Sources checked:

- `https://export.arxiv.org/api/query?id_list=2605.11527`
- `https://arxiv.org/abs/2605.11527`
- `https://arxiv.org/html/2605.11527v1`
- public GitHub repository and code search for `FERMI` / `2605.11527`

## Findings

| Surface | Current finding |
| --- | --- |
| arXiv Atom metadata | Status `200`, length `2949`, SHA-256 `8ec292871e572236590fb3f1cc66f997c7a8214062201ee52cad2d337635a0cd`. The public paper identity is `FERMI: Exploiting Relations for Membership Inference Against Tabular Diffusion Models`. |
| arXiv abstract page | Status `200`, length `47380`, SHA-256 `460c0c8d1a357a4402fec52e3b8847ca799139cbf0972edad712ab09d03c4dd0`. |
| arXiv HTML page | Status `200`, length `385574`, SHA-256 `8a57aba58f2bf1641952447fb971979d0cce890d9b23644808c436565ed054bc`. The HTML surface exposes paper text and reported experimental tables. |
| Official artifacts | No official public code repository, data packet, Zenodo/OSF/Figshare artifact, Hugging Face artifact, score packet, ROC array, metric JSON, or verifier link was observed from the arXiv pages. GitHub searches for the paper identifier and title terms returned no matching official repository. |

## Interpretation

`E2SCT-023` creates useful support pressure because the paper reports
low-FPR tabular-diffusion MIA gains and has a readable arXiv HTML surface. A
weak paper-claim rule or reported-metric rule could overstate that surface.

DiffAudit still blocks C14 expansion:

- no official public implementation or artifact packet is visible;
- no hashable tabular target model or endpoint contract is public;
- no immutable member/nonmember table split manifest is public;
- no generated synthetic-table response packet is public;
- no row-bound FERMI score rows, ROC arrays, metric JSON, or verifier are
  public.

The row is also outside the current image-diffusion denominator. It can remain a
tabular-lane watch/support item, but the current public surface is not a clean
false-promotion exemplar for the paper-facing C14 object because it is
paper-reported only.

## Decision

`paper_source_only_reported_metric_support / tabular_lane_watch_plus /
no_compute_release`.

Do not count `E2SCT-023` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, completed external adjudication, reviewer
reliability evidence, or compute release. It is no longer pending a first
public-surface look; keep it only as paper-source-only / reported-metric
support.

Do not download arXiv source or PDF payloads. Do not reconstruct Berka,
Diabetes, or other tabular datasets. Do not run FERMI, Tabsyn, TabDDPM,
ClavaDDPM, relational-tabular training, score extraction, or local metrics.

Reopen only if the authors publish official public code plus paper-bound
target identity, exact member/nonmember split manifests, reusable score/ROC or
metric artifacts, and a no-training verifier, or if DiffAudit opens a separate
tabular-diffusion denominator with a consumer-boundary decision.
