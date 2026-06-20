# E2 Targeted Public Artifact Discovery, Pass E

> Date: 2026-06-08
> Mode: current arXiv/GitHub primary-source refresh, no downloads
> Decision: no new row-bound public score/response artifact found; no C14 expansion; no compute release

## Scope

This pass refreshes the current arXiv primary-source surface for recent titles
that can look like new DiffAudit opportunities after the post-C14 queue reached
`0`. It uses arXiv API metadata, GitHub repository search, GitHub code search,
and `git ls-remote` for one already-known official repository. It does not
download PDFs, source tarballs, datasets, archives, generated media,
checkpoints, model weights, or score files. It does not execute code or use
GPU/DCU resources.

The purpose is duplicate control and route hygiene, not corpus expansion. A row
can move the CCF-A route only if it exposes target identity, exact
member/nonmember row identities, row-bound score or response coverage, metric
provenance, and a no-training verifier.

## Findings

| Candidate | Current public surface | Blocking surface | Decision |
| --- | --- | --- | --- |
| SD-MIA / pre-training data of image-generation models | arXiv `2605.27020v1` is a CVPR 2026 camera-ready paper. `wanghl21/SD-MIA` still points `HEAD` and `refs/heads/main` to `89384223da4ef95f9bddb3d1e222ccf339b914ac`. | This is the same surface already checked as `E2SCT-028`: public code and paper result, but no committed `data/original.json`, perturbation JSONs, generated responses, `attack_results.json`, row-score table, ROC arrays, metric JSON, or verifier. | Duplicate current-source refresh only; keep as support-only code-public pre-training T2I MIA reference. |
| Silent Brush / Art Arena | arXiv `2605.17500v1` remains the primary paper surface and is already covered by the Silent Brush artifact gate. | Style-leakage/copyright evaluation rather than per-sample membership; no target checkpoint hash, immutable member/nonmember artwork manifest, generated image packet, row score, ROC, metric JSON, or verifier. | Duplicate current-source refresh only; related privacy / semantic-shift watch. |
| Data-Free MIA on Federated Learning in Hardware Assurance | arXiv `2604.19891v1`; exact-title GitHub repository search returned no primary artifact repository in this pass. | Hardware-assurance FL gradient-inversion target, not image/latent diffusion training-set membership; no row-bound target/split/score/response packet. | Out-of-scope FL/hardware paper-source watch. |
| DISCO-TAB | arXiv `2604.01481v1`; exact-title GitHub repository search returned no primary artifact repository in this pass. | Privacy-preserving clinical tabular synthesis / LLM+RL framework, not diffusion MIA; no member/nonmember score packet, ROC/metric JSON, or verifier. | Out-of-scope synthetic-EHR privacy paper-source watch. |
| Risk In Context | arXiv `2507.17066v1`; exact-title GitHub repository search returned no primary artifact repository in this pass. | Tabular in-context synthetic-data leakage benchmark rather than image-diffusion target membership; no row-bound diffusion score/response packet or verifier. | Tabular/ICL related privacy watch only. |

## Decision

Pass E found no new public row-bound diffusion MIA score or response packet.
It does not change the evidence state:

- C14 selected stress rows remain `13`.
- Directly freezable external denominator rows remain `0`.
- New row-bound score/response artifacts from current arXiv/GitHub primary
  refresh: `0`.
- `active_gpu_question = none`.
- `next_gpu_candidate = none`.
- `CPU sidecar = none selected`.

This pass should stop future re-scans of these current-title surfaces unless a
primary source changes: SD-MIA repository commit/artifact layout changes,
Silent Brush publishes a row-bound membership artifact, or one of the
paper-source/out-of-scope rows publishes official target/split/score/verifier
artifacts and passes a consumer-boundary review.

## Stop Rule

Do not download arXiv source/PDF payloads, artwork datasets, clinical/tabular
datasets, hardware-assurance images, generated media, target models,
checkpoints, or score archives from these rows. Do not implement methods from
paper text. Reopen only if a public primary source exposes immutable
member/nonmember row IDs, committed score or response rows, metric provenance,
and a no-training verifier.
