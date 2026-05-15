# CopyMark Official Score Artifact Gate

> Date: 2026-05-15
> Status: official score artifacts public / member-nonmember logs present / no small public data packet or checkpoint hash / no HF dataset download / no GPU release / no admitted row

## Question

Does `caradryanl/CopyMark` provide reusable non-CommonCanvas score artifacts
that should change the current `active_gpu_question`, `next_gpu_candidate`, or
Platform/Runtime admitted evidence boundary?

This gate was opened after the existing CopyMark evidence had already closed
the local CommonCanvas response packet as weak. The scope here is different:
inspect the official repository's committed experiment artifacts for `sd`,
`ldm`, `sdxl`, `mixing`, and `laion_ridar`. The check used GitHub API metadata,
README/script snippets, committed JSON result files, committed image logs, and
small committed `.pth` score tensors for shape checks. No Hugging Face
`datasets.zip`, image payload, model weight, checkpoint folder, full repository
clone, training run, inference run, or GPU work was used.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Real-World Benchmarks Make Membership Inference Attacks Fail on Diffusion Models` |
| Official repository | `https://github.com/caradryanl/CopyMark` |
| Checked branch / commit | `main` / `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea` (`2024-11-24T04:00:19Z`) |
| Latest push observed | `2024-11-24T04:00:25Z` |
| GitHub repo size field | `385,408` KB |
| License field | none |
| GitHub releases | `0` |
| Experiment artifact families under `diffusers/experiments/` | `kohaku 44`, `laion_mi 50`, `laion_ridar 8`, `ldm 52`, `mixing 38`, `sd 52`, `sdxl 51` |

The committed tree is materially stronger than a paper-only asset because it
ships official benchmark output files, not only scripts. It is still not a
drop-in DiffAudit execution packet because the small public artifact layer is
split across metric JSON, image logs, tensors/features, and threshold files,
while the underlying images and target model folders still live outside the
repository.

## Experiment Contracts Checked

The official shell scripts bind model families to member and holdout sources:

| Family | Target path in scripts | Member source | Holdout source |
| --- | --- | --- | --- |
| `ldm` | `models/ldm-celebahq-256/` | `celeba-hq-2-5k-{eval,test}` | `ffhq-2-5k-{eval,test}` |
| `sd` | `models/stable-diffusion-v1-5/` | `laion-aesthetic-2-5k-{eval,test}` | `coco2017-val-2-5k-{eval,test}` |
| `sdxl` | `models/CommonCanvas-XL-C/` | `commoncatalog-2-5k-{eval,test}` | `coco2017-val-2-5k-{eval,test}` |
| `mixing` | `models/stable-diffusion-v1-5/` | `laion-aesthetic-eval` | `laion-mi-nonmember-eval` or COCO/LAION-MI mixed holdouts |
| `laion_ridar` | `models/stable-diffusion-v1-5/` | `laion-aesthetic/eval` | `cc12m/eval`, `yfcc100m/eval`, `datacomp/eval`, `coco2017-val/eval` |

The scripts call `load_dataset(...)` with explicit `member_dataset` and
`holdout_dataset` arguments, write `image_log.json` as
`{member: [...], nonmember: [...]}`, and then produce benchmark or test result
JSON from separate member/nonmember score tensors. For PIA/PFAMI/SecMI they
also save `*_member_scores_all_steps*.pth` and
`*_nonmember_scores_all_steps*.pth`. For GSA they save concatenated feature
arrays and XGBoost models rather than direct per-row JSON scores.

## Artifact Shape

Representative committed image logs are real member/nonmember sequence logs:

| File | Member count | Nonmember count | First member | First nonmember |
| --- | ---: | ---: | --- | --- |
| `sd/gsa_1/gsa_1_sd_image_log.json` | `2500` | `2500` | `0.jpg` | `000000397133.jpg` |
| `sd/gsa_1/gsa_1_sd_image_log_test.json` | `2500` | `2500` | `3420.jpg` | `000000180878.jpg` |
| `ldm/pia/pia_ldm_image_log.json` | `2500` | `2500` | `2206.png` | `00000.png` |
| `sdxl/secmi/secmi_sdxl_image_log_test.json` | `2500` | `2500` | `322963345.jpg` | `000000180878.jpg` |
| `mixing/secmi_coco50_laion50_plus_image_log.json` | `2500` | `2500` | `0.jpg` | `000000173091.jpg` |
| `laion_ridar/laion_ridar_image_log.json` | `10000` | `10000` | `0.png` | `0.png` |

