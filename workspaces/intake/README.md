# Intake Workspace

## Current Status

- Direction: new method evaluation and paper scouting.
- No active intake review.
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
