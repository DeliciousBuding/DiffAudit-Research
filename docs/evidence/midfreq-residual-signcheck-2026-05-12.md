# Mid-Frequency Residual Sign-Check

## Verdict

`candidate-only; bounded signal present; no admitted promotion`

The first frozen `64/64` same-noise residual packet produced a real signal on
the collaborator DDIM/CIFAR10 750k checkpoint, but it is not admitted evidence
and does not change Platform or Runtime schemas. The strict-tail value is a
finite `4/64` empirical recovery at zero false positives, not calibrated
sub-percent FPR evidence.

## Question

Does a fixed mid-frequency same-noise residual score separate members from
nonmembers well enough to keep the observable alive after the CPU cache
preflights?

## Hypothesis

Members should have lower band-pass residual distance between matched
same-noise states:

```text
score = -|| M_mid * (tilde_x_t - x_t) ||_2
```

where `M_mid` is frozen to the annulus defined by `cutoff = 0.25` and
`cutoff_high = 0.50`. No band search, score fusion, or post-hoc threshold
tuning is allowed in this packet.

## Falsifier

Close the line as `negative-but-useful` if the frozen `64/64` packet has
`AUC < 0.6` or no member recovered at zero false positives.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-sign-check `
  --workspace workspaces/black-box/runs/midfreq-residual-signcheck-20260512-gpu-64 `
  --sample-count-per-split 64 `
  --batch-size 8 `
  --seed 12 `
  --timestep 80 `
  --device cuda
```

The workspace path is ignored and contains `summary.json` plus
`residual-cache.npz`. Raw caches and tensors remain local artifacts, not Git
evidence.

## Assets

| Field | Value |
| --- | --- |
| Target family | collaborator ReDiffuse/DDIM CIFAR10 checkpoint |
| Checkpoint | `Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt` |
| Split | `CIFAR10_train_ratio0.5.npz` |
| Split SHA-256 | `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0` |
| Timestep | `80` |
| Seed | `12` |
| Device | `cuda` |

## Metrics

| Metric | Value |
| --- | --- |
| AUC | `0.733398` |
| ASR | `0.710938` |
| TPR@1%FPR | `0.062500` |
| TPR@0.1%FPR | `0.062500` |
| Member distance mean | `0.036908` |
| Nonmember distance mean | `0.045728` |
| Member count | `64` |
| Nonmember count | `64` |

Because there are only `64` nonmembers, both low-FPR fields are finite
strict-tail summaries. `0.0625` means `4/64` members recovered at the zero-FP
threshold under this packet; it must not be worded as calibrated continuous
`0.1%` FPR performance.

## Decision

The observable stays alive as a candidate because the packet clears the
pre-registered sign-check gate: `AUC >= 0.6` and at least one member recovered
at zero false positives. It is still too small and too single-contract to
promote.

Boundary:

- Do not add this to `admitted-results-summary.md`.
- Do not expose it as a Platform or Runtime consumer row.
- Do not run a larger same-contract packet just to improve the table.
- Only spend another GPU slot if a stability question is frozen in advance and
  would decide whether to keep or close the observable.

## Related Evidence

- [midfreq-same-noise-residual-preflight-20260512.md](midfreq-same-noise-residual-preflight-20260512.md)
- [midfreq-residual-scorer-contract-20260512.md](midfreq-residual-scorer-contract-20260512.md)
- [midfreq-residual-collector-contract-20260512.md](midfreq-residual-collector-contract-20260512.md)
- [midfreq-residual-tiny-runner-contract-20260512.md](midfreq-residual-tiny-runner-contract-20260512.md)
- [midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md)

## Next Action

Run a CPU-only stability decision review before any repeat. The review should
ask whether one additional seed or timestep check would change the keep/close
decision. If not, stop the line as candidate-only instead of expanding it into
low-value ablations.
