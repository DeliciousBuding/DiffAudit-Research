# CopyMark CommonCanvas Response Preflight

> Date: 2026-05-12
> Status: needs text-to-image responses / local CUDA exists / no scorer yet

## Question

Can the fixed CopyMark/CommonCanvas `50/50` query split advance to
deterministic response generation on the local GPU?

## Taste Check

This preflight is a stop/go check, not environment building. The goal is to
separate real response-generation blockers from avoidable environment excuses.
If deterministic CommonCanvas responses cannot be generated, the package must
stay `needs_responses`; if the blocker is only the default Python interpreter,
use the CUDA-capable Research environment instead of writing more prose.

## Evidence

Default PATH Python:

```text
torch = 2.11.0+cpu
torch.cuda.is_available() = False
diffusers = installed
transformers = installed
```

CUDA-capable Research environment:

```text
conda run -n diffaudit-research python -X utf8 -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
torch = 2.5.1+cu121
torch.cuda.is_available() = True
device = NVIDIA GeForce RTX 4070 Laptop GPU
```

CommonCanvas model and contract check:

```text
common-canvas/CommonCanvas-XL-C is public and non-gated.
model_index.json class = StableDiffusionXLPipeline.
The model card describes CommonCatalog text captions as input and images as output.
The correct endpoint mode is text_to_image, not image_to_image.
<HF_CACHE> has no complete CommonCanvas/CommonCanvas-XL-C weights cached.
```

The query package itself exists under `<DIFFAUDIT_ROOT>/Download` and the
package probe reaches `needs_responses` with `endpoint_mode = text_to_image`.
The remaining package-gate failures are `response_member_count` and
`response_nonmember_count`, so the blocker is response generation, not query
split construction or CUDA absence.

Minimal download / GPU smoke attempt:

```text
HF_HUB_DISABLE_XET=1 snapshot_download(...)
allow_patterns = diffusers fp16 essentials only
progress reached 4 / 18 files
<HF_CACHE> reached about 0.293 GiB
no response image was generated
```

This proves the download path starts, but the required CommonCanvas fp16
weights were not available locally by the end of the attempt. The smoke was
stopped rather than left as a long-running background process.

## Verdict

`needs deterministic text-to-image responses / no scorer yet`.

The next valuable action is not a scorer and not another validator. It is:

1. Resume or complete the CommonCanvas fp16 weight download using a faster
   path, mirror, or pre-attached cache.
2. Run a minimal CUDA smoke for one member and one nonmember caption using the
   fixed seed policy.
3. If the smoke fits the 8GB RTX 4070 envelope, generate the full `50/50`
   deterministic response packet under the fixed response manifest.
4. If local generation is too slow or memory-bound, generate deterministic
   responses elsewhere and attach them under the fixed
   response manifest.
5. If neither is feasible, mark the CopyMark/CommonCanvas package
   `query-only / blocked` and switch to another second-asset route.

No full dataset download is needed for this blocker. No GPU experiment is
released until the package probe returns `ready`.

## Platform and Runtime Impact

None. This is Research-side response-generation readiness only.
