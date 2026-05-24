# Workspace Evidence Index

This index separates current track state from archived research history.

## Current Track State

Latest Research update:
[rediffuse-stl10-sima-score-norm-20260525.md](rediffuse-stl10-sima-score-norm-20260525.md)
records a one-pass SimA-style denoiser-output score-norm scorer on the existing
ReDiffuse DDPM/STL-10 `300`-step checkpoint and the same `256 / 256` score split.
It ran without training or downloads, completed in `15.938s` with `0.365 GB`
peak allocated VRAM, and remained random-level (`AUC = 0.5052947998046875`,
`ASR = 0.525390625`, `TPR@1%FPR = 0.03125`,
`TPR@0.1%FPR = 0.01953125`). Decision: `bounded scorer completed / weak
score-norm signal / no GPU expansion`.

Previous Research update:
[rediffuse-stl10-bounded-scout-20260525.md](rediffuse-stl10-bounded-scout-20260525.md)
records the only ReDiffuse DDPM/STL-10 bounded scout released by the preflight.
The run trained a `300`-step official ReDiffuse DDPM tiny target on `1024`
STL-10 member samples, produced a `256 / 256` score packet, and stopped at the
step budget after `92.750s` with `2.430 GB` peak allocated VRAM. Fixed-timestep
denoising-loss is random-level (`AUC = 0.4996337890625`, `ASR = 0.509765625`,
`TPR@1%FPR = 0.01171875`, `TPR@0.1%FPR = 0.0`). Decision: `bounded scout
completed / score packet produced / weak denoising-loss signal / no GPU
expansion`.

Previous Research update:
[rediffuse-stl10-split-and-microtrain-preflight-20260525.md](rediffuse-stl10-split-and-microtrain-preflight-20260525.md)
records the ReDiffuse DDPM/STL-10 split, low-level-statistics, and CUDA
resource preflight. The official `STL10_train_ratio0.5.npz` split is exact and
public (`50k / 50k`), binds to the local STL-10 unlabeled payload, and shows no
obvious low-level image-statistics leakage (`80000` holdout linear-probe
`AUC = 0.4994776215625`). Official ReDiffuse DDPM `UNet` +
`GaussianDiffusionTrainer` calibration ran under the CUDA-capable
`diffaudit-research` conda environment; batch `64` for `10` steps completed
with `4.419 GB` peak allocated VRAM. Decision: `split preflight passed /
resource-feasible scout candidate / no membership metric yet / no admitted row`.

Previous Research update:
[identity-focused-inference-extraction-artifact-gate-20260523.md](identity-focused-inference-extraction-artifact-gate-20260523.md)
records a Lane A/B metadata gate for arXiv `2410.10177` /
`Identity-Focused Inference and Extraction Attacks on Diffusion Models`.
Identity-Focused Inference is identity-level privacy context rather than a
current DiffAudit execution target: the checked public surface exposes arXiv
metadata/source availability, but no official code, LDM / DDPM target
checkpoint identity, immutable LFW / CelebA identity or member/nonmember
manifest, generated response packet, per-row membership / identity score file,
ROC array, metric JSON, extraction-quality artifact, or verifier is public.
Decision: `paper-source-only identity-level inference / extraction watch / no
official code / no score artifacts / no download / no GPU release / no admitted
row`.

Previous Research update:
[rapta-admcd-copying-mitigation-artifact-gate-20260523.md](rapta-admcd-copying-mitigation-artifact-gate-20260523.md)
records a Lane A/B metadata gate for arXiv `2603.13070` /
`Mitigating Memorization in Text-to-Image Diffusion via Region-Aware Prompt
Augmentation and Multimodal Copy Detection`. RAPTA / ADMCD is copying /
memorization mitigation context rather than a current DiffAudit execution
target: the checked public surface exposes arXiv HTML/source availability, but
no official code, checkpoint-bound target identity, immutable copied/non-copied
or member/nonmember row manifest, generated response packet, per-row ADMCD
score file, ROC array, metric JSON, retained-utility artifact, or verifier is
public. Decision: `paper-source-only copying / memorization mitigation watch /
no official code / no score artifacts / no download / no GPU release / no
admitted row`.

Previous Research update:
[guard-surgical-mitigation-artifact-gate-20260523.md](guard-surgical-mitigation-artifact-gate-20260523.md)
records a Lane A/B metadata gate for arXiv `2603.00133` /
`You Don't Need All That Attention: Surgical Memorization Mitigation in
Text-to-Image Diffusion Models`. The official `kairanzhao/GUARD` repository is
code-public, MIT-licensed, and exposes inference, detection, mask-generation,
metric, and vendored `open_clip` code for the `sdv1_500_mem` Stable Diffusion
memorization benchmark. It remains mitigation context rather than a current
DiffAudit execution target: the public release points users to Google Drive
benchmark assets and local Stable Diffusion/reference-model execution, but no
checkpoint-bound target identity, immutable row manifest, generated response
packet, pre/post GUARD score rows, ROC arrays, metric JSON, retained-utility
artifact, or no-training verifier is public. Decision: `official code-public
mitigation watch / no score artifacts / no download / no GPU release / no
admitted row`.

