# I-B Reopen Shadow-Reference Guard

Date: 2026-05-12

## Verdict

`CPU guard added; I-B remains hold-protocol-frozen`

The frozen I-B defended-shadow reopen protocol now has a code-level guard on
the active review entrypoint. `review-risk-targeted-unlearning-pilot` keeps its
legacy diagnostic behavior by default, but an explicit defended-shadow reopen
mode refuses old undefended shadow threshold references.

This does not train defended shadows, run an adaptive attacker, report a new
metric, or release GPU work.

## Question

Can the active I-B review path prevent a future reopen packet from silently
reusing the old undefended shadow threshold-transfer reference?

## Hypothesis

A small CPU-only guard is enough to separate historical threshold-transfer
diagnostics from future defended-shadow reopen packets.

## Falsifier

If `review-risk-targeted-unlearning-pilot --review-mode defended-shadow-reopen`
accepts a shadow summary that lacks `threshold_reference=defended-shadows`, the
guard fails and the frozen protocol remains only documentary.

## Implementation

- Added `review_mode` to `review_risk_targeted_unlearning_pilot`.
- Default mode stays `threshold-transfer-diagnostic` to preserve historical
  reproducibility.
- New mode `defended-shadow-reopen` requires the loaded shadow reference summary
  to declare `threshold_reference=defended-shadows`.
- CLI exposes the mode as `--review-mode`.
- H2 defense review remains diagnostic-only when it reuses the shared packet
  writer.

The machine-readable guard record is
[`workspaces/defense/artifacts/ib-reopen-shadow-reference-guard-20260512.json`](../../workspaces/defense/artifacts/ib-reopen-shadow-reference-guard-20260512.json).

## Validation

Targeted checks:

```powershell
conda run -n diffaudit-research python -m unittest tests.test_risk_targeted_unlearning tests.test_h2_adapter
```

Result: `22` tests passed.

Coverage added:

- `defended-shadow-reopen` rejects `threshold_reference=undefended-shadows`.
- `defended-shadow-reopen` accepts `threshold_reference=defended-shadows`.
- CLI passes `--review-mode` into the review implementation.
- H2 adapter still works with the shared review-packet writer.

## Boundary

This guard only prevents a specific protocol regression. It does not satisfy
the defended-shadow training requirement, the adaptive-attacker requirement, or
the retained-utility requirement. I-B remains on hold until those are available
under the frozen protocol.
