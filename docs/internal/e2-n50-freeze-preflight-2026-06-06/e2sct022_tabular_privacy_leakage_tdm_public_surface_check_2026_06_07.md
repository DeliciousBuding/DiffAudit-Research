# E2SCT-022 Tabular Privacy Leakage TDM Public-Surface Check

> Date: 2026-06-07
> Mode: no-download metadata/raw-page check
> Decision: support-only / tabular-lane watch-plus; not C14; not admitted; not denominator; no_compute_release

## Scope

This check closes the first public-surface pass for `E2SCT-022` after the
post-C14 baseline. It uses only paper metadata, GitHub metadata, and small
raw text/config files. It does not clone the toolkit, download archives,
Google Drive resources, Berka/Diabetes data, checkpoints, generated synthetic
tables, challenge payloads, or run code.

Sources checked:

- `https://arxiv.org/abs/2605.06835`
- `https://export.arxiv.org/api/query?id_list=2605.06835`
- `https://github.com/VectorInstitute/midst-toolkit`
- `https://api.github.com/repos/VectorInstitute/midst-toolkit`
- `https://api.github.com/repos/VectorInstitute/midst-toolkit/git/refs/heads/main`
- `https://raw.githubusercontent.com/VectorInstitute/midst-toolkit/main/README.md`
- `https://raw.githubusercontent.com/VectorInstitute/midst-toolkit/main/examples/tartan_federer_attack/README.md`
- `https://raw.githubusercontent.com/VectorInstitute/midst-toolkit/main/examples/ensemble_attack/README.md`
- `https://raw.githubusercontent.com/VectorInstitute/midst-toolkit/main/examples/ept_attack/config.yaml`

## Findings

| Surface | Current finding |
| --- | --- |
| arXiv metadata | Public record `2605.06835` is v1, published/updated `2026-05-07`; Atom API status `200`, length `2950`, SHA-256 `84792f9705503f5da8bcd8e3aeca6270bac26b04e63c656e39b6baaace0b4875`. |
| GitHub repo | `VectorInstitute/midst-toolkit` is public. Repo API initially returned status `200`, length `12987`, SHA-256 `b08a92c8e5836558d0753ae1f020a08e1d13b595cbeb19aca87463299eb539a9`; later unauthenticated calls hit rate limit. |
| Main ref | GitHub main ref API initially returned status `200`, length `356`, SHA-256 `eab96d4556b01ba78650c0d30754ac68bb0f5537c0be2d15b1ce1164b3f7aecc`. |
| Toolkit README | Raw README status `200`, length `1983`, SHA-256 `ced52d8e52fa1e4b44c91290d42b8daac589ff45978bd641f6451ce3129fdb4f`. |
| Tartan Federer example | Raw README status `200`, length `1845`, SHA-256 `0480032d7fb402d15af4b41987cc27c3f3fb46e6171207b75c59d612a7b7ca2e`; the example surface has `6` target models and a TODO to train/upload `30` target models. |
| Ensemble example | Raw README status `200`, length `5369`, SHA-256 `72c9e55122e38516c14b3b70717e7714ab8f8d4b387d46d245eb903b16d9804b`. |
| EPT config | Raw `examples/ept_attack/config.yaml` status `200`, length `1397`, SHA-256 `781c4bbf27288a1d947abbf2abcd0d552dc23043e28e421a0310514431aeed3d`. |

## Interpretation

`E2SCT-022` creates useful false-promotion pressure: a paper-artifact-link rule,
code-availability rule, artifact-availability rule, or challenge-surface rule
could promote it because the paper points to an official public toolkit and the
toolkit has attack/example surfaces.

DiffAudit still blocks the row from C14 and N50 because the current public
surface does not expose a paper-bound Berka/Diabetes replay packet:

- no immutable paper split manifests;
- no target checkpoint identities or hashes for the paper experiments;
- no generated synthetic tables;
- no Tartan/Ensemble/EPT score rows;
- no ROC arrays;
- no metric JSON;
- no no-training verifier.

The remaining mismatch is partly a lane/boundary issue. The public toolkit may
be useful for tabular synthetic-data MIA support, but the current Direction A
paper contract still expects paper-bound target identity, exact
member/nonmember split, score/response coverage, metric packet, provenance, and
consumer fit.

## Decision

`support_only_tabular_lane_watch_plus / code_public_result_missing /
no_compute_release`.

Do not count `E2SCT-022` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, completed external adjudication, reviewer
reliability evidence, or compute release. It is no longer pending a first
public-surface look; keep it only as support-only / tabular-lane watch-plus.

Do not clone `midst-toolkit`. Do not download GitHub archives, Google Drive
MIDST resources, Berka/Diabetes data, checkpoints, synthetic tables, or
challenge payloads. Do not run ClavaDDPM, Tartan Federer, Ensemble, EPT,
metrics, validators, or local scripts.

Reopen only if public paper-bound target/split/score/ROC/metric/verifier
artifacts appear, or if DiffAudit makes an explicit tabular-lane consumer
boundary decision.
