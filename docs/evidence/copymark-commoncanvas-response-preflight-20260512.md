# CopyMark CommonCanvas Response Preflight

> Date: 2026-05-12
> Status: responses ready / first simple scorer weak / not admitted

## Question

Can the fixed CopyMark/CommonCanvas `50/50` query split advance to
deterministic response generation on the local GPU, and does the first simple
distance scorer show useful second-asset transfer?

## Taste Check

This preflight is a stop/go check, not environment building. The goal is to
separate real response-generation blockers from avoidable environment excuses.
The original stop condition was simple: if deterministic CommonCanvas
responses could not be generated, the package would stay blocked; if responses
were generated, run the shortest scorer that can change the decision. Do not
expand into a metric matrix unless the first result justifies a sharper
hypothesis.

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

At the 2026-05-12 preflight, the query package existed under
`<DIFFAUDIT_ROOT>/Download` and the package probe reached the response-missing
gate with `endpoint_mode = text_to_image`. The package-gate failures were
`response_member_count` and `response_nonmember_count`, so the blocker was
response generation, not query split construction or CUDA absence.

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

2026-05-13 completion:

```text
checkpoint = commoncanvas_xl_c.safetensors
checkpoint_size = 6,938,040,286 bytes
cuda_env = diffaudit-research
torch = 2.5.1+cu121
device = NVIDIA GeForce RTX 4070 Laptop GPU
smoke = 1 member + 1 nonmember generated successfully
full_responses = 50 member + 50 nonmember ready
endpoint_mode = text_to_image
generation = 512x512, steps=20, guidance_scale=7.5, fixed seed base 20260513
package_probe = ready
missing = []
```

First simple scorer:

```text
score_name = negative_pixel_mse_resized_512
direction = higher_is_more_member
AUC = 0.5736
ASR = 0.6000
TPR@1%FPR = 0.04
TPR@0.1%FPR = 0.04
verdict = negative_or_weak
```

Artifacts:

```text
workspaces/black-box/artifacts/copymark-commoncanvas-response-contract-probe-20260513.json
workspaces/black-box/artifacts/copymark-commoncanvas-simple-distance-20260513.json
```

## Verdict

`ready but weak / not admitted`.

This P0 did what it was supposed to do: it moved the project from "second
response contract missing" to a real transfer check on a second asset. The
result does not support promoting simple pixel distance on SDXL-class
CommonCanvas responses. It also does not justify a CLIP/pixel/LPIPS ablation
matrix just to complete a table.

Next work should be selected only if it has a sharper mechanism hypothesis that
can plausibly change the portability decision.

## Platform and Runtime Impact

None. This is Research-side response-generation readiness only.
