# FreMIA Frequency-Filter Artifact Gate

> Date: 2026-05-15
> Status: paper-source-plus-stub-repo / frequency-filter MIA watch / no download / no GPU release / no admitted row

## Question

Does `Enhancing Membership Inference Attacks on Diffusion Models from a
Frequency-Domain Perspective` / `FreMIA` provide a runnable DiffAudit asset,
score packet, or frequency-filter execution target?

This gate inspected FreMIA because GitHub search surfaced `poetic2/FreMIA` as
an ICML 2026 official repository for a direct diffusion-model membership
inference paper, and the current queue had no FreMIA-specific evidence row.
Only the GitHub metadata, README, arXiv metadata, and compact arXiv source
archive were fetched. No datasets, model weights, checkpoints, generated
images, attack outputs, or full implementation repos were downloaded or
produced.

## Public Surface

| Field | Value |
| --- | --- |
| Paper | `Enhancing Membership Inference Attacks on Diffusion Models from a Frequency-Domain Perspective` |
| arXiv | `https://arxiv.org/abs/2505.20955` |
| arXiv current version observed | `2505.20955v3` |
| arXiv published / updated | `2025-05-27T09:50:11Z` / `2026-01-29T11:43:24Z` |
| Official repo | `https://github.com/poetic2/FreMIA` |
| Repo default branch / commit | `main` / `7bed9fb829a67ed8d576d9630dc30e428a286c1f` |
| Repo pushed / size field | `2026-05-03T15:09:56Z` / `1` KB |
| Repo tree | one blob: `README.md` (`158` bytes) |
| arXiv source size | `2,857,150` bytes |
| arXiv source SHA256 | `CC830F3F673DAB4137EFBC1AF72D8DAD0335523B4E3166FEE6A931151D61A9F6` |

The official README currently states only that code is coming soon. The repo
does not publish source code, split files, checkpoints, logs, score rows, ROC
arrays, metrics, or a verifier.

## What Is Present

FreMIA is a direct diffusion-model MIA mechanism. The paper formalizes
reconstruction-capability-based MIAs under a common scoring paradigm, then adds
a plug-and-play high-frequency filter to reduce the adverse effect of
high-frequency content on baseline scores.

The arXiv source archive contains TeX, bibliography/style files, figure PDFs,
and comparison images. It includes plot files named like ROC and score
distribution figures under `Fig_final/`, but these are rendered figures, not
machine-readable score rows or ROC arrays.

The paper reports member/hold-out settings including:

| Target family | Dataset | Member / hold-out | Training setting |
| --- | --- | ---: | --- |
| DDIM | CIFAR-100 | `25,000 / 25,000` | `800,000` iterations |
| DDIM | STL10-U | `50,000 / 50,000` | `1,600,000` iterations |
| DDIM | Tiny-ImageNet | `50,000 / 50,000` | `1,600,000` iterations |
| Stable Diffusion v1.4 fine-tune | Pokemon | `416 / 417` | `15,000` iterations |
| Stable Diffusion v1.4 fine-tune | Flickr | `1,000 / 1,000` | `60,000` iterations |
| Stable Diffusion v1.4 fine-tune | MS-COCO | `2,500 / 2,500` | `150,000` iterations |
| Stable Diffusion v1.4/v1.5 pretrained | Laion-MI | `2,500 / 2,500` | no additional training |

Representative paper-table values are strong in the trained/fine-tuned
settings. The paper reports values on a percentage scale:

| Setting | Method | AUC | TPR@1%FPR |
| --- | --- | ---: | ---: |
| DDIM CIFAR-100 | SecMI+F | `93.74` | `24.32` |
| DDIM Tiny-ImageNet | PIA+F | `93.23` | `32.91` |
| Stable Diffusion MS-COCO fine-tune | Naive+F | `98.32` | `41.99` |
| Stable Diffusion Flickr fine-tune | Naive+F | `96.82` | `67.60` |

The same source reports that pre-trained Stable Diffusion v1.4/v1.5 on
Laion-MI remains near random for baseline attacks and the filter adds only small
gains, for example SD1.5 PIA+F `AUC = 53.24` and `TPR@1%FPR = 0.40`.

## What Is Missing

The public surface does not provide:

- official implementation code;
- immutable member/hold-out split manifests;
- target DDIM or fine-tuned Stable Diffusion checkpoints and hashes;
- generated samples, reconstructions, or response/feature caches;
- per-sample membership score rows;
- machine-readable ROC arrays or metric JSON;
- a no-training verifier command.

The arXiv source contains rendered figure PDFs and paper tables, but no
row-bound artifacts. Reproducing the reported DDIM and fine-tuned Stable
Diffusion results would require dataset downloads, target training/fine-tuning,
and attack execution from scratch.

## Decision

`paper-source-plus-stub-repo / frequency-filter MIA watch / no download / no
GPU release / no admitted row`.

FreMIA is a high-value mechanism watch item because it directly targets
diffusion-model membership inference and explicitly improves Naive, SecMI, PIA,
and CLiD-style baselines with a frequency-domain filter. It still does not
release an executable DiffAudit asset. The official repository is currently a
stub, and the arXiv source only supports paper-table and rendered-figure
inspection.

Smallest valid reopen condition:

- the official repo publishes code plus frozen split manifests and matching
  checkpoints; or
- public per-sample score rows, ROC arrays, and metric JSON appear for the
  reported DDIM or fine-tuned Stable Diffusion settings; or
- the authors publish a compact no-training verifier that binds scores to exact
  member/hold-out identities and target checkpoints.

Stop condition:

- Do not download CIFAR-100, STL10-U, Tiny-ImageNet, Pokemon, MS-COCO, Flickr,
  Laion-MI, Stable Diffusion weights, DDIM checkpoints, fine-tuned checkpoints,
  generated images, or score/figure payloads for FreMIA in the current cycle.
- Do not implement the frequency filter from the paper, run Naive/SecMI/PIA/CLiD
  variants, train/fine-tune targets, or launch GPU work.
- Do not promote FreMIA into Platform/Runtime admitted rows or product copy.

## Platform and Runtime Impact

None. FreMIA remains a Research-only watch item. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
