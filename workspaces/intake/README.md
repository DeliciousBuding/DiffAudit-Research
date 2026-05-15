# Intake Workspace

## Current Status

- Direction: new method evaluation and paper scouting.
- No active intake review.
- Rectified Flow MIA / arXiv `2603.13421` is a paper-source-only mechanism
  watch. It is non-duplicate because it targets Rectified Flow / Flow Matching
  vector fields with `T_naive`, `T_mc`, and complexity-calibrated `T_mc_cal`,
  and reports strong low-FPR gains on CIFAR-10, SVHN, and TinyImageNet. The
  paper source claims splits, checkpoints, training code, and testing code are
  released at `mx-ethan-rao/MIA_Rectified_Flow`, but the live GitHub repository
  is empty and exposes no refs, code, split manifest, checkpoint, score row,
  ROC array, metric JSON, or verifier. No dataset/model/checkpoint/image
  download, implementation from paper, CPU sidecar, GPU work, or admitted
  Platform/Runtime row is released.
- Public metadata asset sweep after the DIFFENCE Zenodo sync found no new
  non-duplicate image/latent-image replay packet. Authenticated HF metadata
  still exposes only known `zsf/COCO_MIA_ori_split1` and `chumengl/copymark`
  surfaces: CLiD's `mia_COCO.zip` remains `403` for authenticated `HEAD` and
  range probes, while CopyMark's `datasets.zip` is large and already covered
  by the official score-artifact gate. GitHub artifact-shaped searches only
  returned already-covered CopyMark, CLiD, or DiffAudit evidence hits. No ZIP,
  image, model, checkpoint, full-repo download, CPU sidecar, GPU work, or
  admitted Platform/Runtime row is released.
- GitHub lightweight diffusion MIA triage checked four direct search hits:
  `acha1934/Black-box-Membership-Inference-Attacks-against-Fine-tuned-Diffusion-Models`,
  `KarinMalka1/Stable-Diffusion-Personalization-Forensics`,
  `abramwit/ECE-CS-782-Research-Project`, and
  `josephho9/score_function_diffusion`. They are lightweight/course-style or
  toy reproductions only. None commits public checkpoint-bound targets, exact
  target member/nonmember manifests, row-bound response packets, score rows,
  ROC arrays, metric JSON, trained attack weights, or a verifier. No
  notebook/image/model/Google Drive payload download, script execution, CPU
  sidecar, GPU work, or admitted Platform/Runtime row is released.
- DEB / `Assessing Membership Inference Privacy Risks in Medical Diffusion
  Models via Discrete Encoding-Based Inference` is a paper-source-only grey-box
  medical diffusion mechanism watch. The MDPI Applied Sciences article reports
  discrete-codebook perturbation / intermediate-trajectory metrics against
  SecMI, PIA, and SimA, but no public code, target checkpoint hashes, immutable
  member/nonmember manifests, intermediate-state packets, score rows, ROC
  arrays, metric JSON, or verifier were found. No MedMNIST/CIFAR/TinyImageNet/
  Stable Diffusion/model/checkpoint/image download, DEB implementation from the
  paper, active CPU sidecar, GPU work, or admitted Platform/Runtime row is
  released.
- CPSample / OpenReview `LIBLIlk5M9` is defense watch-plus only. The ICLR 2025
  supplement provides diffusion/classifier code and four small
  `inference_attacks/*.txt` loss fragments, but no immutable denoiser/classifier
  checkpoint hashes, exact subset-index manifests, row-bound protected and
  unprotected score packets, ROC arrays, metric JSON, retained-utility metrics,
  or ready verifier. No CIFAR-10/CelebA/LSUN/Stable Diffusion/checkpoint/image
  download, `python main.py` execution, active CPU sidecar, GPU work, or
  admitted Platform/Runtime defense row is released.
- DSiRe / LoRA-WiSE dataset-size recovery is a future weight-only privacy lane
  candidate, not a current per-sample MIA asset. `MoSalama98/DSiRe` provides
  official code, and public non-gated HF `MoSalama98/LoRA-WiSE` exposes `7`
  configs, `2,050` LoRA fine-tuned model rows, `101` parquet shards, and
  reported dataset-size recovery `MAE = 0.36` images. The claim is aggregate
  fine-tuning dataset-size recovery from LoRA weights, not member/nonmember
  image inference. No LoRA-WiSE dataset/image/model/tensor download, `dsire.py`
  run, GPU work, active CPU sidecar, or admitted Platform/Runtime row is
  released.
