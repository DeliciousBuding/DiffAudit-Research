# Intake Workspace

## Current Status

- Direction: new method evaluation and paper scouting.
- No active intake review.
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
  Lane A second asset. Its public scripts assume local Pokémon/COCO/LAION
  datasets, local split files, and a local `sd-pokemon-checkpoint`; no
  checkpoint, exact member/nonmember manifest, or query/response package is
  published. No download or GPU work is released.

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
- Reopen only if a public-safe artifact exposes a hashable LDM checkpoint or
  deterministic recreation recipe, exact member/nonmember manifests, and a
  generated response or query/response package.
- Do not download or reconstruct the Pokémon checkpoint, scrape LAION/COCO
  assets, or package this fork as an independent second asset.
