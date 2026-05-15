# Quantile Diffusion MIA SecMI T-Error Replay

> Date: 2026-05-15
> Status: third-party score packet replayed / SecMI-style support evidence / no GPU release / no admitted row

## Question

Does `neilkale/quantile-diffusion-mia` provide a reusable score packet that
changes the previous Quantile Regression asset verdict?

This check inspected the public GitHub repository metadata, recursive tree,
README files, split manifests, and committed `t_error` JSON files. It did not
clone the full repository, download checkpoints or datasets, run DDPM training,
or execute GPU work.

## Public Surface

| Field | Value |
| --- | --- |
| Repository | `https://github.com/neilkale/quantile-diffusion-mia` |
| Repo description | `Extending quantile regression-based membership inference attacks on diffusion models to censored or modified images.` |
| Default branch inspected | `main` |
| Latest repo push observed | `2025-03-27T01:13:33Z` |
| Repo size field | `484,083` KB |
| License field | none |
| Checked commit | `2274da4413f358ef4876b5737c50e1a9d4fb08b8` |

The public tree contains `SecMI/mia_evals/member_splits/*.npz` and
precomputed `SecMI/t_errors/{cifar10,cifar100}/{member,nonmember}_results.json`.
The top-level project claims a Quantile Diffusion MIA extension, but the
checked ready packet is a SecMI-style `t_error` packet, not an official
Quantile Regression paper release and not a ready quantile-regression output
artifact.

## Source Artifacts

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| `SecMI/t_errors/cifar10/member_results.json` | `2,012,012` | `aafd7376b36f6f5e0ff39b1fe43af5e2850c832cb5421df05654236cc6557476` |
| `SecMI/t_errors/cifar10/nonmember_results.json` | `2,005,781` | `3f2125fce05b76b2eccd7d42bbbb299183f240543144423fbbe09c876b8ebea6` |
| `SecMI/t_errors/cifar100/member_results.json` | `2,032,015` | `bcbd9312f05c4adaacee7388d06bfd1bb446fac235bab76eac3ea89ab62a9849` |
| `SecMI/t_errors/cifar100/nonmember_results.json` | `2,028,687` | `13fad04b4042049251fc84ff981081c200755721188f1f2e1561425bf9ac2c16` |
| `SecMI/mia_evals/member_splits/CIFAR10_train_ratio0.5.npz` | `400,790` | `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0` |
| `SecMI/mia_evals/member_splits/CIFAR100_train_ratio0.5.npz` | `400,790` | `4b73cc9869bc414f2a87321fd0768f668da346e599ca8cffeea610755c76dae4` |

Each JSON row has `image_id` and `t_error`. The replay treats lower
`t_error` as more member-like, so the membership score is `-t_error`.

## Replay Results

| Dataset | Rows member/nonmember | Unique IDs member/nonmember | Overlap IDs | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cifar10` | `25,000 / 25,000` | `25,000 / 25,000` | `0` | `0.843853` | `0.771040` | `0.090880` | `0.006000` |
| `cifar100` | `25,000 / 25,000` | `25,000 / 25,000` | `0` | `0.782126` | `0.711640` | `0.087360` | `0.007800` |

Machine-readable artifact:
[`workspaces/gray-box/artifacts/quantile-diffusion-mia-secmia-terror-replay-20260515.json`](../../workspaces/gray-box/artifacts/quantile-diffusion-mia-secmia-terror-replay-20260515.json).

## Decision

`third-party score packet replayed / SecMI-style support evidence / no GPU
release / no admitted row`.

This materially updates the old Quantile Regression watch note only at the
artifact layer: a third-party repository now exposes ready CIFAR10/CIFAR100
SecMI-style `t_error` score rows plus exact split manifests. The metrics are
positive and reproducible from public small files. It does not promote
Quantile Regression itself because the checked packet is not the ICML 2024
Quantile Regression paper's official implementation or score output.

It also does not change Platform/Runtime admitted evidence. The packet is same-
family SecMI support evidence, while existing SecMI remains
`structural-support-only` because product semantics, adaptive comparability,
provenance language, and admitted-bundle schema fit are still blocked.

Smallest valid reopen condition:

- The repository or paper authors publish explicit quantile-regression score
  outputs, trained quantile model artifacts, or a bounded verifier command; or
- A consumer-boundary review decides that third-party SecMI-style public
  packets can be used as support material in paperization without entering
  Platform/Runtime admitted rows.

Stop condition:

- Do not clone the full `484,083` KB repository by default.
- Do not download pretrained DDPM checkpoints, CIFAR archives, or SharePoint
  model folders from this gate.
- Do not run training, quantile-model fitting, W&B artifact recovery, or GPU
  jobs from this repository in the current cycle.
- Do not promote this packet as a Quantile Regression result or an admitted
  Platform/Runtime row.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
