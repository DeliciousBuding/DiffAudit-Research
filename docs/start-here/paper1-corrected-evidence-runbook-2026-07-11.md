# Paper 1 Corrected Evidence Runbook

> Date: 2026-07-11
> Status: active protocol repair; the first formal launch was stopped outcome-blind and must be restarted under a new sealed hash.

This runbook supersedes `phase-g-runbook-2026-06-30.md`. It rebuilds the H1
evidence contract after the previous local targets and resubstitution scorer
were quarantined. Historical seed42/43/45 checkpoints MUST NOT be resumed,
overwritten, or cited as corrected evidence.

## Scientific Scope

The primary question is whether H1 or a predeclared established MIA baseline
shows membership signal on newly trained member-only targets. Differences among
four specific targets are finite-target pilot evidence; they do not estimate a
population-level seed variance or establish training run identity as a dominant
mechanism.

## Frozen Matrix

- Stage 1: four predeclared training seeds, each to 100k steps.
- Interim analysis: futility/route selection only, never a confirmatory claim.
- If the predeclared signal gate passes: train four additional predeclared seeds
  to 100k, producing an exploratory four-target set plus an independent
  four-target validation set.
- If the result is non-futile but misses that gate: continue the original four
  targets symmetrically to 200k.
- If both H1 and PIA exclude AUC 0.55 from above for every target: stop.

The seed list, branch thresholds, row manifests, noise manifest, attack
configuration, and bootstrap seeds MUST be frozen before any corrected 100k
metric is viewed.

## Evidence-Contract Gates

Long training is blocked until all items pass:

1. The training dataset is a `Subset` of exactly 25,000 fixed member rows.
2. Member and nonmember indices are disjoint and the split SHA256 is recorded.
3. New output labels contain `corrected`; no historical directory is reused.
4. Training seed, code commit, environment, precision, hyperparameters, and
   checkpoint policy are written to a protocol manifest.
5. Exact resume restores Python, NumPy, Torch CPU/CUDA, and data-loader state,
   or a common restart policy is explicitly frozen and trajectory claims are
   disabled.
6. H1 uses disjoint fixed calibration and evaluation manifests. Each contains
   512 members and 512 nonmembers, stratified by CIFAR-10 class.
7. Evaluation noise is bound to dataset row, timestep, and draw and shared
   across all checkpoints.
8. PIA canonical passes a positive-control test before it is admitted as the
   validation attack. Historical E3 PIA outputs do not satisfy this gate.
9. Row-bound packets include dataset indices, labels, run/step, scores, noise
   IDs, checkpoint SHA256, split SHA256, code commit, and protocol hash.

## Environment Preflight

```powershell
conda activate diffaudit
$env:DIFFAUDIT_DOWNLOAD_ROOT = "<DIFFAUDIT_ROOT>\Download"
$env:DIFFAUDIT_CIFAR10_ROOT = "<CIFAR10_ROOT>"
$env:PYTHONPATH = (Resolve-Path src).Path
$protocolManifest = "<PROTOCOL_MANIFEST>"
$splitPath = "<SPLIT_PATH>"
$seed = <PREDECLARED_SEED>

python -X utf8 -m pytest tests/test_h1_evidence_contract.py -q
python -X utf8 training/ddpm-cifar10/train_ddpm_cifar10_corrected.py `
  --protocol-manifest $protocolManifest `
  --split-path $splitPath `
  --seed $seed `
  --run-label "corrected-preflight-s$seed" `
  --stop-step 2000 `
  --dataset-root $env:DIFFAUDIT_CIFAR10_ROOT `
  --num-workers 4 `
  --preflight `
  --dry-run
```

The dry run is not enough. Run a disposable 2k--5k-step target after the
protocol manifest exists, then record peak VRAM, sustained steps/hour,
temperature, checkpoint/resume behavior, and output-schema completeness.

Before any corrected metric is viewed, benchmark one complete checkpoint
evaluation and project the worst non-STOP branch including a 10% failure
buffer. If the projection exceeds the available GPU window, reduce the step
horizon or target matrix symmetrically and freeze the revised manifest first.
Never drop a target after seeing its score because the budget became tight.

Stop preflight on OOM, sustained throughput below 6.0k steps/hour, thermal
throttling, split mismatch, missing row IDs, or resume mismatch.

### Current preflight result (2026-07-12)

- The first frozen batch-64 attempt was stopped before completion: the observed
  GPU allocation reached about 7.9 GiB on an 8 GiB device and 2,000 steps had not
  completed after about 22 minutes.
- Before any corrected metric was viewed, the single canonical training config
  was revised to batch size 32 and the protocol was rebuilt.
- The replacement run used the same first predeclared seed and completed
  `0 -> 200 -> 400 -> 2,000`, including two exact-resume launches.
- Active segment time was 583 seconds for 2,000 steps, about 12.3k steps/hour.
  Observed peak allocation was about 6.74 GiB during resume, with at least about
  1.21 GiB free. The observed maximum temperature was 71 C.
- Checkpoints at steps 200, 400, and 2,000 have matching SHA256 receipts,
  protocol identity, training config, seed, and step metadata.

This passes the training portion of Stage 0. Long training is still blocked
until one full checkpoint H1 + PIA evaluation is timed and the protocol-bound H1
activation extractor emits a valid row-bound packet. No corrected AUC or other
membership outcome has been inspected.

## Training Template

Use only values from the frozen protocol manifest:

```powershell
python -u training/ddpm-cifar10/train_ddpm_cifar10_corrected.py `
  --protocol-manifest $protocolManifest `
  --split-path $splitPath `
  --seed $seed `
  --run-label "corrected-s$seed" `
  --stop-step 100000 `
  --dataset-root $env:DIFFAUDIT_CIFAR10_ROOT `
  --num-workers 4 `
  --log-file "training/outputs/corrected-s$seed/training-100k.log"
