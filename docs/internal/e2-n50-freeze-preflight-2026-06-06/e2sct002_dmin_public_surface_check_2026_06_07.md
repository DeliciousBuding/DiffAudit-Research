# E2SCT-002 DMin Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-002` expose a public pointwise membership-inference score or
response packet, or is it an attribution/influence surface that weak artifact
rules could over-promote?

## Checked Public Surface

No model payload, HF dataset shard, gradient cache tensor, image, checkpoint, or
generated output was downloaded. The check used public metadata, GitHub file
listings, README text, HF API metadata, and one small repo config file.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/huawei-lin/DMin` |
| GitHub head | `refs/heads/main = a550120a4d6b93dd7202a96e5bdcc61d9af9a787` |
| GitHub tree | Recursive tree was observed as `19` entries and `truncated=false`. |
| GitHub README | Describes DMin as scalable training-data influence estimation for diffusion models, with keywords `Influence Function`, `Influence Estimation`, and `Training Data Attribution`. |
| HF dataset | `huaweilin/DMin_mixed_datasets_8846`, SHA `89e8175bcffb920381dfe6fad694b7b1d4c384c1`, public and not gated, with `8847` train and `2212` test examples; API metadata reports about `10.2GB` download size and much larger stored parquet payload. |
| HF LoRA | `huaweilin/DMin_sd3_medium_lora_r4`, SHA `34b1031eab32beac905352a98a403b5c1e57b98b`, public and not gated, with LoRA weights and optimizer/scheduler state files. |
| HF cache | `huaweilin/DMin_sd3_medium_lora_r4_caching_8846`, SHA `6f1b82ea23bdb1687ccddb193840681620ef17f7`, public and not gated, with `K65536/loss_grad_*.pt` files and a reducer object; API metadata reports about `58GB` storage. |
| Config | `examples/sd3_medium_lora/config.json` names `train_data_path`, `test_data_path`, `model_name_or_path`, `lora_path`, `cache_path`, and `result_output_path = output_dir`. |

## Finding

`E2SCT-002` is an artifact-rich public surface, but the public claim is
training-data attribution / influence estimation, not pointwise membership
inference. A weak rule that treats train/test artifacts, LoRA weights, cached
gradients, or an output path as membership evidence would over-promote it.

The public surface still lacks the DiffAudit response/score contract:

- no public member/nonmember MIA label manifest was found;
- no row-bound membership score packet was found;
- no ROC arrays or metric JSON for a pointwise membership claim were found;
- no no-training verifier was found;
- the visible `output_dir` is a runtime destination, not a frozen score packet.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Repo, HF dataset, LoRA, and cache identities are public, but the consumer question is attribution/influence rather than membership audit. |
| Split identity | `Partial` | HF train/test examples are public in metadata, but not a member/nonmember MIA split for an audit claim. |
| Score or response | `Fail` | Public cache files are gradient/influence artifacts, not row-bound membership scores or responses. |
| Metric provenance | `Fail` | No public pointwise MIA metric JSON, ROC arrays, or verifier were found. |
| Provenance | `Partial` | Public repo/HF provenance exists, but the data/cache payloads are large and not part of this no-download gate. |
| Consumer/delta | `Fail` | The surface supports attribution/influence inspection only, not a per-sample membership audit result. |

## Decision

`attribution_vs_membership_false_promotion / no_response_score_contract /
no_compute_release`.

Do not count `E2SCT-002` as admitted evidence, a response/score asset, or an
external-audit denominator row. Keep it as a semantic false-promotion exemplar:
it can show why public train/test artifacts, LoRA weights, and cached gradients
do not automatically support a membership claim.

Allowed wording:

`DMin exposes public attribution/influence artifacts, including train/test
metadata, LoRA weights, and cached gradients, but no public row-bound
member/nonmember MIA score or verifier was found; it is an attribution-vs-
membership false-promotion exemplar, not admitted response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` unless a public pointwise membership
score packet appears.

## Reopen Condition

Reopen only if a compact public manifest appears that binds target identity,
member/nonmember row IDs, row-bound membership scores or responses, metric
provenance, ROC/TPR recomputation, and a verifier. Do not download HF parquet
shards, LoRA weights, gradient caches, SD3 weights, generated outputs, or
derived result directories for this gate.
