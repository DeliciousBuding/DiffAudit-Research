# E2SCT-032 MIA-EPT Tabular Public-Surface Check

> Date: 2026-06-09
> Mode: GitHub main/gh-pages tree check plus small README, HTML, and code reads;
> no challenge data, model artifacts, submissions, or attack execution
> Decision: support-only tabular-diffusion public-result-page artifact; not
> image-diffusion denominator evidence; not admitted; not a second public
> score/response asset; no_compute_release

## Scope

MIA-EPT surfaced during the search for public score/result artifacts around
diffusion membership inference:

`MIA-EPT: Membership Inference Attack via Error Prediction for Tabular Data`
(`arXiv:2509.13046`, GitHub `eyalgerman/MIA-EPT`, project page on `gh-pages`).

This check asks whether the public repository or project page exposes a
row-bound public evidence packet: target identity, immutable member/nonmember
rows, row-bound scores or predictions, metric artifacts, provenance hashes,
consumer boundary, and a no-training verifier. It does not evaluate the
underlying MIDST competition result.

Sources checked:

- `https://github.com/eyalgerman/MIA-EPT`
- `https://github.com/eyalgerman/MIA-EPT/tree/6890ee833ad90b9fd8b3b3b06abd41613a4b316d`
- `https://github.com/eyalgerman/MIA-EPT/tree/3fa8f0ee6e1f7401572aca869f9735b6af170dd0`
- `https://eyalgerman.github.io/MIA-EPT/`
- `https://arxiv.org/abs/2509.13046`

## Public Surface

`git ls-remote` on 2026-06-09 returned:

- main / HEAD: `6890ee833ad90b9fd8b3b3b06abd41613a4b316d`
- gh-pages: `3fa8f0ee6e1f7401572aca869f9735b6af170dd0`

The public surface is stronger than code-only but still not a row-bound packet.

| Surface | Observation | Boundary |
| --- | --- | --- |
| Main branch | The tree contains only source files such as `main.py`, `features_extraction.py`, `train_classifier.py`, `metrics.py`, `create_predictions_folder.py`, and `README.md`. No committed `results_summary.csv`, prediction CSVs, feature CSVs, labels, score arrays, ROC tables, metric JSON, model files, or submission files were observed. | Code-only for replay; runtime products are absent. |
| README | The README reports 2nd place in MIDST 2025 Black-box Multi-Table and describes a pipeline that creates feature vectors, trains/evaluates classifiers, and writes a submission file. | Useful method and result context, not a public verifier packet. |
| Local path dependency | `data_manager.py` sets `DATA_PATH = "YOUR_PATH_HERE"`. The data loader expects local challenge/synthetic table files such as `challenge_with_id.csv`, `challenge_label.csv`, and `trans_synthetic.csv`. `main.py` reads `results_summary.csv` from runtime output directories and creates a prediction folder from the best runtime row. | Blocks no-training replay and public row binding. |
| Project page | The `gh-pages` branch includes static ROC images/PDFs and an HTML table reporting best AUC-ROC `0.599`, best TPR@10%FPR `22.0%`, and MIDST 2025 Black-box Multi-Table TPR@10%FPR `20.0%` with 2nd place. | Public top-line result and plot surface, not row-level scores or labels. |
| Result artifacts | The checked public trees expose ROC images/PDFs but no row-bound score/prediction table, challenge labels, immutable row manifest, metric JSON/CSV, or verifier command with public inputs. | Blocks score/response, metric provenance, and consumer gates. |

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | MIDST tabular-diffusion setting and synthesizer names are described, but no immutable target model identities or public challenge target packets are committed. | `Partial` |
| Split semantics | Membership labels and challenge rows are implied by the challenge pipeline, but no immutable public member/nonmember row manifest is committed. | `Fail` |
| Score/response coverage | Public page gives aggregate metrics and ROC plots; no row-level score, prediction, or response table is public. | `Fail` |
| Metric provenance | Metric code exists and the project page reports AUC/TPR, but no safe metric JSON/CSV or no-training verifier is public. | `Partial` |
| Provenance | Code commit and static project-page commit are fixed; runtime result files and challenge inputs are absent. | `Partial` |
| Consumer boundary | The task is tabular synthetic-data/MIDST membership inference, not image-diffusion audit evidence. | `Fail` |
| Surface delta | No public control/delta packet is committed. | `Fail` |

## Decision

`support-only tabular-diffusion public-result-page artifact /
row_bound_score_prediction_packet_missing / no_compute_release`.

MIA-EPT is useful false-promotion pressure because a weak reviewer could promote
it from code availability, static ROC plots, reported AUC/TPR, and a challenge
placement. DiffAudit must not admit it without row identities, row-bound scores
or predictions, labels, metric artifacts, and a verifier.

Allowed wording:

`MIA-EPT is a support-only tabular-diffusion public-result-page surface: code,
ROC figures, and top-line metrics are public, but row-bound scores/predictions,
labels, challenge row identities, and a no-training verifier are absent.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 row;
- N50 external denominator row;
- image-diffusion denominator evidence;
- second public score/response asset;
- compute-release target;
- evidence that image-diffusion MIA routes are portable;
- proof that the MIDST result or MIA-EPT method is wrong.

## Next Action

Do not release compute from this gate. Reopen only if the authors or challenge
organizers publish a compact verifier packet with:

- immutable target/challenge row identities;
- member/nonmember labels or an auditable challenge-label protocol;
- row-bound scores or predictions, plus any submitted prediction ZIP if it is
  needed to bind the challenge result;
- metric JSON/CSV or a no-training metric replay command; and
- provenance hashes for all inputs.
