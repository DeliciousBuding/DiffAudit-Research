# Materials Index

`references/materials/` stores the portable material index used by the DiffAudit
research workflow.

It intentionally does not store third-party paper PDFs or DOCX files in Git.
Use `manifest.csv` as the source of truth for upstream source URLs, expected
local paths, checksums, file sizes, and license notes. Local copies should live
in the external asset layer, typically `<DIFFAUDIT_ROOT>/Download/shared/papers/`
or a team-managed asset mirror.

## Layout

```text
materials/
  manifest.csv
  README.md
  paper-index.md
```

Rules:

- Use English folder names only.
- Use ASCII lowercase kebab-case file names.
- Prefer `year-venue-short-title.pdf` or `year-venue-short-title.docx` in the
  manifest path field.
- Keep one canonical copy for the same paper whenever possible.
- Do not commit third-party PDFs, DOCX files, datasets, weights, checkpoints,
  or supplementary bundles to this repository.

## Scoring Rubric

`credibility_score`

- `5`: peer-reviewed flagship venue or official publisher copy
- `4`: arXiv or OpenReview preprint with clear research relevance
- `3`: internal context document or local mirror with known provenance
- `2`: mirrored or partially normalized material with unclear provenance
- `1`: unclassified legacy archive item

`reference_value_score`

- `5`: core paper for the current DiffAudit implementation route
- `4`: strong secondary reference with direct design value
- `3`: useful scenario extension or supporting background
- `2`: weak or indirect reference
- `1`: not yet normalized enough for active research use

## Canonical Highlights

| Track | Canonical files |
| --- | --- |
| `black-box` | `2025-ndss-black-box-membership-inference-fine-tuned-diffusion-models.pdf`, `2024-arxiv-towards-black-box-membership-inference-diffusion-models.pdf`, `2024-neurips-clid-membership-inference-text-to-image-diffusion.pdf` |
| `gray-box` | `2023-icml-secmi-membership-inference-diffusion-models.pdf`, `2024-iclr-pia-proximal-initialization.pdf`, `2025-arxiv-sima-score-based-membership-inference-diffusion-models.pdf`, `2025-arxiv-small-noise-injection-membership-inference-diffusion-models.pdf` |
| `white-box` | `2025-popets-white-box-membership-inference-diffusion-models.pdf`, `2024-neurips-finding-nemo-localizing-memorization-neurons-diffusion-models.pdf` |
| `context` | `diffaudit-team-onboarding.pdf`, `diffaudit-product-requirements.pdf`, `mia-defense-document.docx`, `context/mia-defense-document.md` |
| `survey` | `2025-neurips-tracing-the-roots-origin-attribution-diffusion-trajectories.pdf`, `2025-icdar-dp-docldm-private-document-image-generation-latent-diffusion.pdf`, `2025-aaai-privacy-preserving-lora-membership-inference-latent-diffusion-models.pdf`, `2024-arxiv-dual-model-defense-diffusion-membership-inference-disjoint-data-splitting.pdf`, `2025-ndss-diffence-fencing-membership-privacy-diffusion-models.pdf`, `2025-arxiv-defending-diffusion-models-membership-inference-higher-order-langevin-dynamics.pdf`, `2026-arxiv-inference-attacks-graph-generative-diffusion-models.pdf`, `2025-arxiv-perturb-a-model-not-an-image-anti-personalized-diffusion-models.pdf`, `survey-index-diffusion-privacy-literature.pdf` |

## Source of Truth

`manifest.csv` is the full index.

Columns:

- `relative_path`: canonical path under `references/materials/`
- `primary_track`: primary physical category
- `track_tags`: multi-track labels when a paper spans more than one threat model
- `credibility_score`: source quality score from `1` to `5`
- `reference_value_score`: project usefulness score from `1` to `5`
- `source_url`, `accessed_at`, `sha256`, `size_bytes`, `license_note`, `notes`: provenance and maintenance fields

When adding a new material, update `manifest.csv` in the same commit. If the
material is large or third-party, commit only the manifest row and acquisition
notes, not the binary file.
