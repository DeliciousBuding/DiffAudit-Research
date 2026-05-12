# Mid-Frequency Residual Comparator Audit

## Verdict

`candidate-boundary-narrowed; mid-frequency-specific claim not supported`

The same-noise residual observable remains candidate-only, but the current
evidence does not support a strong mid-frequency-specific claim. A CPU-only
rescore of the two cached `64/64` packets shows that low-frequency and
full-band residual comparators are at least as strong as the frozen mid-band
score on AUC.

## Question

Does the frozen `0.25-0.50` mid-frequency band add distinct value over simpler
same-noise residual comparators on the same cached packets?

## Assets

This audit reuses ignored local cache artifacts only:

- `workspaces/black-box/runs/midfreq-residual-signcheck-20260512-gpu-64/residual-cache.npz`
- `workspaces/black-box/runs/midfreq-residual-stability-seed23-20260512-gpu-64/residual-cache.npz`

No model execution, GPU task, new dataset, or raw cache file is added to Git.

## Method

The audit recomputes residual distances from the same cached `x_t` and
`tilde_x_t` arrays with fixed FFT masks:

- `full`: all frequencies
- `low_0_25`: lowpass `radius <= 0.25`
- `mid_0_25_0_50`: bandpass `0.25 < radius <= 0.50`
- `high_gt_0_50`: highpass `radius > 0.50`

Scores keep the original orientation: lower residual distance is more
member-like, so `score = -distance`.

## Results

| Packet | Comparator | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Member distance mean | Nonmember distance mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| seed12 | full | `0.731934` | `0.718750` | `0.062500` | `0.062500` | `0.058557` | `0.070739` |
| seed12 | low_0_25 | `0.750977` | `0.718750` | `0.062500` | `0.062500` | `0.035605` | `0.043077` |
| seed12 | mid_0_25_0_50 | `0.733398` | `0.710938` | `0.062500` | `0.062500` | `0.036908` | `0.045728` |
| seed12 | high_gt_0_50 | `0.612305` | `0.640625` | `0.046875` | `0.046875` | `0.027801` | `0.031635` |
| seed23 | full | `0.728516` | `0.718750` | `0.046875` | `0.046875` | `0.058441` | `0.070758` |
| seed23 | low_0_25 | `0.756104` | `0.726562` | `0.031250` | `0.031250` | `0.035297` | `0.043402` |
| seed23 | mid_0_25_0_50 | `0.719238` | `0.687500` | `0.046875` | `0.046875` | `0.037066` | `0.045523` |
| seed23 | high_gt_0_50 | `0.617920` | `0.640625` | `0.031250` | `0.031250` | `0.027621` | `0.031530` |

The low-FPR fields are finite packet counts over `64` nonmembers, not
calibrated continuous sub-percent FPR estimates.

## Interpretation

The result falsifies the narrow claim that the current signal is specifically
mid-frequency-dominant. On both seeds, `low_0_25` has higher AUC than
`mid_0_25_0_50`; `full` is close to `mid` and has matching strict-tail values.
High-frequency residuals are weaker but still nonzero.

The defensible claim is therefore narrower:

- `same-noise residual distance` is a candidate observable on this
  DDPM/CIFAR10 collaborator checkpoint.
- The frozen mid-band score is one viable comparator, not the uniquely best or
  mechanism-defining comparator.
- Further same-contract GPU packets would not change the current boundary.

## Boundary

- Do not call this an admitted attack.
- Do not phrase the innovation as a proven mid-frequency-specific mechanism.
- Do not run seed, timestep, band, or larger-packet sweeps from this audit.
- Reopen only if there is a new protocol-level comparator, a second asset, or
  a product-consumable evidence question.

## Next Action

Run post-midfreq next-lane reselection. The next useful question should not be
another DDPM/CIFAR10 residual packet unless it introduces a new comparator or
cross-asset protocol that can change the research boundary.
