# E2Q-006 CopyMark Compact-Manifest Gate

> Date: 2026-06-06
> Scope: no-download public-source check for CopyMark as a possible second
> row-bound asset.

This check asks whether the current public CopyMark surface has gained a compact
row manifest that could bind filename, member/nonmember role, target/checkpoint
identity, per-row score, metric source, and artifact hashes. It does not clone
the repository, download the Hugging Face dataset zip, download image/model
payloads, run scripts, or launch GPU/DCU work.

Machine-readable checks:
[`e2q006_copymark_compact_manifest_gate_2026_06_06.csv`](e2q006_copymark_compact_manifest_gate_2026_06_06.csv).

## Public Sources Checked

### GitHub Repository

- Repository: `https://github.com/caradryanl/CopyMark`
- Default branch: `main`
- Current branch commit: `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`
- Commit date: `2024-11-24T04:00:19Z`
- Last push observed by GitHub API: `2024-11-24T04:00:25Z`
- Repository size field: `385,408` KB
- Recursive tree: `746` entries, `truncated=false`

Authenticated GitHub code search found no CopyMark experiment compact manifest.
The query `manifest repo:caradryanl/CopyMark` returned only vendored
`MANIFEST.in` mentions in UI license text. Queries for row-manifest-style
phrases returned no hits. Searches around `member_scores_all_steps` still point
to scripts that load or produce tensors, not to a row-bound manifest.

Selected `contents` API checks still show the same artifact class as the prior
evidence note:

- `diffusers/experiments/sd/pia/`: score-result JSON files, test image log, and
  member/nonmember score tensors.
- `diffusers/experiments/sd/pfami/`: score-result JSON files, image logs,
  member/nonmember score tensors, and running-time JSON.
- `diffusers/experiments/sd/secmi/`: score-result JSON files, test image log,
  and member/nonmember score tensors.
- `diffusers/experiments/laion_ridar/`: feature arrays, image logs,
  score-result JSON files, running-time JSON, and an XGBoost model.
- `diffusers/experiments/ldm/pia/` and `diffusers/experiments/sdxl/secmi/`:
  analogous score-result JSON, image-log, score tensor, and runtime surfaces.

These files are useful official support artifacts, but they are not one
manifest binding row identity, role, score, metric source, target/checkpoint,
and hashes.

### Hugging Face Dataset

The official README points to the CopyMark dataset on Hugging Face. The current
HF API resolves the dataset surface to `chumengl/copymark`:

- Dataset id: `chumengl/copymark`
- Dataset SHA: `331cd0010f8b638922f184cad0e6f5ccd8db78d4`
- Last modified: `2024-06-17T06:12:46.000Z`
- Public / not gated

The tree has only three entries:

- `.gitattributes`
- `README.md`
- `datasets.zip`

`datasets.zip` is `5,662,307,542` bytes with LFS oid
`7d07a61ade04aff79c9ad4399b2a9e82b25ee715483e0e2d68f4ac995ee4e779`. No compact
manifest, JSON, CSV, parquet, split index, or score packet is exposed outside
the large ZIP.

## Gate Verdict

`no_go_compact_row_manifest_missing_current_public_surface`.

CopyMark remains the closest image-diffusion challenger because the official
repo exposes meaningful image logs, score-result JSON files, and selected score
tensors/features. It still fails the E1/E2 row-bound manifest gate because the
public surface does not provide:

- one row manifest joining filename or immutable row id, member/nonmember role,
  target/checkpoint identity, per-row score, and metric source;
- target checkpoint/model hash;
- compact split/data-packet manifest or row-level hash contract outside the
  large ZIP; the public surface exposes only the large ZIP LFS oid;
- a no-training verifier that recomputes AUC, ASR, TPR@1%FPR, and
  TPR@0.1%FPR from compact public inputs.

## Decision

Keep `E2Q-006` as bounded support / missing-surface evidence. Do not promote it
into `E2-20260606-N50`, do not use it as a second independent response/score
asset, and do not release GPU/DCU work.

Reopen only if one of these changes:

- the GitHub branch moves beyond `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`
  and adds a compact manifest or verifier;
- the Hugging Face dataset SHA changes and exposes manifest-level files outside
  `datasets.zip`;
- the authors publish an explicit row-bound manifest/verifier elsewhere.

## Stop Rules

- Do not download `datasets.zip`.
- Do not clone the full repository by default.
- Do not download image folders, model folders, Stable Diffusion, LDM,
  CommonCanvas, LAION, COCO, CC12M, YFCC, DataComp, FFHQ, CelebA-HQ, or
  CommonCatalog payloads.
- Do not regenerate PIA/PFAMI/SecMI/GSA features, fit XGBoost, train models, or
  launch GPU/DCU jobs from this gate.
