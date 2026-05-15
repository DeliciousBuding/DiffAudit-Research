# Research Task Queue

> Last refreshed: 2026-05-15

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `GitHub lightweight diffusion MIA triage completed` |
| Active GPU task | none running |
| Next GPU candidate | none selected |
| CPU sidecar | none selected after GitHub lightweight diffusion MIA triage |
| Gray-box status | PIA remains admitted; tri-score is positive-but-bounded internal candidate; ReDiffuse candidate-only; Fashion-MNIST SimA score-norm and score-Jacobian sensitivity weak |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| GitHub lightweight diffusion MIA repos | intake / Lane A | false-positive triage | four direct GitHub search hits were checked: acha1934 fine-tuned diffusion MIA, KarinMalka1 personalization forensics, abramwit Boeing 707 toy project, and josephho9 empirical-score MNIST prototype | no public checkpoint-bound target, immutable target member/nonmember manifest, row-bound response packet, score rows, ROC arrays, metric JSON, trained attack weights, or verifier; some require Colab/Google Drive/local training | keep as anti-duplication evidence only; do not download notebooks/images/models/Drive payloads, run scripts, train/fine-tune, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| DEB medical diffusion MIA | gray-box / Lane B | paper-source-only mechanism watch | MDPI Applied Sciences 2026 article reports Discrete Encoding-Based grey-box intermediate-trajectory metrics against SecMI, PIA, and SimA on CIFAR/TinyImageNet and MedMNIST2D subsets | no public code, target checkpoint hashes, immutable member/nonmember manifests, intermediate-state packet, score rows, ROC arrays, metric JSON, or verifier; requires intermediate generation-state access rather than final images only | keep as mechanism watch only; do not download MedMNIST/CIFAR/TinyImageNet/Stable Diffusion assets, implement DEB from the paper, release GPU/CPU sidecar, or promote Platform/Runtime rows |
| same-noise residual comparator family | black-box | candidate-only / hold | seed-12 and seed-23 `64/64` packets retain signal, but low/full residual comparators match or beat mid-band on AUC | single DDPM/CIFAR10 asset, finite tails, no product boundary, mid-frequency specificity not supported | stop same-contract GPU expansion; reopen only with new comparator, second asset, or protocol |
| black-box second response-contract acquisition | black-box | hold / stale skeleton | old Pokemon/Kandinsky skeleton probe returns `needs_query_split`; later CommonCanvas second-response-contract packets were executed and weak across pixel, CLIP, prompt-consistency, response-stability, and denoising-loss scorers | the old skeleton is not the active next lane and filling it would not by itself create a clean second asset | reopen only with a genuinely new public target identity plus exact member/nonmember query images and response/score coverage; do not keep filling the stale Pokemon/Kandinsky template |
| gray-box tri-score successor | gray-box | hold | X-88/X-141/X-142 tri-score truth-hardening closed positive-but-bounded | same-contract expansion would not change admission or product story | reopen only with a genuinely new scorer, surface, or adaptive/low-FPR falsifier |
| Kandinsky/Pokemon response-contract package | black-box | hold / stale skeleton | package preflight is executable but only proves the old skeleton shape | missing query split, endpoint contract, response manifest, and responses; superseded by later weak second-response-contract evidence | do not use this as the default next action; reopen only if real `25/25` or larger member/nonmember query images and responses appear for a clean non-CommonCanvas asset |
| ReDiffuse future reopen | gray-box | hold | exact replay shows modest AUC but weak strict-tail evidence | no admitted promotion; 800k shortcut remains blocked | reopen only with new scorer hypothesis or stricter paper-faithful contract |
| SecMI admission contract | gray-box | structural-support-only | full-split stat/NNS evidence is strong and evidence-ready; consumer review completed | not admitted; NNS product semantics, adaptive comparability, provenance language, and bundle schema fit remain blocked | keep validators active; no new metrics or promotion until a new schema/adaptive protocol exists |
| CPSample defense artifact | defense / Lane A-B | defense watch-plus | OpenReview ICLR 2025 supplement exposes diffusion/classifier code, configs, training/sampling/inference-attack runners, and four small attack-loss text fragments | no immutable denoiser/classifier checkpoint hashes, exact subset-index manifests, row-bound protected/unprotected score packet, ROC arrays, AUC/ASR/TPR-at-FPR metrics, retained-utility metric contract, or ready verifier | keep as defense watch-plus only; do not download CIFAR-10/CelebA/LSUN/Stable Diffusion/checkpoint/image assets, run `python main.py`, launch CPU/GPU sidecars, or promote defense rows |
| DSiRe / LoRA-WiSE dataset-size recovery | gray-box / Lane A-B | weight-only semantic-shift watch | official `MoSalama98/DSiRe` code and public non-gated HF `MoSalama98/LoRA-WiSE` benchmark expose `7` configs, `2,050` LoRA fine-tuned model rows, `101` parquet shards, and reported dataset-size recovery `MAE = 0.36` images | aggregate LoRA fine-tuning dataset-size recovery, not per-sample membership; no member/nonmember query rows, generated response packet, AUC/ASR/TPR-at-FPR metrics, or current Platform/Runtime consumer semantics | keep as future weight-only privacy lane candidate only; do not download LoRA-WiSE data/images/model/tensors, run `dsire.py`, release GPU/CPU sidecar, or promote Platform/Runtime rows |
| Hyperparameter-free SecMI reproduction | gray-box / Lane A | third-party SecMI-family support-only | `mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models` exposes code, notebook/report surface, and claimed CIFAR-100 seed-0 improvements over baseline SecMINNs | same-family SecMI support; no reusable score rows, ROC arrays, metric JSON, trained attacker weights, verifier packet, independent target checkpoint, or immutable split manifest | keep as anti-duplication support gate only; do not clone, download CIFAR/SecMI checkpoints, run `python run.py`, train attackers, release GPU, or promote Platform/Runtime rows |
| DME dual-model entropy | gray-box / Lane A | stub-repo-only watch | official `F-YaNG1/DME` repo claims complexity-induced bias debiasing for diffusion-model MIA | repo is README-only with no linked paper, implementation code, split manifests, checkpoints, score rows, ROC arrays, metric JSON, figures, or verifier | keep as Research-only watch; do not infer missing method details, implement DME, train dual models, release GPU, or promote Platform/Runtime rows |
| FreMIA frequency-filter MIA | gray-box / Lane A | paper-source-plus-stub-repo watch | ICML 2026 direct diffusion MIA; arXiv source reports strong frequency-filter table metrics and rendered ROC/score figures; official `poetic2/FreMIA` repo exists | official repo is README-only; no implementation code, immutable member/hold-out split manifests, target checkpoints, generated samples, score rows, machine-readable ROC arrays, metric JSON, or verifier | keep as Research-only mechanism watch; do not download datasets/weights/checkpoints, implement filter, run Naive/SecMI/PIA/CLiD variants, release GPU, or promote Platform/Runtime rows |
| CopyMark official score artifacts | black-box / Lane A | official score-artifact support-only | official `caradryanl/CopyMark` repo exposes member/nonmember image logs, aggregate ROC/threshold JSONs, selected PIA/PFAMI/SecMI score tensors, GSA feature/XGBoost files, and LAION-RiDAR/mixing results; sampled official artifacts include SD1.5 PIA test `AUROC = 0.766974`, LDM PFAMI test `AUROC = 0.915734`, and LAION-RiDAR test `AUROC = 0.872135` | no checkpoint hashes, compact row-ID-bound score manifest, small immutable data/checkpoint packet, or ready verifier output; sdxl/CommonCanvas artifacts remain weak or threshold-transfer inconsistent | keep as Research-side support evidence; do not download HF `datasets.zip`, images, model folders, full repo, run CopyMark scripts, release GPU, or promote Platform/Runtime rows |
| Quantile Diffusion MIA SecMI `t_error` replay | gray-box / Lane A-B | candidate-support-only | third-party public CIFAR10/CIFAR100 SecMI-style score rows and split manifests replay from committed files with positive AUC | not official Quantile Regression paper output; same-family SecMI support only; no admitted-row consumer contract | keep as support evidence only; do not clone full repo, download DDPM/CIFAR/SharePoint assets, train, fit quantile models, or release GPU |
| DualMD / DistillMD disjoint-split defense | defense / Lane A-B | defense watch-plus | OpenReview DDMD supplement exposes DDPM/LDM defense code, DDPM split-index files, and FID stats | embedded GitHub origin is not public; no checkpoint-bound defended/undefended scores, ROC arrays, metric JSON, generated response packets, or ready verifier are released | keep as defense watch-plus only; do not download SharePoint Pokemon, Stable Diffusion, CIFAR/STL/Tiny-ImageNet assets, train, run attack scripts, or release GPU |
| DIFFENCE classifier defense | defense / Lane A-B | defense watch-plus | official repo exposes code, configs, and split-index files | protected target is an image classifier, diffusion is only a pre-inference defense component, and no checkpoint-bound defended/undefended logits, score rows, ROC arrays, metric JSON, or ready verifier are committed | keep as classifier-defense watch-plus only; do not download Google Drive checkpoints/datasets, train, run MIA scripts, or release GPU |
| MIAHOLD / HOLD++ higher-order Langevin defense | defense / Lane A-B | defense watch-plus | official MIAHOLD repos expose higher-order Langevin defense code, audio split filelists, a CIFAR HOLD config, and PIA-style attack code | no checkpoint-bound target artifact, reusable score rows, ROC arrays, metric JSON, generated responses, or ready verifier | keep as defense watch-plus only; do not download Google Drive checkpoints/datasets, scrape W&B, train HOLD++ models, or release GPU |
| MT-MIA relational diffusion score packet | intake / Lane A | relational-tabular support-only | official `joshward96/MT-MIA` repo exposes multi-table member/nonmember/reference splits, pre-generated ClavaDDPM and RelDiff synthetic outputs, and `18` MT-MIA score/metric JSONL packets | outside current image/latent Platform/Runtime boundary; packets lack row-ID-bound score manifests and no relational-tabular consumer schema exists | keep as Research-only support evidence; do not download raw/synthetic data, full repo, or training assets, regenerate RelDiff, release GPU, or promote Platform/Runtime rows |
| VAE2Diffusion latent-space inversion | gray-box / Lane A | code-public latent-space MIA watch-plus | official `mx-ethan-rao/VAE2Diffusion` repo exposes decoder-geometry / latent-dimension filtering code and LDM/SD scripts; arXiv source claims public splits/checkpoints | README split/checkpoint link is empty; no GitHub releases; recursive tree has no split/checkpoint/score/ROC/metric/response/verifier artifacts; scripts require author-local paths and from-scratch training/fine-tuning/cache generation | keep as latent-space mechanism watch; do not download datasets/models/checkpoints/caches, train/fine-tune, run SimA/PFAMI/PIA variants, release GPU, or promote Platform/Runtime rows |
| DCR copying / replication | intake / Lane A | copying/memorization semantic-shift watch-plus | official `somepago/DCR` repo exposes diffusion replication/copying code, retrieval/similarity scripts, metric helpers, and a committed LAION caption manifest | README LAION-10k Drive split link returns `404`; claim is copying rather than per-sample MIA; no immutable member/nonmember MIA split, target checkpoint, generated response package, score rows, ROC arrays, metric JSON, or ready verifier | keep as copying/privacy watch only; do not download LAION/Drive/model assets, fine-tune, infer, run retrieval, release GPU, or promote Platform/Runtime rows |
| FCRE medical frequency MIA | gray-box / Lane A-B | paper-source-only / cross-domain watch | arXiv `2506.14919` reports frequency-calibrated reconstruction-error MIA metrics on FeTS 2022, ChestX-ray8, and CIFAR-10 | no official code, immutable split manifests, target checkpoints, generated reconstruction packets, score rows, ROC arrays, metric JSON, or ready verifier | keep as method context only; do not download FeTS/ChestX-ray8/CIFAR, train targets, run DDIM reconstruction, sweep frequency bands, release GPU, or promote Platform/Runtime rows |
| Tabular Privacy Leakage TDM | intake / Lane A | single-table tabular watch-plus | arXiv `2605.06835` links official `VectorInstitute/midst-toolkit`; the toolkit exposes ClavaDDPM training/synthesis, Tartan Federer/Ensemble/EPT attacks, privacy/quality metrics, examples, and small integration-test TabDDPM fixtures | no paper-bound Berka/Diabetes target checkpoints, immutable split manifests, generated synthetic tables, score rows, ROC arrays, metric JSON, or ready verifier; current scope lacks a tabular consumer boundary | keep as Research-only watch-plus; do not download Berka/Diabetes/MIDST resources, train targets/shadows, run attacks, release GPU, or promote Platform/Runtime rows |
| Shake-to-Leak code artifact | intake / Lane A | code-public watch-plus | official `VITA-Group/Shake-to-Leak` repo exposes fine-tuning-amplified generative privacy code, vendored SecMI/diffusers code, fine-tuning scripts, SecMI scripts, data extraction code, and a `40`-domain person list | no frozen SD-v1-1 fine-tuned checkpoint, immutable member/nonmember manifest, generated private-set packet, generated attack response, score array, ROC array, metric JSON, or ready verifier output; using it would require SD weights, person/LAION data, generation, fine-tuning, and attack execution | keep as Research-only mechanism watch-plus; do not download assets, clone full repo, generate private sets, fine-tune, run SecMI/data extraction, release GPU, or promote Platform/Runtime rows |
| FSECLab MIA-Diffusion code artifact | intake / Lane A | code-public watch-plus | official `fseclab-osaka/mia-diffusion` repo exposes DDIM/DCGAN training, sampling, white-box attack, black-box attack, dataset-loader, ROC-evaluator code, and two FID-stat `.npz` files | no frozen target checkpoint, immutable split manifest, generated sample packet, score array, ROC array, metric JSON, or ready verifier output; using it would require dataset download and target training/sampling | keep as Research-only code reference; do not download CIFAR-10/CelebA, clone full repo, train/sample DDIM/DCGAN targets, run attack scripts, release GPU, or promote Platform/Runtime rows |
| GSA loss-score LR stability | white-box | CPU-only | leave-one-shadow-out review failed release gate | LR did not beat threshold in enough held-out/target folds | closed; do not GPU-scale |
| CLiD boundary maintenance | black-box | CPU-only | prompt-control boundary anchor and validator exist | no independent image-identity protocol | keep as hold-candidate; no GPU |
| Variation real-query line | black-box | CPU/API-only | query-contract audit | missing member/nonmember query images and endpoint | hold until assets exist |
| Simple-distance portability | black-box | needs assets | second image-to-image or repeated-response contract | no valid second asset contract | hold |
| Cross-box successor hypothesis | cross-box | hold | CPU-only scope review closed without a new release-ready hypothesis | current executable routes are existing score-sharing/fusion/support/tail-gated variants or asset-blocked response-contract transfer | reopen only with a genuinely new observable or ready second response-contract package |
| gray-box archived paper candidates | gray-box / intake | hold | reentry review covers SIMA, Noise-as-Probe, MoFit, and Structural Memorization | current artifacts are weak, canary-only, low-FPR unstable, or covered by closed fusion/support routes | reopen only with a new low-FPR-primary observable or protocol |
| Diffusion Memorization repo | black-box / memorization watch | hold / semantic-shift | official ICLR 2024 repo has a real `500`-row `sdv1_500_memorized.jsonl` prompt manifest | `CompVis/stable-diffusion-v1-4` is not locally cached, ground-truth image archive is `2.60G`, and no member/nonmember MIA split, response/noise-track packet, score JSON, ROC CSV, or low-FPR metric artifact is released | keep as related memorization reference; do not download GDrive assets or run `detect_mem.py` as MIA |
| ReDiffuse OpenReview supplement | black-box / ReDiffuse | hold / split-manifest-only | official OpenReview supplement ships DDPM code and exact CIFAR10/CIFAR100/STL10/Tiny-IN train/eval split index manifests | no target checkpoint, generated response/feature cache, score packet, ROC CSV, or metric artifact; running it would require training or acquiring targets from scratch | keep as provenance improvement only; reopen only if checkpoints or score packets appear for the exact manifests |
| Tracing the Roots feature-packet MIA | gray-box / trajectory features | positive-but-provenance-limited | OpenReview supplement ships fixed CIFAR10 train/eval member/external diffusion-trajectory feature tensors and replay code; bounded local replay gives `AUC = 0.815826`, `TPR@1%FPR = 0.134000`; candidate-only product-bridge card records live OpenReview/arXiv recheck and tensor hashes | feature packet lacks raw target checkpoint/sample IDs and image query-response assets, and arXiv v3 source adds no regeneration manifest, so it is not an admitted product row or GPU release target | keep as Research-side mechanism evidence; reopen only with raw provenance/regeneration assets or an explicit feature-packet consumer-boundary decision |
| CDI official dataset-inference artifact | gray-box / dataset inference | hold-semantic-shift | official `sprintml/copyrighted_data_identification` repo is code-public and exposes model configs, attack feature extraction, scoring, and evaluation surfaces | no ready small score packet; requires Google Drive model checkpoints, ImageNet/COCO assets, COCO text embeddings, submodules, and a consumer-boundary decision because the claim is dataset-level rather than per-sample membership | do not download assets or release GPU by default; reopen only if a dataset-inference lane is explicitly opened with frozen checkpoint hashes, bounded ID manifests, `P` size, p-value/low-FPR metric, and consumer boundary |
| MIDST TabDDPM EPT profile | black-box / tabular diffusion | closed / weak metric verdict | MIA-EPT-style error-prediction profile is a genuinely different tabular mechanism and learns train shadow folders (`AUC = 0.851961`) | dev+final transfer remains weak (`AUC = 0.530089`, `ASR = 0.524625`), so the slight strict-tail improvement (`TPR@1%FPR = 0.029500`) does not reopen MIDST | do not expand account toggles, target-column subsets, random-forest grids, classifier sweeps, TabSyn, multi-table, or white-box MIDST |
| Fashion-MNIST DDPM SimA score-norm | gray-box | closed / weak metric verdict | clean train/test split and denoiser access produced a real `64/64` CUDA scout | `AUC = 0.515137` and both low-FPR metrics are zero | do not expand timestep, `p`-norm, seed, scheduler, or packet-size matrices |
| Fashion-MNIST DDPM score-Jacobian sensitivity | gray-box | closed / weak metric verdict | clean train/test split and denoiser local input-sensitivity access produced a real `64/64` CUDA scout | `AUC = 0.511719` and both low-FPR metrics are zero | do not expand timestep, perturbation-scale, seed, scheduler, norm, or packet-size matrices |
| memorization-LDM medical asset | intake / Lane A | watch / artifact-incomplete | public code and Zenodo software snapshot exist for patient-imaging LDM memorization detection | synthesized samples are request-gated; no target LDM checkpoint, exact member/nonmember manifests, or generated response package is public | do not download medical datasets, request controlled samples, train target LDMs, or release GPU until public-safe target/split/response artifacts exist |
| SecMI-LDM LDM fork | intake / Lane A | support-family / no independent second asset | public repo exposes a Diffusers fork, SecMI-style LDM scripts, and README SharePoint links for datasets plus Pokémon fine-tuned SD checkpoint | this repeats the existing same-author SecMI support family and does not create an independent second asset or black-box response contract | do not download the SharePoint zips, scrape LAION/COCO assets, or treat it as an independent second asset unless explicit SecMI-LDM reproducibility maintenance is selected |
| R125 DreamBooth forensics notebook | intake / Lane A | watch / artifact-incomplete | public repo exposes DreamBooth/LoRA notebook code, report media, and six embedded reconstruction-MSE scores | target LoRA checkpoint and six-image forensics query set are private Colab/GDrive artifacts; no manifest or score JSON is released | do not recreate the private run, scrape report images, or treat embedded scalar scores as a DiffAudit packet |
| SAMA diffusion-language-model asset | intake / Lane A | related-method / out-of-scope code-only | public repo exposes DLM training, dataset-prep, and SAMA/baseline attack code for NLP diffusion language models | no released target DLM checkpoint, exact member/nonmember manifest, reusable response/score packet, or image/latent-image response contract | keep as related-method reference only; do not train DLM targets or download gated language models unless a text/DLM lane is explicitly opened |
| LSA-Probe music diffusion MIA | intake / Lane A | music/audio cross-modal watch-plus | public arXiv source and GitHub Pages demo exist; demo exposes `data/*.json` score-like arrays | project repo has only `README.md`; demo arrays are generated mock data, not checkpoint-bound adversarial-cost scores; no implementation, target identities, exact splits, real ROC/metric artifacts, or verifier | keep as watch-plus only; do not download MAESTRO/FMA/DiffWave/MusicLDM/audio/checkpoints, implement from TeX/demo, release GPU, or promote Platform/Runtime rows |
| VidLeaks text-to-video asset | intake / Lane A | related-method / code-snapshot-only | Zenodo exposes a small T2V_MIA code snapshot, README, attack scripts, and ROC plot PNGs | live GitHub repo is unavailable; no target T2V weights, exact video split manifest, generated videos, feature CSVs, or score packets are published | keep as related-method watch only; do not download T2V datasets/models or generate videos unless a T2V lane is explicitly opened |
| StyleMI style-mimicry asset | intake / Lane A | watch / paper-only artifact-incomplete | DOI metadata confirms a 2025 IEEE Access fine-tuned diffusion style-mimicry membership-relevant paper | no public code repository, target LoRA/checkpoint, exact artist/image split manifest, generated image package, image-processing feature packet, or score file was found | keep as paper-only watch; do not scrape artist images, train style LoRAs, invent splits, or release GPU unless public target/split/response artifacts appear |
| I-A finite-tail / adaptive boundary | system / I-A | synchronized | admitted rows exist and are product-consumable, and the latest audit found no drift | none | keep validators active; do not spend another CPU slot unless a guard fails |
| White-box distinct family | white-box | closed | diagonal-Fisher stability board ties `raw_grad_l2_sq` under shadow-frozen target transfer | no distinct score advantage | do not run larger same-score packet; reopen only with a genuinely different observable or paper-backed contract |
| Research boundary-consumability sync | system | synchronized | admitted-vs-candidate boundary synced after candidate closures; 2026-05-12 drift audit passed all admitted consumer validators and exporters | none | keep docs synchronized; no GPU; rerun only if a guard fails or a reviewed promotion is proposed |
| Cross-modal watch consumer boundary | system / Lane C | synchronized | SAMA/DLM, VidLeaks/T2V, GGDM/graph, DurMI/TTS, LSA-Probe music/audio, and MT-MIA relational-tabular are related-method, watch-plus, or support-only items | no admitted row, no Runtime schema input, and no product copy change | keep out of Platform/Runtime unless a future reviewed scope expansion and promotion occurs |
| I-B risk-targeted unlearning successor | defense | hold-protocol-frozen | best k32 full-split anchor has attack-side AUC delta `-0.021347`, but it remains attack-side threshold transfer; the defended-shadow reopen protocol is machine-checkable, explicit reopen mode rejects undefended threshold references, and the coverage-aware training manifest blocks the current target k32 identity contract; the shadow-local scout found a mechanically possible `shadow-01`/`shadow-02` target-risk remap; the 2026-05-15 GSA-only preflight now produces true shadow-local k32 GSA risk records for `shadow-01`, `shadow-02`, and `shadow-03` | target-risk remap is not true shadow-local scoring; GSA-only risk does not satisfy the frozen PIA+GSA contract; no shadow-local PIA records, no executed defended-shadow training result, no adaptive attacker result, and no retained-utility result | keep hold; next valid work is shadow-local PIA risk scoring or explicit approval of weaker GSA-only semantics before any tiny defended-shadow training execution |
| I-C cross-permission successor | cross-permission | hold | feasibility scout confirms current PIA bridge surface is translated-alias-only with `same_spec_reuse = false` and only a single-pair local score-gap board | no same-spec gray-box evaluator or matched comparator release board | hold until a new same-spec evaluator contract exists |

