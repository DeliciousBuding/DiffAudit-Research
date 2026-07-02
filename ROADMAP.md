# DiffAudit Research Roadmap

> Last updated: 2026-07-02
> Scope: current Research execution board. Historical long-form roadmap is in `docs/ROADMAP.md`.

## Current Baseline

Paper 1 is in Phase G: H1/DAAB run-dynamics replication.

The active scientific question is no longer whether H1 exists. It is whether activation-level membership evidence is controlled mainly by training trajectory / run identity, and whether high-AUC runs retain N=512 low-FPR value while weak runs collapse.

Current verified facts:

| Result | Status | Evidence |
| --- | --- | --- |
| DDPM-750k matched control | Complete | `docs/evidence/ddpm-750k-step-matched-control-2026-06-25.md` |
| H1 v2 N=128 unified table | Complete | `outputs/h1-scout-750k/`, `outputs/h1-scout-800k-v2/`, `outputs/h1-scout-ddim-750k/`, `outputs/h1-scout-800k-same-trajectory/` |
| Independent DDPM-800k N=512 | Complete | `outputs/h1-scout-800k-independent-n512/summary.json` |
| DDIM-750k N=512 | Complete | `outputs/h1-scout-ddim-750k-n512/summary.json` |
| Same-trajectory DDPM-800k N=512 | Complete | `outputs/h1-scout-800k-same-trajectory-n512/summary.json` records rerun AUC=0.605488, TPR@1%=0.025391, shuffle AUC=0.488052 |
| seed=43 training to 750k | Complete | `<DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-seed43/checkpoint-step750000.pt`, SHA256 `1dad28a63cef2ef4439f77457c10825bcb4ff66ef7c7e3e19dbe285e4503aba2` |
| seed=43 H1 scout at 750k | Complete | `outputs/h1-scout-seed43-750k/summary.json` records AUC=0.666687, TPR@1%=0.015625, shuffle AUC=0.453552 |

Current command runbook: `docs/start-here/phase-g-runbook-2026-06-30.md`.

## Active Task Board

### P0: Evidence Hygiene

- [x] Re-run or recover same-trajectory DDPM-800k N=512 raw output into `outputs/h1-scout-800k-same-trajectory-n512/`.
- [ ] Add `summary.json` beside every Phase G H1 output that is cited by the paper.
- [x] Keep `docs/paper1/frozen-claim-matrix.md`, `docs/evidence/experiment-master-log.md`, and `Papers/diffaudit-evidence-paper/evidence_bank.md` aligned after the seed43 750k scout.

2026-07-01 closure: the same-trajectory DDPM-800k N=512 rerun completed with the readable CIFAR root. The rerun produced raw activation cache, `h1_results.json`, and `summary.json`; the archived AUC is 0.605488 rather than the previously documented unarchived 0.576 value.

2026-07-02 closure: seed43 reached 750k and the bounded N=128 H1 scout completed. The result (AUC=0.666687, TPR@1%=0.015625, shuffle AUC=0.453552) stays in the moderate 750k band rather than the strong-run cluster.

### P1: seed=43 Run-Dynamics Replication

- [x] Resume seed=43 training from the durable 624k checkpoint to 750k.
- [x] Run H1 scout at 750k with the parameterized `scripts/h1/h1_activation_scout.py`.
- [ ] Continue seed=43 from 750k to 800k only after the 750k scout is archived.
- [ ] Run H1 scout at 800k.
- [ ] Run fine temporal grid at 800k.
- [ ] Run N=512 tail only if the seed=43 800k H1 scout has AUC > 0.70.

Decision value: seed=43 decides whether the current two-cluster N=512 pattern is a stable run-dynamics phenomenon or a two-run accident.

### P2: seed=44 Decision Gate

Run seed=44 only after seed=43 800k:

| seed=43 result | Decision |
| --- | --- |
| AUC and fine-grid pattern close to seed42 same-trajectory | seed=44 optional |
| AUC differs by 0.05-0.10 or pattern changes | seed=44 recommended |
| AUC differs by >0.10, approaches the independent strong run, or creates a third pattern | seed=44 required |

### P3: H4 Site-Time Attenuation Scout

Do not run H4 before seed=43 fine-grid results. H4 is a bounded site-time intervention scout, not a defense claim. It must report H1 AUC/TPR deltas plus utility-cost proxies.

## Current Scientific Claims

Allowed:

- H1/DAAB is a real activation-level candidate signal across tested checkpoints.
- Signal strength is training-trajectory sensitive.
- seed43 750k replicates the moderate 750k AUC regime (0.666687) but not reliable low-FPR recovery.
- DDIM-750k is stronger than step-matched DDPM-750k.
- Same-trajectory 750k->800k amplification is modest compared with the independent DDPM-800k gap.
- N=512 currently shows a strong cluster around 0.81 and a weak cluster around 0.56-0.61. The same-trajectory 800k raw artifact is now archived and remains weak-to-moderate at AUC=0.605488 with TPR@1%=0.025391.

Blocked:

- H1 is admitted evidence.
- AUC > 0.8 is universal for DAAB.
- DDPM always produces temporally distributed H1 geometry.
- TPR@0.1%FPR claims at N=512.
- H4 is an effective defense.

## Non-Active Lines

Do not reopen H2 same-cache sweeps, C14 metadata expansion, scnet/DCU matrices, Beans/Fashion/MIDST repeats, MoFIT GPU work, or Retrace-Baseline work unless a new user decision explicitly changes the route.
