# DiffAudit Brand Assets

SVG logo files used in README headers, documentation, and presentations.

## Files

| File | Description | Usage |
|------|-------------|-------|
| `diffaudit-logo.svg` | Full logo, dark text | README.md light-mode header |
| `diffaudit-logo-white.svg` | Full logo, white text | README.md dark-mode header |
| `diffaudit-mark.svg` | Icon mark only, dark | Favicon, compact badges |
| `diffaudit-mark-white.svg` | Icon mark only, white | Dark-background badges |

## Source

Custom designed for the DiffAudit project. All four variants share the same
base geometry with color variants for light/dark mode compatibility.

## Usage in Markdown

```markdown
<!-- Light mode (default) -->
<img src="docs/brand/diffaudit-logo.svg#gh-light-mode-only" alt="DiffAudit" width="360">

<!-- Dark mode -->
<img src="docs/brand/diffaudit-logo-white.svg#gh-dark-mode-only" alt="DiffAudit" width="360">
```

The `#gh-light-mode-only` and `#gh-dark-mode-only` fragment identifiers are
GitHub-specific and control visibility based on the viewer's theme.