## Active

### Post-CPSample Long-Horizon Idle State

- `mode`: post-CPSample defense artifact gate after DSiRe / LoRA-WiSE,
  hyperparameter-free SecMI, DME, FreMIA, CopyMark, VAE2Diffusion, DCR copying,
  FCRE medical frequency, Tabular Privacy Leakage TDM, TMIA-DM, Shake-to-Leak,
  FSECLab MIA-Diffusion, MT-MIA relational diffusion score-packet, and the
  2026-05-15 admitted consumer-boundary sync
- `status`: The latest defense verdict is the CPSample artifact gate.
  OpenReview `LIBLIlk5M9` exposes an official ICLR 2025 code supplement with
  diffusion/classifier code and small attack-loss text fragments, but it lacks
  immutable denoiser/classifier checkpoint hashes, exact subset-index
  manifests, row-bound protected/unprotected score packets, ROC arrays, metric
  JSON, retained-utility metrics, and a ready verifier. The result is defense
  watch-plus only: no CIFAR-10/CelebA/LSUN/Stable Diffusion/checkpoint/image
  download, no `python main.py` or `--inference_attack` run, no CPU sidecar, no
  GPU release, no Platform row, and no Runtime schema. The previous boundary
  verdict is the DSiRe / LoRA-WiSE dataset-size gate: strong future weight-only
  privacy evidence, but aggregate dataset-size recovery rather than per-sample
  MIA. The previous score-artifact verdict is the CopyMark official score
  artifact gate. `caradryanl/CopyMark` exposes official member/nonmember image
  logs, aggregate ROC/threshold JSONs, selected PIA/PFAMI/SecMI all-step score
  tensors, GSA feature/XGBoost files, and LAION-RiDAR/mixing results. It
  remains support-only because it lacks checkpoint hashes, a compact
  row-ID-bound score manifest, small immutable data/checkpoint packet, and
  ready verifier output. No HF dataset zip, image payload, model folder, full
  repo clone, script execution, CPU sidecar, GPU release, Platform row, or
  Runtime schema is selected. The previous asset verdict before CopyMark is the
  VAE2Diffusion
  latent-space inversion gate. `mx-ethan-rao/VAE2Diffusion` exposes code for decoder-geometry
  / latent-dimension filtering membership inference on LDMs, but the README
  split/checkpoint link is empty, the repo has no release assets, the recursive
  tree has no split, checkpoint, score, ROC, metric, response, or verifier
  artifacts, and scripts require author-local paths plus local training /
  fine-tuning and pullback/per-dim cache generation. The result is code-public
  latent-space MIA watch-plus only: no dataset/model/checkpoint/cache download,
  CPU sidecar, GPU release, Platform row, or Runtime schema is selected. The
  previous asset verdict is the DCR copying manifest gate.
  `somepago/DCR` publishes official replication/copying code, retrieval scripts,
  metric helpers, and LAION caption metadata, but the README LAION-10k Drive
  split link returned `404`, and no immutable member/nonmember MIA split, target
  checkpoint, generated response package, score rows, ROC arrays, metric JSON,
  or ready verifier outputs are public. The result is copying/memorization
  semantic-shift watch-plus only: no LAION/Drive/model download, fine-tuning,
  inference, retrieval, CPU sidecar, GPU release, Platform row, or Runtime
  schema is selected. The previous asset verdict is the FCRE medical frequency
  artifact gate: arXiv `2506.14919` reports frequency-calibrated
  reconstruction-error MIA metrics on FeTS 2022, ChestX-ray8, and CIFAR-10, but
  no official code, immutable split manifests, target checkpoints, generated
  reconstruction packets, score rows, ROC arrays, metric JSON, or ready verifier
  outputs are public. The previous asset verdict is the Tabular Privacy Leakage
  TDM gate:
  arXiv `2605.06835` links the official `VectorInstitute/midst-toolkit` code
  for ClavaDDPM training/synthesis and Tartan Federer / Ensemble / EPT attacks,
  but no paper-bound Berka/Diabetes target checkpoints, immutable split
  manifests, generated synthetic tables, score rows, ROC arrays, metric JSON,
  or ready verifier outputs are public. The previous gray-box artifact verdict
  is TMIA-DM, which remains paper-only temporal-noise /
  noise-gradient MIA with reported metrics only and no code-score artifact. The
  previous asset verdict is the Shake-to-Leak code artifact gate. The official
  `VITA-Group/Shake-to-Leak` repository publishes fine-tuning-amplified
  generative privacy code, vendored SecMI/diffusers code, fine-tuning scripts,
  SecMI scripts, data extraction code, and a `40`-domain celebrity/person list,
  but no frozen SD-v1-1 fine-tuned checkpoint, immutable member/nonmember
  manifest, generated synthetic private-set packet, generated attack response,
  score array, ROC array, metric JSON, or ready verifier output is committed.
  The result is code-public watch-plus only: no Stable Diffusion weight
  download, LAION/person image acquisition, synthetic-private-set generation,
  fine-tuning, SecMI/data-extraction run, CPU sidecar, GPU release, Platform
  row, or Runtime schema is selected. The previous asset verdict is the FSECLab
  MIA-Diffusion code artifact gate. The
  official `fseclab-osaka/mia-diffusion` repository publishes DDIM/DCGAN
  training, sampling, white-box attack, black-box attack, dataset-loader, and
  ROC-evaluator code plus two FID-stat `.npz` files, but no frozen target
  checkpoint, immutable member/nonmember split manifest, generated sample
  packet, score array, ROC array, metric JSON, or ready verifier output is
  committed. The result is code-public watch-plus only: no CIFAR-10/CelebA
  download, checkpoint/model acquisition, full repo clone, training, sampling,
  attack-script execution, CPU sidecar, GPU release, Platform row, or Runtime
  schema is selected. The previous asset verdict is the MT-MIA relational
  diffusion score-packet gate. MT-MIA publishes official multi-table
  member/nonmember/reference splits, pre-generated ClavaDDPM/RelDiff synthetic
  outputs, and `18` score/metric packets, but it remains cross-modal
  relational-tabular support-only: no raw figshare data, synthetic CSV payload,
  full repo, training asset, CPU sidecar, GPU release, Platform row, or Runtime
  schema is selected. The previous asset verdict is the LSA-Probe music
  diffusion mock-data gate. LSA-Probe remains music/audio cross-modal
  watch-plus only: the public project repo has no implementation tree, and the
  GitHub Pages score-like `data/*.json` arrays are generated mock demo data,
  not checkpoint-bound adversarial-cost score artifacts. No
  MAESTRO/FMA/DiffWave/MusicLDM/audio/checkpoint download, CPU sidecar, GPU
  release, or admitted row is selected. The latest consumer verdict remains
  the admitted consumer drift
  audit. The admitted bundle remains `admitted-only` with exactly five
  Platform/Runtime rows: `recon`, `PIA baseline`, `PIA defended`, `GSA`, and
  `DPDM W-1`. The validator chain passed, and recent watch/candidate lines do
  not change Platform rows, Runtime schemas, product copy, download policy, CPU
  sidecars, or GPU release. The previous asset verdict is the DualMD /
  DistillMD defense gate. The OpenReview `DDMD/` supplement exposes DDPM/LDM
  training, disjoint
  teacher, distillation, PIA/SecMIA, black-box attack code, DDPM split-index
  files, and FID stats, but the embedded GitHub origin is not public and the
  supplement ships no checkpoint-bound defended/undefended scores, ROC arrays,
  metric JSON, generated response packets, or ready verifier. The result is
  defense watch-plus only: no SharePoint Pokemon, Stable Diffusion,
  CIFAR/STL/Tiny-ImageNet download, no training or attack-script execution, no
  CPU sidecar, no GPU release, and no admitted defense row. The previous asset
  verdict is the DIFFENCE classifier-defense gate.
  `SPIN-UMass/Diffence` exposes code, configs, and split-index files, but the
  protected target is an image classifier, diffusion is a pre-inference defense
  component, and the repo ships no checkpoint-bound defended/undefended logits,
  score rows, ROC arrays, metric JSON, or ready verifier outputs. The result is
  classifier-defense watch-plus only: no Google Drive checkpoint/data download,
  no classifier or diffusion training, no MIA script execution, no CPU sidecar,
  no GPU release, and no admitted defense row. The previous asset verdict is
  the MIAHOLD / HOLD++ higher-order
  Langevin artifact gate. `bensterl15/MIAHOLD` and
  `bensterl15/MIAHOLDCIFAR` expose defense code, audio split filelists, a
  CIFAR HOLD config, and PIA-style attack code, but they do not ship
  checkpoint-bound target artifacts, reusable member/nonmember scores, ROC
  arrays, metric JSON, generated responses, or ready verifier outputs. The
  result is defense watch-plus only: no Google Drive checkpoint/data download,
  no W&B scraping, no training, no CPU sidecar, no GPU release, and no
  admitted defense row. The previous metric verdict is the Quantile Diffusion MIA SecMI
  `t_error` replay. `neilkale/quantile-diffusion-mia` publishes committed
  CIFAR10/CIFAR100 SecMI-style score rows plus split manifests. Replaying
  `score = -t_error` gives CIFAR10 `AUC = 0.843853` and CIFAR100
  `AUC = 0.782126`, with positive ASR but weak strict-tail recovery. The
  result is support-only: it is not the official Quantile Regression paper
  output, not an admitted Platform/Runtime row, and it releases no full repo
  clone, asset download, training, quantile fitting, CPU sidecar, or GPU work.
  The previous defense verdict is the I-B shadow-local GSA risk
  preflight. Existing GSA shadow loss-score exports now produce true
  shadow-local GSA-only k32 risk records for `shadow-01`, `shadow-02`, and
  `shadow-03`; duplicate suffix IDs are de-duplicated before identity-file
  selection. The artifact stays blocked because shadow-local PIA risk records
  remain missing from the frozen PIA+GSA defended-shadow contract. It releases
  no training, GPU work, admitted defense row, Platform/Runtime schema, or CPU
  sidecar. The previous product-boundary verdict is the Tracing Roots
  candidate evidence card. The OpenReview supplementary feature packet remains
  positive (`AUC = 0.815826`, `TPR@1%FPR = 0.134000`,
  `TPR@0.1%FPR = 0.038000`) and now has a machine-readable candidate card for
  Research/product-boundary comparison. The 2026-05-15 live recheck found the
  OpenReview attachment still reachable and arXiv `2411.07449v3` source still
  TeX/figures-only, with no raw target checkpoint identity, sample manifest,
  image query-response packet, or feature-regeneration script. It remains
  Research-only feature-packet evidence, not an admitted product row, CPU
  sidecar, or GPU release. The previous metric verdict is MIDST TabDDPM EPT. It
  adapted the MIA-EPT error-prediction profile to local single-table TabDDPM
  assets and used all `30` train, `20` dev, and `20` final model folders. The
  train shadow folders are learnable (`AUC = 0.851961`), but dev+final transfer
  remains weak (`AUC = 0.530089`, `ASR = 0.524625`,
  `TPR@1%FPR = 0.029500`), so MIDST stays closed without account toggles,
  target-column subsets, random-forest grids, classifier sweeps, TabSyn,
  multi-table, or white-box expansion. The previous asset gate is
  `YuxinWenRick/diffusion_memorization`.
  It has a real `500`-row `sdv1_500_memorized.jsonl` prompt manifest, but it is
  a memorization detection/mitigation reference rather than a released
  per-sample MIA packet. `CompVis/stable-diffusion-v1-4` is not cached locally,
  the ground-truth image archive is `2.60G`, and no member/nonmember MIA split,
  generated response/noise-track packet, score JSON, ROC CSV, or low-FPR metric
  artifact is public. It releases no CPU/GPU work. The previous asset audit is
  ReDiffuse OpenReview split-manifest provenance: exact DDPM
  CIFAR10/CIFAR100/STL10/Tiny-IN train/eval split index manifests are public,
  but no target checkpoint or score packet is released. The latest active metric
  verdict is Tracing the Roots feature-packet MIA: bounded local replay gives
  `AUC = 0.815826` and `TPR@1%FPR = 0.134000`, but raw target checkpoint, sample
  IDs, and image query-response assets are missing, so there is no admitted
  promotion and no GPU release. The previous Fashion-MNIST DDPM score-Jacobian sensitivity verdict is weak
  (`AUC = 0.511719`, zero low-FPR recovery) and closes the local score-field
  sensitivity branch after prior weak Fashion-MNIST PIA-loss and SimA
  score-norm scouts. The latest Lane A asset gate keeps StyleMI as paper-only /
  artifact-incomplete: no code, target checkpoint, exact artist/image split,
  generated image package, feature packet, or score file was found. The latest
  CDI official gate is code-public but held as a dataset-inference semantic
  shift with large model/data requirements and no ready small score packet. The latest consumer-boundary sync also
  confirms that SAMA/DLM, VidLeaks/T2V, GGDM/graph, DurMI/TTS, and LSA-Probe
  music/audio are related-method or watch-plus items only.
  They do not change admitted rows, Runtime schemas, recommendation logic, or
  product copy. I-B, I-C, ReDiffuse,
  CommonCanvas, MIDST, Beans LoRA, LAION-mi, Zenodo, MoFit, MIAGM, Quantile
  Regression, DualMD/DistillMD, DIFFENCE, MIAHOLD/HOLD++, FSECLab
  MIA-Diffusion, and Noise as a Probe remain governed by
  `ROADMAP.md` lane gates
  and do not release automatic CPU/GPU work.
