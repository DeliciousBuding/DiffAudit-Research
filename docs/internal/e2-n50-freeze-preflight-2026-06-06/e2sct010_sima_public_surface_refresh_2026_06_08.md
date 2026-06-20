# E2SCT-010 SimA Public-Surface Refresh

> Date: 2026-06-08
> Mode: no-download metadata/raw-text refresh
> Decision: support-only code-public score-norm mechanism reference; not C14; not admitted; not denominator; no_compute_release

## Scope

This refresh closes the post-C14 live look for `E2SCT-010` after the
2026-05-15 SimA artifact gate and the 2026-05-25 public asset refresh. It uses
only arXiv metadata, `git ls-remote`, and small raw text/source files. It does
not clone the repository, download archives, request checkpoints by email,
download datasets or model weights, run attacks, or launch GPU/DCU jobs.

Sources checked:

- `https://export.arxiv.org/api/query?id_list=2509.25003`
- `https://github.com/mx-ethan-rao/SimA`
- `https://raw.githubusercontent.com/mx-ethan-rao/SimA/master/README.md`
- `https://raw.githubusercontent.com/mx-ethan-rao/SimA/master/scripts.sh`
- `https://raw.githubusercontent.com/mx-ethan-rao/SimA/master/DDPM/attack.py`
- `https://raw.githubusercontent.com/mx-ethan-rao/SimA/master/DDPM/main.py`
- `https://raw.githubusercontent.com/mx-ethan-rao/SimA/master/diffusers/src/mia/attack.py`

GitHub's unauthenticated recursive-tree API was rate-limited during this
refresh, so the branch identity was checked with `git ls-remote` and artifact
surface checks used raw file URLs.

## Findings

| Surface | Current finding |
| --- | --- |
| arXiv metadata | Atom API status `200`, length `2863`, SHA-256 `01d5d4d9d47c8cb0a1bc6b9ac1846e09af7f382a9e7fa916e35bb1a60abb0f5a`. The public paper identity is `Score-based Membership Inference on Diffusion Models`, arXiv `2509.25003v2`, published `2025-09-29`, updated `2026-04-23`. |
| Git branch | `git ls-remote https://github.com/mx-ethan-rao/SimA.git refs/heads/master` returned `97dce4fec6030094fc722557a8b03b6858eab37b`, matching the earlier refresh. |
| README | Raw README status `200`, length `9129`, SHA-256 `175b15f8b9b2afb0914fdb0a80e106c2d0de67a1591014f9d5a54b3f50619642`. It still describes the repository as the official implementation and lists DDPM, Guided Diffusion, LDM, SD1.4, and SD1.5 experiments. |
| Asset links | The README still points DDPM splits/checkpoints to an empty `here` link and SD1.4 splits to an empty `here` link; SD1.4 checkpoints still require emailing the author. |
| Scripts | Raw `scripts.sh` status `200`, length `6447`, SHA-256 `25921590ef2bd2202d5d1982b5645e982247cde24f01761c14ded87d934ff40b`. Commands use `/path/to/...` dataset roots, checkpoint paths, and CUDA execution. |
| DDPM attack code | Raw `DDPM/attack.py` status `200`, length `7286`, SHA-256 `7914e309c1232fd1981bc8358d363546dc5cbcd66c40f13c405da89a584815a0`. The code exposes SecMI, PIA, Loss, PIAN, and SimA attackers and computes AUROC/ROC metrics. |
| Stable Diffusion attack code | Raw `diffusers/src/mia/attack.py` status `200`, length `13049`, SHA-256 `c4df969809b400d6152896f88343f3b2436f07d1d3c41f514a918165de64d619`. Dataset loaders still reference hard-coded `/banana/ethan/MIA_data/...` paths for Pokemon, Flickr, COCO, LAION, and default checkpoints. |

## Interpretation

SimA remains relevant because it is an official code-public, score-norm /
denoiser-output mechanism for diffusion-model membership inference. A weak
code-availability rule could over-promote it: the README has an extensive
experiment matrix and the repository has attack/metric code.

DiffAudit still blocks C14 expansion, denominator use, admitted evidence, and
compute release:

- no public immutable member/nonmember split manifests;
- no public checkpoint bundle or checkpoint hashes for the reported targets;
- no row-bound response or score packet;
- no ROC array, metric JSON/CSV, or verifier artifact;
- SD1.4 assets still require empty split links plus author email;
- executable scripts remain local-path and CUDA dependent.

This also should not be added to the Direction A main text now. The paper's
current contribution is evidence-contract calibration, not method coverage, and
SimA would not strengthen the main claim until public row-bound artifacts
appear. It can remain a related-method/watch-plus support note.

## Decision

`support_only_code_public_score_norm_reference / split_checkpoint_score_missing
/ no_compute_release`.

Do not count `E2SCT-010` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, completed external adjudication, reviewer
reliability evidence, or compute release. It is no longer pending a live
post-C14 first look; keep it as support-only / code-public score-based MIA
watch-plus.

Do not download CIFAR, STL10, CelebA, ImageNet, Pokemon, COCO, Flickr, LAION,
Stable Diffusion, DDPM, Guided Diffusion, or LDM assets. Do not run SimA,
SimA-MC, PIA, SecMI, training, fine-tuning, local score extraction, or GPU/DCU
jobs from this gate.

Reopen only if the authors publish public split manifests plus matching
checkpoint or ready per-sample score/ROC/metric artifacts with a no-training
verifier, or if Direction A deliberately opens a separate method-watch
supplement that does not affect C14 counts, denominator status, or compute
release.
