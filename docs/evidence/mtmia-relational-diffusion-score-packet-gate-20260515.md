# MT-MIA Relational Diffusion Score Packet Gate

> Date: 2026-05-15
> Status: relational tabular diffusion score-packet public / cross-modal support-only / no dataset-model download / no GPU release / no admitted row

## Question

Does `joshward96/MT-MIA` provide a clean Lane A artifact after FERMI remained
arXiv-source-only: public target/split evidence plus reusable diffusion
synthetic-data membership score packets?

This was a metadata and score-packet gate. It inspected the official GitHub
tree at commit `d02aebb9241b383f08a4f89cc32054cf283c2ec6`, the README, split
directories, synthetic-data directories, and result JSONL files. Only the
official `results/{clava_ddpm,reldiff}/*/mtmia_seed_*.jsonl` metric/score
packets were downloaded to temporary storage for extraction. No original raw
data, synthetic CSV payloads, model checkpoints, full repository clone, or GPU
work was used.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Finding Connections: Membership Inference Attacks for the Multi-Table Synthetic Data Setting` |
| Repository | `https://github.com/joshward96/MT-MIA` |
| Checked commit | `d02aebb9241b383f08a4f89cc32054cf283c2ec6` |
| Public license file | none observed in the checked tree |
| Diffusion generators checked | `ClavaDDPM`, `RelDiff` |
| Datasets checked | `airbnb`, `airlines`, `california` |
| Domain | Multi-table relational synthetic-data membership inference, not current image/latent-image DiffAudit admitted scope |

The README states that the repository is the official implementation and that
it includes pre-processed real data with fidelity metrics under `data/`,
pre-generated synthetic data under `synth_data/`, and all MT-MIA and
single-table attack runs under `results/`. It also states that RelDiff
generation required about `450` H200 GPU-hours, which is why the present gate
does not regenerate synthetic data.

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `data/{airbnb,airlines,california}/split/{mem,non_mem,ref}/` | Public split directories exist for member, nonmember, and reference data. They contain relational CSV tables such as `user/session`, `activity/loyalty_history`, and `household/individual`, plus schema metadata where applicable. |
| `synth_data/clava_synth/*/seed_{42,43,44}/` | Public pre-generated ClavaDDPM synthetic relational tables and `multi_quality.pkl` files exist for all three datasets and seeds. |
| `synth_data/reldiff_synth/*/seed_{42,43,44}/` | Public pre-generated RelDiff synthetic relational tables and `multi_quality.pkl` files exist for all three datasets and seeds. |
| `results/clava_ddpm/*/mtmia_seed_*.jsonl` | `9` official ClavaDDPM MT-MIA JSONL score/metric packets exist, totaling `38,490,744` bytes. Each parsed packet exposes `full.results` and `full.scores`. |
| `results/reldiff/*/mtmia_seed_*.jsonl` | `9` official RelDiff MT-MIA JSONL score/metric packets exist, totaling `29,823,763` bytes. Each parsed packet exposes `full.results` and `full.scores`. |
| `src/synth_mia/base.py` and `src/utils.py` | The attack/evaluation code defines the score/metric machinery used by `run_MTMIA.py`, including AUC and fixed-FPR TPR outputs. |

The `18` checked diffusion result packets total `68,314,507` bytes and each
final packet contains `2,000` scores. The JSONL packets include official metric
summaries and score arrays, but they do not attach row-level IDs to each score.
That is enough for Research-side score-packet support evidence, not for a
Platform/Runtime row.

Machine-readable summary:
[`mtmia-relational-diffusion-score-packet-gate-20260515.json`](mtmia-relational-diffusion-score-packet-gate-20260515.json).

## Parsed Metric Summary

`TPR@0.1%FPR` maps to the repository field `tpr_at_fpr_0.001`; `TPR@1%FPR`
maps to `tpr_at_fpr_0.01`.

