# Research Download Current Status

> Updated: `2026-06-08`
> Scope: only assets that are already local, currently being handled by Codex, or may still require user-side manual web actions.

---

## 1. Confirmed Archived

### 1.1 SecMI OneDrive Weights Bundle

- Original archives stored at:
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\supplementary\secmi-onedrive\raw\OneDrive_1_2026-4-15.zip`
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\supplementary\secmi-onedrive\raw\OneDrive_1_2026-4-15-duplicate.zip`
- Extracted to:
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\weights\secmi-cifar-bundle\CIFAR10\`
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\weights\secmi-cifar-bundle\CIFAR100\`
- Confirmed contents:
  - `checkpoint.pt`
  - `flagfile.txt`
- Status: `ready`

Official link (already obtained, no re-download needed):

- SecMI OneDrive bundle:
  `https://drexel0-my.sharepoint.com/:f:/g/personal/jd3734_drexel_edu/EnVid-empkpNvzC_mOfHwv0BpgkDsB_C4RmHO4rIH8BSzw?e=c17NjE`

### 1.2 CLID_MIA Supplementary Files

- Original archive stored at:
  - `<DIFFAUDIT_ROOT>\\Download\\black-box\supplementary\clid-mia-supplementary\raw\1311_Membership_Inference_on_T_Supplementary_Material.zip`
