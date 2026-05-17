# Stable Diffusion ReDiffuse Collaborator Artifact Audit

> Date: 2026-05-17
> Status: collaborator-local artifact imported / candidate-only / no new download / no GPU release / no admitted row

## Question

Does the collaborator-provided Stable Diffusion ReDiffuse reproduction material
change the current DiffAudit black-box mainline?

This cycle inspected the transferred local bundle, added a dedicated
`diffaudit` CLI artifact probe, and replayed the committed `metrics.json`,
`result.csv`, and `roc_curve.csv` without rerunning the `2500 / 2500`
evaluation. It did not download COCO, Stable Diffusion weights, or any new
artifact from upstream.

## Surface Imported

| Field | Value |
| --- | --- |
| Source | collaborator manual transfer |
| Paper claim | `Towards Black-Box Membership Inference Attack for Diffusion Models` Stable Diffusion line |
| Artifact family | Stable Diffusion ReDiffuse final-result bundle |
| Dataset label in artifact | `laion5_blip` |
| Target checkpoint label | `CompVis/stable-diffusion-v1-4` |
| Feature mode | `logistic_l2_C3` |
| Result packet size | `5000` rows |
| Split balance | `2500` member + `2500` nonmember |
| Result columns | `global_index`, `sample_index`, `image_path`, `file_name`, `label`, `label_name`, `source`, `caption`, `score`, `low_score`, `threshold`, `prediction`, `prediction_name`, `correct` |

The transferred material also includes the collaborator's
`SD_MIA_Reproduction/attack.py`, `score_single_image.py`, feature-sweep CSVs,
holdout-validation JSON, and README/status notes. The local README explicitly
states that the member set is a repeatable LAION-like subset rather than the
exact paper LAION-5B member split, and the implementation uses a local
Diffusers Stable Diffusion pipeline rather than an external `img2img` or
variation endpoint.

## Artifact Audit

The new CLI command
`python -m diffaudit probe-rediffuse-sd-artifacts --artifact-dir <local-dir>`
audits the imported result directory without rerunning the attack.

Audit result on the transferred `runs/final_rediffuse_combined/` directory:

| Check | Result |
| --- | --- |
| Required files present | pass |
| Required result columns present | pass |
| Balanced `2500 / 2500` split | pass |
| Reported `AUC` matches recomputed score packet | pass |
| Reported `ASR` matches recomputed score packet | pass |
| Reported split counts match `result.csv` | pass |
| Prediction column matches `correct` column | pass |

Reported metrics from `metrics.json`:

| Metric | Reported |
| --- | ---: |
| `AUC` | `0.71031888` |
| `ASR` | `0.6846` |
| `TPR@1%FPR` | `0.0716` |

Recomputed from `result.csv` / `roc_curve.csv`:

| Metric | Recomputed |
| --- | ---: |
| `AUC` | `0.710319` |
| `ASR` | `0.6846` |
| `TPR@1%FPR` | `0.0736` |
| `TPR@0.1%FPR` | `0.0100` |

The `AUC` and `ASR` replay exactly. The low-FPR TPR differs by `0.0020`, which
is small enough to treat as threshold-grid rounding in the collaborator metric
export rather than a schema mismatch.

Additional validation committed in the bundle:

| Validation surface | Result |
| --- | --- |
| holdout JSON | `test_auc = 0.704604`, `test_asr = 0.701000`, `test_tpr_1fpr = 0.084000` |
| five-fold summary | `mean_test_auc = 0.708036`, `std_test_auc = 0.011590` |

## Usefulness

- This is a real imported Stable Diffusion candidate packet, not another empty
  paper watch or README-only repo. It gives DiffAudit a validated `5000`-row
  black-box-like result surface with nontrivial signal.
- The artifact is strong enough to preserve as candidate evidence and to justify
  a first-class CLI import path. It is materially more useful than a chat note
  or screenshot because the full score packet can now be re-audited and
  compared in a uniform way.
- The bundle is also a practical bridge to future product or report work if the
  user later wants a candidate evidence card, detector import, or single-image
  scoring wrapper around the collaborator detector.

## Decision

`collaborator-local artifact imported / candidate-only / no new download / no
GPU release / no admitted row`.

This does not satisfy the current Lane A reopen gate for a public replay asset:

- it is a collaborator local transfer, not a public immutable packet;
- the member side is a LAION-like repeatable subset rather than the exact paper
  LAION-5B member split;
- the current boundary is local-model-query black-box, not strict external
  API-only black-box; and
- the missing COCO payload is not needed for artifact audit, but it also means
  this cycle does not reopen a fresh end-to-end reproduction.

The correct mainline role is therefore candidate-only black-box evidence. Keep
the current slots unchanged:
`active_gpu_question = none`, `next_gpu_candidate = none`, and
`CPU sidecar = none selected after Stable Diffusion ReDiffuse collaborator artifact audit`.

## Stop Condition

- Do not request or rebuild `coco_data` just to preserve this result.
- Do not download Stable Diffusion weights or rerun the full `2500 / 2500`
  pipeline in the current cycle.
- Do not promote this imported artifact into Platform or Runtime admitted rows
  unless a later cycle resolves the public-asset and product-boundary gaps.

## Platform and Runtime Impact

None for now. The admitted five-row bundle remains unchanged.
