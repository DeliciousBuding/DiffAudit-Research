# CopyMark Provenance Intake

> Date: 2026-05-12
> Status: high-value candidate / needs asset manifest check / no GPU release

## Taste Check

This intake answers one route question: is CopyMark worth treating as the next
second membership benchmark candidate?

It does not add a loader, a dataset downloader, a validator, or an experiment.
The goal is to avoid another round of "dataset name equals membership label"
while also not ignoring a benchmark that may directly target the current
blocker.

## What Was Checked

- Paper: `Real-World Benchmarks Make Membership Inference Attacks Fail on
  Diffusion Models` / CopyMark (`arXiv:2410.03640`).
- Code: `https://github.com/caradryanl/CopyMark`.
- Dataset page/API pointer: Hugging Face `CaradryanLiang/copymark`, which was
  observed through the API as public `chumengl/copymark` with a single large
  `datasets.zip` sibling plus README metadata.
- Local action: a shallow repository clone retrieved the root README only. A
  sparse pull of `diffusers/` failed before code download, so this note does
  not claim script-level readiness.

No large dataset or model weights were downloaded.

## Evidence

CopyMark is relevant because it was built as a real-world membership/copyright
detection benchmark for diffusion models, not as a generic image dataset. The
paper names three target settings:

- `ldm-celebahq-256`, a latent diffusion model trained on CelebA-HQ.
- `stable-diffusion-v1-4`, trained on LAION-scale web data.
- `stable-diffusion-xl-base-1.0`, also trained on LAION-scale web data.

The paper also describes a benchmark protocol with an attack set, a validation
set used for thresholding, and a test set used for final evaluation. That is
closer to the current need than ordinary model cards that only say "trained on
dataset X".

The GitHub root README says the repository contains a diffusers benchmark,
raw experimental records, data preparation utilities, and datasets placed under
`diffusers/datasets`. That is promising, but the root README alone does not
prove the exact file schema, split identities, or whether the downloadable
package contains enough prompts/images/responses for immediate local scoring.

## Gate Against Overclaim

CopyMark is not `ready-to-score` yet in this repository.

Missing before promotion:

1. Inspect the dataset archive manifest without downloading the full package,
   or download only if size and contents are explicitly justified.
2. Confirm target-model identity per row.
3. Confirm which images are members, which are nonmembers, and which subset is
   validation versus final test.
4. Confirm whether CopyMark ships responses, prompts, encoded latents, or only
   query images and metadata.
5. Confirm that a CPU-first scorer can run on a tiny fixed subset before any
   GPU packet is considered.

## Decision

`high-value candidate / needs asset manifest check / no GPU release`.

CopyMark should replace random external model-card hunting as the next
acquisition target, because its paper-level goal matches the missing second
membership benchmark. But it should not yet replace the current scope gate as a
ready benchmark.

Smallest useful next action:

- Inspect CopyMark's dataset archive layout and `diffusers/` README/scripts
  enough to decide whether the package contains explicit member/nonmember
  provenance and a reproducible query/response contract.

Stop condition:

- If the archive only contains images without clear membership provenance, or
  if it requires treating LAION membership as a guess, mark CopyMark as
  `candidate-needs-provenance` and do not build tooling around it.

GPU condition:

- No GPU until a tiny fixed subset has proven true membership labels,
  query/response availability, a frozen scorer, metrics, and a stop condition.

## Platform and Runtime Impact

None. This changes Research intake priority only. It does not modify admitted
product rows or Runtime contracts.
