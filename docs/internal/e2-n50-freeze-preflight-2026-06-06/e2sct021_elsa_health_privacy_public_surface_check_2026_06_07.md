# E2SCT-021 ELSA Health Privacy Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-021` expose public target labels, challenge predictions, Noisy
Diffusion synthetic datasets, score rows, metric JSON/CSV, or a verifier that
can make it a current E2 denominator row?

## Checked Public Surface

No platform registration, data agreement, challenge dataset, release asset,
ZIP payload, medical data, model, generated data, submission packet, or
participant artifact was downloaded. The check used public README/config pages,
GitHub HTML, and the prior Research evidence gate:
[`docs/evidence/elsa-health-privacy-challenge-gate-20260515.md`](../../evidence/elsa-health-privacy-challenge-gate-20260515.md).

| Surface | Observation |
| --- | --- |
| Starter repo | `https://github.com/PMBio/Health-Privacy-Challenge` |
| Root README | Describes a CAMDA 2026 / ELSA Health Privacy starter package with baseline generative methods and MIA algorithms. It says datasets are available on the ELSA benchmark platform after registration and a data download agreement. |
| Track I | Bulk RNA-seq blue-team / red-team setting. Red teams run membership inference attacks against baseline and blue-team synthetic-data solutions. |
| Track II | Single-cell RNA-seq donor-level privacy setting with donor-level score aggregation. |
| Data README | Describes TCGA-BRCA `1089 x 978` and TCGA-COMBINED `4323 x 978` preprocessed RNA-seq datasets and points users to the ELSA platform for downloads. |
| Track I red-team README | Lists MC, LOGAN, GAN-Leaks, calibrated GAN-Leaks, DOMIAS KDE, Confidence LR, and Confidence RF. It evaluates accuracy, AUC, AUPR, and TPR at FPR `0.01` and `0.1`. |
| Public example packet | The public starter exposes `running_baseline_example.zip`; the prior evidence gate recomputed a public example with `1089` candidate rows and AUC `0.565453`. |
| Track I blue-team config | Includes multivariate, CVAE, DP-CVAE, CTGAN, CVAE-GMM, WGAN-GP, and DP-CTGAN generator settings. |
| Track II privacy config | Uses `onek1k`, membership labels, and `sc_domias_baselines` for a Poisson subset example. |

## Finding

`E2SCT-021` is a gated-benchmark false-promotion exemplar. It is stronger than
a paper-only row because the public starter package contains baseline MIA code,
example labels/predictions, and a real metric contract. A weak starter-packet
or metric-code rule could over-promote it as current evidence.

DiffAudit still blocks the row for the current image-diffusion E2 denominator:

- actual challenge datasets are behind registration and a data download
  agreement;
- real challenge labels, predictions, target metadata, and participant outputs
  are not public E2 artifacts;
- the public example packet is a starter sanity check, not an actual Noisy
  Diffusion challenge result;
- the domain is biomedical tabular / single-cell synthetic data, not current
  image/latent-image diffusion evidence.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / model identity | `Fail` | Public docs name benchmark tracks and generator families, but actual target datasets and participant outputs are platform-gated. |
| Split identity | `Partial` | Public example labels exist; real challenge split/label artifacts require platform access or submissions. |
| Score or response | `Fail` | Public examples can be scored, but real challenge predictions and target packets are not public E2 artifacts. |
| Metric provenance | `Partial` | Metric definitions and example recomputation exist, but not for public real challenge targets. |
| Provenance | `Partial` | Starter repo and example packet are public; evidence-bearing challenge artifacts are gated. |
| Consumer/delta | `Fail` | Biomedical tabular/single-cell benchmark context needs a separate consumer boundary and cannot be pooled into the current image-diffusion denominator. |

## Decision

`gated_benchmark_false_promotion_exemplar / public_starter_metric_contract /
real_targets_gated / no_compute_release`.

Do not count `E2SCT-021` as admitted evidence, a response/score asset, an
image-diffusion denominator row, or an external-audit denominator row. Keep it
as a false-promotion exemplar candidate for the measurement route: public
starter code and example metrics are not enough when the actual challenge
target data, labels, predictions, and metadata are gated.

Allowed wording:

`ELSA Health Privacy exposes a public biomedical synthetic-data starter package
with MIA baseline code, example labels/predictions, and a metric contract, but
the actual challenge datasets, labels, predictions, Noisy Diffusion targets,
and participant artifacts are platform-gated or submission-bound. It is a
gated-benchmark false-promotion exemplar, not current image-diffusion E2
denominator or admitted response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `metric_code_split_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` unless public real-challenge score rows
or predictions appear outside starter examples.

## Reopen Condition

Reopen only if DiffAudit explicitly opens a biomedical/tabular synthetic-data
consumer boundary, or if public-safe real challenge target/split/score artifacts
appear without platform registration, a data agreement, participant submission
access, or medical-data download.

Do not register for the platform, accept agreements, download TCGA / OneK1K /
challenge datasets, download starter ZIP payloads, regenerate synthetic data,
run red-team attacks, launch CPU/GPU sidecars, or promote ELSA into
Platform/Runtime rows from this gate.
