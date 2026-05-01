# H2 Cross-Asset Contract Preflight

This note records the CPU-only portability check after the H2 DDPM/CIFAR10
follow-up. It prevents the project from treating "we have SD/CelebA assets" as
evidence that H2 response-strength transfers.

## Verdict

```text
negative but useful for default SD/CelebA text-to-image
```

Local assets are sufficient for SD/CelebA black-box work, but the default
text-to-image protocol does not instantiate H2 response-strength. H2 needs a
query image or an unconditional diffusion state that can be perturbed at fixed
strengths and repeated under controlled stochasticity. A prompt-only endpoint
does not provide that contract.

## CPU Probe Result

The probe is implemented in:

```powershell
python scripts/probe_h2_cross_asset_contract.py
```

Default result:

| Check | Result |
| --- | --- |
| SD1.5 diffusers assets | ready |
| CelebA image and annotation assets | ready |
| Recon CelebA public splits and target LoRA | ready |
| Endpoint mode | `text_to_image` |
| H2 protocol compatibility | blocked |
| Verdict | `negative but useful; text-to-image assets alone do not instantiate H2 response-strength` |

The same probe marks an `image_to_image` endpoint as eligible only when all
protocol assumptions are explicit:

```powershell
python scripts/probe_h2_cross_asset_contract.py `
  --endpoint-mode image_to_image `
  --controlled-repeats `
  --response-images-observable
```

That eligibility result is now frozen as a separate CPU contract in
[h2-image-to-image-contract.md](h2-image-to-image-contract.md). It is not
admitted evidence; it only authorizes a tiny image-to-image protocol scout if a
runner exists and GPU memory is available.

## Research Decision

Do not run a GPU H2 portability packet on the current SD/CelebA text-to-image
surface. The next black-box slot should choose one of two paths:

| Option | Status | Why |
| --- | --- | --- |
| H2 image-to-image contract | eligible CPU contract | Requires only a tiny frozen scout before any scale-up. See [h2-image-to-image-contract.md](h2-image-to-image-contract.md). |
| CLiD / recon / variation continuation | ready for CPU selection | These methods are protocol-compatible with SD/CelebA text-to-image or returned-image black-box surfaces. |

## Boundary

- This does not weaken the DDPM/CIFAR10 H2 candidate result.
- This does not promote H2 to admitted evidence.
- This does not change Platform or Runtime schemas.
- This blocks same-name transfer claims from DDPM/CIFAR10 to conditional
  diffusion until a compatible endpoint contract exists.
