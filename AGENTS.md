# Research Agent Guide

This file is the operating guide for agents and teammates working in `Research/`.

## Authority

This file is subordinate to `<DIFFAUDIT_ROOT>/AGENTS.md` (root governance charter).
The root AGENTS.md defines directory boundaries, agent organization, release policy,
and cross-repo coordination rules. This file governs Research-specific operations
and may refine or override root defaults for Research-only concerns.

Naming conventions are jointly governed by this file and
`../Docs/NAMING_CONVENTIONS.md` (canonical for all DiffAudit directories).
Where this file is silent on naming, `Docs/NAMING_CONVENTIONS.md` applies.
Where this file specifies Research-only naming rules (script names, evidence doc
names, workspace structure), this file takes priority within Research/.

S.U.P.E.R. principles are defined canonically in this file (Section "Governance
Rules → S.U.P.E.R Principles"). Root `AGENTS.md` Section 五 points here as the
canonical source.

## Repository Role

`Research/` holds research code, configs, experiment status, and
results for diffusion-model privacy auditing. Product UI is in
`Platform/`; job scheduling is in `Runtime-Server/`.

## Fresh-Session Intake

Read in this order:

1. `<DIFFAUDIT_ROOT>/ROADMAP.md`
2. `<DIFFAUDIT_ROOT>/Research/ROADMAP.md`
3. `<DIFFAUDIT_ROOT>/Research/README.md`
4. `<DIFFAUDIT_ROOT>/Research/docs/README.md`
5. `<DIFFAUDIT_ROOT>/Research/docs/start-here/getting-started.md`
6. `<DIFFAUDIT_ROOT>/Research/docs/evidence/reproduction-status.md`
7. `<DIFFAUDIT_ROOT>/Research/docs/product-bridge/README.md`
8. `<DIFFAUDIT_ROOT>/Research/docs/governance/research-governance.md`
9. `<DIFFAUDIT_ROOT>/Docs/archive/Research/docs/rebuild/codebase-rebuild-plan.md`
10. `<DIFFAUDIT_ROOT>/Research/docs/evidence/workspace-evidence-index.md`
11. The relevant `workspaces/<direction>/README.md` and `plan.md`

Note: `docs/start-here/` files may be stale. A freshness check runs as part of the
weekly CI job (`scripts/util/run_docs_checks.py`). If docs/start-here/ files are
flagged as >30 days stale, refresh them before relying on their content for a new
session.

Do not start from memory or old chat context. Re-anchor on repository files.

## Active Research Direction

Paper 1 (DiffAudit MIA Audit) is in Phase G: H1/DAAB run-dynamics
replication. The active scientific question is whether activation-level
membership evidence is controlled mainly by training trajectory / run
identity.

Start from:
1. `ROADMAP.md` — current task board and evidence baseline
2. `docs/start-here/phase-g-runbook-2026-06-30.md` — operational commands
3. `docs/evidence/ddpm-750k-step-matched-control-2026-06-25.md` — Phase G evidence packet
4. `docs/paper1/frozen-claim-matrix.md` — canonical claim registry

Default CUDA environment: see `docs/start-here/phase-g-runbook-2026-06-30.md`.

Closed lines (do not reopen without explicit user decision):
- H2 same-cache sweeps, C14 metadata expansion, scnet/DCU matrices
- Beans, Fashion-MNIST, MIDST, CommonCanvas, ReDiffuse repeats
- Retrace-Baseline watermark work (frozen by collaborator)
- defense-transfer claims (separate repository)

Historical artifact-gate decisions for candidate methods are recorded
in `docs/evidence/experiment-master-log.md`.

## Research Rules

- Paper reproduction is a starting point, not the full project.
- Every experiment needs a hypothesis, data plan, expected result, and conclusion.
- Experiments must be hypothesis- and decision-value driven. Do not run
  experiments just to complete a narrative, fill a table, or make an ablation
  set look comprehensive; each run must answer a clear hypothesis or support a
  concrete decision.
- Stop low-marginal-information directions early. If a planned run is
  predictably unlikely to improve performance, change the directional decision,
  or unlock a better next step, especially when it only repeats an already
  established no-effect or infeasible verdict, record the reason and do not
  run an exhaustive validation.
- Report `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR` for promoted attack or
  defense results when applicable.
- DDPM/CIFAR10 results cannot be generalized to conditional-diffusion or
  commercial models without separate evidence.
- Candidate results must stay labeled as candidate-only until promoted through
  an evidence note and roadmap decision. Smoke tests are not benchmark results.
- Long autonomous runs must follow:
  `review -> select -> preflight -> run -> verdict -> docs -> next`.

### 运行实验原则：决策价值导向实验

1. 实验应以假设和决策价值为导向，而不是为了补齐口径、填满表格、让 ablation 看起来完整。实验必须回答一个明确假设，或支持一个真实路线决策。
2. 不在低边际信息增益的方向上穷举。当可以预见某组实验对性能提升、方向判断或后续改进都没有明显贡献，尤其只是重复确认"不可行 / 无效果"时，应立即停止，不做穷举式验证。

这条优先于"补实验完整性"的冲动。如果一个方向已经明显效果很差，不允许为了把消融表跑满而继续扩大条件矩阵；应记录最短有用结论，然后切换到更高价值问题。

## Research Taste Guard

Every cycle must start with a blunt self-check before adding code, validators,
docs, or experiments:

1. Am I discovering a new signal, testing portability, or changing a decision?
2. Or am I just adding another tool, artifact, validator, or long note around a
   direction we already know is blocked, weak, or candidate-only?
3. Would a good scientist stop here and switch direction?
4. Is this "差生文具多": more stationery, more process, more scaffolding, but
   no real model insight?

If the answer suggests tool-making or defensive writing rather than research,
stop and reselection is required. Do not create another CLI/validator/doc set
unless at least one is true:

- It gates a high-value experiment that is actually likely to run.
- It protects an admitted result that Platform/Runtime already consumes.
- It records a result that changes the project decision.
- It is the smallest way to prevent a known serious mistake.

Default behavior after a blocked or candidate-only verdict:

- Write the shortest useful conclusion.
- Do not keep polishing the dead end.
- Do not run another same-contract repeat unless it can change a decision.
- Move to a stronger question, preferably second asset / second response
  contract / second model scenario.

Current strategic correction:

- ReDiffuse target training/checkpoint-portability/score-norm repeats, I-B target-risk
  remap training, I-B GSA-only preflight expansion without PIA/contract
  approval, I-C translated replay,
  diagonal-Fisher repeats, GSA loss-score LR repeats, and mid-frequency
  same-contract repeats are not default next steps.
- The next high-value Research direction is a real second-asset or
  second-response-contract package, then simple, direction-setting tests before
  any complex fusion or new framework.

## Workspace Structure

Current research state lives in:

- `workspaces/black-box/`
- `workspaces/gray-box/`
- `workspaces/white-box/`
- `workspaces/implementation/`
- `workspaces/intake/`
- `workspaces/runtime/`
- `workspaces/cross-box/`
- `workspaces/defense/`
- `workspaces/xuchi-reproduction-20260516/`

Historical notes are in `legacy/workspaces/`. Don't add new dated logs to the
active workspace directories unless they are current summaries.

Use descriptive names like `Cross-box experiment boundary hardening` in active
docs, not run IDs.

## Public Documentation Rules

Public docs are for new contributors and external reviewers. They must not
contain personal machine paths, private operator instructions, raw agent prompts,
deadline pressure, or unverified product claims.

Use:

- `<DIFFAUDIT_ROOT>`
- `<DOWNLOAD_ROOT>`
- environment variables
- repository-relative paths

Run before pushing documentation or governance changes:

```powershell
python -X utf8 scripts/util/check_markdown_links.py
```

Note: `scripts/check_public_surface.py` has been superseded — use `scripts/util/run_pr_checks.py` for pre-commit enforcement of the public-only boundary.

## Subagent Policy

Subagents are optional. Use them for bounded side work such as paper scouting,
review, or implementation slices with explicit write scope. Read-only is the
default. The main agent owns roadmap truth and result promotion.

## Governance Rules (2026-06-20)

### S.U.P.E.R Principles

Every file, directory, and commit in this repository must satisfy five gates:

| Gate | Principle | Test |
|------|-----------|------|
| **S** | Single-purpose | One directory = one concern. No kitchen-sink folders. |
| **U** | Unambiguous naming | kebab-case, descriptive, no abbreviations that require a glossary. |
| **P** | Public-only surface | No internal hostnames, workstation paths, secrets, operator notes, or private progress in committed files. |
| **E** | Evidence-bound | Every claim in `docs/evidence/` links to a reproducible experiment with a dated evidence doc. |
| **R** | Reviewable | Every change is small enough for a reviewer to understand in one sitting. Commits are atomic. |

### Directory Structure

```
Research/
  AGENTS.md                  ← This file (public governance)
  ROADMAP.md                 ← Research roadmap (public)
  README.md                  ← Entry point for new contributors
  scripts/                   ← Executable experiment and utility scripts
    util/                    ← CI, pre-commit, and docs-check utility scripts
    {section}_{experiment}_{variant}.py  ← Naming convention for experiment scripts
  configs/                   ← Shared configuration (YAML)
    assets/                  ← Checkpoint registry, dataset manifests
      checkpoint-registry.yaml
  data/                      ← Git-ignored. Contains splits/ and datasets/
    splits/                  ← Train/val/test split manifests
  docs/                      ← Documentation (public, except docs/internal/)
    README.md
    evidence/                ← One evidence doc per experiment
    governance/              ← Governance and process documents
    start-here/              ← Onboarding documents (may be stale; refreshed by CI)
    product-bridge/          ← Research-to-Platform handoff artifacts
    internal/                ← Git-ignored. Local-machine-only planning.
  outputs/                   ← Git-ignored. Generated results, caches, logs.
  Download/                  ← Git-ignored. External asset acquisition cache.
  Archive/                   ← Git-ignored. Archived runs, figures, obsolete artifacts.
  workspaces/                ← Git-ignored. Active experiment workspaces.
    black-box/
    gray-box/
    white-box/
    cross-box/
    defense/
    implementation/
    intake/
    runtime/
    xuchi-reproduction-20260516/
  legacy/                    ← Historical notes and archived workspaces.
```

### Naming Conventions

- **Directories**: `kebab-case`, single purpose. No `PascalCase`, no `snake_case`, no spaces, no Chinese characters.
- **Scripts**: `{section}_{experiment}_{variant}.py`. Script names do NOT include dates — the date is recorded in the evidence doc produced by the script.
  - Example: `run_commoncanvas_denoising_loss.py`, `review_h2_output_cloud_geometry.py`
- **Evidence docs**: `{section}-{topic}-YYYY-MM-DD.md`
  - Example: `black-box-response-contract-acquisition-audit.md`, `rediffuse-stl10-bounded-scout-20260525.md`
- **All dated filenames**: `YYYY-MM-DD` (ISO 8601). `YYYYMMDD` is forbidden.
- **Config files**: `kebab-case.yaml`. Local overrides use `*.local.yaml` (git-ignored).

### Public-Only Boundary

This is a **public repository**. Every committed file must pass `scripts/check_public_surface.py`.

Forbidden in committed files:
- Absolute workstation paths (`C:\Users\...`, `/home/...`)
- Internal hostnames, IP addresses, or network topology
- Secrets, API keys, tokens, or credentials
- Operator-only instructions or raw agent prompts
- Private progress notes, deadlines, or collaborator aliases

Use instead:
- `<DIFFAUDIT_ROOT>` for the repository root
- `<DOWNLOAD_ROOT>` for the asset download cache
- Environment variable names (never values)
- Repository-relative paths

`docs/internal/` is explicitly git-ignored and exists only on the local machine. AGENTS.md and ROADMAP.md may reference `docs/internal/` paths that will 404 for anyone who has cloned the repository. This is by design — internal planning is not part of the public repository surface.

### Git Rules — Hygiene

Before every commit, run:

```bash
python -X utf8 scripts/util/run_pr_checks.py
```

Rules enforced:

1. **DO NOT commit training data.** `data/datasets/` is git-ignored. All of `data/` is git-ignored.
2. **DO NOT commit generated images.** `*.png` and `*.jpg` belong in `outputs/` or `Archive/`, both git-ignored.
3. **DO NOT commit paper PDFs.** Papers live in the separate `Papers/` monorepo. `papers/` is git-ignored.
4. **DO NOT commit model weights or checkpoints.** `*.pt`, `*.pth`, `*.ckpt`, `*.safetensors` are git-ignored.
5. **DO NOT commit secrets or local config.** `configs/*.local.yaml` and `.env` files are git-ignored.
6. **DO NOT rewrite history or force-push** without a separate approved audit.

### Git Rules — Workflow

1. Check `.gitignore` coverage before adding new file types.
2. `git status` before every commit — no accidental large binaries, no stray `data/` or `outputs/` files.
3. Commit atomically: one logical change per commit.
4. Push after every completed step; do not accumulate changes in the working tree.
5. No `git reset --hard` or destructive operations without explicit approval.

### Experiment Workflow

Every experiment follows this data flow:

```
Download/ → data/splits/ → scripts/ → outputs/ → docs/evidence/
```

Steps:

1. **Acquire**: External assets go into `Download/` (git-ignored).
2. **Split**: Create or verify train/val/test split manifests in `data/splits/`.
3. **Run**: Execute the experiment script from `scripts/`. Every script must produce a machine-readable result artifact in `outputs/`.
4. **Evidence**: Write exactly one evidence doc in `docs/evidence/` per experiment, following the evidence document template.
5. **Verdict**: The evidence doc must contain a one-sentence conclusion (Verdict header).

### Evidence Document Template

Every file in `docs/evidence/` MUST contain the following header fields:

```markdown
# {section}: {topic}

- **Date**: YYYY-MM-DD
- **Status**: draft | review | final | superseded
- **Verdict**: One-sentence conclusion.
```

`scripts/util/run_docs_checks.py` enforces this. A pre-commit hook rejects new `.md` files in `docs/evidence/` that are missing any of the three header fields.

### Script-Path Contract

All experiment scripts MUST use `configs/assets/checkpoint-registry.yaml` for checkpoint paths. Hardcoded absolute paths are forbidden. The pre-commit hook enforces this.

To reference a checkpoint:

```python
from diffaudit.utils.config import load_checkpoint_registry
registry = load_checkpoint_registry()
ckpt_path = registry["ddpm-cifar10-800k"]
```

### Stale Governance Check

Governance documents (`docs/governance/`) and onboarding documents (`docs/start-here/`) must be reviewed every 30 days. If a document is >30 days stale, the CI job `scripts/util/run_docs_checks.py` will flag it in a GitHub Issue.

To resolve a stale flag, the researcher must either:
- Update the document content and refresh its internal date marker, or
- Add an HTML comment marking the file as archived with a date:
  ```html
  <!-- archived: YYYY-MM-DD -->
  ```

### Enforcement — Pre-Commit Hook

The pre-commit hook (`scripts/util/run_pr_checks.py`) rejects:

| Violation | Rule |
|-----------|------|
| `YYYYMMDD` in filename | Only `YYYY-MM-DD` allowed in dated filenames |
| New `.py` in `scripts/` not in a subdirectory | Scripts must live in `scripts/{section}/` or `scripts/util/` |
| New `.md` in `docs/evidence/` without Date, Status, Verdict headers | Evidence doc template required |
| Hardcoded absolute paths in scripts | Use checkpoint registry or relative paths |
| Large files (>1 MB) staged for commit | Check `.gitignore` coverage |
| Stale governance docs (>30 days) | Update or archive |

### CI Job — Weekly Stale-Doc Check

A weekly CI job runs:

```bash
python -X utf8 scripts/util/run_docs_checks.py
```

This checks all governance and onboarding documents for staleness (>30 days since last update). Flagged documents are reported in a GitHub Issue titled "Stale governance documents — week of YYYY-MM-DD". The researcher must resolve each flag by updating the content or marking the file as archived before the next weekly check.
