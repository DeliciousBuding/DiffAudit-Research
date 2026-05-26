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
| Paper type | Artifact/demo/report-correctness package first; systems paper only after measured prevention evidence |
| Venue posture | Demo/artifact track or software-engineering-for-ML venue now; applied security systems only after fault-injection, report-drift, external-use, or deployment evidence exists |
| Current status | Downstream artifact package only; full systems-paper promotion is blocked until at least one missing-evidence gate is satisfied |

## Abstract Draft

Membership inference outputs are hard to consume safely: a score may be
positive under a narrow experiment, candidate-only under a research boundary, or
non-portable because artifacts lack row binding. This paper describes an
artifact contract that turns diffusion privacy results into machine-checkable
evidence bundles and report-correctness obligations. The contract records
target identity, split semantics, metrics, finite-tail denominators, provenance,
boundary language, and admission state. The exported bundle encodes an
admitted-only consumption contract over five admitted rows: black-box
reconstruction, PIA baseline, PIA defended, GSA, and DPDM W-1. Strong research
candidates such as H2 output-cloud geometry and Tracing the Roots are kept as
blocked-promotion examples. The current evidence supports an artifact/demo
paper package; it does not evaluate deployed enforcement or measured prevention
of report drift.

## Core Thesis

Research metrics become user-facing audit evidence only through an artifact
contract that preserves admission state, provenance, finite-tail semantics, and
boundary language. Direction D is the downstream artifact/demo and
report-correctness package: it can specify the contract, show public-safe report
examples, and define the tests that unsafe consumption must fail. It becomes a
full systems paper only after measured evidence shows prevention of consumer
drift or correct external use. Until then, the contract fields and
admitted/candidate taxonomy support Direction A, while Direction D records the
promotion gate.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| D1: Machine-checkable evidence bundles encode admitted/candidate separation. | `admitted-evidence-bundle.json`, public-surface checks | Current bundle has five rows only; deployed enforcement is not evaluated. |
| D2: Candidate visibility and product admission must be separated. | H2 and Tracing Roots boundary notes | No new Platform/Runtime rows or deployed enforcement claim. |
| D3: Finite-tail semantics need consumer-facing language. | TPR@0.1%FPR denominator notes | Does not calibrate sub-percent risk. |
| D4: Report correctness can be evaluated through injected consumer faults. | Proposed report-drift and fault-injection cases | This is a required evaluation gate, not demonstrated systems benefit yet. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Show how score drift becomes a report-correctness risk when boundary metadata is dropped. |
| Contract Design | Define schema and admission states. |
| Artifact Bridge | Explain export, validation, and admitted-only report inputs. |
| Case Studies | Five admitted rows, H2 blocked candidate, Tracing Roots feature packet. |
| Evaluation | Bundle completeness, public-surface checks, admitted-only row-count guard, finite-tail denominator presence, and planned fault-injected report correctness. |
| Deployment Lessons | What evidence is safe to expose and what remains Research-only; no deployed-enforcement claim. |

## Missing-Evidence Promotion Gate

Direction D can be packaged now as an artifact/demo report-correctness paper. It
must not be promoted to a full systems paper until at least one of these gates
has concrete evidence:

| Gate | Minimum evidence before systems-paper promotion | Current state |
| --- | --- | --- |
| Fault-injection | Inject candidate promotion, missing denominator, row-count drift, unsafe source field, or overclaiming language and show the contract/report path blocks or flags it. | Planned only. |
| Report-drift | Compare an unconstrained report path with the contract-governed path and show fewer unsupported claims. | Not measured. |
| External-use | A competition report, third-party reviewer, or non-Research author uses the bundle and records allowed vs blocked claims. | Not collected. |
| Deployment evidence | Public-safe deployment or demo telemetry showing the contract governs report inputs without private topology. | Not collected. |

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
| Promoting a schema-only package to full systems paper | Confuses artifact correctness with measured enforcement. |

## Decision

Hold as an artifact/demo/report-correctness package. It becomes a systems-paper
candidate only after Direction A defines the measurement contract and at least
one missing-evidence gate produces fault-injection, report-drift, external-use,
or deployment evidence.
