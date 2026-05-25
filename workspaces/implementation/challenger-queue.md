# Research Task Queue

> Last refreshed: 2026-05-26

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `Paperization active: papers/diffaudit-evidence-paper now contains a multi-direction paper portfolio, direction-specific version briefs, evidence bank, claim register, generated CSV/PDF figures, a compiled 8-page IEEEtran draft, Direction C v1 metadata corpus, a 2026-05-26 fixed-search metadata batch, and selected-corpus gate-summary assets; H2 output-cloud remains a strong Research-side case study, not admitted; no selected heavy CPU/GPU sidecar` |
| Active GPU task | none running |
| Next GPU candidate | none selected |
| CPU sidecar | paper asset generation / metadata-only artifact-corpus expansion only |
| Gray-box status | PIA remains admitted; feature-packet channel remains deferred; Tracing the Roots is positive Research-only evidence; FMIA, Rectified Flow, SimA, VAE2Diffusion, DME, and FreMIA remain watch-plus or paper/stub-only; Fashion-MNIST SimA score-norm and score-Jacobian sensitivity remain weak |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| Identity-Focused Inference / Extraction | identity-level diffusion privacy / Lane A-B | paper-source-only semantic-shift watch | arXiv `2410.10177` reports membership inference, identity inference, and data extraction against diffusion models in LFW / CelebA-style face settings; arXiv source `HEAD` is a `3,990,545` byte gzip with SHA-256 ETag `eedf38231ea31b6440f63109d7ab9fa3d49fa5bf3601703ac259d3e0405253e2` and was not downloaded | claim boundary is identity-level inclusion / extraction, not current per-sample membership rows; no official code, LDM / DDPM target checkpoint bundle, LFW / CelebA identity or member/nonmember manifest, generated response packet, per-row membership / identity scores, ROC arrays, metric JSON, extraction-quality artifact, or verifier is public | keep as Research-only identity-level privacy watch evidence; do not download arXiv source/PDF, face images, generated images, training data, model weights, checkpoints, or inferred code archives; do not implement from paper, launch CPU/GPU sidecars, or promote Platform/Runtime rows unless public row-bound identity/member artifacts and a reviewed identity-privacy consumer boundary appear |
| RAPTA / ADMCD copying mitigation | text-to-image copying / memorization mitigation / Lane A-B | paper-source-only mitigation watch | arXiv `2603.13070` proposes Region-Aware Prompt Augmentation and Attention-Driven Multimodal Copy Detection; arXiv source `HEAD` is a `4,172,177` byte gzip with SHA-256 ETag `f44be31acedbcb98485527bb56c4c1e7e02c96d646b7f09e36edf356280fe059` and was not downloaded | claim boundary is copying / memorization mitigation, not current per-sample membership rows; no official code, target checkpoint bundle, copied/non-copied or member/nonmember row manifest, generated response packet, per-row ADMCD scores, ROC arrays, metric JSON, retained-utility artifact, or verifier is public | keep as Research-only copying / memorization mitigation watch evidence; do not download arXiv source/PDF, generated images, training data, detector assets, Stable Diffusion weights, checkpoints, or inferred code archives; do not implement RAPTA/ADMCD, launch CPU/GPU sidecars, or promote Platform/Runtime rows unless public row-bound pre/post copying artifacts and a reviewed copying/memorization consumer boundary appear |
| GUARD surgical mitigation | Stable Diffusion memorization mitigation / Lane A-B | code-public mitigation watch | arXiv `2603.00133` has official `kairanzhao/GUARD` code at commit `3a49dafe6de652c1a6d9b6dd13758d2e67118094`; the repo exposes inference, detection, mask-generation, metric, and vendored `open_clip` code for `sdv1_500_mem`; arXiv source `HEAD` is a `1,429,877` byte gzip with SHA-256 ETag `7d33099de25263768026fd4d5d45cbb825acbe01bac60ee648843bae565ba625` and was not downloaded | claim boundary is memorized-generation mitigation, not current per-sample membership rows; the repo points to Google Drive benchmark assets and requires Stable Diffusion/reference-model execution, but no checkpoint-bound target identity, immutable row manifest, generated response packet, pre/post mitigation score rows, ROC arrays, metric JSON, retained-utility artifact, or verifier is public | keep as Research-only surgical mitigation watch evidence; do not download arXiv source, GitHub archive, Google Drive assets, SD/reference weights, generated images, masks, or checkpoints; do not run GUARD scripts, launch CPU/GPU sidecars, or promote Platform/Runtime rows unless public row-bound pre/post mitigation artifacts and a reviewed memorization-mitigation consumer boundary appear |
| BAF LoRA parameter-space mitigation | LoRA weight-only / Lane A-B | semantic-shift mitigation watch | arXiv `2605.10439` proposes Base-Anchored Filtering, a post-hoc, training-free, data-free LoRA memorization-mitigation method that decomposes LoRA updates into spectral channels and suppresses weakly backbone-aligned channels as possible memorization carriers; arXiv source `HEAD` is a `5,785,836` byte gzip with SHA-256 ETag `1d10717f5eb4f9ea99d8f36ce0d044e68a937aa88376af20c9d2000a04f6904a` and was not downloaded | claim boundary is weight-only mitigation, not current per-sample membership; arXiv says code is in supplementary material but no official public repository, target LoRA/checkpoint bundle, training-image manifest, member/nonmember rows, generated response packet, score/ROC/metric artifacts, retained-utility artifact, or verifier is public | keep as Research-only LoRA mitigation watch evidence; do not download source/supplement, LoRA weights, SD base weights, training images, generated images, or checkpoints; do not implement BAF, train LoRAs, launch CPU/GPU sidecars, or promote Platform/Runtime rows unless public row-bound artifacts and a reviewed weight-only LoRA mitigation boundary appear |
| Broken Memories | Stable Diffusion memorization / Lane A-watch | semantic-shift paper-source-only watch | arXiv `2605.22050` reports SD `1.4` memorization detection with `AUC > 0.999`, post-mitigation memorization rate `0.0%`, and about `0.01s` overhead; the setup describes `500` Webster memorized prompts, nonmember prompts from Lexica / COCO / GPT-4, LAION-400M reference prompts, and a fine-tuned SD `1.4` LAION subset setup | claim boundary is memorized-generation detection/mitigation rather than current per-sample membership rows; no official code, exact prompt/image manifest, generated image packet, internal trace, per-row score file, ROC array, metric JSON, mitigation-decision artifact, or verifier is public; arXiv source is a `24,383,310` byte gzip and was not downloaded | keep as Research-only memorization watch evidence; do not download the arXiv source, SD weights, LAION/Webster assets, generated images, or baseline repos; do not implement from paper or promote Platform/Runtime rows unless row-bound public artifacts or a reviewed memorization consumer boundary appears |
| IAR Privacy Attacks | image autoregressive / Lane A-watch | code-public watch-plus | arXiv `2502.02514` and official `sprintml/privacy_attacks_against_iars` expose image-generation privacy code for MIA, dataset inference, and extraction; reported claims include IAR `TPR@FPR=1% = 94.57%`, dataset inference with `4` samples, and `698` extracted samples from `VAR-d30`; repository exposes `main.py`, `environment.yaml`, analysis scripts, VAR/RAR/MAR configs, and attack implementations | target family is image autoregressive rather than current diffusion/latent-image rows; no model hashes, immutable ImageNet train/val row manifests, generated sample packet, per-row MIA scores, ROC arrays, metric JSON, DI CSV, memorization CSV, or no-training verifier is committed; README path requires upstream model repos, ImageNet train/val, model downloads, and local output generation | keep as Research-only watch-plus evidence; do not download ImageNet, VAR/RAR/MAR weights, generated samples, memorization candidates, or extraction outputs; do not clone upstream repos or run MIA/DI/extraction scripts unless row-bound replay artifacts appear or a reviewed IAR consumer boundary is opened |
| Silent Brush / Art Arena | style leakage / Lane A-watch | semantic-shift watch with code-notebook inventory | arXiv `2605.17500` introduces Art Arena for evaluating unintended artwork style resurfacing in text-to-image diffusion outputs; anonymous inventory exposes `ArtArena.ipynb`, `README.md`, ET/MD eval and infer scripts, `FT_models.py`, `get_leadger.py`, prep scripts, `CSD/model.py`, `CSD/utils.py`, and figure PDFs | claim boundary is style leakage / copyright evaluation, not current per-sample membership; no target checkpoint hash, immutable member/nonmember artwork manifest, generated image packet, per-row membership score file, ROC array, metric JSON, or ready verifier is visible; raw file/tree/readme endpoints were not metadata-readable, and GitHub searches returned no official public artifact repo | keep as Research-only related privacy evidence; do not download artwork datasets, generated images, SD1.5/SDXL/SANA weights, anonymous repo archives, or the 35,598,493 byte arXiv source tarball; do not run Art Arena scripts or promote Platform/Runtime rows unless a reviewed style-leakage consumer boundary or row-bound membership artifacts appear |
| Trajectory Generation Privacy | trajectory/mobility / Lane A-watch | cross-domain paper-source-only watch | arXiv `2605.15246` evaluates MIA against LSTM-TrajGAN, MoveSim, DiffTraj, and Diff-RNTraj; the diffusion trajectory rows are near random (`0.5012` and `0.4949` AUC-ROC), while the only positive table value is GAN MoveSim `AUC-ROC = 0.7002` | arXiv source tarball has only LaTeX material; exact-title, arXiv-id, author/title, and trajectory-generation GitHub repo/code searches returned no official hits; no trajectory checkpoint, immutable member/nonmember manifest, generated trajectory packet, score rows, ROC arrays, metric JSON, or verifier | keep as cross-domain boundary evidence only; do not download Foursquare/GeoLife/DiDi data, generated trajectories, model checkpoints, or preprocessing assets; do not implement trajectory MIA or promote Platform/Runtime rows unless a trajectory consumer boundary and row-bound artifacts appear |
| Model Will Tell / DRC | black-box/restoration / Lane A-B | paper-source-only restoration-prior watch | arXiv `2403.08487` proposes Degrade Restore Compare: degrade an image, restore it with the target diffusion model, and compare semantic similarity to the original; paper tables report CelebA `AUC = 0.989`, `TPR@1%FPR = 80.46%`, and `TPR@0.1%FPR = 54.52%` | arXiv source tarball has only TeX/style/bibliography/figure files; the paper says authors intend to release code but gives no official code URL; exact-title, DRC phrase, author-name, and arXiv-id GitHub repo/code searches returned no official hits; no target checkpoint, immutable split manifest, restored response packet, score rows, ROC arrays, metric JSON, or verifier | keep as Research-only mechanism watch; do not download Cifar10/Cifar100/CelebA/FFHQ/model/checkpoint assets, implement DRC, run restoration, launch CPU/GPU sidecars, or promote Platform/Runtime rows unless row-bound public artifacts appear |
| Discrete DLM withdrawn paper | text/DLM / Lane B-watch | withdrawn paper-source-only | arXiv `2605.16445` reports Masked Diffusion Language Model membership metrics in the abstract, including MIMIR-domain mean `AUC = 0.878`, peak `AUC = 0.930`, and `K = 3` shadow-transfer mean `AUC = 0.858` | current arXiv record is withdrawn with no current PDF; comments say citations/co-authors need verification; exact-title and topic-style GitHub repo searches returned no repositories; code search for `2605.16445` returned no hits; no official code, target checkpoint, immutable text split manifest, score rows, ROC arrays, metric JSON, or verifier | keep as Research-only watch signal; do not download MIMIR, MDLM checkpoints, language weights, tokenizers, or text datasets; do not implement reconstruction-loss/XGBoost/MLP features or open a text/DLM sidecar unless a corrected paper, artifacts, and consumer-boundary decision appear |
| Stable Diffusion ReDiffuse collaborator artifact | black-box / Lane A | collaborator-local candidate-only artifact | imported `5000`-row `2500 / 2500` result packet replays to `AUC = 0.710319`, `ASR = 0.6846`; holdout bundle reports `test_auc = 0.704604`; new `probe-rediffuse-sd-artifacts` CLI path now audits the packet without rerun | not a public immutable replay packet; member side is a LAION-like repeatable subset rather than the exact paper LAION-5B split; boundary is local-model-query black-box rather than strict external API-only; missing COCO payload is not needed for audit but blocks a fresh end-to-end reproduction | keep as candidate-only black-box evidence; do not request `coco_data`, do not download Stable Diffusion weights, do not rerun `2500 / 2500`, and do not promote Platform/Runtime rows unless public-asset and product-boundary gaps are resolved |
| Structural MIA for T2I | gray-box / Lane B | paper-source-only mechanism watch | arXiv `2407.13252` proposes structure-level membership inference for Latent Diffusion and Stable Diffusion using DDIM inversion/noising plus SSIM, with strong reported low-FPR paper metrics | arXiv source is TeX/figures only, OpenReview supplement is PDF-only, no official code repo or score/split/checkpoint/verifier artifact was found | keep as non-duplicate mechanism watch only; do not download LAION/COCO/model/checkpoint/image payloads, implement SSIM/DDIM scoring, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| Rectified Flow MIA | gray-box / Lane B | paper-source-only mechanism watch | arXiv `2603.13421` proposes Rectified Flow / Flow Matching MIA statistics `T_naive`, `T_mc`, and complexity-calibrated `T_mc_cal`, with reported low-FPR gains on CIFAR-10, SVHN, and TinyImageNet | promised GitHub repo `mx-ethan-rao/MIA_Rectified_Flow` is empty; no public refs, code, split manifests, checkpoints, score rows, ROC arrays, metric JSON, or verifier | keep as non-duplicate mechanism watch only; do not download datasets/models/checkpoints/images, implement from paper, train RF models, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| HF/GitHub public metadata replay packet search | intake / Lane A | closed / no new artifact | authenticated HF metadata and GitHub artifact-shaped searches previously checked for small target/split/score/ROC/manifest packets after DIFFENCE; the 2026-05-23 follow-up used public HF HTTP API metadata because the HF connector token was invalidated and checked `diffusion membership inference`, `member nonmember diffusion`, and `COCO_MIA diffusion`; `OPTML-Group/Diffusion-MU-Attack` was also checked as metadata only | no usable non-duplicate replay packet appeared; known CLiD and CopyMark surfaces remain covered; `OPTML-Group/Diffusion-MU-Attack` is safety-driven diffusion unlearning robustness / adversarial-prompt code with prompt CSVs, configs, attack/evaluation code, and an ONNX harmful-content detector, but no per-sample membership contract, target member/nonmember manifest, response packet, row-bound score file, ROC array, metric JSON, or verifier | keep as anti-duplication evidence; do not download CLiD/CopyMark/UnlearnDiffAtk ZIPs, prompts, images, model/checkpoint payloads, clone large repos, run scripts, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| GitHub lightweight diffusion MIA repos | intake / Lane A | false-positive triage | five direct GitHub search hits were checked: acha1934 fine-tuned diffusion MIA, KarinMalka1 personalization forensics, abramwit Boeing 707 toy project, josephho9 empirical-score MNIST prototype, and hackerman70000/eidetic Carlini-toolkit reproduction | no public checkpoint-bound target, immutable target member/nonmember manifest, row-bound response packet, committed score rows, ROC arrays, metric JSON, trained attack weights, or verifier; some require Colab/Google Drive/local training, while `eidetic` downloads CIFAR-10 and expects local shadow checkpoints despite README-reported metrics | keep as anti-duplication evidence only; do not download notebooks/images/models/CIFAR/Drive payloads, run scripts, train/fine-tune shadow models, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| DEB medical diffusion MIA | gray-box / Lane B | paper-source-only mechanism watch | MDPI Applied Sciences 2026 article reports Discrete Encoding-Based grey-box intermediate-trajectory metrics against SecMI, PIA, and SimA on CIFAR/TinyImageNet and MedMNIST2D subsets | no public code, target checkpoint hashes, immutable member/nonmember manifests, intermediate-state packet, score rows, ROC arrays, metric JSON, or verifier; requires intermediate generation-state access rather than final images only | keep as mechanism watch only; do not download MedMNIST/CIFAR/TinyImageNet/Stable Diffusion assets, implement DEB from the paper, release GPU/CPU sidecar, or promote Platform/Runtime rows |
| same-noise residual comparator family | black-box | candidate-only / hold | seed-12 and seed-23 `64/64` packets retain signal, but low/full residual comparators match or beat mid-band on AUC | single DDPM/CIFAR10 asset, finite tails, no product boundary, mid-frequency specificity not supported | stop same-contract GPU expansion; reopen only with new comparator, second asset, or protocol |
| black-box second response-contract acquisition | black-box | hold / stale skeleton | old Pokemon/Kandinsky skeleton probe returns `needs_query_split`; later CommonCanvas second-response-contract packets were executed and weak across pixel, CLIP, prompt-consistency, response-stability, and denoising-loss scorers | the old skeleton is not the active next lane and filling it would not by itself create a clean second asset | reopen only with a genuinely new public target identity plus exact member/nonmember query images and response/score coverage; do not keep filling the stale Pokemon/Kandinsky template |
| gray-box tri-score successor | gray-box | hold | X-88/X-141/X-142 tri-score truth-hardening closed positive-but-bounded | same-contract expansion would not change admission or product story | reopen only with a genuinely new scorer, surface, or adaptive/low-FPR falsifier |
| Kandinsky/Pokemon response-contract package | black-box | hold / stale skeleton | package preflight is executable but only proves the old skeleton shape | missing query split, endpoint contract, response manifest, and responses; superseded by later weak second-response-contract evidence | do not use this as the default next action; reopen only if real `25/25` or larger member/nonmember query images and responses appear for a clean non-CommonCanvas asset |
| ReDiffuse future reopen | gray-box | hold | collaborator SD packet replays modestly but has source-label boundary issues; local STL-10 bounded denoising-loss and score-norm scouts are random-level | no admitted promotion; no same-family expansion; 800k shortcut, STL-10 step/seed/timestep matrices, Tiny-ImageNet, and Stable Diffusion downloads remain blocked | reopen only with a public third-party checkpoint/score packet, a truly different membership observable, or an explicitly approved long-train checkpoint/score publication contract |
| SecMI admission contract | gray-box | structural-support-only | full-split stat/NNS evidence is strong and evidence-ready; consumer review completed | not admitted; NNS product semantics, adaptive comparability, provenance language, and bundle schema fit remain blocked | keep validators active; no new metrics or promotion until a new schema/adaptive protocol exists |
| CPSample defense artifact | defense / Lane A-B | defense watch-plus | OpenReview ICLR 2025 supplement exposes diffusion/classifier code, configs, training/sampling/inference-attack runners, and four small attack-loss text fragments | no immutable denoiser/classifier checkpoint hashes, exact subset-index manifests, row-bound protected/unprotected score packet, ROC arrays, AUC/ASR/TPR-at-FPR metrics, retained-utility metric contract, or ready verifier | keep as defense watch-plus only; do not download CIFAR-10/CelebA/LSUN/Stable Diffusion/checkpoint/image assets, run `python main.py`, launch CPU/GPU sidecars, or promote defense rows |
| DSiRe / LoRA-WiSE dataset-size recovery | gray-box / Lane A-B | weight-only semantic-shift watch | official `MoSalama98/DSiRe` code and public non-gated HF `MoSalama98/LoRA-WiSE` benchmark expose `7` configs, `2,050` LoRA fine-tuned model rows, `101` parquet shards, and reported dataset-size recovery `MAE = 0.36` images | aggregate LoRA fine-tuning dataset-size recovery, not per-sample membership; no member/nonmember query rows, generated response packet, AUC/ASR/TPR-at-FPR metrics, or current Platform/Runtime consumer semantics | keep as future weight-only privacy lane candidate only; do not download LoRA-WiSE data/images/model/tensors, run `dsire.py`, release GPU/CPU sidecar, or promote Platform/Runtime rows |
| Hyperparameter-free SecMI reproduction | gray-box / Lane A | third-party SecMI-family support-only | `mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models` exposes code, notebook/report surface, and claimed CIFAR-100 seed-0 improvements over baseline SecMINNs | same-family SecMI support; no reusable score rows, ROC arrays, metric JSON, trained attacker weights, verifier packet, independent target checkpoint, or immutable split manifest | keep as anti-duplication support gate only; do not clone, download CIFAR/SecMI checkpoints, run `python run.py`, train attackers, release GPU, or promote Platform/Runtime rows |
| DME dual-model entropy | gray-box / Lane A | stub-repo-only watch | official `F-YaNG1/DME` repo claims complexity-induced bias debiasing for diffusion-model MIA | repo is README-only with no linked paper, implementation code, split manifests, checkpoints, score rows, ROC arrays, metric JSON, figures, or verifier | keep as Research-only watch; do not infer missing method details, implement DME, train dual models, release GPU, or promote Platform/Runtime rows |
| FreMIA frequency-filter MIA | gray-box / Lane A | paper-source-plus-stub-repo watch | ICML 2026 direct diffusion MIA; arXiv source reports strong frequency-filter table metrics and rendered ROC/score figures; official `poetic2/FreMIA` repo exists | official repo is README-only; no implementation code, immutable member/hold-out split manifests, target checkpoints, generated samples, score rows, machine-readable ROC arrays, metric JSON, or verifier | keep as Research-only mechanism watch; do not download datasets/weights/checkpoints, implement filter, run Naive/SecMI/PIA/CLiD variants, release GPU, or promote Platform/Runtime rows |
| FMIA OpenReview frequency artifact | gray-box / Lane B | watch-plus / bounded rechecked | OpenReview `p9uryyZ5bw` still exposes a small official supplementary ZIP with DDIM/Stable Diffusion frequency-filter attack code and duplicated split `.npz` manifests; 2026-05-23 recheck records SHA-256 `567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045`, `79` entries, and `5,117,651` uncompressed bytes | no trained DDIM checkpoints, Stable Diffusion weights, generated samples, `pos_result.npy` / `neg_result.npy`, row-level score exports, ROC CSVs, metric JSON, or ready verifier | keep as watch-plus only; do not download datasets/models/checkpoints/images, train FMIA targets, fine-tune Stable Diffusion, run filter/timestep matrices, release CPU/GPU sidecar, or promote Platform/Runtime rows |
| CopyMark official score artifacts | black-box / Lane A | official score-artifact support-only | official `caradryanl/CopyMark` repo exposes member/nonmember image logs, aggregate ROC/threshold JSONs, selected PIA/PFAMI/SecMI score tensors, GSA feature/XGBoost files, and LAION-RiDAR/mixing results; `laion_ridar` recheck confirms `10000 / 10000` image logs and aggregate `AUROC = 0.872134768572823` | no checkpoint hashes, compact row-ID-bound score manifest, small immutable data/checkpoint packet, or ready verifier output; public `laion_mi` row binding is blocked because current member parquet exposes only `url/caption`, official numeric filenames exceed the public row range, and URL rehydration is partial | keep as Research-side support evidence; do not download HF `datasets.zip`, images, model folders, full repo, run CopyMark scripts, release GPU, or promote Platform/Runtime rows |
| Quantile Diffusion MIA SecMI `t_error` replay | gray-box / Lane A-B | candidate-support-only | third-party public CIFAR10/CIFAR100 SecMI-style score rows and split manifests replay from committed files with positive AUC | not official Quantile Regression paper output; same-family SecMI support only; no admitted-row consumer contract | keep as support evidence only; do not clone full repo, download DDPM/CIFAR/SharePoint assets, train, fit quantile models, or release GPU |
| DualMD / DistillMD disjoint-split defense | defense / Lane A-B | defense watch-plus | OpenReview DDMD supplement exposes DDPM/LDM defense code, DDPM split-index files, and FID stats | embedded GitHub origin is not public; no checkpoint-bound defended/undefended scores, ROC arrays, metric JSON, generated response packets, or ready verifier are released | keep as defense watch-plus only; do not download SharePoint Pokemon, Stable Diffusion, CIFAR/STL/Tiny-ImageNet assets, train, run attack scripts, or release GPU |
| DIFFENCE classifier defense | defense / Lane A-B | defense watch-plus | official repo plus Zenodo `10.5281/zenodo.13706131` snapshot expose code, configs, and split-index files | protected target is an image classifier, diffusion is only a pre-inference defense component, and no checkpoint-bound defended/undefended logits, score rows, ROC arrays, metric JSON, or ready verifier are committed | keep as classifier-defense watch-plus only; do not download Google Drive checkpoints/datasets, train, run MIA scripts, or release GPU |
| MIAHOLD / HOLD++ higher-order Langevin defense | defense / Lane A-B | defense watch-plus | official MIAHOLD repos expose higher-order Langevin defense code, audio split filelists, a CIFAR HOLD config, and PIA-style attack code; arXiv `2605.19170` adds same-family HOLD memorization-mitigation paper context | no checkpoint-bound target artifact, reusable score rows, ROC arrays, metric JSON, generated responses, ready verifier, or new official code/artifact release for `2605.19170` | keep as defense watch-plus only; do not download Google Drive checkpoints/datasets, scrape W&B, train HOLD++ models, implement from the new paper, or release GPU |
| MT-MIA relational diffusion score packet | intake / Lane A | relational-tabular support-only | official `joshward96/MT-MIA` repo exposes multi-table member/nonmember/reference splits, pre-generated ClavaDDPM and RelDiff synthetic outputs, and `18` MT-MIA score/metric JSONL packets | outside current image/latent Platform/Runtime boundary; packets lack row-ID-bound score manifests and no relational-tabular consumer schema exists | keep as Research-only support evidence; do not download raw/synthetic data, full repo, or training assets, regenerate RelDiff, release GPU, or promote Platform/Runtime rows |
| VAE2Diffusion latent-space inversion | gray-box / Lane A | code-public latent-space MIA watch-plus | official `mx-ethan-rao/VAE2Diffusion` repo exposes decoder-geometry / latent-dimension filtering code and LDM/SD scripts; arXiv source claims public splits/checkpoints | README split/checkpoint link is empty; no GitHub releases; recursive tree has no split/checkpoint/score/ROC/metric/response/verifier artifacts; scripts require author-local paths and from-scratch training/fine-tuning/cache generation | keep as latent-space mechanism watch; do not download datasets/models/checkpoints/caches, train/fine-tune, run SimA/PFAMI/PIA variants, release GPU, or promote Platform/Runtime rows |
| DCR copying / replication | intake / Lane A | copying/memorization semantic-shift watch-plus | official `somepago/DCR` repo exposes diffusion replication/copying code, retrieval/similarity scripts, metric helpers, and a committed LAION caption manifest | README LAION-10k Drive split link returns `404`; claim is copying rather than per-sample MIA; no immutable member/nonmember MIA split, target checkpoint, generated response package, score rows, ROC arrays, metric JSON, or ready verifier | keep as copying/privacy watch only; do not download LAION/Drive/model assets, fine-tune, infer, run retrieval, release GPU, or promote Platform/Runtime rows |
| FCRE medical frequency MIA | gray-box / Lane A-B | paper-source-only / cross-domain watch | arXiv `2506.14919` reports frequency-calibrated reconstruction-error MIA metrics on FeTS 2022, ChestX-ray8, and CIFAR-10 | no official code, immutable split manifests, target checkpoints, generated reconstruction packets, score rows, ROC arrays, metric JSON, or ready verifier | keep as method context only; do not download FeTS/ChestX-ray8/CIFAR, train targets, run DDIM reconstruction, sweep frequency bands, release GPU, or promote Platform/Runtime rows |
| Tabular Privacy Leakage TDM | intake / Lane A | single-table tabular watch-plus | arXiv `2605.06835` links official `VectorInstitute/midst-toolkit`; the toolkit exposes ClavaDDPM training/synthesis, Tartan Federer/Ensemble/EPT attacks, privacy/quality metrics, examples, and small integration-test TabDDPM fixtures | no paper-bound Berka/Diabetes target checkpoints, immutable split manifests, generated synthetic tables, score rows, ROC arrays, metric JSON, or ready verifier; current scope lacks a tabular consumer boundary | keep as Research-only watch-plus; do not download Berka/Diabetes/MIDST resources, train targets/shadows, run attacks, release GPU, or promote Platform/Runtime rows |
| Shake-to-Leak code artifact | intake / Lane A | code-public watch-plus | official `VITA-Group/Shake-to-Leak` repo exposes fine-tuning-amplified generative privacy code, vendored SecMI/diffusers code, fine-tuning scripts, SecMI scripts, data extraction code, and a `40`-domain person list | no frozen SD-v1-1 fine-tuned checkpoint, immutable member/nonmember manifest, generated private-set packet, generated attack response, score array, ROC array, metric JSON, or ready verifier output; using it would require SD weights, person/LAION data, generation, fine-tuning, and attack execution | keep as Research-only mechanism watch-plus; do not download assets, clone full repo, generate private sets, fine-tune, run SecMI/data extraction, release GPU, or promote Platform/Runtime rows |
| FSECLab MIA-Diffusion code artifact | intake / Lane A | code-public watch-plus | official `fseclab-osaka/mia-diffusion` repo exposes DDIM/DCGAN training, sampling, white-box attack, black-box attack, dataset-loader, ROC-evaluator code, and two FID-stat `.npz` files | no frozen target checkpoint, immutable split manifest, generated sample packet, score array, ROC array, metric JSON, or ready verifier output; using it would require dataset download and target training/sampling | keep as Research-only code reference; do not download CIFAR-10/CelebA, clone full repo, train/sample DDIM/DCGAN targets, run attack scripts, release GPU, or promote Platform/Runtime rows |
| GSA loss-score LR stability | white-box | CPU-only | leave-one-shadow-out review failed release gate | LR did not beat threshold in enough held-out/target folds | closed; do not GPU-scale |
| CLiD boundary maintenance | black-box | CPU-only / gated metadata | prompt-control boundary anchor and validator exist; 2026-05-23 recheck confirms local HF token presence and readable dataset metadata | no independent image-identity protocol; authenticated range access to `zsf/COCO_MIA_ori_split1/mia_COCO.zip` still returns `403` restricted / not in authorized list, so no ZIP central directory or internal row manifest can be inspected | keep as hold-candidate; no CLiD ZIP download, no GPU, and no admitted row |
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

