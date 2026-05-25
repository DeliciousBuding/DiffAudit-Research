# Build Notes

## Generate Figures

```powershell
& 'C:\Users\Ding\miniforge3\envs\diffaudit-research\python.exe' -X utf8 .\scripts\build_paper_assets.py
```

This rebuilds:

- `data/admitted_rows.csv`
- `data/h2_output_cloud_rows.csv`
- `data/negative_support_rows.csv`
- `figures/admitted_rows_metrics.pdf`
- `figures/h2_output_cloud_controls.pdf`
- `figures/negative_and_support_rows.pdf`

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

The current verified compile path produced a 5-page `paper.pdf` on 2026-05-26.
