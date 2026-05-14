# Cross-Modal Watch Consumer Boundary

> Date: 2026-05-14
> Status: consumer-boundary-synchronized / related-methods-only / no Platform row / no Runtime schema change

## Question

Do the new SAMA diffusion-language-model and VidLeaks text-to-video watch
verdicts change the admitted Platform/Runtime consumer set?

## Inputs

| Evidence | Status |
| --- | --- |
| [sama-dlm-asset-verdict-20260514.md](sama-dlm-asset-verdict-20260514.md) | Diffusion-language-model related-method codebase; out of scope for the current image/latent-image Lane A and missing released target/split/score artifacts. |
| [vidleaks-t2v-asset-verdict-20260514.md](vidleaks-t2v-asset-verdict-20260514.md) | Text-to-video related-method code snapshot; live GitHub repo unavailable and missing target T2V weights, exact video split manifests, generated videos, feature CSVs, and score packets. |
| [paperization-consumer-boundary-20260513.md](paperization-consumer-boundary-20260513.md) | Recent weak/watch image-diffusion lines remain limitations or future-work hooks only. |
| [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md) | Platform/Runtime admitted rows remain the existing guarded set. |

## Decision

The admitted Platform/Runtime consumer set does not change.

SAMA and VidLeaks can be cited only as related-method or future-work context.
They are not admitted evidence, not candidate product rows, and not schema
inputs. They also should not be used to imply that DiffAudit currently supports
language-model or text-to-video membership auditing.

Downstream consumers should still use only:

- `recon`
- `PIA baseline`
- `PIA defended`
- `GSA`
- `DPDM W-1`

## Boundaries

| Item | Boundary |
| --- | --- |
| Platform product copy | Do not add DLM/T2V support claims from SAMA or VidLeaks. |
| Runtime schema | Do not add DLM prompt/text fields, T2V video fields, caption fields, VBench metrics, or Gemini-derived fields for these watch items. |
| Evidence bundle | Do not add SAMA or VidLeaks to the admitted machine-readable bundle. |
| Research roadmap | Keep both as related-method watch items unless an explicit text/DLM or T2V membership lane is opened with target, split, response/score, and stop-gate artifacts. |

## Next Gate

No follow-up CPU or GPU task is released by this consumer-boundary sync.

Reopen only if one of the cross-modal lines publishes a public-safe target plus
exact per-sample or per-video member/nonmember manifests and a reusable
response/score packet, or if DiffAudit explicitly expands scope into DLM or T2V
membership auditing.
