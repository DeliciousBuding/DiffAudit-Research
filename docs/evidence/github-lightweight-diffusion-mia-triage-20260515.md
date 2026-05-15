# GitHub Lightweight Diffusion MIA Triage

> Date: 2026-05-15
> Status: lightweight / course-style reproduction triage / no score artifact / no download / no GPU release

## Question

Do recent GitHub search hits for direct diffusion-model membership inference
provide a clean Lane A asset with public target identity, exact
member/nonmember semantics, and response or score coverage?

This is a compact anti-duplication triage. It checks the small repositories
that surfaced in GitHub search after the DEB gate and prevents them from being
mistaken for a new second asset. No repositories were cloned, no notebooks were
executed, and no model, dataset, checkpoint, output image, or generated-result
payload was downloaded.

## Candidates Checked

| Repository | Commit checked | Public surface | Triage finding |
| --- | --- | --- | --- |
| `acha1934/Black-box-Membership-Inference-Attacks-against-Fine-tuned-Diffusion-Models` | `88d9d159d27e5dfed6bd85af131db465ed9b9b13` | `README.md` (`4,472` bytes) and `code.py` (`7,760` bytes), no releases, no tags, no license | Lightweight Colab-style reproduction of the NDSS 2025 fine-tuned diffusion paper. The code selects `50` CelebA rows as "members" and `50` offset rows as "nonmembers", loads `runwayml/stable-diffusion-v1-5`, generates BLIP-captioned outputs, computes DeiT cosine scores, then fits and evaluates an MLP on the same feature matrix. It commits no target fine-tuned checkpoint, split manifest, generated response packet, score rows, ROC arrays, metric JSON, or verifier. |
| `KarinMalka1/Stable-Diffusion-Personalization-Forensics` | `9f4ed1047a468f94edcd5756678b96db9a0a5b8b` | One Colab notebook (`2,444,599` bytes) and `49` output files, including `48` PNGs totaling `16,701,428` bytes, no releases, no tags, no license | Course/exercise notebook for DreamBooth/LoRA personalization and SDEdit-style forensics. The committed PNGs are validation/output images, not a member/nonmember MIA packet. The notebook uses Google Drive paths and live training scripts; it publishes no target LoRA/checkpoint hash, exact query split manifest, per-sample scores, ROC arrays, metric JSON, or ready verifier. |
| `abramwit/ECE-CS-782-Research-Project` | `c1d119690c687b481b012781197a62cbbc620814` | One `sd.py` file (`3,627` bytes), no releases, no tags, no license | Student project script for a `10`-image Boeing 707 fine-tuning toy setup. It expects author-local Google Drive folders such as `/content/drive/MyDrive/Fine_tuning_data/T` and `/content/drive/MyDrive/Fine_tuning_data/T_{nt}` and runs DreamBooth training locally. No data, checkpoint, generated response cache, score packet, ROC array, or verifier is public. |
| `josephho9/score_function_diffusion` | `a9e59984dc96128e2e0deee9fe16f5ddccd83498` | `joseph.py` (`2,504` bytes) and `mnist.py` (`3,634` bytes), no releases, no tags, no license | Empirical-score MNIST noising/denoising prototype. It uses MNIST train/test arrays and saves local noising/denoising tensors, but it does not expose a diffusion-model MIA target checkpoint, exact target training membership manifest, reusable score/ROC/metric artifact, or verifier. |

## Gate Result

| Gate | Result |
| --- | --- |
| Public target identity | Fail across all checked repositories. No immutable fine-tuned diffusion checkpoint, target hash, or target-training recipe with public artifacts is released. |
| Exact member semantics | Fail. The checked repos use local toy subsets, offset rows, or private Google Drive folders rather than immutable target-bound member/nonmember manifests. |
| Query/response coverage | Fail. KarinMalka1 commits PNG outputs, but they are validation/course outputs, not row-bound query/response MIA packets. Other repos commit no response packet. |
| Score/metric coverage | Fail. No repository commits per-sample score rows, ROC arrays, metric JSON, trained attack weights, or a no-training verifier. |
| Reproducibility without private/local state | Fail. Several scripts depend on Colab, Google Drive paths, live model downloads, or from-scratch training. |
| Current DiffAudit fit | Anti-duplication support only. These are not clean Lane A assets and do not release CPU/GPU work. |

## Decision

`lightweight / course-style reproduction triage / no score artifact / no
download / no GPU release`.

None of the checked GitHub hits changes the current DiffAudit roadmap. They are
useful only as false-positive search evidence: each looks relevant by title or
description, but none supplies the minimum target identity, immutable
member/nonmember manifests, row-bound responses or scores, ROC/metric artifacts,
or verifier needed for a bounded DiffAudit replay.

Do not download their datasets, notebooks, generated images, Stable Diffusion
weights, LoRA weights, Google Drive payloads, or local Colab artifacts. Do not
run their scripts, fine-tune DreamBooth/LoRA targets, train attack MLPs, or
promote any row into Platform/Runtime. Reopen only if one of these repos later
adds public checkpoint-bound splits plus reusable score/response and metric
artifacts.

## Platform and Runtime Impact

None. This triage keeps the active slots unchanged:
`active_gpu_question = none`, `next_gpu_candidate = none`, and
`CPU sidecar = none selected after GitHub lightweight diffusion MIA triage`.
