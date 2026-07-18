# Paper 1: Weak, Spurious, and Non-Portable

## Diagnosing Membership Signals in Diffusion Models

**Status**: Corrected matrix closed (**Route C**, 2026-07-18); historical Phase G quarantined. SSOT: `frozen-claim-matrix.md` + `ROADMAP.md`  
**Scope**: Research repo + scnet DCU external evidence  
**NOT included**: Watermark baseline data (Retrace-Baseline), Gaussian Shading, Stable Signature, Tree-Ring collapse  

## Repository Boundary

| What | Where | Paper |
|------|-------|-------|
| MIA audit evidence (admitted/killed/candidate lines) | `Research/` | **Paper 1** (DiffAudit independent) |
| Watermark baseline + collapse experiments | `Retrace-Baseline/` | watermark paper team (collaboration) |
| DCU self-trained DDPM evidence | `scnet/` (closed) | Paper 1 (external weak-signal evidence) |
| Defense transfer experiments | `Defense-Transfer/` | Separate line (blocked) |

## Core Taxonomy

- **Weak signal**: Statistically indistinguishable from random OR practically too small (AUC < 0.60, CI crosses 0.5)
- **Spurious signal**: High apparent performance from non-membership covariate (collapses under control)
- **Non-portable signal**: Strong in one environment, fails in second plausible setting
- **Admitted signal**: Passes all gates, scope documented

## Evidence Sources

| Source | File | Content |
|--------|------|---------|
| Admitted results | `docs/evidence/admitted-results-summary.md` | GSA, PIA, Recon, DPDM verified rows |
| Reproduction status | `docs/evidence/reproduction-status.md` | All lines with status stages |
| CLiD case study | `docs/evidence/clid-prompt-perturbation.md` | Spurious signal evidence |
| H2 candidate | docs/evidence H2 notes | Non-portable candidate |
| scnet external | `../scnet/output/` | Weak signal evidence (DCU CIFAR-10) |

## Paper 1 Evidence Files (this directory)

| File | Content |
|------|---------|
| `README.md` | This file |
| `evidence-matrix.md` | Complete experiment table with WSN classification |
| `statistical-audit.md` | CI calculations, significance tests, low-FPR warnings |
| `contribution-boundary.md` | Paper 1 vs Paper 2 vs external evidence boundaries |

## Manuscript Packaging

Manuscript packaging lives outside this public Research repository. Do not store double-blind / acceptance playbooks here.

