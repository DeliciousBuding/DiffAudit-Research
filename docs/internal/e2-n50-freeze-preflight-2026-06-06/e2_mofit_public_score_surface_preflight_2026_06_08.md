# MoFit Public Score-Surface Preflight

> Date: 2026-06-08
> Mode: no-clone metadata plus small public text replay
> Decision: notable support/candidate surface; not admitted evidence

## Scope

`JoonsungJeon/MoFit` surfaced during a targeted search for current public
diffusion MIA artifacts. Unlike most code-only repositories checked in this
cycle, MoFit commits compact COCO result text files and caption files. This
preflight asks whether that public surface supplies any part of Direction A's
missing row-bound public score/response asset requirement.

The check reads GitHub repository metadata, README text, recursive path names,
small result text files, caption JSONL headers, and the public evaluation
script. It does not clone the repository, download images, download numpy
embedding/noise arrays, run MoFit optimization, load checkpoints, unpickle
objects, run notebooks, or use GPU/DCU compute.

## Public Surface

MoFit is the official implementation of the ICLR 2026 paper "No Caption, No
Problem: Caption-Free Membership Inference via Model-Fitted Embeddings." The
public repository was checked at:

- repo: `https://github.com/JoonsungJeon/MoFit`
- default branch: `main`
- latest pushed timestamp observed by GitHub metadata: `2026-05-27T08:05:53Z`

The README states that MoFit supports COCO, Flickr, Pokemon, and LAION-mi, and
that `Eval/calculate_pred.py`, `Eval/mia_th_COCO.py`, and
`Eval/mia_th_Pokemon.py` compute prediction values and MIA performance. It also
points COCO to the Hugging Face dataset `zsf/COCO_MIA_ori_split1`.

## Evidence Observed

| Surface | Observation | Boundary |
| --- | --- | --- |
| `Results/COCO/COCO_emb_500images_train_t_[140].txt` | Public text file, `13,690` bytes, Git blob SHA `6f6dde8940ba162055bb6118053eb4c575c190d6`, `500` numeric rows after the header. | Header records a local/private target path (`/mnt/nas5/.../sd-COCO-checkpoint-3`); rows have no explicit row IDs. |
| `Results/COCO/COCO_emb_500images_test_t_[140].txt` | Public text file, `13,797` bytes, Git blob SHA `75918cee48e68758a97bc7744cbb065a77505312`, `500` numeric rows after the header. | Same blocker: local/private target path, numeric rows without explicit row IDs. |
| `Results/COCO/COCO_blip_500images_train_t_[140].txt` | Public text file, `29,027` bytes, Git blob SHA `580dca642bafe6bc53735c98cc7a252199348a04`, `500` numeric rows after the header. | Used by the official script as VLM baseline/fusion input; no explicit row IDs in the result rows. |
| `Results/COCO/COCO_blip_500images_test_t_[140].txt` | Public text file, `29,531` bytes, Git blob SHA `ccfb53fd7f198d8196988a618a7c08bfafd3df5a`, `500` numeric rows after the header. | Same row-ID blocker. |
| `data/Captions/COCO/blip2_members_2500_captions.jsonl` | Public JSONL, `179,789` bytes, Git blob SHA `c04b46f1d95daf1547e71e894d511d8d39708e6d`; rows contain `filename` and `caption`. | The captions provide filename IDs, but the result text rows do not explicitly include those IDs. |
| `data/Captions/COCO/blip2_non_members_2458_captions.jsonl` | Public JSONL, `177,451` bytes, Git blob SHA `5740b8ed2691e83fbf59c5f3622a9d77e71652ef`; rows contain `filename` and `caption`. | Same: possible row-binding lead, not a manifest-certified score table. |

The public `data/` directory also contains five small `rnd_noise_*.npy` files,
but this preflight did not download or inspect numpy payloads.

## Metric Replay

Using the public `Eval/mia_th_COCO.py` logic, a CPU-only replay was performed on
the four public COCO text files:

