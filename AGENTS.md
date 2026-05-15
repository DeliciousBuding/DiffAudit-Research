# Research Agent Guide

This file is the operating guide for agents and teammates working in `Research/`.

## Repository Role

`Research/` holds research code, configs, experiment status, and
results for diffusion-model privacy auditing. Product UI is in
`Platform/`; job scheduling is in `Runtime-Server/`.

## Fresh-Session Intake

Read in this order:

1. `<DIFFAUDIT_ROOT>/ROADMAP.md`
2. `<DIFFAUDIT_ROOT>/Research/ROADMAP.md`
3. `<DIFFAUDIT_ROOT>/Research/README.md`
4. `<DIFFAUDIT_ROOT>/Research/docs/README.md`
5. `<DIFFAUDIT_ROOT>/Research/docs/start-here/getting-started.md`
6. `<DIFFAUDIT_ROOT>/Research/docs/evidence/reproduction-status.md`
7. `<DIFFAUDIT_ROOT>/Research/docs/product-bridge/README.md`
8. `<DIFFAUDIT_ROOT>/Research/docs/governance/research-governance.md`
9. `<DIFFAUDIT_ROOT>/Research/docs/rebuild/README.md`
10. `<DIFFAUDIT_ROOT>/Research/docs/evidence/workspace-evidence-index.md`
11. The relevant `workspaces/<direction>/README.md` and `plan.md`

Do not start from memory or old chat context. Re-anchor on repository files.

## Current Operating State

- Active work: `Tabular Privacy Leakage TDM artifact gate completed after the TMIA-DM temporal artifact gate. Status: On Privacy Leakage in Tabular Diffusion Models is single-table tabular diffusion watch-plus / official code-public / no paper score packet / no download / no GPU release; TMIA-DM remains paper-only temporal-noise gradient MIA / reported metrics only / no code-score artifact / no download / no GPU release / no admitted row. active_gpu_question = none; next_gpu_candidate = none; CPU sidecar = none selected after Tabular Privacy Leakage TDM artifact gate, with Berka, Diabetes, MIDST Google Drive resources, ClavaDDPM checkpoints, generated synthetic tables, target/shadow training, Tartan Federer, Ensemble, and EPT execution still blocked.`
- Next GPU candidate: none selected
- Long-horizon control: follow `ROADMAP.md` section
  `Long-Horizon Research Task Board（2026-05-13 起）` before reopening any
  Research lane. The selected forward path is Lane A external asset acquisition
  watch unless a genuinely new mechanism family satisfies the same gates; do
  not create another scope/audit/reselection chain when no candidate passes
  target identity, exact member/nonmember split, query/response coverage, and
  non-adjacent mechanism checks.
- Continuous-run discipline: use the roadmap loop
  `Anchor -> Select -> Execute -> Reflect -> Archive -> Merge` for every
  autonomous cycle. Each cycle must name exactly one primary artifact type
  (`asset verdict`, `metric verdict`, `consumer verdict`, or
  `roadmap operating-system update`), update the three slots
  `active_gpu_question` / `next_gpu_candidate` / `CPU sidecar`, and close with
  a clean `main` after PR/merge when repository files change.
- Reflection/correction discipline: enforce the No-stationery, Two-weak-runs,
  Membership semantics, Response contract, Consumer honesty, and stale-doc
  conflict gates from `ROADMAP.md`. If a step only adds process around a weak
  lane, stop or switch lanes instead of adding another scope/audit chain.
