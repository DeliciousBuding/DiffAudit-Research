# Build Notes

## Generate Figures

```powershell
python -X utf8 .\scripts\build_paper_assets.py
```

This rebuilds:

- `data/admitted_rows.csv`
- `data/h2_output_cloud_rows.csv`
- `data/negative_support_rows.csv`
- `data/artifact_gate_summary.csv`
- `data/artifact_strata_summary.csv`
- `figures/admitted_rows_metrics.pdf`
- `figures/h2_output_cloud_controls.pdf`
- `figures/evidence_contract_pipeline.pdf`
- `figures/artifact_gate_summary.pdf`

## Compile Paper

`latexmk` is installed through MiKTeX but currently cannot run because MiKTeX
cannot find Perl. Use the manual chain:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
bibtex build/main
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
Copy-Item -LiteralPath .\build\main.pdf -Destination .\paper.pdf -Force
```

The current verified compile path produced an 8-page `paper.pdf` on 2026-05-26.

## Pre-Submission Sanity Checks

Run these checks before claiming the PDF is submission-ready:

```powershell
pdfinfo .\paper.pdf | Select-String 'Pages|Page size'
Select-String -Path .\build\main.log -Pattern 'Undefined|Citation.*undefined|Reference.*undefined|Overfull|LaTeX Warning'
pdftotext .\paper.pdf - | Select-String -Pattern 'D:\\|C:\\|Users\\|Documents\\|secret|token|product-ready|disprove|field-wide prevalence' -Context 0,1
```

From the repository root, also run:

```powershell
python -X utf8 scripts\run_pr_checks.py
git diff --check
```

The PDF text scan is intentionally conservative. Hits are not automatically
failures, but each hit must be either a harmless boundary/caveat phrase or
removed before public release.
