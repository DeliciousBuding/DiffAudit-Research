# BAF LoRA Parameter-Space Mitigation Gate

> Date: 2026-05-23
> Status: weight-only LoRA mitigation watch / supplementary-code claim only /
> no public score artifacts / no download / no GPU release

## Question

Can arXiv `2605.10439` /
`Filtering Memorization from Parameter-Space in Diffusion Models` become a
bounded DiffAudit execution target, or should it remain a Research-only LoRA
memorization-mitigation watch item?

This was a metadata gate only. I checked public arXiv metadata, the arXiv HTML
page, arXiv source `HEAD`, and GitHub repository/code search results. No arXiv
source tarball, supplementary archive, LoRA weight, image payload, Stable
Diffusion model, checkpoint, generated response, score packet, or repository
payload was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `Filtering Memorization from Parameter-Space in Diffusion Models` |
| arXiv | `2605.10439v1` |
| Published / updated | `2026-05-11T12:09:42Z` |
| Authors | Yu Zhe, Yang Jiayan, Wei Junhao, Yu-Lin Tsai, Wang Chen |
| Primary category | `cs.CV` |
| Mechanism | Base-Anchored Filtering (`BAF`) for post-hoc, training-free, data-free memorization mitigation in diffusion LoRAs |
| Public code signal | arXiv abstract/HTML says code is available in the supplementary material |
| arXiv source `HEAD` | `application/gzip`, `Content-Length = 5,785,836`, SHA-256 ETag `1d10717f5eb4f9ea99d8f36ce0d044e68a937aa88376af20c9d2000a04f6904a` |

## Public Surface Checked

| Source | Finding |
| --- | --- |
| arXiv API | The abstract frames BAF as a LoRA-weight post-processing defense: decompose LoRA updates into spectral channels, retain channels aligned with the pretrained backbone principal subspace, and suppress weakly aligned channels as possible memorization carriers. |
| arXiv HTML | No GitHub URL or external code repository link is visible in the article metadata. The page exposes the normal TeX source link and says the code is in supplementary material. |
| GitHub repository search | Exact-title search, arXiv-id search, `Base-Anchored Filtering` plus diffusion/LoRA/memorization search, and BAF/diffusion/LoRA/memorization search returned no official repository. |
| GitHub code search | Exact-title and arXiv-id searches returned only paper-index / arXiv-tracker style hits or unrelated noise; no official implementation, score file, metric JSON, ROC artifact, or verifier surfaced. |
| Local dedupe | No local evidence note or roadmap entry for arXiv `2605.10439` existed before this gate. The nearest existing LoRA-weight entries are DSiRe / LoRA-WiSE dataset-size recovery, StablePrivateLoRA defense code, and internal Beans member-LoRA weak scouts. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail. The paper concerns released LoRA weights, but no public checkpoint-bound LoRA target package with hashes is visible from the checked public surface. |
| Exact member/nonmember split | Fail. The visible public metadata does not expose training-image identities, member/nonmember query rows, or immutable evaluation splits. |
| Query/response or score coverage | Fail. No generated image packet, per-row memorization score, ROC array, metric JSON, mitigation-decision artifact, or ready verifier is public. |
| Mechanism delta | Pass as a watch item. BAF is a distinct LoRA parameter-space mitigation mechanism, not another denoising-loss, CLIP/pixel, Beans LoRA, CommonCanvas, MIDST, or SecMI repeat. |
| Consumer fit | Fail for current admission. The claim is post-hoc memorization mitigation from LoRA weights, not a current per-sample image/latent-image membership row. It would need a reviewed weight-only LoRA mitigation consumer boundary before Platform/Runtime use. |
| Download justification | Fail. The public metadata is enough to decide this cycle: supplementary/source download would not produce a public row-bound replay artifact without further target/split/score assets. |
| GPU release | Fail. No bounded score packet or verifier exists. |

## Decision

`weight-only LoRA mitigation watch / supplementary-code claim only / no public
score artifacts / no download / no GPU release / no admitted row`.

BAF is worth retaining as LoRA parameter-space memorization-mitigation context
because it targets a real deployment surface: third-party LoRAs distributed
without their training data. It does not release DiffAudit execution work in
the current cycle. The checked public surface has no official repository, no
public target LoRA/checkpoint identities, no training-image manifests, no
member/nonmember rows, no generated response packet, and no score/ROC/metric
artifacts.

Smallest valid reopen condition:

- An official public repository or supplement-visible code release with stable
  paths and license;
- A compact public LoRA target bundle or fixed target hash list;
- Immutable training-image / nonmember or memorized / non-memorized evaluation
  identities;
- Row-bound pre/post-BAF memorization scores, ROC arrays, metric JSON, and
  retained-utility metrics; and
- A no-training verifier that reads those artifacts without downloading Stable
  Diffusion weights, image datasets, or large LoRA corpora.

Stop condition:

- Do not download the `5,785,836` byte arXiv source or supplementary archive in
  this cycle.
- Do not download LoRA weights, Stable Diffusion base weights, training images,
  generated images, or checkpoints.
- Do not implement BAF from the paper, train/fine-tune LoRAs, run mitigation
  sweeps, launch CPU/GPU sidecars, or promote BAF into Platform/Runtime rows
  until public row-bound artifacts and a reviewed weight-only LoRA mitigation
  boundary exist.

## Platform and Runtime Impact

None. BAF remains Research-only weight-space mitigation watch evidence.
Platform and Runtime should continue consuming only the admitted
`recon / PIA baseline / PIA defended / GSA / DPDM W-1` set.
