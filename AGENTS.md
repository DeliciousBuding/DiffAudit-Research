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

- Active work: `Paperization consumer boundary synchronized; CommonCanvas packet closed by default after weak pixel/CLIP/prompt/stability/denoising-loss scouts; known-split gradient-prototype follow-up weak; MIDST TabDDPM nearest-neighbor and shadow-distributional scouts weak; Beans member-LoRA denoising-loss and parameter-delta sensitivity scouts weak; Quantile Regression is mechanism-reference but artifact-incomplete`
- Next GPU candidate: none selected
- Long-horizon control: follow `ROADMAP.md` section
  `Long-Horizon Research Task Board（2026-05-13 起）` before reopening any
  Research lane. The selected forward path is Lane A external asset acquisition
  watch unless a genuinely new mechanism family satisfies the same gates; do
  not create another scope/audit/reselection chain when no candidate passes
  target identity, exact member/nonmember split, query/response coverage, and
  non-adjacent mechanism checks.
- Continuous-run discipline: use the roadmap loop
  `Anchor -> Select -> Execute -> Reflect -> Archive -> Merge` for every
  autonomous cycle. Each cycle must name exactly one primary artifact type
  (`asset verdict`, `metric verdict`, `consumer verdict`, or
  `roadmap operating-system update`), update the three slots
  `active_gpu_question` / `next_gpu_candidate` / `CPU sidecar`, and close with
  a clean `main` after PR/merge when repository files change.
- Reflection/correction discipline: enforce the No-stationery, Two-weak-runs,
  Membership semantics, Response contract, Consumer honesty, and stale-doc
  conflict gates from `ROADMAP.md`. If a step only adds process around a weak
  lane, stop or switch lanes instead of adding another scope/audit chain.
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
  `16 / 64` stability gate weakens that result to `AUC = 0.535156`. The
  2026-05-13 `64 / 64` oracle-style final-layer gradient prototype alignment
  follow-up is also weak (`AUC = 0.500977`, zero low-FPR recovery), so
  same-family final-layer gradient norm/cosine variants are closed by default
  and do not release GPU or layer sweeps. A quick external
  diffusion benchmark scan did not find a ready target whose model card alone
  proves exact member/nonmember provenance. CopyMark is now the highest-value
  external intake candidate because its paper-level protocol is explicitly about
  diffusion membership/copyright detection. Its diffusers README, scripts, and
  zip central directory now show a concrete directory-level member/holdout
  contract with `eval` and `test` splits, but the archive itself carries only
  images plus `caption.json` fields (`path`, `height`, `width`, `caption`), not
  per-row membership provenance. A local
  `response-contract-copymark-commoncanvas-20260512` query split exists under
  `<DIFFAUDIT_ROOT>/Download` with `50` CommonCatalog member queries and `50`
  COCO holdout queries. The `diffaudit-research` conda environment has CUDA
  Torch (`cu121`) and can see the local RTX 4070 Laptop GPU; do not confuse the
  default PATH CPU-only Python with the actual research environment. The
  `common-canvas/CommonCanvas-XL-C` single checkpoint has been downloaded, a
  CUDA smoke passed, deterministic `50/50` text-to-image responses were
  generated, and the package probe returns `ready`. The first simple scorer
  `negative_pixel_mse_resized_512` is weak (`AUC = 0.5736`, `ASR = 0.6000`,
  `TPR@1%FPR = 0.04`, `TPR@0.1%FPR = 0.04`). The only approved sharper
  response-vs-query similarity follow-up, `clip_vit_l14_query_response_cosine`,
  is weaker (`AUC = 0.4588`, `ASR = 0.5300`, zero low-FPR recovery). The
  distinct prompt-response consistency scorer is also weak (`AUC = 0.4408`,
  `ASR = 0.5100`, `1 / 50` member recovered at zero false positives). A bounded
  multi-seed response-distribution stability scout on `4 / 4` prompts and two
  fixed seeds is also weak (`AUC = 0.5625`, `ASR = 0.625`, `1 / 4` zero-FP
  recovery), so do not expand it into seed, subset, or embedding-metric sweeps.
  A genuinely different CommonCanvas conditional denoising-loss scout on the
  existing `50/50` packet is also weak (`AUC = 0.5148`, `ASR = 0.5700`,
  `TPR@1%FPR = 0.02`), so do not expand it into timestep, resolution,
  scheduler, seed, loss-weight, or subset matrices.
  This is not admitted and does not trigger Platform/Runtime consumption. Do
  not expand this into a CLIP/pixel/LPIPS/prompt-adherence/stability metric
  or denoising-loss matrix by default; close the current CommonCanvas packet unless a genuinely
  new mechanism or new asset is proposed. Do not return to I-B remap training,
  Beans distance variants,
  MNIST raw/x0 residual repeats, tiny-denoiser MSE ablations, final-layer
  gradient norm/cosine variants, external-weight downloads without provenance,
  full CopyMark dataset download, CommonCanvas multi-seed stability repeats,
  MIDST nearest-neighbor variants, gradient layer sweeps, or same-contract
  residual repeats by default. Kohaku
  XL / Danbooru is also not a selected
  next asset: model cards give broad HakuBooru/Danbooru2023 training-source
  provenance, but no exact target member list or fixed selection manifest. Do
  not download `38-40 GB` Kohaku weights or TB-scale Danbooru image assets for
  pseudo-membership scoring. A small Fashion-MNIST DDPM PIA-style loss scout
  on `ynwag9/fashion_mnist_ddpm_32` used a real Fashion-MNIST train/test split
  and CUDA, but remained weak (`AUC = 0.535889`, `TPR@1%FPR = 0.03125`);
  do not expand it into seed, timestep, or packet-size sweeps. MIDST TabDDPM
  black-box single-table is locally scoreable and has exact member/nonmember
  labels, but the minimal nearest-synthetic-row scorer is weak
  (`dev+final AUC = 0.566263`, `TPR@1%FPR = 0.016750`). A genuinely different
  shadow-trained marginal-distributional classifier overfits the `train`
  shadow folders (`AUC = 0.881991`) but collapses on dev+final
  (`AUC = 0.499846`, `TPR@1%FPR = 0.013000`). Do not expand MIDST into TabSyn,
  white-box MIDST, nearest-neighbor preprocessing matrices, classifier sweeps,
  or marginal feature matrices unless a genuinely different tabular-diffusion
  membership mechanism appears. A bounded Beans member-LoRA scout repaired the
  old pseudo-membership semantics by creating an exact target
  (`SD1.5 + Beans-member UNet LoRA`) and holding out `25` nonmembers, but
  conditional denoising-loss is weak (`AUC = 0.414400`, reverse `0.585600`,
  `TPR@1%FPR = 0.080000`) and parameter-delta sensitivity is also weak
  (`AUC = 0.512000`, `TPR@1%FPR = 0.040000`). Do not expand Beans LoRA
  train-step, rank, resolution, prompt, scheduler, loss-weight, timestep,
  layer, or block matrices by default.
  Quantile Regression is a useful sample-conditioned reconstruction-loss
  mechanism reference, but it is not a runnable packet: no paper-specific
  public code, exact target artifact bundle, per-sample split manifest, or
  ready t-error packet was found. Do not train STL10/Tiny-ImageNet DDPMs,
  reconstruct SecMI splits, or build a quantile-regression implementation from
  scratch before those artifacts exist.