### 2026-05-26 Paperization Mainline

- `mode`: publication packaging / evidence-contracted measurement paper.
- `status`: first paper workspace created at
  [`../../papers/diffaudit-evidence-paper/README.md`](../../papers/diffaudit-evidence-paper/README.md).
  It contains a paper portfolio, source map, claim register, evidence bank,
  direction-specific version briefs under
  [`../../papers/diffaudit-evidence-paper/versions/README.md`](../../papers/diffaudit-evidence-paper/versions/README.md),
  manuscript-level multi-direction drafts under
  [`../../papers/diffaudit-evidence-paper/multi_direction_paper_drafts.md`](../../papers/diffaudit-evidence-paper/multi_direction_paper_drafts.md)
  and [`../../papers/diffaudit-evidence-paper/versions/drafts/README.md`](../../papers/diffaudit-evidence-paper/versions/drafts/README.md),
  a metadata-only Direction C v0 corpus protocol under
  [`../../papers/diffaudit-evidence-paper/versions/direction-c-corpus-protocol.md`](../../papers/diffaudit-evidence-paper/versions/direction-c-corpus-protocol.md),
  a structured Direction C v1 corpus under
  [`../../papers/diffaudit-evidence-paper/versions/direction-c-corpus-v1.md`](../../papers/diffaudit-evidence-paper/versions/direction-c-corpus-v1.md)
  and [`../../papers/diffaudit-evidence-paper/data/artifact_corpus_v1.csv`](../../papers/diffaudit-evidence-paper/data/artifact_corpus_v1.csv),
  an independent Direction C fixed-search metadata batch under
  [`../../papers/diffaudit-evidence-paper/versions/direction-c-fixed-search-batch-20260526.md`](../../papers/diffaudit-evidence-paper/versions/direction-c-fixed-search-batch-20260526.md)
  and [`../../papers/diffaudit-evidence-paper/data/artifact_corpus_fixed_search_20260526.csv`](../../papers/diffaudit-evidence-paper/data/artifact_corpus_fixed_search_20260526.csv),
  research-team pitches, figure-generation script, CSV/PDF figure assets,
  selected-corpus Direction C gate-summary outputs, IEEEtran `main.tex`,
  bibliography, build notes, and compiled 8-page
  `paper.pdf`.
