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

Raw transfer provenance was rechecked on 2026-05-23 from the original chat
attachments without extracting new payloads into Git. The full transfer ZIP is
`512,403,674` bytes with SHA-256
`3b2f6ea09ce7d9ece4957ec635bac322e0b545b833f1d902f46abbf44f6fef73`,
`2,558` entries, and `542,464,818` uncompressed bytes. The smaller
`artifacts.zip` is `349,479` bytes with SHA-256
`1cb085e1df5c6f305f8af5562be51bf7af7277fd2fa8467c5ce401ed56aff447`,
`6` entries, and `1,566,286` uncompressed bytes; it is only the final
`metrics.json` / `metrics.csv` / `result.csv` / `roc_curve.csv` /
`roc_curve.png` subset already represented under
`runs/final_rediffuse_combined/`. The existing imported manifest at
`<DIFFAUDIT_ROOT>/Download/shared/supplementary/collaborator-stable-diffusion-rediffuse-20260516/manifest.json`
remains the authoritative local subset manifest for the source tree, detector
JSON, merged feature NPZ, and final result packet.

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

The 2026-05-23 current-state probe still returns `ready` for both existing
entrypoints:
`python -m diffaudit probe-rediffuse-sd-artifacts --artifact-dir <imported-final-dir>`
and
`python -m diffaudit probe-rediffuse-sd-assets --bundle-root <imported-raw-dir>`.
The artifact probe still reports `5,000` rows, a balanced `2,500 / 2,500`
split, recomputed `AUC = 0.710319`, `ASR = 0.6846`,
`TPR@1%FPR = 0.0736`, and `TPR@0.1%FPR = 0.0100`; the asset probe still
confirms detector JSON, merged score NPZ, validation JSON, and source files are
present and internally consistent.

## 2026-05-25 Source-Label Boundary Audit

A CPU-only metadata audit checked whether the imported `result.csv` supports a
strict same-distribution membership claim or whether the member label is
confounded with the source domain. This did not rerun Stable Diffusion, download
COCO, request new LAION payloads, or create a new tool. It inspected the
existing `5,000` result rows only.

Observed boundary facts:

| Check | Result |
| --- | ---: |
| Row-level ReDiffuse score AUC | `0.71031888` |
| Source-only AUC from the `source` column | `1.000000` |
| Member source rows | `2,500 / 2,500` from `LAION-5B member subset` |
| Nonmember source rows | `2,500 / 2,500` from `COCO2017-val non-member subset` |
| Caption-unique groups | `4,637` |
| Duplicate-caption groups | `271` |
| Mixed-label caption groups | `0` |
| Caption-deduplicated group AUC | `0.707006` |
| File-name duplicate groups | `0` |

This closes the main interpretation gap. The packet is internally replayable
and nontrivial, but it is not a clean same-distribution per-sample membership
asset because the member/nonmember label is perfectly aligned with
`LAION-5B member subset` versus `COCO2017-val non-member subset`. The
ReDiffuse score remains useful as candidate evidence for a Stable Diffusion
cross-source privacy stress test, not as a second asset for strict
member/nonmember portability or Platform/Runtime admission.

## Usefulness

- This is a real imported Stable Diffusion candidate packet, not another empty
  paper watch or README-only repo. It gives DiffAudit a validated `5000`-row
  black-box-like result surface with nontrivial signal.
- The artifact is strong enough to preserve as candidate evidence and to justify
  a first-class CLI import path. It is materially more useful than a chat note
  or screenshot because the full score packet can now be re-audited and
  compared in a uniform way.
- The imported subset under
  `<DIFFAUDIT_ROOT>/Download/shared/supplementary/collaborator-stable-diffusion-rediffuse-20260516/`
  now supports two additional DiffAudit entrypoints:
  `probe-rediffuse-sd-assets` for source/detector/result-bundle readiness and
  `score-rediffuse-sd-image` as a candidate-only wrapper around the
  collaborator `score_single_image.py` path.
- The single-image scorer is integrated but not yet end-to-end runnable on the
  default local interpreter: the current Python surface is missing `fire`,
  `pytorch_lightning`, `skimage`, and `omegaconf`, and no local
  `CompVis/stable-diffusion-v1-4` checkpoint cache was found during the
  2026-05-17 probe. This is a runtime prerequisite gap, not a research-lane
  reopening signal.

## Decision

`collaborator-local artifact imported / candidate-only / no new download / no
GPU release / no admitted row`.

This does not satisfy the current Lane A reopen gate for a public replay asset:

- it is a collaborator local transfer, not a public immutable packet;
- the member side is a LAION-like repeatable subset rather than the exact paper
  LAION-5B member split;
- the member and nonmember rows are also perfectly separated by source
  (`LAION-5B member subset` versus `COCO2017-val non-member subset`), so the
  packet cannot support a strict same-distribution membership claim;
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
