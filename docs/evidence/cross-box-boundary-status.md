# Cross-Box Evidence Boundary

Last updated: `2026-05-01`

This page records the current cross-box result boundary. It is a research
verdict, not an execution log.

## Verdict

Cross-box score sharing is useful for analysis, but it is not yet an admitted
product result.

Existing shared-surface packets show that multi-surface combinations can
improve AUC on aligned DDPM/CIFAR10 surfaces. The same packets do not show a
stable low-FPR advantage. Because privacy-audit reporting is sensitive to false
positives, the current cross-box claim remains:

```text
candidate-only: useful for internal comparison and hypothesis selection
```

## Evidence Read

| Packet | Shared set | Main read |
| --- | ---: | --- |
| `crossbox-pairboard-gsa-targeted-full-overlap-*` | 461 members / 474 nonmembers | PIA+GSA fusion improves some low-FPR variants but does not consistently dominate the best single surface. |
| `crossbox-pairboard-pia-sima-full-overlap-20260421-r1` | 461 members / 474 nonmembers | PIA+SIMA improves AUC, but low-FPR gains are small and unstable. |
| `x165-crossbox-trisurface-consensus-20260429-r1` | 461 members / 474 nonmembers | Three-surface logistic fusion improves mean AUC, but TPR@0.1%FPR remains low and variable. |

The strongest three-surface packet has:

| Candidate | Mean AUC | Mean ASR | Mean TPR@1%FPR | Mean TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Best single surface | 0.822373 | 0.759158 | 0.111936 | 0.042053 |
| Weighted 3-feature fusion | 0.829173 | 0.757937 | 0.100804 | 0.032158 |
| Logistic 3-feature fusion | 0.838389 | 0.773199 | 0.102659 | 0.048237 |
| Consensus minimum | 0.736098 | 0.684982 | 0.067409 | 0.034632 |
| Consensus mean | 0.785376 | 0.723138 | 0.056895 | 0.004947 |

The result is scientifically useful because it separates two claims that were
easy to conflate:

- `AUC claim`: multi-surface fusion can improve ranking quality.
- `audit claim`: multi-surface fusion is not yet reliable at the false-positive
  rates needed for product-facing privacy audit evidence.

## Claim Boundary

Allowed:

- Cross-box packets can be used to compare attack surfaces under shared sample
  identity.
- Cross-box packets can motivate future surface-acquisition hypotheses.
- Current outputs can appear as internal candidate evidence.

Not allowed:

- Do not claim cross-box consensus is admitted evidence.
- Do not claim low-FPR robustness from the current cross-box packets.
- Do not generalize the DDPM/CIFAR10 aligned-surface result to conditional
  diffusion models.
- Do not present candidate fusion as a replacement for admitted black-box,
  gray-box, or white-box rows.

## Next Research Question

The next useful research question is not another cross-box fusion run. It is:

```text
Can a black-box response-strength surface be given a compatible comparator and
query-budget contract without relying on gray-box or white-box signals?
```

This should start as a CPU preflight. A GPU run is justified only if the
preflight freezes:

- the target asset identity,
- the comparator surface,
- the query budget,
- the adaptive-attacker boundary,
- the low-FPR release gate.
