# Admitted Evidence Bundle

> Status: active product bridge artifact as of 2026-05-11.

## Verdict

```text
admitted evidence rows now have a checked multi-row machine-readable bundle
```

The admitted Platform/Runtime consumer rows are exported to
`workspaces/implementation/artifacts/admitted-evidence-bundle.json`.
This bundle is derived from
`workspaces/implementation/artifacts/unified-attack-defense-table.json` and is
limited to the explicit admitted consumer set guarded by
`scripts/validate_attack_defense_table.py`.

This is not a new model result. It is a system-consumable representation of the
current admitted rows listed in
[`../evidence/admitted-results-summary.md`](../evidence/admitted-results-summary.md).

## Contract

Generate the bundle with:

```powershell
python -X utf8 scripts/export_admitted_evidence_bundle.py
```

CI and local checks validate that the committed bundle is synchronized:

```powershell
python -X utf8 scripts/export_admitted_evidence_bundle.py --check
```

The bundle includes exactly five admitted consumer rows:

| Track | Row |
| --- | --- |
| Black-box | `recon DDIM public-100 step30` / `none` |
| Gray-box | `PIA GPU512 baseline` / `none` |
| Gray-box | `PIA GPU512 baseline` / `provisional G-1 = stochastic-dropout (all_steps)` |
| White-box | `GSA 1k-3shadow` / `none` |
| White-box | `GSA 1k-3shadow` / `W-1 strong-v3 full-scale` |

Per row, the bundle carries:

| Field | Purpose |
| --- | --- |
| `metrics` | `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR`. |
| `quality_cost` | Human-readable packet scale and execution-cost summary from the unified table. |
| `boundary` | Allowed and blocked consumer claims. |
| `low_fpr_interpretation` | Finite empirical tail warning shared by all admitted rows. |
| `provenance` | Repo-relative source table and row source path. |
| `adaptive_check` | Present only for admitted rows that already record bounded adaptive review. |

## Product Boundary

Allowed:

- Use the bundle as the compact admitted evidence payload for Platform and
  Runtime consumers.
- Display admitted rows only with their boundary and low-FPR caveats attached.
- Treat `adaptive_check` as bounded repeated-query evidence only when the field
  is present and marked completed.

Blocked:

- Do not add candidate, hold, needs-assets, challenger, or negative rows to the
  bundle.
- Do not infer row admission from `evidence_level` alone.
- Do not parse `quality_cost` strings into new scientific claims.
- Do not describe low-FPR values as calibrated continuous sub-percent FPR.
- Do not present the bundle as paper-complete reproduction or as
  conditional-diffusion / commercial-model evidence.
