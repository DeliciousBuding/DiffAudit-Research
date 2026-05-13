# Zenodo Fine-Tuned Diffusion Code Reference Audit

> Date: 2026-05-13
> Status: code-reference-found / split-manifest-still-missing / no download / no GPU release

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

The check used only public web metadata, paper text, and source listings. No
Zenodo archive payload, LoRA weight, dataset pickle, or generated response was
downloaded.

## What The Code Reference Adds

The public code confirms that this candidate is not just a raw Zenodo dump. It
has a concrete attack workflow around reconstruction-based scoring for
fine-tuned diffusion membership inference, and the repository gives a plausible
implementation surface for understanding the reported method.

This improves the candidate from `archive-only` to `paper-and-code-backed
archive watch`.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial pass: paper/code context supports the fine-tuned diffusion setting, but the public references do not by themselves bind the Zenodo LoRA folders to a fully specified base-model recipe. |
| Exact member/nonmember split | Fail: no public, readable per-sample target member/nonmember manifest was found. The ZIP central directory still does not expose a complete target split. |
| Query/response or scoring contract | Partial pass: public code shows a reconstruction-based attack workflow, but not a ready, manifest-backed contract tying exact Zenodo target samples to outputs or scores. |
| Download justification | Fail: the remaining missing piece is still split semantics, not compute or parser scaffolding. Full archive download would only move the blocker into opaque `dataset.pkl` inspection. |
| GPU release | Fail: no bounded packet has target identity, split, metric, and stop condition frozen. |

## Decision

`code-reference-found / split-manifest-still-missing / no download / no GPU
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

- Do not write another Zenodo scope/audit note, download the full archive, or
  run LoRA scoring unless the missing split manifest appears. The next
  autonomous cycle should switch away from Zenodo if no new external evidence
  is found.

## Reflection

This cycle tested whether an external public reference changes the asset
decision. It changes the provenance label, but not the execution state. The
research decision remains no GPU and no full download.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
