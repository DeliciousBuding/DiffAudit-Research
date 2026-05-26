# Source Map

This map records where paper claims are allowed to draw evidence from. It is
not a bibliography; it is a claim-control ledger.

All paths are relative to the Research repository root.

## Primary Result Sources

| Source | Role |
| --- | --- |
| `docs/evidence/admitted-results-summary.md` | Five admitted rows and their limitations. |
| `workspaces/implementation/artifacts/admitted-evidence-bundle.json` | Machine-readable admitted bundle for metrics, costs, boundaries, and finite-tail semantics. |
| `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/adaptive-scores.json` | Row-level score source for admitted PIA AUC uncertainty. |
| `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/adaptive-scores.json` | Row-level score source for admitted PIA dropout-comparator AUC uncertainty. |
| `workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/scores.json` | Row-level target score source for admitted DPDM W-1 AUC uncertainty. |
| `papers/diffaudit-evidence-paper/data/metric_uncertainty.csv` | Generated AUC uncertainty sidecar for rows with direct score arrays or recorded H2 aggregate CIs. |
| `docs/evidence/h2-output-cloud-geometry-20260525.md` | H2 output-cloud geometry candidate, controls, and cross-cache transfer. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json` | Main H2 output-cloud metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json` | Main H2 label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json` | Shared-position seed-offset control metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json` | Shared-position label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json` | Seed-177 shared-position stability metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json` | Seed-177 label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json` | H2 cross-cache transfer metrics. |
| `docs/evidence/h2-img2img-output-cloud-portability-20260525.md` | SD/CelebA img2img portability boundary. |
| `workspaces/black-box/artifacts/h2-img2img-output-cloud-portability-20260525.json` | Machine-readable img2img portability metrics. |
| `docs/evidence/second-asset-contract.md` | Six-gate second-asset contract. |
| `docs/evidence/workspace-evidence-index.md` | Current track state and anti-overclaim boundary. |
| `docs/evidence/reproduction-status.md` | Track-level status table. |

## Support and Negative-Evidence Sources

| Source | Role |
| --- | --- |
| `docs/evidence/rediffuse-stl10-bounded-scout-20260525.md` | Clean split plus weak bounded scout. |
| `docs/evidence/rediffuse-stl10-sima-score-norm-20260525.md` | Different observable on same target remains weak. |
| `docs/evidence/stable-diffusion-rediffuse-collaborator-artifact-20260517.md` | Replayable but source-confounded Stable Diffusion candidate packet. |
| `docs/evidence/feature-packet-channel-consumer-verdict-20260525.md` | Feature-packet lane consumer-boundary deferral. |
| `workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json` | Positive feature-packet metrics with provenance caveat. |
| `docs/evidence/copymark-official-score-artifact-gate-20260515.md` | Official score artifacts and row-binding caveats. |
| `docs/evidence/copymark-laion-mi-public-binding-gate-20260517.md` | Public row-binding failure for CopyMark LAION-mi. |
| `docs/evidence/commoncanvas-denoising-loss-20260513.md` | CommonCanvas conditional denoising-loss scout and stop rule. |
| `workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json` | CommonCanvas 50/50 score packet used for the negative row. |
| `docs/evidence/midst-blending-plus-plus-scout-20260515.md` | Best MIDST result remains below reopen floor. |
| `docs/evidence/secmi-full-split-admission-boundary-review.md` | SecMI stat and NNS support-only metrics and admission boundary. |
| `docs/evidence/secmi-consumer-contract-review-20260512.md` | SecMI/NNS consumer-boundary review. |
| `workspaces/gray-box/artifacts/secmi-full-split-admission-boundary-20260511.json` | Machine-readable SecMI stat/NNS boundary packet. |
| `workspaces/gray-box/artifacts/secmi-admission-contract-hardening-20260511.json` | Machine-readable SecMI support-only hardening record. |
| `docs/evidence/quantile-diffusion-mia-secmia-terror-replay-20260515.md` | Public SecMI-style support packet, not official quantile result. |
| `docs/evidence/identity-focused-inference-extraction-artifact-gate-20260523.md` | Direction C metadata-only no-artifact row. |
| `docs/evidence/rapta-admcd-copying-mitigation-artifact-gate-20260523.md` | Direction C metadata-only mitigation row. |
| `docs/evidence/guard-surgical-mitigation-artifact-gate-20260523.md` | Direction C code-public no-packet row. |
| `docs/evidence/baf-lora-parameter-space-mitigation-gate-20260523.md` | Direction C metadata-only LoRA mitigation row. |
| `docs/evidence/broken-memories-artifact-gate-20260523.md` | Direction C metadata-only memorization row. |
| `docs/evidence/iar-privacy-attacks-artifact-gate-20260523.md` | Direction C code-public cross-family row. |
| `docs/evidence/silent-brush-artarena-artifact-gate-20260523.md` | Direction C metadata-only style-leakage row. |
| `docs/evidence/trajectory-generation-privacy-artifact-gate-20260523.md` | Direction C metadata-only cross-domain row. |
| `docs/evidence/model-will-tell-drc-artifact-gate-20260523.md` | Direction C metadata-only restoration-MIA row. |
| `docs/evidence/discrete-dlm-withdrawn-artifact-gate-20260523.md` | Direction C withdrawn/no-artifact row. |
| `docs/evidence/ronketer-dreambooth-asset-verdict-20260514.md` | Fixed-search batch re-found DreamBooth/LoRA course-notebook artifact gap. |
| `docs/evidence/fseclab-mia-diffusion-code-artifact-gate-20260515.md` | Fixed-search batch re-found official code-public but no replay-packet artifact gap. |
| `papers/diffaudit-evidence-paper/data/negative_support_curated_metrics.csv` | Curated ReDiffuse metric constants mirrored from cited frozen evidence notes. |
| `papers/diffaudit-evidence-paper/data/artifact_corpus_v1.csv` | Machine-readable selected evidence-note corpus and six-gate labels. |
| `papers/diffaudit-evidence-paper/versions/direction-c-fixed-search-batch-20260526.md` | Direction C fixed-search protocol, flow summary, and no-download decision. |
| `papers/diffaudit-evidence-paper/data/artifact_corpus_fixed_search_20260526.csv` | Machine-readable fixed-search rows and six-gate labels. |
| `papers/diffaudit-evidence-paper/data/artifact_gate_summary.csv` | Generated selected-corpus gate-label counts for claim-control drafting. |
| `papers/diffaudit-evidence-paper/data/artifact_strata_summary.csv` | Generated selected-corpus stratum and inclusion-decision counts. |
| `papers/diffaudit-evidence-paper/figures/artifact_gate_summary.pdf` | Generated gate-count figure used in the active manuscript. |
| `references/materials/paper-index.md` | Literature positioning and internal reading map. |

## Forbidden Moves

- Do not cite candidate metrics as admitted evidence.
- Do not report finite empirical tail values as calibrated continuous
  sub-percent FPR.
- Do not claim broad portability from H2 output-cloud geometry.
- Do not call weak bounded scouts failed reproductions unless the audited
  contract actually attempted full paper reproduction.
- Do not invent missing checkpoints, split manifests, p-values, confidence
  intervals, or references.
- Do not imply every admitted row has an AUC interval; uncertainty is reported
  only where direct score arrays or recorded H2 aggregate CIs exist.
- Do not present `papers/diffaudit-evidence-paper/data/artifact_corpus_v1.csv`
  as a complete literature survey;
  it is a structured corpus from existing DiffAudit evidence notes.
- Do not present
  `papers/diffaudit-evidence-paper/data/artifact_corpus_fixed_search_20260526.csv`
  as a field prevalence estimate; it is a small metadata-only fixed-search batch.
- Do not present `papers/diffaudit-evidence-paper/data/artifact_gate_summary.csv`
  or `papers/diffaudit-evidence-paper/figures/artifact_gate_summary.pdf` as public artifact prevalence or
  reproducibility rates; they summarize selected coded rows only.