- CPU work: stop expanding blocked or pseudo-membership routes. Beans/SD1.5 is
  contract/debug only because beans train/validation is not proven SD1.5
  membership. MNIST/DDPM via `1aurent/ddpm-mnist` has cleaner train/test
  membership semantics, but raw PIA-style loss and simple `x0`
  reconstruction residuals are weak. A tiny controlled MNIST denoiser with a
  real train/held-out split also failed under raw denoising loss despite
  decreasing training loss; a deliberately overfit `8`-member upperbound still
  produced only weak raw-MSE AUC and zero low-FPR recovery. A final-layer
  per-sample gradient-norm scout on that same overfit target is positive
  (`AUC = 0.734375`, `1 / 8` members recovered at zero false positives), so the
  next mechanism candidate became gradient-sensitive, not MSE. The less extreme
  `16 / 64` stability gate weakens that result to `AUC = 0.535156`. The
  2026-05-13 `64 / 64` oracle-style final-layer gradient prototype alignment
  follow-up is also weak (`AUC = 0.500977`, zero low-FPR recovery), so
  same-family final-layer gradient norm/cosine variants are closed by default
  and do not release GPU or layer sweeps. A quick external
  diffusion benchmark scan did not find a ready target whose model card alone
  proves exact member/nonmember provenance. CopyMark is now the highest-value
  external intake candidate because its paper-level protocol is explicitly about
  diffusion membership/copyright detection. Its diffusers README, scripts, and
  zip central directory now show a concrete directory-level member/holdout
  contract with `eval` and `test` splits, but the archive itself carries only
  images plus `caption.json` fields (`path`, `height`, `width`, `caption`), not
  per-row membership provenance. A local
  `response-contract-copymark-commoncanvas-20260512` query split exists under
  `<DIFFAUDIT_ROOT>/Download` with `50` CommonCatalog member queries and `50`
  COCO holdout queries. The `diffaudit-research` conda environment has CUDA
  Torch (`cu121`) and can see the local RTX 4070 Laptop GPU; do not confuse the
  default PATH CPU-only Python with the actual research environment. The
  `common-canvas/CommonCanvas-XL-C` single checkpoint has been downloaded, a
  CUDA smoke passed, deterministic `50/50` text-to-image responses were
  generated, and the package probe returns `ready`. The first simple scorer
  `negative_pixel_mse_resized_512` is weak (`AUC = 0.5736`, `ASR = 0.6000`,
  `TPR@1%FPR = 0.04`, `TPR@0.1%FPR = 0.04`). The only approved sharper
  response-vs-query similarity follow-up, `clip_vit_l14_query_response_cosine`,
  is weaker (`AUC = 0.4588`, `ASR = 0.5300`, zero low-FPR recovery). The
  distinct prompt-response consistency scorer is also weak (`AUC = 0.4408`,
  `ASR = 0.5100`, `1 / 50` member recovered at zero false positives). A bounded
  multi-seed response-distribution stability scout on `4 / 4` prompts and two
  fixed seeds is also weak (`AUC = 0.5625`, `ASR = 0.625`, `1 / 4` zero-FP
  recovery), so do not expand it into seed, subset, or embedding-metric sweeps.
  A genuinely different CommonCanvas conditional denoising-loss scout on the
  existing `50/50` packet is also weak (`AUC = 0.5148`, `ASR = 0.5700`,
  `TPR@1%FPR = 0.02`), so do not expand it into timestep, resolution,
  scheduler, seed, loss-weight, or subset matrices.
  This is not admitted and does not trigger Platform/Runtime consumption. Do
  not expand this into a CLIP/pixel/LPIPS/prompt-adherence/stability metric
  or denoising-loss matrix by default; close the current CommonCanvas packet unless a genuinely
  new mechanism or new asset is proposed. Do not return to I-B remap training,
  Beans distance variants,
  MNIST raw/x0 residual repeats, tiny-denoiser MSE ablations, final-layer
  gradient norm/cosine variants, external-weight downloads without provenance,
  full CopyMark dataset download, CommonCanvas multi-seed stability repeats,
  MIDST nearest-neighbor variants, gradient layer sweeps, or same-contract
  residual repeats by default. Kohaku
  XL / Danbooru is also not a selected
  next asset: model cards give broad HakuBooru/Danbooru2023 training-source
  provenance, but no exact target member list or fixed selection manifest. Do
  not download `38-40 GB` Kohaku weights or TB-scale Danbooru image assets for
  pseudo-membership scoring. A small Fashion-MNIST DDPM PIA-style loss scout
  on `ynwag9/fashion_mnist_ddpm_32` used a real Fashion-MNIST train/test split
  and CUDA, but remained weak (`AUC = 0.535889`, `TPR@1%FPR = 0.03125`).
  A genuinely different SimA single-query denoiser score-norm scout on the
  same split is also weak (`AUC = 0.515137`, `TPR@1%FPR = 0.0`).
  A local score-Jacobian sensitivity scout on the same split is also weak
  (`AUC = 0.511719`, `TPR@1%FPR = 0.0`); do not expand Fashion-MNIST into
  seed, timestep, `p`-norm, perturbation-scale, scheduler, norm, or
  packet-size sweeps. MIDST TabDDPM
  black-box single-table is locally scoreable and has exact member/nonmember
  labels. Nearest-synthetic-row distance is weak (`dev+final AUC = 0.566263`,
  `TPR@1%FPR = 0.016750`); shadow-trained marginal-distributional learning
  overfits `train` but collapses on dev+final (`AUC = 0.499846`,
  `TPR@1%FPR = 0.013000`); and a MIA-EPT-style error-prediction profile also
  transfers weakly (`AUC = 0.530089`, `TPR@1%FPR = 0.029500`). The official
  CITADEL/UQAM Blending++ score exports are the strongest MIDST signal so far
  (`dev+final AUC = 0.598079`, `ASR = 0.563500`,
  `TPR@1%FPR = 0.095750`), but remain below the `0.60` AUC reopen floor. Do not
  expand MIDST into XGBoost/Optuna retraining, Gower feature matrices, TabSyn,
  white-box MIDST, multi-table MIDST, nearest-neighbor preprocessing matrices,
  classifier sweeps, EPT account/column/config grids, or marginal feature
  matrices unless a genuinely different tabular-diffusion membership mechanism
  or new public artifact appears. A bounded Beans member-LoRA scout repaired the
  old pseudo-membership semantics by creating an exact target
  (`SD1.5 + Beans-member UNet LoRA`) and holding out `25` nonmembers, but
  conditional denoising-loss is weak (`AUC = 0.414400`, reverse `0.585600`,
  `TPR@1%FPR = 0.080000`) and parameter-delta sensitivity is also weak
  (`AUC = 0.512000`, `TPR@1%FPR = 0.040000`). Do not expand Beans LoRA
  train-step, rank, resolution, prompt, scheduler, loss-weight, timestep,
  layer, or block matrices by default.
  Quantile Regression is a useful sample-conditioned reconstruction-loss
  mechanism reference, but the latest public packet is only third-party
  SecMI-style support evidence. `neilkale/quantile-diffusion-mia` exposes
  committed CIFAR10/CIFAR100 `t_error` score rows and split manifests, and
  replaying `score = -t_error` is positive, but this is not the official
  Quantile Regression paper output or an admitted row. Do not clone the full
  repo, download DDPM/CIFAR/SharePoint assets, train STL10/Tiny-ImageNet
  DDPMs, fit quantile models, recover W&B artifacts, reconstruct SecMI splits,
  or build a quantile-regression implementation from scratch before official
  quantile artifacts or a bounded verifier exist.
