# Admitted Evidence Bundle

> Date: 2026-05-11
> Status: synchronized; no GPU release

## Question

Can the admitted Research rows be exported as one machine-readable
Platform/Runtime bundle without promoting candidate-only or needs-assets
evidence?

## Scope

This is a CPU-only system-consumability task. It does not run models, change
metrics, add assets, or change Platform/Runtime schemas.

Inputs:

- `workspaces/implementation/artifacts/unified-attack-defense-table.json`
- `scripts/validate_attack_defense_table.py`
- [admitted-results-summary.md](admitted-results-summary.md)
- [../product-bridge/admitted-evidence-bundle.md](../product-bridge/admitted-evidence-bundle.md)

## Implemented Contract

`scripts/export_admitted_evidence_bundle.py` exports:

```text
workspaces/implementation/artifacts/admitted-evidence-bundle.json
```

The bundle is derived from the explicit admitted consumer selector list in
`scripts/validate_attack_defense_table.py`, not from dynamic `evidence_level`
filtering. This is required because `DPDM W-1` is admitted as a defended
comparator despite its historical `runtime-smoke` evidence label, while several
candidate/challenger rows have strong-looking metrics but must not be exposed
as admitted evidence.

The exported bundle contains exactly five admitted consumer rows:

| Track | Row |
| --- | --- |
| Black-box | `recon DDIM public-100 step30` / `none` |
| Gray-box | `PIA GPU512 baseline` / `none` |
| Gray-box | `PIA GPU512 baseline` / `provisional G-1 = stochastic-dropout (all_steps)` |
| White-box | `GSA 1k-3shadow` / `none` |
| White-box | `GSA 1k-3shadow` / `W-1 strong-v3 full-scale` |

Each row carries metrics, `quality_cost`, boundary language, finite-tail
interpretation, repo-relative provenance, and optional existing structured
fields such as `adaptive_check` and `cost`.

## Verdict

`synchronized`.

The admitted evidence surface now has a checked multi-row bundle for
Platform/Runtime consumers. This does not admit any new method and does not
change the existing consumer rule: ReDiffuse, tri-score, cross-box fusion,
GSA LR, H2/simple-distance, CLiD, response-contract work, GPU1024 PIA, SecMI,
and TMIA-DM remain outside the admitted bundle.

## Validation

```powershell
python -X utf8 scripts/export_admitted_evidence_bundle.py --check
python -X utf8 -m unittest tests.test_export_admitted_evidence_bundle
```

## Next Action

No GPU task is released. The next cycle should either continue
system-consumability hardening for admitted evidence, acquire real
response-contract assets, or select a genuinely new scientific hypothesis with
existing assets and a CPU preflight.
