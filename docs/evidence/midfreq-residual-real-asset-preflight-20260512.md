# Mid-Frequency Residual Real-Asset Preflight

This note records the first real-asset cache preflight for the
mid-frequency same-noise residual line. It is still a tiny cache-contract
check, not a benchmark and not an admitted result.

## Verdict

```text
real-asset-tiny-cache-ready; no GPU release; no admitted evidence
```

## Bounded Question

Can the same cache schema proven by the synthetic runner be written from real
CIFAR10 query images and a real DDPM-style checkpoint, without spending GPU or
changing the scorer contract?

## Hypothesis

If the mid-frequency residual line is ready for a later bounded sign-check,
then a tiny CPU run should load the collaborator 750k checkpoint, load the
matching CIFAR10 ratio0.5 split, collect rank-matched same-noise `x_t` and
`tilde_x_t` states, and write the required cache fields.

## Falsifier

Close or revise the line as `blocked` or `needs-assets` if any of the
following occur:

- the collaborator bundle, checkpoint, split, or CIFAR10 dataset is missing
- the split hash no longer matches the known ratio0.5 CIFAR10 contract
- the model cannot load on CPU
- the cache lacks `x_t`, `tilde_x_t`, labels, timestep, seed, or score fields
- member and nonmember sample counts diverge
- the runner requires GPU for this preflight

## Assets

The run used the existing collaborator ReDiffuse/750k intake assets:

| Asset | Status |
| --- | --- |
| Collaborator DDIM/ReDiffuse bundle | ready |
| DDIM CIFAR-size step-750000 checkpoint | ready |
| CIFAR10 ratio0.5 split | ready; SHA256 `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0` |
| CIFAR10 dataset root | ready |

The checkpoint reports `step = 750000` and exposes `ema_model`. The
collaborator training provenance remains bounded by the existing caveat:
`train1.py` and checkpoint-step metadata are not treated as a paper-faithful
training proof.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-real-asset-preflight `
  --workspace workspaces/black-box/runs/midfreq-real-asset-tiny-20260512-cpu-4 `
  --sample-count-per-split 4 `
  --batch-size 2 `
  --seed 12 `
  --timestep 80
```

The workspace is ignored by Git. The canonical committed evidence is this
note, not the raw `.npz` cache.

## Observed Preflight

| Field | Value |
| --- | --- |
| Status | `ready` |
| Packet | `4` members / `4` nonmembers |
| Device | `cpu` |
| GPU released | `false` |
| Synthetic | `false` |
| Timestep | `80` |
| Seed | `12` |
| Weights key | `ema_model` |
| Checkpoint step | `750000` |

The cache wrote the required fields:

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

Tiny-packet metrics were finite:

| Metric | Value |
| --- | --- |
| AUC | `0.75` |
| ASR | `0.875` |
| TPR@1%FPR | `0.0` |
| TPR@0.1%FPR | `0.0` |
| Member distance mean | `0.037828` |
| Nonmember distance mean | `0.043734` |

These values are not benchmark evidence. With only `4/4` samples, the metrics
only confirm that the real-asset scorer path produces finite, oriented outputs
and that the strict-tail fields remain computable.

## Follow-Up

This preflight cleared the asset/cache schema blocker for the bounded `64/64`
sign-check recorded in
[midfreq-residual-signcheck-20260512.md](midfreq-residual-signcheck-20260512.md).
The preflight itself still does not count as benchmark evidence. A future GPU
run is only justified if a separate stability contract states:

- exact checkpoint and split identity
- fixed timestep and seed policy
- same-noise pairing rule
- primary metrics `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR`
- stop condition: close or hold if the stability result would not change the
  keep/close decision

## Boundary

No admitted result changes. No Platform/Runtime schema changes. Do not cite the
tiny `4/4` values as evidence that the attack works; cite only the readiness of
the real-asset cache contract.
