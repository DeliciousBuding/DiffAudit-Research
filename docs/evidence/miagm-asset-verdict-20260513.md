# MIAGM Asset Verdict

> Date: 2026-05-13
> Status: code-reference-only / artifact-incomplete / no download / no GPU release

## Taste Check

This is a Lane A clean-asset search verdict after the consumer-boundary sync.
The candidate is not LAION-mi live URLs, Zenodo, Noise as a Probe,
CommonCanvas, MIDST, Beans, MNIST, Fashion-MNIST, Kohaku/Danbooru,
final-layer gradient, or midfreq replay.

The question is whether `Generated Distributions Are All You Need for
Membership Inference Attacks Against Generative Models` / `MIAGM` provides a
clean runnable benchmark artifact for DiffAudit.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `Generated Distributions Are All You Need for Membership Inference Attacks Against Generative Models` |
| Public code | `https://github.com/minxingzhang/MIAGM` |
| Model families described by repository | DDPM, DDIM, FastDPM |
| Dataset families described by repository | CIFAR-10 and CelebA |
| Attack surface | classifier over generated distributions / black-box-style generated samples |

No dataset payloads, checkpoints, generated distributions, or large artifacts
were downloaded. Only public paper/search metadata and the public repository
README/code surface were inspected.

## What The Candidate Adds

MIAGM is useful as a related black-box reference because it studies membership
inference against generative models from generated distributions and exposes a
public code repository. It is not one of the currently closed DiffAudit
response-distance, denoising-loss, final-layer-gradient, MIDST tabular, or
LAION-mi URL-recovery paths.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Fail for release: public code names model families, but no exact target checkpoint or training run artifact was found. |
| Exact member/nonmember split | Fail: no per-sample target member/nonmember manifest or deterministic split contract was found. |
| Query/response coverage | Fail: no ready generated-distribution payload or response package was found. |
| Scoring contract | Partial pass: code describes an attack implementation surface, but not a ready DiffAudit packet without target artifacts and generated distributions. |
| Mechanism delta | Pass for watch: generated-distribution membership is distinct from the most recently closed candidates. |
| GPU release | Fail: no target identity, split, generated distribution, or stop condition is frozen. |

## Decision

`code-reference-only / artifact-incomplete / no download / no GPU release`.

MIAGM should stay as a related-method watch reference, not a `next_gpu_candidate`.
It does not justify downloading datasets, training DDPM/DDIM/FastDPM models, or
rebuilding generated distributions from scratch inside this ROADMAP cycle.

Smallest valid reopen condition:

- A public artifact release exposes exact target checkpoints or generated
  distributions; and
- The release includes per-sample member/nonmember split semantics or a
  deterministic split recreation policy; and
- A bounded `25/25` or `50/50` generated-distribution scorer can be frozen with
  a clear `AUC < 0.60` or near-zero strict-tail stop condition.

Stop condition:

- Do not turn MIAGM into a long reproduction project. Without target artifacts
  and splits, it remains a reference for mechanism design and literature
  context only.

## Reflection

This cycle tested a non-duplicate public code reference. It did not unlock a
runnable asset contract, so the correct state remains no GPU and no download.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
