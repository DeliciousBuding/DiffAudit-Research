# X-142: G1-A 512 Seed-2 Stability Repeat

## Question

After `X-141` produced the first matched `512 / 512` positive X-90 result, is the G1-A tri-score signal stable enough under one same-contract noise-seed repeat to remain a live internal auxiliary line?

## Contract

Same as `X-141` except:

- `noise_seed = 2`
- run suffix: `20260429-r2`
- no changes to PIA surfaces, packet size, timesteps, batch size, scorer, or kill gate

GPU asset-generation anchor:

- `workspaces/gray-box/runs/x141-tmiadm512-asset-generation-20260429-r2/summary.json`

Matched tri-score review anchor:

- `workspaces/gray-box/runs/x142-x90-larger-surface-triscore-seed2-20260429-r1/audit_summary.json`

## Result

Macro tri-score metrics:

- `AUC = 0.859043`
- `ASR = 0.786133`
- `TPR@1%FPR = 0.118164`
- `TPR@0.1%FPR = 0.023438`
- component `AUC`: `PIA = 0.834419`, `TMIA-DM = 0.771865`, `zscore_sum = 0.856071`

Per-surface read:

| surface | composite AUC | composite TPR@1%FPR | composite TPR@0.1%FPR | strongest caveat |
| --- | ---: | ---: | ---: | --- |
| `gpu512_undefended` | `0.872810` | `0.103516` | `0.029297` | `AUC` is within tolerance but slightly below z-score/control baselines |
| `gpu512_defended` | `0.845276` | `0.132812` | `0.017578` | `TPR@1%FPR` ties z-score and trails control; `TPR@0.1%FPR` still beats z-score/control |

The scripted kill gate passed again:

- identity alignment stayed frozen on both surfaces
- `AUC` stayed within tolerance
- `gpu512_undefended` won both low-FPR targets against z-score/control baselines
- `gpu512_defended` won the strict `0.1%FPR` target against z-score/control baselines

## Verdict

`positive but bounded / stable internal auxiliary`

The repeat strengthens `X-141` materially: G1-A now has two matched `512 / 512` packets with identity alignment and positive kill-gate outcomes. The honest promotion remains bounded:

- keep `headline_use_allowed = false`
- keep `external_evidence_allowed = false`
- do not replace the admitted gray-box headline `PIA`
- describe this as internal auxiliary gray-box evidence aggregation, not as a new admitted attack family

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = none until a fresh bounded candidate is selected`
- `current_cpu_sidecar = G1-A consumer-boundary sync + non-graybox next-lane reselection`
- Platform / Runtime schema handoff: none
- Materials handoff: optional wording update only; if mentioned, use `two-seed internal auxiliary G1-A positive on matched 512 surfaces`
