# DiffAudit Research Roadmap

> Last updated: 2026-07-18
> Scope: current Research execution board (public-safe).
>
> Implementation: corrected-evidence code is on main (merged from
> feat/paper1-corrected-evidence). Do not resume historical Phase G targets.

## Current Baseline

Paper 1 remains **not submission-ready** as a positive membership-signal paper.
The historical Phase G seed42/43/45 targets were trained on the full CIFAR-10
training set while evaluation treated half of those rows as nonmembers. The old
H1 scorer also fitted PCA/LR and reported AUC on the same rows.

Consequences that still hold:

- all old H1 AUCs are diagnostic-only;
- three-seed, continuation-direction, N=512 cluster, knockout, fine-temporal,
  and run-identity claims are quarantined;
- corrected training/scoring code cannot retroactively validate old targets;
- historical targets MUST NOT be resumed into corrected runs.

**Corrected confirmatory matrix (executed):** four predeclared corrected-*
targets were trained symmetrically to 100k, branched **MATURE** to 200k with
exact resume, and evaluated with held-out H1 plus canonical PIA under the frozen
protocol. Membership-signal and cross-target heterogeneity gates **did not
pass** at either horizon. The admitted scientific ceiling is therefore an
**audit-failure / non-reproduction** measurement: the historical multi-seed
membership package does not reappear under the pre-registered member-only,
held-out contract. Claim ceiling **must not be upgraded** without a new
pre-registered protocol and explicit authorization.

Active public runbook (protocol text):
docs/start-here/paper1-corrected-evidence-runbook-2026-07-11.md

Historical note (2026-07-12): an earlier first formal attempt was stopped
outcome-blind at step 22,000 when PIA could not load corrected ema checkpoints.
That partial target is permanently excluded and is not part of the completed
roster.

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
  replicate, plus at least 200 full label-permutation refits (1,000 draws).
- [x] Repair PIA canonical and pass a synthetic-checkpoint positive-control gate
  before it is used as the validation attack.
- [x] Implement and test exact resume, including Python/NumPy/Torch CPU/CUDA and
  data-loader state.
- [x] Add strict row-bound H1 and PIA packet schemas with
  dataset/run/checkpoint/noise/protocol identities.
- [x] Bind H1 activation extraction to the locked rows and common-noise contract;
  preflight and confirmatory packets generated under the frozen contract.

Protocol v3 hash: b73b8244. Focused tests on the corrected path remain green
(see latest CI / local pytest on main).

## P1: Short GPU Preflight

- [x] Preflight passed after batch-size contract revision (batch 32); exact-resume
  and schema checks passed. Disposable preflight / engineering smokes remain
  **non-confirmatory** and must not enter paper evidence.

## P2: First-Stage Matrix — 4 Targets x 100k

- [x] Four predeclared seeds trained symmetrically to 100k in independent
  corrected-* directories (no historical seed42-45 resume).
- [x] Full-roster held-out H1 + PIA evaluation under frozen cal/eval, common
  noise, bootstrap, and permutation protocol.

## P3: Frozen 100k Branch

- [x] Branch decision applied: **MATURE** (not STOP, not REPLICATE).
- [x] Same four targets continued symmetrically to 200k with exact resume.
- [x] Held-back four seeds **not** opened (branch rule).

### Branch rules (frozen; retained for audit)

- **STOP** — both attacks AUC 95% upper bounds below 0.55 on every first-stage
  target.
- **REPLICATE** — membership-signal gate passes then train held-back four to 100k
  as independent validation (do not pool and redefine the rule).
- **MATURE** — all other non-futile outcomes then original four to 200k
  symmetrically.

## P4: Confirmatory Analysis

- [x] Primary AUC and secondary TPR@1%FPR reported under the frozen endpoints.
- [x] Heterogeneity gates (global equality + practical range + Holm pairwise)
  applied to H1 and PIA at 100k and 200k.
- [x] Interpretation locked: no admitted cross-attack finite-target heterogeneity;
  no admitted H1-only instability claim; no population seed-variance /
  prevalence / bimodality / mechanism claim.

Endpoints retained:

- Primary: held-out AUC.
- Secondary: TPR@1%FPR with Wilson 95% CI.
- TPR@0.1%FPR blocked at 512 clean evaluation rows.
- Target runs are the paper-level independent units.

## P5: Evidence and Paper Decision

- [x] Preserve checkpoint hashes, protocol/resume identities, row-bound scores,
  and utility metrics for the complete roster.
- [x] Signed evidence verdicts select an **audit-failure / non-reproduction**
  ceiling without claim upgrade.
- [ ] Keep docs/evidence/experiment-master-log.md and
  docs/paper1/frozen-claim-matrix.md aligned with the audit-failure ceiling on
  public surfaces (no private submission paths in this repo).
- [ ] Manuscript polish, peer review, and venue formatting live **outside** this
  public Research repo; do not write venue names or private paper paths here.

Do **not**:

- reopen held-back seeds, exceed 200k, or change the 0.55 threshold without a new
  pre-registered protocol and explicit authorization;
- promote engineering preflight / executor completeness as scientific evidence;
- restore Phase G tables, clusters, or mechanism narratives.

## Claim Boundaries

Allowed:

- the historical evidence contract was invalid and has been quarantined;
- corrected member-only training and held-out scoring infrastructure exist;
- the completed finite-target confirmatory matrix did **not** re-establish the
  historical multi-seed membership / run-identity package under the frozen gates;
- claim ceiling remains an audit-failure / non-reproduction measurement and must
  not be upgraded from exploratory PIA point estimates alone.

Blocked:

- H1 or PIA is admitted positive membership evidence under this matrix;
- H1 is run-dependent as a positive claim;
- seed controls MIA strength or is a dominant variable;
- amplify/flat/drop regimes; N=512 natural clusters;
- Bonnaire timescales as mechanism explanation;
- knockout as stable mechanism/defense target;
- TPR@0.1%FPR for the corrected N=512 evaluation;
- submission-readiness as a Research-repo claim.

## Non-Active Lines

Do not reopen H2 same-cache sweeps, C14 metadata expansion, scnet/DCU matrices,
Beans, Fashion-MNIST, MIDST, CommonCanvas, ReDiffuse repeats, or
Retrace-Baseline watermark work from this Research board. Those lines are closed
or owned elsewhere and are not current Paper 1 blockers.

## Closed Lines (do not reopen)

- Phase G seed42/43/45 and any resubstitution H1 packets
- Outcome-selected N=512 / knockout / fine-grid as confirmatory evidence
- Local diagnostic 16k corrected partial as formal roster member
- Unattended formal expansion beyond the frozen four-target MATURE branch
