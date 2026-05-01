# Recon Product Evidence Card

> Status: active product bridge artifact as of 2026-05-01.

## Verdict

```text
recon admitted row now has a checked machine-readable product evidence card
```

The admitted recon black-box row is exported to
`workspaces/implementation/artifacts/recon-product-evidence-card.json`.
Platform and Runtime consumers can use this card when they need a compact
machine-readable payload with metrics, finite-tail interpretation, claim
boundary, and provenance.

This is not a new model result. It is a system-consumable representation of the
current admitted recon packet recorded in
[`../evidence/recon-product-validation-result.md`](../evidence/recon-product-validation-result.md).

## Contract

The card is derived from
`workspaces/implementation/artifacts/unified-attack-defense-table.json` by:

```powershell
python -X utf8 scripts/export_recon_product_evidence_card.py
```

CI and local checks validate that the committed card is synchronized:

```powershell
python -X utf8 scripts/export_recon_product_evidence_card.py --check
```

The card includes:

| Field | Purpose |
| --- | --- |
| `metrics` | Product headline metrics: `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`. |
| `metric_source` | Confirms the upstream-threshold reimplementation source. |
| `finite_tail` | Count-level interpretation for the public-100 target split. |
| `boundary` | Allowed and blocked product claims. |
| `provenance` | Links back to the unified table, evidence note, handoff note, and run identity. |

## Product Boundary

Allowed:

- Show recon as the admitted black-box Platform row.
- Show the four headline metrics as one coherent metric-source packet.
- Explain `TPR@0.1%FPR = 0.11` as 11 true positives with zero false positives
  on the finite 100-nonmember target split.

Blocked:

- Do not present the card as a new experiment.
- Do not call it a paper-complete reproduction.
- Do not use it as conditional-diffusion generalization evidence.
- Do not describe the strict-tail value as fine-grained continuous sub-percent
  calibration.
