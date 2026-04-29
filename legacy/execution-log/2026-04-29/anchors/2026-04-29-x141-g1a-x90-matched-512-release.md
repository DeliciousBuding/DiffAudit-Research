# X-141: G1-A / X-90 Matched 512 Release

## Question

After `X-140` cleared the stale `04-H2` entry state, is there one honest non-graybox lane that can use GPU productively without reopening a frozen branch mechanically?

## Selected Lane

`G1-A / X-90 larger shared-surface tri-score` was selected because the blocker was concrete and bounded:

- `X-89` had already shown a positive `256 / 256` internal tri-score canary.
- `X-90` was blocked only because `PIA` had `512 / 512` surfaces while `TMIA-DM` still had only `256 / 256` surfaces.
- The missing work was not a new method claim; it was a bounded asset-generation task plus the already-written identity-aligned tri-score review.

## GPU Release

Released one bounded GPU task:

- script: `scripts/run_x90_tmiadm512_assets.py`
- device: `cuda:0`
- packet: `512` members + `512` nonmembers per surface
- scan timesteps: `[80, 100, 120]`
- noise seed: `1`
- batch size: `8`
- surfaces:
  - undefended `TMIA-DM long_window`
  - temporal-striding defended `TMIA-DM long_window`

Canonical asset-generation anchor:

- `workspaces/gray-box/runs/x141-tmiadm512-asset-generation-20260429-r1/summary.json`

## Matched Review

Then reran X-90 on matched `512 / 512` surfaces:

- script: `scripts/run_x90_larger_surface_triscore.py`
- review anchor: `workspaces/gray-box/runs/x141-x90-larger-surface-triscore-20260429-r1/audit_summary.json`
- PIA surfaces:
  - `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive`
  - `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive`
- TMIA-DM surfaces:
  - `workspaces/gray-box/runs/tmiadm-cifar10-late-window-protocol-probe-20260429-r1-gpu-512`
  - `workspaces/gray-box/runs/tmiadm-cifar10-late-window-temporal-striding-defense-20260429-r1-gpu-512`

## Result

Macro tri-score metrics:

- `AUC = 0.849247`
- `ASR = 0.782226`
- `TPR@1%FPR = 0.069336`
- `TPR@0.1%FPR = 0.022461`
- component `AUC`: `PIA = 0.834419`, `TMIA-DM = 0.769458`, `zscore_sum = 0.845657`

Per-surface read:

| surface | composite AUC | composite TPR@1%FPR | composite TPR@0.1%FPR | strongest caveat |
| --- | ---: | ---: | ---: | --- |
| `gpu512_undefended` | `0.866852` | `0.050781` | `0.021484` | loses `TPR@1%FPR` to `PIA` and z-score baselines, but wins the strict `0.1%FPR` target |
| `gpu512_defended` | `0.831642` | `0.087891` | `0.023438` | wins `TPR@1%FPR`, but loses `TPR@0.1%FPR` to z-score/control baselines |

The scripted kill gate passed:

- identity alignment remained frozen on both surfaces
- `AUC` stayed within tolerance
- each surface won at least one low-FPR target against the z-score/control baselines

## Verdict

`positive but bounded`

This resolves the old `TMIA-DM 512-sample gap` and restores `G1-A` as a real internal gray-box auxiliary evidence lane. It does **not** promote `G1-A` to the admitted gray-box headline, because:

- the contract still has `headline_use_allowed = false`
- the low-FPR win is mixed across surfaces and strictness levels
- the result is one `noise_seed = 1` packet and still needs a stability check before any stronger narrative

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = G1-A 512 seed-2 stability repeat`
- `cpu_sidecar = I-A boundary maintenance plus G1-A consumer-boundary sync`
- Platform / Runtime schema handoff: none
- Materials handoff: only mention as internal auxiliary gray-box evidence; do not replace `PIA` as the headline gray-box attack
