# H2 Lowpass Follow-up Contract

This note records the frozen follow-up contract and result for the H2
response-strength line. It is candidate evidence, not admitted evidence and not
a Platform or Runtime handoff.

## Current Verdict

`positive but bounded candidate`

The 512 / 512 raw-primary validation kept strong ranking signal but failed the
strict tail gate:

| Scorer | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Raw H2 logistic | 0.905693 | 0.841797 | 0.134766 | 0.000000 |
| Best simple low-FPR comparator | 0.830601 | 0.775391 | 0.037109 | 0.005859 |
| Lowpass H2 logistic, cutoff 0.50 | 0.895679 | 0.830078 | 0.146484 | 0.025391 |

The raw H2 candidate is closed for promotion. The only live question is whether
a predeclared mid-band lowpass scorer can reproduce tail signal on a fresh
packet without becoming a frequency-filter artifact.

## Follow-up Result

The frozen fresh-offset packet passed the candidate gate:

| Scorer | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Raw H2 logistic | 0.922562 | 0.845703 | 0.292969 | 0.099609 |
| Best simple low-FPR comparator | 0.812347 | 0.748047 | 0.064453 | 0.005859 |
| Lowpass H2 logistic, cutoff 0.50 | 0.908684 | 0.833008 | 0.181641 | 0.082031 |

Cutoff sensitivity on the same response cache:

| Cutoff | AUC | TPR@1%FPR | TPR@0.1%FPR | Beats simple low-FPR comparator |
| ---: | ---: | ---: | ---: | --- |
| 0.25 | 0.869682 | 0.107422 | 0.015625 | yes |
| 0.35 | 0.898300 | 0.154297 | 0.091797 | yes |
| 0.50 | 0.908718 | 0.183594 | 0.082031 | yes |
| 0.65 | 0.916321 | 0.244141 | 0.080078 | yes |
| 0.75 | 0.919994 | 0.277344 | 0.087891 | yes |
| 0.90 | 0.922089 | 0.285156 | 0.097656 | yes |

This closes the lowpass artifact concern for the current DDPM/CIFAR10 packet.
It does not prove portability beyond this asset family.

## Frozen Follow-up Hypothesis

Mid-band lowpass response-strength may improve strict low-FPR behavior by
removing high-frequency denoising noise while preserving most raw H2 ranking
quality.

The follow-up must not select a cutoff after seeing the next packet. The fixed
primary scorer is:

```text
lowpass_h2_logistic_cutoff_0_50
```

Raw H2 logistic remains a reported secondary comparator. Simple same-cache
scorers remain sanity comparators, especially `negative_slope`.

## Follow-up Packet

The completed packet used:

| Field | Value |
| --- | --- |
| Dataset/model family | DDPM / CIFAR10 only |
| Permission level | black-box response observation |
| Packet size | 512 member / 512 nonmember |
| Split offset | 1024 |
| Timesteps | 40, 80, 120, 160 |
| Repeats | 2 |
| Denoise stride | 10 |
| Primary scorer | lowpass H2 logistic, cutoff 0.50 |
| Secondary scorer | raw H2 logistic |
| Same-cache comparator | best simple low-FPR scorer |

## Candidate Gate

The follow-up strengthened the H2 candidate line because all conditions held:

| Gate | Requirement |
| --- | --- |
| Tail presence | primary `TPR@0.1%FPR > 0` |
| Tail comparator | primary `TPR@0.1%FPR` beats the best simple low-FPR comparator |
| Ranking retention | primary AUC is within `0.03` absolute AUC of raw H2 logistic |
| 1% operating point | primary `TPR@1%FPR` is not lower than the best simple low-FPR comparator |
| Artifact guard | nearby cutoffs `0.35` and `0.65` do not both collapse to zero strict-tail signal |

Passing this gate does not make H2 admitted evidence. It only allows a
candidate-strengthening verdict.

## Next Boundary

Do not schedule another DDPM/CIFAR10 H2 scaling packet. The next honest
question is portability: a different black-box asset family with explicit
dataset, model, split, and query-budget contracts. Without that, H2 remains a
DDPM/CIFAR10 candidate surface.

## System Boundary

No Platform or Runtime schema should change from this contract. The only
downstream value is research triage: whether H2 deserves one more bounded
candidate packet or should stay archived as a non-admitted black-box surface.
