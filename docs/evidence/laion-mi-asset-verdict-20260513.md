# LAION-mi Asset Verdict

> Date: 2026-05-13
> Status: metadata-ready / response-not-ready / no GPU release

## Taste Check

This is a Lane A asset-acquisition verdict, not a scorer result. The question
is whether LAION-mi can become the next clean second membership asset without
reopening the closed CommonCanvas, MIDST, Beans, MNIST, Fashion-MNIST, or
Kohaku/Danbooru routes.

## What Was Checked

- Dataset: Hugging Face `antoniaaa/laion_mi`.
- Dataset card: `LAION-mi`, MIT license, text-to-image task, membership and
  latent-diffusion tags.
- Dataset files: `README.md` plus one parquet file for `members` and one for
  `nonmembers`.
- Loaded splits through `datasets.load_dataset("antoniaaa/laion_mi")`.
- Paper text: `Towards More Realistic Membership Inference Attacks on Large
  Diffusion Models` (`arXiv:2306.12983`), used only to verify target and split
  semantics.

No model weights, image payloads, or generated responses were downloaded.

## Evidence

The local metadata load returned:

| Split | Rows | Fields |
| --- | ---: | --- |
| `members` | `13,396` | `url`, `caption` |
| `nonmembers` | `26,874` | `url`, `caption` |

The Hugging Face dataset info reports a small metadata-only package:

| Field | Value |
| --- | --- |
| License | `mit` |
| Download size | `5,044,720` bytes |
| Dataset size | `6,588,117` bytes |
| Files | `.gitattributes`, `README.md`, `data/members-...parquet`, `data/nonmembers-...parquet` |

The paper gives a stronger membership story than broad model-card provenance:

- Target model identity is `Stable Diffusion-v1.4`.
- Members are drawn from LAION Aesthetics v2 5+, which the paper states was
  used to train `Stable Diffusion-v1.4`.
- Nonmembers are drawn from LAION-2B Multi Translated, then filtered through a
  deduplication and sanitization pipeline to reduce contamination and
  distribution mismatch.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Pass: `Stable Diffusion-v1.4` is explicitly named by the paper. |
| Exact member/nonmember split | Partial pass: public metadata has split-level rows with URL and caption, but no image payloads. |
| Query/response coverage | Fail: no ready image cache or generated response package exists in the dataset. |
| Mechanism delta | Pass for asset acquisition: this is not another CommonCanvas, Beans, MIDST, MNIST, Fashion-MNIST, final-layer gradient, or midfreq variant. |
| Public-safe documentation | Pass: dataset card is MIT and only public dataset/model identifiers are needed. |

## Decision

`metadata-ready / response-not-ready / no GPU release`.

LAION-mi is the best current Lane A watch candidate because it has a named
target model and an explicit member/nonmember metadata split. It still cannot
be promoted to `next_gpu_candidate` because the released package does not
provide image bytes or responses, only URLs and captions. A GPU packet would be
premature until a tiny fixed subset proves that member and nonmember URLs are
retrievable and that a deterministic response or scoring contract exists.

Smallest useful next action:

- Run a CPU-only URL availability probe on a fixed `25/25` subset of
  `members` and `nonmembers`, recording only counts and failure classes. Do not
  download a large image set and do not invoke `Stable Diffusion-v1.4` until the
  URL probe shows the tiny query set is recoverable.

Stop condition:

- If the fixed `25/25` URL probe cannot recover enough images from both splits
  for a balanced packet, keep LAION-mi as `metadata-only watch` and return to
  Lane A discovery rather than building response-generation tooling.

GPU condition:

- No GPU until a fixed image subset, target identity, query/response plan,
  scorer, metric contract, and stop condition are all frozen.

## Platform and Runtime Impact

None. This is a Research intake verdict only. It does not change admitted
product rows, Runtime schemas, or Platform-facing evidence.
