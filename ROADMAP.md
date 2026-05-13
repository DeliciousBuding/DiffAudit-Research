# DiffAudit Research Roadmap

> Last updated: 2026-05-13

## 2026-05-13 Leader Steering

> 入口约束:Researcher / Codex 在选下一条 lane 前必须先读完本节。本节覆盖下方 `Current Focus`、`Next Decision Contract`、`Current Sidecars` 中与之冲突的优先级,直至被显式撤回。

### 现状诊断

最近 48h(2026-05-11 → 2026-05-12)产出 49 份 evidence,但模型主线本体没有动:第二资产没有跑出一次真实 scoring 结果,任何一个 box 的 admitted row 都没有变化。真正发生的事情几乎全是 `contract / preflight / manifest / scout / scope / audit / reselection`,典型循环包括 I-B(4 份均 hold)、midfreq(11 份 doc 最终 `mid-band 不 dominate full/low`)、Beans/SD1.5(5 份 doc 自己证伪 split membership 语义)、SecMI / cross-box / archived gray-box(全 hold)。

这是 [AGENTS.md §五 反屎山规则](AGENTS.md) 与本文件 `Research Taste Guard` 明令禁止的"差生文具多"循环 — 在用工程复杂度伪装研究推进。

### 真正的两个抓手

1. **CopyMark / CommonCanvas**:5/12 找到的 paper-level 真实第二 membership 资产候选已经完成 response-contract 验证。`50/50` query split、`text_to_image` endpoint、`commoncanvas_xl_c.safetensors` 单 checkpoint、本机 RTX 4070 CUDA smoke、`50/50` deterministic responses 和 package probe `ready` 均已落地。pixel-distance、CLIP image-similarity、prompt-response consistency、multi-seed response stability 和条件 denoising-loss 五个单点机制均弱。该 CommonCanvas packet 默认关闭,不是 admitted evidence。
2. **tiny known-split gradient-sensitive scout**:5/12 在 `8/8` overfit 上 gradient norm 到过 `AUC = 0.734`,但 `16/64` stability gate 跌到 `0.535`;5/13 更乐观的 `64/64` oracle gradient-prototype alignment 也只有 `AUC = 0.500977` 且低 FPR 为 0。该机制 hint 已被削弱,不释放 GPU,不再跑同家族梯度变体。

### 2026-05-13 外部资产边界

Kohaku XL / Danbooru 被短探测后暂不进入实验。Kohaku Delta/Epsilon 的模型卡
确实指向 HakuBooru / Danbooru2023 训练来源,但当前公开材料只给出大规模数据
来源和 ID 段选择描述,没有可复核的逐样本 target-member 列表或 exact fixed-seed
selection artifact。权重约 `38-40 GB`,相关图像/metadata 仓从 `47 GB` 到 TB 级,
其中部分 `gated=auto`。这不是 GPU blocker,而是 membership 语义 blocker:继续
会重复 Beans/SD1.5 的 pseudo-membership 错误。除非出现精确成员清单、小型
verified split 或 paper-level target split,否则不下载大权重、不跑 Kohaku scorer。
见 [docs/evidence/kohaku-danbooru-asset-decision-20260513.md](docs/evidence/kohaku-danbooru-asset-decision-20260513.md)。

### 2026-05-13 Fashion-MNIST PIA-loss scout

为了避免继续只做外部资产卡片审查,本轮在本机 RTX 4070 上跑了一个小而干净的
second-split scout:`ynwag9/fashion_mnist_ddpm_32` + torchvision
Fashion-MNIST train/test split。`64/64` 固定 timestep epsilon-MSE PIA-style
loss 结果仍弱:`AUC = 0.535889`,`ASR = 0.570312`,`TPR@1%FPR = 0.03125`,
`TPR@0.1%FPR = 0.03125`。该 HF repo 没有 README/model card,所以 provenance
只够做 scout;结果也不支持继续 seed/timestep/size 扩展。见
[docs/evidence/fashion-mnist-ddpm-pia-loss-scout-20260513.md](docs/evidence/fashion-mnist-ddpm-pia-loss-scout-20260513.md)。

### 2026-05-13 CommonCanvas multi-seed stability scout

为避免只从 query-response 或 prompt-response 相似度角度关停 CommonCanvas,本轮
补了一个真正不同但仍 bounded 的机制问题:member prompt 是否在固定 seeds 下
生成更稳定的 response distribution。`4/4` prompts、two fixed seeds、
`clip_vit_l14_response_seed_stability_cosine` 结果仍弱:`AUC = 0.5625`,
`ASR = 0.625`,`TPR@1%FPR = 0.25`,`TPR@0.1%FPR = 0.25`。低 FPR 只恢复
`1/4` member,且 `nonmember_001` 分数高于两个 member 样本。该机制不支持
继续 `8/8`、更多 seeds 或 embedding metric 变体。见
[docs/evidence/copymark-commoncanvas-multiseed-stability-20260513.md](docs/evidence/copymark-commoncanvas-multiseed-stability-20260513.md)。

### 2026-05-13 local package inventory checkpoint

本轮按 fresh-session 规则重读根级与 Research 入口后,只做浅层
second-asset / second-response-contract 盘点,没有释放 GPU,也不新增 evidence
长文档。`<DOWNLOAD_ROOT>/vision` 只有 MNIST 原始数据,属于已验证过的同类小
split 路线;`<DOWNLOAD_ROOT>/black-box` 只有既有 Beans/SD1.5、
CommonCanvas、Pokemon/Kandinsky 三类 response-contract。它们分别是
pseudo-membership、已完成且弱、以及空 split / 无 response,不构成新的 clean
GPU candidate。当前 `active_gpu_question = none`,`next_gpu_candidate = none`,
`CPU sidecar = none selected`。

### 2026-05-13 MIDST TabDDPM nearest-neighbor scout

为避免停在本机包盘点,本轮直接下载 MIDST black-box single-table 的
`tabddpm_black_box.zip` 到 `<DOWNLOAD_ROOT>/shared/midst-data/`,并使用本地
Codabench bundle 中的 dev/final labels 做可判 scorer。MIDST 是 SaTML 2025
tabular diffusion membership benchmark,每个 TabDDPM model folder 有 `200`
challenge rows、`20000` synthetic rows,且 member/nonmember 各半。最小
`negative_standardized_nearest_synthetic_l2` scorer 结果仍弱:
`dev+final AUC = 0.566263`,`ASR = 0.560500`,`TPR@1%FPR = 0.016750`,
`TPR@0.1%FPR = 0.001000`。该结果关闭最近邻方向;不扩 TabSyn、white-box
MIDST 或 tabular preprocessing matrix,除非出现真正不同的 tabular-diffusion
membership 机制。见
[docs/evidence/midst-tabddpm-nearest-neighbor-scout-20260513.md](docs/evidence/midst-tabddpm-nearest-neighbor-scout-20260513.md)。

### 2026-05-13 MIDST TabDDPM shadow-distributional scout

为确认 MIDST 是否只是最近邻 scorer 太弱,本轮只放行一个真正不同的 tabular
机制:用 `train` phase 的 `30` 个 shadow model folders 训练
`HistGradientBoostingClassifier`,输入 challenge row 相对于同 folder
`trans_synthetic.csv` 的 marginal z-score、robust z-score、empirical CDF、
tail-CDF、90% interval indicator 和 row-level outlierness summaries,再只在
dev/final 上评估。结果是典型 shadow overfit:train `AUC = 0.881991`、
`TPR@1%FPR = 0.302333`,但 dev+final 只有 `AUC = 0.499846`、
`ASR = 0.504250`,`TPR@1%FPR = 0.013000`,`TPR@0.1%FPR = 0.001500`。
该结果关闭 MIDST marginal-distributional shadow learning;不扩 classifier sweep、
feature matrix、TabSyn 或 white-box MIDST,除非出现真正不同的
tabular-diffusion membership observable。见
[docs/evidence/midst-tabddpm-shadow-distributional-scout-20260513.md](docs/evidence/midst-tabddpm-shadow-distributional-scout-20260513.md)。

### 2026-05-13 CommonCanvas conditional denoising-loss scout

为确认 CommonCanvas 是否只是黑盒 response scorer 弱,本轮释放一个真正不同的
PIA-style 内部机制:对现有 CopyMark/CommonCanvas `50/50` member/nonmember query
split,用 `common-canvas/CommonCanvas-XL-C` 在 caption 条件下计算固定 timesteps
`[200,500,800]` 的 negative denoising MSE。该 runner 在本机 RTX 4070 上采用
staged GPU 路径,避免 SDXL 全组件同时常驻 8GB 显存。结果仍弱:
`AUC = 0.5148`,`ASR = 0.5700`,`TPR@1%FPR = 0.0200`,
`TPR@0.1%FPR = 0.0200`,member/nonmember mean loss 几乎重叠
(`0.174177` vs `0.175785`)。该结果关闭 CommonCanvas conditional denoising-loss;
不扩 timestep、resolution、scheduler、seed、loss-weight 或 subset matrix。见
[docs/evidence/commoncanvas-denoising-loss-20260513.md](docs/evidence/commoncanvas-denoising-loss-20260513.md)。

### 2026-05-13 Beans member-LoRA denoising-loss scout

为修正 Beans/SD1.5 的 membership 语义问题,本轮没有继续把 Beans
train/validation 当成 base SD1.5 membership,而是在本机 RTX 4070 上创建一个
精确 target identity:`stable-diffusion-v1-5` + 只用 Beans `25` 个 member
query images 微调的 UNet LoRA,再用 held-out Beans `25` 个 nonmember query
images 做条件 denoising-loss scout。该实验是 internal known-split scout,不是
black-box response-contract 或 Platform/Runtime product row。结果仍弱:
`AUC = 0.414400`,`reverse AUC = 0.585600`,`ASR = 0.540000`,
`TPR@1%FPR = 0.080000`,`TPR@0.1%FPR = 0.080000`;member mean loss 反而高于
nonmember (`0.322735` vs `0.317327`)。这关闭 Beans member-LoRA
conditional denoising-loss 后继;不扩 train-step、rank、resolution、prompt、
scheduler、loss-weight 或 timestep matrix。见
[docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md](docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md)。

### 2026-05-13 Beans LoRA delta-sensitivity scout

为避免把 Beans LoRA 只按 denoising-loss 关闭,本轮切到真正不同的
architecture-local observable:在相同 noisy latents、prompt、timesteps 和 noise
seeds 下,测量 member-only LoRA 对 base SD1.5 UNet noise prediction 的相对 L2
扰动。结果仍弱:`mean_relative_unet_prediction_delta_l2_after_member_lora`
只有 `AUC = 0.512000`,`ASR = 0.600000`,`TPR@1%FPR = 0.040000`;
secondary `mean_base_minus_lora_denoising_loss_delta` 更弱
(`AUC = 0.468800`,`TPR@1%FPR = 0.000000`)。member/nonmember mean relative
delta 几乎重叠(`0.199573` vs `0.199563`)。这关闭 Beans LoRA
parameter-delta sensitivity 后继;Beans LoRA 已在修正 membership 语义后同时
失败 conditional denoising-loss 和 parameter-delta sensitivity,不得扩 layer/block、
timestep、prompt、rank、train-step、resolution、scheduler 或 loss-delta matrix。
见
[docs/evidence/beans-lora-delta-sensitivity-20260513.md](docs/evidence/beans-lora-delta-sensitivity-20260513.md)。

### 2026-05-13 paperization consumer boundary review

按长程 task board 的 Lane C,本轮检查 admitted summary、admitted bundle、unified
attack-defense table、product bridge 和 innovation map。admitted artifacts 中
没有 CommonCanvas、MIDST、Beans、Quantile、MIAGM、LAION、Zenodo、Noise as a
Probe 或 Kohaku 条目;它们只出现在 boundary、candidate、watch 或 limitation
文档里。结论是 `synchronized / paperization boundary updated / no schema
change`:Platform/Runtime 与国创/论文材料仍只消费 `recon`、`PIA baseline`、
`PIA defended`、`GSA`、`DPDM W-1` 五条 admitted rows;最近的 weak/watch
结果只能作为 limitations 或 future-work hooks,不能写成 product evidence、
admitted bundle entry 或 headline claim。见
[docs/evidence/paperization-consumer-boundary-20260513.md](docs/evidence/paperization-consumer-boundary-20260513.md)。

### 2026-05-13 MIA_SD face-LDM asset verdict

Lane A 继续检查非重复候选 `osquera/MIA_SD`。该 repo 是 face-image
membership against fine-tuned Stable Diffusion 的有用 code reference,但 root
README 明确说明实验图片未发布,`target_model/README.md` 只描述如何用本地图像
fine-tune SD1.5 并生成输出,`fine_tune.sh` 使用 `TRAIN_PATH` / `OUT_PATH`
占位符,没有 released target checkpoint、per-sample member/nonmember split
manifest 或 reusable query/response package。`dtu-400-target-loss.csv` 是
loss trace,不是逐样本 score packet。结论是 `code-and-result-artifacts /
private-images-missing / no download / no GPU release`;不得 scrape DTU/AAU/LFW
images、训练 400 epoch SD1.5、重建私有 folders 或从 plots/result traces 硬做
scorer。见
[docs/evidence/miasd-face-ldm-asset-verdict-20260513.md](docs/evidence/miasd-face-ldm-asset-verdict-20260513.md)。

