# DME Dual-Model Entropy Artifact Gate

> Date: 2026-05-15
> Status: stub-repo-only / complexity-bias MIA watch / no download / no GPU release / no admitted row

## Question

Does `F-YaNG1/DME` / `Dual-Model with Entropy Augmentation` provide a runnable
DiffAudit asset, score packet, or new diffusion-model MIA debiasing target?

This gate inspected DME because GitHub search surfaced it as an official
repository for a plug-and-play debiasing module for diffusion-model membership
inference attacks, and the current Research queue had no DME evidence row. Only
GitHub metadata, the recursive tree, releases/tags metadata, and README content
were fetched. No datasets, model weights, checkpoints, generated images, attack
outputs, or implementation repos were downloaded or produced.

## Public Surface

| Field | Value |
| --- | --- |
| Repository | `https://github.com/F-YaNG1/DME` |
| Description | Official PyTorch implementation of DME, a dual-model entropy-augmentation module for removing complexity-induced bias from diffusion-model membership inference attacks. |
| Created / pushed / updated | `2025-11-17T11:47:14Z` / `2025-11-17T11:47:15Z` / `2025-11-17T11:47:18Z` |
| Default branch / commit | `main` / `ae0cc48476746945720bf24b42d4f9dfecb6de31` |
| Repo size field | `1` KB |
| License | none declared in GitHub metadata |
| Releases / tags | `0` releases / `0` tags |
| Recursive tree | one blob: `README.md` (`248` bytes) |

The README does not link a paper, arXiv record, dataset, checkpoint, release
asset, or external result packet.

## What Is Present

DME is a potentially relevant mechanism watch item because it targets a
diffusion-MIA failure mode: complexity-induced bias. The public description
frames DME as a plug-and-play dual-model plus entropy-augmentation module for
more accurate privacy risk assessment.

## What Is Missing

The public surface does not provide:

- implementation code;
- a linked paper or formal metric table;
- immutable member/nonmember split manifests;
- target diffusion checkpoints or model hashes;
- generated samples, reconstructions, or response/feature caches;
- per-sample score rows;
- ROC arrays, metric JSON, or figure artifacts;
- a no-training verifier command.

## Decision

`stub-repo-only / complexity-bias MIA watch / no download / no GPU release / no
admitted row`.

DME is worth recording as a non-duplicate watch item because its stated
mechanism is different from FreMIA, VAE2Diffusion, CopyMark, ReDiffuse, SecMI,
PIA, and CLiD: it claims to debias diffusion-model membership inference rather
than add another reconstruction/frequency/trajectory score. It still has no
actionable asset. The repository is currently a placeholder and cannot justify
dataset download, model download, implementation work, CPU sidecar, GPU work, or
Platform/Runtime promotion.

Smallest valid reopen condition:

- public code plus a paper-bound experiment protocol; and
- frozen target checkpoints or exact member/nonmember manifests; and
- public score rows / ROC arrays / metric JSON, or a no-training verifier.

Stop condition:

- Do not implement DME from the README description.
- Do not infer missing paper details from the repo description.
- Do not download datasets, model weights, checkpoints, or train dual models for
  this line in the current cycle.
- Do not promote DME into Platform/Runtime admitted rows or product copy.

## Platform and Runtime Impact

None. DME remains a Research-only watch item. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
