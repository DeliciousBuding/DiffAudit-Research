# FMIA OpenReview Frequency Artifact Gate

> Date: 2026-05-15
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
| Main code root | `FMIA/` |
| Attack code | `FMIA/DDIM/attack.py`, `FMIA/DDIM/components.py`, `FMIA/DDIM/filter.py`, `FMIA/Stable_Diffusion/attack.py`, `FMIA/Stable_Diffusion/filter.py` |
| Training code | `FMIA/train/main.py`, `FMIA/train/diffusion.py`, `FMIA/train/model.py` |
| README claim | datasets and model weights cannot be uploaded because of file size; users should refer to previous methods such as SecMI and PIA for pretrained weights and segmented datasets |

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