- `goal`: next cycle must select exactly one Lane A/B/C task from
  `ROADMAP.md`; if no candidate passes target identity, exact split,
  query/response coverage, provenance, and non-adjacent mechanism gates, stop
  rather than writing another scope/audit/reselection chain.
- `latest trigger`: Diffusion Memorization tested a non-ReDiffuse public T2I
  privacy repo and found a real small prompt manifest, but the claim is
  memorization detection, not DiffAudit MIA, and the execution assets are either
  large GDrive packages or missing score packets. Tracing the Roots tested a non-adjacent trajectory-feature
  mechanism using a released small supplementary packet. It produced a real
  positive metric but also exposed the current boundary: feature-packet evidence
  is not raw image/query-response evidence. The ReDiffuse supplement then
  improved split provenance but did not add checkpoints or score artifacts. CDI tested a non-adjacent scientific pivot from weak
  pointwise MIAs to dataset inference. The public gate found official code, but
  not a bounded DiffAudit-ready score packet; assets remain too large and the
  consumer claim semantics would change. The latest StyleMI gate tested a
  non-duplicate style-mimicry paper-only candidate, but found no executable
  target/split/response or score artifacts. The latest cross-modal watch
  consumer boundary keeps SAMA/DLM, VidLeaks/T2V, GGDM/graph, DurMI/TTS, and
  LSA-Probe music/audio out of Platform/Runtime rows and releases no CPU/GPU
  work. The latest admitted consumer drift audit confirms these watch/candidate
  lines did not leak into the admitted Platform/Runtime bundle.
