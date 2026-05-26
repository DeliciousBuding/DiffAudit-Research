# Version D: Artifact Contract and Consumer Boundary

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Systems lead | Contract architecture lead | Architecture, threat model, consumer-boundary semantics. |
| Contract engineer | Bundle validation lead | Bundle schema, export checks, public-surface checks, reproducibility hooks. |
| Product/report lead | Report correctness lead | UI/report diagrams, risk-card language, bilingual copy alignment. |
| Deployment critic | Public-boundary critic | Block private topology and unsupported product claims. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Paper type | Artifact/demo paper first; systems paper only after measured prevention evidence |
| Venue posture | Demo/artifact track or software-engineering-for-ML venue now; applied security systems only after fault-injection, report-drift, external-use, or deployment evidence exists |
| Current status | Downstream brief only; hold full systems claims until fault-injection, report-drift, or external-adopter evidence exists |

## Abstract Draft

Membership inference outputs are hard to consume safely: a score may be
positive under a narrow experiment, candidate-only under a research boundary, or
non-portable because artifacts lack row binding. This paper describes an
artifact contract that turns diffusion privacy results into machine-checkable
evidence bundles. The contract records target identity, split semantics,
metrics, finite-tail denominators, provenance, boundary language, and admission
state. The exported bundle and validators encode an admitted-only consumption
contract over five admitted rows: black-box reconstruction, PIA baseline, PIA
defended, GSA, and DPDM W-1. Strong research candidates such as H2 output-cloud
geometry and Tracing the Roots are kept as blocked-promotion examples. The
current evidence supports contract encoding and validation; it does not yet
evaluate deployed enforcement.

## Core Thesis

Research metrics become user-facing audit evidence only through an artifact
contract that preserves admission state, provenance, finite-tail semantics, and
boundary language. This becomes a systems paper only if we can show measured
prevention of consumer drift and improved report correctness. Until then, the
contract fields and admitted/candidate taxonomy belong in Direction A, while
Direction D records the downstream artifact/demo evaluation plan.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| D1: Machine-checkable evidence bundles encode admitted/candidate separation. | `admitted-evidence-bundle.json`, public-surface checks | Current bundle has five rows only; deployed enforcement is not evaluated. |
| D2: Candidate visibility and product admission must be separated. | H2 and Tracing Roots product-bridge notes | No new Platform/Runtime rows. |
| D3: Finite-tail semantics need consumer-facing language. | TPR@0.1%FPR denominator notes | Does not calibrate sub-percent risk. |
| D4: Report correctness checks can be fault-injected. | Existing validation/check scripts | Needs fault-injection, deployment, or external user evidence for systems venue strength. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Show how score drift becomes a product/report risk. |
| Contract Design | Define schema and admission states. |
| Artifact Bridge | Explain export, validation, and admitted-only report inputs. |
| Case Studies | Five admitted rows, H2 blocked candidate, Tracing Roots feature packet. |
| Evaluation | Bundle completeness, public-surface checks, admitted-only row-count guard, finite-tail denominator presence, and fault-injected report correctness. |
| Deployment Lessons | What evidence is safe to expose and what must stay Research-only. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Add one external-adopter or competition-report usage case. | Turns internal contract into systems evidence. |
| Measure fault-injected report drift before/after guardrails. | Provides a systems evaluation beyond schema description. |
| Produce one clean architecture diagram. | Makes the bridge understandable to non-Research reviewers. |
| Produce one public-safe risk-card example. | Shows finite-tail and boundary language without leaking private topology. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Writing private deployment topology into public docs | Violates release policy. |
| Adding Runtime modes for candidates | Would break the admitted/candidate boundary. |
| Claiming user impact without usage evidence | Weak systems paper. |

## Decision

Hold as an artifact/demo paper. It becomes attractive as a systems paper only
after Direction A defines the measurement contract and there is fault-injection,
report-drift, external-use, or deployment evidence.