```

Never pass `--resume` against `ddpm-cifar10-seed42`, `seed43`, `seed44`,
`seed45`, `ddpm-cifar10-750k`, or any other historical target.

If the MATURE branch is selected, resume only after the exact-resume gate:

```powershell
python -u training/ddpm-cifar10/train_ddpm_cifar10_corrected.py `
  --protocol-manifest $protocolManifest `
  --split-path $splitPath `
  --seed $seed `
  --run-label "corrected-s$seed" `
  --resume 100000 `
  --stop-step 200000 `
  --dataset-root $env:DIFFAUDIT_CIFAR10_ROOT `
  --num-workers 4 `
  --log-file "training/outputs/corrected-s$seed/training-200k.log"
```

All targets in the chosen branch must be trained symmetrically. Do not continue
only a high-AUC target.

## Confirmatory Evaluation Contract

The current repeated OOF code is useful for regression testing and exploratory
diagnostics, but the confirmatory scorer must fit PCA/LR only on the locked
calibration rows and compute metrics only on the locked evaluation rows.

- H1 configuration: sites `late_down`, `mid_0`, `mid_1`, `early_up`;
  timesteps `100`, `400`, `700`; PCA components `6`; fixed score direction.
- Primary endpoint: held-out AUC.
- Secondary endpoint: TPR at 1% FPR with Wilson interval.
- Do not report TPR at 0.1% FPR with 512 clean evaluation rows.
- Bootstrap calibration and evaluation rows stratified by class; refit the
  attack inside every replicate and use paired row draws across checkpoints.
- Use exactly 1,000 paired bootstrap draws for H1 and PIA. With eight targets
  there are 28 pairwise comparisons; 200 plus-one draws cannot make the first
  Holm-adjusted p-value smaller than 0.05.
- Run at least 200 full label permutations with attack refitting.
- PIA is the fixed validation attack after its positive-control gate. SecMI is
  exploratory unless frozen before any corrected outcome is inspected.

## Outcome-Blind Restart Rule

The first formal Stage 1 launch was stopped at step 22,000 on its first target
after the post-training command audit found an incomplete canonical PIA bridge
and missing complete-roster PIA statistics. No membership outcome was generated
or viewed, and the remaining targets did not start.

That partial target MUST NOT be resumed, scored, or relabeled. After the PIA
repair is committed, rebuild the protocol with the same predeclared seeds and
training matrix, use fresh corrected run labels, repeat the required dry-run and
resource checks, and start every target from step zero.

## Interim Branch Rules

- **STOP** only when both H1 and PIA have AUC 95% upper bounds below 0.55 on
  every first-stage target.
- **REPLICATE** when the predeclared membership-signal gate passes; train the
  four held-back seeds to 100k without changing rows, attacks, or thresholds.
- **MATURE** for all other non-futile outcomes; continue all original targets
  to 200k symmetrically.

Do not change N, seeds, attack direction, PCA dimension, sites, timesteps, or
checkpoint selection after seeing the interim scores.

## Required Reporting

- Report every target in the frozen set, including failures.
- Report all predeclared pairwise deltas with Holm correction, not only the
  largest pair.
- Require both a global difference test and practical range of at least 0.05
  before describing finite-target heterogeneity.
- H1-only differences are H1-specific variability. Cross-attack heterogeneity
  requires the same decision from H1 and PIA.
- Four or eight targets do not establish population variance, prevalence,
  bimodality, or a memorization mechanism.
- Do not name point-estimate signs as amplify/flat/drop regimes.
- Report the same fixed-test denoising-loss utility proxy for every target in
  the confirmatory set. Any FID/KID extension must also cover the full set
  symmetrically, never only high-AUC targets.

## Evidence Closure

After a branch completes, update together:

1. `ROADMAP.md`
2. `docs/evidence/experiment-master-log.md`
3. `docs/paper1/frozen-claim-matrix.md`
4. one new dated evidence memo for the corrected experiment
5. the paper evidence bank and submission-readiness review (in `Papers/`)

Before any public commit:

```powershell
python -X utf8 scripts/util/run_pr_checks.py
python -X utf8 scripts/util/check_markdown_links.py
```
