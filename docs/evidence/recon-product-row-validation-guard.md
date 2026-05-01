# Recon Product Row Validation Guard

This note records the CPU-only hardening step for the admitted recon black-box
product row.

## Verdict

```text
system-consumable guard added; no GPU task selected
```

The admitted recon row is now protected by `scripts/validate_attack_defense_table.py`.
The validator already checked the unified table schema and gray-box adaptive
metadata. This step adds product-row-specific checks for the black-box recon
headline so future edits cannot silently drop the metric source, strict-tail
fields, source anchor, or boundary language.

## Guarded Contract

The validator now requires exactly one admitted recon product row with:

| Field | Required value |
| --- | --- |
| `track` | `black-box` |
| `attack` | `recon DDIM public-100 step30` |
| `defense` | `none` |
| `evidence_level` | `runtime-mainline` |
| `metric_source` | `upstream_threshold_reimplementation` |
| `source` | `docs/evidence/recon-product-validation-result.md` |
| Metrics | numeric `auc`, `asr`, `tpr_at_1pct_fpr`, `tpr_at_0_1pct_fpr` |
| Boundary phrases | `controlled`, `public-subset`, `proxy-shadow-member`, `zero-false-positive empirical tail`, `not a final exploit` |

## Why This Matters

This is not a new attack result. It is a system-consumable synchronization guard:

- Platform and Runtime consumers depend on the unified table.
- The recon row is the admitted black-box product row.
- The row must keep its finite-tail interpretation attached to the metrics.
- The row must not regress to older incomplete metric-source semantics.

## Validation

```powershell
python -X utf8 -m unittest tests.test_validate_attack_defense_table
python -X utf8 scripts/validate_attack_defense_table.py
conda run -n diffaudit-research python scripts/run_local_checks.py --fast
```

## Next Action

No recon GPU task is selected. The next CPU task is to choose whether further
black-box hardening should improve recon artifact provenance, add a product
display handoff for `tail_resolution`, or move to a non-recon lane with a
stronger low-FPR hypothesis.
