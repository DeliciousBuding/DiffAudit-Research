# CopyMark Provenance Intake

> Date: 2026-05-12
> Status: high-value candidate / manifest inspected / no GPU release

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
- First local action: a shallow repository clone retrieved the root README only.
- Follow-up local action: fetched `diffusers/README.md`, benchmark shell
  scripts, selected training scripts, `copymark/data_utils.py`, Hugging Face
  zip headers, the zip central directory, and representative `caption.json`
  payloads through HTTP range requests.

No large dataset, image payload, or model weights were downloaded. The checked
zip payload size is `5,662,307,542` bytes, so a full download is not justified
until a tiny scoring packet is frozen.

## Evidence

CopyMark is relevant because it was built as a real-world membership/copyright
detection benchmark for diffusion models, not as a generic image dataset. The
paper and released scripts include target settings such as:

- `ldm-celebahq-256`, a latent diffusion model trained on CelebA-HQ.
- `stable-diffusion-v1-5`, checked with LAION-aesthetic versus COCO.
- `CommonCanvas-XL-C`, checked with CommonCatalog versus COCO.

The paper also describes a benchmark protocol with an attack set, a validation
set used for thresholding, and a test set used for final evaluation. That is
closer to the current need than ordinary model cards that only say "trained on
dataset X".

The diffusers reproduction README and shell scripts provide an executable
mapping from models to directory-level member/holdout datasets:

| Model script | Member directory | Holdout directory | Split |
| --- | --- | --- | --- |
| `exp_ldm_*` | `celeba-hq-2-5k-*` | `ffhq-2-5k-*` | `eval` and `test` |
| `exp_sd_*` | `laion-aesthetic-2-5k-*` | `coco2017-val-2-5k-*` | `eval` and `test` |
| `exp_sdxl_*` | `commoncatalog-2-5k-*` | `coco2017-val-2-5k-*` | `eval` and `test` |

The training scripts call `load_dataset(..., member_dataset)` and
`load_dataset(..., holdout_dataset)`, then write separate `member_scores`,
`nonmember_scores`, and image logs. This is a real runnable membership-style
contract, not just a loose dataset name.

The zip central directory was inspected by HTTP range. It contains `25,030`
entries under ten top-level dataset directories:

- `celeba-hq-2-5k-eval`
- `celeba-hq-2-5k-test`
- `coco2017-val-2-5k-eval`
- `coco2017-val-2-5k-test`
- `commoncatalog-2-5k-eval`
- `commoncatalog-2-5k-test`
- `ffhq-2-5k-eval`
- `ffhq-2-5k-test`
- `laion-aesthetic-2-5k-eval`
- `laion-aesthetic-2-5k-test`

The archive has ten `caption.json` files and no central-directory hits for
`metadata`, `member`, `nonmember`, `csv`, `score`, or `prompt`. Representative
`caption.json` entries have only `path`, `height`, `width`, and `caption`.
So the archive does not itself carry per-row provenance labels beyond the
directory-level dataset choice.

## Gate Against Overclaim

CopyMark is still not `ready-to-score` locally, but the blocker is now sharper:
script and manifest shape are understood; what remains is membership provenance
and a tiny asset/scoring packet.

Missing before promotion:

1. Use CommonCanvas/CommonCatalog as the first CopyMark target unless a later
   check contradicts its training provenance. It is more defensible than
   SD1.5/LAION-aesthetic because CommonCanvas was released as an open model
   trained on CommonCatalog-style Creative-Commons data, while SD1.5 membership
   is tied to a much broader LAION training pool.
2. Confirm that the selected member directory is truly part of the target
   model's training or fine-tuning data, not merely a plausible source dataset.
3. Confirm which images are members, which are nonmembers, and which subset is
   validation versus final test.
4. Download only a tiny fixed subset after the selected target passes the
   provenance check.
5. Confirm that a CPU-first scorer can run on that tiny subset before any GPU
   packet is considered.

## Decision

`high-value candidate / manifest inspected / no GPU release`.

CopyMark should remain the next acquisition target. The follow-up inspection
proves that it has a concrete script-level member/holdout contract and a
manageable eval/test layout, but the archive stores those labels at directory
level rather than as per-row provenance metadata. Therefore it still should not
replace the current scope gate as a ready benchmark.

Smallest useful next action:

- Create a tiny CPU-only CommonCanvas/CommonCatalog asset packet from fixed
  `commoncatalog-2-5k-{eval,test}` member images and matching
  `coco2017-val-2-5k-{eval,test}` holdout images. Do not include SD1.5/LAION
  until the CommonCanvas path is blocked or exhausted.

Stop condition:

- If the selected member source cannot be defended as target-model training or
  fine-tuning membership, mark that CopyMark target as
  `candidate-needs-provenance` and switch to the other target instead of
  building tooling around it.

GPU condition:

- No GPU until a tiny fixed subset has proven true membership labels,
  query/response availability, a frozen scorer, metrics, and a stop condition.

## Platform and Runtime Impact

None. This changes Research intake priority only. It does not modify admitted
product rows or Runtime contracts.
