# 产品桥接

本目录说明 Research 如何向 DiffAudit Platform 和 Runtime 输送结果。

Platform 只应消费具有明确状态和清晰局限性的结果。Research 提供三类输出：

| 输出 | 含义 |
| --- | --- |
| 已验证结果 | 经审查的实验结果，可作为审计证据展示。 |
| 候选结果 | 对内部比较有用的结果，但尚未准备好供外部使用。 |
| 约束说明 | 已知局限性，防止 Platform UI 中的过度声明。 |

当前跨审计线路状态：跨审计线路评分共享仅为候选。它可以为内部排序和未来研究方向选择提供参考，但在低 FPR 稳定性确立之前不应作为准入的 Platform 证据出现。参见
[../evidence/cross-box-boundary-status.md](../evidence/cross-box-boundary-status.md)。

当前边界可消费性状态：Platform 和 Runtime 只应消费五个准入捆绑包行（`recon`、`PIA baseline`、`PIA defended`、`GSA` 和 `DPDM W-1`），除非未来的审查晋升显式更改此规则。ReDiffuse、SecMI stat/NNS、三评分、跨审计线路融合、GSA LR、H2/simple-distance、CLiD、黑盒响应合约获取、I-B 和 I-C 为候选、支撑参考、负面、暂缓或需要资产状态。近期的第二资产和机制检查也仅为 Research：CommonCanvas / CopyMark、MIDST TabDDPM、Beans LoRA、Quantile Regression、MIAGM、LAION-mi、Zenodo fine-tuned diffusion、Noise as a Probe、Kohaku / Danbooru、MIDM、StablePrivateLoRA、FMIA frequency-component diffusion MIA、SimA score-based diffusion MIA、Tracing the Roots diffusion-trajectory feature-packet MIA、ReproMIA withdrawn proactive MIA、Noise Aggregation small-noise diffusion MIA、GenAI Confessions black-box image-to-image MIA、DurMI TTS duration-loss MIA、LSA-Probe music diffusion MIA、FERMI multi-relational tabular MIA、MT-MIA relational tabular diffusion MIA score packets、Shake-to-Leak fine-tuning-amplified generative privacy code release、TMIA-DM temporal-noise / noise-gradient diffusion MIA、FSECLab MIA-Diffusion DDIM/DCGAN code release、DualMD/DistillMD disjoint-split defense、SAMA diffusion-language-model membership、VidLeaks text-to-video membership 以及 GGDM graph generative diffusion membership 为弱、观察、仅元数据、防御观察、相关方法、范围外、评分包缺失、代码公开结果缺失、正面但溯源受限、已撤回、仅论文源或工件不完整的线路。它们不改变准入行、Runtime 模式、推荐逻辑、防御声明或 Platform 产品文案。参见
[../evidence/paperization-consumer-boundary-20260513.md](../evidence/paperization-consumer-boundary-20260513.md)
和
[../evidence/watch-candidate-consumer-boundary-20260513.md](../evidence/watch-candidate-consumer-boundary-20260513.md)。
另见
[../evidence/cross-modal-watch-consumer-boundary-20260515.md](../evidence/cross-modal-watch-consumer-boundary-20260515.md)。
参见
[../evidence/admitted-consumer-drift-audit-20260515.md](../evidence/admitted-consumer-drift-audit-20260515.md)、
[../evidence/admitted-consumer-drift-audit-20260512.md](../evidence/admitted-consumer-drift-audit-20260512.md)
和
[../evidence/research-boundary-consumability-sync-20260510.md](../evidence/research-boundary-consumability-sync-20260510.md)。
准入行守卫现在由 `scripts/validate_attack_defense_table.py` 强制执行，该脚本在本地检查通过之前验证完整的准入消费方集合。参见
[../evidence/post-response-contract-reselection-20260511.md](../evidence/post-response-contract-reselection-20260511.md)。
多行机器可读的准入证据捆绑包为
[`../../workspaces/implementation/artifacts/admitted-evidence-bundle.json`](../../workspaces/implementation/artifacts/admitted-evidence-bundle.json)，其合约记录在
[admitted-evidence-bundle.md](admitted-evidence-bundle.md)。

