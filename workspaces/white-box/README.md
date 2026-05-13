# White-Box Workspace

## Current Status

- Direction: white-box membership inference using internal model signals.
- Main method: `GSA` is the strongest white-box attack.
- Defense comparator: `DPDM` provides defended baseline comparison.
- Active CPU task: none in this lane; diagonal-Fisher self-influence is closed
  as negative-but-useful after the stability board.
- GPU: no active white-box GPU task.
- Zenodo `10.5281/zenodo.14928092` is admitted-family GSA provenance only. It
  is not a new second asset and does not release a `DDPM.zip` download, GSA GPU
  replay, or adjacent loss-score/gradient ablation.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |
| [signal-access-matrix.md](signal-access-matrix.md) | Which model signals each method can access. |

Current lane selection:
[../../docs/evidence/post-secmi-next-lane-reselection-20260511.md](../../docs/evidence/post-secmi-next-lane-reselection-20260511.md).

Current feasibility contract:
[../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md](../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md).

Current micro-board result:
[../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md](../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md).

Current layer-scope review:
[../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md](../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md).

Current stability board:
[../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md](../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md).

Current GSA Zenodo archive identity:
[../../docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md](../../docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md).

## Archive

Closed notes are in
[../../legacy/workspaces/white-box/2026-04/](../../legacy/workspaces/white-box/2026-04/).