- `GPU cap`: none selected
- `integration`: no schema change; admitted five-row consumer set intact;
  Research-only candidate feature-packet cards remain non-consumable

Current evidence:

- [../../docs/evidence/privacy-leakage-tdm-artifact-gate-20260515.md](../../docs/evidence/privacy-leakage-tdm-artifact-gate-20260515.md)
- [../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md](../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md)
- [../../docs/evidence/fseclab-mia-diffusion-code-artifact-gate-20260515.md](../../docs/evidence/fseclab-mia-diffusion-code-artifact-gate-20260515.md)
- [../../docs/evidence/mtmia-relational-diffusion-score-packet-gate-20260515.md](../../docs/evidence/mtmia-relational-diffusion-score-packet-gate-20260515.md)
- [../../docs/evidence/lsaprobe-music-diffusion-mock-data-gate-20260515.md](../../docs/evidence/lsaprobe-music-diffusion-mock-data-gate-20260515.md)
- [../../docs/evidence/admitted-consumer-drift-audit-20260515.md](../../docs/evidence/admitted-consumer-drift-audit-20260515.md)
- [../../docs/evidence/dualmd-distillmd-defense-artifact-gate-20260515.md](../../docs/evidence/dualmd-distillmd-defense-artifact-gate-20260515.md)
- [../../docs/evidence/diffence-classifier-defense-artifact-gate-20260515.md](../../docs/evidence/diffence-classifier-defense-artifact-gate-20260515.md)
- [../../docs/evidence/miahold-higher-order-langevin-artifact-gate-20260515.md](../../docs/evidence/miahold-higher-order-langevin-artifact-gate-20260515.md)
- [../../docs/evidence/quantile-diffusion-mia-secmia-terror-replay-20260515.md](../../docs/evidence/quantile-diffusion-mia-secmia-terror-replay-20260515.md)
- [../../docs/evidence/ib-shadow-local-gsa-risk-preflight-20260515.md](../../docs/evidence/ib-shadow-local-gsa-risk-preflight-20260515.md)
- [../../docs/product-bridge/tracing-roots-candidate-evidence-card.md](../../docs/product-bridge/tracing-roots-candidate-evidence-card.md)
- [../../docs/evidence/midst-tabddpm-ept-scout-20260515.md](../../docs/evidence/midst-tabddpm-ept-scout-20260515.md)
- [../../docs/evidence/diffusion-memorization-asset-gate-20260515.md](../../docs/evidence/diffusion-memorization-asset-gate-20260515.md)
- [../../docs/evidence/rediffuse-openreview-split-manifest-audit-20260515.md](../../docs/evidence/rediffuse-openreview-split-manifest-audit-20260515.md)
- [../../docs/evidence/tracing-roots-feature-packet-mia-20260515.md](../../docs/evidence/tracing-roots-feature-packet-mia-20260515.md)
- [../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md](../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md)
- [../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md)
- [../../docs/evidence/cdi-official-artifact-gate-20260515.md](../../docs/evidence/cdi-official-artifact-gate-20260515.md)
- [../../docs/evidence/stylemi-asset-verdict-20260514.md](../../docs/evidence/stylemi-asset-verdict-20260514.md)
- [../../docs/evidence/cross-modal-watch-consumer-boundary-20260514.md](../../docs/evidence/cross-modal-watch-consumer-boundary-20260514.md)
- [../../docs/evidence/vidleaks-t2v-asset-verdict-20260514.md](../../docs/evidence/vidleaks-t2v-asset-verdict-20260514.md)
- [../../docs/evidence/sama-dlm-asset-verdict-20260514.md](../../docs/evidence/sama-dlm-asset-verdict-20260514.md)
- [../../docs/evidence/ronketer-dreambooth-asset-verdict-20260514.md](../../docs/evidence/ronketer-dreambooth-asset-verdict-20260514.md)
- [../../docs/evidence/secmi-ldm-asset-verdict-20260514.md](../../docs/evidence/secmi-ldm-asset-verdict-20260514.md)
- [../../docs/evidence/post-midfreq-next-lane-reselection-20260512.md](../../docs/evidence/post-midfreq-next-lane-reselection-20260512.md)
- [../../docs/evidence/secmi-consumer-contract-review-20260512.md](../../docs/evidence/secmi-consumer-contract-review-20260512.md)
- [../../docs/evidence/secmi-full-split-admission-boundary-review.md](../../docs/evidence/secmi-full-split-admission-boundary-review.md)
- [../../docs/evidence/secmi-admission-contract-hardening-20260511.md](../../docs/evidence/secmi-admission-contract-hardening-20260511.md)
- [../../docs/evidence/midfreq-residual-signcheck-20260512.md](../../docs/evidence/midfreq-residual-signcheck-20260512.md)
- [../../docs/evidence/midfreq-residual-stability-decision-20260512.md](../../docs/evidence/midfreq-residual-stability-decision-20260512.md)
- [../../docs/evidence/midfreq-residual-stability-result-20260512.md](../../docs/evidence/midfreq-residual-stability-result-20260512.md)
- [../../docs/evidence/midfreq-residual-comparator-audit-20260512.md](../../docs/evidence/midfreq-residual-comparator-audit-20260512.md)
- [../../docs/evidence/midfreq-residual-collector-contract-20260512.md](../../docs/evidence/midfreq-residual-collector-contract-20260512.md)
- [../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md)
- [../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md)
- [../../docs/evidence/midfreq-residual-scorer-contract-20260512.md](../../docs/evidence/midfreq-residual-scorer-contract-20260512.md)
- [../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md)
- [../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md](../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md)
- [../../docs/evidence/post-secmi-next-lane-reselection-20260511.md](../../docs/evidence/post-secmi-next-lane-reselection-20260511.md)
- [../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md](../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md](../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md](../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md](../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md)
- [../../docs/evidence/post-fisher-next-lane-reselection-20260511.md](../../docs/evidence/post-fisher-next-lane-reselection-20260511.md)
- [../../docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md](../../docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md)
- [../../docs/evidence/cross-box-successor-scope-20260512.md](../../docs/evidence/cross-box-successor-scope-20260512.md)
- [../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md)
- [../../docs/evidence/ib-adaptive-defense-contract-20260511.md](../../docs/evidence/ib-adaptive-defense-contract-20260511.md)
- [../../docs/evidence/ib-defense-aware-reopen-scout-20260512.md](../../docs/evidence/ib-defense-aware-reopen-scout-20260512.md)
- [../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md)
- [../../docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](../../docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md)
- [../../docs/evidence/ib-reopen-shadow-reference-guard-20260512.md](../../docs/evidence/ib-reopen-shadow-reference-guard-20260512.md)
- [../../docs/evidence/ib-defended-shadow-training-manifest-20260512.md](../../docs/evidence/ib-defended-shadow-training-manifest-20260512.md)
- [../../docs/evidence/ib-shadow-local-identity-scout-20260512.md](../../docs/evidence/ib-shadow-local-identity-scout-20260512.md)
- [../../docs/evidence/post-ib-next-lane-reselection-20260512.md](../../docs/evidence/post-ib-next-lane-reselection-20260512.md)
- [../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md)
- [../../docs/evidence/admitted-consumer-drift-audit-20260512.md](../../docs/evidence/admitted-consumer-drift-audit-20260512.md)
- [../white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json](../white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json)

