# Version D: Audit Systems and Consumer Boundary

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Systems lead | opus | Architecture, threat model, consumer-boundary semantics. |
| Contract engineer | haiku | Bundle schema, export checks, public-surface checks, reproducibility hooks. |
| Product/report lead | sonnet | UI/report diagrams, risk-card language, bilingual copy alignment. |
| Deployment critic | opus | Block private topology and unsupported product claims. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | From Membership Scores to Auditable Evidence: A Runtime Contract for Diffusion Privacy Reports |
| Paper type | Systems / artifact / demo paper |
| Venue posture | Applied security systems, demo/artifact track, software-engineering-for-ML venue |
| Current status | Hold until deployment, user-study, or external-adopter evidence exists |

## Abstract Draft

Membership inference outputs are hard to consume safely: a score may be
positive under a narrow experiment, candidate-only under a research boundary, or
non-portable because artifacts lack row binding. This paper describes an audit
runtime contract that turns diffusion privacy results into machine-checkable
evidence bundles. The contract records target identity, split semantics,
metrics, finite-tail denominators, provenance, boundary language, and admission
state. Platform and Runtime consumers are restricted to five admitted rows:
black-box reconstruction, PIA baseline, PIA defended, GSA, and DPDM W-1. Strong
research candidates such as H2 output-cloud geometry and Tracing the Roots are
kept visible for research planning but blocked from product admission. The
system contribution is a consumer-safe bridge from research artifacts to privacy
reports, with drift checks and public-surface guards preventing unsupported
claims.

## Core Thesis

Research metrics become user-facing audit evidence only through a runtime
contract. This is a systems paper if we can show that the contract prevents real
consumer drift and improves report correctness.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| D1: Machine-checkable evidence bundles prevent unsupported promotion. | `admitted-evidence-bundle.json`, public-surface checks | Current bundle has five rows only. |
| D2: Candidate visibility and product admission must be separated. | H2 and Tracing Roots product-bridge notes | No new Platform/Runtime rows. |
| D3: Finite-tail semantics need consumer-facing language. | TPR@0.1%FPR denominator notes | Does not calibrate sub-percent risk. |
| D4: Report correctness can be guarded automatically. | Existing validation/check scripts | Needs deployment or external user evidence for systems venue strength. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Show how score drift becomes a product/report risk. |
| Contract Design | Define schema and admission states. |
| Runtime Bridge | Explain export, validation, and consumer restrictions. |
| Case Studies | Five admitted rows, H2 blocked candidate, Tracing Roots feature packet. |
| Evaluation | Drift prevention, public-surface checks, report correctness. |
| Deployment Lessons | What evidence is safe to expose and what must stay Research-only. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Add one external-adopter or competition-report usage case. | Turns internal contract into systems evidence. |
| Measure report drift before/after guardrails. | Provides a systems evaluation beyond schema description. |
| Produce one clean architecture diagram. | Makes the bridge understandable to non-Research reviewers. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Writing private deployment topology into public docs | Violates release policy. |
| Adding Runtime modes for candidates | Would break the admitted/candidate boundary. |
| Claiming user impact without usage evidence | Weak systems paper. |

## Decision

Hold as an artifact/demo paper. It becomes attractive after Direction A defines
the measurement contract and there is real deployment or competition-report
evidence.
