# TMIA-DM Temporal Artifact Gate

Date: 2026-05-15

## Verdict

`fresh public-surface recheck / paper-only temporal-noise gradient MIA / reported metrics only / no code-score artifact / no download / no GPU release / no admitted row`

Lane A intake checked `Temporal Membership Inference Attack Method for
Diffusion Models` / `面向扩散模型的时序成员推理攻击方法` because it is a
previously known gray-box mechanism whose public paper surface needed a current
artifact gate. It combines short-horizon noise-gradient information with
longer-horizon temporal-noise information under the name `TMIA-DM`.

This does not reopen the existing internal TMIA-DM / tri-score line and is not
a replay or execution target. The public surface is the journal article and PDF
only. The article page lists `资源附件(0)`, and exact GitHub searches for
`TMIA-DM` and the English/Chinese titles did not find a relevant official
repository or score-release repository.

## Public Surface Checked

| Item | Evidence |
| --- | --- |
| Article page | `https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202440687` |
| PDF | `https://crad.ict.ac.cn/cn/article/pdf/preview/10.7544/issn1000-1239.202440687.pdf` |
| DOI | `10.7544/issn1000-1239.202440687` |
| Authors | Gao Zhipeng, Zhang Yi, You Weijing, Chai Ze, Yang Yang, Rui Lanlan |
| Published surface | CRAD article page and PDF; no resource attachments on the article page |
| Repository search | exact-title and `TMIA-DM` GitHub searches found no relevant official code or artifact repository |

The article reports experiments on `CIFAR-10`, `CIFAR-100`, and `TINY-IN`
against `MIDM`, `SecMI`, and `PIA`, with metrics including `AUC` and
`TPR@0.01%FPR` at `t = 20`, `t = 60`, and `t = 100`. It also describes a
Pokemon/LAION/COCO-style cross-dataset member/nonmember analysis. These are
paper-table results, not reusable score packets.

## Gate Assessment

| Gate | Status |
| --- | --- |
| Target identity | Blocked. The paper names common datasets and a Pokemon fine-tuning scenario, but it publishes no target checkpoint, model hash, training manifest, or immutable target identity. |
| Member/nonmember split | Blocked. The article describes dataset combinations, but no row-level member/nonmember manifest, image IDs, captions, or split files are released. |
| Query/response coverage | Blocked. The temporal-noise and gradient sequences are generated inside the method; no query packet, intermediate trajectory tensor, response packet, or regenerated output archive is public. |
| Score/metric artifacts | Blocked. The public PDF contains tables and plots only; no per-sample scores, ROC arrays, metric JSON/CSV, notebooks, or verifier command are released. |
| Mechanism novelty | Already known internally, but still watch-worthy as a public paper mechanism. Temporal-noise plus noise-gradient evidence is distinct from raw denoising MSE, pixel/CLIP response distance, final-layer gradient norm, and same-family MIDST nearest-neighbor/EPT variants. |
| Download/GPU decision | No release. Replaying would require selecting datasets and checkpoints, reconstructing the method from the paper, generating temporal trajectories, and producing scores from scratch. |

## Boundary Decision

Keep TMIA-DM as Research-only paper-source temporal-mechanism watch evidence.
Do not download CIFAR/Tiny-ImageNet/Pokemon/LAION/COCO assets, train or
fine-tune diffusion targets, reconstruct temporal-noise trajectory pipelines,
or launch GPU work from this paper. Do not promote TMIA-DM into
Platform/Runtime admitted rows without official public code plus immutable
target/split artifacts and reusable score/ROC/metric packets.

Current slots after this gate:

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `CPU sidecar = none selected after TMIA-DM temporal artifact gate`

Decision value: this cycle refreshed the external public surface for a known
mechanism, but found no new public asset. Temporal-noise/gradient MIA should
stay on watch/internal-only boundaries, and the project should continue looking
for a clean asset rather than implementing TMIA-DM from scratch.
