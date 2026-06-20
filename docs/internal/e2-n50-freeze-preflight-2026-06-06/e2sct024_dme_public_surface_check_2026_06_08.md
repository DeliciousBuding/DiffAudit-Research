# E2SCT-024 DME Public-Surface Check

> Date: 2026-06-08
> Mode: no-download GitHub branch / raw README / HTML metadata check
> Decision: official-repo-stub false-promotion exemplar only; not admitted; not external denominator; no_compute_release

## Scope

This check closes the current E2 public-surface pass for `E2SCT-024`
DME / Dual-Model with Entropy Augmentation. It uses `git ls-remote`, the raw
GitHub README, the GitHub HTML page, and the existing local evidence card. It
does not clone the repository, download datasets, download checkpoints, infer
missing paper details, implement DME from the README description, train dual
models, run CPU/GPU sidecars, or change Platform/Runtime rows.

Sources checked:

- `https://github.com/F-YaNG1/DME`
- `https://raw.githubusercontent.com/F-YaNG1/DME/main/README.md`
- `docs/evidence/dme-dual-model-entropy-artifact-gate-20260515.md`

## Findings

| Surface | Current finding |
| --- | --- |
| Repository identity | `git ls-remote` returned `ae0cc48476746945720bf24b42d4f9dfecb6de31` for both `HEAD` and `refs/heads/main`; no tag refs were returned. |
| GitHub HTML | HTML status was `200`; the page contains `1 Commit`, `No releases published`, and `README.md`. |
| README | Raw README status was `200`, length `248`, SHA-256 `b0d1cf04d92d47577a830e6d57477d10d3909ee138ef10b7dea6ed02ecedd225`. It describes DME as the official PyTorch implementation of a dual-model entropy-augmentation module for reducing complexity-induced bias in diffusion-model membership inference. |
| Existing evidence card | The May 2026 gate already classified DME as `stub-repo-only / complexity-bias MIA watch / no download / no GPU release / no admitted row`. The current public check confirms the same blocker. |

## Interpretation

`E2SCT-024` is a clean weak-rule stress row because an official repository exists
and its README claims an implementation. A code-availability shortcut could
over-promote the row even though the current repository is a README-only stub.
DiffAudit blocks it because the evidence-bearing surfaces are absent:

- no implementation code beyond README;
- no linked paper or formal metric table;
- no immutable member/nonmember split manifest;
- no target diffusion checkpoint or model hash;
- no generated response or feature cache;
- no per-sample score rows;
- no ROC arrays or metric JSON/CSV;
- no no-training verifier.

The blocker is not compute availability. Running or reimplementing DME would
turn a placeholder repository into a new local research project, not a public
row-bound audit packet.

## Decision

`official_repo_stub_false_promotion_exemplar /
row_bound_score_response_metric_packet_missing / no_compute_release`.

Count `E2SCT-024` only as a selected false-promotion stress row for weak-rule
analysis. Do not count it as admitted evidence, response/score evidence, N50
external denominator evidence, completed external adjudication, reviewer
reliability evidence, Platform/Runtime evidence, or compute release.

Do not clone the repository. Do not infer missing paper details from the README
description. Do not download datasets, model weights, checkpoints, generated
images, or result payloads. Do not implement DME, train dual models, launch CPU
sidecars, launch GPU/DCU jobs, or promote DME into Platform/Runtime rows from
this gate.

Reopen only if public implementation code plus a paper-bound protocol and
frozen target/split/score-or-response/metric artifacts or a no-training verifier
appear.
