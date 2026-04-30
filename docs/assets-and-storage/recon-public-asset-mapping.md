# Recon Public Asset Mapping

This document records the current semantic mapping for the public `recon` asset bundle, to avoid treating filenames as confirmed paper ground truth.

Public asset bundle source:

- DOI: `10.5281/zenodo.13371475`

Local root directory:

- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/`

Derived mapping notes also exist at:

- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-public-10/mapping-note.md`
- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-public-25/mapping-note.md`
- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-public-50/mapping-note.md`
- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-public-100/mapping-note.md`

## Current Mapping

- `target_member`
  - `source-datasets/partial-100-target/member/dataset.pkl`
- `target_non_member`
  - `source-datasets/partial-100-target/non_member/dataset.pkl`
- `shadow_non_member`
  - `source-datasets/100-shadow/non_member/dataset.pkl`
- `shadow_member`
  - currently proxied by `source-datasets/100-target/non_member/dataset.pkl`

## Why This Mapping

First, `partial-100-target` is the only public data directory that explicitly provides both `member/` and `non_member/` subdirectories for the target split. It is the only source that directly supports the target-member / target-non-member binary division.

Second, `100-shadow` currently only contains `non_member/` with no sibling `member/` directory. It can only directly serve as `shadow_non_member`.

Third, `100-target/non_member` is not a clean `shadow_member` by naming. It is the closest available proxy for the shadow positive class in the current public bundle. Treating it as `shadow_member` is an engineering placeholder, not a confirmed paper-level assignment.

Fourth, checkpoint naming supports two axes -- "target / shadow" and "partial / full":

- `celeba_partial_target`
- `celeba_target`
- `celeba_partial_shadow`
- `celeba_shadow`

But the public dataset directories do not provide a clean four-quadrant split that maps one-to-one to these checkpoints. The current mapping is the most conservative option available; it does not claim that "target/shadow/member/non-member four-way semantics are fully confirmed."

Fifth, the `derived-public-*` directories' `mapping-note.md` files explicitly record the mapping used by the current run chain as:

- `target_member`
- `target_non_member`
- `shadow_non_member`
- `shadow_member_proxy`

This means the current semantics are recorded as part of the local derived assets, not an informal verbal agreement. But because it still says `shadow_member_proxy`, it supports "locally constrained semantics" only, not a full paper-level confirmation.

## Current Conclusion

- Reasonable to claim: the public bundle supports a `Stable Diffusion + DDIM` `10-sample public runtime-mainline`, and a minimal real `runtime-mainline` for `kandinsky_v22`
- Reasonable to claim: the current `derived-public-{10,25,50,100}` directories all carry consistent local mapping notes, so the existing `recon` main evidence chain is "semantically constrained but locally consistent"
- Not reasonable to claim: the public bundle is strictly aligned with the paper's full target/shadow/member/non-member semantics
- After issue #10, strict paper-faithful `Attack-I` entry must use `check-recon-stage0-paper-gate`; the current gate result is `blocked / paper_aligned_semantics = false`

## Recommended Approach

1. `1-sample` and smaller smoke tests can continue using the current mapping, to validate the system and run chain.
2. Before scaling to larger samples, explicitly note in reports that `shadow_member` is still a proxy.
3. For strict paper-faithful `Attack-I`, run `check-recon-stage0-paper-gate` first. When the gate returns `blocked`, do not write results as paper-aligned.
4. If more complete split documentation or supplementary assets become available later, update this document. Do not silently swap mappings in commands.
