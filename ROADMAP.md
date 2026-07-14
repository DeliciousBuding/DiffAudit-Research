# DiffAudit Research Roadmap

> Last updated: 2026-07-12
> Scope: current Research execution board.
>
> Implementation branch: `feat/paper1-corrected-evidence`. See `.worktrees/paper1-corrected-evidence` for active code.

## Current Baseline

Paper 1 is under evidence-contract reconstruction and is not submission-ready.
The historical Phase G seed42/43/45 targets were trained on the full CIFAR-10
training set while evaluation treated half of those rows as nonmembers. The old
H1 scorer also fitted PCA/LR and reported AUC on the same rows.

Consequences:

- all old H1 AUCs are diagnostic-only;
- three-seed, continuation-direction, N=512 cluster, knockout, fine-temporal,
  and run-identity claims are quarantined;
- corrected training/scoring code cannot retroactively validate old targets;
- historical targets MUST NOT be resumed into corrected runs.

The active question is narrower: do newly trained member-only targets exhibit
held-out H1 membership signal, and do differences among a predeclared finite
target set exceed row-level measurement uncertainty? Four or eight targets do
not estimate a population-level seed variance or establish a mechanism.

Current command runbook:
`docs/start-here/paper1-corrected-evidence-runbook-2026-07-11.md`.

The first formal corrected matrix was stopped outcome-blind at step 22,000 on
its first target when the post-training audit found that canonical PIA could not
load corrected `ema` checkpoints and lacked the frozen complete-roster
statistics. No membership outcome was generated or viewed. The partial target
is permanently excluded. The protocol is being refrozen after corrected EMA
loading, repository-bound analysis provenance, canonical target ordering, and
1,000-draw H1/PIA paired bootstrap are completed.

## P0: Freeze the Corrected Evidence Contract

- [x] Train only on the fixed 25,000-row member subset.
- [x] Keep fold-local repeated OOF H1 code for regression/exploratory checks.
- [x] Freeze code commit, environment, hyperparameters, precision, checkpoint
  cadence, split SHA256, eight training seeds, and protocol hash.
- [x] Generate disjoint, class-stratified calibration and evaluation manifests;
  each contains 512 members and 512 nonmembers.
- [x] Generate a common-noise manifest bound to dataset row, timestep, and draw
  for use across all checkpoints.
- [x] Add confirmatory H1 scoring that fits PCA/LR only on calibration rows and
  reports metrics only on evaluation rows.
- [x] Add stratified paired bootstrap that refits the attack inside each
  replicate, plus at least 200 full label-permutation refits. Paired bootstrap
  is now 1,000 draws so the eight-target Holm family is mathematically capable
  of rejection.
- [x] Repair PIA canonical and pass a synthetic-checkpoint positive-control gate
  before it is used as
  the validation attack. Historical E3 PIA outputs are not valid for this gate.
- [x] Implement and test exact resume, including Python/NumPy/Torch CPU/CUDA and
  data-loader state, or freeze a common restart policy and block uninterrupted-
  trajectory claims.
- [x] Add strict row-bound H1 and PIA packet schemas with
  dataset/run/checkpoint/noise/protocol identities.
- [ ] Bind H1 activation extraction to the locked rows and common-noise contract,
  then generate a preflight score packet from the corrected checkpoint.

P0 gates implemented on `feat/paper1-corrected-evidence` (commit `d6ef148`).
Protocol v3 hash: `b73b8244`. 304 focused tests pass.

No corrected outcome may be viewed before these protocol choices are frozen.

## P1: Short GPU Preflight

- [x] P1 preflight done: training throughput gate passed; full H1+PIA evaluation
  benchmark pending protocol regeneration.

Run a disposable 2k--5k-step `corrected-*` target before long training.

Pass criteria:

- dataset length is exactly 25,000 and split sets are disjoint;
- no historical checkpoint/output directory is reused;
- no OOM with the live 8 GB GPU state;
- sustained throughput is at least 6.0k steps/hour without thermal throttling;
- checkpoint/resume and manifest checks pass;
- row-bound evaluation artifacts include all required identities.
- projected training plus full evaluation plus a 10% failure buffer fits the
  available GPU window; otherwise reduce the matrix symmetrically before any
  corrected metric is viewed and refreeze the manifest.

Failure pauses long training. Fix the contract, repeat the same preflight seed,
and record the deviation; do not replace the seed.

