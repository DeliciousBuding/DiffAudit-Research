# Mid-Frequency Residual Tiny Runner Contract

This note records the first executable cache writer for the mid-frequency
same-noise residual line. It is a synthetic schema preflight, not a model
result.

## Verdict

```text
tiny-runner-schema-ready; real-asset preflight now complete; no GPU release
```

The Research CLI now exposes a CPU-only tiny cache writer:

```powershell
python -X utf8 -m diffaudit run-midfreq-residual-tiny-cache `
  --workspace tmp/midfreq-residual-tiny-cache-smoke `
  --member-count 4 `
  --nonmember-count 4 `
  --batch-size 4 `
  --seed 12 `
  --timestep 80
```

The command writes:

- `summary.json`
- `residual-cache.npz`

The cache contains the required residual fields:

- `labels`
- `member_indices`
- `nonmember_indices`
- `timestep`
- `seed`
- `noise_seed`
- `inputs`
- `x_t`
- `tilde_x_t`
- `bandpass_l2`
- `scores`
- `cutoff`
- `cutoff_high`

## Bounded Question

Can the project write and validate a residual cache with the exact fields
required by the same-noise mid-frequency scorer before spending GPU on a real
DDPM/CIFAR10 packet?

## Hypothesis

If the scorer and collector contract is executable, a tiny runner should write
a self-contained cache and standard summary without relying on H2/H3 response
caches or final response images.

## Falsifier

Close or revise the runner contract if any of the following occur:

- the cache lacks `x_t` or `tilde_x_t`
- labels and state arrays have inconsistent sample counts
- noise provenance is absent
- the summary lacks standard `AUC`, `ASR`, `TPR@1%FPR`, or `TPR@0.1%FPR`
- the runner requires GPU or real assets for the schema preflight

## Observed Preflight

The synthetic `4/4` smoke completed on CPU and produced a valid cache schema.
The metric values are intentionally not interpreted as attack results because
the packet uses synthetic inputs and a synthetic epsilon model.

Observed summary fields:

| Field | Value |
| --- | --- |
| Status | `ready` |
| Verdict | `tiny-runner-schema-ready` |
| Packet | `4` members / `4` nonmembers |
| Device | `cpu` |
| GPU released | `false` |
| Synthetic | `true` |
| Timestep | `80` |
| Seed | `12` |

The synthetic summary reported finite standard metrics and per-sample
`bandpass_l2` values. These numbers are a schema smoke only and must not be
cited as benchmark or candidate evidence.

Current follow-up: the real-asset `4/4` preflight is now recorded in
[midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md).

## Validation

Local validation:

```powershell
python -m unittest tests.test_midfreq_residual
python -X utf8 scripts/run_pr_checks.py
git diff --check
conda run -n diffaudit-research python -X utf8 scripts/run_local_checks.py --fast
```

The unit test covers:

- required `.npz` fields
- shape consistency for `x_t`, `tilde_x_t`, and `bandpass_l2`
- tiny packet cap rejection
- CLI parser support for `run-midfreq-residual-tiny-cache`

## Next Action

The real-asset `4/4` preflight now exists. Do not run `64/64` from this note
alone; the next valid action is a separately frozen sign-check contract that
reuses the same cache schema and records the actual model, split, timestep,
noise provenance, metrics, and stop condition.

## Boundary

No admitted result changes. No Platform/Runtime schema changes. No GPU packet
is released by this contract.
