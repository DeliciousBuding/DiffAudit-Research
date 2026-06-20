# DiffAudit Admitted Risk Card

> Public-safe case-study report surface generated from the admitted evidence bundle.

- Source bundle: `workspaces/implementation/artifacts/admitted-evidence-bundle.json`
- Bundle status: `admitted-only`
- Report surface: `report-facing case-study artifact`
- Row count: `5`
- Boundary: three rows are replay-admitted from row/target-score arrays; two rows are source-documented point estimates.
- Candidate exclusion: H2 output-cloud geometry, Tracing the Roots, ReDiffuse, CommonCanvas, MIDST, CLiD, weak scouts, and source-confounded packets are not reportable audit rows in this card.
- Tail caveat: low-FPR values are finite packet readouts, not calibrated continuous sub-percent risk estimates.

| Report role | Access | Method | AUC | TPR@0.1%FPR | Replay/source tier | Tail n0 | Required caveat |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| primary-risk-evidence | black-box | recon DDIM public-100 step30 | 0.837 | 0.11 | source-documented point estimate | 100 | controlled / public-subset / proxy-shadow-member / risk-exists; TPR@0.1%FPR is a zero-false-positive empirical tail on 100 target nonmembers; not a final exploit, paper-complete reproduction, or full real-world benchmark |
| primary-risk-evidence | gray-box | PIA GPU512 baseline | 0.841339 | 0.011719 | row-score replay | 512 | row-score replay with adaptive review recorded; checkpoint/source provenance limits broader paper-alignment wording |
| defense-comparator | gray-box | PIA GPU512 baseline / provisional G-1 = stochastic-dropout (all_steps) | 0.828075 | 0.009766 | row-score replay | 512 | row-score replay with adaptive review recorded; checkpoint/source provenance limits broader paper-alignment wording |
| upper-bound-comparator | white-box | GSA 1k-3shadow | 0.998192 | 0.432 | source-documented point estimate | 1000 | white-box upper-bound comparator; not a final paper-level benchmark |
| defense-bridge | white-box | GSA 1k-3shadow / W-1 strong-v3 full-scale | 0.488783 | 0 | target-score replay | 1000 | white-box defense bridge comparator; not a final paper-level benchmark |

## Report-Correctness Rules

- Do not rank these rows as a cross-access leaderboard.
- Do not describe source-documented point estimates as replay-admitted rows.
- Do not add candidate, support-only, watch, weak-scout, or source-confounded rows to this card without a reviewed admission-state change.
- Do not interpret finite low-FPR tails as calibrated continuous sub-percent rates.
