# Direction D Draft: Audit Systems and Consumer Boundary

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Systems lead | Contract architecture lead | Owns architecture, threat model, and admission-state semantics. |
| Contract engineer | Bundle validation lead | Owns bundle schema, export checks, validation, and reproducibility hooks. |
| Report/product lead | Report correctness lead | Owns user-facing report diagrams, risk-card copy, and UI-safe language. |
| Deployment critic | Public-boundary critic | Blocks private topology, unsupported product claims, and candidate promotion. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Target type | Artifact/demo/report-correctness package first; systems paper only after measured prevention evidence |
| Venue posture | Artifact track, demo track, software-engineering-for-ML venue; applied systems only after fault-injection, report-drift, external-use, or deployment evidence |
| Current artifact | Downstream package after Direction A; not a standalone full systems-paper track yet |

## Abstract

Membership inference scores are not automatically safe to consume in privacy
reports. A score may be valid under a narrow experiment, candidate-only under a
research boundary, or non-portable because artifacts lack row binding. This
paper describes an artifact contract that turns diffusion privacy results into
machine-checkable evidence bundles. The contract records target identity, split
semantics, metric provenance, finite-tail denominators, artifact provenance,
boundary language, and admission state. The exported bundle and validators
encode an admitted-only consumption contract, while strong candidates such as
H2 output-cloud geometry and Tracing the Roots remain visible only as
blocked-promotion examples. Deployment enforcement is not evaluated in the
current evidence bundle, and measured prevention of report drift is not yet
shown.

## Controlling Thesis

The system contribution is safe consumption by contract, not deployed
enforcement. A report generator should not decide from AUC alone. It should
decide from a bundle that encodes whether a claim is admitted, candidate,
support-only, or blocked, and what finite-tail and provenance caveats must be
shown to users. Without fault-injection, report-drift, external-use, or
deployment evidence, this remains an artifact/demo report-correctness package
rather than an independent full systems paper.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| D-C1: Machine-checkable bundles can encode admitted/candidate separation. | `admitted-evidence-bundle.json`, public-surface checks | Current admitted set has five rows only; enforcement is not evaluated. |
| D-C2: Candidate visibility and product admission must be separate states. | H2 and Tracing Roots boundary notes | No Runtime row promotion or deployed-enforcement claim. |
| D-C3: Finite-tail semantics require report language. | TPR@0.1%FPR denominators | Not calibrated sub-percent risk. |
| D-C4: Drift guards require report-correctness evaluation. | Proposed validation checks plus missing fault-injection/report-drift table | Until injected faults or drift measurements exist, this is an evaluation plan rather than a demonstrated systems benefit. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Show how a correct research score can become an incorrect product/report claim when consumed without boundary metadata. |
| Threat Model | Define research producer, admitted bundle, validator, report renderer, consumer, stale artifact, and unsupported candidate promotion. |
| Contract Design | Define schema fields: target identity, split semantics, metrics, finite-tail denominator, provenance, boundary language, admission state. |
| Artifact Bridge | Explain export, validation, public-surface checks, and why candidates remain research-only. |
| Case Studies | Five admitted rows, H2 blocked candidate, Tracing Roots feature packet, weak bounded scouts. |
| Evaluation | Bundle completeness, validator pass/fail checks, admitted-only row-count guard, finite-tail denominator presence, public-surface hygiene, and missing fault-injection/report-drift evidence. |
| Deployment Lessons | What can be public, what stays internal, and what evidence future rows must provide; no deployed-enforcement claim. |
| Limitations | Needs fault-injection, report-drift, external-use, or deployment evidence to become a full systems paper. |

## Standalone Version Definition

This version should read as:

> We package the evidence-contract methodology as a machine-readable artifact
> contract, specify report-correctness checks, and show how a public-safe report
> should preserve admitted/candidate boundaries.

It should not read as:

> This is a deployed enforcement study with proven user-impact reduction.

The current evidence supports an artifact/demo paper only. A systems paper
requires measured prevention or use evidence: fault injection, before/after
drift checks, external use, or deployment evaluation.

## Missing-Evidence Promotion Gate

Direction D should be written as an artifact/demo/report-correctness package
until at least one systems-promotion gate is satisfied.

