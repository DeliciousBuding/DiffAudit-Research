# Evidence Bank

## Admitted Rows

| Track | Method | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Paper role | Caveat |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Black-box | recon DDIM public-100 step30 | 0.837000 | 0.740000 | 0.220000 | 0.110000 | Main | Controlled public-subset/proxy-shadow-member risk proof. |
| Gray-box | PIA GPU512 baseline | 0.841339 | 0.786133 | 0.058594 | 0.011719 | Main | Workspace-verified with adaptive repeats; paper-alignment provenance blocked. |
| Gray-box | PIA with stochastic-dropout | 0.828075 | 0.767578 | 0.052734 | 0.009766 | Defense comparator | Provisional defense, not validated privacy protection. |
| White-box | GSA 1k-3shadow | 0.998192 | 0.989500 | 0.987000 | 0.432000 | Main upper bound | White-box upper-bound comparator. |
| White-box | GSA against DPDM W-1 | 0.488783 | 0.498500 | 0.009000 | 0.000000 | Defense comparator | Bridge frozen; not final benchmark. |

## Admitted Quality/Cost Metadata

These strings are retained in `data/admitted_rows.csv` and the admitted bundle.
They are summarized here so the manuscript can claim retained quality/cost
metadata without adding a wide cost column to the paper table.

| Track | Method | Quality/cost readout |
| --- | --- | --- |
| Black-box | recon DDIM public-100 step30 | 100 public samples per split; DDIM step30; runtime mainline plus unified artifact threshold replay; cuda runtime. |
| Gray-box | PIA GPU512 baseline | attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=212.993833s. |
| Gray-box | PIA with stochastic-dropout | attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=223.128438s. |
| White-box | GSA 1k-3shadow | target_eval_size=2000; shadow_train_size=4200; 3 shadows; cuda. |
| White-box | GSA against DPDM W-1 | target_eval_size=2000; shadow_train_size=6000; classifier=logistic-regression-1d. |

## H2 Output-Cloud Candidate

| Packet | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Role |
| --- | ---: | ---: | ---: | ---: | --- |
| Output-cloud main `512/512` | 0.961529 | 0.900391 | 0.333984 | 0.117188 | Candidate mechanism |
| Raw H2 logistic baseline | 0.905693 | 0.841797 | 0.134766 | 0.000000 | Comparator |
| Lowpass H2 logistic baseline | 0.895679 | 0.831055 | 0.148438 | 0.025391 | Comparator |
| Label shuffle | 0.507595 | 0.521484 | 0.011719 | 0.003906 | Sanity check |
| Shared-position seed 176 | 0.967819 | 0.923828 | 0.410156 | 0.132812 | Order-control |
| Shared-position seed 177 | 0.956192 | 0.896484 | 0.285156 | 0.109375 | Seed stability |
| Transfer seed 176 to 177 | 0.948990 | 0.884766 | 0.375000 | 0.058594 | Cross-cache transfer |
| Transfer seed 177 to 176 | 0.970520 | 0.935547 | 0.390625 | 0.074219 | Cross-cache transfer |

## Boundary and Negative Evidence

| Route | Result | Paper role | Caveat |
| --- | --- | --- | --- |
| H2 img2img portability | Admission AUC `0.7888`, strict-tail `0.0`; stability AUC `0.9600` but below simple distance | Negative boundary | Output-cloud does not cleanly port to SD/CelebA img2img. |
| ReDiffuse STL-10 denoising-loss | AUC `0.4996337890625`, ASR `0.509765625` | Negative | Short bounded scout, not full ReDiffuse reproduction. |
| ReDiffuse STL-10 score-norm | AUC `0.5052947998046875`, ASR `0.525390625` | Negative | Different observable still weak. |
| CommonCanvas/CopyMark denoising-loss | AUC `0.5148`, ASR `0.57` | Negative | Existing `50/50` packet, no expansion released. |
| MIDST Blending++ | AUC `0.598079`, TPR@1%FPR `0.095750` | Related/negative | Best MIDST signal remains below reopen floor. |
| Tracing Roots feature packet | AUC `0.815826`, TPR@1%FPR `0.134000` | Support | Feature-packet only, not raw image audit. |
| Collaborator SD ReDiffuse | AUC `0.710319`; source-only AUC `1.000000` | Support/negative | Cross-source confounding blocks same-distribution claim. |

## Direction C Selected-Corpus Gate Counts

| Corpus | Key readout | Paper role | Caveat |
| --- | --- | --- | --- |
| v1 evidence-note corpus | 21 coded rows; 10 rows pass score/response and metric gates; 1 row passes consumer-boundary gate. | Claim-control support for artifact-corpus framing. | Selected from existing DiffAudit evidence notes; not field-wide prevalence. |
| 2026-05-26 fixed-search batch | 17 coded rows; no row passes target, split, score/response, metric, or consumer-boundary gate. | Metadata-only process trace showing no new admitted row in the frozen batch. | Small fixed-search batch; selected-corpus consistency pass made no CSV label changes, but standalone aggregate claims need broader or second-review evidence. |
