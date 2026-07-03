# ReDiffuse OpenReview Split-Manifest Audit

> Date: 2026-05-15
> Status: official supplementary split manifests found / checkpoint-and-score missing / no GPU release

## Question

Does the OpenReview supplementary material for `Towards Black-Box Membership
Inference Attack for Diffusion Models` provide a stronger immediate ReDiffuse
execution lane than the existing candidate-only state?

This is an asset gate only. It inspects the official supplementary zip central
directory and split manifests. No DDPM, DiT, Stable Diffusion checkpoint,
dataset image archive, generated response cache, or score packet was
downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Towards Black-Box Membership Inference Attack for Diffusion Models` / ReDiffuse |
| Public source | `https://openreview.net/forum?id=LRSspInlN5` |
| Supplement checked | `https://openreview.net/attachment?id=LRSspInlN5&name=supplementary_material` |
| Downloaded supplement size | `1,047,594` bytes |
| Supplement SHA256 | `2d715dcc737a4cd73b375290028ac94864198680929adb3c2d924fb0211e8d5f` |
| Released code surfaces | `Rediffuse/DDPM/`, `Rediffuse/dit/`, `Rediffuse/stable_diffusion/` |
| Released split manifests | `Rediffuse/DDPM/*_train_ratio0.5.npz` |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| OpenReview forum | The paper page exposes a downloadable supplementary material attachment. |
| Supplement `README.md` | Gives DDPM training and attack commands, asks users to place datasets under `DDPM/data/pytorch`, and documents attack methods `naive`, `SecMI`, `PIA`, `PIAN`, and `Denoise` for ReDiffuse. |
| Supplement DDPM directory | Contains runnable-looking DDPM attack/training code plus four train/eval index manifests for CIFAR10, CIFAR100, STL10, and Tiny-ImageNet. |
| Supplement DiT and Stable Diffusion directories | Contains code entrypoints, but no target model weights, generated responses, split score packet, or cached evaluation outputs. |

## Split Manifests

| File | Arrays | Shapes | SHA256 |
| --- | --- | --- | --- |
| `Rediffuse/DDPM/CIFAR10_train_ratio0.5.npz` | `mia_train_idxs`, `mia_eval_idxs`, `ratio` | `25000`, `25000`, scalar | `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0` |
| `Rediffuse/DDPM/CIFAR100_train_ratio0.5.npz` | `mia_train_idxs`, `mia_eval_idxs`, `ratio` | `25000`, `25000`, scalar | `4b73cc9869bc414f2a87321fd0768f668da346e599ca8cffeea610755c76dae4` |
| `Rediffuse/DDPM/STL10_train_ratio0.5.npz` | `mia_train_idxs`, `mia_eval_idxs`, `ratio` | `50000`, `50000`, scalar | `14a06133f36c74e7d3cb97dbe74385fb42c22335a7cb955fd9944ca503baca52` |
| `Rediffuse/DDPM/TINY-IN_train_ratio0.5.npz` | `mia_train_idxs`, `mia_eval_idxs`, `ratio` | `50000`, `50000`, scalar | `14a06133f36c74e7d3cb97dbe74385fb42c22335a7cb955fd9944ca503baca52` |

The split gate is better than previously recorded paper-only ReDiffuse
provenance: exact index manifests are public and hashable for the DDPM side.
The execution gate still fails because those manifests are not enough to score
membership without trained target checkpoints and attack outputs.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for immediate execution. The supplement provides code and training instructions, but no released DDPM/DiT/Stable Diffusion target checkpoint. |
| Exact member split | Pass for DDPM index manifests. |
| Exact nonmember split | Pass for DDPM index manifests. |
| Query/response or score coverage | Fail. The supplement has no generated responses, ReDiffuse scores, baseline scores, ROC CSVs, or ready metric packet. |
| Metric contract | Partial. Attack scripts exist, but no bounded precomputed metric artifact is released. |
| Mechanism delta | No new delta relative to existing ReDiffuse work. This is the same ReDiffuse family, not a new mechanism. |
| Current DiffAudit fit | Hold. Useful provenance improvement for ReDiffuse, but not a next CPU/GPU task. |
| GPU release | Fail. Running this would mean training or acquiring target checkpoints, then generating attack outputs from scratch. |

## Decision

`official supplementary split manifests found / checkpoint-and-score missing /
no GPU release`.

This audit upgrades the ReDiffuse public-asset record: the official OpenReview
supplement includes exact DDPM train/eval index manifests, so ReDiffuse is not
blocked at the split-manifest layer for DDPM. It remains blocked for immediate
DiffAudit execution because there is no released target checkpoint or score
packet.

Do not train DDPM/DiT targets, download ImageNet/Tiny-ImageNet/CIFAR archives,
or run ReDiffuse/PIA/SecMI attack scripts from scratch by default. Reopen only
if a target checkpoint, generated response/feature cache, or score packet
appears for these exact manifests.

## Platform and Runtime Impact

None. This is Research-only provenance evidence. It does not change admitted
Platform/Runtime rows or schemas.
