# GSA Diagonal-Fisher Feasibility Micro-Board

Date: 2026-05-11

## Verdict

`negative-but-useful`; no GPU task is released.

The CPU micro-board proves that selected-layer raw gradient coordinates can be
extracted without persisting raw gradient tensors, but the diagonal-Fisher
self-influence score does not clear the release gate. Shadow-calibrated
orientation transfers in the wrong direction on the target pair.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 scripts\review_gsa_diagonal_fisher_feasibility.py `
  --workspace workspaces\white-box\runs\gsa-diagonal-fisher-feasibility-20260511-cpu-1 `
  --repo-root workspaces\white-box\external\GSA `
  --assets-root workspaces\white-box\assets\gsa-cifar10-1k-3shadow-epoch300-rerun1 `
  --max-samples-per-split 1 `
  --ddpm-num-steps 20 `
  --sampling-frequency 1 `
  --device cpu
```

## Result

Canonical summary:

[../../workspaces/white-box/artifacts/gsa-diagonal-fisher-feasibility-microboard-20260511.json](../../workspaces/white-box/artifacts/gsa-diagonal-fisher-feasibility-microboard-20260511.json)

Key fields:

- Shadow calibration uses `6` samples from three shadow checkpoints.
- Target transfer uses `2` target samples.
- Selected layer: `mid_block.attentions.0.to_v`.
- Gradient feature dimensionality: `262656`.
- Runtime: approximately `18` seconds on CPU.
- Raw gradient vectors are not persisted by default; only scalar records and
  summary fields are written.

Metric summary:

| Board | Score | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Direction |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| shadow calibration | diagonal-Fisher self-influence | 0.555556 | 0.666667 | 0.0 | 0.0 | member-lower |
| shadow calibration | scalar loss | 0.666667 | 0.666667 | 0.333333 | 0.333333 | member-lower |
| target transfer | diagonal-Fisher self-influence | 0.0 | 0.5 | 0.0 | 0.0 | member-lower |
| target transfer | scalar loss | 0.0 | 0.5 | 0.0 | 0.0 | member-lower |
| target transfer | raw grad L2 squared | 0.0 | 0.5 | 0.0 | 0.0 | member-lower |

## Interpretation

This is not an admitted result and not a new white-box family. The useful
finding is narrower: the selected-layer raw-gradient extractor is viable, but
this diagonal-Fisher score is not ready for GPU because the shadow-derived
score directions do not transfer to the target pair. The target self-diagnostic
can separate the two samples with oracle orientation, but that is not a valid
release gate because orientation must be frozen from shadow calibration.

## Next Action

Do not run a larger same-score GPU packet. The only reasonable follow-up is a
CPU-only variant review that changes the score definition or layer scope while
keeping the same baselines and no raw gradient tensor persistence. If that
cannot beat scalar loss on shadow-held-out checks, close the white-box
influence/curvature lane as `negative-but-useful`.
