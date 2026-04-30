# Repository Cleanup Status

Last updated: `2026-04-30`

This document is the current cleanup status for the Research repository. It is
not a research roadmap; use [../ROADMAP.md](../../ROADMAP.md) for active research
direction and [research-governance.md](research-governance.md) for durable
repository rules.

## Current State

- Active long-running cleanup branch: none; governance work should stay PR-scoped
- Merged cleanup baseline: PR #26 through PR #36 are merged to `main`
- GPU work: no active GPU task
- History rewrite: not performed
- Top-level `outputs/`: ignored local scratch, not a canonical evidence layer
- Canonical evidence: workspace verdict notes, small `summary.json` files,
  manifests, and admitted result tables

## Completed In The 2026-04-29 Governance Pass

- PR #26 was squash-merged into `main` as `729160a53829766a6c7216042d9395ed5462090b`.
- `ROADMAP.md` was compressed into a short steering document.
- Long autonomous execution history moved to `legacy/execution-log/2026-04-29/`.
- `workspaces/implementation/challenger-queue.md` now uses
  `active / ready / hold / needs-assets / closed` sections.
- Closed one-off `run_x*.py` scripts moved out of top-level `scripts/`.
- Generated binary artifacts were removed from the current branch.
- `.gitignore` was tightened so tracked curated files are not hidden by broad
  ignore rules.
- `scripts/check_public_surface.py` now guards against private paths, forbidden
  artifacts, oversized tracked files, and tracked files hidden by `.gitignore`.

## Completed In The 2026-04-30 Cleanup Pass

- PR #28 reset the information architecture: public docs, internal docs,
  workspace archives, and asset-boundary docs now have stable entry points.
- PR #29 extracted shared research utility helpers into `src/diffaudit/utils/`
  and migrated the lowest-risk duplicated metrics/I/O call sites.
- PR #30 converted the architecture review into a corrected governance note,
  fixed the `src -> scripts` DDPM factory dependency, added explicit package
  initializers, and aligned fast local checks with CI guards.
- PR #31 synced the post-governance research hot path.
- PR #32 added the local asset-boundary audit and preserved the
  `Download/` versus local generated-artifact split.
- PR #33 and PR #34 split the CLI into the `src/diffaudit/cli/` package and
  grouped dispatch surface without changing command names.
- PR #35 restored the active research state after CLI governance.
- PR #36 removed internal run IDs from public and hot-path navigation while
  keeping legacy IDs available for traceability.
- The portability documentation sync corrected remaining references to the
  removed `src/diffaudit/cli.py` single-file entrypoint.

## Remaining Local State

The working machine may still contain large ignored directories such as:

- `outputs/`
- `workspaces/*/runs/*/checkpoints/`
- `workspaces/*/runs/*/generated-images/`
- `workspaces/*/runs/*/score-artifacts/`
- upstream clones under `external/`

These local directories are intentionally outside the Git review surface. If a
result from them matters, promote a small curated summary into the relevant
workspace before committing.

Do not run broad `git clean -fdX` in this repository. It would remove ignored
local evidence, upstream checkouts, and asset staging directories. Only remove
safe generated caches such as `__pycache__/`, `.pytest_cache/`, and temporary
build metadata when doing routine hygiene.

## Next Cleanup Priorities

1. Keep public docs and onboarding documents product-facing.
2. Keep `AGENTS.md` focused on agent operating discipline, not product copy.
3. Keep `legacy/execution-log/` as traceability archive, not active roadmap.
4. Keep `Download/` manifests current when asset locations or names change.
5. Keep deployment language precise: Research is a conda/editable-package CLI
   and evidence repository, while service deployment belongs to
   `Runtime-Server/` and `Platform/`.
6. Revisit history rewriting only after `docs/governance/history-rewrite-audit.md` is
   separately approved.

## Validation Commands

Run these before opening or updating governance changes:

```powershell
git status --short
git diff --check
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
python -X utf8 scripts/verify_env.py
python -X utf8 -m diffaudit --help
python -X utf8 scripts/run_local_checks.py --fast
```