Restart conditions:

- do not run a larger same-contract tri-score packet; it is closed as
  internal-only positive-but-bounded evidence.
- do not keep constructing the stale Pokemon/Kandinsky skeleton by default;
  reopen response-contract acquisition only with a genuinely new public target
  identity, exact member/nonmember query images, and response/score coverage.
- do not fill the Pokemon/Kandinsky skeleton with CelebA/recon tensors or
  weights-only material.
- do not run 800k ReDiffuse metrics as an automatic shortcut.
- do not run larger ReDiffuse packets without a new scorer hypothesis and CPU
  preflight.
- do not GPU-scale GSA loss-score LR from the current stability review.
- do not reopen diagonal-Fisher from the current stability board; it ties
  `raw_grad_l2_sq` and has no GPU release.
- do not expose ReDiffuse, tri-score, cross-box fusion, GSA LR, H2/simple-distance,
  CLiD, or response-contract acquisition as admitted Platform evidence.
- do not admit SecMI stat or NNS rows until a separate consumer-row schema,
  NNS product-facing decision, adaptive-review protocol, finite-tail semantics,
  and provenance language are reviewed.
- do not GPU-scale I-B from existing attack-side threshold-transfer diagnostics.
- do not call the I-B defended-shadow reopen protocol executable for GPU until
  true shadow-local risk records or explicitly approved remap semantics,
  fixed identity files, tiny defended-shadow training output,
  adaptive-attacker measurement, and retained-utility measurement are
  available.
