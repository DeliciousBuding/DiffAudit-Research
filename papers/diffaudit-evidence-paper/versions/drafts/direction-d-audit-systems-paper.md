# Direction D Draft: Audit Systems and Consumer Boundary

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Systems lead | opus | Owns architecture, threat model, and admission-state semantics. |
| Contract engineer | haiku | Owns bundle schema, export checks, validation, and reproducibility hooks. |
| Report/product lead | sonnet | Owns user-facing report diagrams, risk-card copy, and UI-safe language. |
| Deployment critic | opus | Blocks private topology, unsupported product claims, and candidate promotion. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | From Membership Scores to Auditable Evidence: Runtime Contracts for Diffusion Privacy Reports |
| Target type | Systems/artifact/demo paper |
| Venue posture | Applied security systems, artifact track, demo track, software-engineering-for-ML venue |
| Current artifact | Hold as downstream paper after Direction A |

## Abstract

Membership inference scores are not automatically safe to consume in privacy
reports. A score may be valid under a narrow experiment, candidate-only under a
research boundary, or non-portable because artifacts lack row binding. This
paper describes an audit runtime contract that turns diffusion privacy results
into machine-checkable evidence bundles. The contract records target identity,
split semantics, metric provenance, finite-tail denominators, artifact
provenance, boundary language, and admission state. Runtime consumers are
restricted to admitted rows, while strong candidates such as H2 output-cloud
geometry and Tracing the Roots remain visible only as research evidence. The
systems claim is that explicit runtime contracts prevent unsupported promotion
from research artifacts into user-facing privacy reports.

## Controlling Thesis

The system contribution is safe consumption. A runtime or product report should
not decide from AUC alone. It should decide from a bundle that encodes whether a
claim is admitted, candidate, support-only, or blocked, and what finite-tail
and provenance caveats must be shown to users.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| D-C1: Machine-checkable bundles can preserve admitted/candidate separation. | `admitted-evidence-bundle.json`, public-surface checks | Current admitted set has five rows only. |
| D-C2: Candidate visibility and product admission must be separate states. | H2 and Tracing Roots boundary notes | No Runtime row promotion. |
| D-C3: Finite-tail semantics require report language. | TPR@0.1%FPR denominators | Not calibrated sub-percent risk. |
| D-C4: Drift guards can prevent unsupported report claims. | Existing validation/check scripts | Needs before/after or external-use evidence for systems strength. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Show how a correct research score can become an incorrect product/report claim when consumed without boundary metadata. |
| Threat Model | Define research producer, runtime consumer, report user, stale artifact, and unsupported candidate promotion. |
| Contract Design | Define schema fields: target identity, split semantics, metrics, finite-tail denominator, provenance, boundary language, admission state. |
| Runtime Bridge | Explain export, validation, public-surface checks, and why candidates remain research-only. |
| Case Studies | Five admitted rows, H2 blocked candidate, Tracing Roots feature packet, weak bounded scouts. |
| Evaluation | Drift prevention, public-surface claim checks, bundle completeness, report correctness. |
| Deployment Lessons | What can be public, what stays internal, and what evidence future rows must provide. |
| Limitations | Needs external adopter or deployment study to become a strong systems paper. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Runtime-contract architecture diagram | Shows research artifacts flowing into admitted bundle and report surfaces. |
| Bundle schema table | Defines machine-checkable fields and user-facing meaning. |
| Admission-state state machine | Shows admitted, candidate, support-only, blocked, and watch-only transitions. |
| Drift-guard evaluation table | Counts checks that prevent unsupported public/report claims. |
| Risk-card example | Demonstrates finite-tail and boundary language in a consumer report. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks like product documentation. | Tie every system feature to a measurement error it prevents. |
| No external evidence. | Add competition-report use, user study, or external adopter before submission. |
| Leaks private deployment detail. | Keep topology, secrets, domains, and local machine paths out of public text. |
| Candidate rows creep into product claims. | Treat H2 and Tracing Roots as blocked examples, not feature launches. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as downstream draft | Current state supports a systems idea but not a strong standalone paper. |
| Promote to artifact/demo | Requires clean architecture diagram and public-safe bundle/report example. |
| Promote to full systems paper | Requires deployment, external adopter, user study, or before/after report-drift evidence. |
| Stop | If it only restates schema without showing measurable report-correctness benefit. |
