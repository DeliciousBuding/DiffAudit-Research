# Quantile Regression Asset Verdict

> Date: 2026-05-13
> Status: mechanism-reference / artifact-incomplete / no download / no GPU release

## Taste Check

This is a Lane A clean-asset search verdict after MIAGM stayed
artifact-incomplete. The candidate is not LAION-mi live URLs, Zenodo,
Noise as a Probe, MIAGM, CommonCanvas, MIDST, Beans, MNIST,
Fashion-MNIST, Kohaku/Danbooru, final-layer gradient, or midfreq replay.

The question is whether `Membership Inference Attacks on Diffusion Models via
Quantile Regression` exposes a clean runnable target, split, and scoring
contract for DiffAudit, not whether the paper is methodologically interesting.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `Membership Inference Attacks on Diffusion Models via Quantile Regression` |
| Venue | ICML 2024 / PMLR 235 |
| Primary sources checked | `https://proceedings.mlr.press/v235/tang24g.html`, `https://openreview.net/forum?id=xqqccG7gf1`, PMLR PDF |
| Public code found for this paper | none found in exact-title / OpenReview-ID / arXiv-ID GitHub searches |
| Referenced codebase | `https://github.com/jinhaoduan/SecMI` for target DDPM code and released CIFAR10/CIFAR100 models |
| Attack surface | white-box reconstruction-loss quantile regression with a bag of weak attackers |
| Datasets described | CIFAR-10, CIFAR-100, STL10, Tiny-ImageNet |

No target checkpoints, datasets, split files, or large artifacts were
downloaded. Only public paper pages, the paper PDF text, and public code search
surfaces were inspected.

## What The Candidate Adds

The paper is a useful mechanism reference because it replaces a single global
reconstruction-loss threshold with a sample-conditioned quantile regressor and
aggregates several small attackers. That is distinct from the recently closed
DiffAudit lines: response similarity, conditional denoising loss, final-layer
gradient norm/cosine, generated-distribution MIAGM, live-URL LAION-mi recovery,
and MIDST nearest-neighbor or marginal shadow classifiers.

The asset contract is weaker. The paper describes using the SecMI/Duan et al.
DDPM codebase and released CIFAR10/CIFAR100 target models, then training STL10
and Tiny-ImageNet DDPM targets for 80k steps. It also describes a simple split
rule: half the dataset is private target training data, and the other half is
split into public auxiliary samples and holdout samples. That is not the same
as a released per-sample target manifest for DiffAudit.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial for CIFAR10/CIFAR100 references through SecMI; fail for DiffAudit release because this paper does not publish a self-contained target artifact set. |
| Exact member/nonmember split | Fail: the paper states the split policy, but no per-sample member/public/holdout manifest or deterministic seed contract was found. |
| Query/response coverage | Not applicable for black-box responses and fail for a ready packet: the method needs white-box target access and reconstructed t-error computation. |
| Scoring contract | Partial mechanism pass: quantile-regression scoring is clear at concept level, but no implementation or ready DiffAudit packet was found. |
| Mechanism delta | Pass for watch: sample-conditioned low-FPR reconstruction-loss thresholding is a distinct method family. |
| GPU release | Fail: no exact target split, target artifact bundle, command, metric packet, or stop condition is frozen. |

## Decision

`mechanism-reference / artifact-incomplete / no download / no GPU release`.

Quantile Regression should stay as a Lane B mechanism reference and Lane A
watch candidate, not a `next_gpu_candidate`. It does not justify training STL10
or Tiny-ImageNet DDPMs for 80k steps, reconstructing the paper's split from
scratch, or building a quantile-regression implementation before target
identity and split semantics are released.

Smallest valid reopen condition:

- A public implementation or artifact release for this paper appears; and
- It exposes exact target checkpoints or deterministic target recreation; and
- It exposes per-sample member/public/holdout split semantics; and
- A bounded `25/25` or `50/50` t-error packet can be frozen against the
  existing DiffAudit low-FPR metrics.

Stop condition:

- Do not turn this into a SecMI reproduction or target-training project. If the
  only path is "reuse SecMI, pick our own split, train our own targets", it is
  mechanism background, not a clean external asset.

## Reflection

This cycle tested a non-duplicate mechanism that could matter if artifacts were
available. It changed the roadmap by adding a stronger Lane B reference, but it
did not unlock a runnable asset, so the correct three-slot state remains no GPU
candidate and no CPU sidecar.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, Platform product copy, or the admitted evidence bundle.
