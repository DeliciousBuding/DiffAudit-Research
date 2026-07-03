# ReDiffuse STL-10 SimA-Style Score-Norm Scout

> Date: 2026-05-25
> Status: bounded scorer completed / weak score-norm signal / no GPU expansion

## Question

After the ReDiffuse DDPM/STL-10 bounded scout produced a scoreable but
random-level fixed-timestep denoising-loss packet, does a genuinely different
single-query SimA-style denoiser-output norm expose membership signal on the
same short target and exact `256 / 256` score split?

This is a one-pass scorer on an existing checkpoint. It does not train, tune,
download data, sweep timesteps, sweep norms, or claim a paper-level ReDiffuse
reproduction.

## Frozen Contract

| Field | Value |
| --- | --- |
| Source run | `rediffuse-stl10-bounded-scout-20260525` |
| Source checkpoint | `checkpoint-step-final.pt` from the `300`-step ReDiffuse STL-10 scout |
| Source checkpoint SHA256 | `006f5247ef2f91a331a097d16bdf1c153f94f3c2f112e1e9b8d3efdd5bb2ec5e` |
| Target family | Official ReDiffuse DDPM `UNet`, EMA weights |
| Dataset | STL-10 unlabeled |
| Score packet | Same `256` trained members + `256` official nonmembers as the bounded scout |
| Score definition | `score = -L4_norm(model_epsilon_prediction_at_t100)` |
| Fixed timestep | `100` |
| Fixed norm | `L4` |
| Hard guards | `180s` wall-clock or `7.4 GB` allocated CUDA memory |
| Seed | `20260525` |
| CUDA env | `conda run -n diffaudit-research python` |

## Run Artifacts

Artifacts are stored outside Git under:
`<DOWNLOAD_ROOT>/shared/runs/rediffuse-stl10-sima-score-norm-20260525/`.

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `summary.json` | `2,591` bytes | `68c89c5251ef7c79966907e6f6a24c3115a957ba40c2a5c477695e9d444c7a57` |
| `scores.csv` | `29,835` bytes | `6359728ccea884a4d8fa56d7c9c952c6c66366e3835b0444a03a65f627171db2` |
| `run_rediffuse_stl10_sima_score_norm.py` | `8,768` bytes | `6c199ae2bdd66c4ff810df80cb1b008cc7b8e525023752b01468cd634a8c7a25` |

The script is intentionally kept as a run artifact instead of being promoted
into a reusable repository CLI. The run answered one decision question.

## Result

| Metric | Value |
| --- | ---: |
| Stop reason | `single_pass_score_budget` |
| Elapsed time | `15.938s` |
| Peak allocated VRAM | `0.365 GB` |
| Score packet size | `256` members + `256` nonmembers |
| AUC | `0.5052947998046875` |
| ASR | `0.525390625` |
| TPR@1%FPR | `0.03125` |
| TPR@0.1%FPR | `0.01953125` |
| Nonmember denominator | `256` |
| Minimum nonzero FPR | `0.00390625` |
| Member mean prediction norm | `0.07551077424432151` |
| Nonmember mean prediction norm | `0.07565450783295091` |

The score-norm gap is tiny and the AUC is effectively random. The strict-tail
numbers are finite-packet counts with `256` nonmembers, not calibrated
sub-percent operating points.

## Decision

`bounded scorer completed / weak score-norm signal / no GPU expansion`.

This is a different observable from the prior fixed-timestep denoising-loss
scout, so it was worth one bounded scoring pass. It did not change the
ReDiffuse STL-10 decision: the local short target is executable, but both
tested observables are weak.

Do not expand this into timestep, norm, seed, scheduler, subset-size,
checkpoint-step, or fusion sweeps. Reopen ReDiffuse STL-10 only if a public
third-party STL-10 checkpoint or score packet appears, a materially different
membership observable is proposed with a one-run falsifiable contract, or a
reviewed long-training budget with checkpoint and score-packet publication
contract is explicitly approved.

## Platform and Runtime Impact

None. The admitted Platform/Runtime bundle remains the existing five rows:
`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`.
