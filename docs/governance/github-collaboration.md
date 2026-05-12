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

The required `unit-tests` check is intentionally a fast PR gate. It runs public
documentation guards, Markdown link checks, Python syntax compilation, and a CLI
parser smoke without installing PyTorch or executing runtime tests. This keeps
PR iteration short and stable.

Full validation is still available, but it is not the default PR bottleneck:

- `full-checks` runs automatically after merges to `main`
- `full-checks` can be triggered manually with `workflow_dispatch`
- local behavior-changing PRs should run `python -X utf8 scripts/run_local_checks.py --fast`

This split keeps the required status-check name stable while moving heavyweight
dependency installation and runtime tests out of every PR commit.

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
