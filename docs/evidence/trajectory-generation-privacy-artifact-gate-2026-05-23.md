# Trajectory Generation Privacy Artifact Gate

> Date: 2026-05-23
> Status: cross-domain trajectory paper-source-only watch / diffusion trajectory MIA weak / no code-score artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2605.15246` / `Privacy Evaluation of Generative Models for
Trajectory Generation` expose a public DiffAudit-ready target, split, score
packet, or verifier that should change the active Research slots?

This was selected as a single Lane A metadata gate because it is a recent
generative-model privacy paper that explicitly includes diffusion trajectory
models and membership inference. The check used arXiv API metadata, arXiv
source inventory, paper text, and GitHub repository/code searches. It did not
download trajectory datasets, model checkpoints, generated trajectories, or run
any attack code.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Privacy Evaluation of Generative Models for Trajectory Generation` |
| arXiv | `https://arxiv.org/abs/2605.15246v1` |
| Published / updated | `2026-05-14T10:57:34Z` |
| Venue note | accepted at MuseKDE 2026, co-located with IEEE MDM 2026 |
| Domain | trajectory generation / mobility data, not current image or latent-image DiffAudit scope |
| Models checked in paper | LSTM-TrajGAN, MoveSim, DiffTraj, Diff-RNTraj |
| arXiv source inventory | `106,622` byte source tarball, SHA-256 `EA94CCE4DB20634E4B1E776AA09D8E2E3F2D5B6D402057DD33CB4BFE6AAABEF4`, `5` entries: `00README.json`, `IEEEtran.bst`, `IEEEtran.cls`, `main.tex`, `ref.bib` |
| GitHub search | exact-title, arXiv-id, author/title, and trajectory-generation topic repository/code searches returned no official repository, code, score, or artifact hits |

The source tarball contains LaTeX material only:

```text
00README.json
IEEEtran.bst
IEEEtran.cls
main.tex
ref.bib
```

No `.py`, notebook, trained model artifact, member/nonmember manifest, score
rows, ROC arrays, metric JSON, generated trajectory packet, or verifier output
is public in the checked surface.

## Paper Metrics

The paper evaluates membership scores on member trajectories from training
data and nonmember trajectories from held-out data. For the two
diffusion-based models, the membership score is the negative average noise
prediction MSE over `50` randomly sampled timesteps.

These values are paper-source table values from `main.tex`, not locally
replayed artifacts:

| Model | Family | Eval set | Reported AUC-ROC |
| --- | --- | ---: | ---: |
| LSTM-TrajGAN | GAN | `2,052 / 1,027` | `0.5029` |
| MoveSim | GAN | `7,000 / 2,500` | `0.7002` |
| DiffTraj | DM | `2,000 / 2,000` | `0.5012` |
| Diff-RNTraj | DM | `2,000 / 2,000` | `0.4949` |

The only clearly positive value is the GAN `MoveSim` discriminator-score
result. The diffusion trajectory results are near random, so this paper does
not provide a positive diffusion-model asset or a reason to open a trajectory
execution lane.

## Gate Result

| Gate | Result |
| --- | --- |
| Current image/latent-image fit | Fail. The paper is about trajectory/mobility generation, not image or latent-image diffusion. |
| Target identity | Fail. The paper names existing trajectory generators, but no paper-bound model checkpoint hashes, revisions, or bundles are released. |
| Exact member split | Fail. Member counts are reported, but no immutable row IDs, user IDs, trajectory IDs, seeds, or manifests are released. |
| Exact nonmember split | Fail. Held-out counts are reported, but no immutable nonmember manifests are released. |
| Query/response or score coverage | Fail. The release has paper tables only; no generated trajectory packet, per-row score file, ROC array, metric JSON, or verifier output is public. |
| Mechanism delta | Fail for execution. The diffusion-model path is standard loss-based denoising MSE and reports near-random AUC. |
| Download justification | Fail. Downloading Foursquare, GeoLife, DiDi, model checkpoints, or trajectory payloads would not evaluate a released score packet. |
| GPU release | Fail. The blocker is missing artifacts plus weak diffusion trajectory metrics, not local compute. |

## Decision

`cross-domain trajectory paper-source-only watch / diffusion trajectory MIA weak
/ no code-score artifact / no download / no GPU release / no admitted row`.

The paper is useful only as cross-domain boundary evidence: generative
trajectory privacy can include MIA-style evaluation, but the checked public
surface does not expose a reusable asset, and the diffusion trajectory results
are not positive. Keep it out of Platform/Runtime and out of the current
image/latent-image Lane A asset path.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after trajectory generation privacy artifact
gate`.

Smallest valid reopen condition:

- authors publish official code plus exact trajectory member/nonmember
  manifests, model checkpoint revisions or hashes, generated trajectory
  packets, per-row scores, ROC arrays, metric JSON, and a verifier; or
- DiffAudit explicitly opens a trajectory/mobility consumer boundary and the
  public release includes row-bound score artifacts that do not require
  reconstructing training from the paper.

Stop condition:

- Do not download Foursquare NYC, GeoLife, DiDi Chengdu, generated
  trajectories, trajectory-model checkpoints, or trajectory preprocessing
  assets from this gate.
- Do not implement trajectory discriminator-score or diffusion-loss attacks,
  train LSTM-TrajGAN, MoveSim, DiffTraj, or Diff-RNTraj, or open CPU/GPU
  sidecars from the paper.
- Do not add Platform/Runtime rows, schemas, product copy, or recommendation
  logic until a reviewed trajectory consumer boundary and row-bound artifacts
  exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
