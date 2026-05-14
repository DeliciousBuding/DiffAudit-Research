# SimA Score-Based Artifact Gate

> Date: 2026-05-15
> Status: code-public / split-and-checkpoint-links-empty / score-artifacts-missing / no download / no GPU release / no admitted row

## Question

Can the official `mx-ethan-rao/SimA` release for `Score-based Membership
Inference on Diffusion Models` become the next bounded DiffAudit execution
target or score packet?

This gate inspected only public metadata, README text, the Git tree, and source
files. No dataset split bundle, model checkpoint, generated response cache, or
score artifact was downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Repository | `https://github.com/mx-ethan-rao/SimA` |
| Repo description | `Code release for "Score-based Membership Inference on Diffusion Models"` |
| Paper | `https://arxiv.org/pdf/2509.25003` |
| OpenReview | `https://openreview.net/forum?id=Ckvsu5xRmf` |
| Default branch inspected | `master` |
| Latest repo push observed | `2026-03-25T18:20:29Z` |
| License field | `MIT` |
| GitHub repo size field | `184,971` KB |
| GitHub releases | none |
| Git LFS marker | no `.gitattributes` file found in the recursive tree |

The OpenReview public note exposes the PDF field only; common supplementary
attachment names `supplementary_material`, `supplementary`, and
`supplemental_material` returned HTTP `404`.

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `README.md` | Claims a complete codebase and lists DDPM, Guided Diffusion, LDM, SD1.4, and SD1.5 experiments. The DDPM split/checkpoint link is empty: `here]()`. The SD1.4 split link is also empty and says to email the author for checkpoints. |
| Recursive Git tree | Outside vendored `diffusers`, `guided-diffusion`, `latent-diffusion`, and `taming-transformers`, the public tree contains only `DDPM/` code, `figures/`, two notebooks, `scripts.sh`, README, license, and editor config. |
| Recursive Git tree | No non-vendor `.npz`, `.npy`, `.pt`, `.pth`, `.ckpt`, `.safetensors`, score CSV, metric JSON, ROC artifact, or manifest file was found. |
| `scripts.sh` | All runnable examples point to `/path/to/...` datasets/checkpoints or local absolute paths and require training or external checkpoints before attack. |
| `DDPM/dataset_utils.py` | Requires split files such as `CIFAR10/CIFAR10_train_ratio0.5.npz`, `CIFAR100/CIFAR100_train_ratio0.5.npz`, `STL10-U/STL10-U_train_ratio0.5.npz`, and `CELEBA/CELEBA_train_ratio0.5.npz`; those manifests are not committed. |
| `DDPM/attack.py` | Loads a checkpoint path, computes per-timestep AUROC, ASR, and `TPR@1%FPR`, but writes no reusable score packet. |
| `DDPM/components.py` | Defines `SimA` as single-query denoiser prediction norm: `ddim_reverse` records `eps_getter(x0, ..., step)` and `distance` computes an L4 norm of the denoiser output. |
| `guided-diffusion/INv2_attack.py` | Samples `3` ImageNet-1K and `3` ImageNetV2 images per class, but requires local ImageNet roots and a local Guided Diffusion checkpoint. |
| `latent-diffusion/INv2_attack.py` | Mirrors the ImageNet-1K/ImageNetV2 split logic and requires a local LDM checkpoint plus matching config. |
| `diffusers/src/mia/attack.py` | Stable Diffusion paths load local Hugging Face datasets from hard-coded `/banana/ethan/MIA_data/...` directories, then require local fine-tuned checkpoints or public SD1.5 weights. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The code names many targets, but DDPM/LDM/SD1.4 checkpoints are not released; SD1.5 public base runs require external LAION/COCO split payloads that are not committed. |
| Exact member split | Fail for current cycle. README gives split sizes, and code names split filenames, but no immutable split manifests are public in the repository or releases. |
| Exact nonmember split | Fail for current cycle. Held-out semantics are described in README and scripts, but the actual row identities are external local datasets or missing split files. |
| Query/response or score coverage | Fail. There are no precomputed score arrays, ROC CSVs, metric JSON files, generated response caches, or ready verifier outputs. |
| Mechanism delta | Pass as a mechanism reference. SimA is a distinct score-norm / denoiser-output statistic and is not another reconstruction trajectory metric. |
| Download justification | Fail. The missing pieces are not small public metadata files; making the release executable would require external split bundles, checkpoints, large datasets, and in several cases training/fine-tuning from scratch or emailing authors. |
| Current DiffAudit fit | Watch-plus. It is more useful than paper-only because official code and metric paths are public, but it is not an executable asset packet. |
| GPU release | Fail. No frozen target, split manifest, score packet, or stop condition exists. |

## Decision

`code-public / split-and-checkpoint-links-empty / score-artifacts-missing / no
download / no GPU release / no admitted row`.

SimA should be retained as a strong score-based mechanism watch item, not a
current execution target. The public repository is useful for understanding the
attack statistic and its reported experiment matrix, but the artifact surface is
local-path-dependent and missing the exact split/checkpoint/score bundle needed
by DiffAudit.

Smallest valid reopen condition:

- Public dataset split manifests for at least one target, with immutable member
  and nonmember identities;
- A matching public checkpoint bundle with verifiable size/hash/training
  binding, or ready per-sample SimA score arrays plus ROC/metric artifacts; and
- A bounded verifier command that reads those artifacts without training DDPM,
  fine-tuning Stable Diffusion, acquiring ImageNet/COCO/LAION from scratch, or
  emailing the authors.

Stop condition:

- Do not download large datasets, train DDPM targets, fine-tune SD1.4, request
  checkpoints by email, or run SimA GPU jobs in the current cycle.
- Do not expand Fashion-MNIST SimA variants, timestep matrices, norm variants,
  scheduler matrices, or Monte Carlo SimA sweeps from this release.
- Do not promote SimA into Platform/Runtime admitted rows, product copy, or
  recommendation logic.

## Reflection

This cycle checked the most promising non-duplicate 2025/2026 score-based MIA
release surfaced by the intake scout. The answer is still negative for
execution: SimA has official code and a distinct mechanism, but not public
artifacts that change the current route decision. Current slots remain
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after SimA score-based artifact gate`.

## Platform and Runtime Impact

None. SimA remains Research-only watch-plus evidence. Platform and Runtime
should continue consuming only the admitted `recon / PIA baseline / PIA defended
/ GSA / DPDM W-1` set.
