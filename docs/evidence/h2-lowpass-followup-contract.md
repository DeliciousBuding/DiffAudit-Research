# H2 Lowpass Follow-up Contract

This note freezes the next decision point for the H2 response-strength line.
It is a candidate contract, not admitted evidence and not a Platform or Runtime
handoff.

## Current Verdict

`negative but useful`

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

The next GPU task is not active. It becomes eligible only if the branch is
otherwise clean and the runner can use portable asset paths supplied by the
operator environment.

If scheduled, the follow-up packet should use:

| Field | Value |
| --- | --- |
| Dataset/model family | DDPM / CIFAR10 only |
| Permission level | black-box response observation |
| Packet size | 512 member / 512 nonmember |
| Split offset | a fresh non-overlap offset not used by earlier H2 packets |
| Timesteps | 40, 80, 120, 160 |
| Repeats | 2 |
| Denoise stride | 10 |
| Primary scorer | lowpass H2 logistic, cutoff 0.50 |
| Secondary scorer | raw H2 logistic |
| Same-cache comparator | best simple low-FPR scorer |

## Admission Gate

The follow-up may strengthen the H2 candidate line only if all conditions hold:

| Gate | Requirement |
| --- | --- |
| Tail presence | primary `TPR@0.1%FPR > 0` |
| Tail comparator | primary `TPR@0.1%FPR` beats the best simple low-FPR comparator |
| Ranking retention | primary AUC is within `0.03` absolute AUC of raw H2 logistic |
| 1% operating point | primary `TPR@1%FPR` is not lower than the best simple low-FPR comparator |
| Artifact guard | nearby cutoffs `0.35` and `0.65` do not both collapse to zero strict-tail signal |

Passing this gate still does not make H2 admitted evidence. It only allows a
candidate-strengthening verdict.

## Failure Rule

Close the lowpass branch without another immediate GPU retry if any of these
happen:

- `TPR@0.1%FPR = 0` for cutoff `0.50`,
- cutoff `0.50` fails to beat the best same-cache simple low-FPR comparator,
- AUC drops by more than `0.03` versus raw H2 logistic,
- only one hand-picked cutoff works while neighboring cutoffs collapse,
- the run requires a non-portable local path assumption to be meaningful.

The honest failure verdict is:

```text
negative but useful; H2 remains a ranking-signal candidate, not a low-FPR
black-box admission path.
```

## System Boundary

No Platform or Runtime schema should change from this contract. The only
downstream value is research triage: whether H2 deserves one more bounded
candidate packet or should stay archived as a non-admitted black-box surface.
