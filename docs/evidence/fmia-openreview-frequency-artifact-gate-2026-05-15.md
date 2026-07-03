# FMIA OpenReview Frequency Artifact Gate

> Date: 2026-05-15
> Last rechecked: 2026-05-23
> Status: code-and-split-manifests-present / checkpoint-and-score-packets-missing / no large download / no GPU release / no admitted row

## Question

Does `Unveiling the Impact of Frequency Components on Membership Inference
Attacks for Diffusion Models` provide a runnable new DiffAudit asset or metric
packet?

This gate inspected the OpenReview supplementary ZIP for submission
`p9uryyZ5bw`. The ZIP is small enough to inspect directly (`1,783,018` bytes)
and contains official code plus split manifests. No datasets, model weights,
checkpoints, generated samples, or score packets were downloaded or generated.

## Public Surface

| Field | Value |
| --- | --- |
| OpenReview submission | `https://openreview.net/forum?id=p9uryyZ5bw` |
| Supplement URL | `https://openreview.net/attachment?id=p9uryyZ5bw&name=supplementary_material` |
| Supplement filename | `3274_Unveiling_Impact_of_Frequ_Supplementary Material.zip` |
| Supplement size | `1,783,018` bytes |
| Supplement SHA-256 | `567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045` |
| OpenReview note status on 2026-05-23 | version `2`, venue `Submitted to ICLR 2026`, venueid `ICLR.cc/2026/Conference/Rejected_Submission`, `mdate = 2026-02-11T10:13:54Z` |
| ZIP inventory on 2026-05-23 | `79` entries, `5,117,651` total uncompressed bytes |
| Main code root | `FMIA/` |
| Attack code | `FMIA/DDIM/attack.py`, `FMIA/DDIM/components.py`, `FMIA/DDIM/filter.py`, `FMIA/Stable_Diffusion/attack.py`, `FMIA/Stable_Diffusion/filter.py` |
| Training code | `FMIA/train/main.py`, `FMIA/train/diffusion.py`, `FMIA/train/model.py` |
| README claim | datasets and model weights cannot be uploaded because of file size; users should refer to previous methods such as SecMI and PIA for pretrained weights and segmented datasets |

## 2026-05-23 Bounded Recheck

The public OpenReview note and supplementary ZIP were rechecked without
downloading datasets, model weights, generated images, or running code.
OpenReview still exposes a rejected ICLR 2026 submission at version `2`, with
supplementary material at
`/attachment/74aa19564760102160f5bbd2d8691d92abf825cc.zip`. A fresh `HEAD`
against the attachment returned `200`, `Content-Type: application/zip`, and
`Content-Length: 1783018`.

The downloaded temporary ZIP has SHA-256
`567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045`, `79`
entries, and `5,117,651` total uncompressed bytes. Entry-name scanning found
only code, bytecode, the duplicated split `.npz` manifests, and training
utility score modules such as `FMIA/train/score/fid.py` and
`FMIA/train/score/inception_score.py`. It did not reveal checkpoint files,
`pos_result.npy`, `neg_result.npy`, row-level score exports, ROC CSVs, metric
JSON, generated sample packets, or a ready verifier.

This recheck does not change the original gate: FMIA remains watch-plus only
and does not justify a dataset/model download, GPU run, CPU sidecar, or
Platform/Runtime promotion.

## What Is Present

The supplement contains a concrete frequency filter module for attack
intermediates:

- `FMIA/DDIM/filter.py`
- `FMIA/Stable_Diffusion/filter.py`

It also contains DDIM and Stable Diffusion attack wrappers with attacker choices
such as `naive`, `pia`, and `sec`, plus `Filter=1` toggles.

Most importantly, the supplement includes exact member split manifests for the
DDIM side:

| Manifest | Member rows | Nonmember rows | Ratio |
| --- | ---: | ---: | ---: |
| `FMIA/train/member_splits/CIFAR10_train_ratio0.5.npz` | `25,000` | `25,000` | `0.5` |
| `FMIA/train/member_splits/CIFAR100_train_ratio0.5.npz` | `25,000` | `25,000` | `0.5` |
| `FMIA/train/member_splits/STL10_Unlabeled_train_ratio0.5.npz` | `50,000` | `50,000` | `0.5` |
| `FMIA/train/member_splits/TINY-IN_train_ratio0.5.npz` | `50,000` | `50,000` | `0.5` |

Each manifest exposes `mia_train_idxs`, `mia_eval_idxs`, and scalar `ratio`.
The split manifests are duplicated under `FMIA/train/mia_evals/member_splits/`.

## What Is Missing

The supplement does not provide:

- trained DDIM checkpoints such as the default `experiments/CIFAR100/checkpoint.pt`;
- Stable Diffusion fine-tuned model weights;
- precomputed `pos_result.npy` / `neg_result.npy` score arrays;
- ROC CSVs, metric JSON, or ready low-FPR summary artifacts;
- generated samples or response packages;
- downloaded datasets needed by the training and attack scripts.

The DDIM attack path calls `get_model(checkpoint)` and defaults to
`checkpoint='experiments/CIFAR100/checkpoint.pt'`. The Stable Diffusion path
expects a local `flags.diff_path` model directory. The README explicitly says
datasets and model weights cannot be uploaded.

## Decision

`code-and-split-manifests-present / checkpoint-and-score-packets-missing / no
large download / no GPU release / no admitted row`.

FMIA is more concrete than a paper-only watch item because the supplement ships
official frequency-filter attack code and exact split manifests. It is still not
a current execution target: the missing checkpoints and score packets mean a run
would require acquiring datasets, training or locating target models, and then
running attacks from scratch. That is not justified inside the current Research
cycle because it would be another same-family reconstruction/PIA/SecMI-style
expansion without a ready target artifact.

Smallest valid reopen condition:

- public trained checkpoints or hashable model artifacts matching the published
  split manifests; or
- public ready score arrays / ROC / metric artifacts for the shipped splits; or
- a bounded command that uses a locally admitted checkpoint without training a
  new target from scratch and answers a non-adjacent frequency-component
  hypothesis.

Stop condition:

- Do not download datasets, train DDIM targets, fine-tune Stable Diffusion, or
  run FMIA GPU attacks in the current cycle.
- Do not expand into timestep/filter-threshold/filter-scale/attacker matrices
  without a ready checkpoint and score contract.
- Do not promote FMIA into Platform/Runtime admitted rows or product copy.

## Platform and Runtime Impact

None. FMIA remains a Research-only watch-plus mechanism reference. Platform and
Runtime should continue consuming only the admitted `recon / PIA baseline / PIA
defended / GSA / DPDM W-1` set.
