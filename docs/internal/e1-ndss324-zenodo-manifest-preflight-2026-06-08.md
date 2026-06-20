# E1 NDSS-324 Zenodo Manifest Preflight

> Date: 2026-06-08
> Scope: manifest-first check for `Black-box Membership Inference Attacks against Fine-tuned Diffusion Models` as a possible second public response/score asset.
> Decision: compute-gated candidate only; no admitted row, no C14/N50 row, and no GPU job yet.

## Sources Checked

Primary sources:

- NDSS paper PDF: `https://www.ndss-symposium.org/wp-content/uploads/2025-324-paper.pdf`
- GitHub repository: `https://github.com/py85252876/Reconstruction-based-Attack`
- Zenodo record/API: `https://zenodo.org/records/13371475`, `https://zenodo.org/api/records/13371475`
- Zenodo archive file: `extra_data-20240825T145405Z-001.zip`

Live identifiers recorded in this check:

| Surface | Value |
| --- | --- |
| GitHub repository | `py85252876/Reconstruction-based-Attack` |
| GitHub default branch HEAD | `93ee8dd4d12697354cd182461a9aa268b8de63e6` |
| Zenodo DOI | `10.5281/zenodo.13371475` |
| Zenodo file size | `736,366,195` bytes |
| Zenodo file checksum | `md5:a52e197025c54c197b00674d398f2f6a` |
| Zenodo file last modified | `2025-11-10T02:51:29Z` from HTTP header |
| Local ZIP path | `Download/shared/supplementary/ndss-2025-324-blackbox-mia-20260608/extra_data-20240825T145405Z-001.zip` |
| Local ZIP MD5 | `A52E197025C54C197B00674D398F2F6A`, matches Zenodo |
| Local ZIP SHA-256 | `ADB63E025238347BF219A001DAD32BBCC92312CA5BE86CCA0A70F1AF0D2D7098` |
| ZIP integrity check | `zipfile.testzip() -> None` |
| Local NDSS PDF SHA-256 | `3A8A3B411D13A2BDD8E8F133878788EF0E9C1278A01B67A23D5BBDB9724623E5` |
| ZIP central-directory entries | `21` |
| ZIP central directory size/offset | `5,212` bytes at offset `736,360,961` |
| Local GitHub clone HEAD | `93ee8dd4d12697354cd182461a9aa268b8de63e6` |

The central-directory rows are recorded in
[`e1-ndss324-zenodo-manifest-preflight-2026-06-08.csv`](e1-ndss324-zenodo-manifest-preflight-2026-06-08.csv).

## What Changed

This candidate is stronger than ordinary code-only surfaces. The paper's
artifact appendix says the artifact package contains fine-tuned LoRA modules,
datasets, BLIP checkpoints, and score vectors for target member, target
nonmember, shadow member, and shadow nonmember samples. The Zenodo current
record is open and the ZIP central directory confirms public target/shadow
LoRA checkpoints plus member/nonmember dataset files.

However, the current ZIP central directory does **not** expose any score-vector,
ROC, metric JSON, generated image, or verifier file. The only visible archive
entries are checkpoint states, LoRA/optimizer/scheduler files, one BLIP README,
and four dataset PKLs. The appendix claim that score vectors are stored in the
artifact package is therefore not satisfied by the current public central
directory.

## Bounded Full-ZIP Probe

The 2026-06-08 bounded artifact probe downloaded the full Zenodo ZIP under
`Download/shared/supplementary/`, verified the Zenodo MD5, recorded a local
SHA-256, and ran `zipfile.testzip()` successfully. This resolved the question
of archive availability, but it did not resolve the manifest gate.

The four `dataset.pkl` entries are nested torch ZIP payloads whose first inner
file is `dataset/data.pkl`. A static probe over the decompressed pickle streams
found only dataset-level `image` and `text` keys plus PIL image construction
globals; it did not find `id`, `file_name`, or `image_id` keys. No unrestricted
`torch.load` or `pickle.load` was used for this probe.

