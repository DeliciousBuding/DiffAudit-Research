# E2 Reviewer Instructions V2

> Scope: internal blind review only. Do not inspect automatic baseline decisions
> or previous reviewer labels before filling your CSV.

## Allowed Inputs

You may read:

- `e2_blind_review_template.csv`
- local source notes referenced by `docs/evidence/...`
- the row's `source_url`, `artifact_url`, and `observed_public_files` fields
- this instruction file

You must not read before labeling:

- `e2_false_promotion_pilot_rows.csv`
- `e2_false_promotion_pilot_summary.csv`
- any `e2_blind_review_*.csv`
- `e2_blind_review_agreement.csv`
- `e2_blind_review_disagreements.csv`
- `aggregate_e2_blind_review.py`

Do not download large files, clone repositories, run training, or run GPU jobs.

## Gate Labels

Each gate must be `Pass`, `Partial`, `Fail`, or `N/A`.

### Target Gate

Does the row identify the relevant model, dataset, target surface, checkpoint,
artifact family, or response/score surface enough for the audit claim?

### Split Gate

Does the row identify member/nonmember, query, split, or equivalent row labels
well enough to interpret the evidence?

### Score Or Response Gate

Does the row expose row-bound scores, responses, features, or score-equivalent
outputs? Code, paper metadata, aggregate metrics, and README descriptions alone
do not pass this gate.

### Metric Gate

Can a reviewer recompute or verify the reported metric from the exposed rows or
from a stable metric/verifier surface? Aggregate text without a replay surface
does not pass this gate.

### Provenance Gate

`Pass` requires enough source identity for another reviewer to locate the same
evidence surface without guessing. For final `N=50`, this means public URL plus
immutable artifact identity or hash. In this internal pilot, local
`docs/evidence/...` notes can summarize sources, but provenance should usually
be `Partial` unless the underlying public artifact is itself stable.

### Consumer Or Delta Gate

This gate asks whether the evidence can support a downstream audit/report
statement at the claimed wording.

- `Pass`: admitted report row with row-bound metric and consumer boundary.
- `Partial`: bounded negative/support claim with exact local packet or public
  split/code surface, but not positive audit admission.
- `Fail`: source-confounded, missing row scores/responses, no verifier, or no
  downstream consumer path.

Strong metrics, public code, public split files, or mechanism evidence do not
pass this gate by themselves.

## Allowed Wording

- `admitted`: target, split, row packet, metric provenance, provenance, and
  consumer/delta gates are sufficient for the audit/report claim.
- `bounded-support`: evidence can support a limited negative, missing-surface,
  reproduction-context, or mechanism-support claim without positive audit
  admission.
- `candidate-only`: relevant public source/artifact exists, but the row cannot
  yet support a bounded claim with stable evidence.
- `blocked`: metadata-only, withdrawn, inaccessible, irrelevant, or no concrete
  artifact/source surface.

## Specific Ambiguity Rules

- Metadata-only public paper rows are `blocked` when no target/split/
  score/response/metric artifact is visible in the row packet. Use
  `candidate-only` only when at least one concrete public artifact surface
  exists but fails row-bound gates.
- Code-only rows with no target-bound scores/responses and no verifier should
  default to `candidate-only` if the source is current and relevant. Use
  `blocked` if the row lacks current paper/source availability or the claim
  target cannot be identified.
- Exact split plus row-level score packet can be `bounded-support` for a
  negative or boundary claim even when the metric is weak. Reserve
  `candidate-only` for positive audit claims that cannot be admitted.
- Public split/code without committed row scores is `bounded-support` only when
  it can support a limited missing-surface or reproduction-context claim;
  otherwise use `candidate-only`.
- Official aggregate score/log/tensor artifacts without compact row manifest
  are `bounded-support`; consumer/delta remains `Fail` until row id, split
  label, target/checkpoint hash, and verifier are bound in one manifest.

## Output Format

Return strict CSV with this header:

```csv
pilot_id,reviewer,target_gate,split_gate,score_or_response_gate,metric_gate,provenance_gate,consumer_or_delta_gate,allowed_wording,first_blocker,notes
```

