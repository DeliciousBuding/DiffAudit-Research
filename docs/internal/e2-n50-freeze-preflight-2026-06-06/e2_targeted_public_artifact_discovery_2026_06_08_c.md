# E2 Targeted Public Artifact Discovery, Pass C

> Date: 2026-06-08
> Mode: no-download live GitHub/source check
> Decision: no new row-bound public score/response artifact found; no C14 expansion; no compute release

## Scope

This pass follows the MoFit paper-facing update and checks two current
cross-domain diffusion/privacy artifacts that could otherwise create shortcut
pressure:

- `Stry233/SAMA`, ICLR 2026 diffusion-language-model MIA;
- `kaslim/LSA-Probe`, music-diffusion MIA.

The check is deliberately no-download. It reads GitHub repository metadata,
default-branch commits, recursive tree path names, README text, small config/code
metadata, and selected source snippets. It does not clone repositories, download
datasets or model checkpoints, execute notebooks/code, train target models,
query GPUs/DCUs, unpickle files, or generate score packets.

## Live Checks

| Candidate | Public surface | Live observation | Blocking surface | Decision |
| --- | --- | --- | --- | --- |
| SAMA / DLM MIA | `Stry233/SAMA` | Public repo; main commit `5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd`; README links arXiv `2601.20125` and OpenReview and describes ICLR 2026 SAMA for finetuned diffusion language models. Tree exposes attack code, metric code, model configs, dataset preparation, and DLM training code. | Cross-domain diffusion-language-model surface; config paths use local `train_subset.json` / `test_subset.json` and local target models. No committed immutable member/nonmember row manifest, target checkpoint hash, per-row score table, ROC/metric JSON, completed metadata output, or no-training verifier was observed. | Support-only DLM code-public artifact; not current image-diffusion denominator, not C14, not admitted evidence, not second public score/response asset, and not compute release. |
| SAMA runtime metadata schema | `attack/attacks/sama.py` and `attack/run.py` | `sama.py` can save `config.json` and `full_metadata.json` with sample indices, step scores, final score, and subset metadata; `run.py` computes AUC and TPR@FPR thresholds and saves metadata under the selected output directory. | The score/metadata packet is generated only after local dataset preparation and target-model execution; it is not committed as a public row-bound packet. | Useful schema pressure for future DLM review only; no paper evidence upgrade. |
| LSA-Probe / music diffusion MIA | `kaslim/LSA-Probe` | Public repo; main commit `594900158e31b5c5b801d3d534dcc44deb8ade7c`; README states the project is under peer review and that full implementation/reproducibility instructions will be released upon acceptance. | No implementation, target/split manifest, row-bound scores/responses, ROC/metric JSON, or verifier was observed in the repo. | Support-only music/audio watch item; not C14 expansion, not current denominator, not admitted evidence, and not compute release. |

## Decision

This pass found no new public row-bound diffusion MIA score or response packet.
It does not change the paper-facing evidence state:

- C14 selected stress rows remain `13`.
- Directly freezable external denominator rows remain `0`.
- New row-bound score/response artifacts from targeted post-queue discovery remain `0`.
- `active_gpu_question = none`.
- `next_gpu_candidate = none`.
- `CPU sidecar = none selected`.

SAMA is the stronger new pressure point because it is public, current, and
contains code that can generate per-sample metadata, but the public repository
does not expose a reusable row-bound packet. LSA-Probe remains implementation
pending. Neither should be added to the Direction A manuscript as evidence.

## Stop Rule

Do not train or run SAMA or LSA-Probe, download their datasets/checkpoints,
generate local metadata, or open GPU/DCU work for these rows. Reopen SAMA only
if a public source exposes target identity, immutable member/nonmember row IDs,
committed score/metadata rows, metric provenance, and a no-training verifier.
Reopen LSA-Probe only after the promised implementation and reproducibility
packet are public and expose row-bound scores/responses or a verifier.
