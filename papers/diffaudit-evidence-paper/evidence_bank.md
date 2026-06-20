# Evidence Bank

## Reportable Rows

| Track | Method | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Paper role | Caveat |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Black-box | recon DDIM public-100 step30 | 0.837000 | 0.740000 | 0.220000 | 0.110000 | Main | Controlled public-subset/proxy-shadow-member risk evidence. |
| Gray-box | PIA GPU512 baseline | 0.841339 | 0.786133 | 0.058594 | 0.011719 | Main | Workspace-verified with adaptive repeats; paper-alignment provenance blocked. |
| Gray-box | PIA with stochastic-dropout | 0.828075 | 0.767578 | 0.052734 | 0.009766 | Defense comparator | Provisional defense, not validated privacy protection. |
| White-box | GSA 1k-3shadow | 0.998192 | 0.989500 | 0.987000 | 0.432000 | White-box comparator upper bound only | White-box upper-bound comparator; not an access-level winner. |
| White-box | GSA against DPDM W-1 | 0.488783 | 0.498500 | 0.009000 | 0.000000 | Defense comparator | Bridge frozen; not final benchmark. |

## Reportable Quality/Cost Metadata

These strings are retained in `data/admitted_rows.csv` and the reportable bundle.
They are summarized here so the manuscript can claim retained quality/cost
metadata without adding a wide cost column to the paper table.

| Track | Method | Quality/cost readout |
| --- | --- | --- |
| Black-box | recon DDIM public-100 step30 | 100 public samples per split; DDIM step30; source-documented public-100 threshold readout; no row-score array retained; CUDA. |
| Gray-box | PIA GPU512 baseline | attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=212.993833s. |
| Gray-box | PIA with stochastic-dropout | attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=223.128438s. |
| White-box | GSA 1k-3shadow | target_eval_size=2000 (1000 member + 1000 nonmember); shadow_train_size=4200; 3 shadows; cuda. |
| White-box | GSA against DPDM W-1 | target_eval_size=2000 (1000 member + 1000 nonmember); shadow_train_size=6000; classifier=logistic-regression-1d. |

## H2 Output-Cloud Candidate

| Packet | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Role |
| --- | ---: | ---: | ---: | ---: | --- |
| Output-cloud main `512/512` | 0.961529 | 0.900391 | 0.333984 | 0.117188 | Candidate observable |
| Raw H2 logistic baseline | 0.905693 | 0.841797 | 0.134766 | 0.000000 | Comparator |
| Lowpass H2 logistic baseline | 0.895679 | 0.831055 | 0.148438 | 0.025391 | Comparator |
| Label shuffle | 0.507595 | 0.521484 | 0.011719 | 0.003906 | Sanity check |
| Shared-position seed 176 | 0.967819 | 0.923828 | 0.410156 | 0.132812 | Order-control |
| Shared-position seed 177 | 0.956192 | 0.896484 | 0.285156 | 0.109375 | Seed stability |
| Cache-reuse seed 176 to 177 | 0.948990 | 0.884766 | 0.375000 | 0.058594 | Same-family cache-reuse stability |
| Cache-reuse seed 177 to 176 | 0.970520 | 0.935547 | 0.390625 | 0.074219 | Same-family cache-reuse stability |

## AUC Uncertainty Sidecar

`data/metric_uncertainty.csv` reports AUC intervals only where the paper
workspace has direct row-score arrays or an upstream artifact already records
aggregate CIs. It is a sidecar for reviewer-facing stability checks, not a new
admission criterion. Recon public-100 and GSA mainline remain point estimates
in this manuscript because the committed paper workspace does not expose direct
method-level score arrays for them without additional assumptions.
The CSV explicitly records `uncertainty_source`, `recomputed_or_recorded`,
`bootstrap_unit`, `score_array_hash`, and `eligible_claims` so row-bootstrap
intervals and recorded H2 aggregate intervals cannot be interpreted as the same
evidence tier.

