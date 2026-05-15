# Tabular Privacy Leakage TDM Artifact Gate

> Date: 2026-05-15
> Status: single-table tabular diffusion watch-plus / official code-public / no paper score packet / no download / no GPU release

## Question

Does `On Privacy Leakage in Tabular Diffusion Models: Influential Factors,
Attacker Knowledge, and Metrics` provide a new executable DiffAudit lane, a
ready MIDST/ClavaDDPM score packet, or a consumer-boundary change after the
FERMI and MT-MIA tabular checks?

This is an artifact gate only. It inspects the arXiv record/source bundle and
the official code surface linked from the paper. It does not download Berka,
Diabetes, MIDST Google Drive resources, trained targets, generated synthetic
tables, or attack result packets.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `On Privacy Leakage in Tabular Diffusion Models: Influential Factors, Attacker Knowledge, and Metrics` |
| arXiv | `https://arxiv.org/abs/2605.06835` |
| arXiv version | `v1` |
| arXiv publication date | `2026-05-07` |
| Authors | Masoumeh Shafieinejad; D. B. Emerson; Behnoosh Zamanlooy; Elaheh Bassak; Fatemeh Tavakoli; Sara Kodeiri; Marcelo Lotif; Xi He |
| Primary category | `cs.LG` |
| arXiv source size | `7,335,590` bytes |
| arXiv source SHA256 | `3BC7EBAA21BFA05E0825CFE67780B7AE5167509242BBAD3A5D16B7807D5002EE` |
| Source entries | `56` entries: one TeX file, one bibliography, one style file, one `00README.json`, and `52` PDF figures |
| Official code link in paper | `https://github.com/VectorInstitute/midst-toolkit` |
| Toolkit main commit checked | `e0a3b3ee07fd1245a0d8617afa028f3988c7e812` |
| Toolkit main tree | `321` blobs totaling `194,506,541` bytes |
| Domain | Single-table tabular diffusion privacy leakage, not current image/latent-image admitted scope |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| arXiv Atom metadata | The record is `v1`, published and updated on `2026-05-07`, with title and authors matching the source. |
| arXiv source bundle | Contains only paper source and figures. No Python/R code, notebook, config, CSV, JSON score row, ROC array, checkpoint, generated synthetic-table output, or metric packet is included. |
| Paper methodology | The paper studies ClavaDDPM single-table synthesis on Berka and Diabetes with Tartan Federer and Ensemble MIDST attacks, plus heuristic privacy metrics such as DCR, NNDR, HR, and EIR. |
| Paper official code footnote | The paper points to `VectorInstitute/midst-toolkit` for model training and attack code. |
| `midst-toolkit` main tree | The toolkit exposes ClavaDDPM training/synthesis code, Tartan Federer attack code, Ensemble attack code, EPT attack code, privacy/quality metrics, examples, and tests. |
| `midst-toolkit` committed test assets | The main tree commits small integration-test TabDDPM assets: `6` `None_trans_ckpt.pkl` files of about `19.4 MB` each, `6` cluster checkpoints, and `6` `challenge_label.csv` files with `200` labels each (`100` member and `100` nonmember). |
| `midst-toolkit` README/examples | The Tartan Federer and Ensemble examples still instruct users to download MIDST resources from Google Drive for real runs; the Tartan Federer README says the public example currently has only `6` target models and still has a TODO to train/upload `30` target models. |
| Targeted branch scan | Public `ft/*`, `sk/*`, `target_model`, and `marcelo/tabsyn*` branches add or modify configs, scripts, tutorial/test assets, and TabSyn preprocessing. They do not expose Berka/Diabetes paper target checkpoints, immutable split manifests, generated synthetic tables, score rows, ROC arrays, metric JSON, or ready verifier outputs. |

Representative paper setup facts from the source:

