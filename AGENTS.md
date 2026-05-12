# Research Agent Guide

This file is the operating guide for agents and teammates working in `Research/`.

## Repository Role

`Research/` holds research code, configs, experiment status, and
results for diffusion-model privacy auditing. Product UI is in
`Platform/`; job scheduling is in `Runtime-Server/`.

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
11. The relevant `workspaces/<direction>/README.md` and `plan.md`

Do not start from memory or old chat context. Re-anchor on repository files.

## Current Operating State

- Active work: `mid-frequency same-noise residual collector implementation`
- Next GPU candidate: none selected
- CPU work: diagonal-Fisher self-influence, cross-box successor scoping,
  I-B defense-aware reopen scouting, and archived gray-box paper-candidate
  reentry are closed or on hold. The mid-frequency residual scorer contract is
  now ready; the current reducible work is a CPU-first residual collector for
  the distinct same-noise observable.
- ReDiffuse is closed as candidate-only / hold unless a new scorer or
  checkpoint-portability hypothesis appears.
- No GPU task should start from documentation or governance cleanup alone.
- Only one GPU task may run at a time; every GPU task needs a frozen command,
  metric contract, stop condition, and evidence-note target.
- No history rewrite or force-push without a separate approved audit.

## Research Rules

- Paper reproduction is a starting point, not the full project.
- Every experiment needs a hypothesis, data plan, expected result, and conclusion.
- Experiments must be hypothesis- and decision-value driven. Do not run
  experiments just to complete a narrative, fill a table, or make an ablation
  set look comprehensive; each run must answer a clear hypothesis or support a
  concrete decision.
- Stop low-marginal-information directions early. If a planned run is
  predictably unlikely to improve performance, change the directional decision,
  or unlock a better next step, especially when it only repeats an already
  established no-effect or infeasible verdict, record the reason and do not
  run an exhaustive validation.
- Report `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR` for promoted attack or
  defense results when applicable.
- DDPM/CIFAR10 results cannot be generalized to conditional-diffusion or
  commercial models without separate evidence.
- Candidate results must stay labeled as candidate-only until promoted through
  an evidence note and roadmap decision. Smoke tests are not benchmark results.
- Long autonomous runs must follow:
  `review -> select -> preflight -> run -> verdict -> docs -> next`.

## Workspace Structure

Current research state lives in:

- `workspaces/black-box/`
- `workspaces/gray-box/`
- `workspaces/white-box/`
- `workspaces/implementation/`
- `workspaces/intake/`
- `workspaces/runtime/`

Historical notes are in `legacy/workspaces/`. Don't add new dated logs to the
active workspace directories unless they are current summaries.

Use descriptive names like `Cross-box experiment boundary hardening` in active
docs, not run IDs.

## Public Documentation Rules

Public docs are for new contributors and external reviewers. They must not
contain personal machine paths, private operator instructions, raw agent prompts,
deadline pressure, or unverified product claims.

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

Subagents are optional. Use them for bounded side work such as paper scouting,
review, or implementation slices with explicit write scope. Read-only is the
default. The main agent owns roadmap truth and result promotion.
