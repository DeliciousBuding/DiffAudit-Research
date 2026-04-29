# X-165 Cross-Box Tri-Surface Consensus Review

Date: 2026-04-29
Status: `negative but useful`

## Question

Can an existing-surface `PIA + GSA + SimA` consensus scorer improve low-FPR membership signal over the best single scorer on the shared full-overlap packet?

## Method

CPU-only repeated holdout over the existing shared surfaces:

- `PIA`: `workspaces/gray-box/runs/pia-packet-score-export-gsa-full-overlap-20260418-r1/scores.json`
- `GSA`: `workspaces/white-box/runs/gsa-loss-score-export-targeted-full-overlap-20260418-r1/summary.json`
- `SimA`: `workspaces/gray-box/runs/sima-packet-score-export-pia-full-overlap-20260421-r1/scores.json`

Shared identity:

- `461` members
- `474` nonmembers

Candidates:

- `best_single`
- `weighted_average_3feature`
- `logistic_3feature`
- `consensus_min`
- `consensus_mean`

Gate:

- no `TPR@0.1%FPR` losses against best single
- at least four `TPR@0.1%FPR` wins across repeated holdout
- nonnegative mean deltas on `TPR@1%FPR` and AUC

## Result

`PIA` is selected as best single in `7 / 7` repeated holdout splits.

Best alternative:

- `logistic_3feature`
  - AUC: `7 / 0 / 0` wins/ties/losses, mean delta `+0.016016`
  - `TPR@1%FPR`: `3 / 0 / 4`, mean delta `-0.009276`
  - `TPR@0.1%FPR`: `4 / 0 / 3`, mean delta `+0.006184`

Other alternatives are weaker or unstable at low FPR.

## Verdict

`negative but useful`

The tri-surface consensus idea improves AUC under logistic calibration, but it does not improve the low-FPR tail robustly enough to become a release candidate. No GPU is justified.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until a follow-up freezes a genuinely new surface-acquisition hypothesis`
- `next_live_lane = X166 I-A / cross-box boundary hardening after tri-surface consensus review`
- `handoff = none`

Canonical evidence anchor:

- `workspaces/cross-box/runs/x165-crossbox-trisurface-consensus-20260429-r1/summary.json`
