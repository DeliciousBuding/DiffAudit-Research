# Noise Aggregation Small-Noise Artifact Gate

> Date: 2026-05-15
> Status: arXiv-source-only diffusion MIA claim / strong paper metrics / no code-score packet / no download / no GPU release

## Question

Does arXiv `2510.21783` / `Noise Aggregation Analysis Driven by
Small-Noise Injection: Efficient Membership Inference for Diffusion Models`
provide a public, executable diffusion-model membership-inference artifact
after the ReproMIA withdrawn artifact gate left no active GPU candidate or CPU
sidecar?

This is an artifact verdict. It exists because the paper reports strong DDPM
metrics and a distinct small-noise, predicted-noise aggregation mechanism, so it
could otherwise look like a fresh Lane B execution target.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Noise Aggregation Analysis Driven by Small-Noise Injection: Efficient Membership Inference for Diffusion Models` |
| Public source | `https://arxiv.org/abs/2510.21783` |
| Current arXiv version checked | `v2`, submitted `2026-04-17` |
| Authors in v2 source | Guo Li, Weihong Chen, Yongfu Fan |
| Source checked | `https://arxiv.org/e-print/2510.21783` |
| Source size | `1,433,015` bytes |
| Source SHA256 | `C6091EF4F664D28E8128778C42BC194C04DF169154A9C304E3CFBC6005BA3D25` |
| Source contents | `00README.json`, `liguo_paper.tex`, `liguo_paper.bbl`, and figure PDFs under `fig/` |
| Public official repo search | No official GitHub repository found by `gh search repos` for the exact title or `2510.21783` |
| Public code search | `gh search code "Noise Aggregation Analysis Driven by Small-Noise Injection"` found no hits; `gh search code "2510.21783"` found arXiv index mirrors, not an official code or artifact release |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Current arXiv abstract page | The paper is public as `v2`, last revised `2026-04-17`, with no code link exposed in the arXiv metadata checked during this gate. |
| arXiv source central directory | The package contains TeX, bibliography, and figure PDFs only. It does not contain Python code, configs, checkpoints, split manifests, score arrays, ROC CSVs, metric JSON, or generated response/feature packets. |
| TeX title/authors | The source title matches the candidate; the `v2` TeX names Guo Li, Weihong Chen, and Yongfu Fan. |
| TeX experimental setup | DDPM experiments use CIFAR-10, CIFAR-100, and Tiny-ImageNet with random `50% / 50%` train/test splits; CIFAR-10 and CIFAR-100 are `25,000 / 25,000`, and Tiny-IN is described as `50,000 / 50,000`. Text-to-image evaluation uses Stable Diffusion v1.4/v1.5 from Hugging Face, `1,000` LAION-aesthetic-5plus member images, and `1,000` COCO2017-Val nonmember images. |
| TeX DDPM table metrics | Reports `Ours` with CIFAR-10 `ASR = 0.901`, `AUC = 0.957`, `TPR@1%FPR = 28.7`, `TPR@0.1%FPR = 1.22`; CIFAR-100 `ASR = 0.839`, `AUC = 0.903`, `TPR@1%FPR = 9.65`, `TPR@0.1%FPR = 0.78`; Tiny-IN `ASR = 0.842`, `AUC = 0.912`, `TPR@1%FPR = 14.58`, `TPR@0.1%FPR = 1.03`. |
| TeX Stable Diffusion table metrics | Reports `Ours` with SD1.4 `ASR = 0.701`, `AUC = 0.652`, `TPR@1%FPR = 8.0`, and SD1.5 `ASR = 0.696`, `AUC = 0.661`, `TPR@1%FPR = 8.3`. The same table reports stronger low-FPR `NaiveLoss` values (`TPR@1%FPR = 23.7`) for both SD1.4 and SD1.5, so this is not dominant on the strict-tail Stable Diffusion setting. |
| GitHub search | Exact-title repository search and `2510.21783` repository search returned no repositories. Code search returned only paper-index mirrors for `2510.21783`, not a release from the authors. |

## Gate Result

| Gate | Result |
| --- | --- |
| Official public code | Fail. No official public repository or code release was found. |
| Target identity | Fail. The paper names DDPM and Stable Diffusion settings, but ships no target checkpoints, model hashes, or training logs. |
| Exact member split | Fail. The paper describes random splits and LAION/COCO sampling, but releases no member manifest or sample IDs. |
| Exact nonmember split | Fail. No nonmember manifest or sample IDs are released. |
| Query/response or score coverage | Fail. No response packet, feature packet, score array, ROC CSV, or metric JSON is released. |
| Metric contract | Paper-table only. The reported metrics are not backed by reusable public score artifacts. |
| Mechanism delta | Watch-worthy. Small-noise injection plus predicted-noise aggregation is distinct from recent raw denoising-loss, score-norm, score-Jacobian, response-similarity, feature-packet, prompt-memorization, and tabular/TTS watch lines. |
| Current DiffAudit fit | Research-only paper-source watch. It does not release a CPU sidecar, GPU task, Platform row, Runtime schema, or admitted bundle change. |

## Decision

`arXiv-source-only diffusion MIA claim / strong paper metrics / no code-score
packet / no download / no GPU release`.

Noise Aggregation is a useful mechanism watch because its DDPM paper metrics
are strong and the proposed observable is not just another response-distance or
raw-loss repeat. It is not a current DiffAudit execution lane. The public
surface lacks the minimum target identity, split manifests, query/response or
score coverage, and metric artifacts needed to verify or consume the claim.

Do not download Stable Diffusion weights, LAION-aesthetic-5plus, COCO2017-Val,
CIFAR, Tiny-ImageNet, or train DDPMs for this line. Do not implement the method
from scratch from the TeX. Reopen only if an official code release plus
public-safe target/split manifests and reusable score/metric artifacts appear,
or if a separate public packet exposes the same small-noise aggregation
observable with immutable sample identities.

## Platform and Runtime Impact

None. Noise Aggregation does not change admitted Platform/Runtime rows, Runtime
schemas, recommendation logic, or the active Research slots.