- `primary thesis`: DiffAudit should be written as an evidence-calibrated
  security/privacy measurement paper: strong diffusion MIA scores are useful
  only when bound to target identity, split, score/response coverage, metric
  provenance, consumer boundary, and surface delta.
- `candidate tracks`: Direction A evidence-contracted auditing is primary;
  Direction B output-cloud geometry is a mechanism short/workshop candidate
  needing a second response asset or explicit H2-short-paper scope for
  standalone promotion; Direction C reproducibility/claim-support now has a
  21-row structured v1 corpus from existing evidence notes plus a 17-row
  fixed-search metadata batch plus selected-corpus gate-summary outputs and a
  selected-corpus consistency pass with no CSV label changes, but standalone
  aggregate claims still need a broader corpus or second independent label review;
  Direction D consumer-boundary systems paper is later artifact/demo material
  and needs deployment, external-use, user-study, or report-drift evidence.
- `next action`: Direction A has been expanded from the initial paper skeleton
  to an 8-page draft with stronger method, evidence-state, metric-replay,
  audit-surface framing, corpus-protocol, fixed-search integration,
  selected-corpus gate-summary figure, H2 admission decision, non-admitted
  decision-value table, and artifact-release framing. Continue polishing venue
  framing and prose density; use Direction C v1 plus the fixed-search batch and
  gate-summary assets for selected-corpus claim-control drafting. Do not launch
  heavyweight model training or same-family sweeps for paper padding.
