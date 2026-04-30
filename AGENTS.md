# Research Agent Guide

This file is the operating guide for agents and teammates working inside
`Research/`.

## Repository Role

`Research/` is the evidence engine for diffusion-model privacy auditing. It
owns research code, configs, evidence status, bounded experiments, and
claim-boundary language. Product UI belongs in `Platform/`; runtime job
orchestration belongs in `Runtime-Server/`.

## Fresh-Session Intake

Read in this order:

1. `<DIFFAUDIT_ROOT>/ROADMAP.md`
2. `<DIFFAUDIT_ROOT>/Research/ROADMAP.md`
3. `<DIFFAUDIT_ROOT>/Research/README.md`
4. `<DIFFAUDIT_ROOT>/Research/docs/README.md`
5. `<DIFFAUDIT_ROOT>/Research/docs/start-here/getting-started.md`
6. `<DIFFAUDIT_ROOT>/Research/docs/evidence/reproduction-status.md`
7. `<DIFFAUDIT_ROOT>/Research/docs/product-bridge/README.md`
8. `<DIFFAUDIT_ROOT>/Research/docs/governance/research-governance.md`
9. `<DIFFAUDIT_ROOT>/Research/docs/rebuild/README.md`
10. `<DIFFAUDIT_ROOT>/Research/docs/evidence/workspace-evidence-index.md`
11. The relevant `workspaces/<lane>/README.md` and `plan.md`

Do not start from memory or old chat context. Re-anchor on repository files.

## Current Operating State

- Active work: `Cross-box evidence boundary hardening`
- Next GPU candidate: `none`
- CPU sidecar: `Public-surface / hot-path sync`
- No GPU task should start from documentation or governance cleanup alone.
- No history rewrite or force-push without a separate approved audit.

## Research Rules

- Treat paper reproduction as grounding, not the whole project.
- Treat free exploration as bounded innovation, not open-ended wandering.
- Every research task needs a hypothesis, budget, evidence anchor, verdict,
  and next action.
- Report `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR` for promoted attack or
  defense evidence when applicable.
- Do not promote DDPM/CIFAR10 results into conditional-diffusion or commercial
  model claims without separate evidence.

## Workspace Discipline

Current lane state lives in:

- `workspaces/black-box/`
- `workspaces/gray-box/`
- `workspaces/white-box/`
- `workspaces/implementation/`
- `workspaces/intake/`
- `workspaces/runtime/`

Historical dated notes live under `legacy/workspaces/`. Do not add new dated
verdict logs to the hot path unless they are current lane summaries.

Internal execution identifiers may exist in legacy archives, but they are not
the public navigation system. Hot-path docs should use descriptive lane names
such as `Cross-box evidence boundary hardening`, not run IDs.

## Public Documentation Rules

Public docs are for new teammates and external reviewers. They must not contain
personal machine paths, private operator instructions, raw agent prompts,
deadline pressure, or unstated product claims.

Use:

- `<DIFFAUDIT_ROOT>`
- `<DOWNLOAD_ROOT>`
- environment variables
- repository-relative paths

Run before pushing documentation or governance changes:

```powershell
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
```

## Subagent Policy

Subagents are optional. Use them only for bounded side work such as paper
scouting, review, audit, or implementation slices with explicit write scope.
Read-only is the default. The main agent owns roadmap truth and promotion into
mainline language.
