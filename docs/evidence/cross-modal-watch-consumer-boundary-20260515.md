# Cross-Modal Watch Consumer Boundary

> Date: 2026-05-15
> Status: consumer-boundary-synchronized / related-methods-only / no Platform row / no Runtime schema change

## Question

Do the current cross-modal watch verdicts change the admitted Platform/Runtime
consumer set?

This is a consumer verdict, not a new experiment. It updates the previous
SAMA/VidLeaks boundary after the GGDM artifact gate added a graph generative
diffusion watch item.

## Inputs

| Evidence | Status |
| --- | --- |
| [sama-dlm-asset-verdict-20260514.md](sama-dlm-asset-verdict-20260514.md) | Diffusion-language-model related-method codebase; out of scope for the current image/latent-image Lane A and missing released target/split/score artifacts. |
| [vidleaks-t2v-asset-verdict-20260514.md](vidleaks-t2v-asset-verdict-20260514.md) | Text-to-video related-method code snapshot; live GitHub repo unavailable and missing target T2V weights, exact video split manifests, generated videos, feature CSVs, and score packets. |
| [ggdm-zenodo-artifact-gate-20260515.md](ggdm-zenodo-artifact-gate-20260515.md) | Graph-diffusion related-method code archive; missing fixed graph target checkpoint, exact graph member/nonmember manifest, generated graph cache, score/ROC artifact, metrics packet, and public AWE module. |
| [paperization-consumer-boundary-20260513.md](paperization-consumer-boundary-20260513.md) | Weak/watch image-diffusion lines remain limitations or future-work hooks only. |
| [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md) | Platform/Runtime admitted rows remain the existing guarded set. |

## Decision

The admitted Platform/Runtime consumer set does not change.

SAMA, VidLeaks, and GGDM can be cited only as related-method or future-work
context. They are not admitted evidence, not candidate product rows, and not
schema inputs. They also should not be used to imply that DiffAudit currently
supports language-model, text-to-video, or graph generative diffusion membership
auditing.

Downstream consumers should still use only:

- `recon`
- `PIA baseline`
- `PIA defended`
- `GSA`
- `DPDM W-1`

## Boundaries

| Item | Boundary |
| --- | --- |
| Platform product copy | Do not add DLM, T2V, graph-diffusion, or general cross-modal support claims from SAMA, VidLeaks, or GGDM. |
| Runtime schema | Do not add DLM prompt/text fields, T2V video fields, caption/VBench/Gemini fields, graph adjacency/node-feature fields, graph-diffusion target fields, or AWE/GRA/PIA graph metrics for these watch items. |
| Evidence bundle | Do not add SAMA, VidLeaks, or GGDM to the admitted machine-readable bundle. |
| Research roadmap | Keep all three as related-method watch items unless an explicit DLM, T2V, or graph generative diffusion membership lane is opened with target, split, response/score, and stop-gate artifacts. |

## Next Gate

No follow-up CPU or GPU task is released by this consumer-boundary sync.

Reopen only if one of the cross-modal lines publishes a public-safe target plus
exact member/nonmember manifests and a reusable response/score packet, or if
DiffAudit explicitly expands scope into that modality with a consumer-boundary
decision first.

## Platform and Runtime Impact

None. This note blocks product/schema drift and preserves the admitted consumer
set.
