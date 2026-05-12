# Mid-Frequency Residual Scorer Contract

This note records the first implementation step after the same-noise residual
cache audit. It adds a CPU-only scorer utility and tests. It does not collect
model states and does not release GPU.

## Verdict

```text
scorer-contract-ready; collector and synthetic runner now available; no GPU release
```

The Research package now has a reusable scorer for the proposed
mid-frequency same-noise residual observable:

```text
src/diffaudit/attacks/midfreq_residual.py
```

The scorer expects an already-collected residual packet with matched
`x_t` and `tilde_x_t` tensors. It computes band-pass FFT L2 over
`tilde_x_t - x_t`, orients lower residual as more member-like, and reports the
standard four metrics through the shared metrics utilities.

## Frozen Scorer Surface

| Field | Value |
| --- | --- |
| Method id | `mid_frequency_same_noise_residual` |
| Score orientation | `negative_bandpass_l2_higher_is_member` |
| Default band | normalized radial FFT annulus `0.25-0.50` |
| Required arrays | `labels`, `x_t`, `tilde_x_t` |
| Required shape | `[sample, channel, height, width]` for both states |
| Metrics | `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`, score means, distance means |

The first packet must keep the scorer frozen. Do not add SSIM, learned fusion,
or post-hoc band search to the first residual sign check.

## Validation

The dedicated unit test is:

```powershell
python -m unittest tests.test_midfreq_residual
```

It checks per-sample distance shape, score orientation, standard metric
summary output, metadata preservation, and invalid band rejection. The test is
included in `scripts/run_local_checks.py --fast` and the GitHub Actions
`full-checks` job. The required PR `unit-tests` check is now a fast syntax and
documentation gate only.

## Next Action

The collector and synthetic tiny cache writer now exist. The next real-asset
preflight must preserve these fields:

- `labels`
- `x_t`
- `tilde_x_t`
- `timestep`
- noise provenance
- `bandpass_l2`

The first real-asset packet remains capped at `4/4` or `8/8`. A larger packet
or GPU release remains blocked until this schema works on real assets and the
same-cache final-response comparator is frozen.

## Boundary

This is not admitted evidence and not a Platform/Runtime handoff. It is the
minimal scorer contract needed before a real residual packet can be evaluated.
