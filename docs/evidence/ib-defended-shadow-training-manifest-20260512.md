# I-B Defended-Shadow Training Manifest

Date: 2026-05-12

## Verdict

`blocked preflight; no training run; no GPU release`

The I-B defended-shadow line now has a coverage-aware CPU-only training
manifest. The current target k32 identity contract is blocked before any GPU
work starts because the target forget IDs are mostly absent from the shadow
member datasets. The manifest is a precondition check, not a defense result.

The machine-readable artifact is
[`workspaces/defense/artifacts/ib-defended-shadow-training-manifest-20260512.json`](../../workspaces/defense/artifacts/ib-defended-shadow-training-manifest-20260512.json).
The validator is `scripts/validate_ib_defended_shadow_training_manifest.py`,
including relative forward-slash path checks.

## Question

Can the existing GSA shadow assets and k32 risk-targeted identity files support
a multi-shadow defended-training contract without reusing a target-only pilot
as if it were defended-shadow evidence?

## Hypothesis

If at least two shadow entries have member datasets, checkpoint roots, fixed
forget/matched nonmember identity files, full forget-ID coverage in their
member datasets, and `training_role=defended-shadow`, then the next I-B step
can be a tiny defended-shadow training run instead of another protocol-only
note.

## Falsifier

If fewer than two shadows are ready, the forget/nonmember identity counts do
not match, the identity files contain duplicates, the shadow member datasets do
not cover the required forget IDs, or a future command lacks
`--training-role defended-shadow`, the line remains blocked.

## Preflight Result

The preflight used existing local assets only:

- assets root: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1`
- forget file: `workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/forget-members-k32.txt`
- matched nonmember file: `workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/matched-nonmembers-k32.txt`
- shadow IDs: `shadow-01`, `shadow-02`, `shadow-03`
- planned budget: `100` steps, batch size `4`, seed `0`

The manifest returned `status=blocked` with `32` unique forget members and `32`
unique matched nonmembers. Coverage-aware validation found that the current
target k32 forget list is not a valid shadow-local training contract:

- `shadow-01`: `2/32` forget IDs covered, `30` missing
- `shadow-02`: `2/32` forget IDs covered, `30` missing
- `shadow-03`: `1/32` forget IDs covered, `31` missing

The immediate unblock condition is to construct shadow-local forget identity
files or explicitly remap the defended-shadow contract before any tiny training
run.

## Boundary

This does not execute training, export defended-shadow threshold references,
measure adaptive-attacker behavior, measure retained utility, or report
strict-tail improvement. I-B remains `hold-protocol-frozen` until shadow-local
identity coverage, training outputs, and review metrics exist under the frozen
protocol.

## Validation

```powershell
conda run -n diffaudit-research python -m diffaudit prepare-defended-shadow-training-manifest --workspace workspaces/defense/artifacts/ib-defended-shadow-training-manifest-20260512 --assets-root workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1 --forget-member-index-file workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/forget-members-k32.txt --matched-nonmember-index-file workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/matched-nonmembers-k32.txt --shadow-ids shadow-01,shadow-02,shadow-03 --num-steps 100 --batch-size 4 --seed 0
conda run -n diffaudit-research python scripts/validate_ib_defended_shadow_training_manifest.py
```

The first command returned `status=blocked`; the second validates the curated
flat artifact copied from `summary.json` and preserves the blocker instead of
releasing GPU work.