当前 CLiD 状态：CLiD 仅为候选。官方 GitHub `inter_output/*` 包现可在 CPU 上干净重放，且在官方阈值路径下表现强劲（`AUC = 0.961277`、`TPR@1%FPR = 0.675470`、`ASR = 0.891957`），但证据仍受提示条件约束且未解决图像身份边界。后续身份清单关卡发现仅有数值评分行、无公开行清单或 COCO 图像 ID 绑定，且 `mia_COCO.zip` 的认证 HEAD/Range 访问返回 `403`；2026-05-15 实时访问复查对认证 `HEAD`、起始 `Range` 和结束 `Range` 探测仍返回 `403`。机器可读候选卡片仅为 Research/产品边界比较而存在；在产品桥接交接定义图像身份安全协议之前，它不得作为准入 Platform 证据或 Runtime 行出现。参见
[clid-candidate-evidence-card.md](clid-candidate-evidence-card.md)、
[../evidence/clid-identity-manifest-gate-20260515.md](../evidence/clid-identity-manifest-gate-20260515.md)、
[../evidence/clid-official-inter-output-replay-20260515.md](../evidence/clid-official-inter-output-replay-20260515.md)
和
[../evidence/clid-prompt-conditioning-boundary.md](../evidence/clid-prompt-conditioning-boundary.md)。

当前 Tracing the Roots 状态：仅 Research 正面特征包证据。OpenReview 补充材料提供固定的 CIFAR10 扩散轨迹特征张量和重放代码，有界本地线性重放达到 `AUC = 0.815826`、`accuracy = 0.737500`、`TPR@1%FPR = 0.134000` 和 `TPR@0.1%FPR = 0.038000`。它不得作为准入 Platform 证据行或 Runtime 模式输入，因为公开包缺少原始目标检查点身份、原始成员/外部样本 ID 以及图像查询/响应工件。机器可读候选卡片仅为 Research/产品边界比较而存在；在非黑盒特征包消费方交接显式定义这些语义之前，它不得作为准入 Platform 证据或 Runtime 行出现。参见
[tracing-roots-candidate-evidence-card.md](tracing-roots-candidate-evidence-card.md)
和
[../evidence/tracing-roots-feature-packet-mia-20260515.md](../evidence/tracing-roots-feature-packet-mia-20260515.md)。

当前 ReproMIA 状态：仅 Research 已撤回论文源观察。当前 arXiv 记录已被撤回，历史 v1 源仅为 TeX 加图，尽管报告了 DDPM 和 Stable Diffusion 表格度量。它没有官方公开代码、目标检查点、精确划分清单、评分数组、ROC CSV 或度量 JSON。它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作出现。参见
[../evidence/repromia-withdrawn-artifact-gate-20260515.md](../evidence/repromia-withdrawn-artifact-gate-20260515.md)。

当前 Noise Aggregation 状态：仅 Research 论文源观察。arXiv `2510.21783` v2 报告了强劲的 DDPM 论文度量和一个独特的小噪声预测噪声聚合机制，但公开源仅为 TeX、参考文献和图片。它没有官方公开代码、目标检查点、精确划分清单、评分数组、ROC CSV、度量 JSON 或查询/响应包。它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作出现。参见
[../evidence/noise-aggregation-small-noise-artifact-gate-20260515.md](../evidence/noise-aggregation-small-noise-artifact-gate-20260515.md)。

当前 FMIA 状态：仅 Research 观察加。OpenReview 补充材料提供频率滤波 DDIM/Stable Diffusion 攻击代码和精确划分清单，但没有训练检查点、评分数组、ROC/度量工件、生成样本或就绪验证器包。它不得作为准入 Platform 证据或 Runtime 行出现。参见
[../evidence/fmia-openreview-frequency-artifact-gate-20260515.md](../evidence/fmia-openreview-frequency-artifact-gate-20260515.md)。

当前 SimA 状态：仅 Research 观察加。官方 GitHub 仓库提供基于评分的 MIA 代码和脚本，但公开发布有空划分和检查点链接、无发布资产、无提交的非供应商划分清单、无目标检查点、无评分数组、无 ROC/度量 JSON 且无就绪验证器包。它不得作为准入 Platform 证据或 Runtime 行出现。参见
[../evidence/sima-scorebased-artifact-gate-20260515.md](../evidence/sima-scorebased-artifact-gate-20260515.md)。

当前 GenAI Confessions 状态：仅 Research 边界观察。公开发布有 STROLL、Carlini 和 Midjourney 设置的训练内/训练外图像输入，但不提供微调 STROLL 检查点、生成的图像到图像响应、DreamSim 距离向量、ROC/度量工件、Midjourney 查询日志或就绪验证器包。它不得作为准入 Platform 证据或 Runtime 行出现。参见
[../evidence/genai-confessions-black-box-artifact-gate-20260515.md](../evidence/genai-confessions-black-box-artifact-gate-20260515.md)。

