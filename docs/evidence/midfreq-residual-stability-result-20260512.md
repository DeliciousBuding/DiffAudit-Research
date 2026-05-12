# Mid-Frequency Residual Stability Result

## Verdict

`candidate-stable-but-bounded; no admitted promotion; stop same-contract GPU`

The released seed-only stability packet retained the mid-frequency same-noise
residual signal. This keeps the observable alive as an internal candidate, but
it still does not become admitted evidence because both packets are small,
single-asset DDPM/CIFAR10 checks with finite strict-tail denominators.

## Bounded Question

Does the candidate signal survive one seed/noise-pairing repeat when the
checkpoint, split, timestep, band-pass mask, scorer, and packet size are held
fixed?

## Answer

Yes, within the bounded `64/64` contract. The seed-23 repeat passes the frozen
keep gate from
[midfreq-residual-stability-decision-20260512.md](midfreq-residual-stability-decision-20260512.md):
`AUC >= 0.65` and at least one strict-tail member recovery at zero false
positives.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-sign-check `
  --workspace workspaces/black-box/runs/midfreq-residual-stability-seed23-20260512-gpu-64 `
  --sample-count-per-split 64 `
  --batch-size 8 `
  --seed 23 `
  --timestep 80 `
  --device cuda
```

The run workspace is ignored. It contains the local `summary.json` and
`residual-cache.npz`; raw cache payloads are not Git evidence.

## Metrics

| Packet | Seed | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Member distance mean | Nonmember distance mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Initial sign-check | `12` | `0.733398` | `0.710938` | `0.062500` | `0.062500` | `0.036908` | `0.045728` |
| Stability repeat | `23` | `0.719238` | `0.687500` | `0.046875` | `0.046875` | `0.037066` | `0.045523` |

With `64` nonmembers, `0.062500` means `4/64` members recovered at the
zero-FP threshold and `0.046875` means `3/64`. These are finite strict-tail
packet counts, not calibrated continuous sub-percent FPR claims.

## Decision

The seed-only repeat reduces AUC slightly but preserves the same qualitative
separation:

- member mid-band residual distances remain lower than nonmember distances;
- AUC stays above the frozen `0.65` keep gate;
- strict-tail recovery remains nonzero at zero false positives.

Therefore the line remains a `candidate-only` internal Research signal. The
stability result rules out the weakest explanation that the first packet was
only one favorable noise seed. It does not rule out single-asset, checkpoint,
timestep, or scorer-specific effects.

## Boundary

- Do not add this line to `admitted-results-summary.md`.
- Do not expose it as a Platform or Runtime consumer row.
- Do not run larger same-contract packets, seed sweeps, timestep sweeps, band
  searches, or 800k shortcut replays from this result.
- Reopen only with a genuinely new comparator, second asset, or protocol that
  can change the product/research boundary.

## Next Action

Stop same-contract GPU expansion and run a CPU-only post-midfreq lane
reselection. The likely next useful direction is a system-consumable or
cross-asset question rather than another DDPM/CIFAR10 residual packet.
