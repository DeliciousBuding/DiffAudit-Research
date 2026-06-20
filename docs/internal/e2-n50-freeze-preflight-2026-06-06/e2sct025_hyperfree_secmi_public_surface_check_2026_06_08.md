# E2SCT-025 Hyperparameter-Free SecMI Public-Surface Check

> Date: 2026-06-08
> Mode: no-download raw-file/HTML metadata check
> Decision: support-only / third-party SecMI-family code-report surface; not C14; not admitted; not external denominator; no_compute_release

## Scope

This check closes the current E2 public-surface pass for `E2SCT-025`
Hyperparameter-Free SecMI reproduction. It uses `git ls-remote`, raw GitHub
files, the GitHub HTML page, and the existing local evidence card. It does not
clone the repository, download CIFAR, download official SecMI SharePoint
checkpoints, fetch caches/plots/notebooks beyond small raw text sampling, train
attackers, or run code.

Sources checked:

- `https://github.com/mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models`
- `https://raw.githubusercontent.com/mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models/main/README.md`
- Raw small files under `main`: `.gitignore`, `run.py`, `secmia_mia/config.py`,
  `secmia_mia/download.py`, `secmia_mia/data.py`, `secmia_mia/secmi_features.py`,
  `secmia_mia/attackers.py`, and `docs/README.md`
- `docs/evidence/hyperfree-secmi-reproduction-gate-20260515.md`

## Findings

| Surface | Current finding |
| --- | --- |
| Repository identity | `git ls-remote` returned `3a8855cb54bbff9d15fb19e734b2feadd0cb12bb` for both `HEAD` and `refs/heads/main`. GitHub REST API remained unauthenticated-rate-limited in this pass, so the check used raw-file and HTML fallback surfaces. |
| README | Raw README status was `200`, length `11717`, SHA-256 `a05d928357f2544a1a454cdb35f022308f94eee4ddd96121276ad6ca8abef060`. It reports CIFAR-100 seed-0 aggregate metrics: baseline SecMINNs `AUC = 0.971`, `TPR@1%FPR = 0.519`, and hyperparameter-free SecMI `AUC = 0.984`, `TPR@1%FPR = 0.642`. |
| Source sampling | Raw source files are public. `run.py` contains train/full/robustness workflows and AUC/TPR/ROC logic; `config.py` refers to `SecMI_official`; `download.py` refers to SharePoint checkpoint download; `data.py` uses CIFAR download and official split files; `attackers.py` and `secmi_features.py` create local caches/features. |
| Ignored runtime outputs | `.gitignore` excludes caches, checkpoints, `SecMI_official`, data, and plots. The README also says not to commit generated assets such as `SecMI_official/`, `checkpoints_official/`, `data/`, `plots/`, and `cache_*`. |
| Existing evidence card | The May 2026 gate already classified the repo as a third-party SecMI-family code/report surface with no reusable score packet, no download, no GPU release, and no admitted row. This current check confirms that the public surface has not changed in a way that clears the row-bound packet blocker. |

## Interpretation

`E2SCT-025` has real weak-rule pressure. A paper/report-link rule,
code-availability rule, or aggregate-metric rule could over-promote it because
the README and report surface describe strong AUC/TPR results and provide
runnable code. DiffAudit still blocks the row because the public surface is a
same-family SecMI reproduction workflow rather than a row-bound replay packet:

- no public per-sample score rows;
- no ROC arrays;
- no metric JSON;
- no trained attacker weights;
- no generated response packet;
- no no-training verifier;
- no independent non-adjacent response/score asset;
- no Platform/Runtime consumer-boundary decision for third-party SecMI-family
  support rows.

The blocker is not compute availability. Running this repository would require
cloning or using official SecMI assets, downloading official checkpoints,
downloading CIFAR data, generating caches/error maps, and training/evaluating
attackers from scratch. That would reproduce a same-family support workflow
without creating a public immutable score packet.

## Decision

`support_only_third_party_secmi_family_code_report_surface /
row_bound_score_metric_packet_missing / duplicate_secmi_family_support /
no_compute_release`.

Do not count `E2SCT-025` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, second independent response/score asset,
completed external adjudication, reviewer reliability evidence, or compute
release. Keep it as support-only SecMI-family code/report evidence and as an
anti-duplication closure for the current E2 search.

Do not clone the full repository. Do not download CIFAR-10/CIFAR-100, official
SecMI SharePoint checkpoints, SecMI clone assets, generated caches, notebooks,
or plot payloads. Do not run `python run.py train`, `python run.py full`,
robustness runs, notebook cells, attacker training, CPU sidecars, GPU/DCU jobs,
or Platform/Runtime schema work from this gate.

Reopen only if public per-sample score rows with row/split identity, ROC arrays
or metric JSON, trained attacker weights or a no-training verifier, and a
consumer-boundary review for third-party SecMI-family packets appear.
