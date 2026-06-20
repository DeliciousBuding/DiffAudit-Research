# H1 Activation-Subspace Fingerprint — Final Result

> Date: 2026-06-20
> Verdict: **CANDIDATE** — Real, stable, distinct white-box signal. Second mechanism confirmed.

## Scoreboard

| N | AUC | TPR@1%FPR | TPR@0.1%FPR | Shuffle AUC | Ablation |
|---|:---:|:---------:|:-----------:|:-----------:|----------|
| 64 | 0.874 | 0.484 | 0.000 | 0.410 ✅ | no single site ✅ |
| **128** | **0.873** | **0.055** | 0.000 | 0.486 ✅ | no single site ✅ |

Signal stable: ΔAUC = 0.001 from N=64→128.

## Claim Matrix Gates

| Gate | Result |
|------|:------:|
| Target identity (checkpoint hash) | ✅ secmi-bundle MD5 verified |
| Split semantics (member/nonmember) | ✅ CIFAR10_train_ratio0.5 |
| Score provenance (features auditable) | ✅ Script committed |
| Metric provenance (AUC/TPR computation) | ✅ Bidirectional, fixed bug |
| Consumer boundary (white-box activation) | ✅ Distinct from GSA/loss |
| Surface delta (signal stable across N) | ✅ ΔAUC=0.001 |

**Allowed**: "Distinct white-box signal (AUC=0.873), limited low-FPR (TPR@1%=0.055)"
**Blocked**: "Reliable low-FPR MIA", "As strong as GSA", any TPR@0.1% claim

## Comparison

| Method | Access | AUC | TPR@1% | Mechanism |
|--------|--------|:---:|:-----:|-----------|
| GSA | White-box gradient | 0.998 | 0.987 | Gradient norm |
| **H1** | White-box activation | **0.873** | 0.055 | Activation subspace |
| PIA | Gray-box | 0.841 | 0.059 | DDIM trajectory |
| H2 | White-box score-vector | 0.681 | 0.063 | Epsilon geometry |

## H4 Decision

**Closed.** Signal distributed across all UNet sites (ablation ΔAUC < 0.01). No stable risky subspace for targeted editing. H4 prerequisite not met.

## Sources

- Script: `scripts/h1_activation_scout.py`
- Raw data: `outputs/h1_scout/h1_raw_activations.pkl`
- Results: `outputs/h1_scout/h1_results.json`
