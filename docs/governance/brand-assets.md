# Brand Assets

This repository keeps small SVG brand assets in Git so the README and docs stay
portable across GitHub, forks, local clones, and archived releases.

## Assets

| Asset | Use |
| --- | --- |
| [brand/diffaudit-logo.svg](../brand/diffaudit-logo.svg) | Primary horizontal logo for light backgrounds and the GitHub README. |
| [brand/diffaudit-logo-white.svg](../brand/diffaudit-logo-white.svg) | Primary horizontal logo for dark backgrounds. |
| [brand/diffaudit-mark.svg](../brand/diffaudit-mark.svg) | Compact mark for small placements on light backgrounds. |
| [brand/diffaudit-mark-white.svg](../brand/diffaudit-mark-white.svg) | Compact mark for small placements on dark backgrounds. |

## README And Docs Usage

Use paths relative to the Markdown file that contains the image.

For the repository-root `README.md`, use the `docs/assets/...` path and
GitHub's theme-specific image fragments:

```html
<img src="docs/brand/diffaudit-logo.svg#gh-light-mode-only" alt="DiffAudit" width="360">
<img src="docs/brand/diffaudit-logo-white.svg#gh-dark-mode-only" alt="DiffAudit" width="360">
```

For Markdown files inside `docs/`, use the shorter `assets/...` path:

```html
<img src="assets/brand/diffaudit-logo.svg#gh-light-mode-only" alt="DiffAudit" width="360">
<img src="assets/brand/diffaudit-logo-white.svg#gh-dark-mode-only" alt="DiffAudit" width="360">
```

This keeps the visual identity versioned with the documentation and avoids
external image availability problems.

## Hosting Policy

Prefer repository-relative SVGs for:

- GitHub README files;
- repository documentation;
- release notes that should remain readable in forks or archives.

Use a website CDN or image host only for:

- public websites that already depend on the website deployment;
- social preview images or raster assets that need CDN caching;
- marketing pages where analytics, cache invalidation, or cross-repository reuse
  is managed by the website.

Do not reference local presentation paths or `.ai` source files from GitHub
README documents. The `.ai` files remain source material for design workflows,
while SVG exports are the documentation assets that last across versions.
