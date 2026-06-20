# E2SCT-033 Diffusion MIA Public-Surface Check

> Date: 2026-06-09
> Mode: GitHub commit/tree check plus small README, code, and split-file reads;
> no raw datasets, model checkpoints, generated images, attack execution, or
> large downloads
> Decision: support-only black-box diffusion MIA code-and-split surface; not
> admitted; not a second public score/response asset; no_compute_release

## Scope

`lijingwei0502/diffusion_mia` surfaced during the search for a second public
row-bound score/response asset:

`Towards Black-Box Membership Inference Attack for Diffusion Models`
(`arXiv:2405.20771`, ICML 2025, GitHub `lijingwei0502/diffusion_mia`).

This check asks whether the public repository exposes an audit packet:
target identity, immutable member/nonmember rows, row-bound scores or
responses, metric artifacts, provenance hashes, consumer boundary, and
surface-delta controls. It does not evaluate the paper result or rerun any
attack.

Sources checked:

- `https://github.com/lijingwei0502/diffusion_mia`
- `https://github.com/lijingwei0502/diffusion_mia/tree/26e6471c15472bf89ee49ff3057f66a5407dae00`
- `https://arxiv.org/abs/2405.20771`

## Public Surface

`git ls-remote` on 2026-06-09 returned the same commit for `HEAD` and
`refs/heads/main`:

`26e6471c15472bf89ee49ff3057f66a5407dae00`

The repository is a relevant public black-box diffusion MIA surface. It is not
a score/response packet.

| Surface | Observation | Boundary |
| --- | --- | --- |
| Tree contents | The checked tree exposes DDIM, DiT, and Stable Diffusion attack code plus two small DDIM split files. No committed `result.csv`, `results.csv`, score table, ROC array, metric JSON/CSV, verifier, checkpoint packet, generated response packet, or release asset was observed. | Public code and split-index surface only. |
| DDIM split files | `DDIM/CIFAR10_train_ratio0.5.npz` and `DDIM/CIFAR100_train_ratio0.5.npz` each contain `mia_train_idxs` and `mia_eval_idxs` with `25,000` indices per side, plus `ratio=0.5`. `DDIM/dataset_utils.py` also references `STL10_train_ratio0.5.npz`, but that file is not present in the public tree. | Useful split-index evidence for DDIM CIFAR, but no target checkpoint, score row, metric artifact, or verifier is bound to those rows. |
| DDIM attack path | `DDIM/attack.py` loads `logs/DDPM_<DATASET>_EPS/ckpt-step<STEP>.pt`, reads raw datasets under `DDIM/data/datasets/pytorch`, computes AUC/ASR/TPR at runtime, and appends local `result.csv`. | Checkpoint and score outputs are local runtime products. |
| Stable Diffusion path | `Stable_Diffusion/attack.py` loads `CompVis/stable-diffusion-v1-4`, but `Stable_Diffusion/dataset.py` expects local `stable_diffusion_data`, COCO files, `val-list-2500-random.npy`, generated-caption CSVs, and `coco-2500-random.yaml`. The README command names `attack_sd.py`, while the public file is `Stable_Diffusion/attack.py`. The attack appends local `result.csv`. | A public pretrained model name exists, but member/nonmember rows, generated captions, scores, and metrics are not committed. |
| DiT path | `DiT/attack.py` can auto-load a pretrained DiT checkpoint if no custom checkpoint is passed, but member and nonmember inputs are local `ImageFolder` paths such as `/data_server3/ljw/imagenet/member_512` and `/data_server3/ljw/imagenet/val`. It appends local `results.csv`. | Local data and runtime score products block no-training replay. |

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | The Stable Diffusion path names `CompVis/stable-diffusion-v1-4`, and DiT can auto-load a public pretrained model, but DDIM paper-style checkpoints and run-specific target hashes are not committed. | `Partial` |
| Split semantics | DDIM CIFAR-10/CIFAR-100 split-index arrays are public. Stable Diffusion, DiT, STL-10, SVHN, and Tiny-ImageNet rows remain local or absent; the referenced STL-10 split file is not in the public tree. | `Partial` |
| Score/response coverage | No row-bound score, response, prediction, generated-image packet, ROC array, metric table, or completed `result.csv` is committed. | `Fail` |
| Metric provenance | Metric code exists, but metrics are printed or appended only after local model/data execution. | `Fail` |
| Provenance | The code commit and two split blobs are fixed; target checkpoints, raw row identities, score rows, response rows, and metric artifacts are not. | `Partial` |
| Consumer boundary | The repo is semantically in the image-diffusion black-box MIA lane, but it has no compact audit-consumer packet. | `Partial` |
| Surface delta | No public label-shuffle, permutation, surface-delta control, or no-training verifier was observed. | `Fail` |

## Decision

`support-only black-box diffusion MIA code-and-split surface /
row_bound_score_response_packet_missing / no_compute_release`.

This row is not code-only because it commits DDIM CIFAR split indices. It still
lacks the files needed for DiffAudit admission: public checkpoint identity for
the reported runs, row-bound scores or responses, metric artifacts, hashes for
all run inputs, and a verifier that can replay the claim without training or
attack execution.

Allowed wording:

`lijingwei0502/diffusion_mia is a support-only black-box diffusion MIA
code-and-split surface. Its DDIM CIFAR split indices are public, but the public
repo does not expose row-bound scores, responses, completed result CSVs,
checkpoint-bound metrics, or a no-training verifier.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 row;
- N50 external denominator row;
- second public score/response asset;
- compute-release target;
- proof that the paper result is wrong;
- evidence that the attack works on a public audit packet.

## Next Action

Do not release GPU/DCU compute from this gate. Reopen only if the authors
publish a compact no-training package with:

- target checkpoint identities or checkpoint hashes for the reported runs;
- immutable member/nonmember row manifests for each evaluated setting;
- row-bound scores, generated responses, predictions, ROC arrays, or metric
  JSON/CSV;
- artifact hashes and a verifier command; and
- label-shuffle, permutation, or surface-delta controls.
