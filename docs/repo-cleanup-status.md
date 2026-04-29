# Repository Cleanup Status

Last updated: `2026-04-29`

This document is the current cleanup status for the Research repository. It is
not a research roadmap; use [../ROADMAP.md](../ROADMAP.md) for active research
direction and [research-governance.md](research-governance.md) for durable
repository rules.

## Current State

- Active cleanup branch: `research-governance-cleanup-20260429`
- GPU work: frozen for governance cleanup
- History rewrite: not performed
- Top-level `outputs/`: ignored local scratch, not a canonical evidence layer
- Canonical evidence: workspace verdict notes, small `summary.json` files,
  manifests, and admitted result tables

## Completed In The 2026-04-29 Governance Pass

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

## Next Cleanup Priorities

1. Keep public docs and onboarding documents product-facing.
2. Keep `AGENTS.md` focused on agent operating discipline, not product copy.
3. Keep `legacy/execution-log/` as traceability archive, not active roadmap.
4. Keep `Download/` manifests current when asset locations or names change.
5. Revisit history rewriting only after `docs/history-rewrite-audit.md` is
   separately approved.

## Validation Commands

Run these before opening or updating governance PRs:

```powershell
git status --short
git diff --check
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/verify_env.py
python -X utf8 -m diffaudit --help
python -X utf8 scripts/run_local_checks.py --fast
```
