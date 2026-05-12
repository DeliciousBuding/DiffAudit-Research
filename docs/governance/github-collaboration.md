# GitHub Collaboration And Permissions

This document covers how to grant collaborators push access and the recommended
permission and branch-protection strategy.

Root-level GitHub settings baseline:

- [github-settings-baseline.md](github-settings-baseline.md)

## 1. Granting Push Access To Contributors

The direct approach is to add contributors as repository collaborators instead
of sharing your account.

On the GitHub web UI:

1. Open the repository `Settings`
2. Go to `Collaborators and teams`
3. Click `Add people`
4. Enter the contributor's GitHub username
5. Select a permission level

Recommended permissions:

- `Write`: suitable for most contributors; lets them push their own branches and open PRs
- `Maintain`: suitable for leads or core maintainers

Generally avoid granting:

- `Admin`

## 2. Recommended Team Collaboration Model

Recommended workflow:

- Everyone pushes to their own branch
- Nobody pushes directly to `main`
- All changes go through PRs merged into `main`

Benefits:

- No accidental overwrites between contributors
- Each research track can be reviewed independently
- Easy to trace and revert changes

## 3. Protecting The Main Branch

Enable branch protection for `main` in the repository settings.

Recommended rules:

- Block direct pushes to `main`
- Require Pull Request merges
- Require at least 1 review before merging
- Require the `unit-tests` status check

The `unit-tests` check has a fast path for documentation-only and
evidence-only PRs. It keeps the required status-check name stable, but skips
Conda setup unless the change touches code, tests, scripts, configs, tools, or
GitHub workflow files. This keeps research-note PRs cheap while preserving full
checks for executable changes.

For a smaller team, a lighter version works:

- Regular contributors go through the PR flow
- The owner can handle emergencies directly

## 4. Local Development Workflow

Each contributor:

1. Clones the repository
2. Creates a personal branch
3. Works in the relevant workspace and shared code directories
4. Commits changes
5. Pushes the branch
6. Opens a PR

Suggested branch naming:

- `black-box/<topic>`
- `white-box/<topic>`
- `gray-box/<topic>`
- `implementation/<topic>`

## 5. Configuring Git Identity For GitHub Avatars

The local git commit email must match a verified email on the GitHub account, or
use GitHub's noreply email.

Check current settings:

```powershell
git config user.name
git config user.email
```

Set local identity for this repository:

```powershell
git config user.name "Your GitHub name"
git config user.email "Your verified GitHub email"
```

Future commits will use the corrected identity. Past commits keep their original
identity; fixing those requires rewriting history and force-pushing, which needs
careful coordination.

## 6. Recommendations For This Repository

Current recommended setup:

- You are the repository owner
- Add core contributors as collaborators with `Write` permission
- Protect `main` with branch rules
- Merge all changes through PRs after one human review and a passing `unit-tests` check

Additional notes:

- Repository-level Copilot review instructions live in `Research/.github/copilot-instructions.md`
- Copilot acts as a first-pass static check, not the final reviewer
