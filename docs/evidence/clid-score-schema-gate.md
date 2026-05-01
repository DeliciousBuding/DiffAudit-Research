# CLiD Score Schema Gate

This note freezes the CPU-only CLiD score-summary gate that must pass before a
large CLiD GPU packet is considered. It is not benchmark evidence.

## Verdict

```text
score schema gate is defined; no GPU packet is selected
```

The gate requires a committed summary schema and ignored raw score artifacts.
It separates three states:

| State | Meaning |
| --- | --- |
| `blocked` | The score summary is missing required fields or uses non-portable artifact references. |
| `ready` + `not_eligible` | The summary schema is reusable, but low-FPR promotion did not pass. |
| `ready` + `eligible` | The summary schema is reusable and the held-out low-FPR gate passed. This only authorizes review as a bounded GPU candidate. |

## Required Summary Fields

A CLiD score summary must contain:

| Field | Requirement |
| --- | --- |
| `status` | Score run status. |
| `track` | Must be `black-box`. |
| `method` | Must be `clid`. |
| `mode` | Must be `score-summary`. |
| `split_identity` | Member/nonmember row counts, metadata alignment, and held-out target split flag. |
| `score_outputs` | Scorer family plus portable references to ignored raw matrices and committed threshold summary. |
| `metrics` | `auc`, `asr`, `tpr_at_1pct_fpr`, and `tpr_at_0_1pct_fpr`. |
| `low_fpr_gate` | Minimum split size, strict-tail metric, promotion rule, and gate result. |

Raw matrices and generated run payloads remain ignored under workspace run
directories. The repository should commit compact summaries and verdict notes
only.

## Review Command

`summarize-clid-artifacts` writes both the legacy `summary.json` and the frozen
`score-summary.json`, then embeds the schema review result under
`score_schema_review`.

For local two-file bridge runs, use `summarize_clid_bridge_pair_outputs.py`.
It writes the same `score-summary.json` contract without pretending that the
released four-file shadow/target evaluator was run.

```powershell
python scripts/review_clid_score_schema.py `
  --summary workspaces/black-box/runs/<clid-score-run>/score-summary.json
```

The review exits successfully when the schema is reusable. Promotion still
requires `promotion_status = eligible`; otherwise the result stays candidate-only.

## Promotion Boundary

- No promotion without a held-out target split.
- No promotion without balanced member/nonmember rows.
- No promotion without numeric AUC, ASR, TPR@1%FPR, and TPR@0.1%FPR.
- No promotion when `tpr_at_0_1pct_fpr` is zero.
- No promotion from absolute local paths or committed raw score matrices.
