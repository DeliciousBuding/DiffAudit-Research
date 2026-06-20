# E2 False-Promotion Internal Pilot

> Date: 2026-06-06
> Scope: internal proxy pilot only; not external adjudication evidence.

This pilot validates the E2 measurement pipeline on 15 existing Direction C surfaces.
It is used to harden the blind review template, stronger baselines, and paired statistics before freezing the final N=50 corpus.

## Outputs

- `e2_false_promotion_pilot_rows.csv`
- `e2_false_promotion_pilot_summary.csv`
- `e2_blind_review_template.csv`
- `e2_blind_review_A.csv`
- `e2_blind_review_B.csv`
- `e2_blind_review_C.csv`
- `e2_blind_review_combined.csv`
- `e2_blind_review_agreement.csv`
- `e2_blind_review_disagreements.csv`
- `e2_blind_review_baseline_summary.csv`
- `e2_blind_review_aggregation.md`

## Proxy Wording Distribution

- `blocked`: 9
- `bounded-support`: 2
- `candidate-only`: 4

## Highest False-Promotion Proxy Rules

- `artifact_availability`: 10/15 (rate `0.6667`, proxy-pilot paired delta CI `[0.4, 0.8667]`)
- `paper_claim_artifact_link`: 10/15 (rate `0.6667`, proxy-pilot paired delta CI `[0.4, 0.8667]`)
- `code_availability`: 4/15 (rate `0.2667`, proxy-pilot paired delta CI `[0.0667, 0.4667]`)

## Proxy Limitation

`paper_claim_artifact_link` is a pilot stress rule here. Some pilot rows use local `docs/evidence/...` notes as reviewer-facing source summaries rather than external paper or official artifact pages. The final N=50 run must evaluate this baseline only against frozen public source links and blind adjudicated wording.

## Stop Boundary

Do not use this proxy summary as a paper result.

## Blind Review Result

Three independent internal reviewers labeled all 15 rows before seeing automatic
baseline decisions.

- allowed wording raw all-reviewer agreement: `0.6667`
- allowed wording mean pairwise kappa: `0.6565`
- provenance gate raw all-reviewer agreement: `0.6`
- consumer/delta gate raw all-reviewer agreement: `0.6667`
- blind-majority false-promotion stress signal:
  - `artifact_availability`: `7/15`
  - `paper_claim_artifact_link`: `7/15`
  - `score_only`: `3/15`

Pilot Go/No-Go: `revise-codebook-rerun-small-pilot`.

Reason: weaker-baseline false-promotion examples exist, but allowed wording raw
agreement is below the protocol target `>= 0.70`; provenance and consumer/delta
gate disagreements are the main ambiguity classes. Refine the codebook before
freezing `N=50`.

Refinement notes:
[`../e2-codebook-refinement-2026-06-06.md`](../e2-codebook-refinement-2026-06-06.md).