1. read the `COCO_emb_*` train/test files and take `e[-2]` as the MoFit value;
2. read the `COCO_blip_*` train/test files and take `-e[-2]` as the VLM value;
3. fit `RobustScaler` on train+test for each value family;
4. sweep `alpha` over `0, 0.05, ..., 1.0`;
5. select the row with highest ASR and then highest AUC.

The public script uses the same `e[-2]` / `-e[-2]` column convention,
train+test `RobustScaler` fitting, and `np.arange` threshold sweep. The replay
therefore checks the public text surface, not a new attack variant.

Replay result:

| Rows | Best alpha | ASR | AUC | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| COCO 500 member / 500 nonmember | `0.55` | `0.883` | `0.941948` | `0.488` | `0.324` |

The bounded replay is now captured as a small-file network verifier:

```powershell
python -X utf8 scripts\replay_mofit_public_coco_scores.py --check
```

That helper only fetches the four public COCO text files, verifies their
byte-level hashes, row counts, and column counts, then recomputes the public
threshold sweep. It does not admit MoFit into the evidence contract or release
compute.

The low-FPR readouts use max TPR under the stated FPR budget, matching the
paper's finite-tail rule. With `500` nonmember rows, `1%` corresponds to `5`
false positives and `0.1%` is a zero-FP strict tail because the false-positive
budget is `0.5` rows.

The current DiffAudit-side verifier also records two CPU-only controls over the
implicit public score-file positions: a `1000`-sample row bootstrap gives mean
AUC `0.943795` with 95% interval `[0.929991, 0.955904]`, and a `1000`-sample
label-permutation null gives mean AUC `0.500805` with 95% interval
`[0.465629, 0.535924]` and empirical `p = 0.000999` for AUC at least the
observed value. These controls show the public score vectors are not behaving
like a random label assignment under the replayed scoring rule. They are still
implicit-position controls, not official upstream row-bound controls, external
labels, target identity, or surface-delta evidence.

The same verifier now also fetches the two small public caption JSONL files and
emits `data/mofit_public_caption_position_manifest.csv` for the first `500`
train/test score positions. Each row records the implicit score-file position,
score-file line numbers, caption JSONL line number, public caption filename,
caption row hash, and caption text hash. This is a candidate order anchor only:
the score rows still do not embed those caption IDs, and the official score
files still do not certify the row-to-caption binding.

This is a self-consistent public metric replay on compact text files. It is not
yet an admitted DiffAudit row.

## Admission Boundary

MoFit is a notable public score-surface lead found in the current
post-C14 discovery cycle, but the current public surface still misses several
DiffAudit gates:

- target identity is incomplete because the score headers and scripts point to
  local checkpoint paths such as `/mnt/nas5/.../sd-COCO-checkpoint-3` or
  `path/to/ckpts/sd-MSCOCO-checkpoint`;
- result rows are numeric arrays without explicit row IDs;
- row binding to `data/Captions/COCO/*.jsonl` is plausible by order and now has
  a DiffAudit-side candidate caption-order manifest, but it is not
  manifest-certified in the result files;
- the metric JSON/ROC/checker files are DiffAudit-generated from public text
  files, not upstream-provided official verifier artifacts;
- label-permutation and bootstrap controls exist only as DiffAudit-side
  implicit-position checks; no surface-delta control packet was observed.

Decision: `MoFit` becomes a bounded support/candidate surface for E1/E2
follow-up. It does not change C14, does not create a directly countable N50
external denominator row, does not become admitted evidence, and does not
release GPU/DCU compute.

## Follow-Up Gate

Reopen this as a possible second public score asset only if one of the following
becomes available or can be verified without private reconstruction:

- an immutable public checkpoint identity for `sd-COCO-checkpoint-3`;
- a manifest that maps each of the `500` score rows to public member/nonmember
  row IDs;
- a compact metric JSON/ROC packet or verifier that recomputes the reported
  AUC and low-FPR values from the public text files;
- official or manifest-certified row-bound controls, plus a surface-delta
  boundary.

Until then, keep it as public score-surface support and possible
false-promotion pressure, not paper-admitted evidence.
