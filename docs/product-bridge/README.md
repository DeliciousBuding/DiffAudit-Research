# Product Bridge

This directory explains how Research feeds DiffAudit Platform and Runtime.

Platform should only consume results that have explicit status and clear
limitations. Research provides three kinds of output:

| Output | What it means |
| --- | --- |
| Verified result | A reviewed experiment result that can be shown as audit evidence. |
| Candidate result | A result useful for internal comparison, not yet ready for external use. |
| Constraint note | A known limitation that prevents overclaiming in Platform UI. |

Current cross-box status: cross-box score sharing is candidate-only. It can
inform internal ranking and future research selection, but it should not appear
as admitted Platform evidence until low-FPR stability is established. See
[../evidence/cross-box-boundary-status.md](../evidence/cross-box-boundary-status.md).

Current boundary-consumability status: Platform and Runtime should consume only
the five admitted bundle rows (`recon`, `PIA baseline`, `PIA defended`, `GSA`,
and `DPDM W-1`) unless a future reviewed promotion explicitly changes this.
ReDiffuse, SecMI stat/NNS, tri-score, cross-box fusion, GSA LR,
H2/simple-distance, CLiD, black-box response-contract acquisition, I-B, and I-C
are candidate, supporting-reference, negative, hold, or needs-assets states.
Recent second-asset and mechanism checks are also Research-only: CommonCanvas /
CopyMark, MIDST TabDDPM, Beans LoRA, Quantile Regression, MIAGM, LAION-mi,
Zenodo fine-tuned diffusion, Noise as a Probe, Kohaku / Danbooru, MIDM,
StablePrivateLoRA, FMIA frequency-component diffusion MIA, SimA score-based
diffusion MIA, Tracing the Roots diffusion-trajectory feature-packet MIA,
ReproMIA withdrawn proactive MIA, Noise Aggregation small-noise diffusion MIA,
GenAI Confessions black-box image-to-image MIA, DurMI TTS duration-loss MIA,
FERMI multi-relational tabular MIA, SAMA diffusion-language-model membership, VidLeaks
text-to-video membership, and GGDM graph generative diffusion membership are
weak, watch, metadata-only, defense-watch, related-method, out-of-scope,
score-packet-missing, positive-but-provenance-limited, withdrawn,
paper-source-only, or artifact-incomplete lines. They do not change admitted
rows, Runtime schemas, recommendation logic, defense claims, or Platform
product copy.
See
[../evidence/paperization-consumer-boundary-20260513.md](../evidence/paperization-consumer-boundary-20260513.md)
and
[../evidence/watch-candidate-consumer-boundary-20260513.md](../evidence/watch-candidate-consumer-boundary-20260513.md).
See also
[../evidence/cross-modal-watch-consumer-boundary-20260515.md](../evidence/cross-modal-watch-consumer-boundary-20260515.md).
See
[../evidence/admitted-consumer-drift-audit-20260512.md](../evidence/admitted-consumer-drift-audit-20260512.md)
and
[../evidence/research-boundary-consumability-sync-20260510.md](../evidence/research-boundary-consumability-sync-20260510.md).
The admitted-row guard is now enforced by
`scripts/validate_attack_defense_table.py`, which checks the complete admitted
consumer set before local checks pass. See
[../evidence/post-response-contract-reselection-20260511.md](../evidence/post-response-contract-reselection-20260511.md).
The multi-row machine-readable admitted evidence bundle is
[`../../workspaces/implementation/artifacts/admitted-evidence-bundle.json`](../../workspaces/implementation/artifacts/admitted-evidence-bundle.json)
and its contract is documented in
[admitted-evidence-bundle.md](admitted-evidence-bundle.md).