The checked score-result JSON files are aggregate metric/curve artifacts, not
standalone per-sample rows. They expose fields such as `AUROC`, `TPR`, `FPR`,
`threshold`, and either `best_TPR_at_1_FPR` / `best_threshold_at_1_FPR` for
evaluation outputs or `TPR_at_1_threshold` / `FPR_at_1_threshold` for test
outputs.

Small committed tensor checks show that some official score packets can be
paired with image logs without running the model:

| Tensor | Shape | Meaning |
| --- | ---: | --- |
| `sd/pia/pia_sd_member_scores_all_steps.pth` | `(2500, 50)` | member PIA all-step scores |
| `sd/pia/pia_sd_nonmember_scores_all_steps.pth` | `(2500, 50)` | nonmember PIA all-step scores |
| `ldm/secmi/secmi_ldm_member_scores_all_steps.pth` | `(2500, 20)` | member SecMI all-step scores |
| `ldm/secmi/secmi_ldm_nonmember_scores_all_steps.pth` | `(2500, 20)` | nonmember SecMI all-step scores |

This is stronger than the earlier CopyMark intake, which only verified the
large HF zip layout and local CommonCanvas query/response packet. It is weaker
than an admitted DiffAudit packet because the official release still lacks a
single immutable row manifest that binds image ID, split role, score, target
checkpoint hash, and verifier command.

## Representative Metrics

These are official committed result files read from GitHub, not regenerated
locally.

| Family / method | File | AUROC | Threshold-transfer low-FPR signal |
| --- | --- | ---: | --- |
| `sd` / PIA sum | `pia_sd_sum_score_result_test.json` | `0.766974` | `TPR_at_1_threshold = 0.342000`, `FPR_at_1_threshold = 0.011200`; `TPR_at_01_threshold = 0.191200`, `FPR_at_01_threshold = 0` |
| `sd` / PFAMI sum | `pfami_sd_sum_score_result_test.json` | `0.606423` | `TPR_at_1_threshold = 0.206800`, `FPR_at_1_threshold = 0.007200`; `TPR_at_01_threshold = 0.100400`, `FPR_at_01_threshold = 0` |
| `sd` / SecMI sum | `secmi_sd_sum_score_result_test.json` | `0.701479` | `TPR_at_1_threshold = 0.309600`, `FPR_at_1_threshold = 0.008400`; `TPR_at_01_threshold = 0.150800`, `FPR_at_01_threshold = 0` |
| `ldm` / PIA sum | `pia_ldm_sum_score_result_test.json` | `0.632061` | `TPR_at_1_threshold = 0.025200`, `FPR_at_1_threshold = 0.010000` |
| `ldm` / PFAMI sum | `pfami_ldm_sum_score_result_test.json` | `0.915734` | `TPR_at_1_threshold = 0.501600`, `FPR_at_1_threshold = 0.019200`; `TPR_at_01_threshold = 0.191600`, `FPR_at_01_threshold = 0.001200` |
| `ldm` / SecMI 50th | `secmi_ldm_50th_score_result_test.json` | `0.626191` | `TPR_at_1_threshold = 0.069600`, `FPR_at_1_threshold = 0.008400` |
| `sdxl` / PIA sum | `pia_sdxl_sum_score_result_test.json` | `0.538079` | weak threshold transfer |
| `sdxl` / PFAMI sum | `pfami_sdxl_sum_score_result_test.json` | `0.493723` | threshold transfer unusable (`TPR_at_01_threshold = 0.743200`, `FPR_at_01_threshold = 0.756000`) |
| `sdxl` / SecMI 50th | `secmi_sdxl_50th_score_result_test.json` | `0.503493` | weak threshold transfer |
| `laion_ridar` | `laion_ridar_score_result_test.json` | `0.872135` | `TPR_at_1_threshold = 0.221700`, `FPR_at_1_threshold = 0.010000`; `TPR_at_01_threshold = 0.073900`, `FPR_at_01_threshold = 0.001000` |

