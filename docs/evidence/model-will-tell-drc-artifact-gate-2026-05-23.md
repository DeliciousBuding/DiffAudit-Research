# Model Will Tell DRC Artifact Gate

> Date: 2026-05-23
> Status: paper-source-only DRC restoration MIA watch / no official code / no split-score artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2403.08487` / `Model Will Tell: Training Membership Inference for
Diffusion Models` expose a public DiffAudit-ready asset, score packet, or
bounded replay path that should change the active Research slots?

This was selected as a single Lane A/B metadata gate because the proposed
Degrade Restore Compare (`DRC`) signal is not just another raw denoising loss,
final-layer gradient, frequency cutoff, same-noise residual repeat, or
response-distance variant. The check used arXiv API metadata, arXiv source
inventory, page text, and GitHub repository/code searches. It did not download
datasets, diffusion checkpoints, generated images, model weights, or run any
restoration code.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Model Will Tell: Training Membership Inference for Diffusion Models` |
| arXiv | `https://arxiv.org/abs/2403.08487v1` |
| Published / updated | `2024-03-13T12:52:37Z` |
| Authors | Xiaomeng Fu, Xi Wang, Qiao Li, Jin Liu, Jiao Dai, Jizhong Han |
| Mechanism | Degrade Restore Compare (`DRC`) |
| arXiv source inventory | `1,745,140` byte source tarball, `19` entries: TeX, bibliography/style files, and figure PDFs only |
| Code release statement | paper says the authors intend to release code, but no official code URL is present |
| GitHub search | exact-title, DRC phrase, author-name, and arXiv-id repository/code searches returned no official repository or code hits |

The source tarball contains only:

```text
ablation_inverted_ratio.pdf
eccvabbrv.sty
eccv.sty
eijkel2.eps
figures/
figures/ablation_AP_AR.pdf
figures/ablation_epoch.pdf
figures/ablation_mask_ratio.pdf
figures/log_roc.pdf
figures/log_roc_celeba_ffhq.pdf
figures/log_roc_cifar10_cifar100.pdf
figures/method_framework.pdf
figures/motivation.pdf
figures/motivation_intuition.pdf
figures/motivation_pipeline.pdf
llncs.cls
main.bbl
main.bib
main.tex
```

No `.py`, notebook, split manifest, score rows, ROC CSV, metric JSON,
generated response packet, checkpoint hash, or verifier output is public in
the checked surface.

## Mechanism Signal

DRC intentionally degrades an input image, restores it with the target
diffusion model, then compares the restored image with the original image. The
paper uses semantic similarity for the score: CLIP image embeddings for
natural images and a face-recognition encoder for face images.

This is mechanism-relevant because it tests a target model's restoration prior
after controlled degradation. It is closer to a black-box restoration response
contract than to SecMI/PIA loss probing or final-layer sensitivity. However,
the current release is paper-source only, so implementing DRC locally would be
a new reproduction, not a bounded replay of a released artifact.

## Reported Metrics

These metrics are paper-source values from `main.tex`, not locally replayed.

| Dataset | Reported DRC AUC | Reported DRC TPR@1%FPR | Reported DRC TPR@0.1%FPR |
| --- | ---: | ---: | ---: |
| Cifar10 | `0.931` | `12.20%` | `0.82%` |
| Cifar100 | `0.919` | `16.56%` | `2.44%` |
| CelebA | `0.989` | `80.46%` | `54.52%` |
| FFHQ | `0.811` | `30.85%` | `18.60%` |

The experiment setup describes Cifar10, Cifar100, and CelebA as random
half-train member/nonmember splits, while FFHQ uses the public
`CompVis/latent-diffusion` FFHQ model and labels the whole FFHQ dataset as
members because validation identities are not reported. Those split choices
are not released as immutable row manifests.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Partial/fail. The paper names Cifar/CelebA trained models and the public FFHQ latent-diffusion model, but no trained target checkpoint hashes, revisions, or bundles are released for the paper experiments. |
| Exact member split | Fail. Random half-train splits are described but not released as row IDs, URLs, filenames, seeds, or manifests; FFHQ membership is also an approximation because validation images are not reported. |
| Exact nonmember split | Fail. The remaining halves and CelebA nonmember set are described but not released as immutable manifests. |
| Query/response or score coverage | Fail. There are rendered tables and figures only; no restored-image packet, per-row DRC score file, ROC arrays, metric JSON, or verifier output is public. |
| Mechanism delta | Pass for watch. Degrade-restore semantic comparison is a distinct restoration-prior observable. |
| Download justification | Fail. Downloading datasets, FFHQ/CelebA/CIFAR payloads, or latent-diffusion weights would not evaluate a released score packet. |
| GPU release | Fail. The blocker is missing public artifacts, not local compute. |

## Decision

`paper-source-only DRC restoration MIA watch / no official code / no
split-score artifact / no download / no GPU release / no admitted row`.

DRC should remain a Research-only mechanism watch. It is useful because it
frames membership as restoration-prior evidence and reports strong paper-table
metrics on CelebA and Cifar. It is not a current execution target because no
public target identity, split manifest, restored response packet, score rows,
ROC arrays, metric JSON, or verifier is released.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after Model Will Tell DRC artifact gate`.

Smallest valid reopen condition:

- authors publish official code plus exact Cifar/CelebA/FFHQ member/nonmember
  manifests, target checkpoint revisions or hashes, restored-image response
  packets, per-row scores, ROC arrays, metric JSON, and a verifier; or
- an independent public artifact package exposes row-bound DRC scores without
  requiring local model training, FFHQ/CelebA/CIFAR downloads, or
  implementation from the paper.

Stop condition:

- Do not download Cifar10, Cifar100, CelebA, FFHQ, latent-diffusion weights,
  face-recognition encoders, CLIP checkpoints, generated images, or restored
  image payloads from this gate.
- Do not implement DRC, train Cifar/CelebA diffusion models, run
  latent-diffusion restoration, sweep degradation masks, or build score
  matrices from the paper.
- Do not launch CPU/GPU sidecars, add Platform/Runtime rows, change schemas,
  or change product copy until row-bound public artifacts exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
