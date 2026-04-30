# DiffAudit Research Download Current Status

> Updated: `2026-04-15`
> Scope: only assets that are already local, currently being handled by Codex, or may still require user-side manual web actions.

---

## 1. 已确认归档完成

### 1.1 SecMI OneDrive 权重包

- 原始压缩包已归档到：
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\supplementary\secmi-onedrive\raw\OneDrive_1_2026-4-15.zip`
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\supplementary\secmi-onedrive\raw\OneDrive_1_2026-4-15-duplicate.zip`
- 已解压到：
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\weights\secmi-cifar-bundle\CIFAR10\`
  - `<DIFFAUDIT_ROOT>\\Download\\gray-box\weights\secmi-cifar-bundle\CIFAR100\`
- 已确认解压结果包含：
  - `checkpoint.pt`
  - `flagfile.txt`
- 状态：`ready`

官方链接（已拿到，不需要再下）：

- SecMI OneDrive bundle:
  `https://drexel0-my.sharepoint.com/:f:/g/personal/jd3734_drexel_edu/EnVid-empkpNvzC_mOfHwv0BpgkDsB_C4RmHO4rIH8BSzw?e=c17NjE`

### 1.2 CLID_MIA supplementary 包

- 原始压缩包已归档到：
  - `<DIFFAUDIT_ROOT>\\Download\\black-box\supplementary\clid-mia-supplementary\raw\1311_Membership_Inference_on_T_Supplementary_Material.zip`
- 已解压到：
  - `<DIFFAUDIT_ROOT>\\Download\\black-box\supplementary\clid-mia-supplementary\contents\CLID_MIA\`
- 已确认内容包括：
  - `cal_clid_th.py`
  - `cal_clid_xgb.py`
  - `mia_SEC_PIA.py`
  - `inter_output\CLID\`
  - `inter_output\PFAMI\`
  - `inter_output\PIA\`
  - `inter_output\SecMI\`
- 状态：`ready`

### 1.3 共享数据集与基础权重

以下资产已确认本地存在：

- CIFAR-10：
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\cifar-10-python.tar.gz`
- CelebA 主图像包：
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\celeba\img_align_celeba.zip`
- CelebA 标注与分割文件：
  `<DIFFAUDIT_ROOT>\\Download\\shared\datasets\celeba\`
- OpenAI CLIP ViT-L/14：
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\clip-vit-large-patch14\`
- Google DDPM CIFAR-10 32：
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\google-ddpm-cifar10-32\`
- Stable Diffusion v1.5：
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\stable-diffusion-v1-5\`
- BLIP image captioning large：
  `<DIFFAUDIT_ROOT>\\Download\\shared\weights\blip-image-captioning-large\`

---

## 2. Assets Handled By The Research Workflow

以下项目属于 GitHub / Hugging Face / repository workflow 可以自动处理或由团队资产镜像提供的范围：

- GitHub 代码仓库本身
  - `Reconstruction-based-Attack`
  - `localizing_memorization_in_diffusion_models`
  - 以及后续需要的其他公开 GitHub repo
- Hugging Face 非人工门槛模型
  - `openai/clip-vit-large-patch14`
  - `google/ddpm-cifar10-32`
  - `Salesforce/blip-image-captioning-large`
  - `laion/CLIP-ViT-L-14-laion2B-s32B-b82K`
- 已进入 local staging 的整理、解压、归档工作

当前判断：

- `stable-diffusion-v1-5` 已完成本地落盘；
- `blip-image-captioning-large` 已完成本地落盘；
- 当前没有新的首波 Hugging Face 权重缺口需要人工处理。

---

## 3. Assets That May Require Manual Web Confirmation

当前不是立刻必须；只有在自动拉取失败或上游要求网页许可确认时，才需要人工处理：

### 3.1 Stable Diffusion v1.5 网页许可确认

用途：

- 黑盒 `CLiD` / SD1.5 相关路线需要基础模型

直达链接：

- `https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5`

当前状态：

- 本地下载已完成；新成员只需要从团队资产镜像同步，或按上游许可重新下载。

仅当未来再次出现以下情况时才需要你手动处理：

- Hugging Face CLI 因 license / gated restriction 无法补齐文件
- 本地最终仍缺 `vae/` 或其他核心权重目录

建议落盘位置：

- `<DIFFAUDIT_ROOT>\\Download\\shared\weights\stable-diffusion-v1-5\`

---

## 4. 当前结论

- `OneDrive` SecMI 权重包已经归档并解压到 canonical `Download/` 位置。
- `1311_Membership_Inference_on_T_Supplementary Material.zip` 已归档并解压到 canonical `Download/` 位置。
- GitHub 代码仓库属于 `Research/external/` clone 或 vendored-code 管理范围，不属于手工下载资产清单。
- 当前没有新的 first-wave `OneDrive / Google Drive` 手工下载缺口。
- 后续如出现必须人工网页确认的 gated asset，应在本文件或
  [research-download-master-list.md](research-download-master-list.md) 中记录直达链接、许可说明和目标落盘路径。


