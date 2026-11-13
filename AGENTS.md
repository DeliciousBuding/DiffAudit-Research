# Research Agent Guide

Subordinate to `<DIFFAUDIT_ROOT>/AGENTS.md` for workspace coordination; naming follows this file within `Research/` and `../Docs/NAMING_CONVENTIONS.md` across DiffAudit. `Research/` holds research code, configs, experiment status, and evidence for diffusion-model privacy auditing (`Platform/` owns UI; `Runtime-Server/` owns job scheduling).

## Fresh-Session Intake

Read in order:

1. `<DIFFAUDIT_ROOT>/AGENTS.md` and `<DIFFAUDIT_ROOT>/ROADMAP.md` (when in the full DiffAudit workspace)
2. `ROADMAP.md` — board status and claim boundaries
3. `README.md` · `docs/README.md`
4. `docs/start-here/paper1-corrected-evidence-runbook-2026-07-11.md` — closed protocol record (replay only)
5. `docs/paper1/frozen-claim-matrix.md` — claim registry and quarantine boundary
6. `docs/evidence/experiment-master-log.md` — experiment verdict ledger
7. Relevant `workspaces/<direction>/README.md` and `plan.md` only when reopening a non-Phase-G direction

Do not start from memory, archived rebuild plans, or old chat context. Check `docs/start-here/` against `ROADMAP.md` before relying on older onboarding prose.

## Active Research Direction

Paper 1 corrected-evidence matrix is **closed (2026-07-18, Route C)**. Historical Phase G targets and the resubstitution H1 scorer remain permanently quarantined. Admitted claim ceiling is **audit-failure / non-reproduction only** — not positive membership recovery, run-identity heterogeneity, or seed-population variance.

**Default work in this repo**: ledger hygiene, public-safe docs alignment, and exploratory packaging that does **not** upgrade claims (matrix-closed does not freeze all DiffAudit science).

**Not blocked by this board**:
- black-box defense transfer (line B) lived in a sibling `defense-transfer/` repository, which was **lost in a local workspace incident on 2026-08-04** (no remote backup). Rebuilding it is pending an explicit decision; until then there is **no live line-B work**, and nothing may mutate this evidence ledger in its name.
- private manuscript packaging under `Papers/` only after the user's venue phrase.

**Hard stops**:
- No formal relaunch, held-back seeds, >200k steps, or 0.55 threshold change without a new pre-registered protocol and explicit authorization.
- Default CUDA env for historical replay: corrected-evidence runbook (not a live formal resume checklist). For any future GPU experiment work use the `diffaudit` conda env.

**Closed lines (do not reopen without explicit user decision)**:
- H2 same-cache sweeps, C14 metadata expansion, scnet/DCU matrices
- Beans, Fashion-MNIST, MIDST, CommonCanvas, ReDiffuse repeats (target training, checkpoint portability, score norm), I-B/I-C same-contract repeats, diagonal-Fisher / mid-frequency repeats
- Retrace-Baseline watermark work (frozen by collaborator) and `defense-transfer` claims
- Prior literature baseline context: Bonnaire et al. (NeurIPS 2025, arXiv:2505.17638), SoK (PoPETs 2023), CopyMark (arXiv:2410.03640), MIA reliability (IBM 2025), GAN-Leaks (CCS 2020), TrajectoryMIA (CCS 2022), Gu et al. (arXiv:2310.02664); keep mechanism language blocked unless directly tested.

## Decision-Value & Taste Guard

1. Every experiment requires a hypothesis, data plan, expected result, and verdict (`AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR` for promoted attack/defense results; smoke tests are not benchmarks and candidate results remain candidate-only until promoted).
2. **Decision-value over completeness**: Stop early when a run repeats an already established no-effect/infeasible verdict or cannot change a directional decision — record the shortest useful conclusion and pivot rather than filling ablation grids.
3. **No busywork scaffolding**: Do not create extra validators, tools, or long notes around blocked/candidate-only directions unless they gate a high-value run, protect an admitted result, record a decision-changing verdict, or prevent a concrete failure mode.

## Public-Only & Workspace Boundaries

`Research/` is a **public repository** enforced by `scripts/util/check_public_surface.py` and [docs/governance/research-governance.md](docs/governance/research-governance.md) (authoritative for directory boundaries, naming conventions, artifact policy, evidence schema, and checkpoint registry usage via `load_checkpoint_registry()`).

- Forbidden in committed files: workstation paths, internal hostnames/IPs, secrets, collaborator aliases, operator prompts/deadlines, training data (`data/`), images (`*.png`/`*.jpg`), paper PDFs, and checkpoints/weights (`*.pt`/`*.pth`/`*.ckpt`/`*.safetensors`).
- Use `<DIFFAUDIT_ROOT>`, `<DOWNLOAD_ROOT>`, env vars, or repo-relative paths. `docs/internal/` is local-only and git-ignored (404s in public clones by design).
- Active track state lives in `workspaces/{black-box,gray-box,white-box,implementation,intake,runtime,cross-box,defense}/`; historical notes belong in `legacy/workspaces/`. Use descriptive titles in active docs rather than internal run IDs.

## Verification Before Commit

```powershell
python -X utf8 scripts/util/run_pr_checks.py
python -X utf8 scripts/util/check_markdown_links.py
```

Commit atomically with descriptive messages; keep `.gitignore` aligned with `Download/`, `outputs/`, `data/`, and generated run artifacts; never rewrite history or force-push without explicit approval.
