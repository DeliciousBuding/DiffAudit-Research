# E2SCT-034 ReMIA Tabular Public Result Archive Check

> Date: 2026-06-09
> Mode: GitHub commit check, raw script reads, and bounded schema inspection of
> the public `experiments.tar.xz` archive in a temp directory; no datasets,
> generator training, model downloads, challenge submissions, or experiments
> Decision: support-only tabular synthetic-data aggregate-result archive; not
> image-diffusion denominator evidence; not admitted; not a second public
> score/response asset; no_compute_release

## Scope

ReMIA surfaced during the search for current public result archives that might
look like a second public score/response asset:

`ReMIA: a Powerful and Efficient Alternative to Membership Inference Attacks
against Synthetic Data Generators` (GitHub `aindo-com/remia`).

This check asks whether the public repository and result archive expose a
row-bound packet: target identity, immutable member/nonmember rows, row-bound
scores or predictions, metric artifacts, provenance hashes, consumer boundary,
and a no-training verifier. It does not evaluate the ReMIA method.

Sources checked:

- `https://github.com/aindo-com/remia`
- `https://github.com/aindo-com/remia/tree/84da2feee749b56639f8c8d9a6bbfffdbc0e87b3`
- `https://raw.githubusercontent.com/aindo-com/remia/84da2feee749b56639f8c8d9a6bbfffdbc0e87b3/scripts/experiments_to_csv.py`
- `https://raw.githubusercontent.com/aindo-com/remia/84da2feee749b56639f8c8d9a6bbfffdbc0e87b3/src/remia.py`

## Public Surface

`git ls-remote` on 2026-06-09 returned:

- main: `84da2feee749b56639f8c8d9a6bbfffdbc0e87b3`

The checked result archive was stored only under:

`%TEMP%\diffaudit-remia-preflight\experiments.tar.xz`

Archive SHA-256:

`26F903EEE3355912BEA3AE8D80E3C066F19556D46A06F374789EF992B2ED1C3E`

The public surface is stronger than a code-only repository because it ships
many run-level JSON results. It is still not a row-bound score/label packet.

| Surface | Observation | Boundary |
| --- | --- | --- |
| Repository identity | Main branch points to `84da2feee749b56639f8c8d9a6bbfffdbc0e87b3`. The repository includes `experiments.tar.xz`, `article/neurips_2026.pdf`, article tables/figures, `scripts/experiments_to_csv.py`, and `src/remia.py`. | Public code and aggregate result archive, fixed for this check. |
| Archive inventory | The archive contains `2,879` JSON files and `0` CSV files. Privacy-result groups include `remia_1.0`, `remia_0.5`, `domias`, `dcr_mia`, `dcr_comparison`, `shadow_modeling_achilles_median`, and `shadow_modeling_achilles_heels`. | Public run archive exists, but files are run summaries. |
| DDPM generator rows | The archive has `60` JSON files under DDPM generator paths, with `12` each for `remia_1.0`, `remia_0.5`, `domias`, `dcr_mia`, and `dcr_comparison`. | DDPM here is a tabular synthetic-data generator setting, not image-diffusion score/response evidence. |
| JSON schema | Recursive schema inspection found `408` list values; the longest list length is `1`; there are `0` lists with length at least `20` and `0` lists with length at least `100`. AUC, accuracy, `n`, and successes are scalar fields. | Blocks row-bound score/label admission. |
| CSV export path | `scripts/experiments_to_csv.py` builds rows from `d["input"]`, `d["output"]["summary"]`, `time`, and `timestamp`, then writes aggregate privacy and quality CSVs if run locally. | The public export path flattens run-level summaries, not per-record scores. |
| ReMIA implementation | `src/remia.py` computes AUC internally from validation hooks and returns scalar readouts such as `auc`, `accuracy`, `n`, `step`, and `auc_diff`. | Internal arrays exist during execution, but the public archive does not expose them. |

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | Dataset, generator, metric, training size, seed, and timestamp are recorded per run, but immutable target model identities and full generator-training artifacts are not packaged as audit targets. | `Partial` |
| Split semantics | Tabular target/control construction is described in code, but no public member/nonmember row manifest or label table is exposed. | `Fail` |
| Score/response coverage | No row-level score, prediction, label, generated table row, or response packet was found in the JSON archive. | `Fail` |
| Metric provenance | Aggregate AUC/accuracy and significance fields are public, and code explains how summaries are produced, but there is no no-training metric replay over row-level public inputs. | `Partial` |
| Provenance | Commit and archive hash are fixed for this check; runtime inputs and row-level arrays are absent from the public package. | `Partial` |
| Consumer boundary | The task is tabular synthetic-data privacy, not image-diffusion membership auditing. | `Fail` |
| Surface delta | No public label-shuffle, permutation, or surface-delta control packet is exposed as a row-bound verifier. | `Fail` |

## Decision

`support-only tabular synthetic-data aggregate-result archive /
aggregate_run_json_only / no_compute_release`.

ReMIA should not enter the current image-diffusion E2 denominator. It also does
not provide the second public score/response asset needed for Direction A. The
public archive is useful only as a route-closure sidecar: it shows that a fresh
result archive with many aggregate JSON files can still lack row-bound
membership scores or labels.

Allowed wording:

`ReMIA is a support-only tabular synthetic-data public result archive. It ships
aggregate JSON summaries, including DDPM-generator tabular settings, but the
public archive does not expose row-bound scores, labels, predictions, metric
replay inputs, or a no-training verifier.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 row;
- N50 external denominator row;
- image-diffusion denominator evidence;
- second public score/response asset;
- compute-release target;
- proof that ReMIA or its reported tabular result is wrong;
- evidence that image-diffusion MIA routes transfer to tabular synthetic data.

## Next Action

Do not release compute from this gate. Reopen only if the authors publish a
compact verifier packet with:

- immutable target and row identities;
- member/nonmember labels or an auditable challenge-label protocol;
- row-bound scores, predictions, responses, or generated-row packets;
- metric JSON/CSV or a no-training metric replay command over public inputs;
- hashes for all inputs; and
- label-shuffle, permutation, or surface-delta controls.
