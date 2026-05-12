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

2026-05-13 single sharper scorer:

The only approved follow-up hypothesis was that pixel MSE might be too strict
for text-to-image copying, while CLIP image embedding similarity might recover
semantic or structural copying. This was tested as one pre-selected scorer, not
a CLIP/pixel/LPIPS metric matrix.

```text
score_name = clip_vit_l14_query_response_cosine
direction = higher_is_more_member
AUC = 0.4588
ASR = 0.5300
TPR@1%FPR = 0.0
TPR@0.1%FPR = 0.0
member_score_mean = 0.705783
nonmember_score_mean = 0.719170
verdict = negative_or_weak
```

Artifact:

```text
workspaces/black-box/artifacts/copymark-commoncanvas-clip-image-similarity-20260513.json
```

2026-05-13 prompt-response consistency scorer:

After closing response-vs-query image similarity, one distinct mechanism
remained: the text-to-image model might follow member CommonCatalog captions
more consistently than COCO holdout captions. This was tested as one
pre-selected CLIP text-image scorer on the generated responses.

```text
score_name = clip_vit_l14_prompt_response_cosine
direction = higher_is_more_member
AUC = 0.4408
ASR = 0.5100
TPR@1%FPR = 0.02
TPR@0.1%FPR = 0.02
member_score_mean = 0.258505
nonmember_score_mean = 0.266125
verdict = negative_or_weak
```

Artifact:

```text
workspaces/black-box/artifacts/copymark-commoncanvas-prompt-response-consistency-20260513.json
```

2026-05-13 multi-seed response-distribution stability scout:

One final bounded mechanism check asked whether member prompts produce a more
stable response distribution across fixed seeds. This is not query-response
similarity or prompt adherence: it scores only pairwise similarity among
generated responses for the same prompt.

```text
subset = 4 member + 4 nonmember
seeds = 20260613, 20260614
score_name = clip_vit_l14_response_seed_stability_cosine
direction = higher_is_more_member
AUC = 0.5625
ASR = 0.625
TPR@1%FPR = 0.25
TPR@0.1%FPR = 0.25
member_score_mean = 0.843675
nonmember_score_mean = 0.832792
verdict = negative_or_weak
```

Artifact:

```text
workspaces/black-box/artifacts/copymark-commoncanvas-multiseed-stability-20260513.json
```

## Verdict

`ready but weak / not admitted / CommonCanvas closed by default`.

This P0 did what it was supposed to do: it moved the project from "second
response contract missing" to a real transfer check on a second asset. The
result does not support promoting simple pixel distance on SDXL-class
CommonCanvas responses. The one sharper CLIP image-similarity check also fails,
the distinct prompt-response consistency check fails as well, and the bounded
multi-seed response-stability scout is weak. CommonCanvas should now be closed
by default rather than expanded into a similarity, prompt-adherence, seed,
subset, or embedding-metric ablation matrix.

Next work should require a genuinely new mechanism or a new asset. Do not keep
mining the same CommonCanvas `50/50` response packet with adjacent CLIP scores
or multi-seed stability repeats.

## Platform and Runtime Impact

None. This is Research-side response-generation readiness only.