- Shake-to-Leak / `VITA-Group/Shake-to-Leak` is a code-public
  generative-privacy watch-plus item, not a replay target. The public repo
  exposes the SatML 2024 paper code, vendored SecMI/diffusers code,
  fine-tuning scripts, SecMI scripts, data extraction code, and a `40`-domain
  celebrity/person list. Its execution path locally generates `2,000`
  synthetic private images per domain from `CompVis/stable-diffusion-v1-1`,
  fine-tunes checkpoints under `./ckpts/<domain>/`, expects local
  `data/laion-2b` and `data/celeb_and_web` member/nonmember folders, and then
  prints SecMI AUROC or generates extraction candidates at runtime. It commits
  no frozen target checkpoint, immutable sample membership manifest, generated
  private-set packet, generated attack response, per-sample score array, ROC
  array, metric JSON, or ready verifier. Do not download SD weights,
  LAION/person images, synthetic private sets, checkpoints, or full repo
  payloads; do not run `sp_gen.py`, LoRA/DB/End2End fine-tuning, SecMI scripts,
  or data extraction; and do not promote it into Platform/Runtime rows without
  public checkpoint-bound score artifacts and immutable membership semantics.
- TMIA-DM / `Temporal Membership Inference Attack Method for Diffusion Models`
  is a previously known gray-box mechanism whose current public surface is
  paper-only, not a replay target. The CRAD article reports
  CIFAR/Tiny-ImageNet-style experiments and a Pokemon/LAION/COCO-style
  setting, but the public page lists `资源附件(0)` and no official code, target
  checkpoint, immutable split manifest, per-sample score rows, ROC arrays,
  metric JSON, or verifier output is public. Do not download
  CIFAR/Tiny-ImageNet/Pokemon/LAION/COCO assets, train or fine-tune diffusion
  targets, reconstruct temporal-noise trajectory pipelines, launch GPU work,
  or promote TMIA-DM without official code plus immutable target/split
  artifacts and reusable score packets.
- DualMD / DistillMD remains defense watch-plus only. The OpenReview `DDMD/`
  supplementary archive exposes DDPM/LDM training, disjoint teacher,
  distillation, PIA/SecMIA, black-box attack code, DDPM split-index files, and
  FID stats, but the embedded `btr13010/DDMD` GitHub origin is not public and
  the supplement ships no checkpoint-bound defended/undefended scores, ROC
  arrays, metric JSON, generated response packet, or ready verifier. Do not
  download the SharePoint Pokemon payload, Stable Diffusion weights,
  CIFAR/CIFAR100/STL10/Tiny-ImageNet datasets, run DDPM/LDM training,
  distillation, SecMIA/PIA, black-box attack scripts, launch GPU work, or
  promote disjoint-split defense rows until checkpoint-bound score artifacts
  and a consumer-boundary decision exist.
- MIAHOLD / HOLD++ higher-order Langevin remains defense watch-plus only. The
  official `bensterl15/MIAHOLD` and
  `bensterl15/MIAHOLDCIFAR` repos expose defense code, audio split filelists, a
  CIFAR HOLD config, and PIA-style attack code, but no checkpoint-bound target
  artifacts, reusable member/nonmember scores, ROC arrays, metric JSON,
  generated responses, or ready verifier outputs. Do not download
  Grad-TTS/HiFi-GAN/CLD-SGM checkpoints, CIFAR/CelebA/audio datasets, scrape
  W&B artifacts, train HOLD++ models, launch GPU work, or promote defense rows
  until checkpoint-bound score artifacts exist.
- DIFFENCE is classifier-defense related-method watch-plus only. The official
  `SPIN-UMass/Diffence` repo exposes code, configs, and small split-index files,
  but the protected target is an image classifier and diffusion is an
  input-side purification/pre-inference defense component, not the audited
  diffusion generator. The repo relies on Google Drive classifier/diffusion
  checkpoints and local result generation; it commits no defended/undefended
  logits, score rows, ROC arrays, metric JSON, or ready verifier. Do not
  download DIFFENCE model folders or CIFAR/SVHN payloads, train classifiers or
  diffusion models, generate reconstructions, run its MIA scripts, launch GPU
  work, or promote classifier-defense rows without a consumer-boundary decision
  and checkpoint-bound score artifacts.
