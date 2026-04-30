# Rebuild

This directory tracks codebase rebuild work for DiffAudit Research.

Use it for architecture debt, refactor sequencing, and behavior-preserving
cleanup plans. Do not use it for research evidence, asset handoff, GitHub
collaboration rules, or long execution logs.

## Scope

| Area | Belongs Here | Does Not Belong Here |
| --- | --- | --- |
| Package architecture | CLI package shape, adapter boundaries, shared utility extraction | New attack results or admitted evidence |
| Refactor plans | Small PR sequence, characterization-test requirements, rollback boundaries | Agent prompts or chat transcripts |
| Audit triage | Which reviewer findings are admitted, stale, rejected, or deferred | Raw local disk inventories without reproducible commands |
| Rebuild status | What has merged and what remains as code debt | Repository policy that belongs in `docs/governance/` |

## Current State

Merged by 2026-04-30:

- Shared utility extraction into `src/diffaudit/utils/`.
- CLI package split into `src/diffaudit/cli/`.
- Local checks aligned with public-surface and Markdown-link guards.
- Empty placeholder package directories removed from `src/diffaudit/`.

Still open as rebuild work:

- Split the largest adapter modules only after characterization tests exist.
- Replace private cross-module imports with explicit public helper APIs.
- Move remaining reusable script logic into package modules when it is needed
  by tests, CLI commands, or downstream consumers.
- Revisit package dependency extras after the package/runtime boundary is
  stable.

## Documents

| Document | Purpose |
| --- | --- |
| [codebase-rebuild-plan.md](codebase-rebuild-plan.md) | Current behavior-preserving rebuild sequence and validation floor. |
| [architecture-audit-triage-2026-04-30.md](architecture-audit-triage-2026-04-30.md) | Corrected outcomes from the 2026-04-30 architecture review. |

## Rules

- Prefer behavior-preserving PRs with narrow scope.
- Do not mix code architecture rebuilds with new GPU experiments.
- Do not move evidence files into this directory.
- Record only durable decisions; transient execution notes belong in PRs or
  `legacy/` when they need to be preserved.
