# Paper 1 — Scientific Narrative Restructuring

> Based on ChatGPT deep scientific review 2026-06-20.
> Core insight: "Membership inference is not a score-ranking problem; it is an evidence-admission problem."

## Core Thesis (sharpened)

**Weak version** (obvious, avoid): "High AUC is not everything."

**Strong version** (the real contribution):
> A diffusion MIA score can be statistically real (AUC well above random), mechanistically interpretable (clear feature-story), and control-passing (shuffle, ablation), yet still inadmissible as membership evidence because the forensic tail fails at the intended claim boundary.

## Differentiation from CopyMark

| Dimension | CopyMark | DiffAudit |
|-----------|----------|-----------|
| Main object | Benchmark realism | Claim admissibility |
| Failure mode | Over-training, dataset shift | Weak, spurious, non-portable, tail-fragile |
| Output | "MIA degrades under realistic eval" | "What claims can/cannot be admitted" |
| Unit | Attack method on benchmark | Score surface + evidence contract + claim boundary |

**Key sentence for Related Work:**
> CopyMark shows diffusion MIA performance can be overestimated under unrealistic benchmarks. DiffAudit addresses a complementary question: even when a score is reproducible and statistically non-random, what additional evidence is required before the score can be admitted as support for a specific membership claim?

## Negative Evidence Reorganization

NOT "we tried many things; most failed." INSTEAD: a theory of promotion errors.

| Error type | What it means | Evidence |
|------------|--------------|----------|
| **Average-score promotion** | Treating AUC as admissible evidence | H1: AUC=0.873, TPR@1% collapses |
| **Covariate promotion** | Mistaking prompt/source signal for membership | CLiD: AUC 1.000→0.586 under control |
| **Scale promotion** | Assuming more capacity → stronger MIA | scnet: 54× capacity, ΔAUC=0.003 |
| **Surface-transfer promotion** | Assuming same-family signal generalizes | H2: AUC=0.962 within-family, fails portability |
| **External-positive boundary** | Strong external scores need row-bound provenance | MoFIT: AUC=0.942, missing row binding |

## Conceptual Figure: Admission Map

3-axis framework:
- **Axis 1**: Is the signal real? (AUC, shuffle controls, CIs)
- **Axis 2**: Is the signal about membership? (covariate controls, provenance)
- **Axis 3**: Is the signal usable at the claim boundary? (low-FPR, portability, consumer)

Cases placed on the map:

| Case | Real? | Membership-specific? | Claim-boundary usable? | State |
|------|-------|---------------------|----------------------|-------|
| GSA | ✅ yes | ✅ yes | ✅ yes | admitted |
| H1 | ✅ yes (AUC 0.84-0.87) | ✅ probably | ❌ no (tail fragile) | candidate-positive |
| CLiD | ✅ yes (AUC 1.000) | ❌ no (prompt) | ❌ no | spurious |
| H2 cloud | ✅ yes (AUC 0.962) | ✅ maybe | ❌ no (portability) | non-portable |
| scnet | ❌ no (AUC≈0.52) | unclear | ❌ no | weak |
| MoFIT | ✅ yes (external) | ✅ yes | ⚠️ incomplete | external support |

## H1 as Intellectual Centerpiece

H1 decouples three things most MIA papers conflate:
1. **Average ranking signal** — AUC ≈ 0.873, stable across N and checkpoints
2. **Mechanistic distinctness** — activation-based, not gradient/loss
3. **Forensic admissibility** — low-FPR tail collapses under scale-up

This makes H1 the paper's best scientific illustration:
- Not an obvious failure (like CLiD which is almost too clean)
- A subtle case where the signal is real, stable, and distinct — yet still not admissible
- Exactly the kind of nuance target-venue reviewers respect

## Protocol Weakness Mitigation

**Problem**: Protocol may feel post-hoc.

**Fix**: State gates as a claim-admission framework BEFORE presenting results. For each row, say which gate it fails. Structure:
1. Define the 6-gate contract (pre-specified)
2. Apply to each case
3. Record which gate blocks each claim

**Problem**: Too many gates.

**Fix**: Collapse 6 gates into 3 families in narrative:
1. Identity/provenance (target, split)
2. Calibration/operating point (score/response, metric)
3. Portability/consumer (consumer boundary, surface delta)

**Problem**: "Admitted" sounds legalistic.

**Fix**: Use "scope-bounded admitted evidence" — admitted within stated contract and scope, not "true forever."

## Excellent-Paper Checklist

- [ ] One memorable 3-axis "admission map" figure
- [ ] "Promotion error" table (teaches the field how not to fool itself)
- [ ] H1 as intellectual centerpiece (not just another section)
- [ ] Negative rows organized by error type, not as a dump
- [ ] Clear differentiation from CopyMark in Related Work
- [ ] Protocol presented as pre-specified, not post-hoc
- [ ] Core thesis sharpened to "evidence-admission problem"