- Paperization/consumer boundary: recent weak/watch lines, including
  CommonCanvas, MIDST, Beans LoRA, Quantile Regression, MIAGM, LAION-mi,
  Zenodo fine-tuned diffusion, Noise as a Probe, Noise Aggregation,
  Kohaku/Danbooru, MIDM, DMin, ELSA Health Privacy,
  Memorization Anisotropy, StablePrivateLoRA, DualMD/DistillMD,
  MIAHOLD/HOLD++, DIFFENCE, LSA-Probe, MT-MIA, FSECLab MIA-Diffusion,
  Shake-to-Leak, and TMIA-DM,
  remain limitations or future-work hooks only. Platform/Runtime and
  paperization admitted claims still use only `recon`, `PIA baseline`,
  `PIA defended`, `GSA`, and `DPDM W-1`.
- Official `zhaisf/CLiD` now has a public CPU replay packet under
  `inter_output/*`: replaying the official threshold path selects
  `alpha = 0.9` and reaches target `AUC = 0.961277`,
  `TPR@1%FPR = 0.675470`, and `ASR = 0.891957`, much stronger than PIA,
  SecMI, and PFAMI on the same packet. It remains candidate-only because the
  packet is prompt-conditioned and the public metadata does not bind numeric
  score rows to immutable COCO image identities. The HF dataset exposes only
  gated `mia_COCO.zip`, and authenticated HEAD/Range probes returned `403`;
  a 2026-05-15 live recheck still returns `403` for authenticated `HEAD`,
  start `Range`, and end `Range` probes. A machine-readable candidate-only
  card exists at
  `docs/product-bridge/clid-candidate-evidence-card.json` for
  Research/product-boundary comparison, not Platform/Runtime admission.
  Do not download `mia_COCO.zip`, `COCO_MIA_ori_split1`, SD weights, CLiD
  target/shadow checkpoints, or generated images; do not run CLiD GPU jobs,
  XGBoost sweeps, prompt-shuffle matrices, or promote CLiD into
  Platform/Runtime admitted rows without an image-identity-safe protocol and
  product-bridge handoff.
- Tracing the Roots now has a machine-readable candidate-only product bridge
  card at `docs/product-bridge/tracing-roots-candidate-evidence-card.json`.
  The OpenReview supplementary CIFAR10 diffusion-trajectory feature packet
  remains positive (`AUC = 0.815826`, `accuracy = 0.737500`,
  `TPR@1%FPR = 0.134000`, `TPR@0.1%FPR = 0.038000`), but it is
  Research-only feature-packet evidence. The 2026-05-15 primary-source recheck
  found the OpenReview attachment still reachable and arXiv `2411.07449v3`
  source still TeX/figures-only, with no raw target checkpoint identity,
  member/external sample manifest, image query-response packet, or
  feature-regeneration script. Do not download raw CIFAR/CelebA-HQ/FFHQ assets,
  target checkpoints, or generated images; do not expand timestep,
  feature-family, seed, classifier, optimizer, or regularization sweeps; do not
  promote Tracing the Roots into Platform/Runtime admitted rows unless
  DiffAudit explicitly opens a non-black-box feature-packet consumer lane.
- FMIA / `Unveiling the Impact of Frequency Components on Membership Inference
  Attacks for Diffusion Models` is watch-plus only. The OpenReview supplement
  is small and ships frequency-filter DDIM/Stable Diffusion attack code plus
  exact `CIFAR10`, `CIFAR100`, `STL10-Unlabeled`, and `TINY-IN` split
  manifests, but it does not ship trained checkpoints, Stable Diffusion
  weights, generated samples, `pos_result.npy` / `neg_result.npy`, ROC CSVs,
  metric JSON, or ready score packets. Do not download datasets, train FMIA
  DDIM targets, fine-tune Stable Diffusion, run filter/timestep matrices, or
  promote FMIA into Platform/Runtime admitted rows without ready score artifacts
  and a product-bridge handoff.
- SimA / `Score-based Membership Inference on Diffusion Models` is watch-plus
  only. The official `mx-ethan-rao/SimA` repo is code-public and implements a
  distinct denoiser-output score-norm attack across DDPM, Guided Diffusion,
  LDM, SD1.4, and SD1.5 scripts, but its public surface has empty split and
  checkpoint links, no GitHub release assets, no non-vendor split manifests,
  no checkpoints, no score arrays, no ROC/metric artifacts, and no ready
  verifier. Do not download large datasets, train DDPM targets, fine-tune
  SD1.4, request checkpoints by email, run SimA GPU jobs, expand
  Fashion-MNIST SimA variants, or promote SimA into Platform/Runtime admitted
  rows unless public split/checkpoint/score artifacts appear.
- GenAI Confessions / `hanyfarid/MembershipInference` is a black-box
  related-method watch item, not an execution target. The public release has
  STROLL, Carlini, and Midjourney raw member/nonmember-style image inputs, but
  it does not ship the STROLL fine-tuned SD2.1 checkpoint, generated
  image-to-image response grids, DreamSim distance vectors, ROC/metric
  artifacts, Midjourney query logs, or a ready verifier. Do not download the
  Zenodo/HF image payloads, fine-tune STROLL SD2.1, query Midjourney manually,
  rebuild DreamSim/logistic-regression replay from scratch, or promote it into
  Platform/Runtime rows without a consumer-boundary decision and ready
  response/metric artifacts.