- do not GPU-scale I-C same-pair replay without a same-spec evaluator and
  matched random comparator contract.
- do not call an influence/curvature scout distinct unless it defines a signal
  that is not scalar loss, gradient norm, GSA loss-score LR, or the prior
  activation-subspace observable.
- do not release GPU for the influence/curvature scout until a CPU micro-board
  retains selected-layer raw gradient coordinates and compares against required
  baselines.
- do not run a larger same-score diagonal-Fisher packet; the first CPU
  micro-board failed target-transfer orientation and baseline comparison.
- do not release GPU from the stability board; `up_blocks.1.attentions.0.to_v`
  failed to beat `raw_grad_l2_sq`.
- do not run another cross-box score-sharing, weighted/logistic fusion,
  support/disconfirm, tail-gated cascade, or same-contract tri-score board
  without a new observable or ready second response-contract package.
- do not treat H2/H3 lowpass, highpass, or bandpass response-cache metrics as
  evidence for mid-frequency same-noise residual scoring.
- do not cite the residual line as evidence from the `4/4` preflight; use it
  only as the precondition that enabled the completed `64/64` sign-check.
- do not cite the `64/64` sign-check as admitted evidence; it is candidate-only
  and strict-tail values are finite packet counts, not calibrated sub-percent
  FPR.
