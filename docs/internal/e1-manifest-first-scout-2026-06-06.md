# E1 Manifest-First Scout

> Date: 2026-06-06
> Scope: internal second-asset scout for the CCF-A upgrade gate.

## 1. Decision

E1 is not a GPU queue. It is a manifest gate.

CopyMark official score artifacts were the closest historical second-asset
challenger, but the current cycle has now rechecked and rejected that route.
Quantile Diffusion MIA and Tracing the Roots remain useful
support packets, but none of these candidates currently supplies the public
target/split/row/metric surface needed to become a non-adjacent CCF-A attack or
observable result.

2026-06-06 update: the authenticated no-download CopyMark compact-manifest gate
has now been rerun. See
[`e2-n50-freeze-preflight-2026-06-06/e2q006_copymark_compact_manifest_gate_2026_06_06.md`](e2-n50-freeze-preflight-2026-06-06/e2q006_copymark_compact_manifest_gate_2026_06_06.md).
The gate still fails: GitHub `main` remains at
`069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`, code/tree search found no compact
manifest or no-training verifier, and the HF dataset exposes only README plus a
`5,662,307,542` byte `datasets.zip`. CopyMark therefore remains bounded support
/ missing-surface evidence and does not release downloads, GPU, or a second-asset
observable route.

No large download, model training, feature sweep, or GPU job is allowed until a
candidate passes the row-bound manifest preflight below.

2026-06-08 update: a new candidate, NDSS-324 / Zenodo
`10.5281/zenodo.13371475`, is stronger than ordinary code-only rows because the
public archive central directory exposes fine-tuned Stable Diffusion LoRA
checkpoints and member/nonmember dataset PKLs. It still does not pass the
score/response gate: the 21-entry current ZIP central directory has no score
vectors, generated responses, ROC arrays, metric JSON, or verifier, despite the
paper appendix saying score vectors are stored in the artifact package. Treat it
as a compute-gated E1 candidate only. See
[`e1-ndss324-zenodo-manifest-preflight-2026-06-08.md`](e1-ndss324-zenodo-manifest-preflight-2026-06-08.md).

2026-06-08 full-ZIP probe update: the full `736,366,195` byte Zenodo ZIP was
downloaded under `Download/shared/supplementary/`, its MD5 matched Zenodo, and
`zipfile.testzip()` passed. Static inspection of the nested torch dataset
payloads found only `image` and `text` fields and no `id`, `file_name`, or
`image_id` fields. The public split also remains semantically incomplete: the
archive has partial target member/nonmember and shadow nonmember payloads, but
no clean paper-faithful four-quadrant target/shadow member/nonmember manifest.
This confirms the candidate remains compute-gated and does not release GPU.

## 2. Candidate Gate Table

| Candidate | Current fit | Required manifest gate | First blocker | Download allowed | GPU allowed | Allowed wording now | Reopen condition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CopyMark official score artifacts | Best E1 candidate; official score/image-log surface remains artifact-rich but currently fails the compact-manifest gate. | Must bind each row to `dataset_family`, `method`, `target_family`, `image_filename` or immutable public row id, `member/nonmember`, per-row score, score tensor hash, image-log hash, metric JSON hash, target checkpoint/model hash, and dataset packet hash. Must include a no-training verifier that recomputes AUC, ASR, TPR@1%FPR, and TPR@0.1%FPR. | Current authenticated no-download recheck found no compact manifest or verifier; HF exposes only README plus large `datasets.zip`. | Only compact metadata/manifest files. No full HF zip, image directory, SD/LDM/SDXL/CommonCanvas weights, or large repo clone. | No. | `bounded-support` / E2 missing-surface example. | GitHub commit moves beyond `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`, HF dataset SHA changes with manifest-level files, or authors publish a compact row manifest plus verifier. |
| NDSS-324 / Zenodo fine-tuned diffusion artifact | Strongest current E1 compute-gated candidate; official paper, GitHub code, verified Zenodo ZIP, target/shadow LoRA checkpoints, and member/nonmember dataset directories. | Must expose immutable row IDs and labels, complete paper-faithful target/shadow member/nonmember split semantics, row-level score vectors or generated responses, and a verifier for AUC/ASR/TPR plus label-shuffle control. | Full-ZIP static probe found no row-id fields in the nested dataset payloads, no complete four-quadrant split manifest, and no score-vector, ROC, metric JSON, generated-response, or verifier files. | Completed for bounded probe only; do not expand into extraction, training, broad image generation, or score production from the current package. | No. A single smoke can be considered only after a compact row manifest and score-generation or score-vector path exists. | `compute-gated candidate`, not public score replay. | Authors publish a compact row manifest, complete split mapping, or the missing score-vector/metric packet described by the paper appendix. |
| Quantile Diffusion MIA `t_error` packet | E2/Direction A support packet; third-party SecMI-style evidence. | Must fix repo commit, four score JSON hashes, two split `.npz` hashes, row fields `dataset`, `image_id`, `label`, `t_error`, `score=-t_error`, and CPU verifier output hash. Must prove split overlap is zero. | It is not official Quantile Regression output and does not provide a non-adjacent second mechanism. | Only small JSON/NPZ metadata already needed for CPU replay. No full 484MB repo clone or SharePoint/DDPM weights. | No. | `support-only` / E2 false-promotion support. | Official Quantile Regression score output or trained quantile model artifact appears with row-bound verifier. |
| Tracing the Roots feature packet | Strong mechanism/support signal; not a raw audit asset. | Must bind feature row id to `train/eval`, `member/external`, tensor index, tensor hashes, supplement hash, probe script hash, replay output hash, and label-shuffle/permutation control. To upgrade, also needs raw CIFAR sample ids or a public regeneration path and target checkpoint identity. | Current artifact is a feature packet; raw target/checkpoint/image/query-response provenance is missing. | Only existing supplement/feature packet metadata and CPU replay if already local. No raw dataset regeneration. | No new sweep. | `support-only` / mechanism evidence. | Public raw sample manifest plus target checkpoint identity or regeneration path becomes available. |

