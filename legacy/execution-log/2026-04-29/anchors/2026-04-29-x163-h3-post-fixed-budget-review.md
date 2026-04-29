# X-163: H3 Post-Fixed-Budget Review / Freeze-Or-Reselect Decision

## Question

After X162, should H3 receive another GPU packet, a deployable runner contract, or a hard freeze followed by reselection?

## Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x163_h3_post_fixed_budget_review.py`

Command:

```powershell
python -X utf8 legacy/execution-log/2026-04-29/scripts/run_x163_h3_post_fixed_budget_review.py
```

Artifact:

- `workspaces/gray-box/runs/x163-h3-post-fixed-budget-review-20260429-r1/summary.json`

## Evidence

| Gate | Result | Evidence |
| --- | --- | --- |
| fixed-budget low-FPR tail match | pass | selective and all-steps both `0.031250 / 0.031250` |
| full-metric privacy dominance | fail | selective AUC/ASR are weaker than all-steps by `+0.008789 / +0.007813` |
| gate-leak robustness | fail | gate-leak low-FPR worsens to `0.046875 / 0.046875` |
| oracle-route escape robustness | fail | oracle-route escape restores baseline `0.078125 / 0.078125` |

## Verdict

`positive but bounded / freeze H3`

X162 proves H3 is not just a score-level mirage: under a narrow fixed-budget defended-policy attacker, selective routing still matches full all-steps low-FPR tail while routing a minority of samples.

But the branch should now stop as a GPU lane:

- it fails full-metric privacy dominance
- it is sensitive to gate-score leakage
- oracle-route escape recovers baseline
- it remains candidate-only and below deployable runtime claims

## Control State After X-163

- `active_gpu_question = none`
- `next_gpu_candidate = none until X164 selects a genuinely new bounded hypothesis`
- `next live lane = X164 nongraybox next-lane reselection after H3 fixed-budget closure`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change.
- `Docs/materials`: H3 can be mentioned only as internal candidate evidence, not as validated defense.