The `mixing` eval artifacts are also useful as official trend evidence:
PIA sum AUC rises from `0.668904` at `coco0_laion100_plus` to `0.745244` at
`coco75_laion25_plus`; SecMI 50th AUC rises from `0.660715` to `0.691905`.
Those files are evaluation-side threshold artifacts, not final test outputs.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Partial. Scripts name LDM CelebA-HQ, SD1.5, CommonCanvas-XL-C, and stable-diffusion-v1-5 paths, but the repository does not commit checkpoint hashes or model folders. |
| Exact member split | Partial. Image logs and dataset-directory contracts expose member sequences, but the underlying images live in the external HF dataset zip and no compact row manifest is committed. |
| Exact nonmember split | Partial. Same as member split: nonmember filenames are logged, but the raw packet is external and large. |
| Query/response or score coverage | Pass as Research-side support. Official aggregate ROC/threshold JSONs and some per-sample tensor scores are public. Fail for admitted/product use because the release lacks one row-ID-bound score manifest and ready verifier output. |
| Mechanism delta | Mixed. It covers official CopyMark variants across PIA, PFAMI, SecMI, GSA, laion-ridar, and mixing; it is not a new DiffAudit method family and partly overlaps the closed CommonCanvas target. |
| Download justification | Fail for current execution. Reading committed score artifacts answered the gate; downloading the `5.66` GB HF dataset zip, model folders, or image payloads would not change the current Platform/Runtime boundary. |
| GPU release | Fail. No new execution is needed, and the missing pieces are artifact-packaging / provenance boundaries, not GPU compute. |

## Decision

`official score artifacts public / member-nonmember logs present / no small
public data packet or checkpoint hash / no HF dataset download / no GPU release
/ no admitted row`.

CopyMark should be upgraded from a pure intake/response-contract candidate to
official Research-side score-artifact support evidence. The strongest value is
not to rerun CopyMark, but to cite the official public artifact layer: member
and nonmember image logs, committed ROC/threshold JSONs, and selected score
tensors are present for non-CommonCanvas families such as `sd`, `ldm`,
`mixing`, and `laion_ridar`.

It still does not change DiffAudit's active execution slots. The release does
not provide hash-bound target checkpoints, a small immutable data packet, a
single row-ID-bound per-sample score manifest, or a ready verifier command.
The local CommonCanvas response packet remains weak and closed by default; the
official `sdxl` score artifacts do not rescue that lane because the sampled
PIA/PFAMI/SecMI results are weak or threshold-transfer-inconsistent.

Current slots remain `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after CopyMark official score artifact gate`.

Smallest valid reopen condition:

- authors publish a compact row manifest binding image IDs, split role, target
  model/checkpoint hash, method score, and metric provenance;
- authors publish a no-training verifier command over those committed scores;
- authors publish small immutable data/checkpoint packets sufficient to replay
  one target without the full HF zip or model-folder download; or
- DiffAudit explicitly opens a paperization/support-evidence lane that can use
  CopyMark official score artifacts without admitting them into Platform or
  Runtime.

Stop condition:

- Do not download `CaradryanLiang/copymark` / `chumengl/copymark`
  `datasets.zip` or image folders from this gate.
- Do not download Stable Diffusion, CommonCanvas, LDM, Kohaku, LAION, COCO,
  CC12M, YFCC, DataComp, FFHQ, CelebA-HQ, or CommonCatalog payloads.
- Do not clone the full `385,408` KB repository by default, train target
  models, run PIA/PFAMI/SecMI/GSA scripts, regenerate features, fit XGBoost
  models, or launch GPU jobs from this gate.
- Do not promote CopyMark official score artifacts into Platform/Runtime rows,
  schemas, product copy, or admitted evidence until a consumer-boundary review
  accepts row-ID semantics and checkpoint provenance.

## Reflection

This was a useful exception to the "score-artifacts-missing" pattern: the
official CopyMark tree does ship meaningful result artifacts. The reason it
stays out of active execution is narrower and more defensible now: the public
artifact layer is good support evidence, but not a self-contained, hash-bound
DiffAudit packet.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