Previous Research update:
[baf-lora-parameter-space-mitigation-gate-20260523.md](baf-lora-parameter-space-mitigation-gate-20260523.md)
records a Lane A/B metadata gate for arXiv `2605.10439` /
`Filtering Memorization from Parameter-Space in Diffusion Models`. This is a
weight-only LoRA memorization-mitigation watch item: the paper proposes
Base-Anchored Filtering (`BAF`), a post-hoc, training-free, data-free method
that decomposes LoRA updates into spectral channels and suppresses weakly
backbone-aligned channels as possible memorization carriers. The public surface
is supplementary-code-claim-only: no official public repository, target
LoRA/checkpoint bundle, training-image manifest, member/nonmember rows,
generated response packet, score file, ROC array, metric JSON, retained-utility
artifact, or verifier is public. Decision: `weight-only LoRA mitigation watch /
supplementary-code claim only / no public score artifacts / no download / no GPU
release / no admitted row`.

Previous Research update:
[broken-memories-artifact-gate-20260523.md](broken-memories-artifact-gate-20260523.md)
records a Lane A metadata gate for arXiv `2605.22050` /
`Broken Memories: Detecting and Mitigating Memorization in Diffusion Models
with Degraded Generations`. This is fresh Stable Diffusion memorization
detection/mitigation evidence with reported SD `1.4` `AUC > 0.999`, `0.0%`
post-mitigation memorization rate, and about `0.01s` overhead. The checked
public surface is paper-source-only: arXiv source `HEAD` reports a
`24,383,310` byte gzip with SHA-256 ETag
`e860fea66b3b44ecaa80f001c8443740443711151958005fe11ae82ec1d70c9d`, but the
source tarball was not downloaded; arXiv metadata plus exact-title and
arXiv-id GitHub searches expose no official Broken Memories repository,
prompt manifest, generated image packet, internal trace, per-row score file,
ROC array, metric JSON, mitigation-decision artifact, or verifier. Decision:
`memorization detection/mitigation semantic-shift watch / paper-source-only /
no official code / no score artifacts / no download / no GPU release / no
admitted row`.

Previous Research update:
[iar-privacy-attacks-artifact-gate-20260523.md](iar-privacy-attacks-artifact-gate-20260523.md)
records a Lane A metadata gate for arXiv `2502.02514` /
`Privacy Attacks on Image AutoRegressive Models`. This is strong
image-generation privacy evidence with official code and reported MIA,
dataset-inference, and extraction claims, but the target family is image
autoregressive generation rather than the current diffusion / latent-image
admitted consumer family. The official `sprintml/privacy_attacks_against_iars`
repository exposes `main.py`, `environment.yaml`, MIA/DI/memorization analysis
scripts, VAR/RAR/MAR configs, and attack implementations. It does not commit
model hashes, immutable ImageNet row manifests, generated sample packets,
per-row MIA scores, ROC arrays, metric JSON, DI CSVs, memorization CSVs, or a
no-training verifier. The README execution path requires upstream model
repositories, ImageNet train/validation, model downloads, and local output
generation. Decision: `image-autoregressive privacy watch-plus / official
code-public / no committed score packet / large ImageNet and model assets
required / no download / no GPU release / no admitted row`.

Previous Research update:
[silent-brush-artarena-artifact-gate-20260523.md](silent-brush-artarena-artifact-gate-20260523.md)
records a Lane A metadata gate for arXiv `2605.17500` /
`The Silent Brush: Evaluating Artistic Style Leakage in AI Art Generation`.
This is text-to-image diffusion-adjacent privacy evidence, but the claim
boundary is style leakage / copyright evaluation rather than the current
per-sample membership contract. The metadata-readable anonymous resource
surface exposes code/notebook inventory only, including `ArtArena.ipynb`,
`README.md`, ET/MD eval and infer scripts, `FT_models.py`, `get_leadger.py`,
prep scripts, `CSD/model.py`, `CSD/utils.py`, and figure PDFs. GitHub searches
returned no official public artifact repository, and no target checkpoint,
member/nonmember artwork manifest, generated image packet, per-row membership
score file, ROC array, metric JSON, or verifier is public. Decision:
`style-leakage semantic-shift watch / anonymous code-notebook inventory only /
no row-bound membership artifact / no download / no GPU release / no admitted
row`.

Previous Research update:
[trajectory-generation-privacy-artifact-gate-20260523.md](trajectory-generation-privacy-artifact-gate-20260523.md)
records a Lane A metadata gate for arXiv `2605.15246` / `Privacy Evaluation of
Generative Models for Trajectory Generation`. This is cross-domain
trajectory/mobility privacy evidence, not a current image or latent-image
asset. The diffusion trajectory results are weak, with DiffTraj
`AUC-ROC = 0.5012` and Diff-RNTraj `AUC-ROC = 0.4949`; the only clearly
positive table value is GAN MoveSim `AUC-ROC = 0.7002`. The public surface is
paper-source-only: arXiv source has LaTeX material only, GitHub searches
returned no official code or artifact hits, and no model checkpoint,
member/nonmember trajectory manifest, generated trajectory packet, score file,
ROC array, metric JSON, or verifier is public. Decision: `cross-domain
trajectory paper-source-only watch / diffusion trajectory MIA weak / no
code-score artifact / no download / no GPU release / no admitted row`.