| Gate | Passing evidence | Current state | Claim allowed now |
| --- | --- | --- | --- |
| Fault-injection | Inject candidate promotion, missing denominator, row-count drift, unsafe source field, or overclaiming language and show the contract/report path blocks or flags it. | Planned only. | We can specify test cases, not claim prevention. |
| Report-drift | Compare unconstrained and contract-governed report paths and show fewer unsupported claims under the contract. | Not measured. | We can motivate drift risk, not quantify drift reduction. |
| External-use | A competition report, third-party reviewer, or non-Research author uses the bundle and records allowed vs blocked claims. | Not collected. | We can describe intended users, not adoption. |
| Deployment evidence | Public-safe demo or deployment telemetry shows the contract governs report inputs without exposing private topology. | Not collected. | We can show architecture, not deployed enforcement. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Correct research scores can become unsafe report claims when boundary metadata is dropped. | Direction A admitted/candidate examples. | Do not imply deployed enforcement. |
| 2. Threat Model | The risk is unsupported promotion, stale artifacts, missing denominators, and private/public surface confusion. | Claim register and public-surface checks. | Use abstract components only. |
| 3. Artifact Contract | The bundle records admission state, metrics, finite tails, provenance, and boundary language. | admitted bundle and validation scripts. | Encoding, not proof of runtime prevention. |
| 4. Validator Checks | Validators specify which missing fields and unsafe report inputs must be rejected. | Existing checks plus missing fault-injection table. | Prevention claim requires actual injected failures. |
| 5. Blocked Promotion Examples | H2 and Tracing Roots show why candidates must stay research-only. | H2 and Tracing Roots evidence boundaries. | Do not describe them as product features. |
| 6. Report Example | A public-safe risk card can display admitted rows with caveats. | Existing admitted rows and finite-tail denominators. | No private paths, topology, domains, or deployment details. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Artifact-contract architecture diagram | Shows research artifacts flowing into admitted bundle, validator, and report renderer. |
| Bundle schema table | Defines machine-checkable fields and user-facing meaning. |
| Admission-state state machine | Shows admitted, candidate, support-only, blocked, and watch-only transitions. |
| Fault-injection evaluation table | Tests checks that catch unsupported public/report claims. |
| Risk-card example | Demonstrates finite-tail and boundary language in a consumer report. |

## Minimum Fault-Injection Table Before Submission

| Injected fault | Expected contract response | Why it matters |
| --- | --- | --- |
| Candidate row inserted into admitted bundle | Validator rejects or report renderer hides it from admitted output. | Tests unsupported promotion. |
| Missing low-FPR denominator | Validator rejects finite-tail metric or forces caveat. | Tests low-FPR miswording risk. |
| Absolute local/private path in source field | Public-surface hygiene check fails. | Tests public-safe artifact export. |
| Row-count drift from expected admitted bundle | Validator flags bundle drift. | Tests stale or accidental row promotion. |
| H2 or Tracing Roots described as admitted | Report-language check fails. | Tests candidate visibility boundary. |

## Evidence Required Before Full Systems-Paper Promotion

| Evidence | Minimum acceptable form |
| --- | --- |
| Fault-injection | A table of injected faults with expected and observed contract/report responses, including unsupported promotion and finite-tail miswording cases. |
| External or semi-external use | A competition report, third-party review, or non-Research author using a bundle to produce a report and recording allowed vs blocked claims. |
| Report-drift evaluation | Before/after or fault-injection table showing blocked candidate promotion, finite-tail miswording, row-count drift, candidate insertion into admitted bundle, or UI/report overclaiming. |
| Public-safe report example | A risk card that contains admitted rows, boundary language, and finite-tail caveats without private topology or local paths. |
| Deployment evidence | Public-safe demo or deployment record showing schema, export, validation flow, and report surface only; no real domains, SSH aliases, secrets, or private machine topology. |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Systems lead | Reframe the paper around artifact contract and report-correctness threats. | Do not claim deployed runtime enforcement. |
| Contract engineer | Define a minimal fault-injection table and map each check to existing validators or report-language checks. | Do not add a new validator framework unless existing checks cannot express the fault. |
| Report/product lead | Draft one public-safe risk card using admitted rows only. | Do not include private topology, real domains, local paths, secrets, or candidate-as-feature language. |
| Deployment critic | Block any systems-paper promotion until measured prevention evidence exists. | Do not accept "schema exists" as a systems evaluation. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks like product documentation. | Tie every system feature to a measurement error it prevents. |
| No systems-promotion evidence. | Add fault-injection, report-drift, external-use, or deployment evidence before full systems-paper submission. |
| Leaks private deployment detail. | Keep topology, secrets, domains, and local machine paths out of public text. |
| Candidate rows creep into product claims. | Treat H2 and Tracing Roots as blocked examples, not feature launches. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as downstream draft | Current state supports a systems idea but not a strong standalone paper. |
| Promote to artifact/demo | Requires clean architecture diagram and public-safe bundle/report example. |
| Promote to full systems paper | Requires fault-injection, report-drift, external-use, or deployment evidence. |
| Stop | If it only restates schema without showing measurable report-correctness benefit. |
