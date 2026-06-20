# E2SCT-029 MIA_SD Public Surface Check

> Date: 2026-06-08
> Mode: no-download GitHub metadata, small text/PGF reads, and static pickle-opcode inspection
> Decision: C14-v2 candidate only; not admitted evidence, not external denominator, no compute release

## Scope

`osquera/MIA_SD` surfaced during a fresh public-asset scout for diffusion
membership-inference evidence with public score or response artifacts. This
check asks whether the repository supplies a row-bound public evidence packet
that could strengthen the current Direction A paper beyond the existing C14
false-promotion baseline.

The check reads repository metadata, README text, tree paths/sizes/blob SHAs,
one CSV header/sample, one PGF ROC text file, and two small public pickle files
with `pickletools` opcode/string inspection only. It does not clone the
repository, unpickle payloads, download images, run notebooks, run model code,
download checkpoints, or use GPU/DCU compute.

## Public Surface

Repository metadata observed through GitHub:

- repo: `https://github.com/osquera/MIA_SD`
- description: `Codebase for the bachelor thesis: Membership Inference Attacks for generative models.`
- default branch: `main`
- latest pushed timestamp observed by GitHub metadata: `2024-06-12T11:15:26Z`
- latest updated timestamp observed by GitHub metadata: `2025-02-18T11:06:49Z`

The root README is explicit about a key blocker: the scripts can run only if
the missing images are supplied by the user. Its usage note says the images used
in the experiments are not published and would need to be added for the script
to run.

The target-model README says the target is Stable Diffusion 1.5 fine-tuned on
image-text pairs, with BLIP auto-labeling, local image directories, A100
fine-tuning, and inference over `100` seeds with `25` images each. It does not
publish an immutable target checkpoint, training image manifest, generated-image
packet, or member/nonmember row identity manifest.

## Evidence Observed

| Surface | Observation | Boundary |
| --- | --- | --- |
| Root README | Git blob SHA `bd804c4bd2a6b09c93f381992d7e47cade9b7bd3`; says experiment images are not published. | Strong public-code warning: the input evidence needed to replay target/split rows is missing. |
| `target_model/README.md` | Git blob SHA `ea55243375d7d6aab52c30a3cf221e9dee264113`; describes SD1.5 fine-tuning on local image-text data and inference output generation. | Target training and inference are described, but not packaged as immutable public row artifacts. |
| `experiment.py` | Git blob SHA `ae91b7180d8ffb11834bfcb1df71b78b97d30fb8`; static read found ROC/AUC computation, result pickle writing, and CLIP-result pickle writing. | Metric code is visible, but it consumes local image folders and writes pickle products. |
| Public result files | Recursive tree exposes `44` public `.pkl` files totaling about `6.06` MB, including many `results.pkl` and `CLIP_results.pkl`; it also exposes `400` `.pgf` files totaling about `8.69` MB and `3` `.npy` files totaling about `40.16` MB. | Public result-like artifacts exist, but row IDs and original images are not public. |
| `images_attack_model/DTU_vs_AAU_unseen_test/results.pkl` | Git blob SHA `56bcc1eae522f7df4cb0523bb93cac7e22fe60bc`, size `172,064` bytes; static pickle-opcode inspection found keys `roc_auc`, `tpr`, `fpr`, `thresholds`, `y_pred`, `y_true`, and `cm`; raw SHA-256 `92fcd4ca835d23426d896f31a3ce0331599ac1441d0754d13018b30de56a2c99`. | The pickle appears to contain labels/predictions and ROC arrays, but it is not safe to unpickle in the release path and it does not expose image row IDs. |
| `images_attack_model/DTU_vs_AAU_unseen_test/CLIP_results.pkl` | Git blob SHA `a6df42a379384504b5e0ffe71b2efbe6c3d1137f`, size `41,629` bytes; static pickle-opcode inspection found keys `roc_auc`, `tpr`, `fpr`, `thresholds`, `y_pred`, `y_true`, and `cm`; raw SHA-256 `3e14556f5659eb75b5876603d52fbf554ce925f1b5e485f39bbb4fdf28e6c808`. | Same: a public score/label surface exists, but without row identity, safe verifier format, or public input rows. |
| `images_attack_model/DTU_vs_AAU_unseen_test/roc_auc.pgf` | Git blob SHA `90860b43855ad52d87285aba6b2edb2edc78de56`, size `36,464` bytes; text contains `Mean ROC AUC = 0.86 \pm 0.02`; raw text SHA-256 `62be6ae495bfed8204a6fbc5feadb2f59eb81249068a64319681c07b665819f2`. | Paper-figure-style metric evidence is public, but not a row-bound verifier packet. |
| `dtu-400-target-loss.csv` | Git blob SHA `54dde32938040de2128dbf2f48854810d3a132f4`, size `739,016` bytes; first columns are W&B-style `Step`, `train_loss`, `train_loss__MIN`, `train_loss__MAX`; `10,001` text lines. | Training-loss log surface only; not a member/nonmember row packet. |

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | Stable Diffusion 1.5 and fine-tuning procedure are described, but no immutable public fine-tuned checkpoint identity is packaged. | `Partial` |
| Split semantics | Public pickle keys include `y_true`, but the image rows, member/nonmember file names, and training images are not published. | `Fail` |
| Score/response coverage | Public result pickles appear to contain `y_pred`/`y_true` and ROC arrays; PGF exposes a mean ROC AUC. | `Partial` |
| Metric provenance | `experiment.py` shows ROC/AUC computation and pickle emission; no safe JSON/CSV verifier or row manifest is published. | `Partial` |
| Semantic boundary | The repository is directly about membership inference against Stable Diffusion/generative models. | `Pass` |
| Provenance/consumer boundary | Public result artifacts are not enough for a downstream audit claim because original images and row identities are absent and pickle is not a safe verifier format. | `Fail` |

## Decision

`osquera/MIA_SD` is a stronger public-result-surface candidate than a code-only
repository: it exposes result pickles with label/prediction/ROC keys and PGF
metric figures. That makes it useful as a future false-promotion pressure row:
weak rules could over-promote it because scores and ROC figures are public.

It is not admitted evidence and not an external denominator row in the current
paper. The blocker is not compute. The blocker is public evidence contract
failure: experiment images are explicitly unpublished, row identities are not
bound to public files, the target checkpoint is not immutable/public, and the
score arrays are in unsafe pickle payloads rather than a row-bound verifier
format.

Allowed wording: `MIA_SD is a C14-v2 candidate public-result-surface row: public
score/ROC artifacts exist, but missing public row identities, unpublished input
images, and non-verifier pickle format block downstream audit admission.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 `13`-row baseline member;
- N50 external denominator row;
- not a second public response/score asset;
- compute-release target;
- proof that the underlying thesis result is wrong.

## Next Action

Do not update the current main paper's C14 selected-row count or review bundle
from this check alone. If expanding C14 after the current paper snapshot, add
`E2SCT-029` to a C14-v2 candidate queue, build a reviewer-safe row packet that
does not expose pickle internals as executable evidence, and regenerate the
review bundle only after at least one additional clean row is selected.