- Hyperparameter-free SecMI /
  `mohammadKazzazi/Membership-Inference-Attack-against-Diffusion-Models` is a
  third-party SecMI-family code/report support surface. The repo provides
  source code, a notebook/report, and claimed CIFAR-100 seed-0 metrics for a
  multi-timestep learned SecMI variant, but it depends on the official SecMI
  clone, official SecMI SharePoint checkpoints, CIFAR downloads, local cache
  generation, and attacker training. It commits no reusable score rows, ROC
  arrays, metric JSON, trained attacker weights, immutable new split manifest,
  or no-training verifier. No CIFAR/SecMI checkpoint download, attacker
  training, GPU work, active CPU sidecar, or admitted Platform/Runtime row is
  released.
- DME / `F-YaNG1/DME` is a complexity-bias diffusion-MIA watch item. The
  official repo currently contains only a README and does not link a paper,
  implementation code, split manifest, target checkpoint, generated sample,
  score row, ROC array, metric JSON, figure artifact, or verifier. No
  dataset/model/checkpoint download, DME implementation, dual-model training,
  CPU sidecar, GPU work, or admitted Platform/Runtime row is released.
- FreMIA / `poetic2/FreMIA` is a frequency-filter diffusion MIA watch item. The
  arXiv source reports strong trained/fine-tuned table metrics and includes
  rendered ROC/score figures, but the official repo is currently a README-only
  stub. No implementation code, immutable member/hold-out split manifest, target
  checkpoint, generated sample, score row, machine-readable ROC array, metric
  JSON, or verifier is public. No dataset/model/checkpoint download, filter
  implementation, attack execution, GPU work, or admitted Platform/Runtime row
  is released.
- CopyMark / `caradryanl/CopyMark` is official Research-side score-artifact
  support evidence. The public repo commits member/nonmember image logs,
  aggregate ROC/threshold JSONs, selected PIA/PFAMI/SecMI all-step score
  tensors, GSA feature/XGBoost files, and LAION-RiDAR/mixing results. It still
  lacks checkpoint hashes, a compact row-ID-bound score manifest, small
  immutable data/checkpoint packet, and ready verifier output, so no HF dataset
  zip, image payload, model folder, full repo clone, script execution, GPU
  work, or admitted Platform/Runtime row is released.
- VAE2Diffusion / `mx-ethan-rao/VAE2Diffusion` is a code-public latent-space
  MIA watch-plus item. The paper/source claims public splits and checkpoints,
  and the repo exposes decoder-geometry / latent-dimension filtering code for
  LDM membership inference, but the README split/checkpoint link is empty,
  GitHub releases are absent, the recursive tree contains no split, checkpoint,
  score, ROC, metric, response, or verifier artifacts, and scripts depend on
  author-local paths plus from-scratch training/fine-tuning/cache generation.
  No dataset/model/checkpoint/cache download, SimA/PFAMI/PIA execution, GPU
  work, or admitted row is released.
- DualMD / DistillMD / OpenReview `DDMD` is defense watch-plus only. The
  public supplement exposes code, DDPM split-index files, and FID stats, but
  the embedded GitHub origin is not public, and no frozen checkpoints,
  defended/undefended score rows, ROC arrays, metric JSON, generated response
  packet, or ready verifier are released. No SharePoint Pokemon payload,
  Stable Diffusion weights, CIFAR/STL/Tiny-ImageNet datasets, training,
  attack-script run, GPU work, or admitted defense row is released.
- DIFFENCE / `SPIN-UMass/Diffence` is classifier-defense watch-plus only. The
  public repo and Zenodo `10.5281/zenodo.13706131` snapshot expose code,
  configs, and small split-index files, but the protected target is an image
  classifier and diffusion is an input-side purification/pre-inference defense
  component. The release still requires Google Drive classifier/diffusion
  checkpoints and local result generation, and it commits no
  defended/undefended logits, score rows, ROC arrays, metric JSON, or ready
  verifier. No dataset/model download, classifier training, diffusion training,
  MIA script run, or GPU work is released.
- StablePrivateLoRA / `WilliamLUO0/StablePrivateLoRA` is a defense watch-plus
  candidate because it exposes MP-LoRA/SMP-LoRA code and public dataset split
  payloads. It still is not executable in the current cycle: scripts expect a
  local SD-v1.5 base model, train LoRA variants for `400` epochs, and the repo
  does not commit trained LoRA/checkpoints, raw attack scores, ROC CSVs, metric
  JSON, generated responses, or a ready verifier command. No dataset/model
  download or GPU work is released.
- CLiD / `zhaisf/CLiD` has a real official score packet in public GitHub
  `inter_output/*` files. The CPU replay is strong (`AUC = 0.961277`,
  `TPR@1%FPR = 0.675470`, `ASR = 0.891957`) and materially better than PIA,
  SecMI, and PFAMI on the same packet, but it remains prompt-conditioned
  candidate evidence. The public tree and HF metadata do not bind score rows to
  immutable COCO image identities, and authenticated `mia_COCO.zip` HEAD/Range
  access returned `403`. No `mia_COCO.zip`, `COCO_MIA_ori_split1`, SD weights,
  target/shadow checkpoints, generated images, GPU jobs, XGBoost sweeps,
  prompt-shuffle matrices, or Platform/Runtime admitted rows are released.
