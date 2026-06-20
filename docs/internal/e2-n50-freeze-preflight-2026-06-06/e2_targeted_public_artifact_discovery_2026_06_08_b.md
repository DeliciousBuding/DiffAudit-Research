# E2 Targeted Public Artifact Discovery, Pass B

> Date: 2026-06-08
> Mode: no-download live discovery pass
> Decision: no new row-bound public score/response artifact found; no C14 expansion; no compute release

## Scope

This pass follows the first 2026-06-08 targeted discovery note after the
post-C14 expansion queue reached `0`. It checks additional public repositories
and one companion Zenodo record that looked close to diffusion MIA, generative
privacy, or score/response artifact surfaces.

The question is narrow: did a visible public surface expose a compact,
row-bound score or response packet that could change Direction A's CCF-A
blockers?

Sources were limited to repository metadata, default branches, recursive tree
path names, README text already served by GitHub, and the Zenodo record catalog.
No repository clone, archive download, dataset payload, checkpoint, generated
media, notebook output, pickle, or model file was downloaded or executed. Broad
GitHub search attempts that failed with TLS/EOF errors are not used as evidence.

## Live Checks

| Candidate | Public surface | Live observation | Blocking surface | Decision |
| --- | --- | --- | --- | --- |
| LSA-Probe diffusion MIA | `kaslim/LSA-Probe` | Public repo metadata was visible; the path filter did not expose committed score, result, split, metric, ROC, or verifier artifacts. | No immutable target/split manifest, row-bound score/response packet, ROC/metric JSON, or no-training verifier observed. | Support-only code/public-method reference. |
| MIAGM diffusion MIA | `minxingzhang/MIAGM` | Public repo metadata was visible; the path filter did not expose a row-bound score/result packet. | No public row-bound member/nonmember score rows, generated response packet, ROC/metric JSON, immutable split manifest, or verifier observed. | Support-only code/public-method reference. |
| Memorization-LDM | `Cardio-AI/memorization-ldm` plus Zenodo record `15267790` | GitHub exposes notebooks and model-cache path names. Zenodo exposes `memorization-ldm.zip` as a software archive (`3,686,212` bytes; `md5:f939e9a7c0a0a4a80d8c65b0a1a67cf2`). | No row-bound score/response artifact, ROC/metric JSON, split manifest, or verifier observed. | Support-only software surface. |
| Health Privacy Challenge | `PMBio/Health-Privacy-Challenge` | The filtered tree hit only `src/evaluation/utils/sc_metrics.py`. | No challenge-label/prediction packet, row-bound score table, ROC/metric artifact, or verifier observed. | Support-only benchmark/evaluation-code reference. |
| SecMI | `jinhaoduan/SecMI` | The public tree exposes `mia_evals/member_splits/*.npz`, score code, and `stats/cifar10.train.npz`. | Split/code support exists, but no new independent row-bound result packet, generated response packet, ROC/metric JSON, or verifier was observed. | Known SecMI-family support surface, not a new second asset. |
| Reconstruction-based Attack | `py85252876/Reconstruction-based-Attack` | Metadata is public; filtered tree hits are `build_caption.py` and `train_text_to_image_lora.py`. | Code-level reconstruction/fine-tuning workflow only in this check; no immutable target/split manifest, row-bound score/response packet, ROC/metric JSON, or verifier observed. | Support-only black-box reconstruction reference. |
| GSA | `py85252876/GSA` | Metadata is public; filtered tree hits include DDPM/Imagen dataset, preparation, training, and `test_attack_accuracy.py` paths. | Code/test workflow only in this check; no public row-bound score table, split-bound result packet, ROC/metric JSON, or verifier observed. | Source-documented point/comparator support only, not a replay packet. |
| FSECLab MIA-Diffusion | `fseclab-osaka/mia-diffusion` | Metadata and README are public. The tree exposes attack code and FID stats files such as `TTUR/fid_stats_celeba_60k.npz`, `TTUR/fid_stats_cifar10_train.npz`, `attacks/tools/eval_roc.py`, and checkpoint utility code. | Attack/reproduction code and FID stats only in this check; no row-bound score/result table, immutable split manifest, ROC/metric JSON, or verifier observed. | Support-only code-public diffusion MIA reference. |
| MIA_SD bachelor-thesis repo | `osquera/MIA_SD` | Metadata and README are public. The tree exposes `attack_model.ipynb`, `dtu-400-target-loss.csv`, many training/validation PGF files, and result-like pkl/ROC/confusion-matrix files under `images_attack_model`. | Result-like artifacts exist, but the public surface does not expose an immutable audit target/split manifest, score schema, metric JSON, checkpoint identity, or no-training verifier tying those artifacts to DiffAudit row-bound admission. | Support-only thesis artifact surface; possible false-promotion pressure, not admitted evidence. |

## Decision

This pass found no new public row-bound diffusion MIA score or response packet.
It does not change C14, the external denominator count, admitted evidence, or
compute policy:

- C14 selected stress rows remain `13`.
- Post-C14 expansion queue remains `0`.
- Targeted post-queue discovery candidates checked across the two 2026-06-08
  passes now total `13`.
- Directly freezable external denominator rows remain `0`.
- `active_gpu_question = none`.
- `next_gpu_candidate = none`.
- `CPU sidecar = none selected`.

The closest fresh pressure point in this pass is `osquera/MIA_SD`, because it
commits result-like files. A small-file follow-up is recorded in
[`e2_miasd_result_file_preflight_2026_06_08.md`](e2_miasd_result_file_preflight_2026_06_08.md):
the visible CSV is a training-loss time series, the source notes provide only
DTU/AAU provenance hints, and the result-like pickle/ROC files lack a public
schema, immutable row IDs, checkpoint identity, metric JSON, and verifier. The
row therefore cannot become admitted evidence or an N50 denominator candidate in
the current state.

## Stop Rule

Do not run or download LSA-Probe, MIAGM, Memorization-LDM, Health Privacy
Challenge, SecMI, Reconstruction-based Attack, GSA, FSECLab MIA-Diffusion, or
MIA_SD from this pass. Reopen only if a public source exposes target identity,
immutable member/nonmember row IDs, row-bound score/response artifacts, metric
provenance, and a no-training verifier.
