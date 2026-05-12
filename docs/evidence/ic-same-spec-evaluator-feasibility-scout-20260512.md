# I-C Same-Spec Evaluator Feasibility Scout

Date: 2026-05-12

## Verdict

`hold`; no CPU execution packet or GPU task is released.

The scout asked whether the current I-C cross-permission artifacts can define
an executable same-spec gray-box evaluator with a matched random comparator.
They cannot. The current executable PIA bridge surface is explicitly a
translated-alias canary, not same-spec reuse.

## Inspected Surfaces

| Surface | Observed fact | Release read |
| --- | --- | --- |
| `export-pia-translated-alias-probe` | CLI help describes a translated-contract alias probe on one frozen member/nonmember pair. | Not a same-spec evaluator. |
| `src/diffaudit/attacks/pia_adapter.py` | Summary fields are hard-coded as `translation_not_same_spec = True` and `same_spec_reuse = False`. | Blocks I-C release. |
| `tests/test_pia_adapter.py` | Tests assert `translation_kind = translated-contract` and `translation_not_same_spec` is true. | Boundary is intentionally guarded. |
| `pia-translated-alias-probe-20260417-r1` | `top_abs_delta_k` canary, `1` member and `1` nonmember, local score-gap delta only. | No split-level four-metric board. |
| `pia-translated-alias-probe-random-20260417-r1` | Matched random seeded canary under the same translated contract. | Comparator exists only for the translated alias readout. |
| `pia-translated-alias-probe-bottom-20260417-r1` | Bottom-mask canary under the same translated contract. | Useful falsifier, not release board. |

## Artifact Snapshot

The frozen I-C pair remains `member = 965`, `nonmember = 1278`.

| Probe | Mask | Same-spec reuse | Member-control score-gap delta |
| --- | --- | --- | ---: |
| `pia-translated-alias-probe-20260417-r1` | `top_abs_delta_k` | `false` | `-0.033422` |
| `pia-translated-alias-probe-random-20260417-r1` | `random_k_seeded` | `false` | `0.031760` |
| `pia-translated-alias-probe-bottom-20260417-r1` | `bottom_abs_delta_k` | `false` | `-0.003209` |

The targeted translated alias movement does not beat the random comparator on
the support-facing local score-gap direction, and none of the probes emits
`AUC`, `ASR`, `TPR@1%FPR`, or `TPR@0.1%FPR`.

## Falsifier Triggered

The falsifier from
[post-ib-next-lane-reselection-20260512.md](post-ib-next-lane-reselection-20260512.md)
is triggered:

```text
If the active executable surface remains only translated-alias canaries with
translation_not_same_spec = true, same_spec_reuse = false, and a 1 member /
1 nonmember local score-gap readout, then I-C remains hold and does not get a
CPU/GPU release.
```

## Required Reopen Contract

I-C should reopen only when a new CPU-first contract defines:

- same-spec gray-box evaluator identity rather than translated alias mapping,
- at least a small paired board beyond the single `965 / 1278` pair,
- matched random comparator under the same evaluator,
- four metric outputs: `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`,
- finite-tail denominators and orientation rules,
- adaptive boundary for mask or alias selection.

## GPU State

`active_gpu_question = none`; `next_gpu_candidate = none`.

## Product Boundary

No Platform or Runtime schema change is needed. I-C remains Research-internal
hold evidence and must not be presented as cross-permission support.
