# E2Q-013 R125 DreamBooth Public-Surface Follow-Up

> Date: 2026-06-08
> Mode: GitHub metadata/tree/raw notebook inspection; no clone, no model/image download, no execution
> Decision: course-notebook / private-target support only; not a second public score/response asset; no compute release

## Scope

This follow-up rechecks the current public surface for:

`ronketer/diffusion-membership-inference`

The row was already covered by the R125 DreamBooth forensics asset verdict:
[`../../evidence/ronketer-dreambooth-asset-verdict-20260514.md`](../../evidence/ronketer-dreambooth-asset-verdict-20260514.md).
This current-date pass is narrower. It asks whether the repository changed
after that verdict in a way that would make `E2Q-013` packageable for N50,
second-asset, C14, or admitted-evidence use.

No repository clone, Stable Diffusion weight, LoRA/checkpoint artifact, Google
Drive artifact, report PDF body, image payload, notebook execution, GPU, or DCU
job was used. The pass reads only GitHub metadata, tree paths, README text, and
notebook JSON structure.

Sources checked:

- `https://github.com/ronketer/diffusion-membership-inference`
- `https://raw.githubusercontent.com/ronketer/diffusion-membership-inference/main/README.md`
- `https://raw.githubusercontent.com/ronketer/diffusion-membership-inference/main/IMPR_Ex5_Diffusion_Models_2025_2026%20(8).ipynb`
- `https://raw.githubusercontent.com/ronketer/diffusion-membership-inference/main/ex5.ipynb`

## Current Public Surface

GitHub currently reports:

| Field | Current observation |
| --- | --- |
| repository | `ronketer/diffusion-membership-inference` |
| default branch | `main` |
| HEAD | `eb2df6fdfaddeefbabdd1dc1f04b9dee32174ed4` |
| latest commit date | `2026-04-14T16:20:26Z` |
| latest commit message | `Update and organize README` / `Removed author section from README.` |
| recursive tree | `39` entries, `truncated=false` |
| README raw length | `2,995` characters |
| README SHA-256 | `2dedb244cef2b9f9099212f8a903960f2eef8f2679ae7d8a70df4fe589941b72` |

The current tree contains notebooks, report media, a report PDF, a placeholder
`main.py`, and packaging files. The artifact-shaped paths include:

| Path | Current observation |
| --- | --- |
| `IMPR_Ex5_Diffusion_Models_2025_2026 (8).ipynb` | small notebook, `29,627` bytes; `18` cells, `0` outputs, `0` execution counts |
| `ex5.ipynb` | large notebook, `10,863,752` bytes; SHA-256 `b264836f3d842891689469edcfdcc692156b32a5f056d61a00114643861bb018`; `21` cells, `57` outputs, `6` execution counts, `17` image outputs |
| `reports/images/forensics_scores_plot.png` | report image, not a machine-readable score manifest |
| `reports/images/dataset_good_*.jpg`, `reports/images/dataset_bad_*.jpg` | report media only; not a labeled query/score manifest |
| `reports/report.pdf` | report artifact; not inspected as a scoring packet in this pass |

README still describes a Colab/GPU exploratory pipeline for Stable Diffusion
v1.5 DreamBooth + LoRA, SDEdit, and reconstruction-MSE forensics. The setup
requires Hugging Face access to `runwayml/stable-diffusion-v1-5` and notebook
execution in Google Colab. The reported threshold remains approximately
`0.085`, with training MSE approximately `0.07` and unseen MSE approximately
`0.11`.

The large notebook still depends on private runtime paths for the effective
forensics target:

- `base_path = "/content/gdrive/MyDrive/IMPR_Ex5/ex5_forensics_supplementary"`
- `forensics_model_path = f"{base_path}/checkpoint-1500"`
- image inputs are loaded from the same Google Drive directory

The notebook contains six embedded reconstruction-loss scalars:

| Image key | Embedded scalar |
| --- | ---: |
| `e.png` | `0.06714` |
| `b.png` | `0.06812` |
| `f.png` | `0.07269` |
| `a.png` | `0.09753` |
| `d.png` | `0.10400` |
| `c.png` | `0.11230` |

These values are public notebook outputs, but they are not a reusable
DiffAudit packet. The corresponding target LoRA/checkpoint, exact training
member list, exact nonmember list, query image package tied to labels,
row-level score table, metric JSON/ROC artifact, and no-training verifier are
not committed.

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | The target is SD1.5 plus a private Google Drive LoRA/checkpoint at `checkpoint-1500`; no hashable public target artifact is committed. | `Fail` |
| Split semantics | The notebook/report imply training and unseen examples, but there is no exact machine-readable member/nonmember manifest tied to the six scored rows. | `Fail` |
| Score/response coverage | Six scalar reconstruction losses are embedded in a notebook output, but no public query image package, label join, score JSON/CSV, generated-response packet, or row-bound manifest is committed. | `Partial` |
| Metric provenance | The reconstruction-MSE code path is visible, but metric replay depends on private GDrive artifacts and Colab execution state. | `Partial` |
| Semantic boundary | DreamBooth/LoRA reconstruction forensics is membership-relevant, but it is a small course-notebook example rather than a public benchmark packet. | `Partial` |
| Consumer/delta boundary | No external audit packet, surface-delta control, or no-training verifier is available. | `Fail` |

## Decision

`course-notebook / private-target support only /
row_bound_score_response_packet_missing / no_compute_release`.

The April 2026 README update does not change the prior R125 verdict. `E2Q-013`
remains useful as a false-promotion pressure point because a weak rule could
over-promote visible notebook outputs and report figures. The evidence
contract still blocks admission because the target LoRA/checkpoint and
forensics query set remain private/runtime-bound, and the six scalar losses are
not a row-bound public score packet.

Do not count `E2Q-013` as a second public response/score asset, N50 denominator
row, admitted evidence, C14 false-promotion row, reviewer-reliability evidence,
prevalence evidence, or compute-release target.

Reopen only if a public-safe artifact appears with:

- a hashable LoRA or fine-tuned Stable Diffusion checkpoint;
- exact per-sample member and nonmember manifests;
- the corresponding query images or generated response package tied to labels;
- public score/metric JSON, ROC artifact, or row-bound score table; and
- a no-training verifier command over the published artifacts.