### 2026-05-13 White-box GSA Zenodo archive verdict

Lane A 又检查了 Zenodo `10.5281/zenodo.14928092`。该记录公开
`White-box Membership Inference Attacks against Diffusion Models` / GSA 的
PoPETs 2025 artifact,包含 `6.7 GB` 的 `DDPM.zip`、`README.md`、
`new_environment.yml` 和 `LICENSE`。公开 GSA README 说明它是 DDPM / Imagen
白盒 gradient attack 代码与 target/shadow member/nonmember 数据构造流程。
DiffAudit 已经有 admitted white-box `GSA 1k-3shadow` 与 `DPDM W-1`
consumer rows,所以该 Zenodo 记录是 admitted-family archive,不是新的 Lane A
second asset。结论为 `admitted-family archive / not a new second asset /
no full download / no GPU release`;不得下载 `DDPM.zip`、重跑 GSA GPU、扩
loss-score / gradient ablation 或把它包装成黑盒/条件扩散 response-contract。
见
[docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md](docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md)。

### 2026-05-13 LAION-mi asset verdict

Lane A inspected `antoniaaa/laion_mi` as a non-duplicate second membership
asset candidate. It is stronger than Kohaku/Danbooru-style broad provenance:
the paper names `Stable Diffusion-v1.4`, the public HF metadata has
`13,396` `members` and `26,874` `nonmembers`, and each row has `url` plus
`caption`. The gate still fails `query/response coverage`: the release is
metadata-only and does not provide image bytes or generated responses.

Decision: `metadata-ready / response-not-ready / no GPU release`. LAION-mi is
now the highest-value Lane A watch candidate, but it is not
`next_gpu_candidate` until a fixed `25/25` URL availability probe recovers a
balanced tiny query set and a deterministic response/scoring contract is
frozen. See
[docs/evidence/laion-mi-asset-verdict-20260513.md](docs/evidence/laion-mi-asset-verdict-20260513.md)。

### 2026-05-13 LAION-mi URL availability probe

Research executed the promised CPU-only fixed `25/25` URL availability probe:
`HEAD` with fallback ranged `GET`, no image payloads stored, and image success
defined as `2xx/3xx` plus `Content-Type: image/*`. Results were too weak for a
balanced tiny query set: members recovered `11 / 25` images and nonmembers
recovered `16 / 25`, with mixed `403`, `404`, `401`, `410`, `503`, HTML, TLS,
and timeout failures.

Decision: `fixed 25/25 probe failed / metadata-only watch / no GPU release`.
LAION-mi does not move to response generation, scorer design, or GPU execution.
Do not build tooling around live LAION-mi URLs unless a cached or mirrored
public-safe image subset appears, or a later deterministic scan policy is
explicitly frozen before scoring. See
[docs/evidence/laion-mi-url-availability-probe-20260513.md](docs/evidence/laion-mi-url-availability-probe-20260513.md)。

### 2026-05-13 Zenodo fine-tuned diffusion asset verdict

Lane A clean-asset search inspected Zenodo `10.5281/zenodo.13371475`
(`Black-box Membership Inference Attacks against Fine-tuned Diffusion Models`).
The record is CC-BY-4.0 and exposes a `736,366,195` byte zip. Only API metadata
and the ZIP central directory were inspected. The archive is structured:
`celeba_target`, `celeba_partial_target`, `celeba_shadow`, and
`celeba_partial_shadow` LoRA checkpoints are visible, plus several
`dataset.pkl` payloads under target/shadow member or non-member directories.
However, the central directory does not expose a top-level experiment manifest,
does not prove the base model / training recipe, and does not show a complete
readable target member/nonmember split or query/response contract.

Decision: `archive-structured / manifest-incomplete / no download / no GPU
release`. This candidate stays on Lane A watch, but a full `736 MB` download,
LoRA scorer, or GPU run is blocked until a public README, appendix, code
reference, or tiny manifest proves target identity and exact split semantics.
See
[docs/evidence/zenodo-finetuned-diffusion-asset-verdict-20260513.md](docs/evidence/zenodo-finetuned-diffusion-asset-verdict-20260513.md)。

### 2026-05-13 Zenodo public code reference audit

Research performed the promised public-reference follow-up for Zenodo
`10.5281/zenodo.13371475` without downloading the `736 MB` archive. The NDSS
paper and `py85252876/Reconstruction-based-Attack` repository confirm a real
reconstruction-based attack workflow around fine-tuned diffusion models, so the
candidate improves from archive-only to `paper-and-code-backed archive watch`.
The missing gate did not change: no public readable target member/nonmember
split manifest or ready scoring contract was found, and the repository does not
bind the Zenodo `dataset.pkl` payloads to exact target sample identities.

Decision: `code-reference-found / split-manifest-still-missing / no download /
no GPU release`. Zenodo remains watch-only; do not write another Zenodo
scope/audit note, download the archive, or run LoRA scoring unless a public
manifest or repository file exposes exact split semantics. The next autonomous
cycle should switch away from Zenodo if no new external evidence appears. See
[docs/evidence/zenodo-code-reference-audit-20260513.md](docs/evidence/zenodo-code-reference-audit-20260513.md)。

### 2026-05-13 Noise as a Probe asset verdict

Research switched away from the blocked Zenodo line and inspected `Noise as a
Probe: Membership Inference Attacks on Diffusion Models Leveraging Initial
Noise` through arXiv source. This is a genuinely different mechanism family:
the paper obtains semantic initial noise through DDIM inversion, then feeds the
noise and prompt into the target model and scores reconstruction distance. It
uses Stable Diffusion-v1-4 fine-tuning and reports Pokémon `416/417`, T-to-I
`500/500`, MS-COCO `2500/2500`, and Flickr `1000/1000` member/hold-out counts.

Decision: `mechanism-relevant / reproduction-incomplete / no download / no GPU
release`. It is worth retaining as a Lane B mechanism hook, but it is not
`next_gpu_candidate`: no public code repository, per-sample split manifest,
released checkpoint, inversion cache, or query/response package was found.
Do not implement DDIM inversion or fine-tune SD-v1-4 from scratch for this
paper alone; reopen only if code plus exact split/checkpoint artifacts appear.
See [docs/evidence/noise-as-probe-asset-verdict-20260513.md](docs/evidence/noise-as-probe-asset-verdict-20260513.md)。

### 2026-05-13 watch-candidate consumer boundary verdict

After LAION-mi, Zenodo, and Noise as a Probe all stayed in watch states,
Research switched to Lane C and audited the Platform/Runtime consumer boundary.
`admitted-evidence-bundle.json` still has exactly five `admitted-only` rows:
`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`. The local
`validate_attack_defense_table.py` guard passed, and string checks found no
LAION-mi, Zenodo, Noise as a Probe, CommonCanvas, MIDST, Beans, or Kohaku entry
in the product bridge, admitted summary, unified table, or admitted bundle.

Decision: `synchronized / admitted-only boundary intact / no schema change`.
No Platform row, Runtime schema, admitted bundle, recommendation logic, or
product copy change is released. See
[docs/evidence/watch-candidate-consumer-boundary-20260513.md](docs/evidence/watch-candidate-consumer-boundary-20260513.md)。

### 2026-05-13 MIAGM asset verdict

Research returned to Lane A after the consumer-boundary sync and inspected
`Generated Distributions Are All You Need for Membership Inference Attacks
Against Generative Models` / `MIAGM`. The public repository is a useful
generated-distribution membership reference covering DDPM, DDIM, FastDPM,
CIFAR-10, and CelebA, but it does not expose exact target checkpoints,
per-sample member/nonmember split manifests, or ready generated-distribution
payloads.

Decision: `code-reference-only / artifact-incomplete / no download / no GPU
release`. MIAGM remains related-method watch, not `next_gpu_candidate`; do not
train DDPM/DDIM/FastDPM or regenerate distributions from scratch without
released target artifacts and split semantics. See
[docs/evidence/miagm-asset-verdict-20260513.md](docs/evidence/miagm-asset-verdict-20260513.md)。

### 2026-05-13 Quantile Regression asset verdict

Research continued Lane A with `Membership Inference Attacks on Diffusion
Models via Quantile Regression`. The paper is a useful mechanism reference:
it learns sample-conditioned quantile thresholds over reconstruction t-errors
and aggregates small attackers, which is distinct from response similarity,
denoising-loss, final-layer-gradient, MIDST marginal, and MIAGM generated-
distribution routes. The artifact gate still fails. The paper cites the
SecMI/Duan et al. codebase and released CIFAR10/CIFAR100 targets, and describes
training STL10/Tiny-ImageNet targets, but no paper-specific public code,
per-sample member/public/holdout split manifest, exact target artifact bundle,
or ready t-error packet was found.

Decision: `mechanism-reference / artifact-incomplete / no download / no GPU
release`. Keep it as a Lane B mechanism reference and Lane A watch candidate;
do not train STL10/Tiny-ImageNet DDPMs, reconstruct SecMI splits, or implement
quantile-regression scoring from scratch without released target artifacts and
split semantics. See
[docs/evidence/quantile-regression-asset-verdict-20260513.md](docs/evidence/quantile-regression-asset-verdict-20260513.md)。

Minimal reopen contract: 只有同时满足以下条件,下一轮才允许从 `none` 升为
新的 bounded GPU packet:目标模型身份固定,逐样本 member/nonmember split 可复核,
query 与 response coverage 已存在或可在一次确定性小包内生成,且假设不是
"再试一个相邻相似度/seed/梯度变体",而是能测试一个新机制或新资产迁移。最小
实验上限为先跑 `25/25` 或 `50/50` 的 simple distance / residual distance /
PIA-style score 单点;失败条件是 `AUC < 0.60` 或 `TPR@1%FPR` 近零时立即关闭,
不补矩阵消融。

## Long-Horizon Research Task Board（2026-05-13 起）

本节是当前长程任务板,用于替代继续追加短期 reselection / scope / preflight
文档。直到有新的 admitted row 或真正新资产出现前,下一位 Researcher 必须按
本节执行,不得把已关闭弱线改名重开。

### 总目标

在不牺牲严谨性的前提下,把 DiffAudit Research 从单资产强结果推进到
`可迁移 / 可解释 / 可系统消费` 的长期研究面。当前 admitted 基线已经足够支撑
演示和系统消费;下一阶段的价值只来自三类事情:

1. 找到第二个可复核 target membership 合同并跑出非弱信号。
2. 找到一个真正不同的 membership observable,不是旧 response similarity、
   denoising loss、final-layer gradient、nearest-neighbor 或 shadow marginal
   的相邻变体。
3. 把现有 admitted rows 的消费边界转成更稳定的论文/国创叙事,但不把
   candidate / weak / support-only 结果升格。

### Lane A: External Asset Acquisition Mainline

目标:获取一个比 CommonCanvas / MIDST / Beans 更干净的第二 membership 资产或
response contract。

必备合同:

- target model identity 固定到 checkpoint / endpoint / training recipe。
- target-member 列表逐样本可复核,不是 dataset split 名字、模型卡泛称或
  broad training-source provenance。
- nonmember / holdout 逐样本可复核,且不与 target training source 混淆。
- query/response coverage 已存在,或能在一次 deterministic `25/25` or `50/50`
  小包内生成。
- license / redistribution 边界能写入公开文档;私有路径、token、真实账号不写入。

执行顺序:

1. 每次只审一个候选 asset,先做 card / repo / manifest / file-tree
   membership-semantics check。
2. 只有合同满足上面五条,才允许下载权重或生成 responses。
3. 首包只跑一个最有判断力的 scorer;不得先建 scorer matrix。
4. 若 `AUC < 0.60` 或 `TPR@1%FPR` 近零,立即关闭该 asset 的当前 observable。

当前禁止重开:

- Kohaku / Danbooru,除非拿到 exact target-member manifest 或小型 verified
  split。
- Beans base SD1.5 pseudo-membership、Beans LoRA denoising-loss /
  parameter-delta sensitivity train/rank/timestep/layer variants。
- CommonCanvas 同 packet 的 pixel / CLIP / prompt / stability / denoising-loss
  variants。
- Fashion-MNIST / MNIST public-checkpoint raw-loss or x0 repeat。
- MIDST nearest-neighbor、shadow marginal classifier、TabSyn / white-box MIDST
  expansion。

### Lane B: Mechanism Discovery Mainline

目标:找到一个能解释或超越现有 admitted rows 的新 observable。当前允许的是
concept-level 机制设计,不是围绕弱结果补矩阵。

可考虑的问题形态:

- training-dynamics observable:不同 checkpoint / training phase 的信号轨迹,
  前提是 target membership 和 checkpoint cadence 可复核。
- architecture-local observable:不仅是 final-layer norm/cosine,而是有明确
  diffusion block / attention / normalization 假设,且能先在 tiny target 上证明
  非随机。
- response-contract observable:不是 query-response 距离,而是利用可复核生成
  过程中的中间状态、uncertainty 或 edit trajectory;必须有 fixed query contract。
