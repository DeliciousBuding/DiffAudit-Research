# Research Download Current Status

> Updated: `2026-04-30`
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