| Setting | Evidence |
| --- | --- |
| Default target models | ClavaDDPM-style DNN diffusion targets with `2,000` diffusion timesteps and `200,000` training steps. |
| Berka target setup | `10` target models, each trained on `20,000` records, each generating `20,000` synthetic records, with a `200`-row challenge set per target. |
| Diabetes target setup | `3` target models, each using `10,000` training/synthetic samples and a `1,000`-row challenge set. |
| Tartan Federer attack | Default features use `300` Gaussian noise draws and `7` timesteps, producing `2,100` features per candidate. |
| Compute disclosure | Default Tartan Federer takes about `2.5` hours for Berka and `1` hour for Diabetes on A40; Ensemble takes about `16` hours for Berka and `11` hours for Diabetes on A100. |

The committed toolkit test assets are useful for package-level integration
tests, but they are not the paper's Berka/Diabetes result packet and do not
bind the paper tables to released target identities, score rows, ROC arrays,
or metric JSON.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for the paper experiments. The paper names ClavaDDPM target configurations, and `midst-toolkit` commits small test checkpoints, but no Berka/Diabetes paper target checkpoint set is released. |
| Exact member split | Fail for the paper experiments. The toolkit has small test `challenge_label.csv` files, but no paper Berka/Diabetes immutable member manifests or row hashes are public. |
| Exact nonmember split | Fail for the paper experiments. The toolkit test labels include balanced nonmembers, but no public nonmember split for the paper experiments is released. |
| Query/response or score coverage | Fail. No paper generated synthetic tables, Tartan Federer loss-feature rows, Ensemble feature rows, predictions, score CSVs, ROC arrays, or metric JSON are released. |
| Metric contract | Paper-only for the reported results. The toolkit can compute attacks/metrics after execution, but there is no ready replay packet for the paper tables. |
| Mechanism delta | Pass as a watch-plus item. The paper is a systematic single-table TDM privacy-leakage study over training setup, attacker knowledge, and heuristic metrics, distinct from FERMI's multi-relational mapping and MT-MIA's relational score packets. |
| Current DiffAudit fit | Research-only tabular watch-plus. It can inform future tabular synthetic-data privacy scope but does not reopen MIDST execution or change image/latent-image consumer rows. |
| GPU release | Fail. Reproducing the paper would require external datasets/resources, target and shadow training, attack feature extraction, and result generation from scratch. |

## Decision

`single-table tabular diffusion watch-plus / official code-public / no paper
score packet / no download / no GPU release`.

This paper and toolkit are stronger than an arXiv-source-only tabular watch
because the official MIDST toolkit is public and includes real attack/model
implementations plus small test assets. The public surface still does not
release the paper's Berka/Diabetes target identities, immutable split
manifests, generated synthetic tables, per-sample scores, ROC arrays, metric
JSON, or ready verifier outputs.

Stop condition:

- Do not download Berka, Diabetes, MIDST Google Drive resources, ClavaDDPM
  checkpoints, generated synthetic tables, or paper result artifacts for this
  lane.
- Do not train ClavaDDPM targets/shadows, run Tartan Federer/Ensemble/EPT,
  or generate paper result packets from scratch inside the current roadmap
  cycle.
- Do not promote toolkit test assets into Platform/Runtime rows; they are
  package-level test fixtures, not an admitted DiffAudit evidence packet.
- Do not reopen MIDST/tabular execution unless public paper-bound target,
  split, score/ROC/metric artifacts appear or the project explicitly opens a
  reviewed tabular consumer-boundary lane.

## Reflection

This check separates three things that are easy to conflate: a latest tabular
privacy paper, an official reusable toolkit, and a paper-bound replay artifact.
Only the first two are public. The current slots remain
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after Tabular Privacy Leakage TDM artifact gate`.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted `recon /
PIA baseline / PIA defended / GSA / DPDM W-1` set. This tabular watch-plus line
does not add a product row, Runtime schema, download policy, CPU sidecar, or GPU
task.
