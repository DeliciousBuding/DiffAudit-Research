# GSA Diagonal-Fisher Layer-Scope Review

Date: 2026-05-11

## Verdict

`mixed-but-not-gpu-ready`; no GPU task is released.

The layer-scope review tests whether the first diagonal-Fisher failure was only
a `mid_block.attentions.0.to_v` layer-selection issue. It is not enough to
promote the score family: one alternate attention layer transfers on the tiny
target pair, but it does not beat the raw-gradient L2 baseline and the packet is
still only `1` sample per split.

## Contract

All runs use the same CPU-only contract:

```powershell
conda run -n diffaudit-research python -X utf8 scripts\review_gsa_diagonal_fisher_feasibility.py `
  --workspace <ignored-run-workspace> `
  --repo-root workspaces\white-box\external\GSA `
  --assets-root workspaces\white-box\assets\gsa-cifar10-1k-3shadow-epoch300-rerun1 `
  --layer-selector <layer> `
  --max-samples-per-split 1 `
  --ddpm-num-steps 20 `
  --sampling-frequency 1 `
  --device cpu
```

Raw gradient tensors are not persisted by default. Only scalar summaries and
records are retained.

## Results

| Layer | Verdict | Shadow Fisher AUC | Target Fisher AUC | Target Fisher ASR | Target scalar AUC | Target raw-grad L2 AUC |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `mid_block.attentions.0.to_q` | negative-but-useful | 0.555556 | 0.0 | 0.5 | 0.0 | 0.0 |
| `down_blocks.4.attentions.0.to_v` | negative-but-useful | 0.666667 | 0.0 | 0.5 | 0.0 | 0.0 |
| `up_blocks.1.attentions.0.to_v` | negative-but-useful | 0.888889 | 1.0 | 1.0 | 0.0 | 1.0 |

Canonical artifacts:

- [../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-mid_block-attentions-0-to_q.json](../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-mid_block-attentions-0-to_q.json)
- [../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-down_blocks-4-attentions-0-to_v.json](../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-down_blocks-4-attentions-0-to_v.json)
- [../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-up_blocks-1-attentions-0-to_v.json](../../workspaces/white-box/artifacts/gsa-diagonal-fisher-layer-scope-20260511-up_blocks-1-attentions-0-to_v.json)

## Interpretation

The `up_blocks.1.attentions.0.to_v` row prevents closing the entire
influence/curvature family immediately, but it is not a GPU release gate:

- The transferred Fisher score ties raw-gradient L2 on the target pair.
- The target pair has only `1` member and `1` nonmember sample.
- Two other attention layers still fail target transfer.
- No held-out shadow-fold check has shown `2/3` fold improvement over
  baselines.

## Next Action

Run at most one more CPU-only stability board for
`up_blocks.1.attentions.0.to_v` with a larger still-small cap such as
`2` or `4` samples per split. If it does not beat raw-gradient L2 under
shadow-frozen orientation, close diagonal-Fisher self-influence as
`negative-but-useful` and reselect a different lane. Do not release GPU from
the current layer-scope result.
