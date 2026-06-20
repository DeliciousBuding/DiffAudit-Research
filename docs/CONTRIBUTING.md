# Contributing to DiffAudit Research

Thank you for your interest in DiffAudit Research. This repository contains the
research code, experiments, and evidence tracking for privacy auditing of
diffusion models.

## What You Can Work On

| Area | Examples |
| --- | --- |
| Attack methods | Paper intake, new attack implementations, experiment plans |
| Defense methods | Defense implementations, ablation studies |
| Reproducibility | Environment setup, data pipeline, experiment configs |
| Code | Python package, CLI, adapters, tests, scripts |
| Documentation | Setup guides, experiment status, contributor guides |
| Infrastructure | CI, templates, security, licensing |

## Branches and Pull Requests

Create a branch from `main` and open a pull request. Suggested branch prefixes:

| Prefix | For |
| --- | --- |
| `black-box/` | Black-box attack or experiment work |
| `gray-box/` | Gray-box attack or defense work |
| `white-box/` | White-box attack or defense work |
| `implementation/` | Shared code, CLI, config, tests, scripts |
| `docs/` | Documentation |
| `chore/` | CI, metadata, dependency updates |

Pull request description should cover:

- **What changed** — brief summary
- **Why** — which research or engineering problem it addresses
- **How to verify** — commands run, tests passed
- **Limitations** — what this change does not yet prove
- **Next steps** — known follow-ups or blockers

## Commit Style

Use conventional prefixes:

```
feat: add variation attack smoke test
fix: correct asset path in PIA config
docs: update experiment status for recon
test: cover CLI probe command
chore: update dependency versions
```

Keep commits focused. Don't mix experiment notes, code refactors, and
documentation changes in the same commit.

## Experiment Status

When a research result changes status, update the corresponding status document.
The tracking stages are described in
[docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md):

| Stage | Meaning |
| --- | --- |
| `research-ready` | Paper, code, and data requirements reviewed. |
| `code-ready` | Commands, configs, and tests exist. |
| `asset-ready` | Required datasets or weights are available. |
| `evidence-ready` | A reviewed experiment summary exists. |
| `benchmark-ready` | Paper-level benchmarks are reproducible. |

Don't present smoke tests or dry runs as benchmark results. If a hypothesis
doesn't work out, record the negative result rather than discarding it.

## Data and Third-Party Code

Don't commit private datasets, model weights, credentials, or large data files.
Use the asset handoff documents instead:

| Document | Purpose |
| --- | --- |
| [docs/assets-and-storage/data-and-assets-handoff.md](docs/assets-and-storage/data-and-assets-handoff.md) | How to set up datasets, weights, and data paths |
| [docs/assets-and-storage/download-naming-policy.md](docs/assets-and-storage/download-naming-policy.md) | Naming conventions for project data mirror |
| [docs/governance/licensing.md](docs/governance/licensing.md) | License scope and third-party boundaries |

`third_party/` is for vendored upstream code with retained license notices.

## Validation

Run the standard checks before opening a PR:

```powershell
python scripts/run_local_checks.py
```

For documentation-only changes:

```powershell
git diff --check
python -m diffaudit --help
```

CI runs on Windows and checks CLI install, config rendering, and core tests.

## Review Focus

Reviewers should check:

| Concern | What to look for |
| --- | --- |
| Reproducibility | Commands, configs, and data paths still work |
| Overclaiming | Smoke tests or partial results aren't presented as benchmarks |
| Path safety | No hardcoded private machine paths in shared docs |
| Licensing | Third-party code and data retain their own terms |
| Tests | Behavior changes include tests or a documented reason for skipping |

## Security

Don't include secrets, private data links, credentials, or unpublished model
weights in public issues, PRs, or logs. See [SECURITY.md](SECURITY.md) for
private reporting.
