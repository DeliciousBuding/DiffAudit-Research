# White-Box Influence / Curvature Feasibility Scout

Date: 2026-05-11

## Verdict

`selected-cpu-first`; no GPU task is released.

The GSA white-box asset identity is usable for a feasibility scout, but the
scientific claim is not established. The next implementation must prove that it
has access to a genuinely distinct non-scalar gradient observable before any
runtime packet is scheduled.

## Why This Lane

Gray-box SecMI hardening is complete as a Research-only supporting reference,
black-box response-contract work is blocked by missing query images and
responses, and ReDiffuse is closed as candidate-only. The highest-value next
question is therefore a white-box family that could add a different signal
type, not another same-contract scale-up.

## Asset Probe

The reviewed GSA assets are ready when the workspace-scoped upstream checkout is
used:

```powershell
python -X utf8 -m diffaudit probe-gsa-assets `
  --assets-root workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1 `
  --repo-root workspaces/white-box/external/GSA
```

The default `external/GSA` path is not the runnable checkout for this asset
identity and must not be treated as the active upstream workspace.

The checked machine-readable contract is:

[../../workspaces/white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json](../../workspaces/white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json)

## Distinctness Requirement

The candidate family is diagonal-Fisher self-influence or a curvature-proxy
score. It must retain per-sample or per-channel gradient coordinates at a fixed
timestep and fixed noise, estimate a diagonal curvature proxy from shadow-side
gradients, and score with a diagonal-preconditioned gradient energy such as
`g^T(F + lambda)^-1g`.

The scout must reject itself if it collapses to any of these already-known
surfaces:

- Scalar diffusion reconstruction loss.
- Plain gradient norm.
- GSA loss-score threshold transfer.
- GSA loss-score Gaussian likelihood-ratio transfer.
- Prior activation-subspace or channel-mask observability packets.

## CPU Micro-Board Gate

Before GPU can be reconsidered, a CPU micro-board must produce:

- Extractor provenance and feature dimensionality.
- Shadow-only score orientation.
- AUC, ASR, `TPR@1%FPR`, and `TPR@0.1%FPR`.
- Baseline comparison against scalar loss, raw gradient norm, GSA loss-score LR,
  and activation-subspace or masked-observability when available.
- A failure reason if only scalar or norm data is accessible.

The release floor is strict: at least `2/3` held-out shadow folds must beat the
baselines, and the target comparison must not regress all low-FPR fields. Until
that artifact exists, `active_gpu_question = none` and
`next_gpu_candidate = none`.

## Product Boundary

No Platform or Runtime schema changes are needed. This is a Research-only
feasibility contract, not an admitted row and not a product-facing claim.
