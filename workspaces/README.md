# Workspaces

`workspaces/` contains current lane state only. Historical dated notes and
closed verdicts live under `legacy/workspaces/`.

| Lane | Current entry | Archive |
| --- | --- | --- |
| Black-box | [black-box/README.md](black-box/README.md) | [../legacy/workspaces/black-box/2026-04/](../legacy/workspaces/black-box/2026-04/) |
| Gray-box | [gray-box/README.md](gray-box/README.md) | [../legacy/workspaces/gray-box/2026-04/](../legacy/workspaces/gray-box/2026-04/) |
| White-box | [white-box/README.md](white-box/README.md) | [../legacy/workspaces/white-box/2026-04/](../legacy/workspaces/white-box/2026-04/) |
| Implementation | [implementation/README.md](implementation/README.md) | [../legacy/workspaces/implementation/2026-04/](../legacy/workspaces/implementation/2026-04/) |
| Intake | [intake/README.md](intake/README.md) | [../legacy/workspaces/intake/2026-04/](../legacy/workspaces/intake/2026-04/) |
| Runtime | [runtime/README.md](runtime/README.md) | Current-only workspace. |

Rules:

- Keep `README.md` and `plan.md` short.
- Put new closed dated verdict notes in `legacy/workspaces/<lane>/<date>/`.
- Put shared executable code in `src/diffaudit/`, not in workspace notes.
- Put large local assets under `<DIFFAUDIT_ROOT>/Download/` or ignored
  workspace asset directories, not in Git.