| Row | AUC | 95% interval | Method | Caveat |
| --- | ---: | ---: | --- | --- |
| Gray-box PIA | 0.841339 | [0.816756, 0.863957] | Stratified row bootstrap over adaptive mean scores. | Admitted row only; no cross-asset dominance claim. |
| PIA + G-1 dropout | 0.828075 | [0.803872, 0.853547] | Stratified row bootstrap over adaptive mean scores. | Defense-comparator interval only. |
| DPDM W-1 | 0.488783 | [0.463983, 0.515163] | Stratified row bootstrap over target scores with admitted-score orientation. | Target-score defense-bridge interval only; not final defense benchmark. |
| H2 output-cloud 512/512 | 0.961529 | [0.950939, 0.972625] | Recorded artifact aggregate CI. | Candidate-side interval; does not change admission state. |
| H2 shared-position seed176 | 0.967819 | [0.953779, 0.983615] | Recorded artifact aggregate CI. | Same response-family control only. |
| H2 shared-position seed177 | 0.956192 | [0.941745, 0.970779] | Recorded artifact aggregate CI. | Same response-family stability only. |
| H2 cache-reuse stability 176 to 177 | 0.948990 | [0.930007, 0.966854] | Recorded artifact aggregate CI. | Same-family cache-reuse stability; not cross-model portability. |
| H2 cache-reuse stability 177 to 176 | 0.970520 | [0.957806, 0.982849] | Recorded artifact aggregate CI. | Same-family cache-reuse stability; not cross-model portability. |

## H1 Activation-Subspace Candidate (2026-06-20)

| Packet | AUC | TPR@1%FPR | TPR@0.1%FPR | Role |
| --- | ---: | ---: | ---: | --- |
| CUDA DDPM 800k, N=64 scout | 0.874 | 0.484 | 0.000 | White-box activation scout |
| CUDA DDPM 800k, N=128 scale-up | 0.873 | 0.055 | 0.000 | Candidate-positive / low-FPR-fragile |
| CUDA DDIM 750k, N=128 cross-ckpt | 0.841 | 0.078 | 0.000 | Cross-checkpoint generalization |

| Control | DDPM 800k | DDIM 750k |
| --- | :---: | :---: |
| Label shuffle AUC | 0.486 | 0.504 |
| Ablation (drop any site) | 0.867–0.879 | — |

**Claim allowed**: Internal UNet activations carry stable, generalizable membership signal (AUC=0.841–0.873 across two checkpoints) with a mechanistically distinct white-box observable (non-gradient, non-loss).

**Claim blocked**: Reliable low-FPR membership inference. TPR@1%FPR collapses under scale-up (0.484→0.055) and remains below 0.1 across all configs.

**H4 status**: Not released. Signal distributed across UNet sites; no compact risky subspace identified.

## Boundary and Negative Evidence

| Route | Result | Paper role | Caveat |
| --- | --- | --- | --- |
| SD/CelebA img2img portability | Admission AUC `0.7888`, strict-tail `0.0` (`n0=25`); small 10/10 stability cache AUC `0.9600` | Negative boundary | Output-cloud does not cleanly port to SD/CelebA img2img or establish a portable audit row. |
| ReDiffuse STL-10 denoising-loss | AUC `0.4996337890625`, ASR `0.509765625` | Negative | Short bounded scout, not full ReDiffuse reproduction. |
| ReDiffuse STL-10 score-norm | AUC `0.5052947998046875`, ASR `0.525390625` | Negative | Different observable still weak. |
| CommonCanvas denoising-loss | AUC `0.5148`, ASR `0.57` | Negative | Existing `50/50` packet associated with CopyMark/CommonCanvas materials; no expansion released. |
| MIDST Blending++ | AUC `0.598079`, TPR@1%FPR `0.095750` | Related/negative | Tabular benchmark surface and weak image-diffusion relevance block admission. |
| Tracing the Roots feature packet | AUC `0.815826`, TPR@1%FPR `0.134000` | Support | Feature-packet only, not raw image audit. |
| Separately supplied SD ReDiffuse | AUC `0.710319`; source-only AUC `1.000000` | Support/negative | Cross-source confounding blocks same-distribution claim. |

## 2026-06-08 Public-Surface Refresh Ledger

These rows explain recent candidate decisions. They are paper-facing support and
route-closure evidence only; none changes the admitted rows, current C14
selected-row count, N50 external denominator, second-asset status, or
compute-release status.

