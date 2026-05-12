# Research Agent Guide

This file is the operating guide for agents and teammates working in `Research/`.

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
9. `<DIFFAUDIT_ROOT>/Research/docs/rebuild/README.md`
10. `<DIFFAUDIT_ROOT>/Research/docs/evidence/workspace-evidence-index.md`
11. The relevant `workspaces/<direction>/README.md` and `plan.md`

Do not start from memory or old chat context. Re-anchor on repository files.

## Current Operating State

- Active work: `CopyMark manifest inspected; choose one tiny CPU subset target`
- Next GPU candidate: none selected
- CPU work: stop expanding blocked or pseudo-membership routes. Beans/SD1.5 is
  contract/debug only because beans train/validation is not proven SD1.5
  membership. MNIST/DDPM via `1aurent/ddpm-mnist` has cleaner train/test
  membership semantics, but raw PIA-style loss and simple `x0`
  reconstruction residuals are weak. A tiny controlled MNIST denoiser with a
  real train/held-out split also failed under raw denoising loss despite
  decreasing training loss; a deliberately overfit `8`-member upperbound still
  produced only weak raw-MSE AUC and zero low-FPR recovery. A final-layer
  per-sample gradient-norm scout on that same overfit target is positive
  (`AUC = 0.734375`, `1 / 8` members recovered at zero false positives), so the
  next mechanism candidate became gradient-sensitive, not MSE. The less extreme
  `16 / 64` stability gate weakens that result to `AUC = 0.535156`, so it is a
  mechanism hint only and does not release GPU or layer sweeps. A quick external
  diffusion benchmark scan did not find a ready target whose model card alone
  proves exact member/nonmember provenance. CopyMark is now the highest-value
  external intake candidate because its paper-level protocol is explicitly about
  diffusion membership/copyright detection. Its diffusers README, scripts, and
  zip central directory now show a concrete directory-level member/holdout
  contract with `eval` and `test` splits, but the archive itself carries only
  images plus `caption.json` fields (`path`, `height`, `width`, `caption`), not
  per-row membership provenance. The current reducible work is a tiny CPU-only
  CommonCanvas/CommonCatalog subset first, because that pairing has cleaner
  open-model/open-data provenance than SD1.5/LAION. Fall back to a sharper
  observable than final-layer gradient L2 only if CopyMark target provenance
  blocks. Do not return to I-B remap training, Beans distance variants, MNIST
  raw/x0 residual repeats, tiny-denoiser MSE ablations,
  external-weight downloads without provenance, full CopyMark dataset download
  before a tiny target is frozen, gradient layer sweeps, or same-contract
  residual repeats by default.
- ReDiffuse is closed as candidate-only / hold unless a new scorer or
  checkpoint-portability hypothesis appears.
- No GPU task should start from documentation or governance cleanup alone.
- Only one GPU task may run at a time; every GPU task needs a frozen command,
  metric contract, stop condition, and evidence-note target.
- No history rewrite or force-push without a separate approved audit.

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
2. 不在低边际信息增益的方向上穷举。当可以预见某组实验对性能提升、方向判断或后续改进都没有明显贡献，尤其只是重复确认“不可行 / 无效果”时，应立即停止，不做穷举式验证。

这条优先于“补实验完整性”的冲动。如果一个方向已经明显效果很差，不允许为了把消融表跑满而继续扩大条件矩阵；应记录最短有用结论，然后切换到更高价值问题。

## Research Taste Guard

Every cycle must start with a blunt self-check before adding code, validators,
docs, or experiments:

1. Am I discovering a new signal, testing portability, or changing a decision?
2. Or am I just adding another tool, artifact, validator, or long note around a
   direction we already know is blocked, weak, or candidate-only?
3. Would a good scientist stop here and switch direction?
4. Is this “差生文具多”: more stationery, more process, more scaffolding, but
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

- ReDiffuse 800k, I-B target-risk remap training, I-C translated replay,
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
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
```

## Subagent Policy

Subagents are optional. Use them for bounded side work such as paper scouting,
review, or implementation slices with explicit write scope. Read-only is the
default. The main agent owns roadmap truth and result promotion.
