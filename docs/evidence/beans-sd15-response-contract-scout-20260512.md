# Beans SD1.5 Response-Contract Scout

> Date: 2026-05-12
> Status: feasible candidate; no GPU release

## Question

After the Pokemon/Kandinsky skeleton proved empty, is there a more realistic
second response-contract package we can build locally without mixing asset
identities?

The goal is not to run another model benchmark. The goal is to decide the next
asset acquisition target.

## Candidate

- Query dataset: Hugging Face `AI-Lab-Makerere/beans`
- Member source: `train`
- Nonmember source: `validation` or `test`
- Response model: local `../Download/shared/weights/stable-diffusion-v1-5`
- Endpoint mode: image-to-image
- Minimum package target: `25` member query images, `25` nonmember query
  images, and one controlled response per query

This is a second query dataset, not a second generator family. It is therefore
a practical portability scout, not a full replacement for a future second-model
contract.

## CPU Checks

Dataset readability:

```powershell
python -X utf8 -c "from datasets import load_dataset; ds=load_dataset('AI-Lab-Makerere/beans', split='train[:3]'); print(ds[0]['image'].size, ds[0]['labels'], ds[0]['image_file_path'])"
```

Result:

```text
(500, 500) 0 .../train/angular_leaf_spot/angular_leaf_spot_train.0.jpg
```

Local SD1.5 image-to-image load:

```powershell
python -X utf8 -c "from diffusers import StableDiffusionImg2ImgPipeline; p=StableDiffusionImg2ImgPipeline.from_pretrained('../Download/shared/weights/stable-diffusion-v1-5', local_files_only=True); print(type(p).__name__)"
```

Result:

```text
StableDiffusionImg2ImgPipeline
```

One-image CPU response smoke used a `256 x 256` beans image, local SD1.5
image-to-image, `num_inference_steps = 2`, `strength = 0.25`,
`guidance_scale = 1.0`, fixed seed `20260512`, and disabled safety checker for
the local smoke. It returned a `256 x 256` response image.

## Verdict

`feasible candidate; no GPU release`.

`beans + local SD1.5 image-to-image` is the most practical near-term
response-contract package candidate found so far:

- It has enough real query images for a `25 / 25` member/nonmember split.
- It can use a local response model that already loads offline.
- A single CPU response is slow but feasible, so a small package is realistic.

The tradeoff is scientific scope: it changes the query dataset but not the
generator family. If built, it should be described as a second-query-dataset
portability scout, not a second-model result.

## Decision

Do not keep polishing the empty Pokemon/Kandinsky skeleton as the default near
term path. The next concrete asset task, if we continue response-contract
construction, should be:

1. Create a new package id such as `response-contract-beans-sd15-20260512`.
2. Export `25` train images to `query/member/`.
3. Export `25` validation or test images to `query/nonmember/`.
4. Generate one deterministic local SD1.5 image-to-image response per query.
5. Fill manifest provenance and hashes.
6. Run `probe_response_contract_package.py`; only if it returns `ready`, scope
   a tiny black-box portability test.

No GPU is released by this scout.

## Platform and Runtime Impact

None. This is asset-selection evidence only and does not change admitted rows.
