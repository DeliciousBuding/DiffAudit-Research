# GitHub Settings Baseline

This document defines the GitHub backend settings baseline for the `Research`
repository.

Last synchronized: 2026-04-28.

## 1. Repository Identity

- Repository: `Research`
- Type: research and experiment repository
- Current visibility: `public`
- Description: `Reproducible research scaffolding for privacy-risk auditing of diffusion models.`
- Topics:
  - `diffusion-models`
  - `membership-inference`
  - `privacy-auditing`
  - `machine-learning-security`
  - `reproducibility`
  - `research`
  - `python`
- Goal: keep research assets, experiment code, paper reproduction, and status
  documents collaborative, without treating the research repository as a product
  repository

## 2. Repository-Level Settings

- Visibility: `public`
- Issues: `on`
- Projects: `on`
- Wiki: `off`
- Discussions: `off`
- Merge methods:
  - `squash`: `on`
  - `merge commit`: `off`
  - `rebase`: `off`
- Auto-merge: `on`
- Automatically delete head branches: `on`
- Always suggest updating pull request branches: `on`
- Web commit signoff required: `off`
- Release immutability: `off`

## 3. Main Branch Protection Baseline

- Require pull request: `on`
- Required status checks:
  - `unit-tests`
- Require branch up to date: `on`
- Require pull request review:
  - Current value: `off`
  - Recommended: enable once a second maintainer joins
- Required approval count:
  - Current value: `n/a`
  - Recommended: `1`
- Require CODEOWNERS review:
  - Current value: `off`
  - Recommended: enable once a second maintainer joins
- Dismiss stale reviews:
  - Current value: `off`
  - Recommended: enable once a stable review team is in place
- Require conversation resolution: `on`
- Enforce for admins: `on`
- Allow force pushes: `off`
- Allow deletions: `off`
- Require last push approval:
  - Recommended: `on`
  - Note: increases friction for the owner when merging small doc/governance PRs quickly

## 4. Copilot Review Baseline

Shared requirements:

- `Use custom instructions when reviewing pull requests`: `on`
- Repository-level instruction file:
  - `.github/copilot-instructions.md`

Copilot review in this repository should focus on:

- `src/diffaudit/`
- `tests/`
- `scripts/`
- `configs/`
- reproduction risk, path dependency, provenance, metric consistency, CLI/manifest regression

Copilot review should skip or deprioritize:

- `references/`
- PDF files
- long paper notes
- raw experiment output

## 5. Security Settings Baseline

- Dependency graph: `on`
- Dependabot alerts: `on`
- Dependabot security updates: `on`
- Secret scanning: `on`
- Push protection: `on`

Additional guidance:

- Version updates can be enabled, but keep the frequency moderate
- ML dependencies should not drift through frequent automated updates
- Dependabot version updates:
  - GitHub Actions: weekly
  - Python `pyproject.toml` runtime dependencies: weekly, grouped
  - Conda environment drift: manual review only

## 6. Auto-Merge

- `Allow auto-merge`: `on`

Requirements:

- Pass the `main` branch required checks
- Satisfy review rules
- Merge method: `squash` only

## 7. In-Repository Governance Files

- `SECURITY.md`
- `CITATION.cff`
- `LICENSE`
- `NOTICE`
- `CONTRIBUTING.md`
- `.github/dependabot.yml`
- `.github/ISSUE_TEMPLATE/*.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/copilot-instructions.md`

## 8. Issue And PR Labels

These labels should stay consistent with issue templates and Dependabot config:

- `docs`
- `reproducibility`
- `research`
- `dependencies`
- `github-actions`
- `python`

Default GitHub labels can stay, but documentation issues should use `docs` by
default, not `documentation`.

## 9. Items Requiring Manual Follow-Up

- Confirm that Copilot automatic review is enabled as expected
- Decide whether to enable CODEOWNERS review and stale-review dismissal once a
  second maintainer joins

## 10. Related Documents

- `CONTRIBUTING.md`
- `docs/governance/github-collaboration.md`
- `.github/copilot-instructions.md`