Previous Research update:
[model-will-tell-drc-artifact-gate-20260523.md](model-will-tell-drc-artifact-gate-20260523.md)
records a Lane A/B metadata gate for arXiv `2403.08487` /
`Model Will Tell: Training Membership Inference for Diffusion Models`. DRC is
a non-duplicate restoration-prior watch signal, but the public surface is
paper-source-only: arXiv source has TeX/style/bibliography/figure entries only,
the paper says the authors intend to release code but gives no official code
URL, and exact-title/DRC/author/arXiv-id GitHub searches returned no official
code or artifact hits. Decision: `paper-source-only DRC restoration MIA watch /
no official code / no split-score artifact / no download / no GPU release / no
admitted row`.

Previous Research update:
[ROADMAP.md](../../ROADMAP.md)
now treats `Current Long-Horizon State` as the single active three-slot source
of truth after the PR `#267` current-state dedupe and PR `#268` steering
priority clarification. This is a roadmap operating-system update, not a new
candidate check: no download, CPU/GPU sidecar, Platform row, Runtime schema, or
admitted row is selected. Current slots are now maintained by the latest
candidate verdict above.

Previous Research update:
[discrete-dlm-withdrawn-artifact-gate-20260523.md](discrete-dlm-withdrawn-artifact-gate-20260523.md)
records a Lane B/watch metadata gate for arXiv `2605.16445` /
`Membership Inference Attacks on Discrete Diffusion Language Models`. The
current arXiv record is withdrawn and has no current PDF; repository searches
for the exact title and for `discrete diffusion language models membership
inference` returned no GitHub repositories; code search for `2605.16445`
returned no hits. Decision: `withdrawn arXiv / DLM paper-source-only / no
official code / no artifact packet / no download / no GPU release / no
admitted row`.

Previous Research update:
[workspaces/implementation/challenger-queue.md](../../workspaces/implementation/challenger-queue.md)
now points its `Current State` and `Active` section at the 2026-05-23
`hackerman70000/eidetic` lightweight triage closure instead of the older
ReDiffuse provenance state. This is a roadmap operating-system sync, not a new
candidate check: no download, CPU/GPU sidecar, Platform row, Runtime schema, or
admitted row is selected.

Previous Research update:
[github-lightweight-diffusion-mia-triage-20260515.md](github-lightweight-diffusion-mia-triage-20260515.md)
records the Lane A external-search false-positive triage. Five direct GitHub
diffusion-MIA hits are now covered, including `hackerman70000/eidetic`.
`eidetic` is a code-only Carlini-style toolkit with README-reported CIFAR-10
Strong-LiRA metrics, but it commits no shadow checkpoints, immutable split
manifest, per-row scores, ROC arrays, metric JSON, generated response packet,
or ready verifier, and its experiment path downloads CIFAR-10 plus requires
local shadow checkpoints. Decision: `lightweight GitHub false-positive / no
artifact packet / no download / no GPU release / no admitted row`.

Previous Research update:
[clid-identity-manifest-gate-20260515.md](clid-identity-manifest-gate-20260515.md)
and
[copymark-official-score-artifact-gate-20260515.md](copymark-official-score-artifact-gate-20260515.md)
now include the 2026-05-23 bounded metadata recheck. CLiD still has readable
HF dataset metadata and a local token, but authenticated range access to
`zsf/COCO_MIA_ori_split1/mia_COCO.zip` returns `403` with `restricted` / `not
in the authorized list`, so no ZIP central directory or internal manifest can
be inspected. CopyMark `laion_ridar` still exposes useful public support
evidence: `10000 / 10000` image logs and aggregate ROC/threshold JSON with
`AUROC = 0.872134768572823`, but no per-row score field or compact
filename/role/checkpoint/score manifest. Decision: `metadata recheck / no
download / no GPU release / no admitted row`.

Previous Research update:
[copymark-laion-mi-public-binding-gate-20260517.md](copymark-laion-mi-public-binding-gate-20260517.md)
records the bounded public CopyMark `laion_mi` row-binding audit. The current
public `members.parquet` exposes only `url/caption`, the official member
utility still expects a hidden third parquet column via `df.iloc[idx, 2]`, the
official numeric member filenames span `9617..33905220` while the current
public parquet has only `13396` rows, and a live spot-check found only `4/10`
of the first public member URLs still return `200`. The new
`probe-copymark-laion-mi-assets` command reproduces the gate locally. Decision:
`blocked / public row-binding gap / no download beyond small metadata subset /
no GPU release / no admitted row`.

Previous Research update:
[stable-diffusion-rediffuse-collaborator-artifact-20260517.md](stable-diffusion-rediffuse-collaborator-artifact-20260517.md)
records a collaborator-transferred Stable Diffusion ReDiffuse artifact audit.
The imported `5000`-row `2500 / 2500` result packet replays to
`AUC = 0.710319` and `ASR = 0.6846`, and the small `TPR@1%FPR` delta
(`0.0736` exact curve vs `0.0716` reported) stays within audit tolerance. The
bundle is useful candidate-only black-box evidence and now has a dedicated CLI
artifact probe, a bundle-level readiness probe, and a candidate-only
single-image scoring wrapper around the collaborator detector. It is still not
a public immutable replay packet, not the exact paper LAION-5B member split,
and not a strict external API-only black-box surface. Current local runtime
still lacks `fire`, `pytorch_lightning`, `skimage`, `omegaconf`, and a local
`CompVis/stable-diffusion-v1-4` checkpoint, so no download, CPU sidecar, GPU
release, or admitted row is selected.

