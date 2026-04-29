# Research Repository Governance

> Scope: DiffAudit Research repository structure, asset boundaries, execution
> logs, and public-review hygiene.

This document defines how the repository stays reviewable while supporting
long-running research. It is intentionally separate from the research roadmap:
the roadmap chooses work; this document defines where work products belong.

## Current Governance Freeze

During the 2026-04-29 cleanup:

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- no new `X-181` experiment result should be created
- no history rewrite or force-push should be performed
- cleanup output should be PR-reviewable and reversible

## Directory Boundaries

| Path | Role | Git policy |
| --- | --- | --- |
| `docs/` | Stable documentation, onboarding, evidence maps, public-review material, and governance docs. | Commit curated Markdown, small durable diagrams, and metadata. Do not commit raw OCR dumps or generated extraction caches. |
| `workspaces/` | Lane plans, small evidence anchors, summaries, manifests, and reviewed research notes. | Commit `README`, `summary.json`, manifests, and verdict notes when they are small and useful. Do not commit datasets, weights, raw tensors, checkpoints, generated images, or full runtime dumps. |
| `scripts/` | Reusable maintenance, validation, setup, and replay helpers. | Keep reusable scripts here. One-off X-run scripts must move to the matching execution-log archive once their verdict is closed. |
| `external/` | Ignored upstream clones and local exploratory code checkouts. | Ignored by Git. Do not store datasets, weights, supplementary bundles, or generated results here. |
| `third_party/` | Minimal vendored subsets that the repo actually integrates with. | Commit only the smallest necessary code surface and notice/license context. Keep full upstream repos in `external/`. |
| `<DIFFAUDIT_ROOT>/Download/` | Raw datasets, model weights, paper/supplementary bundles, and large local intake assets. | Outside the `Research` Git repository. Recreate via manifests and handoff docs. |
| `legacy/execution-log/` | Archived run logs, closed X-anchor notes, and one-off scripts kept for traceability. | Commit only lightweight text/code artifacts needed to understand past decisions. Do not put large generated outputs here. |

## Artifact Policy

Commit:

- research verdict notes and small indexes
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

## Execution Log Rule

Hot-path files must stay short:

- `ROADMAP.md` holds current truth, next decision, and governance status.
- `workspaces/implementation/challenger-queue.md` holds active / ready / hold /
  needs-assets / closed candidate state.
- Long X-run timelines move to `legacy/execution-log/<date>/`.

Closed X-run scripts with names like `run_x145_*.py` should not remain in the
top-level `scripts/` directory unless they become reusable CLI surfaces or
generic replay helpers.

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
python scripts/verify_env.py
python -m diffaudit --help
python scripts/check_public_surface.py
```

For governance changes, also run or update:

```powershell
python scripts/run_local_checks.py
```

Skip GPU commands unless the PR explicitly changes a model-run contract and the
roadmap has released exactly one bounded GPU task.
