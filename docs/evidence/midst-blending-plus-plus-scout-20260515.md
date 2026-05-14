# MIDST Blending++ Official Score-Export Scout

> Date: 2026-05-15
> Status: bounded external score-export scout
> GPU release: none

## Question

Does the public CITADEL/UQAM `ensemble-mia` runner-up implementation change the
MIDST TabDDPM black-box decision, compared with our nearest-neighbor,
shadow-distributional, and MIA-EPT scouts?

## Inputs

- Upstream repo: `https://github.com/CRCHUM-CITADEL/ensemble-mia`
- Checked commit: `a27d3653708596acbdf54b03ad446e81779a5e70`
- Local checkout: `<DIFFAUDIT_ROOT>/Download/shared/midst-ensemble-mia`
- Local labels: `<DIFFAUDIT_ROOT>/Download/shared/midst-challenge/codabench_bundles/midst_blackbox_single_table/data/tabddpm_black_box`
- Artifact: `workspaces/black-box/artifacts/midst-blending-plus-plus-scout-20260515.json`
- Script: `scripts/probe_midst_blending_plus_plus_scout.py`

The upstream repository ships score exports and predictions, so this scout only
loads CSVs and local labels. It does not retrain XGBoost, recompute Gower
features, load a TabDDPM model, or run GPU work.

## Results

| Score export | Phases | Models | Rows | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rmia_scores_k_5` | train | 30 | 6,000 | 0.507048 | 0.519000 | 0.006667 | 0.001333 |
| `rmia_scores_k_5` | dev+final | 40 | 8,000 | 0.513076 | 0.523750 | 0.007250 | 0.001750 |
| `blending_plus_plus_prediction` | train | 30 | 6,000 | 0.619608 | 0.578167 | 0.086667 | 0.039000 |
| `blending_plus_plus_prediction` | dev+final | 40 | 8,000 | 0.598079 | 0.563500 | 0.095750 | 0.048250 |

## Interpretation

Blending++ is materially stronger than our previous MIDST mechanisms. The
dev+final score is close to the `0.60` AUC reopen floor and has the best MIDST
low-FPR tail so far.

It still does not clear the gate. The dev+final AUC is `0.598079`, just below
the required threshold-independent floor, and the score is an upstream
competition prediction export rather than a new product-ready mechanism inside
DiffAudit. The correct reading is `borderline best MIDST so far`, not an
admitted or GPU-released result.

## Verdict

`borderline_best_midst_so_far_but_below_auc_reopen_gate`.

Do not expand this into XGBoost / Optuna retraining, Gower feature-matrix
variants, TabSyn, multi-table MIDST, or Platform/Runtime admitted rows. Reopen
MIDST only if a follow-up can change the current decision without simply
retraining the same official ensemble.
