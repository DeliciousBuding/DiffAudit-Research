# Direction A Draft: Evidence-Contracted Auditing

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Paper PI | Framework lead | Controls thesis, venue fit, contribution language, and rebuttal posture. |
| Evidence engineer | Metric audit lead | Verifies admitted-row metrics, finite-tail denominators, scripts, and evidence-source provenance. |
| Figures editor | Visualization lead | Owns evidence-contract diagrams, bundle charts, and candidate/admitted visual separation. |
| Internal area chair | Validity critic | Blocks governance-only prose and unsupported generalization. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | DiffAudit: Evidence-Contracted Membership Leakage Auditing for Diffusion Models |
| Target type | Full security/privacy measurement paper |
| Venue posture | CCF-B security/privacy or measurement venue, after expanding method and corpus framing |
| Current artifact | Active LaTeX draft: [`../../main.tex`](../../main.tex) |

## Abstract

Membership inference results for diffusion models are often reported as scalar
attack metrics, but a privacy audit needs more than a high AUC. It needs a
contract tying each claim to a target identity, member and nonmember semantics,
score or response coverage, metric provenance, consumer-boundary language, and
surface-delta evidence. This paper introduces DiffAudit, an
evidence-contracted methodology for diffusion membership leakage auditing. The
method separates admitted audit evidence from candidate mechanisms,
support-only packets, and bounded negative evidence. In the current bundle,
DiffAudit admits five rows spanning black-box reconstruction, gray-box PIA,
stochastic-dropout comparison, white-box GSA, and a DPDM defense comparator. It
also identifies a strong H2 output-cloud geometry candidate with AUC `0.961529`,
but refuses to admit it after a weak SD/CelebA img2img portability check. The
result is not a claim of universal diffusion-model membership leakage. It is a
measurement framework for deciding when diffusion MIA scores become reusable,
row-bound, consumer-safe privacy evidence.

## Controlling Thesis

The scientific contribution is evidence calibration. Diffusion MIA research has
many attractive scores, but the audit question is narrower: which scores can be
reused by another consumer without changing target identity, split semantics,
metric meaning, or artifact boundary? DiffAudit turns this into a concrete
measurement contract and shows that positive, candidate, and negative results
all have decision value when their boundaries are explicit.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| A-C1: A six-gate contract can separate admitted diffusion audit evidence from candidate/support evidence. | [`../../claim_register.md`](../../claim_register.md), [`../../source_map.md`](../../source_map.md) | Methodological claim, not a claim that all public papers fail the gates. |
| A-C2: Five admitted rows can be reported under one contract. | [`../../evidence_bank.md`](../../evidence_bank.md) admitted rows | Workspace/runtime semantics only; finite tails are packet readouts. |
| A-C3: The admitted white-box GSA row is numerically stronger under its own contract than the current admitted black-box and gray-box rows. | recon AUC `0.837`, PIA AUC `0.841339`, GSA AUC `0.998192` | Upper-bound comparator only; not an access-level leaderboard or universal benchmark. |
| A-C4: Strong candidates can be scientifically useful even when non-admitted. | H2 AUC `0.961529`, transfer mean `0.959755`, img2img AUC `0.7888` | H2 remains Research-side, not product/admitted evidence. |
| A-C5: Negative gates prevent false portability claims. | ReDiffuse, CommonCanvas, MIDST, Tracing Roots, CopyMark, SD ReDiffuse notes | Does not disprove original methods. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Open with the gap between attack scores and audit evidence. Explain why high-AUC diffusion MIA results can be unusable when target identity, split semantics, row coverage, or consumer boundary are missing. |
| Related Work | Position against classical MIA, diffusion MIA, image memorization/copying, and artifact reproducibility. The role is not to claim first attack, but to show why audit consumption needs a contract. |
| Evidence Contract | Define target identity, split semantics, score/response coverage, metric provenance, consumer boundary, and surface delta. Include finite-tail language. |
| Measurement Protocol | Explain admitted/candidate/support/blocked states; show how metrics are generated from existing JSON artifacts and why no candidate can bypass gates. |
| Artifact Corpus | Introduce the current corpus as a controlled evidence set, then state its limits. Use Direction C expansion as future broadening, not as completed broad-literature proof. |
| Admitted Bundle | Present five admitted rows with metrics, costs if available, access mode, and caveat. |
| H2 Case Study | Show output-cloud geometry as a positive candidate and explain the controls: label shuffle, shared-position seed policy, seed stability, and cross-cache transfer. |
| Negative and Support Evidence | Use weak scouts and feature packets to show why second-asset claims require more than scoreability. |
| Discussion | Defend evidence contracts as measurement science, not paperwork. Explain what future papers should publish to become reusable. |
| Threats to Validity | Cover local artifact bias, corpus size, finite tails, candidate boundary, and lack of broad portability. |

## Figure and Table Plan

| Asset | Purpose | Status |
| --- | --- | --- |
| Evidence-contract pipeline | Shows how rows move from artifact to admitted/candidate/support state. | In active LaTeX. |
| Admitted metric chart | Makes five-row bundle legible without hiding caveats. | Generated from JSON-derived CSV. |
| H2 controls chart | Shows candidate signal, label-shuffle sanity, shared-position control, and transfer. | Generated. |
| Candidate/support gate matrix | Prevents H2, Tracing Roots, and weak scouts from reading like admitted rows. | In active LaTeX. |
| Artifact-corpus funnel | Needed for stronger CCF-B posture. | Not yet drawn; depends on Direction C metadata expansion. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Reads like internal governance. | Put measurement problem first: score-only claims are not reusable evidence. |
| Admitted bundle is narrow. | State it as a controlled admitted bundle and use candidate/negative evidence to show why admission is hard. |
| H2 looks like the real paper. | Keep H2 as a case study inside the contract paper unless a second response asset appears. |
| Negative evidence looks cherry-picked. | Use Direction C as selected-corpus claim-control evidence now; require broader corpus or a second independent label review before standalone aggregate claims. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Continue as main LaTeX | Already satisfied: uses all evidence without overclaiming. |
| Continue tightening the 8-page LaTeX draft | Preserve the page budget while improving motivation, method detail, and reviewer-facing contribution wording. |
| Submit as CCF-B-style measurement paper | Needs broader artifact-corpus framing and a final claim audit. |
| Stop | If it cannot be framed as measurement science rather than project documentation. |
