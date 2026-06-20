# E2SCT-005 DIFFENCE Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-005` expose row-bound diffusion-generator membership evidence, or is
it a classifier-defense surface where diffusion is an input-side purifier that
weak code/artifact rules could over-promote?

## Checked Public Surface

No Google Drive model folder, CIFAR/SVHN payload, classifier checkpoint,
diffusion checkpoint, result directory, logits, score row, or Zenodo ZIP was
downloaded. The check used official public metadata, raw README/script files,
Zenodo record metadata, and `git ls-remote`.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/SPIN-UMass/Diffence` |
| GitHub head | `refs/heads/master = 2f7bb87dee863538f902098c84d0fe04ddfdcc3f` via `git ls-remote`. GitHub REST API was rate-limited in this turn. |
| GitHub README | States the repository contains code for NDSS 2025 "Diffence: Fencing Membership Privacy With Diffusion Models". It frames Diffence as a plug-and-play defense for membership privacy of undefended and defended models. |
| Diffusion dependency | README instructs users to download pretrained diffusion model checkpoints from Google Drive and copy `diff_models` into `cifar10/diff_defense/diff_models`. |
| Classifier dependency | README instructs users to download pretrained undefended/defended classifier models from Google Drive into `final-all-models`, e.g. `cifar10/final-all-models/resnet/selena.pth.tar`. |
| MIA evaluation script | `cifar10/evaluate_MIAs/evaluate_mia.sh` runs `parallel_run.py`, then `dist_attack.py` with and without `--diff`, and writes output under `./results`. |
| Data partition script | `cifar10/data_partition.py` downloads CIFAR-10 and partitions it locally. |
| Zenodo record | `https://zenodo.org/records/13706131` records DOI `10.5281/zenodo.13706131` with one `Diffence-master.zip` code snapshot, size `2,133,861`, checksum `md5:3535eb087cba81de655767510d4c2506`. |

## Finding

`E2SCT-005` is a clean consumer-boundary false-promotion exemplar. It is
scientifically relevant because the paper and code are about membership privacy
and diffusion models, but the audited target is a classifier-defense workflow:
diffusion is the purification/defense component, not the generative target whose
responses or scores are being audited as a diffusion generator.

A weak code/artifact rule could over-promote the row because the public surface
has official code, a Zenodo code snapshot, dataset partitioning, defense configs,
diffusion-model code, and MIA evaluation scripts. The DiffAudit contract still
blocks promotion:

- protected targets are undefended/defended classifiers, not diffusion
  generators;
- diffusion checkpoints and classifier checkpoints are external Google Drive
  runtime dependencies;
- result files are produced only after running `evaluate_mia.sh`;
- no public defended/undefended logits, MIA score rows, ROC arrays, metric JSON,
  response packet, or no-training verifier were observed in the no-download
  public surface.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Public repo, paper surface, and code snapshot exist, but the protected target is a classifier defense workflow. |
| Split identity | `Partial` | CIFAR-10 partitioning code exists, but split materialization is runtime-local and not a frozen score packet. |
| Score or response | `Fail` | No public defended/undefended logits, MIA score rows, response packet, or verifier was observed. |
| Metric provenance | `Partial` | MIA evaluation scripts are public, but metrics/results are generated after downloading external checkpoints and running code. |
| Provenance | `Partial` | Git head and Zenodo code snapshot are public; checkpoints/results remain external runtime products. |
| Consumer/delta | `Fail` | Classifier-defense membership privacy cannot be promoted to diffusion-generator response/score evidence. |

## Decision

`classifier_defense_consumer_boundary_false_promotion /
no_response_score_contract / no_compute_release`.

Do not count `E2SCT-005` as admitted evidence, a diffusion response/score asset,
or an external-audit denominator row. Keep it as a classifier-defense
consumer-boundary false-promotion exemplar.

Allowed wording:

`DIFFENCE exposes official code, a Zenodo code snapshot, diffusion-purifier
components, and MIA evaluation scripts for classifier membership privacy, but no
public defended/undefended logits, row-bound MIA score packet, ROC arrays,
metric JSON, response packet, or verifier were observed; it is a
classifier-defense consumer-boundary false-promotion exemplar, not admitted
diffusion-generator response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` unless public frozen score/logit/ROC
artifacts appear.

## Reopen Condition

Reopen only if a compact public packet appears that binds target identity,
member/nonmember row IDs, defended/undefended logits or MIA scores, ROC/TPR
metric provenance, checkpoint identities, and a verifier for a consumer boundary
DiffAudit intends to admit. Do not download Google Drive classifier/diffusion
checkpoints, CIFAR/SVHN payloads, result folders, generated reconstructions, or
the Zenodo ZIP for this gate.
