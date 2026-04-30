# Black-Box Response-Strength Preflight

Last updated: `2026-05-01`

This page records the current research status for the H2 response-strength
surface. It decides whether the line is worth another bounded GPU validation.

## Verdict

H2 response-strength is a useful black-box candidate, but the raw-primary
512 / 512 validation does not pass the low-FPR release gate.

The signal is not just a one-off scout:

| Packet | Split | Primary scorer | AUC | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | --- | ---: | ---: | ---: |
| `x168-h2-strength-response-gpu-scout-20260429-r1` | 64 / 64 | H2 logistic | 0.928955 | 0.218750 | 0.218750 |
| `x172-h2-strength-response-validation-20260429-r1` | 128 / 128 non-overlap | raw H2 logistic | 0.887756 | 0.093750 | 0.062500 |
| `x176-h2-nonoverlap-256-validation-20260429-r1` | 256 / 256 non-overlap | raw H2 logistic | 0.913940 | 0.171875 | 0.062500 |
| `h2-response-strength-512-20260501-r1` | 512 / 512 non-overlap | raw H2 logistic | 0.905693 | 0.134766 | 0.000000 |

The compatible internal comparator already exists on the same response cache:
simple H2 scorers such as `negative_slope` reach useful AUC but much weaker
low-FPR values. In the 256 / 256 non-overlap packet, `negative_slope` records
`AUC = 0.839172`, `TPR@1%FPR = 0.027344`, and `TPR@0.1%FPR = 0.003906`, while
raw H2 logistic records `0.913940 / 0.171875 / 0.062500`.

The 512 / 512 validation changes the read:

- raw H2 logistic remains strong by AUC (`0.905693`) and `TPR@1%FPR`
  (`0.134766`),
- raw H2 logistic fails the strict tail gate with `TPR@0.1%FPR = 0.000000`,
- the same-cache `negative_slope` comparator has lower AUC (`0.830601`) but
  nonzero `TPR@0.1%FPR = 0.005859`,
- lowpass H2 logistic recovers the strict tail (`TPR@0.1%FPR = 0.025391`) with
  slightly lower AUC (`0.895679`).

CPU cutoff review on the same cache shows the lowpass-tail effect is not a
single cutoff artifact:

| Cutoff | AUC | TPR@1%FPR | TPR@0.1%FPR | Beats simple low-FPR comparator |
| ---: | ---: | ---: | ---: | --- |
| 0.25 | 0.858387 | 0.076172 | 0.003906 | no |
| 0.35 | 0.877884 | 0.091797 | 0.015625 | yes |
| 0.50 | 0.895660 | 0.146484 | 0.025391 | yes |
| 0.65 | 0.901302 | 0.132812 | 0.005859 | yes |
| 0.75 | 0.904388 | 0.134766 | 0.001953 | no |
| 0.90 | 0.905586 | 0.146484 | 0.000000 | no |

At cutoff `0.50`, the strict-tail value corresponds to about 13 of 512 members
above the `0.1%FPR` operating point. The effect is real enough for candidate
analysis but still too small for admitted evidence.

## Boundary

This line is scientifically live because it stays inside black-box response
observations. It does not borrow gray-box epsilon trajectories or white-box
gradients.

Current limits:

- The asset family is still `DDPM/CIFAR10`.
- Stable entrypoints now exist:
  `scripts/run_h2_response_strength_validation.py` for response collection and
  `scripts/evaluate_h2_response_cache.py` for CPU cache scoring.
- The result is a candidate surface, not a replacement for the admitted `recon`
  black-box row.
- The low-FPR signal is positive but still too small for product-facing
  admission.

## Current Verdict

```text
negative but useful
```

The raw-primary H2 candidate should not be promoted. The useful new hypothesis
is narrower: mid-band lowpass response-strength may preserve enough ranking
quality while improving the strict false-positive tail.

## Next Research Question

```text
Can mid-band lowpass H2 response-strength produce stable low-FPR gains on a
second non-overlap packet without becoming a frequency-filter artifact?
```

The CPU contract is frozen in
[h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md). It fixes
`lowpass_h2_logistic_cutoff_0_50` as the only eligible primary scorer for a
future packet, with explicit failure rules before any further GPU run.