- do not run another same-contract residual packet; the seed-23 stability
  result is reviewed and synced.
- do not claim mid-frequency specificity from the current residual packets;
  low-frequency and full-band residual comparators are at least as strong on
  AUC.

## Ready

### Public Documentation Sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs or repository surface become stale; this is
  not a research lane, GPU release gate, or substitute for Lane A/B evidence.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### CLiD Prompt-Conditioned Diagnostic Lane

- `mode`: black-box candidate
- `reason for hold`: original prompt-conditioned packet is strong, but fixed
  prompt, swapped-prompt, within-split shuffle, prompt-text-only, and control
  attribution reviews show prompt-conditioned auxiliary instability.
- `reopen trigger`: new protocol that isolates image identity from
  prompt-conditioned auxiliary behavior and keeps low-FPR metrics primary.

### Stable Diffusion / CelebA Adapter Contract Watch

- `mode`: future black-box data acquisition
- `reason for hold`: current assets do not provide a second valid
  image-to-image or repeated-response portability contract.
- `reopen trigger`: image-to-image or unconditional-state endpoint contract
  with fixed repeats, response images, split source, and low-FPR gate.

### Cross-Box Successor-Hypothesis Watch

- `mode`: cross-track support
- `reason for hold`: existing score-sharing packets are useful internally, but
  do not establish stable low-FPR gains.
- `reopen trigger`: a new shared-surface or calibration hypothesis with
  low-FPR as the primary gate.

### White-Box Distinct-Family Watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace, cross-layer, and trajectory variants
  all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### Selective / Suspicion-Gated Routing

- `mode`: defense candidate
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block promotion.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### Response-Strength Black-Box Candidate

- `mode`: black-box candidate
- `reason for hold`: positive-but-bounded on `DDPM/CIFAR10`, but not admitted
  or portable.
- `reopen trigger`: a cross-asset black-box contract with dataset, model, split,
  and query-budget boundaries.

### Variation Real-Query Line

- `mode`: API-only black-box
- `reason for hold`: missing real query-image set and real endpoint.
- `reopen trigger`: `Download/black-box/datasets/variation-query-set` contains
  member/nonmember images and a real endpoint contract is available.

## Needs Data

| Need | Blocker | Data rule |
| --- | --- | --- |
| Cross-box transfer / portability | missing paired model contracts, paired split contracts, and one shared-surface hypothesis | do not schedule execution until required paired data is present in `Download/` or documented through workspace manifests |
| Conditional diffusion wider-family validation | current `DDPM/CIFAR10` results cannot generalize to conditional diffusion | raw datasets, weights, and supplementary files belong under `<DIFFAUDIT_ROOT>/Download/`, not Git |
| Simple-distance second asset | no valid second image-to-image or repeated-response contract | follow [../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) before GPU |

