# Cross-Modal Watch Consumer Boundary

> Date: 2026-05-15
> Status: consumer-boundary-synchronized / related-methods-and-watch-plus-only / no Platform row / no Runtime schema change

## Question

Do the current cross-modal watch verdicts change the admitted Platform/Runtime
consumer set?

This is a consumer verdict, not a new experiment. It updates the previous
SAMA/VidLeaks/GGDM boundary after the DurMI artifact gate added a TTS/audio
watch-plus item.

## Inputs

| Evidence | Status |
| --- | --- |
| [sama-dlm-asset-verdict-20260514.md](sama-dlm-asset-verdict-20260514.md) | Diffusion-language-model related-method codebase; out of scope for the current image/latent-image Lane A and missing released target/split/score artifacts. |
| [vidleaks-t2v-asset-verdict-20260514.md](vidleaks-t2v-asset-verdict-20260514.md) | Text-to-video related-method code snapshot; live GitHub repo unavailable and missing target T2V weights, exact video split manifests, generated videos, feature CSVs, and score packets. |
| [ggdm-zenodo-artifact-gate-20260515.md](ggdm-zenodo-artifact-gate-20260515.md) | Graph-diffusion related-method code archive; missing fixed graph target checkpoint, exact graph member/nonmember manifest, generated graph cache, score/ROC artifact, metrics packet, and public AWE module. |
| [durmi-tts-artifact-gate-20260515.md](durmi-tts-artifact-gate-20260515.md) | TTS/audio cross-modal watch-plus; public attack code, GradTTS LJSpeech exact split, and Zenodo checkpoint/data metadata are present, but ready duration-loss score arrays, ROC arrays, metric JSON, generated result graphs, and a TTS consumer-boundary decision are missing. |
| [paperization-consumer-boundary-20260513.md](paperization-consumer-boundary-20260513.md) | Weak/watch image-diffusion lines remain limitations or future-work hooks only. |
| [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md) | Platform/Runtime admitted rows remain the existing guarded set. |

## Decision

The admitted Platform/Runtime consumer set does not change.

SAMA, VidLeaks, GGDM, and DurMI can be cited only as related-method,
future-work, or cross-modal watch-plus context. They are not admitted evidence,
not candidate product rows, and not schema inputs. They also should not be used
to imply that DiffAudit currently supports language-model, text-to-video, graph
generative diffusion, or TTS/audio membership auditing.

Downstream consumers should still use only:

- `recon`
- `PIA baseline`
- `PIA defended`
- `GSA`
- `DPDM W-1`

## Boundaries

| Item | Boundary |
| --- | --- |
| Platform product copy | Do not add DLM, T2V, graph-diffusion, TTS/audio, or general cross-modal support claims from SAMA, VidLeaks, GGDM, or DurMI. |
| Runtime schema | Do not add DLM prompt/text fields, T2V video fields, caption/VBench/Gemini fields, graph adjacency/node-feature fields, graph-diffusion target fields, AWE/GRA/PIA graph metrics, TTS text/audio fields, phoneme-duration fields, or duration-loss metrics for these watch items. |
| Evidence bundle | Do not add SAMA, VidLeaks, GGDM, or DurMI to the admitted machine-readable bundle. |
| Research roadmap | Keep SAMA, VidLeaks, GGDM, and DurMI as related-method/watch-plus items unless an explicit DLM, T2V, graph generative diffusion, or TTS/audio membership lane is opened with target, split, response/score, and stop-gate artifacts. |

## Next Gate

No follow-up CPU or GPU task is released by this consumer-boundary sync.

Reopen only if one of the cross-modal lines publishes a public-safe target plus
exact member/nonmember manifests and a reusable response/score packet, or if
DiffAudit explicitly expands scope into that modality with a consumer-boundary
decision first. DurMI additionally requires either ready duration-loss
score/ROC/metric artifacts or an explicit TTS/audio lane before any Zenodo
dataset/checkpoint download or GPU run.

## Platform and Runtime Impact

None. This note blocks product/schema drift and preserves the admitted consumer
set.
