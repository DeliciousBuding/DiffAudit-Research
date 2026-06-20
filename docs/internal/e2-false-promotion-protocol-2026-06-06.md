# E2 False-Promotion Protocol

> Date: 2026-06-06
> Scope: internal protocol for the CCF-A measurement-paper upgrade path.

## 1. Hypothesis

DiffAudit's evidence contract has scientific value if it measurably prevents
false claim promotion compared with weaker review rules.

The experiment is not a new attack benchmark. It tests whether a claim-admission
protocol changes externally adjudicated paper/artifact decisions.

## 2. Corpus Freeze

Target corpus: `50` distinct diffusion/privacy artifact surfaces.

Inclusion rule:

- one row per distinct target surface, not one row per paper paragraph;
- diffusion generator, diffusion defense, diffusion reconstruction, output
  response, score packet, or artifact-surface claim related to privacy,
  membership, memorization, copying, or reportability;
- source must be public and citeable through paper, official repository, model
  card, dataset card, artifact archive, or official supplementary material.

Exclusion rule:

- no duplicate title/same-repo variants unless they expose a distinct target,
  split, score, response, or consumer boundary;
- no private-only asset, local-only collaborator bundle, inaccessible drive
  payload, or paper-only claim without a public source URL;
- no row whose only purpose is to pad a known weak family.

Relationship to existing Direction C corpus:

- existing `21 / 17 / 10 / targeted-L1` records may seed the corpus, but E2
  must freeze its own denominator as `E2-20260606-N50`;
- existing records are not pooled automatically; each included surface receives
  a new E2 row id and gate annotation;
- the E2 corpus supports false-promotion measurement only, not field prevalence
  or artifact-quality prevalence.

## 3. Internal Pilot First

Before the final external-adjudication run, run an internal blind pilot over
`10-15` rows. The pilot must cover at least:

- one positive/reportable control;
- one high-AUC non-admitted candidate;
- one official-code/no-row-packet surface;
- one split-visible/no-metric surface;
- one weak negative/support packet.

The pilot rows do not become the final `N=50` denominator unless the final
protocol explicitly freezes them and they are re-labeled blind.

Internal reviewers must label gates and allowed wording before seeing automatic
baseline or DiffAudit decisions.

Current revised pilot workspace:
[`e2-pilot-2026-06-06-v2/`](e2-pilot-2026-06-06-v2/). Its aggregation supports
the internal Go/No-Go decision only; it is not external adjudication evidence.
The first pilot remains archived in
[`e2-pilot-2026-06-06/`](e2-pilot-2026-06-06/).

Pilot row template:

| Field | Purpose |
| --- | --- |
| `pilot_id` | Stable pilot id. |
| `title` | Public surface title. |
| `source_url` | Public source, paper, repository, model card, dataset card, or local evidence note. |
| `artifact_url` | Public artifact surface or compact artifact description. |
| `observed_public_files` | Files or records visible to a reviewer before seeing automatic decisions. |
| `consumer_question` | The audit/report claim the reviewer must judge. |
| `reviewer` | Reviewer id. |
| `target_gate` | Blind reviewer label: `Pass / Partial / Fail / N/A`. |
| `split_gate` | Blind reviewer label: `Pass / Partial / Fail / N/A`. |
| `score_or_response_gate` | Blind reviewer label for row-bound scores, responses, or features. |
| `metric_gate` | Blind reviewer label for metric provenance and recomputability. |
| `provenance_gate` | Blind reviewer label for source, hash, and artifact identity. |
| `consumer_or_delta_gate` | Blind reviewer label for downstream use and surface-delta boundaries. |
| `allowed_wording` | `admitted`, `bounded-support`, `candidate-only`, or `blocked`. |
| `first_blocker` | First missing artifact that prevents stronger wording. |
| `notes` | Short reviewer note; no baseline decision leakage. |

## 4. Baseline Rules

Each row receives four decisions.

| Rule | Admit condition | Output |
| --- | --- | --- |
| Score-only | source reports AUC, ASR, TPR, or equivalent above its own claimed threshold | `admit / block` |
| Code-availability | official or author-linked code repository exists | `admit / block` |
| Artifact-availability | any public split, checkpoint, response, score, dataset, or generated artifact exists | `admit / block` |
| Paper-claim + artifact-link | paper or official source states a privacy/membership claim and links any artifact surface | `admit / block` |
| Metric + code + split | reported metric plus official code and stated split or split artifact | `admit / block` |
| Reproducibility-checklist | target, split, evidence, and metric surfaces are all present before consumer-boundary review | `admit / block` |
| DiffAudit contract | target identity, split identity, row-bound score or response coverage, metric provenance, consumer boundary, and surface-delta gates support bounded wording | `admit / block / bounded-support` |

DiffAudit `bounded-support` is counted as a block for false-promotion rate, but
is reported separately because it can be a valid limited scientific claim.

Pilot limitation: `paper-claim + artifact-link` may use local evidence notes as
reviewer-facing source summaries during internal calibration. The final `N=50`
external run must apply this rule only to frozen public source links and blind
adjudicated wording.

