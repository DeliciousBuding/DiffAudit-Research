# DEB Medical Diffusion Artifact Gate

> Date: 2026-05-15
> Status: paper-source-only medical diffusion MIA / grey-box intermediate-trajectory mechanism watch / no code-score packet / no download / no GPU release

## Question

Does `Assessing Membership Inference Privacy Risks in Medical Diffusion
Models via Discrete Encoding-Based Inference` provide a runnable DiffAudit
asset, score packet, or GPU-ready mechanism after the post-CPSample idle state?

This is a Lane B artifact gate. The candidate is worth recording because it is
not another raw denoising-loss, final-layer gradient, response-distance,
frequency-filter, or score-norm repeat. It proposes a discrete-codebook
trajectory perturbation observable for grey-box diffusion membership inference,
with medical-image results. It is not a current execution target.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Assessing Membership Inference Privacy Risks in Medical Diffusion Models via Discrete Encoding-Based Inference` |
| Primary URL | `https://www.mdpi.com/2076-3417/16/7/3140` |
| DOI | `10.3390/app16073140` |
| Venue | `Applied Sciences`, `2026`, `16(7)`, article `3140` |
| Authors | Fei Kong, Hao Cheng, Tianlong Chen, Xiaoshuang Shi, Chenxi Yuan |
| Mechanism name | Discrete Encoding-Based membership inference attack (`DEB`) |
| Access setting | Grey-box; assumes access to intermediate model inputs/outputs during generation, not just final generated images |
| Public code search | `gh search repos` and `gh search code` for the exact title and DOI returned no GitHub repository, code hit, or artifact release |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| MDPI article page | The article is public and describes DEB as a grey-box attack inspired by Denoising Diffusion Codebook Models. DEB injects semantically meaningful discrete-codebook noise and aggregates intermediate predictions across selected time steps. |
| MDPI abstract / results | The paper reports DEB improvements over SecMI, PIA, and SimA on several settings. Reported examples include CIFAR-10 `TPR@1%FPR = 60.3%` for DEB versus `35.9%` for SimA, and PathMNIST `TPR@1%FPR = 10.2%` for DEB versus `1.1%` for PIA. |
| MedMNIST table surface | The paper evaluates five large MedMNIST2D subsets: PathMNIST, ChestMNIST, OCTMNIST, TissueMNIST, and OrganAMNIST. Reported results are modality-dependent: ChestMNIST is near-saturated for several attacks, while PathMNIST remains harder. |
| Applicability statement | The paper explicitly frames the attack as requiring intermediate generation-state access. It also says the grey-box attack does not apply to pipelines that expose only final generated images. |
| GitHub repository search | Exact-title and DOI repository searches produced no candidate repository. |
| GitHub code search | Exact-title and DOI code searches produced no implementation, result file, split manifest, or artifact hit. |

## Gate Result

| Gate | Result |
| --- | --- |
| Official public code | Fail. No official code repository or supplementary implementation was found. |
| Target identity | Fail. The paper names dataset/model families, but no target checkpoint hashes, trained model archives, or reproducible target manifests are released. |
| Exact member split | Fail. The article reports experimental splits and MedMNIST subsets, but no immutable member-row manifest is public. |
| Exact nonmember split | Fail. No held-out sample IDs or nonmember manifest are released. |
| Query/response or feature coverage | Fail. No intermediate-state trajectory packet, generated response packet, feature tensor, or score row artifact is released. |
| Metric contract | Paper-table only. Reported AUC and `TPR@1%FPR` values are not backed by reusable ROC arrays, metric JSON, or verifier output. |
| Mechanism delta | Watch-worthy. Discrete-codebook perturbation plus intermediate-trajectory aggregation is distinct from raw loss, PIA/SecMI approximations, SimA score norm, FreMIA frequency filtering, FCRE frequency reconstruction, CLiD prompt likelihood, and CopyMark response-distance artifacts. |
| Current DiffAudit fit | Research-only grey-box medical diffusion watch. It does not release a CPU sidecar, GPU task, Platform row, Runtime schema, or admitted bundle change. |

## Decision

`paper-source-only medical diffusion MIA / grey-box intermediate-trajectory
mechanism watch / no code-score packet / no download / no GPU release`.

DEB is a useful future mechanism reference because it targets a genuinely
different observable: stability under discrete-codebook perturbation of
intermediate diffusion states. The reported medical-image modality differences
are also scientifically relevant for paper limitations and future scope.

It is not executable or consumable in the current DiffAudit cycle. The public
surface lacks the minimum target identity, split manifests, intermediate-state
packet, score rows, ROC arrays, metric JSON, and verifier needed for a bounded
CPU/GPU replay.

Do not download MedMNIST, CIFAR, TinyImageNet, Stable Diffusion weights, medical
image payloads, or target checkpoints for this line. Do not implement DEB from
the paper. Reopen only if public code appears together with checkpoint-bound
target/split manifests and reusable intermediate-state or score artifacts.

## Platform and Runtime Impact

None. DEB does not change admitted Platform/Runtime rows, Runtime schemas,
recommendation logic, or the active Research slots.
