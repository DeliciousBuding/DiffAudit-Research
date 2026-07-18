# Admission Map — Conceptual Figure for Paper 1

> **QUARANTINED historical narrative (2026-07-18).** Phase G / positive H1 language is not paper-admissible. Corrected matrix = Route C audit-failure only. SSOT: `frozen-claim-matrix.md`.


> ChatGPT recommendation: "One memorable conceptual figure" showing evidence states.

## 3-Axis Admission Map

```
                    HIGH CLAIM-BOUNDARY VALIDITY
                              |
                         GSA  |  
                    admitted   |
                              |
                              |
    LOW SIGNAL ◄-------------+-------------► HIGH SIGNAL
    STRENGTH                  |              STRENGTH
                              |
          scnet (weak)        |         H1 (DAAB)
          H2 score-vector     |    candidate-positive
                              |    tail-fragile
                              |
                              |
                    LOW CLAIM-BOUNDARY VALIDITY
```

## Evidence State Transitions

| Case | Real? | Membership-specific? | Claim-boundary usable? | State |
|------|:-----:|:--------------------:|:---------------------:|-------|
| GSA | ✅ | ✅ | ✅ | Admitted |
| H1/DAAB | ✅ | ⚠️ probably | ❌ tail-fragile | Candidate-positive |
| CLiD | ✅ | ❌ spurious | ❌ | Spurious |
| H2 output-cloud | ✅ | ⚠️ | ❌ non-portable | Non-portable |
| scnet | ❌ | unclear | ❌ | Weak |
| MoFIT | ✅ (external) | ✅ | ⚠️ incomplete | External support |

## H1's Unique Position

H1 is the ONLY case in the claim matrix that satisfies:
- ✅ Real signal (AUC well above random)
- ✅ Replicated (cross-checkpoint)
- ✅ Mechanistically characterized (μ_abs dominant, site/timestep decomposition)
- ✅ Controls pass (shuffle, ablation)
- ❌ NOT causally localizable (targeted KO ≤ random KO)
- ❌ NOT forensically admissible (TPR@1% collapses)

This makes H1 the most nuanced evidence state: it has every property of a strong MIA EXCEPT the two that matter for forensic admission.

## Figure Caption

> **Figure X: Evidence-state admission map.** Each evaluated MIA signal is placed according to signal strength (AUC, control-passing) and claim-boundary validity (low-FPR stability, portability, causal localizability). GSA occupies the upper-right as an admitted strong signal. H1/DAAB (center-right, low validity) illustrates the paper's core insight: a signal can be real, replicated, and mechanistically characterized while remaining non-localizable and forensically inadmissible. CLiD (upper-left) shows spurious high-AUC collapse under covariate control. scnet (lower-left) shows a clean scale-null.
