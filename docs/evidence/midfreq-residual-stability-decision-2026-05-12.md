# Mid-Frequency Residual Stability Decision

## Verdict

`release-one-stability-probe; no admitted promotion`

The first `64/64` same-noise residual sign-check is candidate-only, with
moderate AUC and finite strict-tail recovery. A single seed-only stability
probe is worth one GPU slot because it can change the line-level decision:
repeat signal keeps the observable alive; collapse closes it as unstable. This
is not a table-filling ablation and does not release a sweep.

## Bounded Question

Does the mid-frequency same-noise residual signal survive one seed/noise-pairing
repeat when the checkpoint, split, timestep, band-pass mask, scorer, and packet
size are held fixed?

## Hypothesis

If the observed signal is tied to member/nonmember residual behavior rather
than one favorable noise pairing, then a second fixed-seed packet should retain
positive AUC and at least one zero-FP member recovery under the same scorer.

## Falsifier

Close or hold the line if the stability packet meets either condition:

- `AUC < 0.60`
- `TPR@1%FPR = 0` and `TPR@0.1%FPR = 0`

Keep the line candidate-only, without admission, only if both conditions hold:

- `AUC >= 0.65`
- at least one strict-tail member recovery at zero false positives

Borderline results between those gates should stop the GPU line and move the
observable to hold unless a genuinely new scorer or comparator hypothesis is
defined.

## Fixed Contract

| Field | Value |
| --- | --- |
| Command | `run-midfreq-residual-sign-check` |
| Target | collaborator ReDiffuse/DDIM CIFAR10 750k checkpoint |
| Split | `CIFAR10_train_ratio0.5.npz` |
| Split SHA-256 | `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0` |
| Sample count | `64` member + `64` nonmember |
| Timestep | `80` |
| Band | `cutoff = 0.25`, `cutoff_high = 0.50` |
| Previous seed | `12` |
| Stability seed | `23` |
| Device | `cuda` |

## Released Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-sign-check `
  --workspace workspaces/black-box/runs/midfreq-residual-stability-seed23-20260512-gpu-64 `
  --sample-count-per-split 64 `
  --batch-size 8 `
  --seed 23 `
  --timestep 80 `
  --device cuda
```

This releases exactly one GPU packet. Do not run a timestep sweep, seed sweep,
larger packet, 800k checkpoint replay, or band search from this decision.

## Metrics To Record

- `AUC`
- `ASR`
- `TPR@1%FPR`
- `TPR@0.1%FPR`
- member/nonmember distance means
- finite-tail denominators
- elapsed/runtime metadata if emitted

With `64` nonmembers, the low-FPR fields remain finite strict-tail summaries,
not calibrated continuous sub-percent FPR claims.

## Prior Evidence

- [midfreq-residual-signcheck-20260512.md](midfreq-residual-signcheck-20260512.md)
- [midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md)
- [midfreq-residual-scorer-contract-20260512.md](midfreq-residual-scorer-contract-20260512.md)
- [midfreq-residual-collector-contract-20260512.md](midfreq-residual-collector-contract-20260512.md)

## Boundary

No admitted result changes. No Platform/Runtime schema changes. This probe can
only decide whether the mid-frequency residual line remains an internal
candidate or moves to hold/closed.