| Dataset entry | Inner payload | Static keys/globals observed | Identifier fields observed | Gate implication |
| --- | --- | --- | --- | --- |
| `extra_data/dataset/partial-100-target/non_member/dataset.pkl` | `dataset/data.pkl`, `449,003,695` bytes | `image`, `text`; `PIL.Image Image`; `_codecs encode` | none among `id`, `file_name`, `image_id` | Directory-level nonmember label only; no immutable row id. |
| `extra_data/dataset/100-target/non_member/dataset.pkl` | `dataset/data.pkl`, `449,003,695` bytes | `image`, `text`; `PIL.Image Image`; `_codecs encode` | none among `id`, `file_name`, `image_id` | Still not a confirmed shadow-member split; only a possible local proxy. |
| `extra_data/dataset/100-shadow/non_member/dataset.pkl` | `dataset/data.pkl`, `444,081,007` bytes | `image`, `text`; `PIL.Image Image`; `_codecs encode` | none among `id`, `file_name`, `image_id` | Shadow nonmember label is directory-level only. |
| `extra_data/dataset/partial-100-target/member/dataset.pkl` | `dataset/data.pkl`, `441,846,383` bytes | `image`, `text`; `PIL.Image Image`; `_codecs encode` | none among `id`, `file_name`, `image_id` | Target member label is directory-level only. |

The public source code matches this finding. `train_text_to_image_lora.py`,
`inference.py`, `build_caption.py`, and `cal_embedding.py` load datasets with
`torch.load(...)` and then build a HuggingFace `Dataset.from_dict(...)`.
`cal_embedding.py` and `test_accuracy.py` expect score files to be generated
separately; those generated score files are not present in the Zenodo ZIP.

## Six-Gate Preflight

| Gate | Status | Evidence |
| --- | --- | --- |
| Target identity | `Partial` | Zenodo exposes CelebA target/partial-target/shadow LoRA checkpoints under `checkpoint-25000`, but no compact model card binds the base model, training split, and checkpoint roles into a paper-faithful manifest. |
| Split labels | `Fail` | Directory names expose partial target member/nonmember and shadow nonmember PKLs, but the static full-ZIP probe found no immutable row-id fields and the public four-quadrant target/shadow member/nonmember split is incomplete. |
| Score/response packet | `Fail` | No score-vector, generated-response, ROC, metric JSON, or verifier file appears in the 21-entry central directory or full ZIP probe. |
| Metric provenance | `Partial` | GitHub code exposes `cal_embedding.py` and `test_accuracy.py`; the code can generate score files, but no no-training metric packet or row-score join is public. |
| Consumer boundary | `Partial` | The paper targets black-box MIA against fine-tuned diffusion models, but the current public package can only support a local proxy semantics chain, not a paper-aligned no-training audit row. |
| Surface delta | `Pass` | Non-adjacent to current H2/PIA/GSA rows: fine-tuned Stable Diffusion LoRA, CelebA-style data, and reconstruction-distance black-box attack. |

## Decision

This is now the strongest E1 compute-gated candidate found after CopyMark and
MoFit, but it is not a public score/response asset. The full-ZIP probe moved the
blocker from "archive not locally verified" to "verified archive lacks
row-bound identifiers, complete paper-faithful split semantics, and public score
packets."

Allowed wording:

- `official checkpoint-and-split package candidate`
- `compute-gated E1 candidate`
- `not public score-vector replay`
- `not admitted evidence`

Forbidden wording:

- Do not call it a second public response/score asset.
- Do not call it admitted, N50, C14, external adjudication, or reviewer reliability evidence.
- Do not cite the paper appendix's score-vector sentence as true of the current Zenodo archive without resolving the central-directory mismatch.

## Next Gate

The next useful step is not broad searching. It is a bounded artifact probe:

1. Do not release GPU/DCU work from the current ZIP.
2. Keep the candidate as an official checkpoint-and-split package reference,
   not a public score replay.
3. Reopen only if the authors publish a compact row manifest, a complete
   paper-faithful target/shadow member/nonmember split mapping, or the missing
   score-vector/metric packet described by the paper appendix.
4. If a future manifest appears, require a label-shuffle or permutation control
   before any score-producing smoke.

No GPU/DCU job is released by this note. The candidate is worth preserving
because it may change Direction B/E1 if a future public manifest or artifact
revision exposes row identity and a feasible scoring path.
