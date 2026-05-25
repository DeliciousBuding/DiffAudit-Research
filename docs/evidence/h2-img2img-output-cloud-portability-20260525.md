# H2 Img2img Output-Cloud Portability Review

> Date: 2026-05-25
> Status: weak or unstable / not distinct from simple distance / no admitted row / no Runtime runner

## Question

H2 output-cloud geometry is strong on the DDPM/CIFAR10 response-strength
cache. This review asks a narrower portability question: does the same
output-output geometry carry useful signal on the existing SD/CelebA
image-to-image response caches, without using the known stronger
input-to-output simple distance?

This is a CPU-only existing-cache review. It does not generate new responses,
download models, or release GPU work.

## Contract

Script:
`scripts/review_h2_img2img_output_cloud_portability.py`

Output:
`workspaces/black-box/artifacts/h2-img2img-output-cloud-portability-20260525.json`

Inputs:

| Packet | Cache | Samples | Members | Nonmembers | Strength | Repeats |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Admission | `workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1/response-cache.npz` | `50` | `25` | `25` | `0.75` | `2` |
| Stability | `workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1/response-cache.npz` | `20` | `10` | `10` | `0.75` | `2` |

Features use only output-output geometry:

- within-strength repeat-pair RMSE
- response-cloud PCA trace

The raw feature builder also considers duplicate mean/slope/std and PCA
top-share views, but this single-strength packet makes those columns duplicate
or constant. The review script prunes degenerate columns and records the
dropped feature names in the JSON artifact.

The review intentionally excludes input-to-output distance so it cannot
silently become the already-known img2img simple-distance scorer.

## Result

| Packet | Output-cloud logistic AUC | TPR@1%FPR | TPR@0.1%FPR | Best simple-distance AUC | Delta vs simple distance |
| --- | ---: | ---: | ---: | ---: | ---: |
| Admission `25 / 25` | `0.7888` | `0.0` | `0.0` | `0.8768` | `-0.0880` |
| Stability `10 / 10` | `0.9600` | `0.8` | `0.8` | `0.9900` | `-0.0300` |

Decision gate:

| Field | Value |
| --- | ---: |
| `min_auc` | `0.7888` |
| `min_tpr_at_0_1pct_fpr` | `0.0` |
| `max_auc_delta_vs_best_simple_distance` | `-0.0300` |
| `verdict` | `img2img_output_cloud_weak_or_unstable` |

The admission packet is the blocking result: output-cloud AUC stays below
`0.8`, strict-tail recovery is zero, and it is materially weaker than the
existing simple-distance comparator.

## Decision

`weak or unstable / not distinct from simple distance / no admitted row`.

This narrows, rather than expands, H2 output-cloud geometry:

- It remains a strong Research-side candidate on the DDPM/CIFAR10
  response-strength cache.
- It does not port cleanly to the existing SD/CelebA img2img caches.
- It does not justify a Runtime runner, Platform schema, admitted bundle row,
  image-to-image product claim, or same-contract sweep.

Do not expand this into strength, seed, repeat-count, feature-family,
input-distance fusion, or GPU response-generation matrices. Reopen only if a
second public asset, independent consumption contract, or formal mechanism
promotion changes the decision value.

## Platform and Runtime Impact

Expose only a watch-only boundary metadata row. The admitted
Platform/Runtime bundle remains the existing five rows: `recon`,
`PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`.
