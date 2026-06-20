# Source Map

This map records where paper claims are allowed to draw evidence from. It is not
a bibliography; it is a human-readable view of the generated claim-trace
record. The concrete per-claim rows live in
`papers/diffaudit-evidence-paper/data/claim_trace.csv`; local artifact identity
for the paper workspace lives in
`papers/diffaudit-evidence-paper/data/source_provenance.csv`, including local
SHA-256 hashes, repository commit, tree state, generator command, and
availability tier.

All paths are relative to the Research repository root.
The provenance table is a local packet-identity sidecar for reviewer audit and
regeneration. Local paths, dirty tree state, and generator commands identify the
workspace packet; they do not expand public artifact availability or change any
paper claim surface. Claim changes must be reflected in `claim_trace.csv` and
the allowed wording, not inferred from provenance metadata alone.

## Primary Result Sources

| Source | Role |
| --- | --- |
| `docs/evidence/admitted-results-summary.md` | Five reportable rows and their limitations. |
| `workspaces/implementation/artifacts/admitted-evidence-bundle.json` | Machine-readable reportable bundle for metrics, costs, required access, report roles, boundaries, and finite-tail semantics. |
| `papers/diffaudit-evidence-paper/data/claim_trace.csv` | Generated per-claim trace records: source artifact, replay tier, six explicit gate columns, first blocker, state, and allowed wording. |
| `papers/diffaudit-evidence-paper/data/source_provenance.csv` | Generated artifact identity table with local SHA-256 hashes, repository commit IDs, tree state, generator command, and availability tiers. |
| `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/adaptive-scores.json` | Row-level score source for admitted PIA AUC uncertainty. |
| `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/adaptive-scores.json` | Row-level score source for admitted PIA dropout-comparator AUC uncertainty. |
| `workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/scores.json` | Row-level target score source for admitted DPDM W-1 AUC uncertainty. |
| `papers/diffaudit-evidence-paper/data/metric_uncertainty.csv` | Generated AUC uncertainty sidecar for rows with direct score arrays or recorded H2 aggregate CIs. |
| `docs/evidence/h2-output-cloud-geometry-20260525.md` | H2 output-cloud geometry candidate, controls, and same-family cache robustness. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json` | Main H2 output-cloud metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json` | Main H2 label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json` | Shared-position seed-offset control metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json` | Shared-position label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json` | Seed-177 shared-position stability metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json` | Seed-177 label-shuffle sanity metrics. |
| `workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json` | H2 same-family cache-robustness metrics; raw path name is provenance. |
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
| `papers/diffaudit-evidence-paper/versions/direction-c-broader-source-pass-20260527.md` | Direction C no-download Hugging Face Hub, Zenodo, and OpenReview metadata-screening/query pass. |
| `papers/diffaudit-evidence-paper/data/artifact_corpus_broader_source_20260527.csv` | Machine-readable broader-source metadata observations; metadata-screening/query hygiene only, not source-completeness or prevalence evidence. |
| `papers/diffaudit-evidence-paper/versions/direction-c-targeted-artifact-link-pass-20260527.md` | Direction C targeted artifact-link pass over existing metadata-only seeds; three L1 public artifact surfaces, not score/metric replay. |
| `papers/diffaudit-evidence-paper/data/artifact_corpus_targeted_artifact_links_20260527.csv` | Machine-readable targeted artifact-link rows; non-pooled L1 inspection evidence only. |
| `papers/diffaudit-evidence-paper/data/artifact_gate_summary.csv` | Generated selected-corpus gate-label counts for claim-control drafting. |
| `papers/diffaudit-evidence-paper/data/artifact_strata_summary.csv` | Generated selected-corpus stratum and inclusion-decision counts. |
| `papers/diffaudit-evidence-paper/figures/artifact_gate_summary.pdf` | Generated gate-count support figure; kept as paper-workspace evidence, while the active manuscript now summarizes the counts in text to preserve page budget and visual clarity. |
| `docs/internal/e1-ndss324-zenodo-manifest-preflight-2026-06-08.md` | NDSS-324 / Zenodo full-ZIP manifest-first preflight; verified archive integrity but no row-id, public score/response packet, metric JSON/ROC, or verifier. |
| `docs/internal/e1-manifest-first-scout-2026-06-06.md` | E1 manifest-first scout ledger including CopyMark, Tracing the Roots, Quantile, and NDSS-324 route decisions. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_e.md` | Pass E current arXiv/GitHub primary-source refresh; five current-title checks and zero new row-bound public score/response artifacts. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.md` | High-value public asset identity refresh over NDSS-324, CopyMark, MoFit, MIA_SD, SAMA, MIA-EPT, Diffusion MIA, ReMIA, and OpenLVLM-MIA; 9/9 identities matched, with zero compact reopen hints and zero new row-bound score/response artifacts. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_refresh_2026_06_09.csv` | Machine-readable high-value delta refresh table; source identity and reopen-hint sidecar only, not admission or prevalence evidence. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_watchlist_2026_06_09.csv` | Watchlist input for the high-value delta refresh; source-refresh hygiene only, not a C14/N50/admitted-evidence or compute-release upgrade. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv` | Four-row follow-up queue for sidecar/manual-review hints; not a public score/response artifact and not a compute-release queue. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct028_sdmia_public_surface_check_2026_06_08.md` | SD-MIA public code-surface check; support-only code-public pre-training T2I MIA reference, not a denominator or admitted row. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2_miasd_result_file_preflight_2026_06_08.md` | MIA_SD file-level result preflight; public result-like files remain non-admitted because row IDs, score schema, metric JSON, checkpoint identity, and no-training verifier are missing. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct029_mia_sd_public_surface_check_2026_06_08.md` | MIA_SD C14-v2 planning check; candidate public-result surface only, not current C14/N50/admitted evidence. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct031_sama_dlm_public_surface_check_2026_06_09.md` | SAMA DLM public-code check; support-only DLM/text surface, not a score/response asset, denominator row, admitted row, or compute-release target. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct032_miaept_tabular_public_surface_check_2026_06_09.md` | MIA-EPT tabular public-result-page check; support-only tabular-diffusion surface, not a score/response asset, denominator row, admitted row, or compute-release target. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct033_diffusion_mia_public_surface_check_2026_06_09.md` | Diffusion MIA public code-and-split check; support-only black-box diffusion MIA surface, not a score/response asset, denominator row, admitted row, or compute-release target. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md` | ReMIA tabular public result-archive check; support-only aggregate-result surface, not a score/response asset, denominator row, admitted row, or compute-release target. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md` | OpenLVLM-MIA VLM controlled-benchmark scout; future VLM stratum only, not current Direction A image-diffusion evidence, C14/N50, a second public score/response asset, or a compute-release target. |
| `docs/internal/e2-n50-freeze-preflight-2026-06-06/e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.csv` | Machine-readable OpenLVLM-MIA no-download gate readout; public labels/model/code with runtime score outputs only and wrong current consumer lane. |
| `papers/diffaudit-evidence-paper/versions/direction-a-mofit-public-score-surface.md` | Paper-facing MoFit boundary note; support-only public score-surface replay blocked by row-binding and target-identity gates. |
| `papers/diffaudit-evidence-paper/data/mofit_public_score_metrics.json` | Derived MoFit replay metrics and controls; workspace audit output, not official metric JSON or admitted row binding. |
| `papers/diffaudit-evidence-paper/data/mofit_public_gate_status.csv` | Generated six-gate status for the MoFit public score-surface replay; machine-readable support-only boundary, not an admission decision. |
| `references/materials/paper-index.md` | Literature positioning and internal reading map. |

## Replay and Availability Matrix

This matrix is the paper-workspace replay boundary. It records what can be
replayed from row-level scores or frozen response artifacts, what is only a
source-documented point estimate, and what availability tier applies. It does
not imply that every source is already packaged as an anonymous public
supplement.

| Row or packet | Replay tier | Replay surface in this workspace | Paper use | Availability boundary |
| --- | --- | --- | --- | --- |
| Recon DDIM public-100 step30 | Source-documented point estimate | Unified/reportable bundle metric row plus `docs/evidence/recon-product-validation-result.md`. | Black-box proxy point estimate only. | Availability tier: research-workspace source documentation plus generated paper CSV. No separate row-level score array is committed in the paper workspace; report as a controlled public-subset/proxy-shadow risk signal, not a full exploit, product claim, or public benchmark. |
| PIA GPU512 baseline | Workspace row-score replay | `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/adaptive-scores.json`. | Admitted gray-box baseline with bootstrap AUC sidecar. | Availability tier: research-workspace row-score array plus generated paper sidecar. Checkpoint/source provenance caveat remains attached; no statistical dominance claim. |
| PIA + stochastic dropout | Workspace row-score replay | `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/adaptive-scores.json`. | Admitted provisional defense comparator with bootstrap AUC sidecar. | Availability tier: research-workspace row-score array plus generated paper sidecar. Not validated privacy protection. |
| GSA 1k-3shadow | Source-documented point estimate | Unified/reportable bundle metric row plus GSA summary/gradient artifacts. | Reportable white-box upper-bound comparator only. | Availability tier: research-workspace source documentation plus generated paper CSV. Direct row-level score array is not committed in the paper workspace; keep as point estimate and upper-bound/comparator evidence, not a leaderboard winner. |
| GSA against DPDM W-1 | Workspace target-score replay | `workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/scores.json`. | Target-score defense bridge with bootstrap AUC sidecar. | Availability tier: research-workspace target-score array plus generated paper sidecar. Target score arrays are `1000/1000`; `target_eval_size=2000` is total target evaluation size, not a nonmember denominator. |
| H2 output-cloud 512/512 and controls | Frozen response/aggregate replay | Frozen H2 JSON artifacts listed above plus recorded aggregate CIs. | Non-admitted response-geometry candidate and failed admission stress test. | Availability tier: research-workspace response-metric artifacts plus generated paper CSV. Same response-contract family only; SD/CelebA img2img portability is insufficient for admission and no consumer-boundary admission path exists. |
| MoFit public COCO score files | Workspace replay over public score-file positions | `papers/diffaudit-evidence-paper/data/mofit_public_score_metrics.json` and related `mofit_public_*` sidecars generated from official public text files. | Support-only public score-surface replay only. | Availability tier: public score files plus workspace-derived replay sidecars. Missing explicit score row IDs, immutable public target checkpoint identity, official metric JSON/ROC, and manifest-certified caption/score row binding block admitted-evidence, N50, C14, second-asset, and compute-release claims. |

## Allowed Claim Boundaries

| Surface | Allowed wording | Blocked upgrade |
| --- | --- | --- |
| Candidate metrics | Candidate or support evidence with the first missing gate attached. | Admitted evidence wording without a passing target/split/score/metric/consumer packet. |
| Finite empirical tails | Denominator-count packet summaries tied to the recorded nonmember count. | Calibrated continuous sub-percent FPR language. |
| H2 output-cloud geometry | High-AUC non-admission response-geometry stress test. | Broad portability or consumer admission from same-family response geometry. |
| Bounded weak scouts | Route-local negative or support findings under the audited contract. | Full paper-reproduction failure claims without a full reproduction contract. |
| Missing checkpoints, split manifests, p-values, intervals, or references | Named unresolved surfaces in claim traces and source notes. | Filled-in artifact, statistic, or reference claims without a source row. |
| Uncertainty sidecars | AUC intervals where direct score arrays or recorded H2 aggregate CIs exist. | Universal interval wording for every admitted row. |
| `data/artifact_corpus_v1.csv` | Structured corpus from existing DiffAudit evidence notes. | Complete literature-survey coverage. |
| `data/artifact_corpus_fixed_search_20260526.csv` | Small metadata-only fixed-search batch. | Field prevalence estimate. |
| `data/artifact_corpus_targeted_artifact_links_20260527.csv` | Three non-pooled L1 artifact-inspection surfaces recovered from metadata-only seeds. | Score replay, admitted evidence, or pooled denominator wording. |
| `data/artifact_gate_summary.csv` and `figures/artifact_gate_summary.pdf` | Selected coded-row summaries. | Public artifact prevalence or reproducibility-rate claims. |
| MoFit, NDSS-324, SD-MIA, MIA_SD, and targeted discovery passes | Support-only route closures and claim-hygiene evidence. | C14 row-count, N50 denominator, admitted-evidence, second-asset, or compute-release upgrades. |
| Current-source refresh passes | Targeted route-closure evidence for the current packet. | Field-wide absence proof. |
