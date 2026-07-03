# ReDiffuse STL-10 Bounded Scout

> Date: 2026-05-25
> Status: bounded scout completed / score packet produced / weak denoising-loss signal / no GPU expansion

## Question

After the STL-10 split and resource preflight, can a short ReDiffuse DDPM/STL-10
target produce a scoreable membership packet, and does fixed-timestep
denoising-loss show any immediate membership signal?

This is a bounded scout, not a paper-level ReDiffuse reproduction. It does not
claim a trained STL-10 DDPM benchmark, does not use full-paper training length,
and does not promote Platform/Runtime evidence.

## Frozen Contract

| Field | Value |
| --- | --- |
| Target family | Official ReDiffuse DDPM `UNet` + `GaussianDiffusionTrainer` |
| Dataset | STL-10 unlabeled |
| Split source | `STL10_train_ratio0.5.npz` |
| Train member subset | `1024` samples from official member split |
| Score packet | `256` trained members + `256` official nonmembers |
| Training budget | `300` steps, batch `32` |
| Hard guards | `900s` wall-clock or `7.4 GB` allocated CUDA memory |
| Score definition | `score = -mean_fixed_timestep_denoising_mse` |
| Score timesteps | `50`, `200`, `500`, `800` |
| Seed | `20260525` |
| CUDA env | `conda run -n diffaudit-research python` |

Batch `32` was selected instead of `64` for the scout because live free VRAM
before the run was only about `4.6 GB`, while the earlier batch-64 calibration
had peaked at `4.419 GB`. This was a safety change, not a change in hypothesis.

## Run Artifacts

Artifacts are stored outside Git under:
`<DOWNLOAD_ROOT>/shared/runs/rediffuse-stl10-bounded-scout-20260525/`.

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `summary.json` | `2,243` bytes | `02cfe2af7346e7b380608ef748d164031ec89ba67d10822ef9d0badb8c3b209e` |
| `scores.csv` | `28,732` bytes | `c0f396502114986c8c3549f626ce5083fcaaec2fcf8a319aabe509588d8abd0a` |
| `checkpoint-step-final.pt` | `573,473,892` bytes | `006f5247ef2f91a331a097d16bdf1c153f94f3c2f112e1e9b8d3efdd5bb2ec5e` |
| `run_rediffuse_stl10_bounded_scout.py` | `10,945` bytes | `4ee76c37594cb7834459b3059f8c0af58c1eabb5c34323275f3990c8c9933d1f` |

The script was intentionally kept as a run artifact rather than promoted into a
repo CLI. The run answered the decision question without needing a new reusable
tool surface.

## Result

| Metric | Value |
| --- | ---: |
| Completed steps | `300` |
| Stop reason | `step_budget` |
| Elapsed time | `92.750s` |
| Peak allocated VRAM | `2.430 GB` |
| First training loss | `1.0019083023` |
| Last training loss | `0.0491645448` |
| Mean last-25 loss | `0.0447090799` |
| Score packet size | `256` members + `256` nonmembers |
| AUC | `0.4996337890625` |
| ASR | `0.509765625` |
| TPR@1%FPR | `0.01171875` |
| TPR@0.1%FPR | `0.0` |
| Nonmember denominator | `256` |
| Minimum nonzero FPR | `0.00390625` |

The target did train in the narrow engineering sense: loss fell quickly over
the `300` steps, and a checkpoint plus row-level score packet were produced.
The membership signal is effectively random under this fixed-timestep
denoising-loss scorer.

## Decision

`bounded scout completed / score packet produced / weak denoising-loss signal /
no GPU expansion`.

This scout answers the only question released by the preflight: the ReDiffuse
STL-10 path is executable and scoreable locally, but the short target plus
fixed-timestep denoising-loss does not produce useful membership evidence. This
is a negative-but-useful result, not a reason to launch full-paper training.

Do not expand this into step-count, seed, timestep, batch-size, subset-size,
EMA, scheduler, or denoising-loss matrices by default. Reopen ReDiffuse
STL-10 only if one of these appears:

- a public third-party STL-10 checkpoint or score packet for the official split;
- a clearly different membership observable with a one-run falsifiable
  hypothesis; or
- an explicit decision to spend a reviewed long-training budget for scientific
  portability, with checkpoint publication and score-packet contract defined in
  advance.

## Platform and Runtime Impact

None. The admitted Platform/Runtime bundle remains the existing five rows:
`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`.
