# ReproMIA Withdrawn Artifact Gate

> Date: 2026-05-15
> Status: withdrawn arXiv / historical source-only diffusion MIA claim / no code-score packet / no download / no GPU release

## Question

Does arXiv `2603.28942` / `ReproMIA: A Comprehensive Analysis of Model
Reprogramming for Proactive Membership Inference Attack` provide a current,
public, executable diffusion-model MIA artifact after the Tracing the Roots
feature-packet boundary sync?

This is an artifact verdict. It exists because the title and historical v1
source claim strong DDPM and Stable Diffusion membership-inference results, so
it could otherwise look like a new active lane.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `ReproMIA: A Comprehensive Analysis of Model Reprogramming for Proactive Membership Inference Attack` |
| Public source | `https://arxiv.org/abs/2603.28942` |
| Current arXiv state | Withdrawn current version; canonical PDF and source endpoints return `404` |
| Historical source checked | `https://arxiv.org/e-print/2603.28942v1` |
| Historical source size | `1,609,282` bytes |
| Historical source SHA256 | `45f2b92456a9a5e136c54f3daef9e7850ba15567c1b3624ac20c6aa4f76157bd` |
| Historical source contents | TeX, bibliography, ACM class files, and figure PDFs |
| Public official repo search | No official GitHub repository found by `gh search repos "ReproMIA"` |
| Public code search | `gh search code "2603.28942"` and `"ReproMIA"` found third-party summaries and arXiv mirrors, not an official code or artifact release |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Current arXiv abstract page | The active record is withdrawn, and the canonical current PDF/source endpoints returned `404 Not Found`. |
| Historical arXiv v1 PDF/source headers | `2603.28942v1` remains accessible as a historical PDF/source snapshot, but it is not the active arXiv version. |
| Historical v1 source central directory | The source package contains `sample-sigconf.tex`, bibliography/class files, and figure PDFs such as `cifar10-roc-curve.pdf`, `tinyimagenet-roc-curve.pdf`, and `laion5b-roc-curve.pdf`; it does not contain Python code, configs, checkpoints, manifests, score arrays, ROC CSVs, or metric JSON. |
| Historical v1 TeX | Reports diffusion-model metrics on DDPM and Stable Diffusion, including DDPM CIFAR-10 `AUC = 92.83`, `TPR@1%FPR = 34.14`, TinyImageNet `AUC = 94.05`, `TPR@1%FPR = 37.71`, CIFAR-100 `AUC = 91.00`, `TPR@1%FPR = 26.10`, and Stable Diffusion LAION-5B-family AUC values around `76`. |
| Historical v1 TeX experimental setup | Says DDPM targets are trained locally for `800k` steps and Stable Diffusion v1.5 is downloaded from Hugging Face; this is not a ready public replay packet. |

## Gate Result

| Gate | Result |
| --- | --- |
| Current scientific record | Fail. The current arXiv record is withdrawn. |
| Official public code | Fail. No official public GitHub repository was found. |
| Target identity | Fail. The historical source names DDPM and Stable Diffusion settings, but ships no target checkpoints or hashes. |
| Exact member split | Fail. No member manifest or sample IDs are released. |
| Exact nonmember split | Fail. No nonmember manifest or sample IDs are released. |
| Query/response or score coverage | Fail. No response packet, feature packet, score array, ROC CSV, or metric JSON is released. |
| Metric contract | Paper-table only. The historical TeX reports metrics, but they are not backed by reusable public score artifacts. |
| Current DiffAudit fit | Withdrawn paper-source-only watch. It does not release a CPU sidecar, GPU task, Platform row, Runtime schema, or admitted bundle change. |

## Decision

`withdrawn arXiv / historical source-only diffusion MIA claim / no code-score
packet / no download / no GPU release`.

ReproMIA should not be used as an active DiffAudit execution lane. The
historical v1 numbers are interesting as a watch signal for proactive
reprogramming-style MIA, but the current paper is withdrawn and the public
surface lacks the artifacts needed to verify or consume the claim.

Do not download Stable Diffusion weights, LAION/COCO assets, CIFAR/TinyImageNet
targets, or train DDPMs for this line. Do not implement ReproMIA from scratch
from the TeX. Reopen only if an official current-version paper plus public-safe
code, exact target/split manifests, and reusable score/metric artifacts appear.

## Platform and Runtime Impact

None. ReproMIA does not change admitted Platform/Runtime rows, Runtime schemas,
recommendation logic, or the active Research slots.
