# MIDST TabDDPM Shadow Distributional Scout

Date: 2026-05-13

## Question

After the MIDST TabDDPM nearest-synthetic-row scorer was weak, does a genuinely
different tabular mechanism work: training an attack on the provided shadow
models to recognize how member and nonmember challenge rows sit inside each
model's synthetic marginal distribution?

## Contract

- Benchmark: MIDST SaTML 2025 black-box single-table challenge.
- Model family: TabDDPM synthetic tabular diffusion models.
- Train attack data: MIDST `train` phase only, `30` shadow model folders.
- Evaluation: MIDST `dev` and `final` model folders; labels are used only for
  scoring from the local Codabench bundle.
- Features: per-row marginal z-score, absolute z-score, robust z-score,
  empirical CDF, tail-CDF, 90% interval indicators, and row-level outlierness
  summaries relative to each model's `trans_synthetic.csv`.
- Classifier: fixed-seed `sklearn` `HistGradientBoostingClassifier`.
- Stop condition: close if dev+final `AUC < 0.60` or strict-tail recovery
  remains near zero.

Artifact:

`workspaces/black-box/artifacts/midst-tabddpm-shadow-distributional-scout-20260513.json`

## Result

| Phase | N | AUC | ASR | TPR@10%FPR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | `6000` | `0.881991` | `0.795333` | `0.647333` | `0.302333` | `0.130333` |
| dev | `4000` | `0.504604` | `0.508500` | `0.106000` | `0.012000` | `0.004000` |
| final | `4000` | `0.495282` | `0.506500` | `0.091500` | `0.012500` | `0.001000` |
| dev+final | `8000` | `0.499846` | `0.504250` | `0.099000` | `0.013000` | `0.001500` |

## Decision

Close this mechanism by default.

The attack learns the `train` shadow folders strongly, but the signal does not
transfer to dev/final. This is more informative than the nearest-neighbor
failure: MIDST remains a clean external benchmark, but marginal-distributional
shadow learning is not the mechanism that rescues it for DiffAudit's next
mainline. Do not expand this into classifier sweeps, feature matrices, TabSyn,
or white-box MIDST unless a genuinely different tabular-diffusion membership
observable appears.

## Platform and Runtime Impact

None. No admitted result, schema change, or downstream consumer change.
