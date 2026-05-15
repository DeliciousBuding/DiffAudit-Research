# VAE2Diffusion Latent-Space Inversion Gate

> Date: 2026-05-15
> Status: code-public latent-space MIA watch-plus / split-checkpoint link empty / local-path training scripts / score-artifacts-missing / no download / no GPU release / no admitted row

## Question

Does `mx-ethan-rao/VAE2Diffusion` / `Latent Diffusion Inversion Requires
Understanding the Latent Space` provide a usable DiffAudit target identity,
member/nonmember split, checkpoint, response, or score packet?

This gate was opened because the arXiv source for `2511.20592` explicitly says
that data splits, model checkpoints, training/fine-tuning scripts, and testing
code are released in `https://github.com/mx-ethan-rao/VAE2Diffusion.git`. The
scope is asset-surface verification only: inspect the arXiv source archive,
public GitHub metadata, README, release list, recursive tree shape, and small
script snippets. No dataset, checkpoint, generated response, score artifact, or
model weight was downloaded or executed.

## Public Surface

| Field | Value |
| --- | --- |
| Paper | `https://arxiv.org/abs/2511.20592` |
| arXiv source size | `3,247,943` bytes |
| arXiv source SHA256 | `BC730B7195224CD6DAFC77BB16EC8A318CA945D77E206E57140A8F450DA0A8CA` |
| Official repository | `https://github.com/mx-ethan-rao/VAE2Diffusion` |
| Checked branch / commit | `master` / `4b9dd2b5b8d350c77beeb79d0757eba72cce5aa1` (`2026-03-25T21:35:22Z`) |
| GitHub releases | none |
| Recursive tree | `2,363` entries / `2,045` blobs / `45,337,637` blob bytes |
| Non-vendored tree | `28` blobs / `6,983,731` bytes outside vendored `diffusers/` |
| Artifact extensions found | no `.npz`, `.npy`, `.pt`, `.pth`, `.ckpt`, `.safetensors`, `.csv`, `.jsonl`, `.pkl`, `.zip`, `.tar`, or `.gz` blobs |
| README asset link | `Please download all dataset splits and checkpoints [here]().` |

## What Is Present

The paper and repository expose a real latent-space memorization / MIA mechanism:

- the arXiv source reports that decoder pullback geometry and per-dimensional
  latent distortion affect latent diffusion model memorization;
- the abstract reports average AUROC gains of `1-4%` and TPR@1%FPR gains of
  `1-32%` across `CIFAR-10`, `CelebA`, `ImageNet-1K`, `Pokemon`, `MS-COCO`,
  and `Flickr`;
- the repository contains code roots for `ldm_light/`, `ldm4imagenet/`, and a
  vendored `diffusers/` tree with `diffusers/src/mia/attack_per_dim.py`;
- scripts and README commands cover LDM training, pullback metric computation,
  per-dimensional contribution estimation, and SimA-style attack variants.

This is more concrete than a paper-only watch item because the method code is
public and the mechanism is non-adjacent to simple pixel/CLIP distance,
raw denoising loss, CommonCanvas response scoring, and tabular nearest-neighbor
or EPT variants.

## What Is Missing

The public asset surface does not match the arXiv release claim:

- the README split/checkpoint link is empty;
- GitHub has no release assets;
- the recursive tree contains no split `.npz`, checkpoint, score, ROC, metric,
  response, or verifier artifact blobs;
- `ldm_light/scripts.sh` references author-local paths such as
  `/banana/ethan/MIA_data/CIFAR10/CIFAR10_train_ratio0.5.npz`,
  `/data/mingxing/tmp/...`, and `/home/ethanrao/MIA_LDM/...`;
- `ldm4imagenet/scripts.sh` expects local `/data/mingxing/IMNET100K/` data,
  local output directories, and locally generated pullback / per-dimension
  `.npz` files;
- `diffusers/src/mia/scripts.sh` expects local fine-tuned Stable Diffusion
  checkpoints and local `per_dim_*_diffuser.npz` files for COCO, Pokemon,
  Flickr, and LAION-style runs;
- no immutable public member/nonmember identities, generated images,
  per-sample scores, ROC arrays, metric JSON, or ready verifier output are
  released.

The repository is therefore a code reference plus local reproduction scaffold,
not a downloadable score packet or bounded DiffAudit execution target.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. Code and commands name CIFAR-10, CelebA, ImageNet-1K, Pokemon, COCO, Flickr, LAION-style, and SD targets, but no hashable target checkpoints are public in the repo or releases. |
| Exact member split | Fail. The paper reports split sizes and the scripts name split files, but the actual split manifests are absent and the README asset link is empty. |
| Exact nonmember split | Fail. Nonmember/eval identities are local files, not committed public manifests. |
| Query/response or score coverage | Fail. No generated response package, pullback/per-dim cache, per-sample score rows, ROC arrays, metric JSON, or verifier output is public. |
| Mechanism delta | Pass as watch-plus. Decoder-geometry / latent-dimension filtering is a distinct latent-space MIA enhancement. |
| Download justification | Fail. The missing pieces would require acquiring datasets, training or fine-tuning LDM/SD targets, computing pullback caches, and running attacks from scratch. |
| GPU release | Fail. No frozen target, split, score packet, or stop condition exists. |

## Decision

`code-public latent-space MIA watch-plus / split-checkpoint link empty /
local-path training scripts / score-artifacts-missing / no download / no GPU
release / no admitted row`.

VAE2Diffusion should be retained as a strong latent-space mechanism reference,
especially because it directly targets LDM geometry and reports low-FPR
membership improvements. It is not a current execution target: the public repo
does not release the claimed splits/checkpoints or any ready score packet, and
executing it would be a from-scratch reproduction project.

Smallest valid reopen condition:

- public dataset split manifests with immutable member and nonmember identities;
- matching public target checkpoints or generated response/feature caches with
  sizes and hashes; and
- reusable per-sample score rows, ROC arrays, metric JSON, or a bounded verifier
  command that does not train or fine-tune targets from scratch.

Stop condition:

- Do not download CIFAR-10, CelebA, ImageNet-1K, Pokemon, COCO, Flickr, LAION,
  Stable Diffusion weights, or VAE/LDM checkpoints from this gate.
- Do not train LDMs, fine-tune Stable Diffusion, compute pullback/per-dimension
  caches, run SimA/PFAMI/PIA variants, or launch GPU work from this release.
- Do not promote VAE2Diffusion into Platform/Runtime admitted rows or product
  copy.

## Reflection

This cycle tested a real external-asset claim rather than adding process: the
paper claims public splits/checkpoints, but the repository currently exposes
only code and local-path reproduction scripts. The decision value is to keep
latent-space decoder geometry as a future mechanism hook while leaving
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after VAE2Diffusion latent-space inversion gate`.

## Platform and Runtime Impact

None. VAE2Diffusion remains Research-only watch-plus evidence. Platform and
Runtime should continue consuming only the admitted `recon / PIA baseline / PIA
defended / GSA / DPDM W-1` set.