- FMIA / `Unveiling the Impact of Frequency Components on Membership Inference
  Attacks for Diffusion Models` is a watch-plus mechanism candidate. Its
  OpenReview supplement ships frequency-filter DDIM/Stable Diffusion attack code
  and exact CIFAR10/CIFAR100/STL10/TINY-IN split manifests, but no trained
  checkpoints, Stable Diffusion weights, generated samples, score arrays, ROC
  CSVs, metric JSON, or ready verifier packet. No dataset/model download or GPU
  work is released.
- DCR / `somepago/DCR` is a copying/memorization semantic-shift watch-plus item.
  The official repo publishes diffusion replication/copying code,
  retrieval/similarity scripts, metric helpers, and a committed LAION caption
  manifest, but the README LAION-10k Drive split link returns HTTP `404`, and
  no immutable member/nonmember MIA split, target checkpoint, generated response
  package, score rows, ROC arrays, metric JSON, or ready verifier are public. No
  LAION/Drive/model download, fine-tuning, inference, retrieval, or GPU work is
  released.
- FCRE / `Frequency-Calibrated Reconstruction Error` is a medical-image
  frequency MIA paper-source-only watch item. arXiv `2506.14919` reports
  FeTS 2022, ChestX-ray8, and CIFAR-10 metrics, but no official code, immutable
  split manifests, target checkpoints, generated reconstruction packets, score
  rows, ROC arrays, metric JSON, or ready verifier are public. No
  FeTS/ChestX-ray8/CIFAR download, target training, DDIM reconstruction,
  frequency sweep, or GPU work is released.
- SimA / `Score-based Membership Inference on Diffusion Models` is a
  watch-plus mechanism candidate. The official `mx-ethan-rao/SimA` repo ships
  score-based MIA code and scripts across DDPM, Guided Diffusion, LDM, SD1.4,
  and SD1.5 examples, but the README split/checkpoint links are empty or
  require emailing authors, and the public tree has no non-vendor split
  manifests, checkpoints, score arrays, ROC/metric artifacts, or ready verifier
  packet. No dataset/model download or GPU work is released.
- GenAI Confessions / `hanyfarid/MembershipInference` is a black-box
  related-method watch item. It has public raw member/nonmember-style image
  inputs for STROLL, Carlini, and Midjourney, including public/non-gated HF
  `faridlab/stroll` metadata and a Zenodo `133,599,324` byte data ZIP, but it
  does not ship the STROLL fine-tuned SD2.1 checkpoint, generated image-to-image
  response grids, DreamSim distance vectors, ROC/metric artifacts, Midjourney
  query logs, or a ready verifier. No dataset download or GPU work is released.
- DurMI / `DurMI: Duration Loss as a Membership Signal in TTS Models` is a
  TTS/audio cross-modal watch-plus item. The OpenReview supplement ships
  GradTTS, WaveGrad2, and VoiceFlow attack code plus an exact GradTTS LJSpeech
  `5,977 / 5,977` member/nonmember split; Zenodo publishes open metadata for
  the audio datasets and checkpoints. It is not an execution target in the
  current image/latent-image cycle because the public release does not ship
  ready duration-loss score arrays, ROC arrays, metric JSON, generated result
  graphs, or a TTS/audio consumer-boundary decision. No dataset/checkpoint
  download or GPU work is released.
- LSA-Probe / `Membership Inference Attack Against Music Diffusion Models via
  Generative Manifold Perturbation` is a music/audio cross-modal watch-plus
  item. The paper and demo are public, but the project repo currently exposes
  only `README.md`; the GitHub Pages `data/*.json` score-like arrays are mock
  demo data generated by `generate_demo_data.py`, not checkpoint-bound
  adversarial-cost scores or ROC artifacts. No MAESTRO/FMA/MusicLDM/DiffWave
  download, implementation-from-paper work, or GPU run is released.
- FERMI / `FERMI: Exploiting Relations for Membership Inference Against
  Tabular Diffusion Models` is a multi-relational tabular watch item. The
  2026-05-12 arXiv source reports strong TabDDPM/TabDiff/TabSyn relational MIA
  metrics, but the public surface has no code tree, target/split manifests,
  generated synthetic tables, feature/score rows, ROC arrays, metric JSON, or
  replay command. No tabular dataset download, model training, implementation
  work, or GPU work is released.
- `On Privacy Leakage in Tabular Diffusion Models: Influential Factors,
  Attacker Knowledge, and Metrics` is a single-table tabular diffusion
  watch-plus item. The 2026-05-07 arXiv source is paper/figures only, while the
  official `VectorInstitute/midst-toolkit` code exposes ClavaDDPM training and
  MIDST attack implementations plus small integration-test TabDDPM fixtures.
  The public surface still has no paper-bound Berka/Diabetes target
  checkpoints, immutable split manifests, generated synthetic tables, score
  rows, ROC arrays, metric JSON, or ready verifier. No Berka/Diabetes/MIDST
  resource download, attack execution, model training, or GPU work is released.