- defense-aware observable:必须同时定义 defended target、adaptive attacker、
  retained utility 和 member/nonmember identity,否则仍属于 I-B hold。

机制 release gate:

- 先写一句 falsifiable hypothesis:如果成功,会改变哪一条 project decision。
- tiny smoke 只验证可运行;不得用 `2/2` 或 `4/4` 结果做结论。
- 正式最小包优先 `25/25` or `50/50`;低于该规模只能叫 smoke。
- 弱结果不得进入 second variant,除非变体改变 observable family。

当前禁止重开:

- final-layer gradient norm/cosine/prototype variants。
- raw denoising MSE / x0 residual / pixel or CLIP distance variants。
- midfreq same-contract repeat or frequency cutoff sweep。
- CLiD prompt / prompt-text / image-prompt shuffle variants。

### Lane C: Consumer Boundary And Paperization Mainline

目标:让已有强结果更容易被 Platform / Runtime / 国创材料消费,但不制造新研究
claim。

允许动作:

- 同步 admitted consumer rows:recon、PIA baseline、PIA defended、GSA、DPDM W-1。
- 把 finite-tail / adaptive boundary 写成可引用的限制条件。
- 将 weak/candidate/support-only rows 编入 negative evidence 或 limitations,
  但不改变 status。
- 给 Platform / Runtime 提供 machine-readable bundle,前提是 bundle 只含
  admitted rows 或明确的 candidate label。

禁止动作:

- 为了让系统看起来丰富,把 ReDiffuse、SecMI NNS/stat、tri-score、H2、
  CLiD、CommonCanvas、Beans LoRA、MIDST、I-B、I-C 写成 product row。
- 因为某个候选有高 AUC 就绕过 low-FPR、adaptive、consumer-boundary review。
- 在公共文档里写本机路径、SSH alias、真实域名、token 或 agent 私聊指令。

### Execution Cadence

每个长程循环最多只能落一个主产物:

- `asset verdict`:一个新资产合同通过/失败,并更新 task board。
- `metric verdict`:一个 bounded scorer packet 通过/失败,并写 evidence note。
- `consumer verdict`:一个 admitted/candidate boundary 同步,并跑 public checks。
- `roadmap operating-system update`:当路线图本身缺少连续运行、纠错、复盘或归档
  机制时,只允许更新权威入口,不得伪装成实验进展。

每轮都必须更新:

- `<DIFFAUDIT_ROOT>/ROADMAP.md`
- `<DIFFAUDIT_ROOT>/Research/ROADMAP.md`
- 相关 `workspaces/<direction>/README.md` 或 `plan.md`

每轮都必须结束于:

- `active_gpu_question` 明确为具体 bounded packet 或 `none`。
- `next_gpu_candidate` 明确为具体候选或 `none`。
- `CPU sidecar` 明确为一个小任务或 `none selected`。
- 如果 Research repo 有改动,走 branch -> checks -> PR -> squash merge ->
  clean `main`。

### Continuous Run Loop

每个 Research 长程循环按以下顺序执行,不得跳步:

1. `Anchor`
   - 读 `<DIFFAUDIT_ROOT>/ROADMAP.md`
   - 读 `Research/ROADMAP.md`
   - 读 `Research/AGENTS.md`
   - 读 `docs/evidence/workspace-evidence-index.md`
   - 读相关 `workspaces/<lane>/README.md` 或 `plan.md`
2. `Select`
   - 从 Lane A/B/C 只选一条
   - 写明本轮唯一主产物类型:`asset verdict`、`metric verdict`、
     `consumer verdict` 或 `roadmap operating-system update`
   - 写明如果失败会关闭什么,而不是还想再补什么
3. `Execute`
   - Lane A:只做一个候选的 target/split/query-response/provenance gate
   - Lane B:只做一个新 observable family 的 falsifiable hypothesis 或 tiny smoke
   - Lane C:只做一个 admitted/candidate/support-only boundary sync
   - GPU release 前必须有 frozen command、metric contract、evidence-note target 和
     stop condition
4. `Reflect`
   - 回答:`本轮是否发现新信号、测试迁移或改变决策?`
   - 若答案是否,必须停止扩展,只做最短同步
   - 若同一 family 连续两个 verdict 是 weak / blocked / metadata-only,下一轮默认
     切 lane
5. `Archive`
   - 新 verdict 写入 `docs/evidence/`
   - `workspace-evidence-index.md` 的 latest update 指向最新 verdict
   - 当前三槽位写回本节 `Current Long-Horizon State`
   - 相关 workspace README/plan 写最短 next gate
6. `Merge`
   - 本地检查:`check_public_surface.py`,`check_markdown_links.py`,`git diff --check`
   - 远端检查:GitHub `unit-tests` success;`full-checks` skipped 只能按 workflow
     规则记录,不能当成功代理
   - squash merge 后回到 clean `main`

### Reflection And Correction Gates

| Gate | Rule | Correction |
| --- | --- | --- |
| No-stationery | 新 CLI、validator、manifest、长文档不能单独算研究推进 | 改成 asset/metric/consumer verdict,或停止 |
| Two-weak-runs | 同一 asset/observable 连续两个 weak/block verdict | 默认关闭 family,下一轮切 lane |
| Membership semantics | 没有逐样本 target member/nonmember 语义 | 不下载大权重,不跑 scorer |
| Response contract | 黑盒路线没有 query/response coverage | 不生成 responses,不释放 GPU |
| Consumer honesty | 非 admitted row 想进 Platform/Runtime | 退回 limitations/evidence index |
| Stale-doc conflict | ROADMAP/AGENTS/index 出现旧 next action | 直接替换权威条目,不追加旁注 |

### Progress Review And Archive Cadence

短复盘触发条件:

- 每个自然日结束前;
- 或每完成两个 Research PR;
- 或每次 `active_gpu_question` / `next_gpu_candidate` / `CPU sidecar` 变化。

短复盘必须检查:

- 最新 verdict 是否在 `docs/evidence/` 有独立 note;
- `workspace-evidence-index.md` latest update 是否指向最新 note;
- 本节 `Current Long-Horizon State` 是否与根级 ROADMAP 一致;
- 相关 workspace README/plan 是否只保留当前 next gate;
- Research 是否 clean `main...origin/main`。

归档复盘触发条件:

- 同一 family 被关闭;
- 同一 workspace README/plan 累积多个过期 next action;
- 准备同步到 Platform / Runtime / Docs;
- 进入国创材料整理。

归档复盘动作:

- 将已关闭路线压缩成 negative evidence 或 limitation;
- 保留 evidence note,删除或迁移过期活跃 workspace 待办;
- 不把 agent 操作流水写进公共 docs;
- 只把 admitted 或明确标注 candidate/support-only 的结果交给 consumer 层。

### Autonomous Next Task Queue

| Priority | Task | Entry Gate | Stop Gate |
| --- | --- | --- | --- |
| 1 | Lane A clean asset search | 非 LAION-mi live URL、非 CommonCanvas/MIDST/Beans/MNIST/Fashion-MNIST/Kohaku;有 target identity 与 split 线索 | 任一 target/split/query-response/provenance gate 失败则写 asset verdict 并关闭 |
| 2 | Lane B new observable sketch | 一句话 falsifiable hypothesis 能改变 project decision | 如果只是 final-layer gradient、raw denoising MSE、pixel/CLIP distance、midfreq cutoff 或 same-contract repeat,停止 |
| 3 | Lane C consumer/paperization review | 只处理 admitted rows 与 limitations 口径 | 需要新增 product row 或 schema 时先写 product-bridge handoff,不直接跨仓 |

### Current Long-Horizon State

| Field | Value |
| --- | --- |
| Active GPU question | none |
| Next GPU candidate | none |
| CPU sidecar | none selected; White-box GSA Zenodo is admitted-family provenance only; MIA_SD lacks public images/checkpoint/split/query-response; Quantile Regression is mechanism-reference but artifact-incomplete; MIAGM is code-reference-only and artifact-incomplete; Noise as a Probe is mechanism-relevant but reproduction-incomplete; Zenodo fine-tuned diffusion is paper-and-code-backed but split-manifest incomplete; LAION-mi remains metadata-only watch |
| Highest-value next action | Continue Lane A only with a non-duplicate candidate that exposes exact split artifacts, or switch to Lane B only with a genuinely different runnable target contract; otherwise stop instead of writing another scope/audit chain |
| Stop condition | Do not download GSA `DDPM.zip` or replay admitted-family GSA as a new asset; do not scrape MIA_SD images or train SD1.5; do not train Quantile Regression STL10/Tiny-ImageNet targets or reconstruct SecMI splits from scratch; do not train MIAGM targets or regenerate distributions from scratch; do not implement Noise-as-Probe from scratch; do not download the full Zenodo fine-tuned diffusion archive, write another same-line Zenodo audit/scope note, build LoRA scoring, or reopen LAION-mi live URLs without manifest-backed split/query evidence |

### P0 — 完成且弱

CopyMark / CommonCanvas 已跑出第一个真实 `50/50` scorer 结果:

```text
package_probe = ready
score_name = negative_pixel_mse_resized_512
direction = higher_is_more_member
AUC = 0.5736
ASR = 0.6000
TPR@1%FPR = 0.04
TPR@0.1%FPR = 0.04
verdict = negative_or_weak
```

P0 结论:

- 第二响应合同不再是 missing asset 问题;`50/50` responses 已经存在。
- 最简单 pixel-distance transfer 在 SDXL-class CommonCanvas 上很弱,不准入 admitted evidence。
- 单点 CLIP image-similarity follow-up 也弱:`AUC = 0.4588`,`ASR = 0.5300`,低 FPR 恢复为 0。
- 单点 prompt-response consistency follow-up 也弱:`AUC = 0.4408`,`ASR = 0.5100`,低 FPR 只恢复 `1/50` member。
- 单点 multi-seed response stability follow-up 也弱:`4/4`,`AUC = 0.5625`,`ASR = 0.625`,低 FPR 只恢复 `1/4` member。
- 单点 conditional denoising-loss follow-up 也弱:`50/50`,`AUC = 0.5148`,`ASR = 0.5700`,低 FPR 只恢复 `1/50` member。
- 不继续补 CLIP / pixel / LPIPS 变体矩阵来让消融表好看。
- CommonCanvas 当前 packet 默认关闭;只有出现真正不同的新机制或新资产时,才允许继续,不得扩 denoising-loss 矩阵。

### 2026-05-13 P0 result checkpoint

- 已确认:HF auth 可用,`diffaudit-research` 环境有 CUDA Torch 并能看到 RTX 4070;默认 PATH Python 是 CPU-only,不得再把它误判为本机无 CUDA。
- `commoncanvas_xl_c.safetensors` 已完整下载,大小 `6,938,040,286` bytes。
- `StableDiffusionXLPipeline.from_single_file` CUDA smoke 已生成 `1 member + 1 nonmember`。
- full deterministic response packet 已完成:`50` member responses + `50` nonmember responses,`512x512`,`20` steps,`guidance_scale = 7.5`,fixed seed base `20260513`。
- package probe artifact `workspaces/black-box/artifacts/copymark-commoncanvas-response-contract-probe-20260513.json` 返回 `ready`,缺失列表为空。
- simple-distance artifact `workspaces/black-box/artifacts/copymark-commoncanvas-simple-distance-20260513.json` 返回 `negative_or_weak`。
- CLIP image-similarity artifact `workspaces/black-box/artifacts/copymark-commoncanvas-clip-image-similarity-20260513.json` 返回 `negative_or_weak`:`AUC = 0.4588`,`ASR = 0.5300`,`TPR@1%FPR = 0.0`,`TPR@0.1%FPR = 0.0`。
- prompt-response consistency artifact `workspaces/black-box/artifacts/copymark-commoncanvas-prompt-response-consistency-20260513.json` 返回 `negative_or_weak`:`AUC = 0.4408`,`ASR = 0.5100`,`TPR@1%FPR = 0.02`,`TPR@0.1%FPR = 0.02`。
- multi-seed response stability artifact `workspaces/black-box/artifacts/copymark-commoncanvas-multiseed-stability-20260513.json` 返回 `negative_or_weak`:`4/4`,`AUC = 0.5625`,`ASR = 0.625`,`TPR@1%FPR = 0.25`,`TPR@0.1%FPR = 0.25`。
- conditional denoising-loss artifact `workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json` 返回 `negative_or_weak`:`50/50`,`AUC = 0.5148`,`ASR = 0.5700`,`TPR@1%FPR = 0.02`,`TPR@0.1%FPR = 0.02`。
- 下一决策:不默认继续 CommonCanvas 当前 packet;转入真正不同的机制或新资产,不再挖相邻 CLIP 分数、prompt-adherence、response-stability 或 denoising-loss 变体。

### P1 — 已执行且弱

`tiny self-trained MNIST/DDPM known-split target × gradient-sensitive scorer`。

