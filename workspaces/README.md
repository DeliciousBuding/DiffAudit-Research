# Workspaces

`workspaces/` contains the current state of each research direction. Archived
notes and closed experiment records are in `legacy/workspaces/`.

| Direction | Entry point | Archive |
| --- | --- | --- |
| Black-box | [black-box/README.md](black-box/README.md) | [../legacy/workspaces/black-box/2026-04/](../legacy/workspaces/black-box/2026-04/) |
| Gray-box | [gray-box/README.md](gray-box/README.md) | [../legacy/workspaces/gray-box/2026-04/](../legacy/workspaces/gray-box/2026-04/) |
| White-box | [white-box/README.md](white-box/README.md) | [../legacy/workspaces/white-box/2026-04/](../legacy/workspaces/white-box/2026-04/) |
| Implementation | [implementation/README.md](implementation/README.md) | [../legacy/workspaces/implementation/2026-04/](../legacy/workspaces/implementation/2026-04/) |
| Intake | [intake/README.md](intake/README.md) | [../legacy/workspaces/intake/2026-04/](../legacy/workspaces/intake/2026-04/) |
| Runtime | [runtime/README.md](runtime/README.md) | Current-only workspace. |

Rules:

- Keep `README.md` and `plan.md` short and current.
- Archive closed experiment notes under `legacy/workspaces/<direction>/<date>/`.
- Put shared code in `src/diffaudit/`, not in workspace notes.
- Put large data files under `<DIFFAUDIT_ROOT>/Download/` or git-ignored
  workspace directories, not in Git.
