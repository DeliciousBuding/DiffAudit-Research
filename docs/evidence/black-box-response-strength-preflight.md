# Black-Box Response-Strength Preflight

Last updated: `2026-05-01`

This page records the current research status for the H2 response-strength
surface. It decides whether the line is worth another bounded GPU validation.

## Verdict

H2 response-strength is the next black-box candidate worth a bounded GPU run,
but it is not admitted evidence.

The signal is not just a one-off scout:

| Packet | Split | Primary scorer | AUC | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | --- | ---: | ---: | ---: |
| `x168-h2-strength-response-gpu-scout-20260429-r1` | 64 / 64 | H2 logistic | 0.928955 | 0.218750 | 0.218750 |
| `x172-h2-strength-response-validation-20260429-r1` | 128 / 128 non-overlap | raw H2 logistic | 0.887756 | 0.093750 | 0.062500 |
| `x176-h2-nonoverlap-256-validation-20260429-r1` | 256 / 256 non-overlap | raw H2 logistic | 0.913940 | 0.171875 | 0.062500 |

The compatible internal comparator already exists on the same response cache:
simple H2 scorers such as `negative_slope` reach useful AUC but much weaker
low-FPR values. In the 256 / 256 non-overlap packet, `negative_slope` records
`AUC = 0.839172`, `TPR@1%FPR = 0.027344`, and `TPR@0.1%FPR = 0.003906`, while
raw H2 logistic records `0.913940 / 0.171875 / 0.062500`.

## Boundary

This line is scientifically live because it stays inside black-box response
observations. It does not borrow gray-box epsilon trajectories or white-box
gradients.

Current limits:

- The asset family is still `DDPM/CIFAR10`.
- The stable cache scorer now exists at
  `scripts/evaluate_h2_response_cache.py`; the GPU response-collection runner
  still needs promotion out of archived execution scripts.
- The result is a candidate surface, not a replacement for the admitted `recon`
  black-box row.
- The low-FPR signal is positive but still too small for product-facing
  admission.

## Next GPU Candidate

Promote exactly one stable GPU collection runner first, then run one bounded
validation:

```text
H2 response-strength raw-primary 512 / 512 non-overlap validation
```

Release gate:

- same `DDPM/CIFAR10` asset contract,
- `packet_size = 512`,
- `split_offset` outside earlier validation packets,
- timesteps `40, 80, 120, 160`,
- repeats `2`,
- primary scorer `raw_h2_logistic`,
- comparator `negative_slope` and best simple low-FPR scorer from the same
  cache,
- cache scoring through `scripts/evaluate_h2_response_cache.py`,
- report `AUC / ASR / TPR@1%FPR / TPR@0.1%FPR`,
- no Platform or Runtime schema change.

Promotion rule:

The run may strengthen the black-box candidate line only if it keeps an AUC
advantage over the simple comparator and keeps nonzero `TPR@0.1%FPR` on the
non-overlap split. It still needs a later cross-asset or stronger black-box
comparator before becoming admitted evidence.