- 唯一依据:5/12 `tiny-overfit-gradient-norm-scout` 在 `8/8` overfit 上 `AUC = 0.734`,`16/64` stability gate 跌到 `0.535`。
- 2026-05-13 follow-up:在更真实的 `64/64` known-split tiny denoiser 上测试更乐观的 oracle `final_layer_gradient_prototype_cosine`,结果 `AUC = 0.500977`,`ASR = 0.562500`,`TPR@1%FPR = 0.0`,`TPR@0.1%FPR = 0.0`。
- 结论:不继续叠 raw-MSE / x0-residual / pixel-distance / CLIP-distance / final-layer gradient norm/cosine 变体。

### 冻结清单(违反即视为浪费 cycle)

- **I-B**:任何 reopen-protocol / shadow-reference / defended-shadow training manifest / shadow-local identity scout / defense-aware reopen 的第 N+1 版。`hold-protocol-frozen` 已是终态;reopen 必须由新的 bounded hypothesis 触发,而不是再加一份 audit。
- **midfreq**:同 DDPM/CIFAR10 资产的第三个 seed、新 comparator、新 stability 跑。`mid-frequency-specific` 已被 5/12 comparator audit 证伪。
- **Beans/SD1.5**:任何 distance variant。membership semantics 已被 `beans-sd15-membership-semantics-correction-20260512` 证伪;contract-debug 价值已耗尽。
- **cross-box / archived gray-box paper candidates**:第二版 successor scope 或 reentry review。
- **SecMI**:第 N+1 版 admission-contract-hardening。`research-support-only` 是终态。
- **ReDiffuse**:800k 任何版本、新 scoring contract 变体。`candidate-only / hold` 是终态。
- **I-C same-spec evaluator**:不再写 third 份 feasibility scout。

### 程序性约束 — 防止再次进入空转

1. **3-doc cap per lane**:同一 lane 在不出真实 metric(`AUC / TPR / ASR`)前,累计 contract / manifest / preflight / scout / scope / audit 类 evidence 上限 3 份;第 4 份触发自动暂停并向管理员 escalate。
2. **Trigger-word audit**:连续 3 份 evidence 标题含 `contract`/`preflight`/`manifest`/`scout`/`scope`/`audit`/`reselection` 之一,必须暂停并 escalate,由把控者决定是切 lane、改 acquisition,还是确认死路。
3. **Reselection 必须答一句**:本次 reselection 改变了什么具体决策?若答案只是"换下一条 hold lane",不允许 reselection,必须 escalate。
4. **GPU release 不再走"CPU-first scoping"反复流程**:P0 step 3 完成 → step 4 直接释放 GPU(`active_gpu_question` 升为 `commoncanvas-recon-50/50`)。RTX 4070 闲置写 prose 是研究失败,不是审慎。
5. **不再写"反思 / taste reset / 路线纠偏"长 doc**:这种 doc 本身就是新一轮"差生文具多"。本节是当前唯一有效的纠偏 source-of-truth,直到 P0 出结果为止。

### Sync 字段(覆盖下方 `Current Focus` 表格,直至 P0 verdict)

| Field | 2026-05-13 value |
| --- | --- |
| Active work | P0/P1 weak; CommonCanvas pixel/CLIP/prompt/stability/denoising-loss weak; Kohaku blocked; Fashion-MNIST PIA-loss scout weak; MIDST TabDDPM nearest-neighbor and shadow-distributional scouts weak; Beans LoRA denoising-loss and parameter-delta sensitivity weak; LAION-mi fixed `25/25` URL probe failed; Zenodo fine-tuned diffusion is paper-and-code-backed but split-manifest incomplete; Noise as a Probe is mechanism-relevant but reproduction-incomplete; MIAGM is code-reference-only and artifact-incomplete; Quantile Regression is mechanism-reference but artifact-incomplete |
| Active GPU question | none selected after weak CommonCanvas pixel/CLIP/prompt/stability/denoising-loss, gradient-prototype, Fashion-MNIST, MIDST TabDDPM, Beans LoRA denoising-loss/delta-sensitivity, and LAION-mi URL-probe verdicts |
| Next GPU candidate | none; reopen only with a genuinely new mechanism or cleaner asset with exact member/nonmember split and response coverage |
| CPU sidecar | none selected; Quantile Regression lacks paper-specific code, exact target artifacts, and per-sample split manifests; MIAGM lacks target checkpoint/split/generated-distribution artifacts; Noise as a Probe lacks public code/split/checkpoint artifacts; Zenodo full download and further same-line audits are blocked on a public split manifest; and LAION-mi live URLs remain closed |
| Platform/Runtime impact | none; no admitted promotion |

### 对 Codex 的明确指令

"CommonCanvas 已经在第二个真实 membership 资产上跑过,且 pixel-distance、CLIP image-similarity、prompt-response consistency、multi-seed response stability、conditional denoising-loss 都弱。P1 的 known-split gradient-prototype follow-up 也弱。Beans LoRA 在修正 membership 语义后,conditional denoising-loss 和 parameter-delta sensitivity 都弱。不要把弱结果扩展成消融矩阵、seed/subset 矩阵、denoising-loss 矩阵、delta/layer 矩阵或梯度变体表。下一步必须重新选一个真正不同的机制或新资产;如果没有,就停在当前结论。"

---

This is the short steering document for Research. Execution history and old
run narratives live in `legacy/`; current workspace state lives in
`workspaces/`; reviewed evidence lives in `docs/evidence/`.

## Current Focus

| Field | Current value |
| --- | --- |
| Active work | `White-box GSA Zenodo archive is admitted-family and not a new second asset; MIA_SD face-LDM asset verdict is code-and-result-artifacts but private-images-missing; Paperization consumer boundary synchronized after weak/watch second-asset and mechanism checks; CommonCanvas packet closed by default after weak pixel/CLIP/prompt/stability/denoising-loss scouts; known-split gradient-prototype follow-up weak; MIDST TabDDPM nearest-neighbor and shadow-distributional scouts weak; Beans LoRA denoising-loss and parameter-delta sensitivity weak under repaired known-split semantics; LAION-mi fixed 25/25 URL probe failed; Zenodo fine-tuned diffusion paper/code-backed but split-manifest incomplete; Noise as a Probe mechanism-relevant but reproduction-incomplete; MIAGM code-reference-only and artifact-incomplete; Quantile Regression mechanism-reference but artifact-incomplete` |
| Current GPU candidate | none selected |
| CPU sidecar | none selected; White-box GSA Zenodo is already admitted-family provenance and not a new second asset; MIA_SD lacks published images, target checkpoint, exact split manifest, and reusable query/response packet; paperization can cite recent weak/watch lines only as limitations or future-work hooks; Quantile Regression needs paper-specific code plus exact target/split artifacts, MIAGM needs target checkpoint/split/generated-distribution artifacts, Noise as a Probe needs public code/split/checkpoint artifacts, Zenodo fine-tuned diffusion needs a public split manifest before full download, and LAION-mi needs cached images or a frozen deterministic scan policy |
| Active GPU question | none after weak CommonCanvas P0/CLIP/prompt/stability/denoising-loss follow-ups, weak P1 gradient-prototype scout, weak Fashion-MNIST PIA-loss scout, weak MIDST TabDDPM nearest-neighbor/shadow-distributional scouts, weak Beans LoRA denoising-loss/delta-sensitivity scouts, and failed LAION-mi URL probe |
| Platform/Runtime impact | no schema change; admitted consumer rows are guarded |

Current objective: stop turning weak or blocked lines into larger engineering
surfaces. The second response contract has now been tested, and pixel-distance,
CLIP image-similarity, prompt-response consistency, multi-seed response
stability, and conditional denoising-loss are all weak. A more optimistic known-split final-layer gradient
prototype scout is also weak. A small Fashion-MNIST DDPM PIA-style loss scout
on a real train/test split is also weak. MIDST TabDDPM is a cleaner external
membership benchmark and is locally scoreable, but both the minimal
nearest-synthetic-row scorer and a shadow-trained marginal distributional
classifier are weak on dev/final. CommonCanvas PIA-style denoising-loss also
failed on the true `50/50` packet, so do not reopen it via timestep or scheduler
matrices. Beans LoRA also failed both conditional denoising-loss and
parameter-delta sensitivity after the known-split repair, so do not reopen it
through train-step, rank, layer/block, timestep, prompt, scheduler, or
resolution matrices. The next high-value move must be a
genuinely different mechanism or cleaner asset, not another validator,
boundary note, adjacent CLIP score, stability repeat, same-family gradient
variant, same-contract repeat, or remap-training detour.

Taste reset: every cycle must ask whether the work is finding new signal or
just adding "more stationery" around a dead end. If a direction is already
blocked, weak, or candidate-only, write the shortest useful verdict and move
on unless the next action can change a real decision. ReDiffuse 800k, I-B
target-risk remap training, I-C translated replay, diagonal-Fisher repeats,
GSA loss-score LR repeats, and mid-frequency same-contract repeats are not
default next steps.

The current scope gate is frozen in
[docs/evidence/true-second-membership-benchmark-scope-20260512.md](docs/evidence/true-second-membership-benchmark-scope-20260512.md).
A true second membership benchmark must identify the target model, its real
member training or fine-tuning set, a held-out nonmember set, and a reproducible
query/response contract. Beans/SD1.5 remains useful only for contract/debug
plumbing; MNIST/DDPM is semantically cleaner but raw-loss transfer is already
weak. The next valid move is either a sharper MNIST/DDPM scorer or a tiny
known-split self-trained/fine-tuned target, not more validators or pseudo-split
distance variants.

A follow-up CPU-only MNIST/DDPM `x0` reconstruction scout is also weak:
mean `x0` MSE/L1/edge residual AUCs are about `0.55`, with the best
single-timestep `x0` L1 AUC only `0.656250`. This closes simple raw-loss and
simple reconstruction-residual scoring on MNIST/DDPM unless a sharper mechanism
appears. See
[docs/evidence/mnist-ddpm-x0-reconstruction-scout-20260512.md](docs/evidence/mnist-ddpm-x0-reconstruction-scout-20260512.md).
A tiny known-split MNIST denoising sanity check also failed to produce raw-loss
membership separation even though the training loss decreased: `AUC = 0.492676`
and `TPR@1%FPR = 0.0`. This blocks the easy route "train tiny known-split target
and reuse raw denoising loss"; future work needs a mechanism beyond simple
MSE or a real external benchmark with documented provenance. See
[docs/evidence/tiny-known-split-denoising-sanity-20260512.md](docs/evidence/tiny-known-split-denoising-sanity-20260512.md).
An external diffusion benchmark provenance scan did not find an obvious
ready-to-score second benchmark: Fashion-MNIST/CelebA/CIFAR-style model cards
are not enough unless they prove exact target training membership and held-out
nonmembers. Do not download large external weights or run scoring from dataset
names alone. See
[docs/evidence/external-diffusion-benchmark-provenance-scan-20260512.md](docs/evidence/external-diffusion-benchmark-provenance-scan-20260512.md).
A final tiny overfit upperbound deliberately trained a denoiser on only `8`
MNIST member images for `80` CPU epochs. Raw denoising MSE still produced only
`AUC = 0.552734` with `TPR@1%FPR = 0.0`, so simple raw-MSE known-split work is
closed unless a genuinely different observable appears. See
[docs/evidence/tiny-overfit-mse-upperbound-20260512.md](docs/evidence/tiny-overfit-mse-upperbound-20260512.md).
A CPU-only gradient-norm mechanism scout on the same `8`-member overfit target
is the first useful post-reset signal: final-layer per-sample gradient L2 gives
`AUC = 0.734375` and recovers `1 / 8` members at zero false positives
(`TPR@1%FPR = 0.125`). This is not admitted and does not release GPU, but it
changes the next mechanism candidate from raw MSE to gradient-sensitive
observables. See
[docs/evidence/tiny-overfit-gradient-norm-scout-20260512.md](docs/evidence/tiny-overfit-gradient-norm-scout-20260512.md).
A less extreme `16 / 64` CPU stability gate weakens that result: final-layer
gradient L2 falls to `AUC = 0.535156`, with only `1 / 16` members recovered at
zero false positives. This keeps gradient-sensitive scoring as a mechanism hint
but blocks GPU scaling and broad layer sweeps. See
[docs/evidence/gradient-norm-stability-gate-20260512.md](docs/evidence/gradient-norm-stability-gate-20260512.md).
A 2026-05-13 `64 / 64` oracle-style gradient prototype alignment follow-up is
also weak: `final_layer_gradient_prototype_cosine` gives `AUC = 0.500977`,
`ASR = 0.562500`, and zero low-FPR recovery despite clear training-loss
decrease. This closes same-family final-layer gradient variants by default. See
[docs/evidence/tiny-known-split-gradient-prototype-alignment-20260513.md](docs/evidence/tiny-known-split-gradient-prototype-alignment-20260513.md).
CopyMark is now the best external intake candidate because its paper and
repository describe a diffusion membership/copyright benchmark rather than a
generic model card. The follow-up manifest pass inspected `diffusers/` scripts,
zip headers, the zip central directory, and representative `caption.json`
payloads without downloading image data. CopyMark has a concrete directory-level
member/holdout contract with `eval` and `test` splits, but the archive does not
ship per-row membership provenance beyond directory choice. The selected
CommonCanvas/CommonCatalog target now has a local `50/50` query split,
deterministic `50/50` text-to-image responses from
`common-canvas/CommonCanvas-XL-C`, and a package probe status of `ready`. See
[docs/evidence/copymark-provenance-intake-20260512.md](docs/evidence/copymark-provenance-intake-20260512.md).
The query asset note is
[docs/evidence/copymark-commoncanvas-query-asset-20260512.md](docs/evidence/copymark-commoncanvas-query-asset-20260512.md).
A response-generation preflight corrected the blocker: the default PATH Python
is CPU-only, but the `diffaudit-research` conda environment has CUDA Torch and
sees the local RTX 4070. CommonCanvas is a text-to-image SDXL pipeline, so the
package contract is `text_to_image`, not `image_to_image`. The 2026-05-13
completion generated the deterministic responses and ran two bounded scorers:
`negative_pixel_mse_resized_512` gives `AUC = 0.5736`, `ASR = 0.6000`,
`TPR@1%FPR = 0.04`, and `TPR@0.1%FPR = 0.04`; the single sharper
`clip_vit_l14_query_response_cosine` follow-up gives `AUC = 0.4588`,
`ASR = 0.5300`, and zero low-FPR recovery; the distinct
`clip_vit_l14_prompt_response_cosine` check gives `AUC = 0.4408`,
`ASR = 0.5100`, and only `1 / 50` member recovered at zero false positives.
All are `negative_or_weak` and not admitted. Do not expand this weak result into
a variant matrix. See
[docs/evidence/copymark-commoncanvas-response-preflight-20260512.md](docs/evidence/copymark-commoncanvas-response-preflight-20260512.md).

