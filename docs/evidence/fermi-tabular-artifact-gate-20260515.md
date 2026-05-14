# FERMI Tabular Artifact Gate

> Date: 2026-05-15
> Status: multi-relational tabular watch / arXiv-source-only / no public code-score artifact / no download / no GPU release

## Question

Does `FERMI: Exploiting Relations for Membership Inference Against Tabular
Diffusion Models` provide a new executable DiffAudit tabular-diffusion
membership lane after MIDST, or a public score/feature packet that should
change the current `active_gpu_question = none` state?

This is an artifact gate only. It inspects arXiv metadata and the arXiv source
bundle. No tabular datasets, tabular diffusion models, generated synthetic
tables, or training assets were downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `FERMI: Exploiting Relations for Membership Inference Against Tabular Diffusion Models` |
| arXiv | `https://arxiv.org/abs/2605.11527` |
| arXiv version | `v1` |
| arXiv publication date | `2026-05-12` |
| Authors | Abtin Mahyar; Masoumeh Shafieinejad; Yuhan Liu; Xi He |
| Primary category | `cs.LG` |
| arXiv source size | `7,181,010` bytes |
| arXiv source SHA256 | `2951549e2b1fb0b1ecfbac8085e73b1a7df7f6345a04b52d8a6f859e39d8c034` |
| Source entries | `17` entries: TeX files plus PDF figures, no code tree |
| Domain | Multi-relational tabular diffusion membership inference, not image/latent-image DiffAudit admitted scope |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| arXiv Atom metadata | The abstract says FERMI targets multi-relational tabular diffusion membership inference and reports gains across three tabular diffusion architectures and three real-world relational datasets. |
| arXiv source bundle | Contains `00README.json`, TeX files, bibliography/style files, and PDF figures (`method.pdf`, `loss_*.pdf`). It does not contain Python/R code, configs, notebooks, data manifests, CSVs, JSON metrics, checkpoints, or generated synthetic-table outputs. |
| Source URL scan | No `github`, `zenodo`, or `huggingface` URL appears in the source bundle. No code/data availability section was found. |
| `exp.tex` | Evaluates `TabDDPM`, `TabDiff`, and `TabSyn` on Berka, Instacart 05, and California. It reports strong table metrics, but only as paper tables. |
| `appendix.tex` dataset section | Reports target-table sizes: California `1,690,642`, Instacart 05 `1,616,315`, and Berka `1,056,320` target rows. |
| `appendix.tex` evaluation details | Describes `10` shadow models, `1,000` member and `1,000` nonmember records per shadow model, `5` target models, and `200/200` target member/nonmember samples per model. These are experimental details, not released split artifacts. |

Representative paper metrics observed in source tables:

| Setting | Metric evidence |
| --- | --- |
| Direct single-table baseline | Example TabDDPM AUC / TPR@0.1 / TPR@0.01: Berka `.753 / .388 / .266`, Instacart `.949 / .806 / .636`, California `.896 / .640 / .456`. |
| FERMI white-box relational mapping | Example FERMI AUC / TPR@0.1 / TPR@0.01: Berka TabDDPM `.811 / .504 / .350`, Instacart TabDDPM `.967 / .892 / .658`, California TabDiff `.935 / .752 / .550`. |
| Black-box California TabDDPM | Single-table `.687 / .348 / .208`, FERMI `.725 / .424 / .250`, merged `.755 / .496 / .374`. |

The metrics are useful scientific pointers, but they are not reusable DiffAudit
artifacts because the public surface does not bind them to code, splits,
trained targets, score rows, or a replay command.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The paper names TabDDPM, TabDiff, and TabSyn, but no fixed trained target checkpoints, exact training recipes, or synthetic-table output artifacts are released. |
| Exact member split | Fail. The paper describes member sampling from model training splits, but no per-row target member manifests or hashes are public. |
| Exact nonmember split | Fail. The paper describes disjoint nonmember sampling and key-based deduplication, but no nonmember manifests are public. |
| Query/response or score coverage | Fail. No generated synthetic tables, diffusion-loss features, mapped features, score CSVs, ROC arrays, or metric JSON are released. |
| Metric contract | Paper-only. AUC / TPR@0.1 / TPR@0.01 are reported in tables, but there is no verifier or replay packet. |
| Mechanism delta | Pass as a watch item. Multi-relational feature mapping is genuinely different from MIDST nearest-neighbor / shadow-distributional / EPT / Blending++ score-export work. |
| Current DiffAudit fit | Research-only tabular watch. It can inform future multi-table synthetic-data privacy scope, but does not reopen the current MIDST single-table execution lane. |
| GPU release | Fail. Running this would require collecting relational datasets, training TabDDPM/TabDiff/TabSyn targets and shadows, implementing FERMI, and building split/score artifacts from scratch. |

## Decision

`multi-relational tabular watch / arXiv-source-only / no public code-score
artifact / no download / no GPU release`.

FERMI is a meaningful new tabular-diffusion MIA idea and is more relevant than
generic tabular privacy papers because it targets relational side information.
It still does not release a DiffAudit action: there is no public code, no
target/split manifest, no score or feature packet, no generated-table cache,
and no bounded command.

Stop condition:

- Do not train TabDDPM, TabDiff, TabSyn, surrogate models, FERMI mappers, or
  attack MLPs from scratch for this paper inside the current roadmap cycle.
- Do not download California, Instacart, Berka, or other relational tabular
  datasets for FERMI until public target/split/score artifacts or an explicit
  multi-relational tabular lane exists.
- Do not reopen MIDST with FERMI-style feature mapping unless a ready artifact
  appears or the project explicitly expands into multi-relational tabular
  diffusion membership with a new consumer-boundary decision.

## Reflection

This check prevents a likely failure mode: treating a strong latest paper table
as permission to build a new tabular benchmark from scratch. The right state is
watch-only. Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after FERMI
tabular artifact gate`.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted `recon /
PIA baseline / PIA defended / GSA / DPDM W-1` set. FERMI does not add a tabular
product row or Runtime schema.
