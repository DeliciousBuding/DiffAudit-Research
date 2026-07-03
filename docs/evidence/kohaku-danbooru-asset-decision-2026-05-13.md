# Kohaku / Danbooru Asset Decision

Date: 2026-05-13

## Question

Can `KBlueLeaf/Kohaku-XL-*` plus Danbooru/HakuBooru become the next true
second-asset response contract after weak CommonCanvas results?

## Probe

Used Hugging Face metadata and small model-card/config reads only. No large
weights or image archives were downloaded.

Observed:

- `KBlueLeaf/Kohaku-XL-Epsilon`: public, not gated, about `38.244 GB` across
  `231` files.
- `KBlueLeaf/Kohaku-XL-Delta`: public, not gated, about `40.039 GB` across
  `280` files.
- `KBlueLeaf/danbooru2023-metadata-database`: `gated=auto`, about `47.261 GB`.
- `KBlueLeaf/danbooru2023-webp-4Mpixel`: `gated=auto`, about `1662.101 GB`.
- `nyanko7/danbooru2023`: public, about `8751.139 GB`.

The model cards state that Kohaku XL Delta/Epsilon were trained from
HakuBooru selections over Danbooru2023, with millions of images and described
ID ranges. They do not expose a concrete per-image member list or an exact
fixed-seed selection artifact sufficient to build a clean member/nonmember
split.

## Decision

Do not release a GPU experiment or large download for Kohaku/Danbooru now.

The candidate is scientifically interesting but not clean enough for the next
DiffAudit decision because membership would be inferred from broad dataset and
ID-range descriptions rather than a verified target member list. That would
repeat the pseudo-membership mistake already seen in Beans/SD1.5.

Reopen only if one of these appears:

- A reproducible HakuBooru selection manifest for the exact Kohaku target.
- A small verified subset that explicitly labels target members and
  nonmembers.
- A paper or dataset package with a target-model membership split rather than
  only broad training-source provenance.

## Next

Keep the current Research state at `no selected GPU candidate`. The next valid
move remains either a genuinely different mechanism or a genuinely cleaner
asset/response contract.
