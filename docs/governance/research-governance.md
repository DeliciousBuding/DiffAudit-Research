# Research Repository Governance

> Scope: DiffAudit Research repository structure, asset boundaries, execution
> logs, and public-review hygiene.

This document defines how the repository stays reviewable while supporting
long-running research. It is separate from the research roadmap: the roadmap
chooses work; this document defines where work products belong.

## Current Governance Baseline

The 2026-04-29 and 2026-04-30 governance cleanups are merged to `main`
from PR #26 through PR #36. The ongoing baseline is:

- Active work is `temporary resting state: needs external assets or new hypothesis`
- Next GPU candidate is none selected
- Current CPU sidecar is none currently reducible
- ReDiffuse is a candidate gray-box baseline-alignment track, not an admitted
  result release; reopen only with a new scorer or checkpoint-portability
  hypothesis
- The black-box response-contract lane is blocked on a second asset package
  matching the acquisition spec
- No history rewrite or force-push should be performed without separate approval
- Future cleanup output should be PR-reviewable and reversible
- Research is deployable as a conda/editable Python package and CLI research
  surface; HTTP service deployment belongs to `Runtime-Server/` and
  user-facing deployment belongs to `Platform/`

## Directory Boundaries

| Path | Role | Git policy |
| --- | --- | --- |
| `docs/` | Stable documentation, onboarding, evidence maps, public-review material, and governance docs. | Commit curated Markdown, small durable diagrams, and metadata. Do not commit raw OCR dumps or generated extraction caches. |
| `workspaces/` | Research-track plans, small evidence anchors, summaries, manifests, and reviewed research notes. | Commit `README`, `summary.json`, manifests, and result notes when they are small and useful. Do not commit datasets, weights, raw tensors, checkpoints, generated images, or full runtime dumps. |
| `scripts/` | Reusable maintenance, validation, setup, and replay helpers. | Keep reusable scripts here. One-off run scripts must move to the matching execution-log archive once their result is closed. |
| `external/` | Ignored upstream clones and local exploratory code checkouts. | Ignored by Git. Do not store datasets, weights, supplementary bundles, or generated results here. |
| `third_party/` | Minimal vendored subsets that the repo actually integrates with. | Commit only the smallest necessary code surface and notice/license context. Keep full upstream repos in `external/`. |
| `<DIFFAUDIT_ROOT>/Download/` | Raw datasets, model weights, paper/supplementary bundles, and large local intake assets. | Outside the `Research` Git repository. Recreate via manifests and integration docs. |
| `legacy/execution-log/` | Archived run logs, closed X-anchor notes, and one-off scripts kept for traceability. | Commit only lightweight text/code artifacts needed to understand past decisions. Do not put large generated outputs here. |

## Artifact Policy

Commit:

- research result notes and small indexes
- reproducibility contracts
- `summary.json` files that are small enough to review
- manifests and metadata describing local assets
- reusable scripts and tests
- small brand assets and canonical report figures

Do not commit:

- datasets, weights, checkpoints, optimizer state, or raw supplementary bundles
- generated images from experiments
- raw score tensors, `.npy`, `.npz`, `.pt`, `.pth`, `.ckpt`, `.safetensors`
- large runtime job dumps or stdout/stderr logs
- paper OCR dumps, full extracted paper Markdown, or temporary page JSON
- machine-specific absolute paths or private local storage locations

If an artifact is needed for reproduction but too large or license-sensitive for
Git, record it in the relevant manifest and put the local copy under
`<DIFFAUDIT_ROOT>/Download/` or a team asset mirror.

## Ignore Rule Invariant

No Git-tracked file should be hidden by `.gitignore`.

This is a hard hygiene rule. If a curated summary, manifest, provenance file,
or result is committed, future edits must show up in `git status`. Broad ignore
rules such as `/outputs/`, `/runs/`, and `/artifacts/` should therefore be
root-anchored unless the intent is explicitly to ignore the same directory name
everywhere. Workspace run directories are the main exception: they remain
ignored as local scratch by default, and any committed run evidence inside them
must be explicitly re-included by the repository ignore rules.

The top-level `outputs/` directory is a local generated-output layer. It may
contain checkpoints, logs, weights, and temporary evaluation files, but it is
not a canonical evidence anchor. Promote durable results into workspace result
notes, `workspaces/<track>/runs/<run>/summary.json`, or another curated
workspace artifact before committing.

## Execution Log Rule

Active files must stay short:

- `ROADMAP.md` holds current truth, next decision, and governance status.
- `workspaces/implementation/challenger-queue.md` holds active / ready / hold /
  needs-assets / closed candidate state.
- Long run timelines move to `legacy/execution-log/<date>/`.

Closed one-off run scripts should not remain in the top-level `scripts/`
directory unless they become reusable CLI surfaces or generic replay helpers.

Internal execution identifiers may remain in legacy archives for traceability,
but public docs should use descriptive track names instead of run IDs.

## Portability And Deployment Boundary

Research must remain portable across machines by using repository-relative
paths, `team.local.yaml`, `<DIFFAUDIT_ROOT>`, `<DOWNLOAD_ROOT>`, and documented
asset manifests. It should not require the original maintainer's drive layout
or personal shell profile.

Research is not the production HTTP service. The supported local runtime shape
is:

- install the conda environment;
- install the repository as an editable Python package;
- bind local assets through ignored local config;
- run `diffaudit` CLI commands and validation scripts.

Runtime job orchestration, API serving, authentication, and user-facing
deployment are sibling-repository responsibilities. Research may emit experiment
summaries, manifests, and contract notes for those repositories, but it should
not document itself as a standalone deploy target.

## Public Surface Rule

The public front door is:

1. `README.md`
2. `docs/README.md`
3. onboarding, setup, data/assets, command, reproduction, licensing, security,
   and brand documents linked from `docs/README.md`

Those files must use product-facing or research-facing language. They should
not mention local operator instructions, personal machine paths, deadline
pressure, or raw agent prompts. Use `<DIFFAUDIT_ROOT>`, `<DOWNLOAD_ROOT>`,
environment variables, or repository-relative paths.

Internal planning files may remain in `docs/`, but they must be labeled and
should not be presented as product copy.

## Before Opening A PR

Run:

```powershell
git status --short
git diff --check
python -X utf8 scripts/verify_env.py
python -X utf8 -m diffaudit --help
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
```

The public-surface guard also fails if any tracked file is ignored by the
current `.gitignore` rules or if a tracked file exceeds the current repository
size threshold.

For governance changes, also run or update:

```powershell
python -X utf8 scripts/run_local_checks.py
```

Skip GPU commands unless the PR explicitly changes a model-run contract and the
roadmap has released exactly one bounded GPU task.
