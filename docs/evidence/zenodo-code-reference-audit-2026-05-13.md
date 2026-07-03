# Zenodo Fine-Tuned Diffusion Code Reference Audit

> Date: 2026-05-13
> Updated: 2026-06-08
> Status: code-reference-found / full-probe-still-split-and-score-blocked / no GPU release

## Taste Check

This is the second and final near-term Lane A check for Zenodo
`10.5281/zenodo.13371475`. The previous cycle found a structured archive but no
manifest. This cycle asked whether public paper or code references can close
that gate without downloading the `736 MB` archive.

## Public References Checked

| Reference | Evidence |
| --- | --- |
| NDSS 2025 paper PDF | Public paper for `Black-box Membership Inference Attacks against Fine-tuned Diffusion Models`; identifies the attack family and fine-tuned diffusion setting. Source: `https://www.ndss-symposium.org/wp-content/uploads/2025-324-paper.pdf`. |
| `py85252876/Reconstruction-based-Attack` GitHub repository | Public code repository named by the paper; contains attack scripts including `test_accuracy.py`. Source: `https://github.com/py85252876/Reconstruction-based-Attack`. |

The 2026-05-13 check used only public web metadata, paper text, and source
listings. The 2026-06-08 bounded follow-up downloaded and verified the full
Zenodo ZIP, then statically inspected the nested dataset payloads without
unrestricted `torch.load` or `pickle.load`.

## What The Code Reference Adds

The public code confirms that this candidate is not just a raw Zenodo dump. It
has a concrete attack workflow around reconstruction-based scoring for
fine-tuned diffusion membership inference, and the repository gives a plausible
implementation surface for understanding the reported method.

This improves the candidate from `archive-only` to `paper-and-code-backed
archive watch`.

The 2026-06-08 source clone at
`93ee8dd4d12697354cd182461a9aa268b8de63e6` also clarified the implementation
boundary:

- `train_text_to_image_lora.py`, `inference.py`, `build_caption.py`, and
  `cal_embedding.py` load dataset payloads with `torch.load(...)` and wrap the
  result with `Dataset.from_dict(...)`.
- `cal_embedding.py` writes reconstruction-distance score files with
  `torch.save(...)`.
- `test_accuracy.py` consumes target/shadow member/nonmember score files and
  trains/evaluates the attack.

Those score files are generated outputs, not files exposed by the current
Zenodo ZIP.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial pass: paper/code context supports the fine-tuned diffusion setting, but the public references do not by themselves bind the Zenodo LoRA folders to a fully specified base-model recipe. |
| Exact member/nonmember split | Fail: no public, readable per-sample target member/nonmember manifest was found. The full-ZIP probe found only `image` and `text` fields in nested dataset payloads, with no `id`, `file_name`, or `image_id` keys. |
| Query/response or scoring contract | Fail: public code shows how to generate reconstruction-distance scores, but the current Zenodo ZIP does not ship row-level score files, generated response packets, ROC arrays, metric JSON, or a no-training verifier. |
| Download justification | Closed for bounded probe: the archive was verified, and the blocker moved from download uncertainty to missing row identity, complete split semantics, and score packet. |
| GPU release | Fail: no bounded packet has target identity, split, metric, and stop condition frozen. |

## Decision

`code-reference-found / full-probe-still-split-and-score-blocked / no GPU
release`.

Zenodo stays on Lane A watch, but this cycle does not upgrade it to
`next_gpu_candidate`. The public references are useful for provenance and
method context; they do not satisfy the membership-semantics gate.

Smallest valid reopen condition:

- A public README, appendix, issue, repository file, or small manifest maps the
  Zenodo `extra_data/dataset/...` payloads to exact target member and nonmember
  sample identities; and
- The same reference fixes the base model / LoRA training recipe enough to
  define a bounded `25/25` or `50/50` scoring packet.

Stop condition:

- Do not run LoRA scoring or GPU work unless the missing split manifest,
  immutable row IDs, and row-level score/metric packet appear. The next
  autonomous cycle should switch away from Zenodo if no new external evidence
  is found.

## Reflection

This cycle tested whether an external public reference changes the asset
decision. The 2026-06-08 follow-up tested whether the complete public ZIP
changes it. Both improve provenance and storage certainty, but not the evidence
state. The research decision remains no GPU.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