- MT-MIA / `Finding Connections: Membership Inference Attacks for the
  Multi-Table Synthetic Data Setting` is a relational tabular diffusion
  score-packet support item. The official `joshward96/MT-MIA` repository
  publishes member/nonmember/reference split folders, pre-generated ClavaDDPM
  and RelDiff synthetic outputs, and `18` official MT-MIA `mtmia_seed_*.jsonl`
  score/metric packets. It is not an image/latent-image execution target and
  does not change Platform/Runtime admitted rows. No raw figshare data,
  synthetic CSV payload, full repo, model/training asset, GPU work, or active
  CPU sidecar is released.
- Shake-to-Leak / `VITA-Group/Shake-to-Leak` is a code-public
  generative-privacy watch-plus item. The official repository publishes
  fine-tuning-amplified leakage code, a vendored SecMI/diffusers tree,
  fine-tuning scripts, SecMI scripts, data extraction code, and a `40`-domain
  celebrity/person list. It does not publish frozen target checkpoints,
  immutable member/nonmember manifests, generated synthetic private sets,
  generated attack responses, score arrays, ROC arrays, metric JSON, or a
  ready verifier. No Stable Diffusion weight download, LAION/person image
  download, synthetic-private-set generation, fine-tuning, SecMI run, data
  extraction, GPU work, or active CPU sidecar is released.
- FSECLab MIA-Diffusion / `fseclab-osaka/mia-diffusion` is a direct
  diffusion-MIA code-public watch-plus item. The official repository publishes
  DDIM/DCGAN training, sampling, white-box attack, black-box attack,
  dataset-loader, ROC-evaluator code, and two FID-stat `.npz` files, but no
  frozen target checkpoint, immutable member/nonmember split manifest,
  generated sample packet, score array, ROC array, metric JSON, or ready
  verifier output. No CIFAR-10/CelebA download, checkpoint/model acquisition,
  full repo clone, training, sampling, attack-script run, GPU work, or active
  CPU sidecar is released.
- MIDM / `HailongHuPri/MIDM` is a stronger image-diffusion watch-plus
  candidate than generic paper-only items because it exposes FFHQ DDPM
  loss/likelihood attack code, `ffhq_1000_idx.npy` member-index semantics,
  `1000/1000` labels in `Example.ipynb`, and fixed-FPR TPR metric code. It is
  still not executable in the current cycle: the repo does not commit fixed
  member/nonmember manifests, HDF5 score packets, ROC/metric artifacts, or
  notebook outputs, and the advertised Google Drive DDPM checkpoint returned
  HTTP `401` in this environment. No FFHQ/model download or GPU work is
  released.
- Current long-horizon intake posture: LAION-mi is a Lane A metadata-only watch
  candidate. It has a named `Stable Diffusion-v1.4` target and public
  member/nonmember metadata splits, but the fixed `25/25` URL availability
  probe recovered only `11 / 25` member images and `16 / 25` nonmember images.
  No response generation or GPU work is released for LAION-mi.
- Zenodo `10.5281/zenodo.13371475` is a paper-and-code-backed archive watch
  candidate: target/shadow LoRA checkpoint and dataset payload names are
  visible from the ZIP central directory, and public paper/code references
  confirm a reconstruction-based attack workflow. The exact target
  member/nonmember split manifest is still missing. Do not download the full
  `736 MB` archive until a public manifest or repository file resolves that
  split-semantics gate.
- `Noise as a Probe` is a mechanism-relevant watch candidate, not a runnable
  asset. The arXiv source defines a semantic-initial-noise reconstruction
  attack on Stable Diffusion-v1-4 fine-tuning and reports Pokémon, T-to-I,
  MS-COCO, and Flickr member/hold-out counts. It does not provide public code,
  per-sample split manifests, released checkpoints, or query/response packages.
- `MIAGM` / `Generated Distributions Are All You Need` is a code-reference-only
  watch candidate. The public repository is useful for generated-distribution
  membership context, but it does not expose exact target checkpoints,
  generated-distribution payloads, or per-sample member/nonmember split
  manifests.
- `Membership Inference Attacks on Diffusion Models via Quantile Regression`
  is a mechanism-reference watch candidate. It gives a distinct
  sample-conditioned reconstruction-loss quantile-regression attack and cites
  the SecMI/Duan et al. DDPM codebase, but no paper-specific public code,
  per-sample member/public/holdout split manifest, exact target artifact
  bundle, or ready t-error packet was found.