- Paperization/consumer boundary: recent weak/watch lines, including
  CommonCanvas, MIDST, Beans LoRA, Quantile Regression, MIAGM, LAION-mi,
  Zenodo fine-tuned diffusion, Noise as a Probe, and Kohaku/Danbooru, are
  limitations or future-work hooks only. Platform/Runtime and paperization
  admitted claims still use only `recon`, `PIA baseline`, `PIA defended`,
  `GSA`, and `DPDM W-1`.
- ReDiffuse is closed as candidate-only / hold unless a new scorer or
  checkpoint-portability hypothesis appears.
- No GPU task should start from documentation or governance cleanup alone.
- Only one GPU task may run at a time; every GPU task needs a frozen command,
  metric contract, stop condition, and evidence-note target.
- CPU-first means "cheaply prove the contract before spending GPU", not
  CPU-only or GPU avoidance. When a real asset, clear membership semantics,
  fixed query split, metric contract, and stop condition exist, prefer a
  bounded GPU packet over more documentation, validators, or environment
  excuses. A local RTX 4070 sitting idle while the agent writes more prose is a
  research failure, not prudence.
- Before declaring GPU blocked, probe the actual CUDA-capable environments,
  especially `conda run -n diffaudit-research python -X utf8 -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"`.
  Do not infer GPU unavailability from the default PATH Python alone.
- Hugging Face CLI is available in the `diffaudit-research` environment and
  should be treated as the normal asset-acquisition path when a model card,
  gated repo, or checkpoint needs verification. Do not write tokens into docs
  or scripts; if auth is uncertain, check `hf auth whoami` inside the research
  environment before claiming that an asset is inaccessible.
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
