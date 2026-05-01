# Semantic-Auxiliary Low-FPR Review

> Status: closed as negative-but-useful on 2026-05-01.

## Verdict

```text
semantic-auxiliary classifiers do not justify a GPU packet under the current protocol
```

The review reuses the existing black-box semantic-auxiliary classifier record
dumps and applies a promotion gate before any GPU work is scheduled.

```powershell
python -X utf8 scripts/review_semantic_aux_low_fpr.py
```

## Gate

| Requirement | Result |
| --- | --- |
| Device | CPU only. |
| Minimum AUC gain over `mean_cos` | `0.01`. |
| Observed best AUC gain over `mean_cos` | `0.001953`. |
| Strict-tail requirement | Candidate metrics must include positive `TPR@0.1%FPR`. |
| GPU decision | Not selected. |

The best observed auxiliary fusion only marginally improves over the plain
`mean_cos` baseline. That makes it useful as a diagnostic surface, but not a
research-mainline packet. The finite split also means strict-tail values should
be interpreted as bounded packet metrics, not a broad deployment claim.

## Evidence Inputs

| Input | Role |
| --- | --- |
| `workspaces/black-box/runs/semantic-aux-classifier-comparator-20260415-r1/outputs/records.json` | First existing comparator record dump. |
| `workspaces/black-box/runs/semantic-aux-classifier-comparator-20260416-r2/outputs/records.json` | Larger existing comparator record dump. |

The review does not create new images, train a new model, or call an endpoint.
It only decides whether the existing semantic-auxiliary surface is strong enough
to consume the next GPU slot.

## Decision

- Keep semantic-auxiliary classifiers as black-box diagnostic support.
- Do not schedule a semantic-auxiliary GPU packet under the current protocol.
- Do not promote the auxiliary fusion as a Platform or Runtime product row.
- Reopen only if a new contract shows a material gain over `mean_cos` while
  preserving low-FPR behavior on a held-out split.