- `MIA_SD` is a face-LDM related code/result reference, not a runnable asset:
  experiment images, target checkpoint, exact member/nonmember split manifest,
  and reusable query/response package are not released.
- Zenodo `10.5281/zenodo.14928092` is admitted-family white-box GSA provenance,
  not a new Lane A second asset. It does not release a fresh download/GPU task
  for asset acquisition.
- `MoFit` / caption-free model-fitted embeddings is mechanism-relevant, but the
  public repository still marks code instructions as `TBW` and no released
  target checkpoint or exact split manifest was found.
- `Cardio-AI/memorization-ldm` is a non-duplicate medical LDM memorization
  watch candidate. The public repo and Zenodo release provide code and a small
  software snapshot, but synthesized samples are request-gated and no target
  LDM checkpoint, exact per-sample member/nonmember manifest, or generated
  response package is published. No download or GPU work is released.
- `jinhaoduan/SecMI-LDM` is a SecMI support-family Diffusers fork, not a clean
  Lane A second asset. Its default-branch README provides SharePoint download
  links for datasets and the Pokémon fine-tuned SD checkpoint, but this remains
  same-author SecMI reproduction/support material rather than an independent
  second asset or black-box response contract. No download or GPU work is
  released.
- `ronketer/diffusion-membership-inference` is a public DreamBooth/LoRA
  course-notebook forensics example, not a runnable asset. It reports a
  reconstruction-MSE threshold and embeds six MSE scores, but the target LoRA
  checkpoint and forensics query images live under private Colab/GDrive paths.
  No download or GPU work is released.
- `Stry233/SAMA` is a diffusion-language-model membership codebase, not a
  current image/latent-image Lane A asset. The repo provides dataset
  preparation, DLM training, and SAMA/baseline attack code, but no released
  target DLM checkpoint, exact member/nonmember manifest, response packet, or
  score metadata bundle. No download or GPU work is released.
- VidLeaks / `wangli-codes/T2V_MIA` is a text-to-video membership code
  snapshot, not a current runnable asset. Zenodo publishes a small software
  archive and ROC images, while the live GitHub repo is unavailable and the
  archive lacks target T2V weights, exact member/nonmember video manifests,
  generated videos, feature CSVs, and score packets. No model/video download or
  GPU work is released.
- GGDM / `Inference Attacks Against Graph Generative Diffusion Models` is a
  graph-diffusion cross-modal related-method watch item. Zenodo `17946102`
  publishes a small code archive, but it lacks a fixed graph diffusion target
  checkpoint, exact member/nonmember graph manifests, generated graph caches,
  score/ROC artifacts, and the public `MIA/README.md` says the Anonymous Walk
  Embeddings module is withheld. No graph dataset download, target training,
  AWE request, or GPU work is released.
- StyleMI is a style-mimicry / fine-tuned diffusion membership-relevant
  paper-only watch item. Public DOI metadata confirms the 2025 IEEE Access
  paper, but no public code repository, target LoRA/checkpoint, exact
  artist/image member/nonmember manifests, generated images, feature packets,
  or score files were found. No artist-image scraping, style-LoRA training,
  download, or GPU work is released.

Archived reviews are in
[../../legacy/workspaces/intake/2026-04/](../../legacy/workspaces/intake/2026-04/).

## Next Steps

New intake proposals should include:

- target model identity: checkpoint, endpoint, or reproducible training recipe
- exact member evidence: per-sample target training or fine-tuning membership
- exact nonmember evidence: held-out samples that are not target training data
- query/response contract: existing responses or deterministic generation plan
- mechanism delta: why this is not another CommonCanvas, Beans, MIDST, MNIST,
  Fashion-MNIST, final-layer gradient, or midfreq variant
- stop gate: close immediately if the first bounded packet has `AUC < 0.60` or
  near-zero `TPR@1%FPR`

If a proposal cannot satisfy these fields, keep it as watch-only and do not
write a new scope/audit chain.

Current LAION-mi follow-up:

- Keep LAION-mi as metadata-only watch.
- Reopen only if a public-safe cached image subset appears, or if a later
  deterministic URL scan policy is frozen before scoring.
- Do not build response-generation tooling around live LAION-mi URLs.

Current MIDM follow-up:

- Keep it as image-diffusion watch-plus, not an execution target.
- Reopen only if public artifacts fix exact FFHQ member/nonmember identities,
  checkpoint size/hash/training binding, and ready loss/likelihood scores or a
  bounded command that does not require acquiring FFHQ from scratch.
- Do not download FFHQ thumbnails, request or scrape checkpoint access, train
  MIDM DDPM, run loss/likelihood scoring from scratch, or promote MIDM into
  Platform/Runtime rows inside the current roadmap cycle.

Current StablePrivateLoRA follow-up:

- Keep it as defense watch-plus, not an execution target.
- Reopen only if public artifacts bind MP-LoRA/SMP-LoRA/LoRA checkpoints to
  fixed splits and include raw attack scores, ROC/metric artifacts, or a
  verifier command that does not require training SD-v1.5 LoRAs from scratch.