- `stop rule`: every paper claim must pass `claim_register.md`; candidates and
  support-only rows must remain visually and textually distinct from admitted
  rows.

### 2026-05-25 Research Resting State

- `mode`: post-H2 output-cloud cross-cache transfer and img2img portability review / post-ReDiffuse STL-10 weak scout / post-feature-packet consumer verdict.
- `status`: H2 output-cloud geometry is the latest strong Research-side candidate, with the existing `512 / 512` response-cache review, two `256 / 256` shared-position order-control scouts, and a CPU-only fold-disjoint transfer review retaining strong signal while label-shuffle stays random-level. The transfer review gives seed `176` -> `177` `AUC = 0.948990`, `TPR@1%FPR = 0.375000`, `TPR@0.1%FPR = 0.058594`, and seed `177` -> `176` `AUC = 0.970520`, `TPR@1%FPR = 0.390625`, `TPR@0.1%FPR = 0.074219`. The SD/CelebA img2img portability review is weak or unstable on the admission cache (`AUC = 0.7888`, strict-tail recovery `0.0`) and not distinct from simple distance, so it does not release img2img sweeps or product work. It is not admitted because it is still a single H2 response-cache geometry candidate, not a second public asset or Platform/Runtime contract.
- `status`: ReDiffuse STL-10 is closed by default. The official split and local CUDA path are executable, but the bounded `300`-step target produced random-level fixed-timestep denoising-loss metrics, and the same checkpoint/split also failed a SimA-style denoiser-output score-norm scorer.
- `status`: Feature-packet consumption remains deferred. Tracing the Roots is positive Research-only evidence, but there is no second public non-source-equivalent feature packet and no raw target/sample/regeneration asset.
- `goal`: next cycle must select exactly one high-information task. Valid reopen triggers are a public third-party checkpoint/score packet, a genuinely different membership observable with bounded preflight, an explicit cross-modal/feature-level consumer-boundary decision, or an approved long-train checkpoint/score publication contract.
- `stop rule`: if a candidate cannot pass target identity, exact split, query/response or score coverage, provenance, and non-adjacent mechanism gates, stop rather than writing another scope/audit/reselection chain.
- `GPU cap`: none selected.
- `CPU sidecar`: none selected after H2 img2img output-cloud portability review.
- `integration`: no schema change; admitted five-row consumer set remains intact; H2 output-cloud, H2 simple-distance, ReDiffuse, CLiD, Tracing Roots, SecMI stat/NNS, and MT-MIA remain outside Platform/Runtime admitted rows.

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
- [../../docs/evidence/gray-box-paper-candidate-reentry-review-20260512.md](../../docs/evidence/gray-box-paper-candidate-reentry-review-20260512.md)
- [../../docs/evidence/post-secmi-next-lane-reselection-20260511.md](../../docs/evidence/post-secmi-next-lane-reselection-20260511.md)
- [../../docs/evidence/white-box-influence-curvature-feasibility-scout-20260511.md](../../docs/evidence/white-box-influence-curvature-feasibility-scout-20260511.md)
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
| Simple-distance second asset | no valid second image-to-image or repeated-response contract | follow [../../docs/evidence/black-box-response-contract-asset-acquisition-spec.md](../../docs/evidence/black-box-response-contract-asset-acquisition-spec.md) before GPU |

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