- DurMI / `DurMI: Duration Loss as a Membership Signal in TTS Models` is a
  TTS/audio cross-modal watch-plus item, not an image/latent-image execution
  target. The OpenReview supplement ships GradTTS, WaveGrad2, and VoiceFlow
  attack code plus an exact GradTTS LJSpeech `5,977 / 5,977`
  member/nonmember split; Zenodo publishes open metadata for three dataset
  archives and nine model checkpoints. It is not runnable in the current cycle
  because the public packet does not ship ready duration-loss score arrays,
  ROC arrays, metric JSON, generated result graphs, or a TTS consumer-boundary
  decision. Do not download the Zenodo audio datasets/checkpoints, fetch
  Google Drive TextGrid files, train or run TTS attacks, launch DurMI GPU jobs,
  or promote TTS/audio claims into Platform/Runtime rows unless DiffAudit
  explicitly opens a TTS/audio membership lane or ready score artifacts appear.
- LSA-Probe / `Membership Inference Attack Against Music Diffusion Models via
  Generative Manifold Perturbation` is a music/audio cross-modal watch-plus
  item, not an image/latent-image execution target. The public project repo has
  only `README.md` and says implementation/reproducibility instructions will be
  released upon acceptance. The visible GitHub Pages `data/*.json` arrays are
  generated by `lsa-probe/generate_demo_data.py` as mock demo data with seeded
  random member/nonmember adversarial-cost distributions, not checkpoint-bound
  paper scores. Do not download MAESTRO, FMA-Large, DiffWave, MusicLDM, audio
  clips, checkpoints, or demo JSON as experiment evidence; do not implement
  LSA-Probe from the TeX or demo; and do not promote music/audio support into
  Platform/Runtime rows unless real target identities, exact splits, and
  adversarial-cost score/ROC artifacts appear or DiffAudit explicitly opens a
  music/audio lane.
- ELSA Health Privacy Challenge / `PMBio/Health-Privacy-Challenge` is a
  biomedical synthetic-data MIA benchmark watch-plus item, not a current
  image/latent-image execution target. The public starter package has baseline
  MIA code, a label/prediction/metric example packet, and names Noisy Diffusion
  among challenge targets, but the actual challenge datasets and metadata
  require ELSA platform registration and a data download agreement. Do not
  register, accept agreements, download challenge data, or treat the public
  starter example AUC as a Noisy Diffusion research result unless DiffAudit
  explicitly opens a biomedical synthetic-data MIA lane or public-safe
  Noisy Diffusion target/split/score artifacts appear.
- DMin / `DMin: Scalable Training Data Influence Estimation for Diffusion
  Models` is a diffusion data-attribution watch-plus item, not a membership
  inference execution target. The public release has an SD3 LoRA, mixed
  dataset, compressed-gradient cache, and retrieval index artifacts, but it has
  no member/nonmember labels, MIA score rows, ROC arrays, or AUC/ASR/TPR-at-FPR
  metric packet. Do not download the mixed dataset, SD3 base assets, LoRA
  payloads, cached gradients, or retrieval index by default; do not reframe
  data-attribution retrieval as membership inference unless DiffAudit
  explicitly opens a training-data attribution lane or DMin releases a bounded
  MIA score/metric packet.
- Memorization Anisotropy / `Detecting and Mitigating Memorization in
  Diffusion Models through Anisotropy of the Log-Probability` is a
  prompt-level memorization watch-plus item, not a current per-sample
  image/latent-image MIA execution target. The official ICLR 2026 release has
  code and public SD v1.4, SD v2, and Realistic Vision prompt splits, but no
  released score tensors, ROC/metric artifacts, generated image packet, model
  snapshot hashes, or image-identity MIA manifest. Do not download SD v1.4,
  SD v2, Realistic Vision, generated images, or MemBench-style assets; do not
  run prompt-memorization CUDA forward passes, seed/generation/mode/gamma
  sweeps, or mitigation notebooks unless ready score artifacts appear or
  DiffAudit explicitly opens a prompt-memorization lane.
- Noise Aggregation / `Noise Aggregation Analysis Driven by Small-Noise
  Injection` is a paper-source-only diffusion MIA watch item. arXiv
  `2510.21783` v2 reports strong DDPM paper metrics (`CIFAR-10 AUC = 0.957`,
  `TPR@1%FPR = 28.7`) and a distinct small-noise predicted-noise aggregation
  mechanism, but the public source is only TeX, bibliography, and figures. No
  official code, target checkpoints, exact split manifests, score arrays, ROC
  CSVs, metric JSON, or query/response packet were found. Do not download
  Stable Diffusion weights, LAION-aesthetic-5plus, COCO2017-Val,
  CIFAR/Tiny-ImageNet, train DDPMs, implement the method from scratch, launch
  CPU/GPU sidecars, or promote it into Platform/Runtime rows unless public-safe
  code, target/split manifests, and reusable score artifacts appear.
