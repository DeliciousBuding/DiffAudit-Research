# CLiD Identity Manifest Gate

> Date: 2026-05-15
> Status: identity-manifest-missing / gated-zip-inaccessible-with-auth / score-rows-numeric-only / candidate-only / no download / no GPU release / no admitted row

## Question

Can the official `zhaisf/CLiD` score packet be promoted from strong
prompt-conditioned candidate evidence to an image-identity-safe DiffAudit
artifact using only public-safe metadata?

This gate checked the official GitHub tree, README/script references, public
intermediate-output file structure, Hugging Face dataset metadata, and
authenticated HEAD/Range probes against the gated dataset ZIP. It did not
download `mia_COCO.zip`, images, Stable Diffusion weights, target/shadow
checkpoints, generated outputs, or any GPU artifact.

## Public Surface Checked

| Surface | Evidence |
| --- | --- |
| GitHub repository | `https://github.com/zhaisf/CLiD` |
| Default branch | `main` |
| Latest push observed | `2025-09-15T12:24:56Z` |
| License | Apache-2.0 |
| Public tree shape | `README.md`, evaluator scripts, attack/training scripts, poster image, `train_sh/ft_mia.sh`, and numeric `inter_output/*` files |
| Missing in public tree | no committed `json`, `jsonl`, `csv`, manifest, `data/impt_metadata`, COCO image-id list, caption list, or row-id map |
| HF dataset | `zsf/COCO_MIA_ori_split1`, `private=false`, `gated=auto`, `sha=4af0207c955c893a49b7c2970db5ada414b37ed2`, `lastModified=2025-01-04T07:57:18.000Z` |
| HF siblings | `.gitattributes` (`2,307` bytes), `README.md` (`871` bytes), `mia_COCO.zip` (`1,620,731,171` byte LFS object, `sha256=7b78861d38b07a9593f2615418ccde8b8d06cd9d8a6990496169a7d7a89ee587`) |
| HF storage | `usedStorage=4,873,649,351` bytes |
| Auth state | `hf auth whoami` in `diffaudit-research` confirmed an authenticated user |
| ZIP access with auth | authenticated `HEAD` and `Range: bytes=0-1023` returned `403 Forbidden`; unauthenticated probes returned `401 Unauthorized` |

## Row Identity Findings

The public score files are numeric-only score tables. They do not contain
headers, row IDs, COCO image IDs, captions, file names, URLs, split IDs, or any
other durable identity field.

Representative public output structure:

| File | Lines | Columns | Parse result | First row shape |
| --- | ---: | ---: | --- | --- |
| `inter_output/CLID/Atk_Impt_M_coco_real_ori_DATA_val17_TRTE_train_MAXsmp_3_T_0506_145842.txt` | `2,500` | `5` | all floats | `loss + 4 condition scores` |
| `inter_output/CLID/Atk_Impt_M_coco_real_ori_DATA_val17_TRTE_test_MAXsmp_3_T_0506_145842.txt` | `2,500` | `5` | all floats | `loss + 4 condition scores` |
| `inter_output/CLID/Atk_Impt_M_coco_real_split1_DATA_val17_split1_TRTE_train_MAXsmp_3_T_0506_145909.txt` | `2,500` | `5` | all floats | `loss + 4 condition scores` |
| `inter_output/CLID/Atk_Impt_M_coco_real_split1_DATA_val17_split1__TRTE_test_MAXsmp_3_T_0506_145909.txt` | `2,500` | `5` | all floats | `loss + 4 condition scores` |
| `inter_output/PIA/Atk_pia_M_coco_real_ori_DATA_val17_TRTE_train_T_0510_172145.txt` | `2,500` | `1` | all floats | scalar PIA score |
| `inter_output/SecMI/Atk_sec_M_coco_real_ori_DATA_val17_TRTE_train_T_0510_172145.txt` | `2,500` | `1` | all floats | scalar SecMI score |
| `inter_output/PFAMI/Atk_fluc_M_coco_real_ori_DATA_val17_TRTE_train_T_0518_160926.txt` | `2,500` | `1` | all floats | scalar PFAMI score |

The official evaluators call `f.readlines()[1:]`, so the replayable packet has
`2,499` member rows and `2,499` nonmember rows per target/shadow split under the
official script convention. That convention still does not recover identity
because the skipped first line is also numeric, not a header.

## Script and Dataset Findings

- `README.md` points target/shadow fine-tuning to the HF dataset and states that
  the repository provides intermediate MS-COCO validation results.
- `train_sh/ft_mia.sh` keeps both `TRAIN_DIR` and `dataset_name` as
  `xxxxxxxxxxx`, so the public shell entrypoint does not identify the exact
  target/shadow split names or row order.
- `mia_CLiD_impt.py` references local metadata files such as
  `data/impt_metadata/dealed_coco_imp_metadata.jsonl`, but the public GitHub
  tree does not contain `data/impt_metadata/` or any equivalent metadata file.
- The attack scripts use dataset-name dictionaries and data paths as
  placeholders, not public immutable split manifests.
- The HF dataset card says the dataset was randomly selected from MS-COCO and
  processed for the CLiD code, but the only data-bearing sibling is the gated
  ZIP. The public dataset README does not publish image IDs, captions, row
  order, split hashes, or a manifest preview.
- Because authenticated HEAD/Range requests returned `403`, this cycle could
  not list the ZIP central directory or inspect whether it contains metadata
  files without downloading the dataset.

## Decision

`identity-manifest-missing / gated-zip-inaccessible-with-auth /
score-rows-numeric-only / candidate-only / no download / no GPU release / no
admitted row`.

The official CLiD replay remains a strong candidate signal, but it still cannot
be promoted into DiffAudit Platform/Runtime admitted evidence. The public score
packet establishes train-vs-test score separability under the authors'
prompt-conditioned MS-COCO real-world setting, not an image-identity-safe
consumer artifact. DiffAudit cannot bind the replayed rows to immutable COCO
image IDs, captions, or a public member/nonmember manifest from the currently
available public metadata.

Smallest valid reopen condition:

- Authors publish a manifest mapping each `inter_output/*` row to immutable
  COCO image identity, caption/text, target/shadow split, and member/nonmember
  role; or
- HF gated access becomes available and a metadata-only ZIP central-directory
  or manifest inspection exposes the same row binding without downloading image
  payloads; and
- A product-bridge handoff defines how the prompt-conditioned CLiD contract
  differs from the admitted `recon` black-box row.

Stop condition:

- Do not download `mia_COCO.zip`, `COCO_MIA_ori_split1`, images, SD weights,
  target/shadow checkpoints, or generated images in the current cycle.
- Do not run CLiD GPU jobs, XGBoost sweeps, prompt-shuffle matrices, or new
  prompt-control experiments from this gate alone.
- Do not change Platform/Runtime admitted rows, recommendation logic, product
  copy, report schemas, or machine-readable admitted bundles.

## Platform and Runtime Impact

None. CLiD remains Research-only candidate evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
