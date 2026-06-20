# Paper 1 Evidence Matrix

Complete experiment table for Paper 1 "Weak, Spurious, and Non-Portable: Diagnosing Membership Signals in Diffusion Models."

Status stages: admitted / candidate / hold / weak / blocked / deferred / killed  
Failure modes: weak / spurious / non-portable / admitted

## Admitted Evidence (publication-ready)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | TPR@0.1%FPR | N | CI | Status | WSN |
|---|--------|--------|-----------|:---:|:---------:|:-----------:|:---:|-----|--------|:---:|
| 1 | **GSA 3-shadow** | White-box | GPU-scale / internal | **0.998** | 0.987 | — | 1000 | — | admitted | Admitted |
| 2 | **DPDM defended** | White-box | Defended model | 0.489 | ~0 | — | — | — | admitted | — (defense works) |
| 3 | **PIA baseline** | Gray-box | GPU512 / internal | 0.841 | 0.059 | — | — | — | admitted | Weak low-FPR |
| 4 | **Recon DDIM** | Black-box | Public-100, step30 | 0.837 | 0.22 | 0.11 | 100 | Wilson [0.15,0.31] | admitted | Underpowered (N=100) |

## Rejected / Killed Evidence

| # | Method | Access | Model/Data | Best AUC | Best TPR | N | Kill Reason | WSN |
|---|--------|--------|-----------|:---:|:---------:|:---:|-------------|:---:|
| 5 | **CLiD (paper)** | Black-box | T2I diffusion | **1.000** | 1.00@1% | 100 | Prompt overfitting | **Spurious** |
| 6 | CLiD (neutral) | Black-box | Same, neutral prompts | 0.586 | 0.02@1% | 100 | Collapse control (ΔAUC=0.414) | — |
| 7 | **scnet TC64** | Black/Gray | CIFAR-10 DDPM 0.78M | 0.514 | — | K=2000 | CI [0.495, 0.531] | **Weak** |
| 8 | **scnet TC128** | Black/Gray | CIFAR-10 DDPM 11.76M | 0.518 | — | K=2000 | CI [0.501, 0.536] | **Weak** |
| 9 | **scnet TC192** | Black/Gray | CIFAR-10 DDPM 42.97M | 0.517 | — | K=2000 | CI [0.499, 0.535] | **Weak** |

**Updated 2026-06-18**: DCU HPC bootstrap with K=2000, N_BOOT=10000. Previous AUC ceiling (0.538) was overestimated with K=500. All AUCs cluster at 0.50-0.52 with tighter CIs (width ~0.035). Best = TC128 DDIM SecMI AUC 0.518 [0.501, 0.536] — statistically indistinguishable from random. 54× capacity yields zero meaningful MIA signal gain.
| 10 | CommonCanvas | Black-box | CommonCanvas | 0.574 | — | — | All scorers weak | Weak |
| 11 | Fashion-MNIST | Black-box | DDPM | 0.515 | — | — | Zero low-FPR | Weak |
| 12 | MIDST | Black-box | TabDDPM | 0.530 | — | — | Below floor | Weak |
| 13 | Beans LoRA delta | Black-box | LoRA probe | 0.512 | — | 25 | Near random | Weak |
| 14 | Beans LoRA loss | Black-box | LoRA probe | 0.414 | — | 25 | Direction reversed | Weak |
| 15 | ReDiffuse DiT | Black-box | DiT local probe | ~0.5 | ~0.5 | — | Degenerate | Weak |
| 16 | Semantic-Aux | Black-box | Fusion | +0.002 gain | 0@0.1% | — | Below gate | Weak |

## Candidate / Pending

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | TPR@0.1%FPR | N | Blocker | WSN |
|---|--------|--------|-----------|:---:|:---------:|:-----------:|:---:|---------|:---:|
| 17 | **H2 output-cloud** | Black-box | Single response family | **0.961** | 0.334 | 0.117 | — | img2img fails, single-family | **Non-Portable** |
| 18 | **MoFIT** | Black-box | T2I diffusion | 0.902 | 0.45 | 0.28 | 500 | Pending admission | Candidate |
| 19 | PIA/TMIA-DM switch | Gray-box | GPU512 | — | — | — | — | Not admitted yet | Candidate |

## Evidence Source Mapping

| # | Method | Source File(s) |
|---|--------|---------------|
| 1 | GSA | `docs/evidence/admitted-results-summary.md` |
| 3 | PIA | `docs/evidence/admitted-results-summary.md` |
| 4 | Recon | `docs/evidence/admitted-results-summary.md`, `workspaces/recon/` |
| 5-6 | CLiD | `docs/evidence/clid-prompt-perturbation.md` |
| 7-9 | scnet | `../scnet/output/dcu_experiments_2026-06-05.md`, MANIFEST.json |
| 17 | H2 | `workspaces/h2-output-cloud/` (candidate-only) |