- FERMI / `FERMI: Exploiting Relations for Membership Inference Against
  Tabular Diffusion Models` is a multi-relational tabular watch item, not a
  current execution target. The 2026-05-12 arXiv source reports strong
  TabDDPM/TabDiff/TabSyn relational MIA metrics, but the public surface is
  paper-source only: no code tree, target/split manifests, generated synthetic
  tables, feature/score rows, ROC arrays, metric JSON, or replay command. Do
  not implement FERMI from scratch, download California/Instacart/Berka
  relational datasets, train TabDDPM/TabDiff/TabSyn or surrogate models, or
  reopen MIDST/tabular execution unless public artifacts appear or DiffAudit
  explicitly opens a multi-relational tabular membership lane.
- `On Privacy Leakage in Tabular Diffusion Models: Influential Factors,
  Attacker Knowledge, and Metrics` is a single-table tabular diffusion
  watch-plus item, not a current execution target. The arXiv source is TeX plus
  figures only, but the paper links the official `VectorInstitute/midst-toolkit`
  code. That toolkit exposes ClavaDDPM training/synthesis, Tartan
  Federer/Ensemble/EPT attacks, privacy/quality metrics, examples, and small
  integration-test TabDDPM fixtures. It does not release the paper's
  Berka/Diabetes target checkpoints, immutable split manifests, generated
  synthetic tables, score rows, ROC arrays, metric JSON, or ready verifier.
  Do not download Berka, Diabetes, MIDST Google Drive resources, target
  checkpoints, or generated tables; do not run the attacks or train targets
  from scratch unless public paper-bound artifacts appear or DiffAudit opens a
  reviewed tabular consumer-boundary lane.
- MT-MIA / `Finding Connections: Membership Inference Attacks for the
  Multi-Table Synthetic Data Setting` is a relational tabular diffusion
  score-packet support item, not a current image/latent-image execution target.
  The official `joshward96/MT-MIA` repository publishes member/nonmember/
  reference splits, pre-generated ClavaDDPM and RelDiff synthetic relational
  tables, and `18` official MT-MIA score/metric JSONL packets. It remains
  cross-modal support-only because it is outside the current Platform/Runtime
  consumer boundary, lacks row-level score IDs suitable for product admission,
  and has no reviewed relational-tabular schema. Do not download the raw
  figshare datasets, synthetic CSV payloads, ClavaDDPM/RelDiff training assets,
  or full repository; do not regenerate RelDiff or promote MT-MIA into
  Platform/Runtime rows unless DiffAudit explicitly opens a relational tabular
  synthetic-data membership lane or row-ID-bound verifier artifacts appear.
- `WilliamLUO0/StablePrivateLoRA` is a defense watch-plus candidate with public
  dataset split payloads and MP-LoRA/SMP-LoRA training code. It is not an
  execution target because the repo does not ship trained LoRA/checkpoint
  hashes, raw per-sample attack scores, ROC CSVs, metric JSON, generated
  responses, or a ready verifier command. Do not clone or download the large
  dataset payloads, SD-v1.5 base model, LoRA checkpoints, generated images, or
  logs; do not train MP-LoRA/SMP-LoRA or promote it into Platform/Runtime
  defense rows unless public checkpoint-bound score artifacts appear.
- `HailongHuPri/MIDM` is an image-diffusion watch-plus candidate with concrete
  FFHQ DDPM loss/likelihood attack code, `ffhq_1000_idx.npy` member-index
  semantics, `1000/1000` labels in `Example.ipynb`, and fixed-FPR TPR metric
  code. It is not an execution target because the repo does not commit fixed
  member/nonmember manifests, HDF5 score packets, ROC/metric artifacts, or
  notebook outputs, and the advertised Google Drive checkpoint was not
  fetchable for metadata here. Do not download FFHQ, request or scrape
  checkpoint access, train MIDM DDPM, or run loss/likelihood scoring from
  scratch unless public fixed manifests, checkpoint hash/size/training binding,
  and ready scores appear.
- MIA_SD / face-LDM is a related code reference only: the public repo says the
  experiment images are not published, gives fine-tuning scripts with local
  `TRAIN_PATH` / `OUT_PATH` placeholders, and does not release a target
  checkpoint, exact member/nonmember split manifest, or query/response packet.
  Do not scrape staff images, train SD1.5 for 400 epochs, or reconstruct private
  folders from result traces.
- MoFit / caption-free gray-box MIA is mechanism-relevant, but the public
  repository still marks code instructions as `TBW` and this workspace has no
  released target checkpoint, exact split manifest, or ready cache contract.
  Do not implement the surrogate/embedding optimization from scratch or release
  GPU until upstream code and exact assets exist.
- Cardio-AI `memorization-ldm` is a non-duplicate medical LDM memorization
  watch candidate, but the public release is code plus request-gated synthetic
  samples and detector checkpoints. It does not expose a target LDM checkpoint,
  exact per-sample member/nonmember manifests, or generated response package.
  Do not download medical datasets, request controlled samples, train the
  target LDM, or reconstruct the paper pipeline unless public-safe target,
  split, and response artifacts appear.
- `jinhaoduan/SecMI-LDM` is a support-family SecMI LDM Diffusers fork, not a
  clean Lane A second asset. The default-branch README provides SharePoint
  download links for a dataset bundle and Pokémon fine-tuned SD checkpoint,
  but this remains same-author SecMI reproduction/support material rather than
  an independent second asset or black-box response contract. Do not download
  those zips, scrape LAION/COCO assets, or package it as a new second
  response-contract candidate unless the task is explicitly SecMI-LDM
  reproducibility maintenance or new independent target/split/query-response
  artifacts appear.