Current CLiD status: CLiD is candidate-only. The official GitHub
`inter_output/*` packet now replays cleanly on CPU and is strong
(`AUC = 0.961277`, `TPR@1%FPR = 0.675470`, `ASR = 0.891957`) under the
official threshold path, but the evidence is still prompt-conditioned and does
not resolve the image-identity boundary. The follow-up identity-manifest gate
found numeric-only score rows, no public row manifest or COCO image-id binding,
and authenticated `mia_COCO.zip` HEAD/Range access returned `403`; the
2026-05-15 live access recheck still returns `403` for authenticated `HEAD`,
start `Range`, and end `Range` probes. A machine-readable candidate card exists
only for Research/product-boundary comparison; it must not appear as admitted
Platform evidence or a Runtime row until a product-bridge handoff defines an
image-identity-safe protocol. See
[clid-candidate-evidence-card.md](clid-candidate-evidence-card.md),
[../evidence/clid-identity-manifest-gate-20260515.md](../evidence/clid-identity-manifest-gate-20260515.md),
[../evidence/clid-official-inter-output-replay-20260515.md](../evidence/clid-official-inter-output-replay-20260515.md)
and
[../evidence/clid-prompt-conditioning-boundary.md](../evidence/clid-prompt-conditioning-boundary.md).

Current Tracing the Roots status: Research-only positive feature-packet
evidence. The OpenReview supplementary material ships fixed CIFAR10
diffusion-trajectory feature tensors and replay code, and the bounded local
linear replay reaches `AUC = 0.815826`, `accuracy = 0.737500`,
`TPR@1%FPR = 0.134000`, and `TPR@0.1%FPR = 0.038000`. It must not appear as an
admitted Platform evidence row or Runtime schema input because the public
packet lacks raw target checkpoint identity, raw member/external sample IDs,
and image query/response artifacts. See
[../evidence/tracing-roots-feature-packet-mia-20260515.md](../evidence/tracing-roots-feature-packet-mia-20260515.md).

Current ReproMIA status: Research-only withdrawn paper-source watch. The
current arXiv record is withdrawn, and the historical v1 source is TeX plus
figures only despite reporting DDPM and Stable Diffusion table metrics. It has
no official public code, target checkpoints, exact split manifests, score
arrays, ROC CSVs, or metric JSON. It must not appear as admitted Platform
evidence, Runtime schema input, or active GPU/CPU work. See
[../evidence/repromia-withdrawn-artifact-gate-20260515.md](../evidence/repromia-withdrawn-artifact-gate-20260515.md).

Current Noise Aggregation status: Research-only paper-source watch. arXiv
`2510.21783` v2 reports strong DDPM paper metrics and a distinct small-noise
predicted-noise aggregation mechanism, but the public source is TeX,
bibliography, and figures only. It has no official public code, target
checkpoints, exact split manifests, score arrays, ROC CSVs, metric JSON, or
query/response packet. It must not appear as admitted Platform evidence,
Runtime schema input, or active GPU/CPU work. See
[../evidence/noise-aggregation-small-noise-artifact-gate-20260515.md](../evidence/noise-aggregation-small-noise-artifact-gate-20260515.md).

Current FMIA status: Research-only watch-plus. The OpenReview supplement ships
frequency-filter DDIM/Stable Diffusion attack code and exact split manifests,
but no trained checkpoints, score arrays, ROC/metric artifacts, generated
samples, or ready verifier packet. It must not appear as admitted Platform
evidence or a Runtime row. See
[../evidence/fmia-openreview-frequency-artifact-gate-20260515.md](../evidence/fmia-openreview-frequency-artifact-gate-20260515.md).

Current SimA status: Research-only watch-plus. The official GitHub repository
ships score-based MIA code and scripts, but the public release has empty split
and checkpoint links, no release assets, no committed non-vendor split
manifests, no target checkpoints, no score arrays, no ROC/metric JSON, and no
ready verifier packet. It must not appear as admitted Platform evidence or a
Runtime row. See
[../evidence/sima-scorebased-artifact-gate-20260515.md](../evidence/sima-scorebased-artifact-gate-20260515.md).

Current GenAI Confessions status: Research-only boundary watch. The public
release has raw in-training/out-of-training image inputs for STROLL, Carlini,
and Midjourney settings, but it does not ship the fine-tuned STROLL checkpoint,
generated image-to-image responses, DreamSim distance vectors, ROC/metric
artifacts, Midjourney query logs, or a ready verifier packet. It must not appear
as admitted Platform evidence or a Runtime row. See
[../evidence/genai-confessions-blackbox-artifact-gate-20260515.md](../evidence/genai-confessions-blackbox-artifact-gate-20260515.md).

