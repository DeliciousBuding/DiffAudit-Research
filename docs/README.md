# DiffAudit Research Documentation

This is the documentation index for DiffAudit Research. The public path is for
new contributors and external reviewers. Internal material is retained for
reference but is not part of the default reading path.

## Public Path

Read these in order when getting started:

| Step | Document | Purpose |
| --- | --- | --- |
| 1 | [../README.md](../README.md) | Project overview and ecosystem context. |
| 2 | [start-here/getting-started.md](start-here/getting-started.md) | First steps for new contributors. |
| 3 | [start-here/teammate-setup.md](start-here/teammate-setup.md) | Machine setup and first validation. |
| 4 | [assets-and-storage/data-and-assets-handoff.md](assets-and-storage/data-and-assets-handoff.md) | How to get datasets, model weights, and external code. |
| 5 | [start-here/command-reference.md](start-here/command-reference.md) | CLI commands and usage examples. |
| 6 | [evidence/reproduction-status.md](evidence/reproduction-status.md) | Per-track experiment status. |
| 7 | [product-bridge/README.md](product-bridge/README.md) | How Research feeds into Platform and Runtime. |

## Reference Sections

| Section | Contents |
| --- | --- |
| [start-here/](start-here/) | Contributor setup, environment, CLI reference, repository map. |
| [assets-and-storage/](assets-and-storage/) | Data layout, storage boundaries, naming conventions, asset handoff. |
| [evidence/](evidence/) | Experiment status, verified results, innovation map, workspace index. |
| [product-bridge/](product-bridge/) | Research-to-Platform/Runtime integration and data contracts. |
| [governance/](governance/) | Repository governance, GitHub workflow, licensing, branding. |
| [rebuild/](rebuild/) | Codebase rebuild status and refactoring notes. |

## Internal Research Material

| Location | Contents |
| --- | --- |
| [internal/](internal/) | Internal coordination notes, progress logs, competition notes, paper reports. |
| [../workspaces/](../workspaces/) | Current research state per direction. |
| [../legacy/](../legacy/) | Archived experiment logs and closed notes. |

Internal files are preserved for reference. They should not be copied into
public documentation without rewriting and fact-checking.

## Documentation Rules

- Use repository-relative paths, `<DIFFAUDIT_ROOT>`, or `<DOWNLOAD_ROOT>` —
  not personal machine paths.
- Don't include private operator instructions or raw agent prompts in public docs.
- Don't present smoke tests, dry runs, or blocked attempts as benchmark results.
- Datasets, model weights, and large generated files should stay outside Git.