- Do not clone or download the large dataset image payloads, SD-v1.5 base
  model, LoRA checkpoints, generated images, or logs; do not train
  MP-LoRA/SMP-LoRA, OCR table PNGs into admitted metrics, or promote it into
  Platform/Runtime defense rows inside the current roadmap cycle.

Current DIFFENCE follow-up:

- Keep it as classifier-defense related-method watch-plus, not a DiffAudit
  diffusion-generator membership row. The immutable Zenodo code snapshot is
  useful provenance, not a result packet.
- Reopen only if public checkpoint-bound defended/undefended logits, score
  rows, ROC arrays, metric JSON, or a bounded verifier appear, and a
  consumer-boundary decision explicitly admits classifier-defense evidence.
- Do not download Google Drive diffusion/classifier checkpoints, CIFAR/SVHN
  datasets, train classifiers or diffusion models, generate DIFFENCE
  reconstructions, run MIA scripts, or promote it into Platform/Runtime rows
  inside the current roadmap cycle.

Current DualMD / DistillMD follow-up:

- Keep it as disjoint-split defense watch-plus, not an execution target.
- Reopen only if public artifacts bind DualMD/DistillMD DDPM or LDM
  checkpoints to fixed member/nonmember manifests and include raw defended and
  undefended scores, ROC arrays, metric JSON, generated response packets, or a
  bounded verifier that avoids retraining and dataset acquisition from scratch.
- Do not download the SharePoint Pokemon payload, Stable Diffusion weights,
  CIFAR/CIFAR100/STL10/Tiny-ImageNet datasets, run DDPM/LDM training,
  distillation, SecMIA/PIA, black-box attack scripts, or promote
  disjoint-training defense rows inside the current roadmap cycle.

Current CLiD follow-up:

- Keep it as strong official CPU replay evidence, not a Platform/Runtime
  admitted row.
- Reopen only if authors publish a row-level manifest, or if HF gated access
  enables metadata-only ZIP central-directory/manifest inspection without image
  payloads, plus a prompt-neutral or image-identity-safe protocol that preserves
  the official strict-tail signal.
- Do not download `mia_COCO.zip`, `COCO_MIA_ori_split1`, SD weights,
  target/shadow checkpoints, or generated images; do not run CLiD GPU jobs,
  XGBoost sweeps, or prompt-shuffle matrices inside the current roadmap cycle.

Current FMIA follow-up:

- Keep it as frequency-component mechanism watch-plus, not an execution target.
- Reopen only if public trained checkpoints or ready score arrays/ROC/metric
  artifacts appear, or if a bounded command can use a locally admitted
  checkpoint without training a new target from scratch.
- Do not download datasets, train FMIA DDIM targets, fine-tune Stable Diffusion,
  or run filter-threshold/filter-scale/timestep matrices inside the current
  roadmap cycle.

Current SimA follow-up:

- Keep it as score-based mechanism watch-plus, not an execution target.
- Reopen only if public split manifests, checkpoint size/hash/training binding,
  and ready score arrays/ROC/metric artifacts appear, or if a bounded verifier
  can read public artifacts without training a target from scratch.
- Do not download large datasets, train DDPM targets, fine-tune SD1.4, request
  checkpoints by email, run SimA GPU jobs, or expand Fashion-MNIST SimA
  timestep/norm/seed/scheduler matrices inside the current roadmap cycle.

Current GenAI Confessions follow-up:

- Keep it as black-box image-to-image boundary watch, not an execution target.
- Reopen only if a public STROLL fine-tuned SD2.1 checkpoint, generated
  response grid, DreamSim distance vector packet, ROC/metric artifact, or ready
  verifier appears, plus a consumer-boundary decision for image-to-image service
  membership.
- Do not download the Zenodo ZIP or HF image payload, fine-tune STROLL SD2.1,
  query Midjourney manually, or rebuild DreamSim/logistic-regression replay
  from scratch inside the current roadmap cycle.

Current DurMI follow-up:

- Keep it as TTS/audio cross-modal watch-plus, not an image/latent-image
  execution target.
- Reopen only if DiffAudit explicitly opens a TTS/audio membership lane with a
  consumer-boundary decision, or if the authors publish ready duration-loss
  score arrays, ROC arrays, metric JSON, or generated result graphs that can be
  replayed without acquiring multi-GB audio datasets and checkpoints.
- Do not download the Zenodo audio datasets/checkpoints, fetch Google Drive
  TextGrid files, run GradTTS/WaveGrad2/VoiceFlow attacks, train TTS targets,
  or launch DurMI GPU jobs inside the current roadmap cycle.

Current LSA-Probe follow-up:

- Keep it as music/audio cross-modal watch-plus, not an image/latent-image
  execution target.
