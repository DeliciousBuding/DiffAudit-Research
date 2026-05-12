# Mid-Frequency Same-Noise Residual Preflight

This note records a CPU-only intake decision for a paper-backed black-box
observable: mid-frequency residual scoring at the same diffusion noise level.
It is not admitted evidence and does not release a GPU task.

## Verdict

```text
blocked-by-cache-contract; distinct observable gap; no GPU release
```

The proposed observable is distinct from the existing H2/H3 frequency work, but
the current local caches cannot evaluate it. Existing H2/H3 artifacts contain
final response images and response-distance summaries; they do not preserve the
same-noise state required for a mid-frequency residual score.

## Bounded Question

Can a fixed mid-frequency residual score expose member/nonmember separation
that is not just H2 response-strength, H3 frequency filtering, or simple
image-to-image response distance?

The score must compare a noisy state and its same-noise reconstruction:

```text
score(x) = || M_mid * FFT(tilde_x_t - x_t) ||_2
```

where `M_mid` is a fixed annular mid-frequency mask selected before the packet.
The first implementation should use band-pass L2 only. SSIM or learned fusion
are later ablations, not the first scorer.

## Distinction From Existing Evidence

| Existing line | What it covers | Why it does not close this question |
| --- | --- | --- |
| H2 lowpass response-strength | Lowpass-filtered final response distances on DDPM/CIFAR10 response caches. | It scores `response - input` after denoising, not `tilde_x_t - x_t` at the same noise level. |
| H3 frequency-filter cache ablation | Lowpass, highpass, and bandpass plug-ins over the X168 H2/H1 response cache. | It reuses H2/H1 response outputs and is a cache-level plug-in, not a same-noise residual observable. |
| SD/CelebA simple distance | Bounded single-asset image-to-image response-distance evidence. | It is a final image response-distance signal and not a DDPM same-noise residual score. |

This means the direction is neither admitted nor already falsified. It is a
distinct preflight gap.

## Cache Audit

The local audit checked representative H2/H3 and image-to-image caches for the
fields required by the same-noise residual contract.

Required fields:

| Field | Required role |
| --- | --- |
| `labels` | membership labels |
| `timestep` or `timesteps` | fixed residual timestep |
| `x_t` | noisy state before reconstruction |
| `tilde_x_t` | same-noise reconstructed state |
| `noise_seed` or equivalent | reproducible noise provenance |
| `same_noise_residual` | optional precomputed residual |

Audited caches:

| Cache | Existing useful fields | Missing blocker |
| --- | --- | --- |
| `x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz` | `labels`, `timesteps`, `inputs`, `responses`, `min_distances_rmse` | `x_t`, `tilde_x_t`, noise provenance, same-noise residual |
| `x172-h2-strength-response-validation-20260429-r1/response-cache.npz` | `labels`, `timesteps`, `inputs`, `responses`, `lowpass_min_distances_rmse` | `x_t`, `tilde_x_t`, noise provenance, same-noise residual |
| `x176-h2-nonoverlap-256-validation-20260429-r1/response-cache.npz` | `labels`, `timesteps`, `inputs`, `responses`, `lowpass_min_distances_rmse` | `x_t`, `tilde_x_t`, noise provenance, same-noise residual |
| `h2-response-strength-512-20260501-r1/response-cache.npz` | `labels`, `timesteps`, `inputs`, `responses`, `lowpass_min_distances_rmse` | `x_t`, `tilde_x_t`, noise provenance, same-noise residual |
| `h2-lowpass-followup-512-20260501-r1/response-cache.npz` | `labels`, `timesteps`, `inputs`, `responses`, `lowpass_min_distances_rmse` | `x_t`, `tilde_x_t`, noise provenance, same-noise residual |
| `h2-img2img-simple-distance-admission-20260501-r1/response-cache.npz` | `labels`, `strengths`, `inputs`, `responses`, `lowpass_min_distances_rmse` | `timesteps`, `x_t`, `tilde_x_t`, noise provenance, same-noise residual |

The machine-readable audit summary is
`workspaces/black-box/artifacts/midfreq-same-noise-residual-cache-audit-20260512.json`.

## Falsifier

Do not run a GPU packet unless a CPU/tiny preflight can produce a residual cache
with:

- `64` members and `64` nonmembers at most for the first sign check.
- One fixed timestep selected before execution, initially `t = 80` or `t = 120`.
- One fixed band-pass mask selected before execution, initially a radial FFT
  annulus in the `0.25-0.50` or `0.35-0.65` normalized range.
- Per-sample `labels`, `x_t`, `tilde_x_t`, `timestep`, noise provenance, and
  `bandpass_l2` score.
- Metrics: `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`, member/nonmember score
  means, and finite-tail denominators.

The line should close as `negative-but-useful` if the first frozen residual
packet fails to beat the same-cache final-response distance comparator on AUC
or fails to produce any strict-tail signal. It should stay candidate-only even
if positive.

## Next Action

Implement or freeze a CPU-first residual collector contract before any GPU
release. The collector should reuse the existing DDPM/CIFAR10 model path only
if it can store same-noise state explicitly. Existing H2 response caches must
not be reused as evidence for this observable.

## System Boundary

No Platform or Runtime schema changes are needed. No admitted result changes.
This is a Research-only preflight decision.