After closing cross-box successor scoping, I-B defense-aware
reopen scoping, archived gray-box paper-candidate reentry, and I-C same-spec
feasibility as `hold`, verifying no admitted consumer drift, and freezing the
I-B defended-shadow reopen protocol, advance only a genuinely distinct
observable with a CPU-first contract. The
paper-backed new-observable scout identifies mid-frequency same-noise residual
scoring as distinct from H2/H3 response-cache frequency filtering, but the
local H2/H3 caches lack `x_t`, `tilde_x_t`, noise provenance, and
same-noise residual fields. The synthetic tiny cache writer and real-asset
`4/4` preflight proved the cache path; the frozen `64/64` sign-check then
completed on the collaborator 750k checkpoint with `AUC = 0.733398`,
`ASR = 0.710938`, and finite strict-tail `TPR = 4/64` at zero false positives.
The verdict is candidate-only. The seed-only stability repeat retained the
signal with `AUC = 0.719238`, `ASR = 0.6875`, and finite strict-tail
`TPR = 3/64` at zero false positives. The line is now
`candidate-stable-but-bounded`: it remains internal Research evidence, but no
same-contract GPU expansion is authorized. A CPU-only comparator audit then
narrowed the claim: low-frequency and full-band residual comparators are at
least as strong as the frozen mid-band score on AUC, so do not phrase the line
as proven mid-frequency-specific. Post-midfreq reselection selected a CPU-only
SecMI consumer-contract review; that review keeps SecMI as
`structural-support-only` because NNS product semantics, adaptive comparability,
provenance language, and bundle schema fit remain blocked. The follow-up I-B
protocol audit is also closed as `hold-structural`: the active
risk-targeted-unlearning review path previously borrowed an undefended shadow
threshold-transfer reference. The defended-shadow reopen protocol is now frozen
as a machine-checkable CPU artifact, and explicit defended-shadow reopen mode
now rejects undefended threshold references. A CPU-only defended-shadow
training manifest then checked the fixed k32 forget/matched identity files
against three shadow member datasets, but coverage-aware validation blocks the
current contract: `shadow-01` covers `2/32` forget IDs, `shadow-02` covers
`2/32`, and `shadow-03` covers `1/32`. It releases no GPU and does not execute
training. A follow-up CPU shadow-local identity scout shows that target-level
risk records can be filtered into a two-shadow remap for `shadow-01` and
`shadow-02`, while `shadow-03` remains short at `31/32` member records. The
scout remains blocked as true shadow-local evidence because its risk records
come from target-level PIA/GSA full-overlap prep, not per-shadow scoring.
Post-I-B reselection selected an I-C same-spec
evaluator feasibility scout; that scout is now closed as `hold` because the
active PIA bridge surface remains translated-alias-only with
`same_spec_reuse = false` and no split-level four-metric board. The admitted
consumer drift audit then passed the full consumer-validator chain and
confirmed the machine-readable Platform/Runtime bundle still admits only recon,
PIA baseline, PIA defended, GSA, and DPDM W-1. See
[docs/evidence/ib-reopen-shadow-reference-guard-20260512.md](docs/evidence/ib-reopen-shadow-reference-guard-20260512.md),
[docs/evidence/ib-defended-shadow-training-manifest-20260512.md](docs/evidence/ib-defended-shadow-training-manifest-20260512.md),
[docs/evidence/ib-shadow-local-identity-scout-20260512.md](docs/evidence/ib-shadow-local-identity-scout-20260512.md),
[docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md),
[docs/evidence/admitted-consumer-drift-audit-20260512.md](docs/evidence/admitted-consumer-drift-audit-20260512.md),
[docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md),
[docs/evidence/post-ib-next-lane-reselection-20260512.md](docs/evidence/post-ib-next-lane-reselection-20260512.md),
[docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](docs/evidence/ib-defense-reopen-protocol-audit-20260512.md),
[docs/evidence/secmi-consumer-contract-review-20260512.md](docs/evidence/secmi-consumer-contract-review-20260512.md),
[docs/evidence/post-midfreq-next-lane-reselection-20260512.md](docs/evidence/post-midfreq-next-lane-reselection-20260512.md),
[docs/evidence/midfreq-residual-comparator-audit-20260512.md](docs/evidence/midfreq-residual-comparator-audit-20260512.md),
[docs/evidence/midfreq-residual-stability-result-20260512.md](docs/evidence/midfreq-residual-stability-result-20260512.md),
[docs/evidence/midfreq-residual-stability-decision-20260512.md](docs/evidence/midfreq-residual-stability-decision-20260512.md),
[docs/evidence/midfreq-residual-signcheck-20260512.md](docs/evidence/midfreq-residual-signcheck-20260512.md),
[docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](docs/evidence/midfreq-same-noise-residual-preflight-20260512.md),
[docs/evidence/midfreq-residual-scorer-contract-20260512.md](docs/evidence/midfreq-residual-scorer-contract-20260512.md),
[docs/evidence/midfreq-residual-collector-contract-20260512.md](docs/evidence/midfreq-residual-collector-contract-20260512.md),
[docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md),
[docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](docs/evidence/midfreq-residual-real-asset-preflight-20260512.md),
[docs/evidence/graybox-paper-candidate-reentry-review-20260512.md](docs/evidence/graybox-paper-candidate-reentry-review-20260512.md),
[docs/evidence/ib-defense-aware-reopen-scout-20260512.md](docs/evidence/ib-defense-aware-reopen-scout-20260512.md),
[docs/evidence/cross-box-successor-scope-20260512.md](docs/evidence/cross-box-successor-scope-20260512.md),
[docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md](docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md),
[docs/evidence/post-fisher-next-lane-reselection-20260511.md](docs/evidence/post-fisher-next-lane-reselection-20260511.md),
and [docs/evidence/post-secmi-next-lane-reselection-20260511.md](docs/evidence/post-secmi-next-lane-reselection-20260511.md).
The first feasibility contract is now checked as a CPU-only artifact. The GSA
assets are ready only with the workspace-scoped upstream checkout, and the
contract blocks GPU until a micro-board proves a distinct non-scalar gradient
or curvature observable beyond scalar loss, raw gradient norm, GSA loss-score
LR, and activation-subspace variants:
[docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md](docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md).
The first CPU micro-board ran on selected-layer raw gradients and closed as
`negative-but-useful`: extraction is viable, but diagonal-Fisher
self-influence fails the target-transfer gate and does not beat scalar loss or
raw-gradient baselines. See
[docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md](docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md).
The follow-up layer-scope review is mixed but still not GPU-ready: one
alternate attention layer transfers on the tiny target pair, but it ties
`raw_grad_l2_sq` and lacks held-out shadow stability. See
[docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md](docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md).
The stability board closes the line: at `4` samples per split,
diagonal-Fisher target-transfer AUC is `0.5`, equal to `raw_grad_l2_sq`, with
no strict-tail advantage. See
[docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md](docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md).
The
Kandinsky/Pokemon package skeleton now exists locally at
`response-contract-pokemon-kandinsky-20260511`, but the probe verdict is
`needs_query_split`: real member/nonmember query images and response coverage
are still missing. See
[docs/evidence/blackbox-response-contract-skeleton-create-20260511.md](docs/evidence/blackbox-response-contract-skeleton-create-20260511.md).
The local query-source audit confirms that the available Kandinsky/Pokemon
material is weights-only and cannot fill the package; CelebA/recon artifacts
must not be copied into this asset identity. See
[docs/evidence/blackbox-response-contract-query-source-audit-20260511.md](docs/evidence/blackbox-response-contract-query-source-audit-20260511.md).
`scripts/validate_attack_defense_table.py` now guards the full admitted
consumer set (`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`)
so candidate-only rows cannot silently become product-consumable evidence.
The same admitted set is now exported as a checked machine-readable bundle for
Platform/Runtime consumers, including explicit finite-tail denominators and
false-positive budgets for strict low-FPR interpretation:
[docs/evidence/admitted-evidence-bundle-20260511.md](docs/evidence/admitted-evidence-bundle-20260511.md).
SecMI full-split review upgrades SecMI to an evidence-ready supporting gray-box
reference, but not to admitted Platform/Runtime evidence. See
[docs/evidence/secmi-full-split-admission-boundary-review.md](docs/evidence/secmi-full-split-admission-boundary-review.md).
The supporting-reference boundary is now guarded by
`scripts/validate_secmi_supporting_contract.py`, which is wired into local
checks to block silent admission, GPU release, missing blockers, or malformed
metric rows. The admission-contract hardening pass adds a second
machine-readable artifact that keeps SecMI stat and NNS as
`research-support-only` rows unless a future CPU-first consumer contract is
reviewed:
[docs/evidence/secmi-admission-contract-hardening-20260511.md](docs/evidence/secmi-admission-contract-hardening-20260511.md).
I-B risk-targeted unlearning and I-C cross-permission successor scoping are both
on hold; neither releases GPU work. I-B now has a machine-checkable
defended-shadow / adaptive-attacker reopen protocol, an explicit reopen-mode
guard against undefended threshold references, and a coverage-aware CPU
training manifest that blocks the current target k32 identity contract. It
now also has a CPU shadow-local identity scout: a two-shadow target-risk
remap is mechanically possible for `shadow-01` and `shadow-02`, but it is not
true shadow-local risk scoring. It still lacks shadow-local risk records or an
explicitly approved remapped defended-shadow contract, executed defended-shadow
training, defended-shadow threshold exports, adaptive-attacker metrics, and
retained utility. See
[docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](docs/evidence/ib-risk-targeted-unlearning-successor-scope.md),
[docs/evidence/ib-adaptive-defense-contract-20260511.md](docs/evidence/ib-adaptive-defense-contract-20260511.md),
[docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md),
[docs/evidence/ib-reopen-shadow-reference-guard-20260512.md](docs/evidence/ib-reopen-shadow-reference-guard-20260512.md),
[docs/evidence/ib-defended-shadow-training-manifest-20260512.md](docs/evidence/ib-defended-shadow-training-manifest-20260512.md),
[docs/evidence/ib-shadow-local-identity-scout-20260512.md](docs/evidence/ib-shadow-local-identity-scout-20260512.md),
and
[docs/evidence/ic-cross-permission-successor-scope.md](docs/evidence/ic-cross-permission-successor-scope.md).
CLiD is now guarded as a prompt-conditioned diagnostic candidate rather than
image-identity black-box evidence. See
[docs/evidence/clid-image-identity-boundary-contract-20260511.md](docs/evidence/clid-image-identity-boundary-contract-20260511.md).
The downstream consumer boundary is synchronized: admitted rows remain `recon`,
`PIA`, and `GSA + DPDM W-1`; ReDiffuse, tri-score, cross-box fusion,
H2/simple-distance, CLiD, GSA LR, and black-box response-contract acquisition
remain candidate, negative, hold, or needs-assets states. See
[docs/evidence/research-boundary-consumability-sync-20260510.md](docs/evidence/research-boundary-consumability-sync-20260510.md).
Gray-box tri-score survives as internal Research candidate evidence, but it is
not admitted, not product-facing, and not a GPU release candidate. See
[docs/evidence/graybox-triscore-consolidation-review.md](docs/evidence/graybox-triscore-consolidation-review.md)
and
[docs/evidence/graybox-triscore-truth-hardening-review.md](docs/evidence/graybox-triscore-truth-hardening-review.md).
The systematic black-box response-contract discovery closed as `needs-assets`,
so acquiring or constructing second response-contract assets remains required
before black-box portability validation can run. The post-tri-score intake
refresh also closes as `needs-assets`; the 2026-05-11 scaffold and skeleton
creation roll the concrete candidate id forward from the missing 2026-05-10
placeholder to `response-contract-pokemon-kandinsky-20260511` and freeze the
next package handoff layout without releasing GPU. The query-source audit
blocks local self-fill from existing weights/tensors. See
[docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md](docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md),
[docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md),
[docs/evidence/blackbox-response-contract-skeleton-create-20260511.md](docs/evidence/blackbox-response-contract-skeleton-create-20260511.md),
and
[docs/evidence/blackbox-response-contract-query-source-audit-20260511.md](docs/evidence/blackbox-response-contract-query-source-audit-20260511.md).
The 750k
exact-replay GPU packet completed with `AUC = 0.702293`, but strict-tail
evidence remains weak (`TPR@1%FPR = 0.019231`, `TPR@0.1%FPR = 0.019231`) and
the held-out ResNet accuracy is `0.5`; ReDiffuse stays candidate-only and no
800k shortcut is released. See
[docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md)
and
[docs/evidence/post-rediffuse-next-lane-reselection.md](docs/evidence/post-rediffuse-next-lane-reselection.md).
The black-box response-contract package preflight remains `needs-assets`; see
[docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
and
[docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md).
The package-level preflight is
[docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md).
The repository-level discovery pass also found no ready paired package:
[docs/evidence/blackbox-response-contract-discovery.md](docs/evidence/blackbox-response-contract-discovery.md).
The resting-state audit is
[docs/evidence/research-resting-state-audit-20260510.md](docs/evidence/research-resting-state-audit-20260510.md).
The first post-resting CPU discovery review closed the GSA loss-score LR rescue
path as negative-but-useful; see
[docs/evidence/gsa-loss-score-shadow-stability-review.md](docs/evidence/gsa-loss-score-shadow-stability-review.md).

## Mainline Claims

| Lane | Status | Current claim | Boundary |
| --- | --- | --- | --- |
| Black-box `recon` | admitted | Current black-box product row and minimal-permission risk proof. | Public-100 strict-tail fields are finite-count evidence, not calibrated continuous sub-percent FPR. |
| Gray-box `PIA` | admitted | Strongest admitted local DDPM/CIFAR10 gray-box line; stochastic dropout is a provisional defended comparator. | Bounded repeated-query adaptive review only; low-FPR values are finite empirical tails, not calibrated sub-percent FPR. |
| Gray-box `SecMI` | evidence-ready supporting reference | Full-split SecMI stat and NNS are strong corroborating gray-box evidence. | Not admitted Platform/Runtime evidence until a consumer-boundary and adaptive-review contract is hardened. |
| White-box `GSA + DPDM W-1` | admitted comparator | Strongest white-box risk upper bound plus defended comparator. | Not a final paper-level benchmark. |
| ReDiffuse | candidate-only | Collaborator bundle and 750k checkpoint are runnable; exact replay shows modest AUC but weak strict-tail evidence. | Do not promote; do not run 800k automatically; reopen only with a new scorer hypothesis or stricter paper-faithful contract. |
| Archived gray-box paper candidates | hold | SIMA, Noise-as-Probe, MoFit, and Structural Memorization are reviewed for reentry. | No GPU release; reopen only with a new low-FPR-primary observable or protocol. |
| CLiD / H2 / simple-distance / variation / semantic-aux | hold or candidate-only | Useful diagnostics and bounded candidates. | No GPU task unless a new protocol/data contract clears a CPU preflight. |

## Recent ReDiffuse Gate Verdict

The ReDiffuse gate is closed as candidate-only. The released 750k ResNet parity
packet completed:

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-packet `
  --workspace workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-parity-20260510-gpu-64 `
  --device cuda `
  --max-samples 64 `
  --batch-size 8 `
  --attack-num 1 `
  --interval 200 `
  --average 10 `
  --k 100 `
  --scoring-mode resnet `
  --scorer-train-portion 0.2 `
  --scorer-epochs 15 `
  --scorer-batch-size 128
```

Result: `AUC = 0.411982`, `ASR = 0.538462`, `TPR@1%FPR = 0.0`,
`TPR@0.1%FPR = 0.0`, and best held-out ResNet accuracy `0.5`. Runtime checks
passed, but the scorer is not a viable parity surface at this gate. See
[docs/evidence/rediffuse-resnet-parity-packet.md](docs/evidence/rediffuse-resnet-parity-packet.md).

The follow-up direct-distance boundary review blocks an automatic 800k metrics
packet because it would only test a Research-specific proxy surface. See
[docs/evidence/rediffuse-direct-distance-boundary-review.md](docs/evidence/rediffuse-direct-distance-boundary-review.md).
The checkpoint-portability gate confirms that 750k/800k metadata and the
collaborator split are compatible, but it still blocks GPU because the
paper-faithful scorer contract is unresolved. See
[docs/evidence/rediffuse-checkpoint-portability-gate.md](docs/evidence/rediffuse-checkpoint-portability-gate.md).
The ResNet contract scout resolves the ambiguity against the current adapter:
collaborator `nns_attack` does not update `test_acc_best` and negates logits
before a member-lower ROC, while the Research adapter restores the true best
held-out epoch and uses unnegated logits as higher-is-member scores. See
[docs/evidence/rediffuse-resnet-contract-scout.md](docs/evidence/rediffuse-resnet-contract-scout.md).
The exact replay preflight adds `resnet_collaborator_replay`, preserving the
collaborator checkpoint-selection counter contract while keeping raw logits in
the project metric convention. A 4-sample CPU smoke passed. See
[docs/evidence/rediffuse-exact-replay-preflight.md](docs/evidence/rediffuse-exact-replay-preflight.md).
The bounded 750k exact-replay packet then completed on CUDA. It shows modest
AUC but weak strict-tail evidence and no admitted promotion. See
[docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md).

## Next Decision Contract

1. ReDiffuse is closed as candidate-only for now. Do not run 800k or larger
   ReDiffuse packets without a new scorer hypothesis and CPU preflight.
2. Black-box second response-contract acquisition remains `needs_query_split`.
   It is no longer the immediate active work until real query/response assets
   appear. Do not GPU-scale until the local
   `response-contract-pokemon-kandinsky-20260511` package has at least `25/25`
   real query images, response coverage, and a ready package probe. Existing
   local Kandinsky/Pokemon weights are not query images or responses.
3. The white-box influence/curvature stability decision is closed. The
   `up_blocks.1.attentions.0.to_v` board at `4` samples per split ties
   `raw_grad_l2_sq` under shadow-frozen target transfer, so diagonal-Fisher
   self-influence is `negative-but-useful` and not GPU-ready.
4. Gray-box tri-score truth-hardening used existing X-88/X-141/X-142 artifacts
   only and closed as `positive-but-bounded`. Do not promote to admitted
   evidence and do not run a larger same-contract packet.
5. I-A truth-hardening completed as positive boundary hardening. See
   [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md).
6. Non-gray-box reselection selected a CPU-only black-box response-contract
   acquisition audit. It closed as `needs-assets`, not GPU-ready. The minimum
   acquisition package is specified in
   [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md);
   see also
   [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
   for the audit result and
   [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md).
7. Do not update `docs/evidence/admitted-results-summary.md` unless a reviewed
   packet is explicitly promoted.
8. Boundary-consumability sync and the 2026-05-12 admitted consumer drift audit
   completed without changing Platform or Runtime schemas. Downstream consumers
   should continue using only the admitted rows listed in
   `docs/evidence/admitted-results-summary.md` and exported by
   `workspaces/implementation/artifacts/admitted-evidence-bundle.json`.
9. I-B risk-targeted unlearning is on hold with a frozen defended-shadow reopen
   protocol. Do not GPU-scale the existing threshold-transfer diagnostics; the
   explicit reopen mode now rejects undefended shadow references, and the
   coverage-aware CPU training manifest blocks the current target k32 identity
   contract. The shadow-local identity scout found a mechanically possible
   `shadow-01`/`shadow-02` target-risk remap, but it is not true shadow-local
   risk scoring. Shadow-local risk records or an explicitly approved remapped
   defended-shadow contract, executed defended-shadow training,
   adaptive-attacker metrics, and retained utility are still missing.
10. I-C cross-permission / translated-contract work is on hold until a same-spec
   evaluator and matched random comparator contract exist. The feasibility
   scout confirms the current executable surface is translated-alias-only,
   reports `same_spec_reuse = false`, and emits only a local `1 member /
   1 nonmember` score-gap board. Do not spend CPU/GPU on same-pair replay from
   current artifacts:
   [docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md).
11. Cross-box successor scoping is on hold. Existing executable candidates are
    same-family score-sharing/fusion/support/tail-gated variants or
    asset-blocked response-contract transfer. Reopen only with a new observable
    or ready second response-contract package.
12. I-B defense-aware reopen scout is on hold. The best k32 full-split anchor
    reduces attack-side AUC by `0.021347`, but the review still borrows
    undefended shadow threshold transfer. The protocol audit confirms this is a
    code-level boundary, and the defended-shadow reopen protocol freezes the
    next valid requirements without releasing GPU:
    [docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](docs/evidence/ib-defense-reopen-protocol-audit-20260512.md)
    and
    [docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md).
13. Archived gray-box paper candidates are on hold after reentry review. Do
    not reopen SIMA, Noise-as-Probe, MoFit, or Structural Memorization without
    a genuinely new low-FPR-primary observable or protocol.
14. Mid-frequency same-noise residual scoring is a distinct black-box
    observable gap, not already covered by H2/H3 response-cache filtering.
    Existing caches did not contain `x_t`, `tilde_x_t`, noise provenance, or
    same-noise residuals, so the line first added a scorer, collector,
    synthetic cache writer, and real-asset `4/4` preflight. The frozen `64/64`
    sign-check is candidate-only with `AUC = 0.733398` and finite `4/64`
    zero-FP recovery. The seed-only repeat retained signal with
    `AUC = 0.719238` and finite `3/64` zero-FP recovery. Stop same-contract
    GPU expansion. The comparator audit shows the mid-band does not dominate
    full or low-frequency residual comparators, narrowing the claim to
    same-noise residual distance rather than a proven mid-frequency-specific
    mechanism. Reopen only with a new comparator, second asset, or protocol.

## Long-Running Goal Loop

Every autonomous research cycle must follow this loop:

1. `review`: read this roadmap, reproduction status, admitted results,
   workspace evidence index, challenger queue, and the relevant workspace plan.
2. `select`: choose one bounded question; keep at most one active GPU task.
3. `preflight`: freeze hypothesis, assets, split, metrics, falsifier, GPU cap,
   output path, and stop conditions.
4. `run`: start with CPU/tiny smoke; run at most one bounded GPU packet.
5. `verdict`: classify as `admitted`, `candidate-only`, `hold`, or
   `negative-but-useful`.
6. `sync`: update the evidence note, `ROADMAP.md`,
   `workspaces/implementation/challenger-queue.md`, and the relevant workspace
   plan.
7. `next`: set `next_gpu_candidate = none` unless the next bounded packet is
   explicitly released.

## Current Sidecars

| Sidecar | Mode | Why |
| --- | --- | --- |
| True second membership benchmark | hold / needs genuinely different mechanism | MNIST public-checkpoint raw/x0 and raw-MSE known-split scouts are weak; gradient norm is positive only under extreme overfit, weakens at `16 / 64`, and oracle gradient-prototype alignment is random at `64 / 64`; no GPU. |
| CopyMark external benchmark intake | ready-but-weak / no admitted promotion | Local CommonCanvas/CommonCatalog query split and deterministic `50/50` text-to-image responses are ready. Pixel distance is weak (`AUC = 0.5736`, `TPR@1%FPR = 0.04`), the single CLIP image-similarity follow-up is weak (`AUC = 0.4588`, zero low-FPR recovery), prompt-response consistency is weak (`AUC = 0.4408`), and multi-seed response stability is weak (`4/4`, `AUC = 0.5625`). Close this packet by default. |
| MIDST TabDDPM external benchmark | hold / weak tabular mechanisms | MIDST black-box single-table is locally scoreable with exact labels, but nearest-synthetic-row distance gives only `dev+final AUC = 0.566263`; shadow-trained marginal distributional learning overfits train and collapses to `dev+final AUC = 0.499846`; no TabSyn, white-box MIDST, classifier sweep, or feature-matrix expansion. |
| Kohaku/Danbooru external asset | hold / membership-semantics blocked | Model cards identify broad HakuBooru/Danbooru2023 training sources, but no exact target member list or fixed selection manifest is available; do not download `38-40 GB` weights or TB-scale image assets for pseudo-membership scoring. |
| Fashion-MNIST DDPM PIA-loss scout | hold / weak scout only | `ynwag9/fashion_mnist_ddpm_32` runs on CUDA with real Fashion-MNIST train/test split, but fixed-timestep epsilon-MSE gives only `AUC = 0.535889` and weak low-FPR recovery; no seed/timestep expansion. |
| Beans member-LoRA mechanism scouts | hold / weak known-split family closed | Creating a precise `SD1.5 + Beans-member LoRA` target fixes the old pseudo-membership semantics, but conditional denoising-loss is weak (`AUC = 0.414400`, reverse `0.585600`, `TPR@1%FPR = 0.080000`) and parameter-delta sensitivity is also near-random (`AUC = 0.512000`, `TPR@1%FPR = 0.040000`); no train-step/rank/resolution/prompt/timestep/layer expansion. |
| Noise as a Probe | watch / reproduction-incomplete | Semantic-initial-noise reconstruction is a genuinely different mechanism family, but there is no public code, exact split manifest, released checkpoint, or query/response package; do not implement DDIM inversion or fine-tune SD-v1-4 from scratch. |
| Zenodo fine-tuned diffusion asset | watch / split-manifest blocked | Public paper/code references confirm a reconstruction-based attack workflow, but exact target member/nonmember sample identities are still not exposed; no full archive download, same-line audit, LoRA scoring, or GPU release. |
| CLiD prompt-conditioned boundary | CPU-only | Preserve diagnostic claim boundary; no GPU unless a new image-identity protocol exists. |
| Variation query-contract watch | CPU-only / blocked | Reopen only when real member/nonmember query images and endpoint contract exist. |
| Simple-distance second-asset portability | weak on CommonCanvas | First valid second response contract is ready, but pixel, CLIP image-similarity, prompt-response consistency, and response-stability scorers are weak; do not treat this as transfer evidence. |
| MNIST simple true-membership scorers | CPU-only / closed | Public MNIST/DDPM raw/x0, tiny known-split raw loss, and tiny overfit raw-MSE upperbound are weak; do not expand simple MSE scoring. |
| Beans/SD1.5 response-contract scout | CPU-only / contract-debug only | `25/25` beans query images and `25/25` local SD1.5 responses pass the package probe, but the split is beans train/validation, not proven SD1.5 training membership. |
| Beans/SD1.5 simple-distance scorer | CPU-only / weak pseudo-split debug | Pixel MSE/MAE is near random on the pseudo-member split; do not enlarge this exact score or cite it as true membership evidence. |
| Beans/SD1.5 CLIP-distance scorer | CPU-only / weak pseudo-split debug | Local CLIP distance is weak and wrong-direction under the lower-distance member convention; not true SD1.5 membership evidence. |
| Response-contract package construction | CPU-only / needs assets | Use the 2026-05-11 scaffold as the portable handoff target; no GPU until preflight is ready. |

## Recent Verdicts

| Item | Verdict | Evidence |
| --- | --- | --- |
| Daily Research review | no active GPU candidate or CPU sidecar after Beans LoRA, paperization, MIA_SD, and White-box GSA Zenodo verdicts; next cycle must pass Lane A/B/C gates or stop | [docs/evidence/daily-research-review-20260513.md](docs/evidence/daily-research-review-20260513.md) |
| White-box GSA Zenodo archive verdict | admitted-family archive for the already admitted GSA line; not a new second asset; no full download or GPU release | [docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md](docs/evidence/whitebox-gsa-zenodo-archive-verdict-20260513.md) |
| MIA_SD face-LDM asset verdict | code-and-result-artifacts but private images/checkpoint/split/query-response missing; no download or GPU release | [docs/evidence/miasd-face-ldm-asset-verdict-20260513.md](docs/evidence/miasd-face-ldm-asset-verdict-20260513.md) |
| Paperization consumer boundary | synchronized; recent weak/watch lines remain limitations/future-work only and do not change Platform/Runtime admitted rows | [docs/evidence/paperization-consumer-boundary-20260513.md](docs/evidence/paperization-consumer-boundary-20260513.md) |
| Quantile Regression asset verdict | mechanism-reference but artifact-incomplete; no paper-specific code, target artifacts, split manifest, download, or GPU release | [docs/evidence/quantile-regression-asset-verdict-20260513.md](docs/evidence/quantile-regression-asset-verdict-20260513.md) |
| MIAGM asset verdict | code-reference-only but artifact-incomplete; no target checkpoints, splits, generated distributions, download, or GPU release | [docs/evidence/miagm-asset-verdict-20260513.md](docs/evidence/miagm-asset-verdict-20260513.md) |
| Watch-candidate consumer boundary | admitted-only Platform/Runtime boundary intact after LAION-mi, Zenodo, and Noise as a Probe watch verdicts; no schema change | [docs/evidence/watch-candidate-consumer-boundary-20260513.md](docs/evidence/watch-candidate-consumer-boundary-20260513.md) |
| Noise as a Probe asset verdict | mechanism-relevant but reproduction-incomplete; no code/split/checkpoint artifacts and no GPU release | [docs/evidence/noise-as-probe-asset-verdict-20260513.md](docs/evidence/noise-as-probe-asset-verdict-20260513.md) |
| Zenodo fine-tuned diffusion code reference audit | paper-and-code-backed watch, but split manifest still missing; no full download or GPU release | [docs/evidence/zenodo-code-reference-audit-20260513.md](docs/evidence/zenodo-code-reference-audit-20260513.md) |
| Zenodo fine-tuned diffusion asset verdict | archive-structured but manifest-incomplete; no full download or GPU release | [docs/evidence/zenodo-finetuned-diffusion-asset-verdict-20260513.md](docs/evidence/zenodo-finetuned-diffusion-asset-verdict-20260513.md) |
| LAION-mi URL availability probe | fixed `25/25` probe failed; metadata-only watch; no response generation or GPU release | [docs/evidence/laion-mi-url-availability-probe-20260513.md](docs/evidence/laion-mi-url-availability-probe-20260513.md) |
| LAION-mi asset verdict | metadata-ready but response-not-ready; no GPU release | [docs/evidence/laion-mi-asset-verdict-20260513.md](docs/evidence/laion-mi-asset-verdict-20260513.md) |
| Beans LoRA delta-sensitivity scout | weak known-split internal mechanism verdict; parameter-delta sensitivity closes and Beans LoRA family is no longer expandable | [docs/evidence/beans-lora-delta-sensitivity-20260513.md](docs/evidence/beans-lora-delta-sensitivity-20260513.md) |
| Beans member-LoRA denoising-loss scout | weak known-split internal scout; membership semantics repaired but denoising-loss signal closes | [docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md](docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md) |
| Beans SD1.5 response-contract scout | feasible second-query-dataset package candidate; no GPU release | [docs/evidence/beans-sd15-response-contract-scout-20260512.md](docs/evidence/beans-sd15-response-contract-scout-20260512.md) |
| Beans SD1.5 response-contract package | ready local `25/25` query/response package; no GPU release | [docs/evidence/beans-sd15-response-contract-ready-20260512.md](docs/evidence/beans-sd15-response-contract-ready-20260512.md) |
| Beans SD1.5 simple-distance scout | weak naive pixel-distance signal; no GPU release | [docs/evidence/beans-sd15-simple-distance-scout-20260512.md](docs/evidence/beans-sd15-simple-distance-scout-20260512.md) |
| Beans SD1.5 CLIP-distance scout | weak embedding-distance signal; no GPU release | [docs/evidence/beans-sd15-clip-distance-scout-20260512.md](docs/evidence/beans-sd15-clip-distance-scout-20260512.md) |
| Beans SD1.5 membership semantics correction | contract/debug only; beans split is not proven SD1.5 membership | [docs/evidence/beans-sd15-membership-semantics-correction-20260512.md](docs/evidence/beans-sd15-membership-semantics-correction-20260512.md) |
| MNIST DDPM PIA portability smoke | raw-loss transfer closed unless sharper scorer appears; no GPU release | [docs/evidence/mnist-ddpm-pia-portability-smoke-20260512.md](docs/evidence/mnist-ddpm-pia-portability-smoke-20260512.md) |
| MNIST DDPM x0 reconstruction scout | simple reconstruction residual weak; no GPU release | [docs/evidence/mnist-ddpm-x0-reconstruction-scout-20260512.md](docs/evidence/mnist-ddpm-x0-reconstruction-scout-20260512.md) |
| Tiny known-split denoising sanity | raw denoising loss fails even with controlled train/held-out split; no GPU release | [docs/evidence/tiny-known-split-denoising-sanity-20260512.md](docs/evidence/tiny-known-split-denoising-sanity-20260512.md) |
| External diffusion benchmark provenance scan | no ready external benchmark found; require documented target membership before scoring | [docs/evidence/external-diffusion-benchmark-provenance-scan-20260512.md](docs/evidence/external-diffusion-benchmark-provenance-scan-20260512.md) |
| Tiny overfit MSE upperbound | raw denoising MSE remains weak even when overfitting 8 members; no GPU release | [docs/evidence/tiny-overfit-mse-upperbound-20260512.md](docs/evidence/tiny-overfit-mse-upperbound-20260512.md) |
| Tiny overfit gradient-norm scout | positive mechanism scout on `8 / 64`; no GPU release until stability gate | [docs/evidence/tiny-overfit-gradient-norm-scout-20260512.md](docs/evidence/tiny-overfit-gradient-norm-scout-20260512.md) |
| Gradient-norm stability gate | weakened at `16 / 64`; gradient norm stays mechanism hint only | [docs/evidence/gradient-norm-stability-gate-20260512.md](docs/evidence/gradient-norm-stability-gate-20260512.md) |
| Tiny known-split gradient prototype alignment | weak oracle-style gradient direction scout on `64 / 64`; close same-family final-layer gradient variants by default | [docs/evidence/tiny-known-split-gradient-prototype-alignment-20260513.md](docs/evidence/tiny-known-split-gradient-prototype-alignment-20260513.md) |
| True second membership benchmark scope | scope frozen; choose sharper MNIST/DDPM scorer or tiny known-split target; no GPU release | [docs/evidence/true-second-membership-benchmark-scope-20260512.md](docs/evidence/true-second-membership-benchmark-scope-20260512.md) |
| CopyMark provenance intake | high-value external candidate; manifest inspected; CommonCanvas/CommonCatalog tiny CPU target selected | [docs/evidence/copymark-provenance-intake-20260512.md](docs/evidence/copymark-provenance-intake-20260512.md) |
| CopyMark CommonCanvas query asset | local `50/50` query split ready; deterministic responses generated in P0 | [docs/evidence/copymark-commoncanvas-query-asset-20260512.md](docs/evidence/copymark-commoncanvas-query-asset-20260512.md) |
| CopyMark CommonCanvas response and scorers | package probe `ready`; pixel-distance scorer is weak (`AUC = 0.5736`, `TPR@1%FPR = 0.04`); CLIP image-similarity is weak (`AUC = 0.4588`, zero low-FPR recovery); prompt-response consistency is weak (`AUC = 0.4408`); no admitted promotion | [docs/evidence/copymark-commoncanvas-response-preflight-20260512.md](docs/evidence/copymark-commoncanvas-response-preflight-20260512.md) |
| CopyMark CommonCanvas multi-seed stability | weak bounded scout (`4/4`, `AUC = 0.5625`, `ASR = 0.625`); no seed/subset/embedding expansion | [docs/evidence/copymark-commoncanvas-multiseed-stability-20260513.md](docs/evidence/copymark-commoncanvas-multiseed-stability-20260513.md) |
| Kohaku/Danbooru asset decision | hold; broad training-source provenance is not enough for a clean target member/nonmember split | [docs/evidence/kohaku-danbooru-asset-decision-20260513.md](docs/evidence/kohaku-danbooru-asset-decision-20260513.md) |
| Fashion-MNIST DDPM PIA-loss scout | weak `64/64` CUDA scout on a real train/test split; no admitted promotion and no expansion | [docs/evidence/fashion-mnist-ddpm-pia-loss-scout-20260513.md](docs/evidence/fashion-mnist-ddpm-pia-loss-scout-20260513.md) |
| MIDST TabDDPM nearest-neighbor scout | weak external benchmark scout; `dev+final AUC = 0.566263` and near-zero strict-tail recovery; no admitted promotion and no expansion | [docs/evidence/midst-tabddpm-nearest-neighbor-scout-20260513.md](docs/evidence/midst-tabddpm-nearest-neighbor-scout-20260513.md) |
| MIDST TabDDPM shadow-distributional scout | weak transfer; train shadow `AUC = 0.881991` but dev+final `AUC = 0.499846`; no classifier/feature expansion | [docs/evidence/midst-tabddpm-shadow-distributional-scout-20260513.md](docs/evidence/midst-tabddpm-shadow-distributional-scout-20260513.md) |
| I-B defended-shadow reopen protocol | protocol-frozen; no GPU release; no admitted defense claim | [docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md) |
| I-B reopen shadow-reference guard | ready CPU guard; defended-shadow reopen mode rejects undefended threshold references; no GPU release | [docs/evidence/ib-reopen-shadow-reference-guard-20260512.md](docs/evidence/ib-reopen-shadow-reference-guard-20260512.md) |
| I-B defended-shadow training manifest | blocked CPU manifest; target k32 forget IDs are not covered by shadow member datasets; no training run | [docs/evidence/ib-defended-shadow-training-manifest-20260512.md](docs/evidence/ib-defended-shadow-training-manifest-20260512.md) |
| I-B shadow-local identity scout | blocked semantic scout; `shadow-01`/`shadow-02` remap mechanically possible, but target-level risk records are not true shadow-local scoring | [docs/evidence/ib-shadow-local-identity-scout-20260512.md](docs/evidence/ib-shadow-local-identity-scout-20260512.md) |
| Admitted consumer drift audit | synchronized; no candidate leakage into Platform/Runtime bundle; no schema change | [docs/evidence/admitted-consumer-drift-audit-20260512.md](docs/evidence/admitted-consumer-drift-audit-20260512.md) |
| SecMI consumer-contract review | structural-support-only; not system-consumable; no GPU release | [docs/evidence/secmi-consumer-contract-review-20260512.md](docs/evidence/secmi-consumer-contract-review-20260512.md) |
| I-C same-spec evaluator feasibility | hold; translated-alias probes are not same-spec release surfaces; no GPU release | [docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md) |
| Post-I-B next-lane reselection | select-I-C-same-spec-evaluator-feasibility-scout; no GPU release | [docs/evidence/post-ib-next-lane-reselection-20260512.md](docs/evidence/post-ib-next-lane-reselection-20260512.md) |
| I-B defense reopen protocol audit | hold-structural; active code path borrows undefended shadow threshold transfer; no GPU release | [docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](docs/evidence/ib-defense-reopen-protocol-audit-20260512.md) |
| Post-midfreq next-lane reselection | select-secmi-consumer-contract-review; no GPU release | [docs/evidence/post-midfreq-next-lane-reselection-20260512.md](docs/evidence/post-midfreq-next-lane-reselection-20260512.md) |
| Mid-frequency residual comparator audit | candidate-boundary-narrowed; mid-frequency-specific claim not supported | [docs/evidence/midfreq-residual-comparator-audit-20260512.md](docs/evidence/midfreq-residual-comparator-audit-20260512.md) |
| Mid-frequency residual stability result | candidate-stable-but-bounded; no admitted promotion; stop same-contract GPU | [docs/evidence/midfreq-residual-stability-result-20260512.md](docs/evidence/midfreq-residual-stability-result-20260512.md) |
| Mid-frequency residual stability decision | release-one-stability-probe; no admitted promotion | [docs/evidence/midfreq-residual-stability-decision-20260512.md](docs/evidence/midfreq-residual-stability-decision-20260512.md) |
| Mid-frequency residual 64/64 sign-check | candidate-only; bounded signal present; no admitted promotion | [docs/evidence/midfreq-residual-signcheck-20260512.md](docs/evidence/midfreq-residual-signcheck-20260512.md) |
| Mid-frequency residual real-asset preflight | real-asset-tiny-cache-ready; no GPU release; no admitted evidence | [docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](docs/evidence/midfreq-residual-real-asset-preflight-20260512.md) |
| Mid-frequency residual tiny runner contract | tiny-runner-schema-ready; real-asset preflight complete; no GPU release | [docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md) |
| Mid-frequency residual collector contract | collector-function-ready; synthetic tiny runner now follows; no GPU release | [docs/evidence/midfreq-residual-collector-contract-20260512.md](docs/evidence/midfreq-residual-collector-contract-20260512.md) |
| Mid-frequency residual scorer contract | scorer-contract-ready; collector and synthetic tiny runner now follow; no GPU release | [docs/evidence/midfreq-residual-scorer-contract-20260512.md](docs/evidence/midfreq-residual-scorer-contract-20260512.md) |
| Mid-frequency same-noise residual preflight | distinct observable gap, but blocked by missing residual cache fields; no GPU release | [docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](docs/evidence/midfreq-same-noise-residual-preflight-20260512.md) |
| ReDiffuse collaborator bundle intake | positive intake, candidate-only | [docs/evidence/rediffuse-collaborator-bundle-intake.md](docs/evidence/rediffuse-collaborator-bundle-intake.md) |
| ReDiffuse 750k direct-distance 64/64 | positive compatibility packet, not admitted | [docs/evidence/rediffuse-cifar10-small-packet.md](docs/evidence/rediffuse-cifar10-small-packet.md) |
| ReDiffuse 800k runtime probe | runtime-compatible, metrics not run | [docs/evidence/rediffuse-800k-runtime-probe.md](docs/evidence/rediffuse-800k-runtime-probe.md) |
| ReDiffuse 750k ResNet parity | negative-but-useful; scoring-contract unresolved | [docs/evidence/rediffuse-resnet-parity-packet.md](docs/evidence/rediffuse-resnet-parity-packet.md) |
| ReDiffuse direct-distance boundary | closed as candidate-only; no GPU release | [docs/evidence/rediffuse-direct-distance-boundary-review.md](docs/evidence/rediffuse-direct-distance-boundary-review.md) |
| ReDiffuse checkpoint-portability gate | blocked-by-scoring-contract; 800k metrics shortcut remains closed | [docs/evidence/rediffuse-checkpoint-portability-gate.md](docs/evidence/rediffuse-checkpoint-portability-gate.md) |
| ReDiffuse ResNet contract scout | blocked-by-contract-mismatch; current adapter is not exact collaborator replay | [docs/evidence/rediffuse-resnet-contract-scout.md](docs/evidence/rediffuse-resnet-contract-scout.md) |
| ReDiffuse exact replay preflight | CPU preflight passed; no GPU release | [docs/evidence/rediffuse-exact-replay-preflight.md](docs/evidence/rediffuse-exact-replay-preflight.md) |
| ReDiffuse 750k exact replay | candidate-only; modest AUC but weak strict-tail evidence | [docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md) |
| Post-ReDiffuse reselection | selects black-box second response-contract acquisition; no GPU release | [docs/evidence/post-rediffuse-next-lane-reselection.md](docs/evidence/post-rediffuse-next-lane-reselection.md) |
| Gray-box tri-score consolidation | positive-but-bounded internal evidence; no admitted promotion | [docs/evidence/graybox-triscore-consolidation-review.md](docs/evidence/graybox-triscore-consolidation-review.md) |
| Gray-box tri-score truth-hardening | positive-but-bounded internal evidence; no admitted promotion and no GPU release | [docs/evidence/graybox-triscore-truth-hardening-review.md](docs/evidence/graybox-triscore-truth-hardening-review.md) |
| PIA stochastic-dropout truth-hardening | positive boundary hardening; no GPU release | [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md) |
| Non-gray-box reselection | selected black-box response-contract acquisition audit; no GPU release | [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md) |
| Black-box response-contract acquisition audit | needs-assets; no GPU release | [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md) |
| Black-box response-contract asset spec | needs-assets; minimum second-asset package defined; no GPU release | [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) |
| Black-box response-contract package preflight | needs-assets; Kandinsky/Pokemon has weights but no query/response package | [docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md) |
| Black-box response-contract discovery | needs-assets; no paired package found under black-box dataset/supplementary roots | [docs/evidence/blackbox-response-contract-discovery.md](docs/evidence/blackbox-response-contract-discovery.md) |
| Black-box response-contract second-asset intake | needs-assets; no ready package after post-tri-score refresh | [docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md](docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md) |
| Black-box response-contract protocol scaffold | CPU-only scaffold dry-run; needs-assets; no GPU release | [docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md) |
| Black-box response-contract skeleton create | local skeleton created; needs query split; no GPU release | [docs/evidence/blackbox-response-contract-skeleton-create-20260511.md](docs/evidence/blackbox-response-contract-skeleton-create-20260511.md) |
| Black-box response-contract query-source audit | needs-assets; local Kandinsky/Pokemon material is weights-only | [docs/evidence/blackbox-response-contract-query-source-audit-20260511.md](docs/evidence/blackbox-response-contract-query-source-audit-20260511.md) |
| Post-response-contract reselection | CPU-only system-consumable admitted evidence hardening; no GPU release | [docs/evidence/post-response-contract-reselection-20260511.md](docs/evidence/post-response-contract-reselection-20260511.md) |
| Admitted evidence bundle | synchronized; complete admitted consumer set exported as checked machine-readable bundle | [docs/evidence/admitted-evidence-bundle-20260511.md](docs/evidence/admitted-evidence-bundle-20260511.md) |
| SecMI full-split admission boundary | evidence-ready supporting reference; not admitted | [docs/evidence/secmi-full-split-admission-boundary-review.md](docs/evidence/secmi-full-split-admission-boundary-review.md) |
| SecMI admission contract hardening | supporting-reference-hardened; not admitted; no GPU release | [docs/evidence/secmi-admission-contract-hardening-20260511.md](docs/evidence/secmi-admission-contract-hardening-20260511.md) |
| Post-SecMI next-lane reselection | selects CPU-first white-box influence/curvature feasibility scout; no GPU release | [docs/evidence/post-secmi-next-lane-reselection-20260511.md](docs/evidence/post-secmi-next-lane-reselection-20260511.md) |
| White-box influence/curvature feasibility | CPU contract ready; assets ready with workspace-scoped GSA checkout; no GPU release | [docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md](docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md) |
| GSA diagonal-Fisher micro-board | negative-but-useful; selected-layer raw gradients are extractable, but the score fails target transfer and no GPU is released | [docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md](docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md) |
| GSA diagonal-Fisher layer scope | mixed-but-not-gpu-ready; one layer transfers on a tiny pair but ties `raw_grad_l2_sq` | [docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md](docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md) |
| GSA diagonal-Fisher stability board | negative-but-useful; the only transferring layer ties `raw_grad_l2_sq` at `4` samples per split, closing the line | [docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md](docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md) |
| Post-Fisher next-lane reselection | selects CPU-only I-A finite-tail / adaptive boundary hardening; no GPU release | [docs/evidence/post-fisher-next-lane-reselection-20260511.md](docs/evidence/post-fisher-next-lane-reselection-20260511.md) |
| I-A finite-tail / adaptive boundary audit | synchronized; admitted strict-tail and adaptive-language boundaries remain guarded | [docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md](docs/evidence/ia-finite-tail-adaptive-boundary-audit-20260511.md) |
| Cross-box successor scope | hold; no genuinely new CPU/GPU successor hypothesis is ready | [docs/evidence/cross-box-successor-scope-20260512.md](docs/evidence/cross-box-successor-scope-20260512.md) |
| I-B defense-aware reopen scout | hold; current I-B evidence is not defense-aware and releases no GPU | [docs/evidence/ib-defense-aware-reopen-scout-20260512.md](docs/evidence/ib-defense-aware-reopen-scout-20260512.md) |
| Gray-box paper-candidate reentry | hold; archived paper candidates do not release CPU/GPU work from current artifacts | [docs/evidence/graybox-paper-candidate-reentry-review-20260512.md](docs/evidence/graybox-paper-candidate-reentry-review-20260512.md) |
| Research boundary-consumability sync | synchronized admitted-vs-candidate boundary; no schema change | [docs/evidence/research-boundary-consumability-sync-20260510.md](docs/evidence/research-boundary-consumability-sync-20260510.md) |
| I-B risk-targeted unlearning successor scope | hold-protocol-frozen; no GPU release until executed defended-shadow training, adaptive-attacker metrics, and retained utility are available | [docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](docs/evidence/ib-risk-targeted-unlearning-successor-scope.md) |
| I-C cross-permission successor scope | hold; no GPU release until same-spec evaluator and matched comparator exist | [docs/evidence/ic-cross-permission-successor-scope.md](docs/evidence/ic-cross-permission-successor-scope.md) |
| Research resting-state audit | temporary resting state; no active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive | [docs/evidence/research-resting-state-audit-20260510.md](docs/evidence/research-resting-state-audit-20260510.md) |
| GSA loss-score shadow stability | negative-but-useful; LR distinct-scorer rescue path fails leave-one-shadow-out gate | [docs/evidence/gsa-loss-score-shadow-stability-review.md](docs/evidence/gsa-loss-score-shadow-stability-review.md) |
| Recon product row | admitted black-box row | [docs/evidence/recon-product-validation-result.md](docs/evidence/recon-product-validation-result.md) |
| Semantic-aux low-FPR review | negative-but-useful | [docs/evidence/semantic-aux-low-fpr-review.md](docs/evidence/semantic-aux-low-fpr-review.md) |

## Key Source Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- Verified results: [docs/evidence/admitted-results-summary.md](docs/evidence/admitted-results-summary.md)
- Innovation map: [docs/evidence/innovation-evidence-map.md](docs/evidence/innovation-evidence-map.md)
- Workspace index: [docs/evidence/workspace-evidence-index.md](docs/evidence/workspace-evidence-index.md)
- Active queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)
- Gray-box plan: [workspaces/gray-box/plan.md](workspaces/gray-box/plan.md)
- Product bridge: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed. The current consumer rule is
to use only the five admitted bundle rows (`recon`, `PIA baseline`,
`PIA defended`, `GSA`, and `DPDM W-1`) and keep ReDiffuse, SecMI stat/NNS,
tri-score, cross-box fusion, H2/simple-distance, CLiD, GSA LR,
response-contract acquisition, I-B, and I-C out of product-facing admitted
evidence. If a future result changes exported fields, report format, or
recommendation logic, create a handoff note under `docs/product-bridge/`
before changing sibling repositories.