2026-07-12 status: the original batch-64 preflight failed the throughput and
VRAM-headroom gates. The contract was revised before viewing any corrected
metric to batch size 32, then refrozen. The corrected 0 -> 200 -> 400 -> 2,000
run passed training, exact-resume, checkpoint receipt, thermal, throughput, and
output-schema checks. Long training remains blocked on one complete H1 + PIA
checkpoint-evaluation benchmark and the H1 extraction binding above.

## P2: First-Stage Matrix — 4 Targets x 100k

Train the first four predeclared seeds symmetrically to 100k. Use independent
`corrected-*` directories and never resume seed42/43/44/45 or other historical
targets.

Evaluate every target with the same:

- fixed calibration and evaluation rows;
- common-noise bank;
- H1 configuration and fixed score direction;
- PIA canonical validation attack;
- primary AUC and secondary TPR@1%FPR;
- bootstrap and label-permutation protocol.

The 100k analysis is interim futility/route selection only.

## P3: Frozen 100k Branch

### STOP

Stop the run-uncertainty direction only if H1 and PIA AUC 95% upper confidence
bounds are below 0.55 for every first-stage target. Do not fill secondary
ablations after this gate.

### REPLICATE

If the frozen membership-signal gate passes, train the four held-back seeds to
100k. Report the first four as exploratory targets and the held-back four as an
independent validation set. Do not pool and redefine the decision rule.

The gate must be written in the protocol manifest before outcomes are viewed.
Current intended rule: for the same attack, at least two first-stage targets
have AUC >= 0.55 and individual 95% lower confidence bounds above 0.50, with a
well-calibrated permutation null.

### MATURE

For all other non-futile outcomes, continue the original four targets
symmetrically to 200k. Do not continue only the strongest target. Paired
100k-to-200k trajectory claims require the exact-resume gate; otherwise the
200k set is analyzed under the frozen common restart policy only.

## P4: Confirmatory Analysis

### Endpoints

- Primary: held-out AUC.
- Secondary: TPR@1%FPR with Wilson 95% CI.
- TPR@0.1%FPR is blocked at 512 clean evaluation rows.
- Rows quantify conditional measurement error; target runs are the paper-level
  independent units.

### Heterogeneity Gate

For H1 and PIA separately:

1. run a predeclared global equality test over the complete target set;
2. require practical range `max(AUC)-min(AUC) >= 0.05`;
3. report every predeclared pairwise delta with Holm correction;
4. use paired stratified resampling across checkpoints and refit attacks inside
   bootstrap replicates.

Interpretation:

- H1 + PIA pass: cross-attack finite-target heterogeneity;
- H1 only: H1-specific variability;
- membership signal without heterogeneity: run-identity thesis fails;
- no minimal signal: stop the full-paper route or reframe as an audit-failure
  case study.

No outcome permits population seed-variance, prevalence, bimodality, or
dominant-mechanism claims from four or eight targets.

## P5: Evidence and Paper Decision

After the chosen branch completes:

- [ ] archive checkpoint hashes, protocol manifest, row manifests, noise bank,
  row-bound scores, bootstrap/permutation outputs, and utility metrics;
- [ ] write one dated corrected-evidence memo with a one-sentence verdict;
- [ ] update `docs/evidence/experiment-master-log.md`;
- [ ] update `docs/paper1/frozen-claim-matrix.md` only after the verdict is
  independently checked;
- [ ] synchronize the private evidence bank and submission-readiness review;
- [ ] decide whether the manuscript should be rebuilt, shortened to a
  cautionary note, or stopped.

Venue formatting, taxonomy expansion, guardrail promotion, knockout, temporal
grids, and mechanism writing remain blocked until the corrected confirmatory
matrix changes the paper decision.

## Claim Boundaries

Allowed now:

- the historical evidence contract was invalid and has been quarantined;
- corrected member-only training and stronger scoring infrastructure exist;
- a predeclared finite-target experiment is planned.

Blocked now:

- H1 is admitted membership evidence;
- H1 is run-dependent;
- seed controls MIA strength or is a dominant variable;
- amplify/flat/drop are regimes;
- the N=512 pattern forms natural strong/weak clusters;
- Bonnaire's timescales explain the old observations;
- knockout identifies a stable mechanism or defense target;
- TPR@0.1%FPR for the corrected N=512 evaluation;
- any submission-readiness claim before corrected evidence closure.

## Non-Active Lines

Do not reopen H2 same-cache sweeps, C14 metadata expansion, scnet/DCU matrices,
Beans/Fashion/MIDST repeats, MoFIT GPU work, Retrace-Baseline work, H4,
fine-temporal grids, or cosmetic paper ablations unless a new result changes a
specific decision.
