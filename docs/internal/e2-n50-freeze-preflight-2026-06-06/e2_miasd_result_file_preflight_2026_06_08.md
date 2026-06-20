# MIA_SD Result-File Preflight

> Date: 2026-06-08
> Mode: small-file and metadata-only follow-up
> Decision: result-like files are public, but no row-bound audit packet is visible

## Scope

`osquera/MIA_SD` was the closest pressure point in the 2026-06-08 targeted
discovery pass because it commits result-like files rather than only source
code. This follow-up checks whether those visible files can plausibly become an
E2 denominator row or a second public response/score asset.

The check is intentionally narrow. It reads GitHub content metadata, the first
rows of the small CSV, and two small `_SOURCE.md` notes. It does not clone the
repository, download or unpickle result objects, run notebooks, execute code,
download embeddings, scrape DTU/AAU/LFW data, or inspect generated media.

## Observations

| Surface | Evidence observed | Missing surface |
| --- | --- | --- |
| `dtu-400-target-loss.csv` | GitHub reports `739,016` bytes, SHA `54dde32938040de2128dbf2f48854810d3a132f4`. The raw header is `Step`, `swept-galaxy-5 - train_loss`, `train_loss__MIN`, and `train_loss__MAX`. | This is a training-loss time series, not per-row membership score rows or a member/nonmember score schema. |
| `images_attack_model/DTU_gen_vs_AAU_v1/SD15_v1/_SOURCE.md` | The note says the images were taken from DTU, upscaled, cropped to `512x512`, and used to finetune SD1.5. | It gives a source/procedure summary but no immutable row IDs, target checkpoint hash, split manifest, or verifier. |
| `images_attack_model/DTU_gen_vs_AAU_v1/aau/_SOURCE.md` | The note says the AAU images were scraped and not preprocessed. | It gives a nonmember-source hint but no immutable row IDs, split manifest, or score/response schema. |
| `images_attack_model/DTU_vs_AAU_test/` | Metadata lists `CLIP_results.pkl` (`44,629` bytes), `results.pkl` (`182,825` bytes), `confusion_matrix.pgf`, and `roc_auc.pgf`. | Result-like files exist, but no public schema, row IDs, checkpoint identity, metric JSON, or no-training verifier ties them to a DiffAudit-admissible packet. |
| `images_attack_model/DTU_vs_AAU_unseen_test/` | Metadata lists `CLIP_results.pkl` (`41,629` bytes), `results.pkl` (`172,064` bytes), `confusion_matrix.pgf`, and `roc_auc.pgf`. | Same blocker: result-like files without a row-bound schema, immutable split manifest, checkpoint identity, metric JSON, or verifier. |

## Decision

This follow-up does not upgrade `MIA_SD`.

The repository remains a useful false-promotion pressure surface because it has
public source notes and result-like artifacts. It is still not a row-bound audit
packet: the visible files do not provide immutable member/nonmember row IDs, a
target checkpoint hash, a score schema, metric provenance, or a no-training
verifier. Therefore it remains support-only / possible false-promotion pressure,
not C14, not an external denominator row, not admitted evidence, not a second
independent response/score asset, and not a compute-release target.

## Stop Rule

Do not download `gen_emb.npy`, `neg_emb.npy`, `pos_emb.npy`, pickle files,
notebooks, generated images, DTU/AAU/LFW data, or SD checkpoints for this row.
Reopen only if the public repository or another official surface adds an
immutable row manifest plus score/response schema and a verifier that can be
checked without target retraining or private data reconstruction.