Previous Research update:
[structural-mia-t2i-artifact-gate-20260515.md](structural-mia-t2i-artifact-gate-20260515.md)
records a direct text-to-image structural MIA mechanism watch. arXiv
`2407.13252` reports strong SSIM/forward-diffusion structure-level metrics, but
the arXiv source is TeX/figures only, exact GitHub searches found no official
release, and the OpenReview supplement ZIP contains only `supplementary.pdf`.
No code, target/split/score/ROC/metric artifacts, verifier, download, CPU
sidecar, GPU release, or admitted row is selected.

Previous Research update:
[rectified-flow-mia-artifact-gate-20260515.md](rectified-flow-mia-artifact-gate-20260515.md)
records a non-duplicate Rectified Flow / Flow Matching MIA mechanism watch.
arXiv `2603.13421` reports complexity-calibrated Monte Carlo vector-field
scoring with strong low-FPR gains, but the promised
`mx-ethan-rao/MIA_Rectified_Flow` repository is empty and no public splits,
checkpoints, scores, ROC arrays, metric JSON, verifier, download, CPU sidecar,
GPU release, or admitted row is selected.

Earlier Research update:
[public-metadata-asset-sweep-20260515.md](public-metadata-asset-sweep-20260515.md)
records the post-DIFFENCE Hugging Face/GitHub metadata sweep. Authenticated HF
metadata still exposes only known CLiD and CopyMark surfaces:
`zsf/COCO_MIA_ori_split1/mia_COCO.zip` remains range-inaccessible with auth,
`chumengl/copymark/datasets.zip` remains too large and already covered by the
CopyMark score-artifact gate, and GitHub artifact-shaped searches returned no
new non-duplicate replay packet. No download, GPU release, CPU sidecar, or
admitted row is selected.

Earlier Research update:
[diffence-classifier-defense-artifact-gate-20260515.md](diffence-classifier-defense-artifact-gate-20260515.md)
now includes the immutable Zenodo `10.5281/zenodo.13706131` code snapshot:
`604` entries with code/config/split-index files, but still no
checkpoint-bound logits, scores, ROC arrays, metric JSON, verifier, download,
GPU release, or admitted row.

Prior Research update:
[github-lightweight-diffusion-mia-triage-20260515.md](github-lightweight-diffusion-mia-triage-20260515.md)
records a Lane A external search triage. Five direct GitHub diffusion-MIA hits
are lightweight/course-style, toy, or code-only-toolkit false positives with no
public target checkpoint, immutable split manifest, row-bound response packet,
committed score rows, ROC arrays, metric JSON, ready verifier, download, GPU
release, or admitted row.

Earlier Research update:
[deb-medical-diffusion-artifact-gate-20260515.md](deb-medical-diffusion-artifact-gate-20260515.md)
records a Lane B mechanism gate. DEB is a paper-source-only medical
diffusion grey-box discrete-codebook / intermediate-trajectory MIA watch; no
public code, target/split/score/ROC/metric artifacts, verifier, download, GPU
release, or admitted row is selected.

Earlier progress review:
[daily-research-review-20260515.md](daily-research-review-20260515.md)
records the required progress review after the DSiRe / LoRA-WiSE and CPSample
gates. The review confirms the latest verdict note exists, current slots are
synchronized across Research and root roadmaps, defense/intake/implementation
workspace notes carry CPSample reopen and stop conditions, Research returned to
clean `main...origin/main` after PR `#248`, and no Platform/Runtime schema,
product-copy, recommendation, download, CPU sidecar, or GPU change was released.