- `ronketer/diffusion-membership-inference` is a public DreamBooth/LoRA
  course-notebook forensics example, not a clean Lane A second asset. It embeds
  a six-image reconstruction-MSE demonstration, but the target LoRA checkpoint
  and forensics images live under private Colab/GDrive paths. Do not recreate
  the DreamBooth run, scrape report images into a pseudo-split, or treat the
  six scalar MSE values as a DiffAudit score packet unless public target,
  split, and query artifacts appear.
- `Stry233/SAMA` is a diffusion-language-model membership attack codebase, not
  a clean image/latent-image Lane A second asset. It exposes dataset
  preparation, target DLM training, and SAMA/baseline attack code, but no
  released target DLM checkpoint, exact member/nonmember manifest, response
  packet, or score metadata bundle. Do not download gated language models,
  prepare MIMIR/NLP subsets, train DLM targets, or launch SAMA GPU jobs unless
  DiffAudit explicitly opens a text/DLM membership lane or a public target/split
  artifact appears.
- VidLeaks / `wangli-codes/T2V_MIA` is a text-to-video membership code
  snapshot, not a clean image/latent-image Lane A second asset. The Zenodo
  archive has code and ROC plot images, but the live GitHub repo is unavailable
  and no target T2V weights, exact member/nonmember video manifests, generated
  videos, feature CSVs, or score packets are released. Do not download
  WebVid-10M, MiraData, Panda-70M, AnimateDiff/InstructVideo/Mira weights,
  generated videos, Gemini captions, or VBench outputs unless DiffAudit
  explicitly opens a text-to-video membership lane or public target/split/score
  artifacts appear.
- GGDM / `Inference Attacks Against Graph Generative Diffusion Models` is a
  graph-diffusion cross-modal related-method watch item, not a clean
  image/latent-image Lane A second asset. Zenodo `17946102` publishes a small
  code archive, but no fixed graph diffusion target checkpoint, exact
  member/nonmember graph manifest, generated graph cache, score/ROC artifact, or
  metrics packet is released, and the public MIA README withholds the Anonymous
  Walk Embeddings module. Do not request AWE code, download graph datasets,
  train EDP-GNN/GDSS/DiGress targets, regenerate graph sample caches, add graph
  Platform rows, or change Runtime schemas unless DiffAudit explicitly opens a
  graph generative diffusion membership lane or public target/split/score
  artifacts appear.
- StyleMI is a 2025 IEEE Access style-mimicry / fine-tuned diffusion
  membership-relevant paper-only watch item. The public gate found DOI metadata
  but no public code repository, target LoRA/checkpoint, exact artist/image
  member/nonmember manifests, generated images, image-processing feature
  packets, or score files. Do not train style LoRAs, scrape artist images, or
  invent style/member splits unless public-safe target/split/response artifacts
  appear.
- Official CDI / `sprintml/copyrighted_data_identification` is code-public and
  scientifically relevant as a dataset-inference pivot, but it is not an
  automatic execution target. The public tree has no ready small score packet,
  and the intended setup requires Google Drive model checkpoints, ImageNet,
  MS-COCO 2014, COCO text embeddings, and submodule payloads. Do not download
  these assets or release GPU unless DiffAudit explicitly opens a
  dataset-inference lane with frozen checkpoint hashes, bounded member/nonmember
  ID manifests, `P` size, p-value/low-FPR metric, and a consumer-boundary note
  separating dataset-level evidence from per-sample membership rows.
- Zenodo `10.5281/zenodo.14928092` is the admitted-family white-box GSA
  artifact archive, not a new Lane A second asset. Do not download the `6.7 GB`
  `DDPM.zip`, rerun GSA GPU, expand GSA loss-score/gradient ablations, or
  package it as a black-box/conditional response-contract candidate unless a
  separate reproducibility-maintenance task explicitly reopens admitted GSA
  provenance.
- ReDiffuse is closed as hold / split-manifest-only. The official OpenReview
  supplement now gives DDPM CIFAR10/CIFAR100/STL10/Tiny-IN train/eval index
  manifests, but no target checkpoint, generated response/feature cache, score
  packet, ROC CSV, or metric artifact. Do not train DDPM/DiT/Stable Diffusion
  targets or rerun same-family attack scripts unless exact checkpoints or score
  packets appear for those manifests.
- `YuxinWenRick/diffusion_memorization` is closed as memorization semantic-shift
  watch. It has a real `500`-row `sdv1_500_memorized.jsonl` prompt manifest, but
  the ground-truth image package is `2.60G`, `CompVis/stable-diffusion-v1-4` is
  not locally cached, and the repo does not ship member/nonmember MIA splits,
  generated response/noise-track packets, score JSON, ROC CSVs, or low-FPR MIA
  metrics. Do not download the GDrive assets or run `detect_mem.py` as a
  membership-inference substitute.
- No GPU task should start from documentation or governance cleanup alone.
- Only one GPU task may run at a time; every GPU task needs a frozen command,
  metric contract, stop condition, and evidence-note target.
