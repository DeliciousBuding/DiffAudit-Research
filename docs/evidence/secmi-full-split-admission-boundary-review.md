# SecMI Full-Split Admission Boundary Review

> Date: 2026-05-11
> Status: evidence-ready supporting reference; not admitted
> GPU release: none

## Question

Does the existing full-split SecMI result justify replacing or joining the
admitted gray-box Platform/Runtime bundle next to PIA?

## Inputs

- `workspaces/gray-box/runs/secmi-cifar10-gpu-full-stat-20260415-r2/summary.json`
- `workspaces/gray-box/runs/secmi-cifar10-gpu-full-stat-20260415-r2/analysis.md`
- `workspaces/implementation/artifacts/admitted-evidence-bundle.json`
- `docs/evidence/admitted-results-summary.md`

No model was run for this review. It is a CPU-only boundary audit of existing
artifacts.

## Observed Metrics

| Method | Samples per split | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | --- | --- | --- | --- |
| PIA admitted baseline | 512 | 0.841339 | 0.786133 | 0.058594 | 0.011719 |
| SecMI stat | 25,000 | 0.885833 | 0.815400 | 0.093960 | 0.007720 |
| SecMI NNS auxiliary head | 25,000 | 0.946286 | 0.879275 | 0.400450 | 0.114000 |

SecMI is not a fragile smoke result. The full `25k / 25k` packet completed on
CUDA, and the NNS auxiliary head is materially stronger than the admitted PIA
baseline on AUC, ASR, and both low-FPR fields.

## Admission Boundary

Verdict: `evidence-ready supporting reference`, not admitted.

The result is strong enough to update SecMI from `code-ready` to
`evidence-ready` in Research tracking. It is not promoted into the admitted
Platform/Runtime bundle in this review because:

- The admitted gray-box bundle currently represents the PIA baseline plus a
  bounded stochastic-dropout comparator under a repeated-query review.
- The SecMI row does not yet carry the same structured `cost`,
  `adaptive_check`, and consumer-boundary fields used by admitted PIA rows.
- The NNS head is an auxiliary scorer and needs an explicit consumer contract
  before it can become a product-facing gray-box row.
- This review does not establish adaptive robustness, paper-complete
  reproduction, conditional-diffusion coverage, or commercial-model coverage.

## Falsifier Result

The falsifier holds for immediate admission: strong full-split metrics alone do
not satisfy the current admitted-bundle contract. The same artifacts do falsify
the older weak statement that SecMI is merely `code-ready`.

## Next Action

No GPU task is released. The next SecMI step, if selected later, should be a
CPU-first admission-contract hardening pass:

1. Add structured cost/provenance/adaptive-boundary metadata for the full-split
   SecMI stat and NNS rows.
2. Decide whether NNS is allowed as a product-facing auxiliary head or must
   remain a Research-only corroboration surface.
3. Only after that contract exists, consider a small repeated-query/adaptive
   review packet. Do not run a larger full-split packet; the scale evidence
   already exists.

## Handoff

No Platform or Runtime schema change is recommended. Downstream consumers
should continue using the admitted bundle only. SecMI may be cited in Research
materials as a strong gray-box supporting reference, with the admission boundary
above attached.