| Track | Active docs | Role |
| --- | --- | --- |
| Black-box | [workspaces/black-box/README.md](../../workspaces/black-box/README.md), [plan.md](../../workspaces/black-box/plan.md), [rediffuse-stl10-bounded-scout-20260525.md](rediffuse-stl10-bounded-scout-20260525.md), [rediffuse-stl10-split-and-microtrain-preflight-20260525.md](rediffuse-stl10-split-and-microtrain-preflight-20260525.md), [copymark-laion-mi-public-binding-gate-20260517.md](copymark-laion-mi-public-binding-gate-20260517.md), [stable-diffusion-rediffuse-collaborator-artifact-20260517.md](stable-diffusion-rediffuse-collaborator-artifact-20260517.md), [public-metadata-asset-sweep-20260515.md](public-metadata-asset-sweep-20260515.md), [copymark-official-score-artifact-gate-20260515.md](copymark-official-score-artifact-gate-20260515.md), [shake-to-leak-code-artifact-gate-20260515.md](shake-to-leak-code-artifact-gate-20260515.md), [fseclab-mia-diffusion-code-artifact-gate-20260515.md](fseclab-mia-diffusion-code-artifact-gate-20260515.md), [genai-confessions-black-box-artifact-gate-20260515.md](genai-confessions-black-box-artifact-gate-20260515.md), [clid-official-inter-output-replay-20260515.md](clid-official-inter-output-replay-20260515.md), [midst-tabddpm-ept-scout-20260515.md](midst-tabddpm-ept-scout-20260515.md), [diffusion-memorization-asset-gate-20260515.md](diffusion-memorization-asset-gate-20260515.md), [rediffuse-openreview-split-manifest-audit-20260515.md](rediffuse-openreview-split-manifest-audit-20260515.md), [beans-lora-delta-sensitivity-20260513.md](beans-lora-delta-sensitivity-20260513.md), [quantile-regression-asset-verdict-20260513.md](quantile-regression-asset-verdict-20260513.md), [miagm-asset-verdict-20260513.md](miagm-asset-verdict-20260513.md), [noise-as-probe-asset-verdict-20260513.md](noise-as-probe-asset-verdict-20260513.md), [zenodo-code-reference-audit-20260513.md](zenodo-code-reference-audit-20260513.md), [zenodo-finetuned-diffusion-asset-verdict-20260513.md](zenodo-finetuned-diffusion-asset-verdict-20260513.md), [laion-mi-url-availability-probe-20260513.md](laion-mi-url-availability-probe-20260513.md), [laion-mi-asset-verdict-20260513.md](laion-mi-asset-verdict-20260513.md), [commoncanvas-denoising-loss-20260513.md](commoncanvas-denoising-loss-20260513.md), [midst-tabddpm-shadow-distributional-scout-20260513.md](midst-tabddpm-shadow-distributional-scout-20260513.md), [midst-tabddpm-nearest-neighbor-scout-20260513.md](midst-tabddpm-nearest-neighbor-scout-20260513.md), [copymark-commoncanvas-multiseed-stability-20260513.md](copymark-commoncanvas-multiseed-stability-20260513.md), [fashion-mnist-ddpm-pia-loss-scout-20260513.md](fashion-mnist-ddpm-pia-loss-scout-20260513.md), [kohaku-danbooru-asset-decision-20260513.md](kohaku-danbooru-asset-decision-20260513.md), [tiny-known-split-gradient-prototype-alignment-20260513.md](tiny-known-split-gradient-prototype-alignment-20260513.md), [copymark-commoncanvas-response-preflight-20260512.md](copymark-commoncanvas-response-preflight-20260512.md), [copymark-commoncanvas-query-asset-20260512.md](copymark-commoncanvas-query-asset-20260512.md), [copymark-provenance-intake-20260512.md](copymark-provenance-intake-20260512.md), [external-diffusion-benchmark-provenance-scan-20260512.md](external-diffusion-benchmark-provenance-scan-20260512.md), [true-second-membership-benchmark-scope-20260512.md](true-second-membership-benchmark-scope-20260512.md), [gradient-norm-stability-gate-20260512.md](gradient-norm-stability-gate-20260512.md), [tiny-overfit-gradient-norm-scout-20260512.md](tiny-overfit-gradient-norm-scout-20260512.md), [tiny-overfit-mse-upperbound-20260512.md](tiny-overfit-mse-upperbound-20260512.md), [tiny-known-split-denoising-sanity-20260512.md](tiny-known-split-denoising-sanity-20260512.md), [mnist-ddpm-x0-reconstruction-scout-20260512.md](mnist-ddpm-x0-reconstruction-scout-20260512.md), [beans-sd15-membership-semantics-correction-20260512.md](beans-sd15-membership-semantics-correction-20260512.md), [beans-sd15-clip-distance-scout-20260512.md](beans-sd15-clip-distance-scout-20260512.md), [beans-sd15-simple-distance-scout-20260512.md](beans-sd15-simple-distance-scout-20260512.md), [beans-sd15-response-contract-ready-20260512.md](beans-sd15-response-contract-ready-20260512.md), [beans-sd15-response-contract-scout-20260512.md](beans-sd15-response-contract-scout-20260512.md), [mnist-ddpm-pia-portability-smoke-20260512.md](mnist-ddpm-pia-portability-smoke-20260512.md), [midfreq-residual-comparator-audit-20260512.md](midfreq-residual-comparator-audit-20260512.md), [midfreq-residual-stability-result-20260512.md](midfreq-residual-stability-result-20260512.md), [midfreq-residual-stability-decision-20260512.md](midfreq-residual-stability-decision-20260512.md), [midfreq-residual-signcheck-20260512.md](midfreq-residual-signcheck-20260512.md), [midfreq-same-noise-residual-preflight-20260512.md](midfreq-same-noise-residual-preflight-20260512.md), [midfreq-residual-scorer-contract-20260512.md](midfreq-residual-scorer-contract-20260512.md), [midfreq-residual-collector-contract-20260512.md](midfreq-residual-collector-contract-20260512.md), [midfreq-residual-tiny-runner-contract-20260512.md](midfreq-residual-tiny-runner-contract-20260512.md), [midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md) | ReDiffuse STL-10 bounded scout now records a scoreable but weak short-target packet: `300` steps, `256 / 256` scores, `AUC = 0.4996337890625`, `ASR = 0.509765625`, `TPR@1%FPR = 0.01171875`, and no GPU expansion. ReDiffuse STL-10 split/statistics/resource preflight recorded exact `50k / 50k` split binding, no low-level image-statistics leakage on holdout, and CUDA batch `64` official DDPM model/trainer feasibility. CopyMark `laion_mi` public binding gate records a bounded public row-binding failure: the current public member parquet exposes only `url/caption`, the official member utility still expects a hidden third column, official numeric member filenames exceed the current public row range, and a live spot-check finds only `4/10` of the first public member URLs still return `200`; keep it as support-only CopyMark evidence with no large download or GPU release. Stable Diffusion ReDiffuse collaborator artifact audit records a real imported `5000`-row `2500 / 2500` result packet with replayed `AUC = 0.710319`, but it remains candidate-only because it is a collaborator local transfer, uses a LAION-like member subset rather than the exact paper split, and is not a strict external API-only packet; public metadata sweep after HF auth and GitHub artifact searches found no new non-duplicate replay packet; CLiD ZIP remains range-inaccessible with auth, CopyMark HF ZIP remains already-covered and too large to change the current decision; CopyMark official score-artifact support evidence with public member/nonmember logs, aggregate ROC/threshold JSONs, selected all-step tensors, laion_ridar/mixing results, but no checkpoint hashes, compact row-ID-bound score manifest, small immutable data/checkpoint packet, or ready verifier; Shake-to-Leak code-public fine-tuning-amplified generative privacy watch-plus with target/data/score artifacts missing, FSECLab MIA-Diffusion official DDIM/DCGAN code-public but checkpoint/score/result-missing watch-plus, GenAI Confessions raw-input data-public but response/checkpoint missing black-box boundary watch, strong official CLiD CPU inter-output replay that remains prompt-conditioned candidate-only, weak MIDST TabDDPM EPT scout after nearest-neighbor and shadow-distributional failures, Diffusion Memorization semantic-shift watch, ReDiffuse official OpenReview split-manifest provenance, Reconstruction, variation, H2/simple-distance, weak Beans LoRA parameter-delta sensitivity and conditional denoising-loss under repaired known-split membership semantics, Quantile Regression sample-conditioned reconstruction-loss mechanism reference that is artifact-incomplete, MIAGM generated-distribution reference that is artifact-incomplete, Noise as a Probe semantic-initial-noise mechanism watch that is reproduction-incomplete, Zenodo fine-tuned diffusion paper/code-backed archive watch that remains split-manifest incomplete, LAION-mi metadata-only watch after failed fixed `25/25` URL availability probe, true second membership benchmark scope, weak CommonCanvas conditional denoising-loss scout, weak MIDST TabDDPM nearest-neighbor scout, weak MIDST shadow-distributional scout, weak Fashion-MNIST DDPM PIA-loss scout, Kohaku/Danbooru membership-semantics block, CopyMark provenance intake, local CommonCanvas query asset, completed `50/50` CommonCanvas responses with weak pixel-distance, CLIP image-similarity, prompt-response consistency, multi-seed response-stability, and conditional denoising-loss scorers, weak `64/64` gradient-prototype alignment scout, external provenance scan, Beans contract/debug boundary, MNIST/DDPM raw-loss and x0 simple-scorer scouts, tiny known-split raw-MSE sanity checks, tiny overfit gradient-norm mechanism signal and weakened stability gate, and same-noise residual candidate status. |
| Gray-box | [workspaces/gray-box/README.md](../../workspaces/gray-box/README.md), [plan.md](../../workspaces/gray-box/plan.md), [structural-mia-t2i-artifact-gate-20260515.md](structural-mia-t2i-artifact-gate-20260515.md), [rectified-flow-mia-artifact-gate-20260515.md](rectified-flow-mia-artifact-gate-20260515.md), [dsire-lora-wise-dataset-size-boundary-20260515.md](dsire-lora-wise-dataset-size-boundary-20260515.md), [hyperfree-secmi-reproduction-gate-20260515.md](hyperfree-secmi-reproduction-gate-20260515.md), [dme-dual-model-entropy-artifact-gate-20260515.md](dme-dual-model-entropy-artifact-gate-20260515.md), [fremia-frequency-filter-artifact-gate-20260515.md](fremia-frequency-filter-artifact-gate-20260515.md), [vae2diffusion-latent-space-inversion-gate-20260515.md](vae2diffusion-latent-space-inversion-gate-20260515.md), [fcre-medical-frequency-artifact-gate-20260515.md](fcre-medical-frequency-artifact-gate-20260515.md), [privacy-leakage-tdm-artifact-gate-20260515.md](privacy-leakage-tdm-artifact-gate-20260515.md), [tmia-dm-temporal-artifact-gate-20260515.md](tmia-dm-temporal-artifact-gate-20260515.md), [quantile-diffusion-mia-secmia-terror-replay-20260515.md](quantile-diffusion-mia-secmia-terror-replay-20260515.md), [noise-aggregation-small-noise-artifact-gate-20260515.md](noise-aggregation-small-noise-artifact-gate-20260515.md), [sima-scorebased-artifact-gate-20260515.md](sima-scorebased-artifact-gate-20260515.md), [tracing-roots-feature-packet-mia-20260515.md](tracing-roots-feature-packet-mia-20260515.md), [../product-bridge/tracing-roots-candidate-evidence-card.md](../product-bridge/tracing-roots-candidate-evidence-card.md), [cdi-official-artifact-gate-20260515.md](cdi-official-artifact-gate-20260515.md), [fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md), [fashion-mnist-ddpm-sima-score-norm-20260514.md](fashion-mnist-ddpm-sima-score-norm-20260514.md), [mofit-artifact-verdict-20260513.md](mofit-artifact-verdict-20260513.md), [secmi-consumer-contract-review-20260512.md](secmi-consumer-contract-review-20260512.md), [post-midfreq-next-lane-reselection-20260512.md](post-midfreq-next-lane-reselection-20260512.md), [gray-box-paper-candidate-reentry-review-20260512.md](gray-box-paper-candidate-reentry-review-20260512.md) | Structural T2I MIA paper-source-only mechanism watch with OpenReview PDF-only supplement, Rectified Flow / Flow Matching MIA paper-source-only mechanism watch with promised but empty public repo, DSiRe / LoRA-WiSE future weight-only dataset-size recovery boundary gate, Hyperparameter-free SecMI third-party code/report support-family gate, DME complexity-bias MIA stub-repo-only watch, FreMIA frequency-filter MIA paper-source-plus-stub-repo watch, PIA, SecMI, VAE2Diffusion latent-space decoder-geometry MIA code-public watch-plus with split/checkpoint/score artifacts missing, FCRE medical-image frequency-calibrated reconstruction-error paper-source watch, single-table Tabular Privacy Leakage TDM watch-plus with official MIDST toolkit code but no paper score packet, TMIA-DM temporal-noise / noise-gradient paper-only watch, Quantile Diffusion MIA third-party SecMI-style `t_error` support packet, Noise Aggregation small-noise predicted-noise aggregation MIA paper-source-only watch, official SimA score-based MIA watch-plus with code-public but split/checkpoint/score artifacts missing, Tracing the Roots positive-but-provenance-limited trajectory feature-packet MIA with a candidate-only product-bridge card, official CDI dataset-inference gate as code-public but large-assets-required/no ready score packet/no GPU release, weak Fashion-MNIST score-Jacobian sensitivity scout, weak Fashion-MNIST SimA score-norm scout, MoFit artifact-incomplete watch, archived paper-candidate, DCR copying/memorization semantic-shift watch, and gray-box defense boundary status. |
| White-box | [workspaces/white-box/README.md](../../workspaces/white-box/README.md), [plan.md](../../workspaces/white-box/plan.md), [white-box-gsa-zenodo-archive-verdict-20260513.md](white-box-gsa-zenodo-archive-verdict-20260513.md), [white-box-influence-curvature-feasibility-scout-20260511.md](white-box-influence-curvature-feasibility-scout-20260511.md), [gsa-diagonal-fisher-feasibility-microboard-20260511.md](gsa-diagonal-fisher-feasibility-microboard-20260511.md), [gsa-diagonal-fisher-layer-scope-review-20260511.md](gsa-diagonal-fisher-layer-scope-review-20260511.md), [gsa-diagonal-fisher-stability-board-20260511.md](gsa-diagonal-fisher-stability-board-20260511.md), [post-fisher-next-lane-reselection-20260511.md](post-fisher-next-lane-reselection-20260511.md) | GSA, DPDM, admitted-family GSA Zenodo archive identity, Finding NeMo, and white-box boundary status. |
| Cross-box | [workspaces/cross-box/README.md](../../workspaces/cross-box/README.md), [cross-box-boundary-status.md](cross-box-boundary-status.md), [cross-box-successor-scope-20260512.md](cross-box-successor-scope-20260512.md), [post-ib-next-lane-reselection-20260512.md](post-ib-next-lane-reselection-20260512.md), [ic-same-spec-evaluator-feasibility-scout-20260512.md](ic-same-spec-evaluator-feasibility-scout-20260512.md) | Cross-track score-sharing, cross-permission boundary, and successor reopen conditions. |
| Defense | [workspaces/defense/README.md](../../workspaces/defense/README.md), [cpsample-defense-artifact-gate-20260515.md](cpsample-defense-artifact-gate-20260515.md), [dualmd-distillmd-defense-artifact-gate-20260515.md](dualmd-distillmd-defense-artifact-gate-20260515.md), [diffence-classifier-defense-artifact-gate-20260515.md](diffence-classifier-defense-artifact-gate-20260515.md), [miahold-higher-order-langevin-artifact-gate-20260515.md](miahold-higher-order-langevin-artifact-gate-20260515.md), [stableprivatelora-defense-artifact-gate-20260515.md](stableprivatelora-defense-artifact-gate-20260515.md), [ib-risk-targeted-unlearning-successor-scope.md](ib-risk-targeted-unlearning-successor-scope.md), [ib-adaptive-defense-contract-20260511.md](ib-adaptive-defense-contract-20260511.md), [ib-defense-aware-reopen-scout-20260512.md](ib-defense-aware-reopen-scout-20260512.md), [ib-defense-reopen-protocol-audit-20260512.md](ib-defense-reopen-protocol-audit-20260512.md), [ib-defended-shadow-reopen-protocol-20260512.md](ib-defended-shadow-reopen-protocol-20260512.md), [ib-reopen-shadow-reference-guard-20260512.md](ib-reopen-shadow-reference-guard-20260512.md), [ib-defended-shadow-training-manifest-20260512.md](ib-defended-shadow-training-manifest-20260512.md), [ib-shadow-local-identity-scout-20260512.md](ib-shadow-local-identity-scout-20260512.md), [ib-shadow-local-gsa-risk-preflight-20260515.md](ib-shadow-local-gsa-risk-preflight-20260515.md) | CPSample sampling-time classifier-protected defense watch-plus, DualMD/DistillMD disjoint-split defense watch-plus, DIFFENCE classifier-defense watch-plus, MIAHOLD/HOLD++ higher-order Langevin defense watch-plus, StablePrivateLoRA defense watch-plus, risk-targeted unlearning boundary, true shadow-local GSA-only risk preflight, and defended-shadow/adaptive reopen conditions. |
| Implementation | [workspaces/implementation/README.md](../../workspaces/implementation/README.md), [challenger-queue.md](../../workspaces/implementation/challenger-queue.md), [daily-research-review-20260515.md](daily-research-review-20260515.md), [daily-research-review-20260513.md](daily-research-review-20260513.md), [../product-bridge/clid-candidate-evidence-card.md](../product-bridge/clid-candidate-evidence-card.md), [../product-bridge/tracing-roots-candidate-evidence-card.md](../product-bridge/tracing-roots-candidate-evidence-card.md) | Shared CLI, schemas, queue state, CLiD and Tracing Roots candidate-only evidence cards, daily slot reviews, and research operations. |
| I-A / consumer boundary | [admitted-consumer-drift-audit-20260515.md](admitted-consumer-drift-audit-20260515.md), [cross-modal-watch-consumer-boundary-20260515.md](cross-modal-watch-consumer-boundary-20260515.md), [cross-modal-watch-consumer-boundary-20260514.md](cross-modal-watch-consumer-boundary-20260514.md), [paperization-consumer-boundary-20260513.md](paperization-consumer-boundary-20260513.md), [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md), [ia-finite-tail-adaptive-boundary-audit-20260511.md](ia-finite-tail-adaptive-boundary-audit-20260511.md), [admitted-results-summary.md](admitted-results-summary.md), [../product-bridge/README.md](../product-bridge/README.md), [../product-bridge/clid-candidate-evidence-card.md](../product-bridge/clid-candidate-evidence-card.md), [../product-bridge/tracing-roots-candidate-evidence-card.md](../product-bridge/tracing-roots-candidate-evidence-card.md) | 2026-05-15 admitted no-drift audit, cross-modal watch boundary including DurMI TTS and LSA-Probe music/audio, CLiD and Tracing Roots candidate-only evidence cards, finite-tail, adaptive-language, paperization limitation, and admitted/candidate boundary status. |
| FMIA / frequency watch | [fmia-openreview-frequency-artifact-gate-20260515.md](fmia-openreview-frequency-artifact-gate-20260515.md) | 2026-05-23 bounded OpenReview recheck confirmed the same small official supplement: version `2` rejected ICLR 2026 submission, `1,783,018` byte ZIP, SHA-256 `567ac598eefc849c9dfdd95c26be24bd6b7349c72843e210b56cce2f67969045`, `79` entries, code and split manifests present, but no checkpoints, generated samples, row-level score exports, ROC CSVs, metric JSON, or ready verifier; FMIA remains watch-plus only with no download, no GPU/CPU sidecar, and no Platform/Runtime admission. |
| Watch candidates / consumer boundary | [identity-focused-inference-extraction-artifact-gate-20260523.md](identity-focused-inference-extraction-artifact-gate-20260523.md), [rapta-admcd-copying-mitigation-artifact-gate-20260523.md](rapta-admcd-copying-mitigation-artifact-gate-20260523.md), [guard-surgical-mitigation-artifact-gate-20260523.md](guard-surgical-mitigation-artifact-gate-20260523.md), [baf-lora-parameter-space-mitigation-gate-20260523.md](baf-lora-parameter-space-mitigation-gate-20260523.md), [broken-memories-artifact-gate-20260523.md](broken-memories-artifact-gate-20260523.md), [iar-privacy-attacks-artifact-gate-20260523.md](iar-privacy-attacks-artifact-gate-20260523.md), [discrete-dlm-withdrawn-artifact-gate-20260523.md](discrete-dlm-withdrawn-artifact-gate-20260523.md), [hyperfree-secmi-reproduction-gate-20260515.md](hyperfree-secmi-reproduction-gate-20260515.md), [dme-dual-model-entropy-artifact-gate-20260515.md](dme-dual-model-entropy-artifact-gate-20260515.md), [fremia-frequency-filter-artifact-gate-20260515.md](fremia-frequency-filter-artifact-gate-20260515.md), [copymark-official-score-artifact-gate-20260515.md](copymark-official-score-artifact-gate-20260515.md), [diffusion-memorization-asset-gate-20260515.md](diffusion-memorization-asset-gate-20260515.md), [memorization-anisotropy-artifact-gate-20260515.md](memorization-anisotropy-artifact-gate-20260515.md), [watch-candidate-consumer-boundary-20260513.md](watch-candidate-consumer-boundary-20260513.md) | Identity-Focused Inference, RAPTA / ADMCD, GUARD, BAF, Broken Memories, IAR Privacy Attacks, Discrete DLM, Hyperparameter-free SecMI, DME, FreMIA, CopyMark score artifacts, Diffusion Memorization, Memorization Anisotropy, and older watch candidates remain Research-only watch / support / semantic-shift / paper-source-only / artifact-incomplete states unless a future reviewed promotion occurs. |
| Intake | [workspaces/intake/README.md](../../workspaces/intake/README.md) | Candidate intake and archived paper-backed scouting. |
| Runtime | [workspaces/runtime/README.md](../../workspaces/runtime/README.md) | Research-side runtime contract notes. |

## Archived Workspace History

| Track | Archive |
| --- | --- |
| Root workspace notes | [legacy/workspaces/root/2026-04/](../../legacy/workspaces/root/2026-04/) |
| Black-box | [legacy/workspaces/black-box/2026-04/](../../legacy/workspaces/black-box/2026-04/) |
| Gray-box | [legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/) |
| White-box | [legacy/workspaces/white-box/2026-04/](../../legacy/workspaces/white-box/2026-04/) |
| Implementation | [legacy/workspaces/implementation/2026-04/](../../legacy/workspaces/implementation/2026-04/) |
| Intake | [legacy/workspaces/intake/2026-04/](../../legacy/workspaces/intake/2026-04/) |

Archived notes are retained for traceability. They are not the default source
of current truth.
