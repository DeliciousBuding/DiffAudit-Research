# DiffAudit

DiffAudit is a research-oriented privacy risk auditing system for diffusion models.

The current repository stage is a minimal project skeleton for topic research, architecture design, and early prototype work. The first milestone is an offline audit pipeline that can:

1. register audit assets such as datasets, checkpoints, and prompts
2. run membership inference attacks against diffusion models
3. evaluate risk with reproducible metrics
4. generate audit-ready reports

## Repository Layout

```text
docs/                  design notes, architecture, and experiment protocols
references/            curated external references copied or summarized for the project
experiments/           experiment runs, result snapshots, and analysis artifacts
configs/               dataset, model, attack, and benchmark configuration files
src/diffaudit/         project source package
notebooks/             exploratory analysis and paper reproduction notebooks
scripts/               repeatable command-line utilities
tests/                 automated tests for code added later
```

## Initial Scope

- Single domain: image diffusion models
- Single adapter baseline: Hugging Face `diffusers`
- Offline auditing only
- Research prototype first, system demo second

## Near-Term Work

1. define the audit asset schema and benchmark protocol
2. select the first attack path to implement
3. wire a reproducible experiment pipeline
4. add reporting outputs for audit evidence
