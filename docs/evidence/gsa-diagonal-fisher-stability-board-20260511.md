# GSA Diagonal-Fisher Stability Board

Date: 2026-05-11

## Verdict

`negative-but-useful`; no GPU task is released. This result closes the current
diagonal-Fisher self-influence line.

The only layer left open by the layer-scope review,
`up_blocks.1.attentions.0.to_v`, does not survive a larger CPU-only stability
board. Under shadow-frozen orientation, diagonal-Fisher self-influence ties the
`raw_grad_l2_sq` baseline on the target transfer board and has no strict-tail
advantage.

This closes the current diagonal-Fisher self-influence line. A future
white-box successor needs a genuinely different observable or a stronger
paper-backed contract; it should not be a larger same-score packet.

## Contract

```powershell
conda run -n diffaudit-research python -X utf8 scripts/review_gsa_diagonal_fisher_feasibility.py `
  --workspace workspaces/white-box/runs/gsa-diagonal-fisher-stability-board-20260511-up_blocks-1-attentions-0-to_v-n4 `
  --repo-root workspaces/white-box/external/GSA `
  --assets-root workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1 `
  --layer-selector up_blocks.1.attentions.0.to_v `
  --max-samples-per-split 4 `
  --ddpm-num-steps 20 `
  --sampling-frequency 1 `
  --device cpu
```

The run is CPU-only. Raw gradient vectors are not persisted by default; the
committed artifact contains scalar summaries only.

## Result

| Board | Fisher AUC | Fisher ASR | Fisher TPR@1%FPR | Fisher TPR@0.1%FPR | Scalar-loss AUC | `raw_grad_l2_sq` AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Shadow calibration | 0.548611 | 0.625 | 0.0 | 0.0 | 0.527778 | 0.548611 |
| Target transfer | 0.5 | 0.625 | 0.25 | 0.25 | 0.25 | 0.5 |
| Target self diagnostic | 0.5 | 0.625 | 0.0 | 0.0 | 0.75 | 0.5 |

Runtime: `23.366477` seconds on CPU, `24` shadow samples and `8` target
samples.

Canonical artifact:

- [../../workspaces/white-box/artifacts/gsa-diagonal-fisher-stability-board-20260511-up_blocks-1-attentions-0-to_v-n4.json](../../workspaces/white-box/artifacts/gsa-diagonal-fisher-stability-board-20260511-up_blocks-1-attentions-0-to_v-n4.json)

## Interpretation

- The target-transfer Fisher AUC is `0.5`, equal to `raw_grad_l2_sq`.
- The target-transfer strict-tail fields are equal to `raw_grad_l2_sq`.
- Shadow calibration is weak and also tied with `raw_grad_l2_sq`.
- Target self-oracle orientation does not rescue the score; scalar loss is
  stronger under target self diagnostic, which is not a valid transfer gate.

## Next Action

Close diagonal-Fisher self-influence as a white-box successor candidate. Keep
GSA + DPDM W-1 as the admitted white-box comparator, and reselect the next
CPU-first lane rather than spending GPU on this score family.
