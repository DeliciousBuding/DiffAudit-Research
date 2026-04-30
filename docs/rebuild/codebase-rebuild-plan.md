# Codebase Rebuild Plan

Last updated: `2026-04-30`

This plan sequences Research codebase cleanup into small, reviewable PRs. It is
not a research-experiment roadmap and does not authorize GPU work.

## Rebuild Principles

- Preserve behavior first; improve shape second.
- Characterize outputs before splitting large research modules.
- Keep one PR focused on one architectural seam.
- Do not combine refactors with new evidence claims.
- Prefer package APIs over imports from `scripts/` or private helpers.

## Completed Baseline

| Area | Status |
| --- | --- |
| Shared metrics and I/O helpers | Initial low-risk extraction merged into `src/diffaudit/utils/`. |
| CLI shape | `diffaudit.cli` is now a package with grouped command registration and dispatch. |
| Local checks | Fast local checks include public-surface and Markdown-link guards. |
| Placeholder packages | Empty tracked package placeholders were removed. |
| External clone dependency in tests | SecMI registry tests create temporary fake upstream workspaces. |
| Rebuild docs | `docs/rebuild/` is the dedicated codebase rebuild planning surface. |
| R1 test and boundary cleanup | Adapter test fixtures are centralized, and active tests no longer require real `external/SecMI` or `external/Reconstruction-based-Attack` clones. |

## Next PR Sequence

| Priority | PR Theme | Acceptance Boundary |
| --- | --- | --- |
| R2 | GSA shared helper extraction | Extract cycle-prone shared helpers from `gsa.py` / `gsa_observability.py` into an explicit internal helper module. |
| R3 | Defense private-import cleanup | Replace defense imports from attack-private helpers with public package APIs or local shared helpers. |
| R4 | Optional external adapter boundary | Replace remaining `sys.path` mutation around ignored upstream clones with explicit optional-contract wrappers. |
| R5 | Package dependency extras | Split package metadata into minimal install extras after runtime boundaries are stable. |

## Deferred Work

The following work is real debt but should not be the next PR unless its
characterization tests already exist:

- Splitting `pia_adapter.py`.
- Splitting `gsa.py`.
- Splitting `recon.py`.
- Moving training loops out of exploratory scripts.
- Consolidating the next-run tools.

## Validation Floor

Every rebuild PR should run:

```powershell
git status --short --branch
git diff --check
conda run -n diffaudit-research python -X utf8 scripts/verify_env.py
conda run -n diffaudit-research python -X utf8 scripts/run_local_checks.py --fast
```

Module-split PRs must also run targeted characterization tests for the moved
module family and document any intentionally changed output field.
