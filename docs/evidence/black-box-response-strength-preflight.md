# Black-Box Response-Strength Preflight

Last updated: `2026-05-01`

This page records the current research status for the H2 response-strength
surface. It decides whether the line is worth another bounded GPU validation.

## Verdict

H2 response-strength is a stronger black-box candidate after the frozen
lowpass follow-up, but it is still not admitted evidence and not a `recon`
replacement.

The signal is not just a one-off scout:

| Packet | Split | Primary scorer | AUC | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | --- | ---: | ---: | ---: |
| `x168-h2-strength-response-gpu-scout-20260429-r1` | 64 / 64 | H2 logistic | 0.928955 | 0.218750 | 0.218750 |
| `x172-h2-strength-response-validation-20260429-r1` | 128 / 128 non-overlap | raw H2 logistic | 0.887756 | 0.093750 | 0.062500 |
| `x176-h2-nonoverlap-256-validation-20260429-r1` | 256 / 256 non-overlap | raw H2 logistic | 0.913940 | 0.171875 | 0.062500 |
| `h2-response-strength-512-20260501-r1` | 512 / 512 non-overlap | raw H2 logistic | 0.905693 | 0.134766 | 0.000000 |
| `h2-lowpass-followup-512-20260501-r1` | 512 / 512 non-overlap | lowpass H2 logistic, cutoff 0.50 | 0.908684 | 0.181641 | 0.082031 |

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

The frozen follow-up at fresh split offset `1024` passed the candidate gate:

- lowpass H2 cutoff `0.50`: `AUC = 0.908684`, `ASR = 0.833008`,
  `TPR@1%FPR = 0.181641`, `TPR@0.1%FPR = 0.082031`,
- raw H2 logistic on the same packet: `0.922562 / 0.845703 / 0.292969 /
  0.099609`,
- best same-cache simple low-FPR comparator: `AUC = 0.812347`,
  `TPR@1%FPR = 0.064453`, `TPR@0.1%FPR = 0.005859`,
- nearby cutoff review did not collapse: cutoff `0.35` kept
  `TPR@0.1%FPR = 0.091797`, and cutoff `0.65` kept `0.080078`.

This strengthens the response-strength surface, but it also shows lowpass is a
stabilizing boundary check rather than a clear replacement for raw H2: raw H2
was stronger on the fresh packet after failing strict-tail on the previous
packet.

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
- The low-FPR signal is now repeated but still limited to `DDPM/CIFAR10`.

## Current Verdict

```text
positive but bounded candidate
```

H2 response-strength should stay in the candidate tier. It has repeated
non-overlap signal and a same-cache sanity comparator, but it is not admitted
evidence because the asset family is narrow and no stronger admitted black-box
comparator has been established.

## Next Research Question

```text
Can response-strength transfer beyond DDPM/CIFAR10 under a portable black-box
asset contract, or is it a DDPM/CIFAR10-specific candidate surface?
```

The lowpass follow-up contract and verdict are recorded in
[h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md). No further
GPU expansion should run until a cross-asset black-box contract exists.
