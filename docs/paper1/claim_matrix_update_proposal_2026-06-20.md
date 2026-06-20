# Claim Matrix Update Proposal (2026-06-20)

> Based on ChatGPT review of H1/H2/H4 GPU experiments.
> Proposed for inclusion in frozen_claim_matrix.md.

## New Row: H1 Activation-Subspace Fingerprint (#23)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | N (m/nm) | Status |
|---|--------|--------|-----------|:---:|:---------:|:---:|--------|
| 23 | **H1 Activation-Subspace** | White-box activation | CUDA UNet CIFAR-10 | **0.873** | 0.055 | 128/128 | candidate-positive / low-FPR-fragile |

### Allowed Claims
- "Internal UNet activation summaries (late_down, mid, early_up) produce a stable aggregate membership signal (AUC=0.873 at N=128, ΔAUC=+0.001 from N=64→128)"
- "Signal passes label-shuffle control (AUC=0.486) and does not depend on a single UNet site"
- "H1 provides a mechanistically distinct white-box observable: non-gradient, non-loss, activation-based"
- "H1 is a worked example of the 'AUC-stable but low-FPR-fragile' category in the WSN taxonomy"

### Blocked Claims
- ❌ "H1 is admitted membership evidence"
- ❌ "Activation-subspace attack achieves reliable low-FPR MIA"
- ❌ Any TPR@0.1%FPR claim
- ❌ "H1 is as strong as GSA"

## Row Update: H2 Output-Cloud → Split (#20 stays, new #24)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | N | Status |
|---|--------|--------|-----------|:---:|:---------:|:---:|--------|
| 24 | **H2 Score-Vector Geometry** | White-box sidecar | CUDA UNet CIFAR-10 | 0.681 | 0.063 | 128/128 | weak/killed |

### Allowed Claims
- "Score-vector geometry on the E3-calibrated target produced weak and unstable sidecar signal"
- "AUC decreased from 0.753 to 0.681 under scale-up (ΔAUC=-0.072)"
- "Low-FPR TPR remained unreliable"

### Blocked Claims
- ❌ Any claim of H2 as a robust second attack family

## H4: Closed (Non-Release)

H4 (Post-Training Subspace Editing Defense) not released:
- H1 signal distributed across all 4 UNet sites (ablation ΔAUC < 0.01)
- No compact risky subspace suitable for targeted editing identified
- Blind pruning/editing would likely degrade utility without reducing GSA

## Revised Claim Matrix Structure

| Category | Rows | Count |
|----------|------|:-----:|
| Admitted | #1 GSA, #2 DPDM, #3 PIA baseline, #4 PIA defended, #5 Recon | 5 |
| Spurious | #6 CLiD | 1 |
| Weak/Killed | #7-19 scnet/CommonCanvas/etc. + #24 H2 score-vector | 14 |
| Non-Portable | #20 H2 output-cloud | 1 |
| External Support | #21 MoFIT | 1 |
| Candidate | #22 PIA/TMIA-DM + **#23 H1 activation-subspace** | 2 |

## Paper Writing Tasks

1. Add §"Activation Fingerprints: Real Signal, Weak Forensic Tail" to main.tex
2. Generate H1 figure: AUC stability vs TPR@1% collapse (N=64→128)
3. Add H1 ablation table to supplement
4. Update claim_register.md and evidence_bank.md
5. Record artifact manifest (score files, configs, seeds, splits)
6. Regenerate paper.pdf and verify
