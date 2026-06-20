# E2 Targeted Public Artifact Discovery

> Date: 2026-06-08
> Mode: no-download live discovery pass
> Decision: no new row-bound public score/response artifact found; no C14 expansion; no compute release

## Scope

This note records a bounded discovery pass after the post-C14 expansion queue
closed with `0` remaining rows. The goal was not to enlarge taxonomy or repeat
existing artifact gates. The pass asked one question: did any currently visible
public surface expose a new compact row-bound score or response packet that
could change Direction A's scientific blockers?

Sources were limited to web search snippets, GitHub repository metadata,
repository contents, release lists, recursive tree path names, and existing
DiffAudit no-download gates. No archive, dataset, media payload, checkpoint,
generated response, notebook output, or model artifact was downloaded. No code
was run.

## Live Checks

| Candidate | Public surface | Live observation | Blocking surface | Decision |
| --- | --- | --- | --- | --- |
| SimA score-based MIA | `mx-ethan-rao/SimA` | Official code repo is public; default branch `master`; latest push `2026-03-25T18:20:29Z`; GitHub releases are empty. The tree is dominated by code, figures, and vendored diffusion dependencies. | No public immutable split manifest, checkpoint bundle, row-bound scores, ROC arrays, metric JSON/CSV, or verifier. | Existing `E2SCT-010` support-only decision unchanged. |
| SD-MIA pre-training T2I MIA | `wanghl21/SD-MIA` | Public repo is fresh; default branch `main`; latest push `2026-06-05T03:38:38Z`; GitHub releases are empty. Top-level entries are `README.md`, `img`, `process.ipynb`, `requirements.txt`, `scripts`, and `src`; filtered tree names expose `img/main_results.png` and `process.ipynb`, not data or results. | No committed `data/original.json`, perturbation JSONs, `attack_results.json`, row-score table, generated response packet, split manifest, ROC/metric JSON, or verifier. | Existing `E2SCT-028` support-only decision unchanged. |
| SAMA diffusion-language-model MIA | `Stry233/SAMA` | Public DLM code repo; default branch `main`; latest push `2026-04-13T20:47:11Z`; GitHub releases are empty. The tree exposes dataset preparation, target training, model configs, and SAMA/baseline attack code. | No released target DLM checkpoint or LoRA, fixed member/nonmember manifest, reusable response/score packet, ROC/metric artifact, or current image/latent-image consumer boundary. | Remains related-method / out-of-scope DLM code-only target recreation. |
| DEB medical diffusion MIA | MDPI article `10.3390/app16073140` | DOI and discrete-encoding title-keyword GitHub repo/code searches returned no hits in this pass. | No official code, target checkpoint, split manifest, intermediate-state packet, score rows, ROC arrays, metric JSON, or verifier. | Existing paper-source-only medical diffusion mechanism-watch decision unchanged. |

## Decision

This pass found no new public row-bound diffusion MIA score or response packet.
It does not change C14, the external denominator count, admitted evidence, or
compute policy:

- C14 selected stress rows remain `13`.
- Post-C14 expansion queue remains `0`.
- Directly freezable external denominator rows remain `0`.
- `active_gpu_question = none`.
- `next_gpu_candidate = none`.
- `CPU sidecar = none selected`.

The strongest fresh public surface is SD-MIA because it is a 2026 image-generation
pre-training MIA with public code. It still lacks the artifacts that would make
it an evidence object. The next paper-changing move remains external label
collection for the prepared C14 packet or discovery of a genuinely public
target/split/score or target/split/response packet.

## Stop Rule

Do not run SimA, SD-MIA, SAMA, or DEB from this pass. Do not download LAION,
FlickrMIA, CIFAR, MedMNIST, language datasets, model weights, checkpoints,
generated images, response archives, or notebook outputs. Reopen only if a
public source exposes target identity, immutable member/nonmember row IDs,
row-bound score/response artifacts, metric provenance, and a no-training
verifier.