- CPU-first means "cheaply prove the contract before spending GPU", not
  CPU-only or GPU avoidance. When a real asset, clear membership semantics,
  fixed query split, metric contract, and stop condition exist, prefer a
  bounded GPU packet over more documentation, validators, or environment
  excuses. A local RTX 4070 sitting idle while the agent writes more prose is a
  research failure, not prudence.
- Before declaring GPU blocked, probe the actual CUDA-capable environments,
  especially `conda run -n diffaudit-research python -X utf8 -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"`.
  Do not infer GPU unavailability from the default PATH Python alone.
- Hugging Face CLI is available in the `diffaudit-research` environment and
  should be treated as the normal asset-acquisition path when a model card,
  gated repo, or checkpoint needs verification. Do not write tokens into docs
  or scripts; if auth is uncertain, check `hf auth whoami` inside the research
  environment before claiming that an asset is inaccessible.
- No history rewrite or force-push without a separate approved audit.

## Research Rules

- Paper reproduction is a starting point, not the full project.
- Every experiment needs a hypothesis, data plan, expected result, and conclusion.
- Experiments must be hypothesis- and decision-value driven. Do not run
  experiments just to complete a narrative, fill a table, or make an ablation
  set look comprehensive; each run must answer a clear hypothesis or support a
  concrete decision.
- Stop low-marginal-information directions early. If a planned run is
  predictably unlikely to improve performance, change the directional decision,
  or unlock a better next step, especially when it only repeats an already
  established no-effect or infeasible verdict, record the reason and do not
  run an exhaustive validation.
- Report `AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR` for promoted attack or
  defense results when applicable.
- DDPM/CIFAR10 results cannot be generalized to conditional-diffusion or
  commercial models without separate evidence.
- Candidate results must stay labeled as candidate-only until promoted through
  an evidence note and roadmap decision. Smoke tests are not benchmark results.
- Long autonomous runs must follow:
  `review -> select -> preflight -> run -> verdict -> docs -> next`.

### 运行实验原则：决策价值导向实验

1. 实验应以假设和决策价值为导向，而不是为了补齐口径、填满表格、让 ablation 看起来完整。实验必须回答一个明确假设，或支持一个真实路线决策。
2. 不在低边际信息增益的方向上穷举。当可以预见某组实验对性能提升、方向判断或后续改进都没有明显贡献，尤其只是重复确认“不可行 / 无效果”时，应立即停止，不做穷举式验证。

这条优先于“补实验完整性”的冲动。如果一个方向已经明显效果很差，不允许为了把消融表跑满而继续扩大条件矩阵；应记录最短有用结论，然后切换到更高价值问题。

## Research Taste Guard

Every cycle must start with a blunt self-check before adding code, validators,
docs, or experiments:

1. Am I discovering a new signal, testing portability, or changing a decision?
2. Or am I just adding another tool, artifact, validator, or long note around a
   direction we already know is blocked, weak, or candidate-only?
3. Would a good scientist stop here and switch direction?
4. Is this “差生文具多”: more stationery, more process, more scaffolding, but
   no real model insight?

If the answer suggests tool-making or defensive writing rather than research,
stop and reselection is required. Do not create another CLI/validator/doc set
unless at least one is true:

- It gates a high-value experiment that is actually likely to run.
- It protects an admitted result that Platform/Runtime already consumes.
- It records a result that changes the project decision.
- It is the smallest way to prevent a known serious mistake.

Default behavior after a blocked or candidate-only verdict:

- Write the shortest useful conclusion.
- Do not keep polishing the dead end.
- Do not run another same-contract repeat unless it can change a decision.
- Move to a stronger question, preferably second asset / second response
  contract / second model scenario.

Current strategic correction:

- ReDiffuse target training/checkpoint-portability repeats, I-B target-risk
  remap training, I-B GSA-only preflight expansion without PIA/contract
  approval, I-C translated replay,
  diagonal-Fisher repeats, GSA loss-score LR repeats, and mid-frequency
  same-contract repeats are not default next steps.
- The next high-value Research direction is a real second-asset or
  second-response-contract package, then simple, direction-setting tests before
  any complex fusion or new framework.

## Workspace Structure

Current research state lives in:

- `workspaces/black-box/`
- `workspaces/gray-box/`
- `workspaces/white-box/`
- `workspaces/implementation/`
- `workspaces/intake/`
- `workspaces/runtime/`

Historical notes are in `legacy/workspaces/`. Don't add new dated logs to the
active workspace directories unless they are current summaries.

Use descriptive names like `Cross-box experiment boundary hardening` in active
docs, not run IDs.

## Public Documentation Rules

Public docs are for new contributors and external reviewers. They must not
contain personal machine paths, private operator instructions, raw agent prompts,
deadline pressure, or unverified product claims.

Use:

- `<DIFFAUDIT_ROOT>`
- `<DOWNLOAD_ROOT>`
- environment variables
- repository-relative paths

Run before pushing documentation or governance changes:

```powershell
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
```

## Subagent Policy

Subagents are optional. Use them for bounded side work such as paper scouting,
review, or implementation slices with explicit write scope. Read-only is the
default. The main agent owns roadmap truth and result promotion.
