# MIDST TabDDPM Nearest-Neighbor Scout

Date: 2026-05-13

## Question

Can MIDST provide a clean external membership benchmark after CommonCanvas,
Fashion-MNIST, and controlled MNIST mechanisms were weak?

## Contract

- Benchmark: MIDST SaTML 2025 black-box single-table challenge.
- Model family: TabDDPM synthetic tabular diffusion models.
- Data: `tabddpm_black_box.zip`, downloaded from the starter-kit Google Drive
  entry to `<DOWNLOAD_ROOT>/shared/midst-data/`.
- Labels: train labels from the downloaded package; dev/final labels from the
  local Codabench bundle cloned with the MIDST repository.
- Membership split: each model folder has `200` challenge rows, exactly
  `100` members and `100` nonmembers.
- Observable: `trans_synthetic.csv`, `20000` generated transaction rows per
  model.
- Score: `negative_standardized_nearest_synthetic_l2`, using only generated
  table columns shared by challenge and synthetic rows. Higher means more
  member-like.

Artifact:

`workspaces/black-box/artifacts/midst-tabddpm-nearest-neighbor-scout-20260513.json`

## Result

| Phase | N | AUC | ASR | TPR@10%FPR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | `6000` | `0.553861` | `0.555833` | `0.113000` | `0.008333` | `0.002000` |
| dev | `4000` | `0.564306` | `0.558000` | `0.123000` | `0.019500` | `0.002000` |
| final | `4000` | `0.568109` | `0.567500` | `0.108500` | `0.014000` | `0.000500` |
| dev+final | `8000` | `0.566263` | `0.560500` | `0.115750` | `0.016750` | `0.001000` |

## Decision

Close this scorer by default.

MIDST is a cleaner membership benchmark than model-card-only assets because it
ships fixed challenge points, generated outputs, and exact member/nonmember
labels. The minimal nearest-synthetic-row scorer is still weak:
`dev+final AUC = 0.566263` and strict-tail recovery is near zero. This does not
change admitted evidence and does not justify expanding into TabSyn, white-box
MIDST, nearest-neighbor variants, or tabular preprocessing matrices.

MIDST may remain an external benchmark candidate only if a genuinely different
tabular-diffusion membership mechanism appears.

## Platform and Runtime Impact

None. No admitted result, schema change, or downstream consumer change.