## 3. Manifest Columns For Any Reopened Candidate

Any reopened E1 row must produce a compact manifest with these columns before
larger compute is considered:

| Column | Meaning |
| --- | --- |
| `candidate_id` | Stable scout id. |
| `candidate_name` | Human-readable candidate name. |
| `public_source` | Citeable public source URL or local evidence note. |
| `official_or_third_party` | Whether the artifact is official, author-linked, or third-party. |
| `asset_surface` | Score packet, response packet, feature packet, checkpoint, split, or generated artifact. |
| `target_identity_gate` | `Pass / Partial / Fail / N/A` for target/checkpoint identity. |
| `row_id_gate` | Whether each score/response/feature row has immutable identity. |
| `split_label_gate` | Whether member/nonmember or equivalent labels are explicit and non-overlapping. |
| `score_or_feature_packet_gate` | Whether row-level scores/features can be loaded without training. |
| `artifact_hashes_required` | Exact files and hashes needed to replay the manifest. |
| `metric_recompute_command` | No-training command that recomputes the claimed metrics. |
| `metric_threshold_result` | AUC and low-FPR result after replay. |
| `control_required` | Label-shuffle, permutation, or surface-delta control required. |
| `first_blocker` | First missing gate that prevents admission. |
| `download_allowed` | The largest allowed asset class before the next gate. |
| `gpu_allowed` | Whether any GPU job is allowed; default is `no`. |
| `allowed_wording` | Current paper wording: `admitted`, `bounded-support`, `candidate-only`, or `support-only`. |
| `paper_track_fit` | Direction A support, Direction B observable, or no paper fit. |
| `reopen_condition` | Concrete evidence that would justify more work. |

## 4. Stop Rules

- Stop CopyMark immediately if row-level member/nonmember identity cannot be
  bound to per-row scores and target/checkpoint identity without downloading a
  full image/weight bundle.
- Stop NDSS-324 under the current ZIP state: safe static inspection did not
  expose immutable row IDs, score vectors remain absent, and score regeneration
  would require a broad image-generation/feature-extractor matrix.
- Stop Quantile immediately if the available packet remains third-party
  SecMI-style `t_error` evidence without official Quantile Regression row
  output.
- Stop Tracing the Roots immediately if the route stays feature-only without
  raw sample ids, target checkpoint identity, or a public regeneration path.
- Do not open a same-family sweep for any candidate. A failed manifest gate is a
  Direction A/C missing-surface result, not an invitation to build a new
  experiment matrix.

## 5. Current Paper Impact

E1 does not block the Direction A measurement route. CopyMark currently fails
the compact-manifest gate, so it does not become a second-asset observable.
NDSS-324 now becomes the only compute-gated E1 candidate worth preserving, but
it is still not a public score/response asset because the verified Zenodo ZIP
does not expose immutable row IDs, a complete paper-faithful split manifest, or
the score vectors described in the paper appendix.
This failure still supports the E2 thesis: public scores or artifacts often look
reportable before row identity, split labels, and metric provenance are checked.
Reopen CopyMark only after the GitHub commit, HF dataset SHA, or
author-published manifest surface changes. Reopen NDSS-324 only through the
future-public-manifest gate described in its preflight note.
