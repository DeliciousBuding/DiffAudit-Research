# E2SCT-011 VAE2Diffusion Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for post-C14 false-promotion expansion.

## Question

Does `E2SCT-011` expose public split/checkpoint, score, ROC, metric, response,
feature-cache, or verifier artifacts that can make it an E2 response/score
evidence row?

## Checked Public Surface

No dataset, checkpoint, model weight, generated response, score array, ROC
array, cache payload, or archive was downloaded. The check used public arXiv
metadata, raw README/script text, Git refs, release-page metadata, and blobless
tree metadata only.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/mx-ethan-rao/VAE2Diffusion` |
| GitHub head | `refs/heads/master = d530fbb7e0aca488e63637167b4d64539397bcf7` |
| arXiv | `https://arxiv.org/abs/2511.20592`, v3 updated `2026-03-25`; abstract reports score-based membership inference gains across CIFAR-10, CelebA, ImageNet-1K, Pokemon, MS-COCO, and Flickr. |
| README | States the CVPR 2026 paper and says `Please download all dataset splits and checkpoints [here]().` The bracketed asset link is empty. |
| Releases | `https://github.com/mx-ethan-rao/VAE2Diffusion/releases` returned status `200`, with `0` release tag links and a no-release page phrase. |
| Tree metadata | A blobless no-checkout tree at `d530fbb7e0aca488e63637167b4d64539397bcf7` has `2,045` paths. Excluding vendored `diffusers/`, only `28` project paths remain. |
| Project payload surface | Among the non-vendored project paths, `0` payload-like split/checkpoint/score/ROC/metric/verifier files were visible. The only artifact-hint path was a PDF figure, `figures/auc_distort.pdf`. |
| README commands | README commands contain `/path/to` placeholders for split files, VAE checkpoints, UNet checkpoints, per-dimensional caches, and CUDA execution. |
| Script snippets | `ldm_light/scripts.sh`, `ldm4imagenet/scripts.sh`, and `diffusers/src/mia/scripts.sh` reference author-local data roots, split `.npz` files, checkpoints, pullback/per-dim `.npz` caches, and CUDA runs. |

## Finding

`E2SCT-011` is a useful false-promotion exemplar because the public paper and
repo surface looks strong under shortcut rules: it is code-public, paper-linked,
claims broad score-based membership gains, and README commands visibly mention
splits, checkpoints, metrics/caches, and CUDA evaluation.

The DiffAudit evidence contract still blocks admission:

- the README split/checkpoint link is empty;
- no GitHub release assets are visible;
- the non-vendored project tree has no public split, checkpoint, score, ROC,
  metric, response, feature-cache, or verifier payload;
- scripts point to author-local paths for splits, checkpoints, data roots, and
  pullback/per-dimension caches;
- executing the row would require acquiring data/checkpoints and regenerating
  caches/attacks rather than auditing the published public surface.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Paper and repo identity are public, but no hashable target checkpoint is public and bound to a row packet. |
| Split identity | `Fail` | README and scripts name split files, but no immutable public member/nonmember split manifest is visible. |
| Score or response | `Fail` | No public per-sample scores, responses, generated samples, feature caches, or equivalent row evidence were found. |
| Metric provenance | `Fail` | No public ROC arrays, metric JSON/CSV, or no-training verifier was found. |
| Provenance | `Partial` | GitHub/arXiv metadata are public, but the evidence-bearing assets are absent or local-path products. |
| Consumer/delta | `Fail` | The current public surface supports a false-promotion control, not a consumer-ready membership audit result. |

## Decision

`code_and_empty_asset_link_false_promotion / no_split_checkpoint_score_contract /
no_compute_release`.

Do not count `E2SCT-011` as admitted evidence, a response/score asset, an
external-audit denominator row, or a compute release. Keep it as a
false-promotion exemplar: it shows why paper-linked public code plus visible
split/checkpoint commands cannot substitute for row-bound target, split,
score/response, metric, and verifier artifacts.

Allowed wording:

`VAE2Diffusion exposes a public latent-space MIA code and paper-claim surface,
but the current public repo has an empty split/checkpoint link, no release
assets, no visible row-bound split/checkpoint/score/ROC/metric/verifier packet,
and scripts that rely on local paths; it is a false-promotion baseline control,
not admitted response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `metric_code_split_would_promote`
- `paper_claim_artifact_link_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `artifact_availability_would_promote` unless the empty asset link is
replaced by public split/checkpoint/cache artifacts. Do not tag
`score_only_would_promote` unless public score rows appear.

## Reopen Condition

Reopen only if the authors expose public split manifests, matching target
checkpoints or generated response/feature caches, reusable per-sample scores,
ROC arrays, metric JSON/CSV, and a bounded verifier command that does not train
or fine-tune targets from scratch. Do not download CIFAR-10, CelebA,
ImageNet-1K, Pokemon, COCO, Flickr, LAION, Stable Diffusion weights, VAE/LDM
checkpoints, split payloads, generated responses, or pullback/per-dimensional
caches for this gate. Do not launch GPU/DCU work from this row.
