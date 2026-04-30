# Black-Box Next-Lane Selection

This note records the CPU-only reselection after the H2 cross-asset preflight.

## Verdict

```text
select CLiD local bridge as the next black-box lane
```

Why:

- H2 is positive-but-bounded on DDPM/CIFAR10, but SD/CelebA text-to-image is
  protocol-incompatible with H2 response-strength.
- `recon` is already the admitted black-box evidence line; running more recon
  first would mostly strengthen an existing lane.
- `variation` remains blocked because the real query-image set and endpoint are
  not present.
- `CLiD` is protocol-compatible with prompt-conditioned SD/CelebA black-box
  surfaces and local asset probes are ready.

## CPU Probe Summary

| Lane | Probe result | Decision |
| --- | --- | --- |
| H2 cross-asset | assets ready, text-to-image protocol blocked | hold unless image-to-image or unconditional-state contract exists |
| CLiD | local config ready; upstream workspace dry-run ready | select next |
| recon | local config ready | keep as admitted baseline, not next exploratory slot |
| variation | blocked; missing query-image set and real endpoint | hold |

## CLiD Bridge Preflight

The first local bridge preparation completed:

| Field | Result |
| --- | --- |
| Run | `clid-local-bridge-preflight-20260501-r1` |
| Mode | paper-alignment local bridge |
| Member export | 8 images + metadata rows |
| Nonmember export | 8 images + metadata rows |
| Localized script | generated from upstream `mia_CLiD_clip.py` |
| Verdict | prepared, not benchmark evidence |

The generated run payload is ignored under `workspaces/black-box/runs/`. The
committed result is only the lane decision and next contract.

## Next Contract

The next CLiD task should be CPU-first:

1. Freeze the local bridge artifact schema: config, exported dataset metadata,
   localized upstream script, and score output locations.
2. Run only a tiny paper-alignment bridge or artifact summary first.
3. Do not run a large GPU CLiD packet until the bridge emits a stable, portable
   summary schema and a low-FPR gate.

## Boundary

This selection does not change admitted evidence. It only chooses the next
bounded black-box research lane.