## Closed

| Task | Result |
| --- | --- |
| Mid-frequency residual real-asset preflight | Real CIFAR10/collaborator-750k `4/4` cache writer ready; no GPU release and no admitted evidence. |
| Mid-frequency residual tiny runner contract | Synthetic tiny cache writer ready; real-asset preflight now complete; no GPU release. |
| Mid-frequency residual collector contract | Same-noise collector functions ready; no GPU release. |
| Mid-frequency residual scorer contract | Scorer utility and tests ready; collector and synthetic tiny runner now follow; no GPU release. |
| Paper-backed new-observable intake scout | Distinct same-noise mid-frequency residual gap found; existing caches fail the residual-field contract, so no GPU release. |
| Post-ReDiffuse reselection | Selects black-box second response-contract acquisition; no GPU release. |
| Gray-box tri-score consolidation | Positive-but-bounded internal evidence; no admitted promotion and no GPU release. |
| Gray-box tri-score truth-hardening | Positive-but-bounded internal evidence; no admitted promotion, no product promotion, and no GPU release. |
| PIA stochastic-dropout truth-hardening | Positive boundary hardening; no GPU release. |
| Non-gray-box reselection | Selected black-box response-contract acquisition audit; no GPU release. |
| Black-box response-contract acquisition audit | Needs-assets; no GPU release. |
| ReDiffuse checkpoint-portability gate | blocked-by-scoring-contract; 800k checkpoint compatibility is not enough to release metrics. |
| ReDiffuse ResNet contract scout | blocked-by-contract-mismatch; current Research `resnet` mode is not exact collaborator replay. |
| ReDiffuse exact replay preflight | CPU preflight passed; `resnet_collaborator_replay` mode is available, no GPU release yet. |
| ReDiffuse 750k exact replay | Candidate-only; modest AUC but weak strict-tail evidence, no admitted promotion. |
| SecMI full-split admission boundary | Evidence-ready supporting reference; not admitted until consumer-boundary/adaptive-review contract exists. |
| SecMI admission contract hardening | Supporting-reference-hardened; SecMI stat and NNS remain Research-only rows with no GPU release. |
| Post-SecMI next-lane reselection | Selected white-box influence/curvature feasibility scout as CPU-first; no GPU release. |
| White-box influence/curvature feasibility | CPU contract ready; GSA assets are ready with workspace-scoped upstream checkout; no GPU release. |
| GSA diagonal-Fisher micro-board | Negative-but-useful; selected-layer raw gradients are extractable, but the diagonal-Fisher score failed target transfer. |
| GSA diagonal-Fisher layer scope | Mixed but not GPU-ready; one tiny layer-scope row transfers but ties `raw_grad_l2_sq`. |
| GSA diagonal-Fisher stability board | Negative-but-useful; the remaining layer ties `raw_grad_l2_sq` at `4` samples per split, closing the line. |
| Post-Fisher next-lane reselection | Selected CPU-only I-A finite-tail / adaptive boundary hardening; no GPU release. |
| I-A finite-tail / adaptive boundary audit | Synchronized; admitted strict-tail and adaptive-language boundaries remain guarded. |
| Cross-box successor scope | Hold; no genuinely new CPU/GPU successor hypothesis is ready. |
| I-B defense-aware reopen scout | Hold; current I-B evidence is not defense-aware and releases no GPU. |
| I-B defense reopen protocol audit | Hold-structural; current code path borrows undefended shadow threshold transfer and cannot release defended-shadow or adaptive-attacker work. |
| I-B reopen shadow-reference guard | Ready CPU guard; explicit reopen mode rejects undefended threshold references but releases no GPU. |
| I-B defended-shadow training manifest | Blocked CPU manifest; current target k32 forget IDs are not covered by shadow member datasets, so no training run or defense result. |
| I-B shadow-local identity scout | Blocked semantic scout; two-shadow target-risk remap is mechanically possible but not true shadow-local scoring. |
| Post-I-B next-lane reselection | Selected I-C same-spec evaluator feasibility scout; no GPU release. |
| I-C same-spec evaluator feasibility | Hold; current translated-alias probes are not same-spec evaluator release surfaces and emit no split-level four-metric board. |
| Gray-box paper-candidate reentry | Hold; archived paper candidates do not release CPU/GPU work from current artifacts. |
| Kandinsky/Pokemon response-contract package preflight | needs-assets; supplementary root exists, but no member/nonmember query package or response contract exists. |
| GSA loss-score shadow stability | negative-but-useful; leave-one-shadow-out LR failed the distinct-scorer release gate. |
| Research resting-state audit | No active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive. |
| Cross-modal watch consumer boundary | Synchronized; SAMA/DLM, VidLeaks/T2V, GGDM/graph, DurMI/TTS, LSA-Probe music/audio, and MT-MIA relational-tabular are related-method, watch-plus, or support-only items and do not change admitted Platform/Runtime rows or schemas. |
| VidLeaks T2V asset gate | Related-method/code-snapshot-only; live GitHub repo unavailable and Zenodo snapshot lacks target T2V weights, exact video split manifests, generated videos, feature CSVs, and score packets. |
| SAMA DLM asset gate | Related-method/out-of-scope for current image-diffusion Lane A; public code lacks a released target DLM checkpoint, exact split manifests, and response/score packet. |
| Memorization-LDM asset gate | Request-gated and artifact-incomplete; public code/Zenodo software snapshot lack target LDM checkpoint, exact split manifests, and generated response package. |
| Fashion-MNIST score-Jacobian sensitivity | Weak clean-split metric verdict; `AUC = 0.511719` with zero low-FPR recovery, no perturbation/timestep/seed/norm expansion. |
| Black-box response-contract asset-acquisition spec | needs-assets; minimum second-asset package defined; no GPU release. |
| Black-box response-contract discovery | needs-assets; discovery found no paired second response-contract package under black-box dataset/supplementary roots. |
| Black-box response-contract second-asset intake | needs-assets; post-tri-score refresh found no ready paired package. |
| Research boundary-consumability sync | synchronized admitted-vs-candidate boundary; no GPU release and no schema change. |
| Admitted evidence bundle | Synchronized; complete admitted consumer set exported as checked machine-readable bundle. |
| I-B risk-targeted unlearning successor scope | hold; small attack-side reductions are not enough without defended-shadow/adaptive review. |
| ReDiffuse collaborator bundle intake | Positive intake; complete enough for bounded compatibility review, not admitted evidence. |
| ReDiffuse 750k direct-distance packet | Positive compatibility packet at 64/64; not comparable with PIA/SecMI without scoring-mode caveat. |
| Recon tail confidence review | Admitted-finite-tail-only; recon remains black-box product row. |
| Semantic-auxiliary low-FPR review | Negative-but-useful; no GPU packet selected. |
| Variation query-contract audit | Blocked by missing real query images and endpoint. |
| H2 simple-distance product bridge comparison | Recon remains product row; simple-distance remains Research evidence only. |
| CLiD prompt-conditioned probing | Hold-candidate; strong original packet but prompt controls block admission. |
| Cross-box evidence boundary hardening | Candidate-only; current packets do not establish stable low-FPR gains. |
| Shared utility extraction | Metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| Information architecture reset | Public docs, internal docs, workspace archives, and data boundaries were reorganized. |

Older closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
