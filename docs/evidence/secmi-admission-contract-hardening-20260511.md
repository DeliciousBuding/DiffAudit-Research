# SecMI Admission Contract Hardening

> Date: 2026-05-11
> Status: supporting-reference-hardened; not admitted
> GPU release: none

## Question

Can the existing full-split SecMI result be safely converted into an admitted
Platform/Runtime gray-box row without a new model run?

## Inputs

- `workspaces/gray-box/artifacts/secmi-full-split-admission-boundary-20260511.json`
- `workspaces/gray-box/artifacts/secmi-admission-contract-hardening-20260511.json`
- `workspaces/implementation/artifacts/admitted-evidence-bundle.json`
- `docs/evidence/admitted-results-summary.md`

This is a CPU-only contract review. No checkpoint was loaded and no GPU task
was run.

## Findings

SecMI remains a strong Research supporting reference. The existing full-split
packet is not weak: the stat head reports `AUC = 0.885833`, and the NNS
auxiliary head reports `AUC = 0.946286` with `TPR@0.1%FPR = 0.114000`.

Those metrics still do not satisfy the admitted consumer contract. The admitted
gray-box rows currently expose PIA-style cost, provenance, bounded adaptive
review, and finite-tail interpretation metadata. SecMI does not yet define the
same consumer boundary. The NNS row has an additional problem: it is an
auxiliary head, so it needs an explicit product-facing scorer contract before
any consumer can treat it like an admitted row.

## Verdict

`supporting-reference-hardened`.

SecMI is stronger than a code-ready baseline and can be cited as evidence-ready
Research corroboration. It is still blocked from the admitted Platform/Runtime
bundle. The hardening artifact now makes that boundary machine-readable:

- `consumer_decision = research-support-only`
- `admission_decision = blocked`
- `gpu_release = none`
- `blocked_claims` includes admitted row, PIA replacement, product-facing NNS,
  adaptive robustness, paper-complete reproduction, conditional diffusion, and
  commercial-model claims.

## Reopen Contract

Before SecMI can become a GPU candidate or admitted-row PR, a CPU-first contract
must freeze:

- A SecMI consumer row schema separate from the existing admitted PIA rows.
- Whether NNS may ever be product-facing or must remain Research-only.
- A bounded repeated-query adaptive review protocol.
- Low-FPR finite-tail denominator semantics.
- Source and provenance language compatible with the current admitted gray-box
  rows.

Until those gates exist, the correct action is to keep SecMI as a hardened
supporting reference and keep the admitted bundle unchanged.

## Handoff

No Platform or Runtime schema change is recommended. Platform and Runtime
consumers should continue using only the five admitted rows in
`workspaces/implementation/artifacts/admitted-evidence-bundle.json`.
