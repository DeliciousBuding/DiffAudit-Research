# Post-Response-Contract Reselection

> Date: 2026-05-11
> Status: CPU-only reselection; no GPU release

## Question

After the response-contract query-source audit closed as `needs-assets`, is
there a higher-value next task than waiting on missing Pokemon/Kandinsky query
images and responses?

## Reviewed State

- Response-contract package construction is blocked by `needs_query_split`.
  The local `response-contract-pokemon-kandinsky-20260511` skeleton exists, but
  available Kandinsky/Pokemon material is weights/cache metadata only.
- White-box distinct-family scouting remains on hold. Existing activation,
  cross-layer, trajectory, and GSA loss-score variants do not release a new
  CPU-first successor.
- I-D conditional defense and selective-gating successors remain on hold.
  Current evidence is candidate-only or negative-but-useful, with no new
  falsifiable contract.
- I-B and I-C are already scoped as hold states until defended-shadow /
  adaptive-attacker or same-spec evaluator contracts exist.
- Active GPU question remains none. Next GPU candidate remains none.

## Decision

Select `system-consumable admitted evidence hardening` as the next CPU sidecar.

This is not a new model result. It is the highest-value bounded task because
current scientific lanes are blocked by either missing assets or lack of a
genuinely new hypothesis, while downstream consumers still depend on a small
set of admitted rows staying cleanly separated from candidate-only evidence.

## Implemented Guard

`scripts/validate_attack_defense_table.py` now validates the full admitted
consumer set, not only the recon product row:

| Track | Method | Required row |
| --- | --- | --- |
| Black-box | recon | `recon DDIM public-100 step30` / `none` / `runtime-mainline` |
| Gray-box | PIA baseline | `PIA GPU512 baseline` / `none` / `runtime-mainline` |
| Gray-box | PIA defended | `PIA GPU512 baseline` / `provisional G-1 = stochastic-dropout (all_steps)` / `runtime-mainline` |
| White-box | GSA attack | `GSA 1k-3shadow` / `none` / `runtime-mainline` |
| White-box | DPDM comparator | `GSA 1k-3shadow` / `W-1 strong-v3 full-scale` / `runtime-smoke` |

Each admitted consumer row must preserve numeric headline metrics,
repo-relative source provenance, non-empty `quality_cost`, and non-empty
boundary language.

## Verdict

`synchronized / CPU-only`.

No Platform or Runtime schema changes are authorized. Platform and Runtime
should continue consuming only the admitted rows listed in
[admitted-results-summary.md](admitted-results-summary.md). ReDiffuse,
tri-score, cross-box fusion, GSA LR, H2/simple-distance, CLiD, and
response-contract work remain candidate, negative, hold, or needs-assets.

## Validation

```powershell
python -X utf8 -m unittest tests.test_validate_attack_defense_table
```

Result: passed locally on 2026-05-11.

## Next Action

Do not release GPU from this task. The next autonomous cycle should either:

- continue system-consumable hardening for product-facing evidence cards,
- acquire a real second response-contract package and rerun CPU preflight,
- or select a genuinely new bounded scientific hypothesis with existing assets.