| Surface | Current readout | Paper role | Caveat |
| --- | --- | --- | --- |
| MoFit COCO public score files | Workspace replay of public score files gives AUC `0.941948`, ASR `0.883`, TPR@1%FPR `0.488`, and TPR@0.1%FPR `0.324`. | Support-only public score-surface replay. | Missing explicit score row IDs, immutable public target checkpoint identity, official metric JSON/ROC, and manifest-certified row binding; not admitted evidence, C14, N50, second asset, or compute release. |
| NDSS-324 / Zenodo `10.5281/zenodo.13371475` | Full ZIP integrity verified; nested dataset payloads expose `image` and `text` fields, not immutable row IDs; no public score-vector, ROC, metric JSON, generated-response, or verifier files were found. | Compute-gated E1 candidate with useful artifact-boundary evidence. | Verified archive integrity does not repair missing row-bound score/response and metric/verifier surfaces. |
| SD-MIA | Public CVF paper and official code tree are relevant and current, but the committed tree lacks original/perturbation JSONs, attack-result JSON, per-row scores, generated responses, ROC/metric JSON, split manifest, and verifier. | Support-only code-public pre-training T2I MIA reference. | Not C14, not N50, not admitted evidence, and not compute release. |
| MIA_SD | Public result-like files include training-loss and pickle/PGF artifacts; static evidence observes ROC-related keys and a reported mean ROC AUC line. | C14-v2 candidate public-result surface. | Missing immutable row IDs, score schema, metric JSON, public target checkpoint identity, safe verifier format, and public experiment images; does not change current C14/N50/admission state. |
| Targeted discovery pass E | Five current arXiv/GitHub primary-source refresh rows checked; zero new row-bound public score/response artifacts. | Source-refresh hygiene and route closure. | Not prevalence evidence and not a proof that future public assets cannot appear. |

## Direction C Selected-Corpus Gate Counts

Direction C separates claim-support levels before interpreting counts:
metadata-only discovery, artifact inspection, scoreable or replayed
research-side measurement, and consumer-admitted evidence. Metadata-only
fixed-search rows are not pooled with replay rows as a reproducibility
denominator.

| Corpus | Key readout | Paper role | Caveat |
| --- | --- | --- | --- |
| v1 evidence-note corpus | 21 coded rows; 10 rows pass score/response and metric gates; 1 row passes consumer-boundary gate. | Claim-control support for selected claim-support framing. | Selected from existing DiffAudit evidence notes; not field-wide prevalence. |
| 2026-05-26 fixed-search batch | 17 coded metadata/search observations; no row passes target, split, score/response, metric, or consumer-boundary gate. | Metadata-only process trace showing no new admitted row in the frozen batch. | Small fixed-search batch; the selected-corpus consistency pass and bounded second-pass label review are internal label-hygiene checks. They found no admitted-like fixed-search row or metadata-batch evidence/metric promotion and adopted two tightenings: `v1-10.delta_gate=Fail` and `fs20260526-arxiv-03.target_gate=Fail`. Standalone aggregate claims need larger distinct-surface corpus evidence; reliability claims need external label audit. |
| 2026-05-27 broader-source API pass | 10 coded source-query observations over HF/Zenodo/OpenReview; zero new distinct artifact surfaces and zero admitted rows. | Metadata-screening/query hygiene showing empty/noisy/duplicate metadata states under no-download rules. | Does not support source-completeness, artifact inspection, replayability, prevalence, or standalone corpus-breadth claims. Stronger standalone aggregate claims still need a larger distinct-surface corpus; reliability claims need external label audit. |
| 2026-05-27 targeted artifact-link pass | 3 L1 public artifact surfaces recovered from existing metadata-only seeds: one HF dataset split artifact, one official SecMI code/split tree, and one official MIDM code/protocol surface. | Non-pooled L1 artifact-inspection evidence. | No score replay, metric reproduction, admission, prevalence, or pooled denominator; no row-score array, response/feature packet, ROC, metric JSON, checkpoint hash, or verifier packet was observed. |

Internal label audit plus bounded second-pass label review on 2026-05-26: the
consistency pass found no invalid gate labels or route-changing contradictions,
and the bounded second pass found no admitted-like fixed-search row or
metadata-batch evidence/metric promotion. The second pass recorded four
reviewer disagreements, adopted two tightenings, and explicitly did not adopt
the admitted-bundle `Pass -> Partial` proposal because the row is a mixed-replay
positive control. This is label-hygiene evidence only, not independent
inter-rater reliability.