- Reopen only if the authors publish implementation plus public-safe target
  model identities, exact member/nonmember manifests, and real adversarial-cost
  score/ROC/metric artifacts, or if DiffAudit explicitly opens a music/audio
  membership lane with a consumer-boundary decision.
- Do not download MAESTRO, FMA-Large, DiffWave, MusicLDM, audio clips, or
  checkpoints; do not treat GitHub Pages `data/*.json` as experiment evidence;
  and do not implement LSA-Probe from the TeX or demo inside the current
  roadmap cycle.

Current FERMI follow-up:

- Keep it as multi-relational tabular watch, not a MIDST/tabular execution
  target.
- Reopen only if public code plus target/split manifests, generated synthetic
  tables, feature/score packets, ROC arrays, metric JSON, or a replay command
  appears, or if DiffAudit explicitly opens a multi-relational tabular
  membership lane with a consumer-boundary decision.
- Do not implement FERMI from scratch, download California/Instacart/Berka
  relational datasets, train TabDDPM/TabDiff/TabSyn or surrogate models, or
  build a FERMI mapper/attack MLP inside the current roadmap cycle.

Current MT-MIA follow-up:

- Keep it as relational-tabular score-packet support evidence, not a current
  image/latent-image execution target.
- Reopen only if DiffAudit explicitly opens a relational tabular
  synthetic-data membership lane, if authors publish row-ID-bound verifier
  artifacts, or if paperization needs clearly labeled cross-domain support.
- Do not download raw figshare datasets, synthetic CSV payloads,
  ClavaDDPM/RelDiff training assets, or the full repository; do not regenerate
  RelDiff or promote MT-MIA into Platform/Runtime rows inside the current
  roadmap cycle.

Current Shake-to-Leak follow-up:

- Keep it as fine-tuning-amplified generative privacy watch-plus, not an
  execution target.
- Reopen only if public artifacts bind SD-v1-1 fine-tuned checkpoints to fixed
  member/nonmember identities and include score arrays, ROC/metric artifacts,
  generated attack responses, or a bounded verifier that does not require
  training and extraction from scratch.
- Do not download Stable Diffusion weights, LAION/person image folders,
  generated synthetic private sets, checkpoints, or full repo payloads; do not
  run `sp_gen.py`, LoRA/DB/End2End fine-tuning, SecMI scripts, or data
  extraction inside the current roadmap cycle.

Current Zenodo fine-tuned diffusion follow-up:

- Keep it as archive-structured watch.
- Reopen only with a public manifest or repository file proving base model,
  target member/nonmember semantics, and query/response or scoring contract.
- Do not download the full archive or run LoRA scoring before that proof exists.
- Do not write another Zenodo audit/scope note unless new external evidence
  supplies the missing split manifest.

Current Noise as a Probe follow-up:

- Keep it as a Lane B mechanism hook and Lane A watch candidate.
- Reopen only if public code plus exact split/checkpoint artifacts appear.
- Do not implement DDIM inversion or fine-tune SD-v1-4 from scratch just to
  reproduce the paper.

Current MIAGM follow-up:

- Keep it as related-method watch.
- Reopen only if target checkpoints or generated-distribution payloads plus
  exact split semantics are released.
- Do not train DDPM/DDIM/FastDPM or regenerate distributions from scratch.

Current Quantile Regression follow-up:

- Keep it as Lane B mechanism reference and Lane A watch.
- Reopen only if paper-specific code or artifacts expose target checkpoints or
  deterministic target recreation plus exact member/public/holdout splits.
- Do not train STL10/Tiny-ImageNet DDPMs, reconstruct SecMI splits, or build a
  quantile-regression implementation from scratch before those artifacts exist.

Current hyperparameter-free SecMI follow-up:

- Keep it as a third-party SecMI-family anti-duplication gate only.
- Reopen only if public artifacts expose row-ID-bound baseline and
  hyperparameter-free SecMI score rows, ROC arrays or metric JSON, trained
  attacker weights, or a no-training verifier.
- Do not clone the repo, download CIFAR/SecMI SharePoint checkpoints, run
  `python run.py`, execute the notebook, train attackers, or promote it into
  Platform/Runtime rows inside the current roadmap cycle.

Current DSiRe / LoRA-WiSE follow-up:

- Keep it as a Research-only future weight-only privacy lane candidate.
- Reopen only if DiffAudit explicitly adds a `weight-only LoRA dataset-size
  recovery` lane with MAE/MAPE/accuracy as primary metrics and a
  consumer-boundary note separating aggregate dataset-size recovery from
  per-sample membership inference.
- Do not download the full LoRA-WiSE dataset, image folders, Stable Diffusion
  weights, LoRA tensor shards, run `python dsire.py`, launch FAISS/SVD sweeps,
  or promote it into Platform/Runtime rows inside the current image/latent-image
  roadmap cycle.

