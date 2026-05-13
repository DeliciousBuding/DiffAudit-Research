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
