# Mid-Frequency Residual Collector Contract

This note records the CPU-compatible collector functions for the
mid-frequency same-noise residual line. It is an implementation contract, not a
model result.

## Verdict

```text
collector-function-ready; executable packet runner pending; no GPU release
```

The package now exposes a one-step same-noise state collector in:

```text
src/diffaudit/attacks/midfreq_residual.py
```

The collector generates matched `x_t` and `tilde_x_t` states from a provided
model and dataloader. It keeps the residual at the same diffusion noise level
instead of reusing final response images from H2/H3 caches.

## Frozen Collector Surface

| Function | Role |
| --- | --- |
| `one_step_same_noise_state` | Generate one batch of matched `x_t` and `tilde_x_t` at a fixed timestep. |
| `collect_midfreq_residual_states` | Iterate a dataloader and return inputs plus matched residual states. |
| `summarize_midfreq_packet` | Score an already-collected residual packet with the frozen band-pass L2 scorer. |

The one-step state contract is:

1. Convert `x0` from `[0, 1]` pixels to DDPM `[-1, 1]` space.
2. Sample one reproducible noise tensor.
3. Form `x_t`.
4. Run the model once at the fixed timestep to predict `eps`.
5. Estimate `x0_pred`.
6. Re-noise `x0_pred` with the same noise tensor back to timestep `t`.
7. Return `x_t` and `tilde_x_t` in normalized state space.

## Validation

The unit test now checks:

- scorer distance shape and ordering
- higher-is-member orientation
- metric summary output
- invalid band rejection
- single-class packet rejection
- one-step same-noise state shape and finite values
- deterministic state collection with a synthetic model and dataloader

Command:

```powershell
python -m unittest tests.test_midfreq_residual
```

## Next Action

Add an executable tiny packet runner or CLI entry that writes a residual cache
with:

- `labels`
- `member_indices`
- `nonmember_indices`
- `timestep`
- `seed`
- `inputs`
- `x_t`
- `tilde_x_t`
- `bandpass_l2`
- `summary.json`

The first real run should be capped at `4/4` or `8/8` for runtime validation.
A `64/64` sign-check packet remains blocked until that tiny runner proves the
cache schema on real assets.

## Boundary

No admitted result changes. No Platform/Runtime schema changes. No GPU packet
is released by this contract alone.