当前 DurMI 状态：仅 Research TTS/音频跨模态观察加。OpenReview 补充材料提供 GradTTS/WaveGrad2/VoiceFlow 攻击代码和精确的 GradTTS LJSpeech `5,977 / 5,977` 成员/非成员划分；Zenodo 发布了所需音频数据集和检查点的开放元数据。它仍不得作为准入 Platform 证据或 Runtime 行，因为它不提供就绪的时长损失评分数组、ROC 数组、度量 JSON 或生成的结果图表，且 DiffAudit 尚未打开 TTS/音频消费方审计线路。参见
[../evidence/durmi-tts-artifact-gate-20260515.md](../evidence/durmi-tts-artifact-gate-20260515.md)。

当前 LSA-Probe 状态：仅 Research 音乐/音频跨模态观察加。论文和演示是公开的，但项目仓库没有实现、目标身份、精确划分清单、真实的对抗成本评分数组、ROC 工件、度量 JSON 或就绪验证器。可见的演示 `data/*.json` 文件是生成的模拟数据，而非论文证据。除非存在真实的公开工件和音乐/音频消费方边界决策，否则它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作。参见
[../evidence/lsaprobe-music-diffusion-mock-data-gate-20260515.md](../evidence/lsaprobe-music-diffusion-mock-data-gate-20260515.md)。

当前 Shake-to-Leak 状态：仅 Research 代码公开观察加。官方 `VITA-Group/Shake-to-Leak` 仓库提供微调放大的生成隐私代码、内置 SecMI/diffusers 代码、微调脚本、SecMI 脚本、数据提取代码和 `40` 域人物列表。它不提供冻结目标检查点、不可变成员/非成员清单、生成的隐私集合图像、生成的攻击响应、评分数组、ROC 数组、度量 JSON 或就绪验证器输出。除非出现公开的检查点绑定评分工件和不可变成员语义，否则它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作。参见
[../evidence/shake-to-leak-code-artifact-gate-20260515.md](../evidence/shake-to-leak-code-artifact-gate-20260515.md)。

当前 TMIA-DM 状态：仅 Research 论文源观察。《Temporal Membership Inference Attack Method for Diffusion Models》的 CRAD 文章报告了时间噪声/噪声梯度扩散 MIA 机制和论文表格度量，但文章页面列出 `资源附件(0)` 且无官方代码、目标检查点、不可变划分清单、评分数组、ROC 数组、度量 JSON 或验证器输出公开。除非官方公开代码加上检查点绑定的目标/划分工件和可复用评分包出现，否则它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作。参见
[../evidence/tmia-dm-temporal-artifact-gate-20260515.md](../evidence/tmia-dm-temporal-artifact-gate-20260515.md)。

当前 FSECLab MIA-Diffusion 状态：仅 Research 代码公开观察加。官方 `fseclab-osaka/mia-diffusion` 仓库提供 DDIM/DCGAN 训练、采样、白盒攻击、黑盒攻击、数据集加载器和 ROC 评估代码，以及两个 FID 统计 `.npz` 文件。它不提供冻结目标检查点、不可变成员/非成员划分清单、生成样本包、原始评分数组、ROC 数组、度量 JSON 或就绪验证器输出。除非公开的检查点绑定评分工件出现，否则它不得作为准入 Platform 证据、Runtime 模式输入或活跃 GPU/CPU 工作。参见
[../evidence/fseclab-mia-diffusion-code-artifact-gate-20260515.md](../evidence/fseclab-mia-diffusion-code-artifact-gate-20260515.md)。

当前 DualMD/DistillMD 状态：仅 Research 防御观察加。OpenReview DDMD 补充材料提供 DDPM/LDM 训练、分离教师、蒸馏、PIA/SecMIA、黑盒攻击代码、DDPM 划分索引文件和 FID 统计，但嵌入的 GitHub 源不公开，且不提供冻结检查点、防御/非防御评分行、ROC 数组、度量 JSON、生成响应包或就绪验证器。它不得作为准入 Platform 证据或 Runtime 行出现。参见
[../evidence/dualmd-distillmd-defense-artifact-gate-20260515.md](../evidence/dualmd-distillmd-defense-artifact-gate-20260515.md)。