- Extracted to:
  - `<DIFFAUDIT_ROOT>\\Download\\black-box\supplementary\clid-mia-supplementary\contents\CLID_MIA\`
- Confirmed contents:
  - `cal_clid_th.py`
  - `cal_clid_xgb.py`
  - `mia_SEC_PIA.py`
  - `inter_output\CLID\`
  - `inter_output\PFAMI\`
  - `inter_output\PIA\`
  - `inter_output\SecMI\`
- Status: `ready`

### 1.3 Shared Datasets And Base Weights

The following assets are confirmed present locally:

- CIFAR-10:
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\cifar-10-python.tar.gz`
- CelebA main image archive:
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\celeba\img_align_celeba.zip`
- CelebA annotations and split files:
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\celeba\`
- OpenAI CLIP ViT-L/14:
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\clip-vit-large-patch14\`
- Google DDPM CIFAR-10 32:
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\google-ddpm-cifar10-32\`
- Stable Diffusion v1.5:
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\stable-diffusion-v1-5\`
- BLIP image captioning large:
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\blip-image-captioning-large\`

### 1.4 NDSS-324 Reconstruction-Based Attack Probe Package

The full public Zenodo ZIP for `Black-box Membership Inference Attacks against
Fine-tuned Diffusion Models` has been verified for a bounded Research probe.
It remains probe-only evidence, not an admitted paper asset.

- DOI: `10.5281/zenodo.13371475`
- Raw ZIP:
  `<DIFFAUDIT_ROOT>\\Download\\shared\supplementary\ndss-2025-324-blackbox-mia-20260608\extra_data-20240825T145405Z-001.zip`
- Size: `736,366,195` bytes
- MD5: `A52E197025C54C197B00674D398F2F6A`, matching Zenodo
- SHA-256: `ADB63E025238347BF219A001DAD32BBCC92312CA5BE86CCA0A70F1AF0D2D7098`
- ZIP integrity: `zipfile.testzip() -> None`
- Source clone for code inspection:
  `<DIFFAUDIT_ROOT>\\Download\\shared\supplementary\ndss-2025-324-blackbox-mia-20260608\Reconstruction-based-Attack`,
  HEAD `93ee8dd4d12697354cd182461a9aa268b8de63e6`
- Existing normalized local recon bundle:
  `<DIFFAUDIT_ROOT>\\Download\\black-box\supplementary\recon-assets\ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models\`

Current status:

- `archive-verified / manifest-incomplete / no GPU release`
- Static dataset probe found only `image` and `text` fields, with no immutable
  row-id fields such as `id`, `file_name`, or `image_id`.
- Existing `derived-public-*` mapping notes keep `shadow_member_proxy` explicit;
  they support local derived-proxy analysis only, not paper-faithful Attack-I
  admission.

---

## 2. Assets Handled By The Research Workflow

These items are covered by GitHub / Hugging Face / repository workflow or by the team asset mirror:

- GitHub code repositories
  - `Reconstruction-based-Attack`
  - `localizing_memorization_in_diffusion_models`
  - and any other public GitHub repos needed later
- Hugging Face models without manual gating
  - `openai/clip-vit-large-patch14`
  - `google/ddpm-cifar10-32`
  - `Salesforce/blip-image-captioning-large`
  - `laion/CLIP-ViT-L-14-laion2B-s32B-b82K`
- Staging, extraction, and archival work already done locally

Current assessment:

- `stable-diffusion-v1-5` is fully downloaded locally
- `blip-image-captioning-large` is fully downloaded locally
- No new first-wave Hugging Face weight gaps require manual handling

---

## 3. Assets That May Require Manual Web Confirmation

These are not immediately needed. They only require manual action if automatic download fails or upstream requires web-based license acceptance.

### 3.1 Stable Diffusion v1.5 Web License Confirmation

Purpose:

- Black-box `CLiD` / SD1.5 tracks need the base model

Direct link:

- `https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5`

Current status:

- Local download is complete. New members only need to sync from the team asset mirror or re-download under the upstream license.

Manual action is only needed if:

- Hugging Face CLI cannot complete the download due to license / gated restrictions
- Local copy is still missing `vae/` or other core weight directories

Recommended location:

- `<DIFFAUDIT_ROOT>\\Download\\shared\weights\stable-diffusion-v1-5\`

---

## 4. Current Conclusion

- The `OneDrive` SecMI weights bundle is archived and extracted to the canonical `Download/` location.
- `1311_Membership_Inference_on_T_Supplementary Material.zip` is archived and extracted to the canonical `Download/` location.
- GitHub code repositories are `Research/external/` clones or vendored-code management, not part of the manual download list.
- No new first-wave `OneDrive / Google Drive` manual download gaps exist.
- Any future gated assets requiring manual web confirmation should be recorded in this file or [research-download-master-list.md](research-download-master-list.md) with direct links, license notes, and target paths.

### 4.1 Black-Box Response-Contract Gap

The black-box response-contract audit found no second compatible asset family
ready for execution. The required acquisition package is now specified in
[../evidence/black-box-response-contract-asset-acquisition-spec.md](../evidence/black-box-response-contract-asset-acquisition-spec.md).

Current status:

- `Download/black-box/datasets/variation-query-set` is missing.
- SD1.5/CelebA image-to-image is locally CPU-eligible, but it is the same asset
  family as the existing simple-distance packet and does not test portability.
- A new package must provide member/nonmember query identities, response files
  or replayable endpoint contract, controlled repeats, and integrity metadata.
- No GPU task is released until the CPU preflight in the acquisition spec
  passes.

---

## 5. 2026-04-30 Local Workspace Boundary Cleanup

The Research checkout was cleaned so it no longer stores large local-only
payloads as ordinary directories.

Summary:

- moved or linked 36 local-only large paths
- covered about 75 GB of local payloads
- moved 5 misplaced raw asset paths to `Download/`
- moved 22 generated artifact paths to
  `<DIFFAUDIT_ROOT>\Archive\research-local-artifacts\2026-04-30\`
- moved 9 `outputs/` or `tmp/` scratch paths to the same local archive
- left ignored junctions in the old `Research/` locations for local
  compatibility
- kept `external/` as upstream-code clone space; large clones are review-only,
  not automatically moved

The execution manifest is local-only:

```text
<DIFFAUDIT_ROOT>\Archive\research-local-artifacts\2026-04-30\manifest.json
```

To reproduce the audit without moving anything:

```powershell
python -X utf8 scripts/audit_local_storage.py
```

Expected current result after cleanup:

- `tracked_large_files = []`
- `move_candidates = []`
- `external_clone_bloat` may list large upstream clones for review only
