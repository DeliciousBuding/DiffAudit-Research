# References

This directory stores the repository-level reference index for papers and
context materials used by DiffAudit Research.

The Git repository does not distribute third-party paper PDFs or DOCX files.
Those materials remain external assets governed by their upstream terms. Use
`materials/manifest.csv` to find the source URL, checksum, size, and expected
local material path when a local copy is needed.

## What changed

`references/materials/` is now organized with English-only folders:

- `black-box/`
- `gray-box/`
- `white-box/`
- `survey/`
- `context/`

The old Chinese folder layout has been removed.

## Index Files

- `materials/manifest.csv`: machine-readable source of truth with path, track, scores, provenance and hashes
- `materials/README.md`: human-readable layout, acquisition rules, naming rules and scoring rubric
- `materials/paper-index.md`: human-readable paper-by-paper summary index with open-source links when available

## Maintenance rules

- Keep material file names ASCII-only and kebab-case.
- Prefer one canonical manifest row per paper or context material.
- Record every new material in `manifest.csv`.
- Do not commit third-party PDFs, DOCX files, datasets, model weights, or other
  large external assets to this repository.
- Store local paper copies outside Git, normally under
  `<DIFFAUDIT_ROOT>/Download/shared/papers/` or a team asset mirror.
- Use `credibility_score` and `reference_value_score` to make triage explicit instead of relying on filename intuition.

Do not treat the presence of a manifest row or local material path as proof
that the paper has already been reproduced.