当前 FERMI 状态：仅 Research 表格数据观察。arXiv 源报告了强劲的多关系 TabDDPM/TabDiff/TabSyn 成员度量，但公开表没有代码树、目标/划分清单、生成合成表、特征/评分行、ROC 数组、度量 JSON 或重放命令。它不得作为准入 Platform 证据或 Runtime 行出现，且不重新打开 MIDST/表格执行。参见
[../evidence/fermi-tabular-artifact-gate-20260515.md](../evidence/fermi-tabular-artifact-gate-20260515.md)。

当前 MT-MIA 状态：仅 Research 关系表格支撑证据。官方 `joshward96/MT-MIA` 仓库发布多表成员/非成员/参考划分、预生成的 ClavaDDPM 和 RelDiff 合成输出以及 `18` 个官方 MT-MIA 评分/度量 JSONL 包。它不得作为准入 Platform 证据或 Runtime 行出现，因为当前产品边界是图像/潜在扩散、这些包不是适合产品准入的行 ID 绑定评分清单、且不存在关系表格消费方模式。参见
[../evidence/mtmia-relational-diffusion-score-packet-gate-20260515.md](../evidence/mtmia-relational-diffusion-score-packet-gate-20260515.md)。

当前 recon 状态：recon 是已准入的黑盒产品行。活跃行使用统一的上游阈值度量源并报告全部四个头条度量。参见
[recon-product-validation-handoff.md](recon-product-validation-handoff.md)。
机器可读的产品证据卡片为
[`../../workspaces/implementation/artifacts/recon-product-evidence-card.json`](../../workspaces/implementation/artifacts/recon-product-evidence-card.json)，其合约记录在
[recon-product-evidence-card.md](recon-product-evidence-card.md)。

当前 H2 图像到图像简单距离状态：simple-distance 信号在 SD1.5/CelebA 式合约上拥有有界单资产证据，但尚不是 Platform 行。将其视为 Research 侧候选，用于未来与 recon 的产品桥接比较。参见
[../evidence/h2-img2img-simple-distance-admission-result.md](../evidence/h2-img2img-simple-distance-admission-result.md)。
当前产品桥接决策记录在
[h2-simple-distance-product-bridge-comparison.md](h2-simple-distance-product-bridge-comparison.md)。

## 文档

| 文档 | 用途 |
| --- | --- |
| [runtime.md](runtime.md) | Runtime 集成笔记。 |
| [asset-registry-local-api.md](asset-registry-local-api.md) | 供 Runtime 消费方使用的数据注册合约。 |
| [local-api.md](local-api.md) | 历史本地 API 笔记。 |
| [recon-artifact-replay-guidance.md](recon-artifact-replay-guidance.md) | 如何解读 recon 调试追踪。 |
| [recon-product-validation-handoff.md](recon-product-validation-handoff.md) | 已晋升的 recon 黑盒行的当前产品边界。 |
| [recon-product-evidence-card.md](recon-product-evidence-card.md) | 已准入 recon 行的机器可读产品卡片。 |
| [admitted-evidence-bundle.md](admitted-evidence-bundle.md) | 完整准入 Platform/Runtime 消费方集合的机器可读捆绑包。 |
| [clid-candidate-evidence-card.md](clid-candidate-evidence-card.md) | 官方 CLiD CPU 评分包重放及身份阻断项的机器可读仅候选卡片。 |
| [tracing-roots-candidate-evidence-card.md](tracing-roots-candidate-evidence-card.md) | Tracing Roots 正面特征包重放及原始溯源阻断项的机器可读仅候选卡片。 |
| [h2-simple-distance-product-bridge-comparison.md](h2-simple-distance-product-bridge-comparison.md) | simple-distance 为何仍为 Research 证据以及产品消费前必须满足的条件。 |
| [../evidence/admitted-consumer-drift-audit-20260515.md](../evidence/admitted-consumer-drift-audit-20260515.md) | 准入 Platform/Runtime 消费方边界的最新无漂移审计。 |
| [../evidence/admitted-consumer-drift-audit-20260512.md](../evidence/admitted-consumer-drift-audit-20260512.md) | 准入 Platform/Runtime 消费方边界的前一次无漂移审计。 |
| [../evidence/research-boundary-consumability-sync-20260510.md](../evidence/research-boundary-consumability-sync-20260510.md) | 面向下游消费方的当前准入 vs 候选边界。 |

## 集成规则

- Platform 文案必须反映实际实验状态。
- 不要将烟雾测试或负面结果呈现为已验证的审计方法。
- Runtime 集成需要稳定的输入/输出合约。
- 在跨仓库更改模式或报告格式之前，首先在此处创建交接笔记。
