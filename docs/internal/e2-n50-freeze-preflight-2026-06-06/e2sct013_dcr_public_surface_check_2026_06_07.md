# E2SCT-013 DCR Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-013` expose pointwise membership evidence, or is it a copying /
replication surface that weak caption-manifest or metric-code rules could
over-promote?

## Checked Public Surface

No caption manifest, generated image, training data, checkpoint, embedding
index, model, or metric output was downloaded. The check used GitHub metadata,
file listings, README text, and the public file-size/hash metadata for one
caption manifest.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/somepago/DCR` |
| GitHub head | `refs/heads/main = bac8b5fbf739c75be6a187f97e2b81e0fd51115c` |
| GitHub tree | Recursive tree was observed as `28` entries and `truncated=false`. |
| Visible files | `diff_train.py`, `diff_inference.py`, `diff_retrieval.py`, `metrics/`, `embedding_search/`, and `miscdata/laion_combined_captions.json`. |
| README | Gives training, inference, retrieval, and metric-computation commands. Metrics are logged to W&B; the LAION-10k split is linked through Google Drive. |
| Caption manifest | `miscdata/laion_combined_captions.json` is visible with size `9,969,183` bytes and SHA `669a197c527f5856997bd8d7e373374063fe12d8`. |

## Finding

`E2SCT-013` is useful for a semantic false-promotion baseline because it has
code, copying/retrieval metrics, and a visible caption manifest. A weak rule
could mistake those public surfaces for pointwise membership evidence.

The public surface still lacks the DiffAudit response/score contract:

- no member/nonmember MIA row labels were found;
- no public row-bound membership score packet was found;
- no ROC arrays, metric JSON, or no-training verifier were found;
- generated data, training data, checkpoints, and W&B metric outputs are
  runtime products or external payloads;
- the consumer question is copying / replication detection, not per-sample
  membership audit.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Public repo and caption manifest exist, but no fixed membership-audit target is bound to a score packet. |
| Split identity | `Fail` | A training-data path and LAION split link are not immutable member/nonmember MIA labels. |
| Score or response | `Fail` | No row-bound membership scores or generated response packet were found. |
| Metric provenance | `Partial` | Copying/retrieval metric code is public, but no membership metric packet is public. |
| Provenance | `Partial` | GitHub metadata is public; W&B outputs and linked data are outside the no-download surface. |
| Consumer/delta | `Fail` | Copying/replication evidence cannot be promoted to per-sample MIA evidence. |

## Decision

`copying_vs_membership_false_promotion / no_response_score_contract /
no_compute_release`.

Do not count `E2SCT-013` as admitted evidence, a response/score asset, or an
external-audit denominator row. Keep it as a copying-context false-promotion
exemplar.

Allowed wording:

`DCR exposes public copying/retrieval code and a caption manifest, but no public
member/nonmember MIA labels, row-bound membership scores, ROC arrays, metric
JSON, or verifier were found; it is a copying-vs-membership false-promotion
exemplar, not admitted response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` unless a public row-bound membership score
packet appears.

## Reopen Condition

Reopen only if a compact public manifest appears that binds target identity,
member/nonmember rows, row-bound membership scores or responses, metric
provenance, ROC/TPR recomputation, and a verifier. Do not download LAION split
payloads, caption JSON, generated images, checkpoints, embedding indices, or
run training/inference/retrieval for this gate.
