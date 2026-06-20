# Version D: Independent Artifact Contract and Consumer Boundary

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Systems lead | Contract architecture lead | Architecture, threat model, consumer-boundary semantics. |
| Contract engineer | Bundle validation lead | Bundle schema, export checks, public-surface checks, reproducibility hooks. |
| Product/report lead | Report correctness lead | UI/report diagrams, risk card language, bilingual copy alignment. |
| Public-boundary critic | Public-boundary critic | Block private topology and unsupported product claims. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Paper type | Independent artifact-contract/demo/report-correctness package; not a deployed systems paper without promotion evidence |
| Venue posture | Demo/artifact appendix now; applied security systems only after measured report-drift reduction, external-use, or public-safe deployment/demo enforcement exists; current fault-injection supports artifact/demo claims only |
| Current status | Artifact-contract appendix/demo version; full systems claim is no-go until systems evidence beyond selected artifact checks is observed |

## Abstract Draft

Membership inference outputs are hard to consume safely: a score may be
positive under a narrow experiment, candidate-only under a research boundary, or
non-portable because artifacts lack row binding. This paper describes an
artifact contract that encodes diffusion privacy results as machine-checkable
evidence bundles with report-correctness obligations. Direction D is written as a
self-contained artifact-contract paper: the contract records target identity,
split semantics, metrics, finite-tail denominators, provenance, boundary
language, and admission state, and the report surface must preserve those
fields. The exported bundle encodes a reportable mixed-strength bundle: three
replay-admitted rows from row/target-score arrays and two source-documented
point-estimate rows. Strong research candidates such as H2 output-cloud
geometry and Tracing the Roots are kept as manually blocked promotion examples
in the vetted card. The current evidence
supports an artifact/demo paper package; it does not evaluate deployed
enforcement, external adoption, or measured prevention of report drift.

## Core Thesis

Research metrics become user-facing audit evidence only through an artifact
contract that preserves admission state, provenance, finite-tail semantics, and
boundary language. Direction D is an independent artifact-contract and
report-correctness package: it specifies the contract, defines the public-safe
report boundary, and lists selected unsafe report states that should fail. A
generated public-safe risk card now exists and is checked by
`scripts/render_admitted_risk_card.py --check`; the reusable fault matrix in
`papers/diffaudit-evidence-paper/versions/direction-d-report-correctness-fault-injection.md`
records 28 selected release-wording cases: one accepted baseline, four renderer
mutations rejected, three fixed phrase flags, two fixed clean controls, eight
candidate/support promotion mutations, six metadata-only promotion mutations,
and four clean boundary phrase controls. These are selected checks, not a
semantic verifier or measured report-drift evaluation. It becomes a full
systems paper only after measured evidence shows report-drift reduction,
correct external use, or public-safe deployment/demo enforcement. Until then,
Direction D may claim a machine-readable artifact contract, a generated report
boundary, and selected renderer/direct-phrase fault checks, but not deployed
systems impact.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| D1: Machine-checkable evidence bundles encode replay/source tiers and admitted/candidate separation. | `admitted-evidence-bundle.json`, public-surface checks | Current reportable bundle has five rows only, with mixed replay strength; deployed enforcement is not evaluated. |
| D2: Candidate visibility and reportable admission must be separated. | H2 and Tracing Roots boundary notes | No new reportable rows or deployed-enforcement claim. |
| D3: Finite-tail semantics need consumer-facing language. | TPR@0.1%FPR denominator notes | Does not calibrate sub-percent risk. |
| D4: Selected report-surface fault cases can be observed before a systems claim. | `papers/diffaudit-evidence-paper/versions/direction-d-report-correctness-fault-injection.md`, `papers/diffaudit-evidence-paper/data/report_correctness_fault_injection.csv`, `scripts/evaluate_report_correctness_faults.py --check`, `scripts/render_admitted_risk_card.py --check`, and `scripts/check_public_surface.py` direct-phrase checks | The generated matrix passes 28 selected expected outcomes: one accepted baseline, four renderer mutations rejected, three fixed phrase flags, two fixed clean controls, eight candidate/support promotion mutations, six metadata-only promotion mutations, and four clean boundary phrase controls. Report-drift reduction, external use, and deployment enforcement remain unmeasured. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Show how score drift becomes a report-correctness risk when boundary metadata is dropped. |
| Contract Design | Define schema and admission states. |
| Artifact Bridge | Explain export, existing checks, and reportable-row inputs with replay/source tiers. |
| Boundary Examples | Five reportable rows, H2 manually blocked candidate, Tracing Roots feature packet. |
| Evaluation | Static bundle-completeness, public-surface hygiene, reportable-row tier preservation, finite-tail denominator checks, and observed bundle/risk card renderer checks; report-drift responses remain planned until measured. |
| Public-Safe Lessons | What evidence is safe to expose and what remains research-only; no deployed-enforcement claim. |

## Hard Go / No-Go Gate

