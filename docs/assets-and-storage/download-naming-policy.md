# Download Naming Policy

This document answers one question:

Which directory names in `Download/` are canonical, and which are just historical source traces?

---

## 1. Summary

The current `Download/` structure is on the right track:

- `shared/ black-box/ gray-box/ white-box/ manifests/` at the top level is clear
- Raw datasets, weights, supplementary files, and papers are separated into distinct buckets

The inconsistency is not at the top level, but at the third-level asset names:

- Some directory names use **project consumption semantics**
- Some directory names use **upstream source semantics**
- Some directory names use **archive/web source semantics**

The right approach is to clarify naming rules first, then gradually fix inconsistencies:

1. Which names are canonical consumer names
2. Which names are source-trace names only
3. How to name new assets going forward

---

## 2. Canonical Rule

`Download/` naming should follow a three-layer structure:

```text
Download/
  <scope>/
    <bucket>/
      <asset-name>/
```

Where:

- `<scope>` must be one of:
  - `shared`
  - `black-box`
  - `gray-box`
  - `white-box`
- `<bucket>` must be one of:
  - `datasets`
  - `weights`
  - `supplementary`
  - `papers`
- `<asset-name>` should describe **what the asset is**, not where it came from

Recommended format:

- all lowercase
- kebab-case
- as short as reasonable
- describe the asset itself, not its download source

Examples:

- `stable-diffusion-v1-5`
- `clip-vit-large-patch14`
- `google-ddpm-cifar10-32`
- `secmi-cifar-bundle`
- `recon-assets`

---

## 3. Source Trace Rule

If a directory only preserves source provenance and is not the project's main consumption entry point, it should not pretend to be a canonical asset name.

These directories should either:

- live inside the canonical asset directory, or
- be clearly documented as source-trace / raw archive

Recommended internal structure:

```text
<asset-name>/
  raw/
  contents/
  notes/
```

Meaning:

- `raw/` -- original archives, web downloads, OneDrive zips, 7z splits
- `contents/` -- unpacked upstream content as-is
- `notes/` -- source notes, licenses, manual download notes

---

## 4. Current Canonical Names

These names are canonical and follow the right convention:

- `shared/weights/stable-diffusion-v1-5/`
- `shared/weights/clip-vit-large-patch14/`
- `shared/weights/blip-image-captioning-large/`
- `shared/weights/google-ddpm-cifar10-32/`
- `shared/datasets/celeba/`
- `black-box/supplementary/recon-assets/`
- `gray-box/weights/secmi-cifar-bundle/`

These names describe what the asset is.

---

## 5. Current Non-Canonical Or Mixed Names

These names are not wrong, but they read more like source traces than canonical asset names:

- `black-box/supplementary/clid-mia-supplementary/`
  - mixes method name with supplementary type
  - acceptable, but long
- `gray-box/supplementary/secmi-onedrive/`
  - this is a source-trace name, not a consumption name
  - it says "came from OneDrive", not "what the asset is"
- `shared/supplementary/celeba-7z-parts/`
  - this is an archive format name, not a data semantics name

The better understanding:

- `secmi-cifar-bundle/` is SecMI's canonical consumer asset
- `secmi-onedrive/` is a raw archive provenance stash
- `celeba/` is the shared dataset entry point
- `celeba-7z-parts/` is supplementary source material

---

## 6. Practical Guidance

When adding new assets, use this decision process:

1. If this is the project's actual consumption root:
   - use a canonical name
2. If this is a downloaded archive only:
   - put it under the corresponding asset directory's `raw/`
3. If this is unpacked upstream content:
   - put it under `contents/`
4. If this is web/auth/mirror documentation:
   - put it under `notes/`

Do not use these as top-level canonical asset names:

- `onedrive`
- `google-drive`
- `zip-parts`
- `manual-download`
- `hf-cache`

These words describe sources, not assets.

---

## 7. Current Project Judgment

The current `Download/` structure is already much more consistent than before and is usable.

For long-term stability, the framing should be:

- `Download/` is the correct raw intake layer
- Existing source-trace directories can stay for now
- New assets should follow the canonical naming policy going forward

In short:

- the structure is mostly right
- naming is not yet perfect
- the practical next step is to set clear rules and stop adding new inconsistencies, not to rename everything at once
