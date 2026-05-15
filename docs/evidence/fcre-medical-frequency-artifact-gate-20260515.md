# FCRE Medical Frequency Artifact Gate

> Date: 2026-05-15
> Status: paper-source-only / medical-image cross-domain watch / no download / no GPU release / no admitted row

## Question

Does `Frequency-Calibrated Reconstruction Error: Enhancing Membership Inference
Attacks on Medical Image Diffusion Models` provide a runnable DiffAudit asset,
score packet, or frequency-line execution target?

This gate inspected arXiv `2506.14919` because FCRE is a non-duplicate
frequency-calibrated reconstruction-error MIA and had appeared in prior internal
frequency-line notes without a current evidence-status row. Only the arXiv PDF
was fetched for text extraction; no datasets, model weights, checkpoints,
generated images, or attack outputs were downloaded or produced.

## Public Surface

| Field | Value |
| --- | --- |
| Paper | `Frequency-Calibrated Reconstruction Error: Enhancing Membership Inference Attacks on Medical Image Diffusion Models` |
| arXiv | `https://arxiv.org/abs/2506.14919` |
| PDF inspected | `https://arxiv.org/pdf/2506.14919` |
| PDF size | `634,123` bytes |
| PDF SHA256 | `E5B9A782047130219D74D39F991DB24D883EE83B30587A58D9179E5E73301AE8` |
| GitHub search | Exact GitHub repo/code searches for the title and `FCRE (L2+SSIM)` returned no public implementation or result packet. |

## What Is Present

The paper defines a frequency-calibrated reconstruction error score over a
partial DDIM reverse process. It reports experiments on:

| Dataset | Paper split description |
| --- | --- |
| FeTS 2022 | `740` cases from `16` institutions for members and `511` cases from a held-out institution for nonmembers, yielding `37,000` member slices and `25,600` nonmember slices. |
| ChestX-ray8 | independently and randomly selected `>3,600` member images and `>3,600` nonmember images. |
| CIFAR-10 | `25,000 / 25,000` member/nonmember split, using pre-defined splits and public weights from prior work. |

Reported headline table values:

| Method | FeTS AUC | FeTS TPR@1%FPR | ChestX-ray8 AUC | ChestX-ray8 TPR@1%FPR | CIFAR-10 AUC | CIFAR-10 TPR@1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FCRE (L2) | `0.898` | `0.185` | `0.958` | `0.316` | `0.880` | `0.162` |
| FCRE (L2+SSIM) | `0.926` | `0.328` | `0.971` | `0.409` | `0.840` | `0.085` |

The ablation table reports that a `15% / 85%` frequency band gives the strongest
medical-image result among the tested ranges.

## What Is Missing

The public surface does not provide:

- official code or a public repository;
- immutable FeTS/ChestX-ray8/CIFAR split manifests;
- target diffusion checkpoints or model hashes;
- generated reconstruction outputs or response/feature caches;
- per-sample score rows, ROC arrays, metric JSON, or a ready verifier command.

The PDF states that FeTS and ChestX-ray8 diffusion models were trained for
`300,000` steps on a single NVIDIA V100. Reproducing those medical-image claims
would require dataset access, target training, and attack execution from
scratch, which is outside the current decision-value gate.

## Decision

`paper-source-only / medical-image cross-domain watch / no download / no GPU
release / no admitted row`.

FCRE is useful as mechanism context for the frequency line, but it does not
release a runnable asset. It also does not justify reopening the closed
mid-frequency residual lane: the current DiffAudit lane already has bounded
same-noise residual evidence and comparator audits, while FCRE would require a
new medical-image target setup or a from-scratch CIFAR reimplementation without
score artifacts.

Smallest valid reopen condition:

- official code plus frozen split manifests and matching checkpoints; or
- public per-sample score rows / ROC arrays / metric JSON for FeTS, ChestX-ray8,
  or CIFAR-10; or
- a reviewed consumer-boundary decision admitting medical-image diffusion MIA as
  a separate cross-domain support lane with public target identity and score
  artifacts.

Stop condition:

- Do not download FeTS, ChestX-ray8, CIFAR-10, or medical-image payloads for
  FCRE in the current cycle.
- Do not train diffusion targets, run DDIM reconstruction, sweep frequency bands,
  or launch GPU work from this paper alone.
- Do not promote FCRE into Platform/Runtime admitted rows or product copy.

## Platform and Runtime Impact

None. FCRE remains a Research-only paper-source watch item. Platform and Runtime
should continue consuming only the admitted `recon / PIA baseline / PIA defended
/ GSA / DPDM W-1` set.
