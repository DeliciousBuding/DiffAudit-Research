# MIDST TabDDPM EPT Scout

Date: 2026-05-15

## Question

After the weak MIDST TabDDPM nearest-neighbor and shadow-distributional scouts,
does a genuinely different tabular membership mechanism help: the
MIA-EPT-style error-prediction profile from synthetic-table attribute
predictors?

## Contract

- Benchmark: MIDST SaTML 2025 black-box single-table challenge.
- Model family: TabDDPM synthetic tabular diffusion models.
- Upstream method reference: [MIA-EPT](https://github.com/eyalgerman/MIA-EPT),
  observed at git `HEAD = 6890ee833ad90b9fd8b3b3b06abd41613a4b316d`.
- Local adaptation: for each model folder, train bounded random-forest
  attribute predictors on `trans_synthetic.csv`, predict held challenge-row
  attributes, and extract actual / predicted / accuracy or error-ratio
  profiles.
- Attack training: train one fixed `HistGradientBoostingClassifier` on the
  `train` phase only.
- Evaluation: use `dev` and `final` labels only for metrics from the local
  Codabench bundle.
- Data: all `30` train models, all `20` dev models, and all `20` final models.
- Per model: `200` challenge rows, exactly `100` members and `100` nonmembers.
- Synthetic rows used: `20000` rows per model.
- Target columns: `trans_date`, `trans_type`, `operation`, `amount`,
  `balance`, `k_symbol`, `bank`.
- Excluded fields: `trans_id`, `account_id`; `account` is excluded as a target
  and not used as a predictor in this bounded run.

Artifact:

`workspaces/black-box/artifacts/midst-tabddpm-ept-scout-20260515.json`

Script:

`scripts/probe_midst_tabddpm_ept_scout.py`

## Result

| Phase | N | AUC | ASR | TPR@10%FPR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | `6000` | `0.851961` | `0.770833` | `0.571333` | `0.194667` | `0.071667` |
| dev | `4000` | `0.536730` | `0.532250` | `0.151000` | `0.027500` | `0.006000` |
| final | `4000` | `0.523352` | `0.521000` | `0.131000` | `0.031000` | `0.009000` |
| dev+final | `8000` | `0.530089` | `0.524625` | `0.139500` | `0.029500` | `0.009250` |

## Decision

Close MIDST EPT by default.

The EPT profile is a valid different mechanism: it does not reuse the previous
nearest-synthetic-row distance or marginal-distributional feature set. It also
learns the train shadow folders (`AUC = 0.851961`), which confirms the local
pipeline is not inert.

The signal still fails the reopen gate on transfer. Dev+final reaches only
`AUC = 0.530089` and `ASR = 0.524625`. The strict-tail value
`TPR@1%FPR = 0.029500` is slightly higher than the two prior MIDST scouts, but
it is not enough to offset the low overall ranking quality. This is a weak
single-table transfer result, not a new mainline.

Do not expand this into classifier sweeps, account-column toggles,
random-forest grids, target-column subsets, TabSyn, white-box MIDST, or
multi-table MIDST. Reopen MIDST only if a new public artifact or a genuinely
new tabular-diffusion membership observable changes the dev/final transfer
story.

## Platform and Runtime Impact

None. No admitted result, schema change, downstream consumer change, GPU
release, or product-row update.