Current CPSample follow-up:

- Keep it as a Research-only defense watch-plus item, not an execution target.
- Reopen only if public artifacts bind denoiser/classifier checkpoints to exact
  train/test/subset identities and include protected plus unprotected row-bound
  score packets, ROC/metric JSON, retained-utility metrics, and a ready
  verifier.
- Do not download CIFAR-10, CelebA, LSUN, Stable Diffusion weights,
  denoiser/classifier checkpoints, generated images, or missing Google Drive
  placeholders; do not run `python main.py`, train classifiers, fine-tune
  denoisers, generate samples, run `--inference_attack`, launch CPU/GPU
  sidecars, or promote it into Platform/Runtime rows inside the current roadmap
  cycle.

Current MIA_SD follow-up:

- Keep it as related-method watch only.
- Reopen only if authors publish a target checkpoint plus exact split manifest
  or a public-safe query/response packet.
- Do not scrape DTU/AAU/LFW images, reconstruct private folders, or train SD1.5
  for 400 epochs from this repo.

Current White-box GSA Zenodo follow-up:

- Treat it as admitted-family provenance for existing GSA rows.
- Reopen only for bounded reproducibility maintenance of admitted GSA.
- Do not download `DDPM.zip`, replay GSA GPU, or promote it as a new second
  asset.

Current MoFit follow-up:

- Keep it as Lane B gray-box mechanism watch.
- Reopen only if upstream publishes runnable code/configs plus exact target
  checkpoint or deterministic recreation and per-sample split manifests.
- Do not implement surrogate/embedding optimization from scratch or launch
  GPU jobs before those artifacts exist.

Current memorization-LDM follow-up:

- Keep it as Lane A medical-LDM watch only.
- Reopen only if a public-safe artifact exposes a target LDM checkpoint or
  deterministic target recreation, exact member/nonmember manifests, and a
  generated sample or query/response package.
- Do not download medical datasets, request controlled synthesized samples, or
  train/reconstruct the paper pipeline inside the current roadmap cycle.

Current SecMI-LDM follow-up:

- Keep it as related SecMI support-family reference only.
- Reopen only for explicit SecMI-LDM reproducibility maintenance, or if a
  genuinely independent public-safe target/split/query-response artifact
  appears.
- Do not download the SharePoint dataset/checkpoint zips, scrape LAION/COCO
  assets, or package this fork as an independent second asset.

Current R125 DreamBooth forensics follow-up:

- Keep it as related-method watch only.
- Reopen only if the author publishes the LoRA/checkpoint, exact member and
  nonmember manifests, and the query images or generated response package.
- Do not recreate the private Colab/GDrive DreamBooth run, scrape report images
  into a pseudo-split, or treat six embedded notebook MSE values as a score
  packet.

Current SAMA / diffusion-language-model follow-up:

- Keep it as a related-method reference only.
- Reopen only if DiffAudit explicitly adds a text/DLM membership lane, or if
  authors publish a public-safe target DLM checkpoint, exact member/nonmember
  manifests, and reusable attack metadata or deterministic scoring command.
- Do not download gated language models, prepare MIMIR/NLP subsets, train DLM
  targets, or launch SAMA GPU jobs inside the current image-diffusion roadmap
  cycle.

Current VidLeaks / text-to-video follow-up:

- Keep it as a related-method watch item only.
- Reopen only if DiffAudit explicitly adds a text-to-video membership lane, or
  if authors publish a public-safe target T2V checkpoint or endpoint, exact
  per-video member/nonmember manifests, and generated video or feature/score
  packets.
- Do not download WebVid-10M, MiraData, Panda-70M, AnimateDiff/InstructVideo/Mira
  weights, generated videos, Gemini captions, or VBench outputs inside the
  current image-diffusion roadmap cycle.

Current GGDM / graph generative diffusion follow-up:

- Keep it as a graph-diffusion cross-modal watch item only.
- Reopen only if authors publish public-safe target checkpoints or deterministic
  target recreation, exact member/nonmember graph manifests, generated graph
  sample caches, and score/ROC artifacts, or if DiffAudit explicitly opens a
  graph generative diffusion membership lane.
- Do not request the withheld AWE module, download graph datasets, train
  EDP-GNN/GDSS/DiGress targets, regenerate graph sample caches, add graph
  Platform rows, or change Runtime schemas inside the current image/latent-image
  roadmap cycle.

Current StyleMI / style-mimicry follow-up:

- Keep it as a paper-only style-mimicry watch item.
- Reopen only if authors publish a public-safe target checkpoint or
  deterministic style fine-tuning recipe, exact artist/image member and
  nonmember manifests, and generated image, image-processing feature, or score
  packets.
- Do not scrape artist images, train style LoRAs, invent style/member splits,
  or build feature packets from scratch inside the current roadmap cycle.