Direction D can be packaged now as an artifact/demo report-correctness paper. It
must not be promoted to a full systems paper, or make a full systems claim,
until report-drift reduction, external use, or public-safe deployment/demo
enforcement has concrete observed evidence. The current fault-injection rows are
artifact/demo evidence only; they do not by themselves count as a systems
promotion gate.

| Evidence class | Required role before systems-paper promotion | Current state |
| --- | --- | --- |
| Fault-injection | Artifact/demo correctness evidence unless tied to measured report-surface drift reduction over realistic reports. | Generated 2026-06-09 matrix: `scripts/evaluate_report_correctness_faults.py --check` verifies 28 selected outcomes. The risk card renderer accepts the current admitted bundle and rejects four mutations: candidate-row replacement, missing nonmember denominator, private source path, and row-count drift. The direct-phrase scan flags direct H2/Tracing Roots promotion, candidate/support promotion mutations, and metadata-only promotion mutations while accepting negated or boundary-preserving language and the generated card. Full report-renderer A/B drift remains unmeasured. |
| Report-drift | Compare an unconstrained report path with the contract-governed path and show fewer unsupported claims. | Boundary no-drift audits exist for 2026-05-12 and 2026-05-15. `run_pr_checks.py` now includes a tiny report-language A/B smoke: an unconstrained H2 admission sentence is flagged while the generated admitted risk card text has no candidate-promotion hit. This is not a measured drift-reduction evaluation. |
| External-use | A competition report, third-party reviewer, or non-Research author uses the bundle and records allowed vs blocked claims. | Not collected. |
| Deployment evidence | Public-safe deployment or demo telemetry showing the contract governs report inputs without private topology. | Not collected. |

Even with the current fault-injection evidence, the decision is still no-go for
full systems framing. The allowed claim is limited to artifact-contract design,
generated bundle/report boundary preservation, and selected observed blocking
cases, not measured report-drift reduction.

## Two-Level Promotion Gate

Direction D now has a demo gate and a systems/tool-paper gate. Passing the demo
gate makes it a useful artifact appendix or demo package; it does not authorize
systems-effectiveness language.

| Gate level | Required artifacts | Current decision |
| --- | --- | --- |
| Demo gate | Public-safe risk card, fault-injection table mapped to existing checks, no-private-surface scan, admitted-bundle check command recorded, and architecture figure. | Passed for static bundle/public-surface checks, generated risk card check, reusable selected-fault matrix (28 selected renderer and phrase-guard cases), and a static architecture SVG. Editorial integration is still needed before submission. |
| Systems/tool-paper gate | Report-renderer A/B drift reduction, semi-external use, or public-safe deployment/demo enforcement. | Not passed. Bundle-level fault-injection and consumer-boundary no-drift audits exist, but they support artifact/demo correctness only; report-renderer A/B drift reduction, external use, and deployment enforcement are not measured. Do not claim drift reduction, external adoption, deployed enforcement, or broad systems impact. |

## Existing Consumer-Drift Evidence

Direction D can cite two existing consumer-boundary drift audits without
creating a new report framework:

| Audit | What was checked | Observed result | Boundary |
| --- | --- | --- | --- |
| `docs/evidence/admitted-consumer-drift-audit-20260512.md` | Candidate closures and hold decisions after SecMI, I-B, I-C, H2/simple-distance, CLiD, and related work. | Validators/exporters passed; admitted bundle stayed `row_count=5`; excluded candidates stayed non-consumable. | No proof of report-renderer drift reduction. |
| `docs/evidence/admitted-consumer-drift-audit-20260515.md` | Watch, watch-plus, support-only, candidate-only, defense, cross-modal, score-packet, paper-source, withdrawn, and artifact-incomplete lines. | Validators/exporters passed; admitted bundle stayed `admitted-only` with `row_count=5`; excluded lines remained non-consumable. | No external adoption or deployed enforcement claim. |

These audits are report-boundary evidence, not a systems effectiveness study.
They support a limited statement: existing checks preserved the admitted-only
consumer boundary across two rounds of Research-side candidate churn.

## Generated Public-Safe Risk Card and Fault Matrix

This is the maximum report surface Direction D may expose before report-drift,
external-use, or deployment evidence exists. It is generated at
`workspaces/implementation/artifacts/admitted-risk-card.md` from
`workspaces/implementation/artifacts/admitted-evidence-bundle.json` by
`scripts/render_admitted_risk_card.py`. It is a mixed-strength case-study card,
not a benchmark card.

Path convention: command and artifact paths in this brief are relative to the
`Research/` repository root.

| Card field | Public-safe wording |
| --- | --- |
| Scope | "DiffAudit case-study bundle for diffusion privacy evidence consumption." |
| What is shown | Five bounded report roles with access surface, replay/source tier, finite-tail caveat, and allowed report wording. |
| What is hidden | Candidate rows, private topology, local machine paths, real deployment domains, secrets, and any non-public raw artifact path. |
| Required banner | "Rows are role-separated. Three rows are replay-admitted from row/target-score arrays; two rows are source-documented point estimates. This card is not a cross-access leaderboard." |
| Candidate banner | "H2 output-cloud geometry, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, CLiD, weak scouts, and source-confounded packets are not reportable audit rows in this card." |