| Generator | Dataset | Seeds | Best AUC range | Mean best AUC | Max TPR@0.1%FPR | Max TPR@1%FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `clava_ddpm` | `airbnb` | `3` | `0.794686-0.813183` | `0.801208` | `0.015` | `0.097` |
| `clava_ddpm` | `airlines` | `3` | `0.752103-0.766168` | `0.759413` | `0.205` | `0.348` |
| `clava_ddpm` | `california` | `3` | `0.644946-0.746011` | `0.703928` | `0.192` | `0.260` |
| `reldiff` | `airbnb` | `3` | `0.608931-0.631966` | `0.623403` | `0.044` | `0.065` |
| `reldiff` | `airlines` | `3` | `0.520509-0.526468` | `0.523063` | `0.001` | `0.014` |
| `reldiff` | `california` | `3` | `0.645424-0.651050` | `0.648407` | `0.211` | `0.253` |

This is a materially better public surface than FERMI's paper-only tabular
state: MT-MIA has official splits, synthetic outputs, and result packets.
It is still not a current image/latent-image execution target or product row.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Partial. The public surface fixes generator family, dataset, and seed through directory names and scripts, but it does not provide reusable trained model checkpoint identities. It provides pre-generated synthetic tables instead. |
| Exact member split | Pass for Research-side relational-tabular support. Public `split/mem` relational CSVs are committed for each dataset. |
| Exact nonmember split | Pass for Research-side relational-tabular support. Public `split/non_mem` relational CSVs are committed for each dataset. |
| Query/response or score coverage | Pass as score/metric support. Official MT-MIA JSONL packets expose `full.results` and `full.scores` for ClavaDDPM and RelDiff. They are not row-ID-bound score manifests. |
| Metric contract | Pass for CPU-only artifact reading. The packets report AUC and fixed-FPR TPR values; no recomputation from raw data was needed for this gate. |
| Mechanism delta | Pass as cross-domain support. This is relational multi-table synthetic-data membership, different from MIDST single-table nearest-neighbor/shadow/EPT/Blending++ and different from image response-distance or denoising-loss routes. |
| Current DiffAudit fit | Cross-modal watch/support only. It can inform future tabular or paperization scope, but the current Platform/Runtime admitted set is image/latent diffusion evidence only. |
| GPU release | Fail. No GPU is needed to read the score packets, and regenerating RelDiff synthetic data would be high-cost and unnecessary for the current decision. |

## Decision

`relational tabular diffusion score-packet public / cross-modal support-only /
no dataset-model download / no GPU release / no admitted row`.

MT-MIA should be retained as a real public score-packet artifact for
multi-table relational synthetic-data membership inference. It is stronger than
paper-only tabular watch items because the checked repository publishes
member/nonmember/reference splits, pre-generated ClavaDDPM and RelDiff
synthetic tables, and official MT-MIA score/metric JSONL packets.

It does not change the active DiffAudit execution slots. The artifact is
outside the current image/latent-image consumer boundary, lacks row-level
score IDs suitable for a product row, has no reusable trained checkpoint
identity, and has no reviewed relational-tabular Platform/Runtime schema.
Current slots remain `active_gpu_question = none`, `next_gpu_candidate =
none`, and `CPU sidecar = none selected after MT-MIA relational diffusion
score-packet gate`.

Stop condition:

- Do not download the raw figshare datasets, synthetic CSV payloads, ClavaDDPM
  or RelDiff training assets, or the full repository in the current roadmap
  cycle.
- Do not regenerate ClavaDDPM or RelDiff synthetic data; the public result
  packets already answer the artifact gate, and RelDiff generation is
  explicitly high-cost.
- Do not promote MT-MIA into Platform/Runtime rows, schemas, product copy, or
  defense claims without an explicit relational-tabular consumer-boundary
  decision and row-level score/ID semantics.
- Reopen only if DiffAudit opens a relational tabular synthetic-data
  membership lane, if authors publish row-ID-bound verifier artifacts, or if a
  paperization task needs clearly labeled cross-domain support evidence.

## Reflection

This was not stationery: it found a new public artifact class with real score
packets and then bounded it to the correct consumer layer. The useful result is
not another local experiment, but a sharper distinction: public relational
diffusion score packets exist, while the current image/latent Platform/Runtime
boundary still does not change.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
