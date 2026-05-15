# Hyperparameter-Free SecMI Reproduction Gate

> Date: 2026-05-15
> Status: third-party SecMI-family code/report surface / no reusable score packet / no download / no GPU release / no admitted row

## Question

Does `mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models`
provide a new DiffAudit replay target, public score packet, or independent
image-diffusion membership asset?

This was a Lane A public-surface gate only. It inspected GitHub repository
metadata, the recursive tree, README claims, selected source files, docs
metadata, and notebook output surface. No repository clone, SecMI checkpoint,
CIFAR dataset, SharePoint bundle, cache, attack output, plot payload, or GPU
job was downloaded or executed.

## Public Surface

| Field | Value |
| --- | --- |
| Repository | `https://github.com/mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models` |
| Description | `We make a comprehensive Survey for MIA against Diffusion Models and propose new attacks.` |
| Created / pushed / updated | `2026-03-21T09:32:27Z` / `2026-03-21T09:46:20Z` / `2026-03-21T09:46:23Z` |
| Default branch / commit | `main` / `3a8855cb54bbff9d15fb19e734b2feadd0cb12bb` |
| Commit message | `Initial commit: SecMI + Hyperparameter-free SecMI` |
| Repo size field | `1,992` KB |
| License | none declared in GitHub metadata |
| Releases / tags | `0` releases / `0` tags |
| Recursive tree | `16` blobs, `2,472,985` total blob bytes |
| Large committed blobs | `docs/DGM_Project_Final_Report.pdf` (`1,230,776` bytes), `secmia_official_plus_hyperfree_clean.ipynb` (`1,113,821` bytes) |

## What Is Present

| Source | Finding |
| --- | --- |
| `README.md` | Frames the project as a SecMI implementation plus a hyperparameter-free SecMI extension. It reports CIFAR-100 seed-0 metrics: baseline SecMINNs `AUC = 0.971`, `TPR@1%FPR = 0.519`; hyperparameter-free multi-timestep variant `AUC = 0.984`, `TPR@1%FPR = 0.642`. |
| `run.py` | Provides `train`, `full`, and `robustness` commands that clone `jinhaoduan/SecMI`, ensure official checkpoints, train baseline SecMINNs and a multi-timestep neural attacker, print AUC / TPR@1%FPR, and save ROC PNGs. |
| `secmia_mia/config.py` | Auto-clones `https://github.com/jinhaoduan/SecMI` into `SecMI_official/` and expects official member split files under that clone. |
| `secmia_mia/download.py` | Attempts to download the official SecMI SharePoint checkpoint folder into `checkpoints_official/` when local `.pt` files are absent. |
| `secmia_mia/data.py` | Loads CIFAR-10/CIFAR-100 via `torchvision` with `download=True`, then builds attacker train/aux/eval splits from official SecMI member split files. |
| `secmia_mia/attackers.py` | Defines baseline SecMINNs and a multi-timestep neural attacker, caching generated error maps locally as `.pt` files. |
| Notebook and docs | The notebook contains embedded output/plot surface and the docs include a course report and literature survey, but there is no separate committed score CSV/JSONL, ROC array, metric JSON, or verifier packet. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for independent replay. The workflow depends on the official SecMI checkpoints from SharePoint and local SecMI clone state, not a new committed target checkpoint or deterministic target recreation packet. |
| Exact member split | Partial as SecMI support only. It reuses official SecMI split files when present, but does not commit a new immutable member/nonmember manifest. |
| Query/response or score coverage | Fail. The repository ships code, a notebook, and reports, but no per-sample score rows, ROC arrays, metric JSON, generated response packet, trained attacker weights, or no-training verifier output. |
| Mechanism delta | Partial. Multi-timestep learned aggregation removes manual `t`/`k` selection, but it remains a SecMI-family learned attacker over generated error maps rather than an independent image/latent-image asset or new Platform/Runtime consumer row. |
| Download justification | Fail. Running it would require cloning SecMI, acquiring SecMI official checkpoints, downloading CIFAR, computing caches, and training attackers from scratch to reproduce a course-project metric. |
| GPU release | Fail. There is no small public score packet, frozen target artifact, or bounded verifier command that changes the current Research decision. |

## Decision

`third-party SecMI-family code/report surface / no reusable score packet / no
download / no GPU release / no admitted row`.

This repository is stronger than a README-only stub because it exposes runnable
source code and a notebook/report surface, but it does not change DiffAudit's
current SecMI boundary. Existing SecMI is already a strong Research supporting
reference and remains blocked from Platform/Runtime admission by consumer
semantics, adaptive comparability, provenance language, and admitted-bundle
schema fit. The newer `neilkale/quantile-diffusion-mia` gate already records a
small public third-party SecMI-style score packet; this hyperparameter-free
SecMI repository does not add a reusable score packet on top of that.

Smallest valid reopen condition:

- Public per-sample score rows for baseline and hyperparameter-free SecMI with
  image IDs and split identity;
- ROC arrays or metric JSON for those score rows;
- trained attacker weights or a no-training verifier that reads public
  artifacts; and
- a consumer-boundary review explicitly deciding that third-party SecMI-family
  packets can enter paperization support without becoming admitted rows.

Stop condition:

- Do not clone the full repository by default.
- Do not download CIFAR-10/CIFAR-100, the official SecMI SharePoint
  checkpoints, SecMI clone assets, or generated caches from this gate.
- Do not run `python run.py train`, `python run.py full`, robustness runs, the
  notebook, or attacker training in the current roadmap cycle.
- Do not promote hyperparameter-free SecMI into Platform/Runtime rows, product
  copy, recommendation logic, or the admitted evidence bundle.

## Reflection

This gate is a narrow anti-duplication record, not a new experiment. It stops a
plausible but low-value path before it turns into another same-family SecMI
reproduction project. Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after
hyperparameter-free SecMI reproduction gate`.

## Platform and Runtime Impact

None. Hyperparameter-free SecMI remains Research-only support-family evidence.
Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
