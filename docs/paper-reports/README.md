# Paper Reading Reports

This directory stores one detailed reading report per indexed material in
`references/materials/manifest.csv`.

## Goals

- Use one uniform scientific writing standard across all reports.
- Preserve one local Markdown report per indexed material in the repository.
- Maintain one Feishu document per report for link-based reading and review.
- Feed the concise, scientific summary in `references/materials/paper-index.md` from the corresponding detailed report rather than hand-written ad hoc notes.
- Link to upstream paper sources through `references/materials/manifest.csv`.
  Do not make reports depend on GitHub-hosted paper PDF blobs.

## Layout

```text
docs/paper-reports/
  README.md
  report-spec.md
  report-template.md
  manifest.csv
  black-box/
  gray-box/
  white-box/
  survey/
  context/
  assets/
```

Generated OCR dumps, full-paper Markdown exports, page-level JSON, service
responses, and extraction scratch images are intentionally excluded from Git.
They are reproducible intermediate artifacts and may contain unstable service
URLs or publisher text beyond what this repository should redistribute.

## Naming Rules

- Report file name: reuse the manifest material stem and append `-report.md`.
- Report location: place reports under the track folder that matches the
  material's `primary_track`.
- Image assets: store extracted figures under `docs/paper-reports/assets/<track>/`.
- Key figure image name: `<pdf-stem>-key-figure-p<page>.png`.
- If the figure is cropped from a page region, keep the same naming rule and record the crop box inside the report.
- Keep only report-referenced canonical figures. Do not commit scratch crops,
  full-page previews, `_sample-*`, `test-*`, or temporary formula-rendering
  files.
- Do not commit generated OCR directories, full-paper Markdown exports,
  page-level OCR JSON, or external OCR service responses.

## Feishu Rules

This repo only defines the report content contract.

Workspace-local Feishu publishing rules and commands are operator-local surfaces outside `Research`.

Do not treat historical `LocalOps/feishu/...` paths in old notes as a portable prerequisite.

If you are working inside the full DiffAudit root workspace, start from `<DIFFAUDIT_ROOT>/Archive/LocalOps/README.md` and then follow the current machine-local publishing flow from there.

Within `Research`, keep these expectations:

- One report corresponds to one Feishu doc.
- Each Feishu doc must be readable by anyone with the link.
- The master Feishu doc should link to the single-report Feishu docs by title.
