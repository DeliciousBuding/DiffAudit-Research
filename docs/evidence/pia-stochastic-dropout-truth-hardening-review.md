# PIA Stochastic-Dropout Truth-Hardening Review

> Date: 2026-05-10
> Status: positive boundary hardening; no GPU release

## Question

Are the admitted gray-box `PIA + stochastic-dropout` claims still stated with
the right formal, adaptive-attacker, low-FPR, and finite-sample boundaries?

## Evidence Reviewed

- [admitted-results-summary.md](admitted-results-summary.md)
- [innovation-evidence-map.md](innovation-evidence-map.md)
- [reproduction-status.md](reproduction-status.md)
- [research-boundary-card.md](research-boundary-card.md)
- [workspace-evidence-index.md](workspace-evidence-index.md)
- [../product-bridge/local-api.md](../product-bridge/local-api.md)
- `workspaces/implementation/artifacts/unified-attack-defense-table.json`
- [../../workspaces/gray-box/README.md](../../workspaces/gray-box/README.md)
- [../../workspaces/gray-box/plan.md](../../workspaces/gray-box/plan.md)

## Admitted Row Boundary

| Row | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Boundary |
| --- | ---: | ---: | ---: | ---: | --- |
| PIA baseline GPU512 | `0.841339` | `0.786133` | `0.058594` | `0.011719` | Workspace-verified local DDPM/CIFAR10 baseline. |
| PIA defended GPU512 | `0.828075` | `0.767578` | `0.052734` | `0.009766` | Provisional stochastic-dropout comparator, not validated privacy protection. |

Both rows use `512` target nonmembers. The `TPR@0.1%FPR` values are finite
empirical strict-tail points on that split, not calibrated continuous
sub-percent FPR estimates.

The repeated-query review is bounded to `adaptive repeats=3` and mean
aggregation. It should be described as bounded repeated-query adaptive review,
not full adaptive robustness.

## Findings

- The admitted summary already excludes candidate `PIA GPU1024` rows and keeps
  the verified headline rows at GPU512.
- The defended row correctly says stochastic dropout weakens
  `epsilon-trajectory consistency`, but it must remain a provisional defended
  comparator and not a validated privacy guarantee.
- The innovation map wording was too broad: "attack-defense closed loop" and
  "adaptive reproduction" can read stronger than the evidence. It should say
  "local attack-defense comparison loop" and "bounded repeated-query adaptive
  review."
- The reproduction-status and gray-box workspace pages were too terse and did
  not carry the finite-sample and privacy-protection caveats.

## Verdict

Positive boundary hardening. No model run is needed.

The strongest admitted I-A claim is:

> On local DDPM/CIFAR10 assets, workspace-verified PIA exposes
> `epsilon-trajectory consistency`; a provisional all-steps stochastic-dropout
> comparator weakens but does not eliminate that signal under bounded
> repeated-query review. All four metrics must be reported, and low-FPR values
> are finite empirical strict-tail points, not calibrated sub-percent FPR.

Do not claim:

- paper-faithful PIA reproduction,
- full adaptive robustness,
- validated privacy protection,
- conditional-diffusion or commercial-model coverage,
- promotion of `PIA GPU1024` runtime-candidate rows.

## Platform and Runtime Impact

No Platform or Runtime schema changes are needed. Existing product consumers
should keep using the verified table fields and boundary language.
