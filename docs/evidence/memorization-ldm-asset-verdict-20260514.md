# Memorization-LDM Asset Verdict

> Date: 2026-05-14
> Status: code-and-request-gated-data / artifact-incomplete / no download / no GPU release

## Question

Does `Cardio-AI/memorization-ldm` provide a clean non-duplicate Lane A asset
for DiffAudit: target model identity, exact member/nonmember split,
query/response or synthetic-sample coverage, and a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No medical dataset,
checkpoint, synthesized sample package, or large artifact was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Unconditional Latent Diffusion Models Memorize Patient Imaging Data` |
| Public code | `https://github.com/Cardio-AI/memorization-ldm` |
| Checked commit | `a8b07caf75a0a093998a827b21b60a995c587c4b` on `main` |
| GitHub license metadata | `GPL-3.0` |
| Zenodo release | `10.5281/zenodo.15267790` |
| Zenodo payload | `memorization-ldm.zip`, `3,686,212` bytes, software snapshot |
| Domain | 2D X-Ray and 3D MRNet latent-diffusion memorization detection |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub root listing | The repository contains training/evaluation code, notebooks, dataset loaders, DDPM/network modules, and a small VGG cache file, not released target LDM checkpoints or generated image volumes. |
| `README.md` | The method trains self-supervised encoders and compares training-synthetic against training-validation correlations to flag copied patient data. |
| `README.md` data section | Public X-Ray and MRNet datasets are referenced, but synthesized samples are not public; they are shared only by request and proof of dataset access. |
| `dataset/` | Contains loader code for NIH chest X-ray, MRNet contrastive pairs, and synthetic data handling; it is not a per-sample member/nonmember manifest. |
| Zenodo `10.5281/zenodo.15267790` | The record is an open software archive linked to the GitHub repo, with one 3.7 MB zip; it does not carry patient data, generated samples, or target LDM weights. |
| Heibox checkpoint link in README | Provides trained self-supervised memorization detector checkpoints, not a target unconditional LDM checkpoint plus exact training/nonmember split. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for DiffAudit release. The public surface does not expose a hashable target latent-diffusion checkpoint or deterministic target recreation bundle. |
| Exact member split | Fail. The public datasets are referenced, but no per-sample target training membership manifest is released in the code or Zenodo snapshot. |
| Exact nonmember split | Fail. Validation/hold-out comparison is described, but no fixed public nonmember manifest suitable for a DiffAudit packet is released. |
| Query/response coverage | Fail. Synthesized samples are access-controlled by request; no reusable generated response package is published. |
| Scoring contract | Partial pass. The repository defines a memorization-detection method, but it depends on unavailable target/generated artifacts for a runnable DiffAudit packet. |
| Mechanism delta | Pass for watch. Medical LDM patient-data memorization is meaningfully different from CommonCanvas, MIDST, Beans, MNIST/Fashion-MNIST, LAION-mi, and Kohaku/Danbooru. |
| GPU release | Fail. There is no frozen target, split, response package, metric command, or stop condition. |

## Decision

`code-and-request-gated-data / artifact-incomplete / no download / no GPU release`.

`Cardio-AI/memorization-ldm` is a valuable related-method and external watch
candidate because it studies patient-imaging memorization in latent diffusion.
It is not a clean DiffAudit second asset today. The blocker is not local GPU
capacity. The blocker is that the public release lacks the exact target LDM,
member/nonmember manifests, and generated sample package needed for a bounded
membership benchmark.

Do not download medical datasets, request controlled synthesized samples, train
the target LDM, or reconstruct the paper pipeline from scratch inside the
current roadmap cycle. Reopen only if a public-safe artifact appears with:

- a hashable target LDM checkpoint or deterministic target recreation recipe,
- exact per-sample member and nonmember manifests,
- a generated sample/query-response package or deterministic generation
  contract, and
- a bounded `25/25` or `50/50` scorer with an `AUC < 0.60` or near-zero
  strict-tail stop gate.

## Platform and Runtime Impact

None. This is Research-only watch evidence. It is not admitted evidence, not a
Platform product row, and not a Runtime schema input.