Current DurMI status: Research-only TTS/audio cross-modal watch-plus. The
OpenReview supplement ships GradTTS/WaveGrad2/VoiceFlow attack code and an
exact GradTTS LJSpeech `5,977 / 5,977` member/nonmember split; Zenodo publishes
open metadata for the required audio datasets and checkpoints. It still must
not appear as admitted Platform evidence or a Runtime row because it does not
ship ready duration-loss score arrays, ROC arrays, metric JSON, or generated
result graphs, and DiffAudit has not opened a TTS/audio consumer lane. See
[../evidence/durmi-tts-artifact-gate-20260515.md](../evidence/durmi-tts-artifact-gate-20260515.md).

Current FERMI status: Research-only tabular watch. The arXiv source reports
strong multi-relational TabDDPM/TabDiff/TabSyn membership metrics, but the
public surface has no code tree, target/split manifests, generated synthetic
tables, feature/score rows, ROC arrays, metric JSON, or replay command. It must
not appear as admitted Platform evidence or a Runtime row, and it does not
reopen MIDST/tabular execution from scratch. See
[../evidence/fermi-tabular-artifact-gate-20260515.md](../evidence/fermi-tabular-artifact-gate-20260515.md).

Current recon status: recon is the admitted black-box product row. The active
row uses a unified upstream-threshold metric source and reports all four
headline metrics. See
[recon-product-validation-handoff.md](recon-product-validation-handoff.md).
The machine-readable product evidence card is
[`../../workspaces/implementation/artifacts/recon-product-evidence-card.json`](../../workspaces/implementation/artifacts/recon-product-evidence-card.json)
and its contract is documented in
[recon-product-evidence-card.md](recon-product-evidence-card.md).

Current H2 image-to-image simple-distance status: the simple-distance signal has
bounded single-asset evidence on the SD1.5/CelebA-style contract, but it is not
yet a Platform row. Treat it as a Research-side candidate for a future product
bridge comparison against recon. See
[../evidence/h2-img2img-simple-distance-admission-result.md](../evidence/h2-img2img-simple-distance-admission-result.md).
The current product bridge decision is recorded in
[h2-simple-distance-product-bridge-comparison.md](h2-simple-distance-product-bridge-comparison.md).

## Documents

| Document | Purpose |
| --- | --- |
| [runtime.md](runtime.md) | Notes for Runtime integration. |
| [asset-registry-local-api.md](asset-registry-local-api.md) | Data registry contract for Runtime consumers. |
| [local-api.md](local-api.md) | Historical local API notes. |
| [recon-artifact-replay-guidance.md](recon-artifact-replay-guidance.md) | How to interpret recon debug traces. |
| [recon-product-validation-handoff.md](recon-product-validation-handoff.md) | Current product boundary for the promoted recon black-box row. |
| [recon-product-evidence-card.md](recon-product-evidence-card.md) | Machine-readable product card for the admitted recon row. |
| [admitted-evidence-bundle.md](admitted-evidence-bundle.md) | Machine-readable bundle for the complete admitted Platform/Runtime consumer set. |
| [clid-candidate-evidence-card.md](clid-candidate-evidence-card.md) | Machine-readable candidate-only card for the official CLiD CPU score-packet replay and identity blockers. |
| [h2-simple-distance-product-bridge-comparison.md](h2-simple-distance-product-bridge-comparison.md) | Why simple-distance remains Research evidence and what must happen before product consumption. |
| [../evidence/admitted-consumer-drift-audit-20260512.md](../evidence/admitted-consumer-drift-audit-20260512.md) | Latest no-drift audit for the admitted Platform/Runtime consumer boundary. |
| [../evidence/research-boundary-consumability-sync-20260510.md](../evidence/research-boundary-consumability-sync-20260510.md) | Current admitted-vs-candidate boundary for downstream consumers. |

## Integration Rules

- Platform copy must reflect the actual experiment status.
- Don't present smoke tests or negative results as validated audit methods.
- Runtime integration requires stable input/output contracts.
- Before changing schemas or report format across repositories, create a
  handoff note here first.