## 5. External Adjudication

Minimum adjudicators: `2` independent reviewers who did not create the E2 row.

Task format:

- reviewer first sees only public source links, the frozen row summary, and the
  consumer question;
- reviewer labels six gates as `Pass / Partial / Fail / N/A`:
  `target`, `split`, `score_or_response`, `metric`, `provenance`,
  `consumer_or_delta`;
- C14 false-promotion stress reviews may split `consumer_or_delta` into
  `semantic_boundary` and `consumer_boundary`, yielding seven gate columns,
  because several controls are blocked by task mismatch before downstream
  consumer fit can be judged;
- reviewer selects allowed wording:
  `admitted`, `bounded-support`, `candidate-only`, `blocked`.
- only after blind labels are recorded, show automatic baseline and DiffAudit
  decisions for disagreement review.

Agreement threshold:

- gate-level Cohen's kappa target: `>= 0.60`;
- final wording kappa target: `>= 0.50`, or raw agreement `>= 70%`;
- consumer/delta-gate disagreement rate must be reported separately;
- if kappa is `< 0.60`, do not claim reliability; use adjudication only to
  identify ambiguity classes and rewrite the protocol;
- disagreements are resolved by a third maintainer only for final row wording,
  not for inflating reliability statistics.

## 6. Metrics

Primary metric:

- false-promotion rate for each weaker rule against adjudicated final wording.

Definitions:

- false promotion: baseline rule says `admit` while adjudicated wording is
  `candidate-only` or `blocked`;
- false block: baseline rule says `block` while adjudicated wording is
  `admitted`;
- bounded-support mismatch: baseline rule says `admit` while adjudicated wording
  is `bounded-support`.

Report:

- `FPR_promotion(rule)`;
- `FPR_promotion(rule) - FPR_promotion(DiffAudit)`;
- paired row bootstrap `95%` CI over rows;
- confusion categories and the top five disagreement examples.

## 7. Success And Stop Gates

Pilot Go/No-Go gate:

- at least `10` rows, with all five required pilot strata represented;
- reviewers label gates and allowed wording before seeing automatic baseline or
  DiffAudit decisions;
- final wording raw agreement is `>= 70%` or disagreement classes are concrete
  enough to rewrite the protocol before corpus freeze;
- at least two weaker baselines produce clear false-promotion examples under
  the proxy/adjudicated wording;
- all pilot outputs stay marked `internal_proxy_not_external_adjudication`.

If the pilot fails this gate, rewrite the codebook and rerun a small pilot. Do
not expand to `N=50` until the blind workflow is understandable.

Current 2026-06-06 v2 pilot decision:
`go-freeze-n50-preflight`. Three revised-codebook reviewers completed all
`15` rows; allowed wording raw agreement is `0.9333`, provenance agreement is
`1.0`, consumer/delta agreement is `0.8`, and weaker-baseline false-promotion
examples exist for four weaker baselines. Proceed to `N=50` freeze preflight,
while keeping all pilot outputs internal and non-external.

Current N=50 preflight:
[`e2-n50-freeze-preflight-2026-06-06/`](e2-n50-freeze-preflight-2026-06-06/)
contains `51` distinct seed rows and `23` actionable candidate/followup rows,
but strict triage finds `0` rows directly freezable into the external
denominator. Five rows are current external candidates after source refresh and
row-bound artifact review; six actionable rows have no public URL candidate and
must stay internal-only unless a public source replaces the local/restricted
evidence note. A separate no-download scout queue contributes `27` new
public-surface candidates for source refresh and duplicate review. None of
these scout rows count toward `E2-20260606-N50` until they pass public-source
refresh, distinct-surface review, and six-gate annotation. C14 false-promotion
stress rows additionally keep the semantic-boundary split described above.

Success for CCF-A measurement push:

- at least `50` frozen rows;
- kappa `>= 0.60`;
- DiffAudit false-promotion rate is `<= 10%` in final adjudication;
- DiffAudit false-promotion rate is at least `15` percentage points lower than
  at least two non-trivial baselines, one of which must be `paper-claim +
  artifact-link`, `metric + code + split`, or `reproducibility-checklist`;
- paired bootstrap `95%` CI for at least one stronger-baseline-vs-DiffAudit
  delta excludes `0`;
- examples show concrete allowed-wording changes, not just bookkeeping.

Downgrade to bounded measurement paper if:

- fewer than `50` rows pass source freeze;
- external agreement is `< 0.60`;
- baseline deltas are small or CI crosses `0`;
- most disagreements are about terminology rather than evidence-state changes.

Stop rule:

- do not add more corpus rows after `N=50` just to rescue weak deltas;
- do not add a new baseline unless it changes a reviewer-facing claim;
- do not run GPU work for E2.

## 8. Branch Decision

After E2 and the second-asset scout:

- if E2 succeeds and no second asset is strong, push Direction A as a CCF-A
  measurement paper;
- if second asset succeeds with row-bound low-FPR evidence, consider Direction B
  or a new observable paper;
- if both fail, keep Direction A as bounded measurement work and stop CCF-A
  claims until new evidence appears.
