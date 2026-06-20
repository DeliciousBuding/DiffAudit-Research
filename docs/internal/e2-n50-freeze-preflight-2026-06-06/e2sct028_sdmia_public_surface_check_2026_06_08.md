# E2SCT-028 SD-MIA Public-Surface Check

> Date: 2026-06-08
> Mode: no-download repo/PDF public-surface check
> Decision: support-only code-public pre-training T2I MIA reference; not C14; not admitted; not denominator; no_compute_release

## Scope

This check records the first DiffAudit look at `E2SCT-028` after the public
scout queue was extended with SD-MIA:

`Black-box Membership Inference Attacks on the Pre-training Data of Image-generation Models`
(`CVPR 2026`, repository `wanghl21/SD-MIA`).

The check uses public metadata, `git ls-remote`, `git ls-tree`, raw README /
notebook / script text, and the CVF paper PDF text. It does not download
datasets, generated images, model weights, media payloads, archives, LAION-mi,
FlickrMIA-25, or API outputs. It does not run SD-MIA, image generation,
BLIP/CLIP scoring, API calls, or GPU/DCU jobs.

Sources checked:

- `https://github.com/wanghl21/SD-MIA`
- `https://raw.githubusercontent.com/wanghl21/SD-MIA/main/README.md`
- `https://openaccess.thecvf.com/content/CVPR2026/papers/Qi_Black-box_Membership_Inference_Attacks_on_the_Pre-training_Data_of_Image-generation_CVPR_2026_paper.pdf`
- repository tree at `89384223da4ef95f9bddb3d1e222ccf339b914ac`

GitHub's unauthenticated API was rate-limited during the automatic metadata
refresh. The detailed check therefore uses `git ls-remote`, `git ls-tree`, raw
file URLs, and the GitHub page fallback rather than treating the rate limit as
evidence absence.

## Findings

| Surface | Current finding |
| --- | --- |
| CVF paper | PDF is reachable, title is `Black-box Membership Inference Attacks on the Pre-training Data of Image-generation Models`, 10 pages letter, SHA-256 `f32a651d1e002b6711c9f628486cd57d2bc2cb1d314bc24cd1c49b954a8a311d`. The paper reports LAION-mi and FlickrMIA-25 experiments and says code/datasets are released at the GitHub repository. |
| Git branch | `git ls-remote https://github.com/wanghl21/SD-MIA.git HEAD refs/heads/main` returned `89384223da4ef95f9bddb3d1e222ccf339b914ac`. No tags were listed during the no-download check. |
| Repository tree | `git ls-tree -r --long HEAD` lists README, `process.ipynb`, requirements, figures, `scripts/pipeline.sh`, and `src/*.py`. It does not list committed `data/`, `res/`, row-score CSV/JSON, generated outputs, ROC arrays, metric JSON/CSV, split manifests, or verifier packets. |
| README | README SHA-256 `7a130a91dd03c0ae8207a7d8d854c09061da450f53a8816ab223629c34440b27`. It describes SD-MIA as a fully black-box pre-training-data MIA and gives an input JSON schema with `path`, `caption`, and `label`, but the actual `data/original.json` or row manifest is not committed. |
| Pipeline | `scripts/pipeline.sh` SHA-256 `f1fae4c9e9350b1a343787994efa1b282857d906a63ffa35b8084e238af618b4`. It asks users to replace `<--path-to-your-original-data-->` and three perturbation paths, then writes runtime outputs under `res/${current_time}`. |
| Score pooling | `process.ipynb` SHA-256 `31f37cae5383fbce134d33017fdad81e20bf92b7089c4fd0300baa5f54aed482`. It reads local `res/20251109-161812/disturb_caption_*/embedding/attack_results.json`, pools disturbed scores, and computes AUC/TPR metrics. The referenced `attack_results.json` files are not public tree entries. |
| Runtime products | Source files show that `attack_results.json`, generated images, captions, embeddings, jobs, and metafiles are created under caller-provided output directories. They are not shipped as public row-bound artifacts. |

## Interpretation

SD-MIA is scientifically relevant to DiffAudit because it is a recent
image-generation, pre-training-data, fully black-box MIA with reported LAION-mi
and FlickrMIA-25 experiments. It is a useful related-method and method-watch
surface for Direction A's false-promotion and evidence-contract argument.

It is not currently a CCF-A evidence object for DiffAudit. The public surface is
code-public and paper-result public, but not row-bound:

- no committed member/nonmember row manifest for LAION-mi or FlickrMIA-25;
- no public `original.json`, perturbation JSONs, or compact image-text ID
  manifest in the repository tree;
- no public generated response packet;
- no public `attack_results.json`, per-row pooled score table, ROC arrays, or
  metric JSON/CSV;
- no no-training verifier;
- the pipeline requires local data paths and produces runtime artifacts.

Thus a code-availability or paper-result rule could over-promote SD-MIA, but
DiffAudit's evidence contract blocks admission.

## Decision

`support_only_code_public_pretraining_t2i_mia_reference /
row_bound_score_response_packet_missing / no_compute_release`.

Do not count `E2SCT-028` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, completed external adjudication, reviewer
reliability evidence, or compute release. It also does not change the current
post-C14 expansion queue count of `0`.

Do not download LAION-mi, FlickrMIA-25, generated images, model weights,
archives, media payloads, or API output. Do not run SD-MIA, image generation,
caption perturbation, BLIP/CLIP scoring, closed-source API queries, or GPU/DCU
jobs from this gate.

Reopen only if the authors publish a compact public row-bound package: target
model identity, member/nonmember image-text IDs, generated response or
per-sample score rows, metric provenance, ROC/metric JSON, and a no-training
verifier.