| Report role | Evidence tier | Public metric line | Finite-tail / boundary caveat | Allowed card sentence |
| --- | --- | --- | --- | --- |
| Black-box public-subset risk | Source-documented point estimate | Recon DDIM public-100 AUC `0.837`, TPR@0.1%FPR `0.11` | Finite packet over `100` public nonmembers; no sidecar interval or real-world deployment claim. | "A controlled public-subset black-box signal is reportable under the stated packet." |
| Gray-box primary risk | Row-score replay | PIA GPU512 AUC `0.841339`, TPR@0.1%FPR `0.011719` | Row replay over `512` nonmembers; finite empirical tail only. | "A row-score replay gray-box DDPM/CIFAR10 signal is reportable under the stated query budget." |
| Gray-box defense comparator | Row-score replay | PIA + stochastic-dropout AUC `0.828075`, TPR@0.1%FPR `0.009766` | Comparator only; not validated privacy protection. | "The provisional defense comparator remains measurable but is not a final defense claim." |
| White-box upper-bound comparator | Source-documented point estimate | GSA AUC `0.998192`, TPR@0.1%FPR `0.432` | Upper-bound comparator only; no access-level winner or interval/dominance claim. | "A white-box comparator gives an upper-bound role under its own access assumption." |
| Target-score defense bridge | Target-score replay | DPDM W-1 AUC `0.488783`, TPR@0.1%FPR `0.0` | Defense bridge; not a final benchmark or general privacy guarantee. | "The DPDM bridge is a target-score replay row showing the stated defense-side measurement." |

The card must reject or caveat any attempt to add H2, Tracing Roots, ReDiffuse,
CommonCanvas, MIDST, CLiD, weak scouts, or source-confounded packets as public
reportable rows.

The current fault matrix is generated at
`papers/diffaudit-evidence-paper/versions/direction-d-report-correctness-fault-injection.md` and
checked by `scripts/evaluate_report_correctness_faults.py --check`.

| Renderer / language check | Observed response | Boundary |
| --- | --- | --- |
| Current admitted bundle to generated card | `render_admitted_risk_card.py --check` passes; generated card has five rows. | Confirms the public report surface is synchronized with the admitted bundle. |
| H2 candidate replaces an admitted row | Renderer exits `2` with `risk card refuses non-admitted row`. | Rejects candidate leakage into the reportable risk card. |
| Missing nonmember denominator | Renderer exits `2` with `risk-card row ... missing nonmember denominator`. | Rejects finite-tail wording when the denominator is absent. |
| Private source field in a risk card row | Renderer exits `2` with `contains private surface`. | Rejects local path leakage before the card is emitted. |
| Row-count drift | Renderer exits with `row_count drift`. | Rejects stale or malformed report-card input counts. |
| Direct candidate-promotion sentence | Direct-phrase scan flags H2 and Tracing Roots promotion snippets. | Flags selected report-language overclaims before publication; this is not a semantic language verifier. |
| Generated current risk card | Direct-phrase scan reports no candidate-promotion hit. | Confirms the guarded output does not contain the selected promotion patterns. |
| Internal evidence-level label | Generated card maps internal `runtime-smoke` to report-facing `target-score replay`. | Avoids exposing internal runtime labels as public evidence tiers. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Add one external-adopter or competition-report usage case. | Would turn internal contract use into systems evidence if allowed vs blocked claims are recorded. |
| Measure renderer A/B report drift before/after guardrails. | Would provide a systems evaluation beyond the current tiny report-language smoke if unsupported-claim reduction is observed on realistic report drafts. |
| Integrate the rendered architecture SVG into the final artifact/demo package. | Makes the bridge understandable to non-Research reviewers. |
| Extend fault injection from current row validation to report-renderer A/B drift. | Required before systems/tool-paper claims; current bundle/risk-card fault injection and no-drift audits are observed, but report-surface reduction behavior is not measured. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Writing private deployment topology into public docs | Violates release policy. |
| Adding Runtime modes for candidates | Would break the admitted/candidate boundary. |
| Claiming user impact without usage evidence | Weak systems paper. |
| Promoting a schema-only package to full systems paper | Confuses artifact correctness with measured enforcement. |

## Decision

Proceed with Markdown artifact/demo preparation. The current package has a
generated public-safe risk card, admitted-bundle/public-surface checks, an
observed selected-fault matrix with four renderer mutations rejected and two
direct-promotion phrases flagged, plus a static architecture SVG for the
artifact/demo draft. Editorial integration is still needed before submission.
Report-drift,
external-use, or deployment evidence is required before adding full
systems-paper claims.
