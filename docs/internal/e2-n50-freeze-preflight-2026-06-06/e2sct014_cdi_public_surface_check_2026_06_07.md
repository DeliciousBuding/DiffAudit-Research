# E2SCT-014 CDI Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-014` expose per-sample membership evidence, or is it a dataset-level
copyrighted-data identification surface that weak metric-code rules could
over-promote?

## Checked Public Surface

No ImageNet/COCO data, model artifact, extracted feature, score output, or
experiment result was downloaded. The check used GitHub metadata, file
listings, and README text.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/sprintml/copyrighted_data_identification` |
| GitHub head | `refs/heads/main = dcd62258b0b3fde05d52aaecfade3b5f4c09507a` |
| GitHub tree | Recursive tree was observed as `81` entries and `truncated=false`. |
| Visible configs | `conf/action/features_extraction.yaml`, `conf/action/scores_computation.yaml`, `conf/action/evaluation.yaml`, `conf/attack/cdi.yaml`, `pia.yaml`, `pian.yaml`, `secmi_stat.yaml`, and several model configs. |
| GitHub README | States that CDI is copyrighted data identification in diffusion models. It explicitly says membership inference attacks are not strong enough to reliably determine membership of individual images in large DMs, and proposes dataset inference. |
| Runtime dependencies | README instructs users to download ImageNet, COCO, and model artifacts, then run feature extraction, score computation, and evaluation scripts. |

## Finding

`E2SCT-014` is a clean semantic-boundary exemplar. It has code, attack configs,
metric/evaluation actions, and a strong public paper claim. A weak metric-code
rule could over-promote it to per-sample membership evidence.

The public surface still lacks the DiffAudit response/score contract:

- the consumer claim is dataset-level copyrighted-data identification, not
  per-sample membership inference;
- no public row-bound per-sample membership score packet was found;
- no public ROC arrays, metric JSON, feature packet, or no-training verifier
  was found;
- features and scores are produced by runtime scripts after downloading
  datasets and models.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Public repo and configs exist, but the target is a dataset-level CDI workflow rather than a per-sample membership audit row. |
| Split identity | `Fail` | Dataset-level owner/non-owner or benchmark setup is not a per-sample member/nonmember MIA split. |
| Score or response | `Fail` | No public row-bound per-sample membership score packet was found. |
| Metric provenance | `Partial` | Metric/evaluation code is public, but no frozen per-sample metric JSON/ROC/verifier packet is public. |
| Provenance | `Partial` | GitHub metadata is public; data/model/feature outputs are runtime products. |
| Consumer/delta | `Fail` | Dataset inference cannot be promoted to per-sample membership evidence. |

## Decision

`dataset_level_vs_per_sample_false_promotion / no_response_score_contract /
no_compute_release`.

Do not count `E2SCT-014` as admitted evidence, a response/score asset, or an
external-audit denominator row. Keep it as a dataset-level boundary
false-promotion exemplar.

Allowed wording:

`CDI exposes public code and metric/evaluation configs for dataset-level
copyrighted data identification, but no public row-bound per-sample membership
score packet, ROC arrays, metric JSON, feature packet, or verifier were found;
it is a dataset-level-vs-per-sample false-promotion exemplar, not admitted
response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `artifact_availability_would_promote` or `score_only_would_promote`
unless public frozen score/feature artifacts appear.

## Reopen Condition

Reopen only if a compact public packet appears that binds target identity,
per-sample member/nonmember row IDs, row-bound membership scores or responses,
metric provenance, ROC/TPR recomputation, and a verifier. Do not download
ImageNet/COCO data, model artifacts, extracted features, or score outputs for
this gate.
