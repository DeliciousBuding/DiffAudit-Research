# DiffAudit Research Documentation

This is the documentation map for DiffAudit Research. The public path is for
new teammates, reviewers, and downstream users. Internal material is retained
for traceability but is no longer part of the default reading path.

## Public Path

Read these in order when onboarding:

| Step | Document | Purpose |
| --- | --- | --- |
| 1 | [../README.md](../README.md) | Project overview and product relationship. |
| 2 | [start-here/getting-started.md](start-here/getting-started.md) | First orientation for contributors. |
| 3 | [start-here/teammate-setup.md](start-here/teammate-setup.md) | New-machine setup and first validation. |
| 4 | [assets-and-storage/data-and-assets-handoff.md](assets-and-storage/data-and-assets-handoff.md) | How to obtain datasets, weights, supplementary files, and external code. |
| 5 | [start-here/command-reference.md](start-here/command-reference.md) | Runnable CLI recipes. |
| 6 | [evidence/reproduction-status.md](evidence/reproduction-status.md) | Per-track reproduction and evidence state. |
| 7 | [product-bridge/README.md](product-bridge/README.md) | What Research can safely expose to Platform and Runtime. |

## Public Reference Groups

| Group | Contents |
| --- | --- |
| [start-here/](start-here/) | Contributor setup, environment, command reference, and repository map. |
| [assets-and-storage/](assets-and-storage/) | `Download/` layout, storage boundaries, naming policy, and asset handoff. |
| [evidence/](evidence/) | Reproduction ladder, admitted results, innovation evidence, and workspace evidence index. |
| [product-bridge/](product-bridge/) | Research-to-Platform/Runtime boundaries and consumer-facing evidence rules. |
| [governance/](governance/) | Repository governance, GitHub workflow, license, brand, and history-rewrite audit. |

## Internal Research Material

| Location | Purpose |
| --- | --- |
| [internal/](internal/) | Agent prompts, long progress ledgers, competition notes, paper reports, and review bundles. |
| [../workspaces/](../workspaces/) | Current lane status only; historical dated notes have moved to `legacy/workspaces/`. |
| [../legacy/](../legacy/) | Archived execution logs, closed verdicts, and old handoff material. |

Internal files are preserved for auditability. They should not be copied into
public product copy without rewriting and evidence-status checks.

## Public-Surface Rules

- Use repository-relative paths, `<DIFFAUDIT_ROOT>`, or `<DOWNLOAD_ROOT>`.
- Do not include personal machine paths, local operator instructions, or raw
  agent prompts in public onboarding material.
- Do not present smoke tests, dry runs, negative packets, or blocked attempts
  as paper-level reproduction.
- Keep datasets, model weights, checkpoints, OCR dumps, raw tensors, and large
  generated artifacts outside Git.
