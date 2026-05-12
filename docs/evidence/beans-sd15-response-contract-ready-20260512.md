# Beans SD1.5 Response-Contract Ready

> Date: 2026-05-12
> Status: ready package; no GPU release

## Question

Can the feasible Beans/SD1.5 candidate become a real response-contract package
that passes the existing CPU gate?

## Package

Local non-Git package roots:

```text
Download/black-box/datasets/response-contract-beans-sd15-20260512/
Download/black-box/supplementary/response-contract-beans-sd15-20260512/
```

Package contents:

- `25` member query images from `AI-Lab-Makerere/beans` train split
- `25` nonmember query images from `AI-Lab-Makerere/beans` validation split
- `25` member response images
- `25` nonmember response images
- `manifest.json`
- `splits/member_ids.json`
- `splits/nonmember_ids.json`
- `endpoint_contract.json`
- `response_manifest.json`

Response policy:

- local `stable-diffusion-v1-5` image-to-image
- `256 x 256` query images
- prompt: `a clear documentary photograph of a bean leaf`
- `num_inference_steps = 2`
- `strength = 0.25`
- `guidance_scale = 1.0`
- deterministic seed policy from seed base `20260512`

## Probe

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-beans-sd15-20260512 `
  --download-root ../Download `
  --output workspaces/black-box/artifacts/beans-sd15-response-contract-probe-20260512.json
```

Tracked artifact:

- `workspaces/black-box/artifacts/beans-sd15-response-contract-probe-20260512.json`

Probe result:

| Field | Value |
| --- | --- |
| status | `ready` |
| member query count | `25` |
| nonmember query count | `25` |
| member response count | `25` |
| nonmember response count | `25` |
| member response coverage | `25 / 25` |
| nonmember response coverage | `25 / 25` |
| missing checks | none |
| endpoint mode | `image_to_image` |
| repeat count | `1` |
| response observability | `image` |

## Verdict

`ready package; no GPU release`.

This is the first local second response-contract package that passes the
existing CPU package gate. It changes the state from `needs-assets` to
`ready-for-bounded-scout-design`.

Scientific boundary:

- This is a second query dataset, not a second generator family.
- It is not admitted evidence.
- It does not by itself show membership signal.
- It only justifies designing a tiny CPU-first black-box portability scorer.

## Next Action

Do not run a large benchmark. The next useful step is a tiny scoring design on
this fixed package, for example:

- one simple image-distance score between query and response,
- one low-cost residual or perceptual-distance variant if available locally,
- report `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR`,
- stop immediately if the result is weak.

No GPU is released until a tiny CPU score changes the direction.

## Platform and Runtime Impact

None. This is Research-side package readiness only.
