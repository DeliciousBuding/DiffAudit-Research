# Rectified Flow MIA Artifact Gate

> Date: 2026-05-15
> Status: paper-source-only rectified-flow MIA mechanism watch / promised GitHub repo empty / no code-score artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2603.13421` / `Generalization and Memorization in Rectified Flow`
provide a non-duplicate image generative-model membership-inference artifact
that should change DiffAudit's `active_gpu_question`, `next_gpu_candidate`, or
Platform/Runtime admitted boundary?

This gate was opened because the paper is not another SecMI/PIA/CLiD/CopyMark
variant on diffusion checkpoints. It targets Rectified Flow / Flow Matching
models and proposes rectified-flow-specific MIA test statistics. The check used
arXiv API metadata, the arXiv source tarball, GitHub metadata, and git remote
reference probing. It did not download CIFAR-10, SVHN, TinyImageNet, model
checkpoints, generated images, or run any training / attack code.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Generalization and Memorization in Rectified Flow` |
| arXiv | `https://arxiv.org/abs/2603.13421v1` |
| Published / updated | `2026-03-12T21:10:39Z` |
| Authors | Mingxing Rao, Daniel Moyer |
| Source tarball inspected | `1,184,212` bytes, `25` entries |
| Claimed code repository in arXiv source | `https://github.com/mx-ethan-rao/MIA_Rectified_Flow.git` |
| GitHub repo state | Public repo exists, default branch `master`, size field `0`, no license, pushed `2026-03-12T20:43:21Z`, but GitHub reports `Git Repository is empty` and `git ls-remote` returns no refs |

The arXiv source contains TeX plus figure PDFs only. It does not ship raw data
splits, checkpoints, score rows, ROC arrays, metric JSON, verifier output, or a
script entrypoint. The paper text says data splits, model checkpoints,
training, and testing code are released in the GitHub repository, but the live
repository is currently empty.

## Mechanism Signal

The paper proposes three MIA statistics for Rectified Flow:

| Statistic | Role |
| --- | --- |
| `T_naive` | Flow-matching-objective-derived baseline statistic |
| `T_mc` | Monte Carlo estimator over Gaussian source samples |
| `T_mc_cal` | Complexity-calibrated `T_mc`, dividing by an image complexity proxy based on compressed byte length |

The mechanism is materially different from the recent closed repeats because
it targets Flow Matching / Rectified Flow vector fields and the midpoint of the
ODE trajectory, not DDPM denoising loss, SecMI reverse denoise distance, PIA
perturbation trajectories, CLiD prompt-conditioned likelihoods, CopyMark
benchmark score packets, or final-layer gradient variants.

The paper also proposes a mitigation direction: replace uniform timestep
sampling with a Symmetric Exponential / U-shaped distribution to reduce
exposure to vulnerable midpoint timesteps.

## Reported Metrics

These are paper-source metrics read from the arXiv source, not locally
replayed.

| Dataset | Split / training setup | `T_mc` AUC | `T_mc` TPR@1%FPR | `T_mc_cal` AUC | `T_mc_cal` TPR@1%FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| CIFAR-10 | `25k/25k`, `32x32`, `500k` RF training steps | `75.12` | `3.05` | `84.89` | `27.88` |
| SVHN | `20k/20k`, `32x32`, `500k` RF training steps | `70.92` | `1.54` | `79.43` | `16.46` |
| TinyImageNet | `50k/50k`, `64x64`, `100k` RF training steps | `76.44` | `5.33` | `92.96` | `50.03` |

The reported gains from `T_mc` to `T_mc_cal` are large:
`+9.77` AUC / `+24.83` TPR points on CIFAR-10, `+8.51` / `+14.92` on SVHN,
and `+16.52` / `+44.70` on TinyImageNet, on the paper's percentage scale.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Fail for execution. The paper reports RF models and training settings, but the promised checkpoint repository is empty and no checkpoint hashes or model files are public. |
| Exact member split | Fail. The paper gives split sizes, but no immutable train/validation index files or row manifests are public. |
| Exact nonmember split | Fail for the same reason: validation split sizes are described, not released as machine-readable manifests. |
| Query/response or score coverage | Fail. No score rows, ROC arrays, metric JSON, generated response packets, or verifier outputs are public. |
| Mechanism delta | Pass for watch. Rectified Flow midpoint memorization and complexity-calibrated Monte Carlo vector-field scoring are non-duplicate mechanisms. |
| Download justification | Fail. There is no bounded public artifact to download; implementing RF training or attacks from the paper would create a new project rather than evaluate a released packet. |
| GPU release | Fail. The missing pieces are public artifacts, not local compute. |

## Decision

`paper-source-only rectified-flow MIA mechanism watch / promised GitHub repo
empty / no code-score artifact / no download / no GPU release / no admitted
row`.

Rectified Flow MIA is worth tracking because it is a genuinely different
generative-model family and has reported low-FPR gains that are large enough to
matter if artifacts appear. It is not a current DiffAudit execution lane. The
live public surface has no released code, split manifest, checkpoint, score,
ROC, metric, or verifier packet.

Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and
`CPU sidecar = none selected after Rectified Flow MIA artifact gate`.

Smallest valid reopen condition:

- `mx-ethan-rao/MIA_Rectified_Flow` becomes non-empty with the promised public
  data splits, model checkpoints, training code, and testing code; or
- authors publish small immutable split/checkpoint/score/ROC/metric/verifier
  artifacts sufficient for a bounded no-training replay; and
- a consumer-boundary note decides whether Rectified Flow image-generation MIA
  belongs beside diffusion-model rows or stays as Research-only mechanism
  evidence.

Stop condition:

- Do not download CIFAR-10, SVHN, TinyImageNet, RF checkpoints, generated
  images, or any large payload for this line.
- Do not implement `T_naive`, `T_mc`, `T_mc_cal`, complexity calibration, or
  Symmetric Exponential training from the paper.
- Do not train Rectified Flow models, launch GPU work, create Platform/Runtime
  rows, change schemas, or change product copy until public artifacts exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
