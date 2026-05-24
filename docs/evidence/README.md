# 证据

本目录包含公开证据概览。

| 文档 | 用途 |
| --- | --- |
| [reproduction-status.md](reproduction-status.md) | 各审计线路复现状态阶段。 |
| [admitted-results-summary.md](admitted-results-summary.md) | 已审查验证的结果摘要。 |
| [innovation-evidence-map.md](innovation-evidence-map.md) | 研究声明到证据状态的映射。 |
| [cross-box-boundary-status.md](cross-box-boundary-status.md) | 当前跨盒候选边界与下一个研究问题。 |
| [github-lightweight-diffusion-mia-triage-20260515.md](github-lightweight-diffusion-mia-triage-20260515.md) | 轻量级/课程式直接扩散 MIA 仓库的 GitHub 误报精简筛查，这些仓库无 target/split/response/score/ROC/metric/verifier 产物，无下载，无 GPU 释放，无已确认行。 |
| [deb-medical-diffusion-artifact-gate-20260515.md](deb-medical-diffusion-artifact-gate-20260515.md) | DEB 医学扩散产物关卡；纯论文来源的灰盒离散码书/中间轨迹 MIA 机制监视项，无代码、无 target/split/score/ROC/metric 产物、无验证器、无下载、无 GPU 释放、无已确认行。 |
| [daily-research-review-20260515.md](daily-research-review-20260515.md) | DSiRe / LoRA-WiSE 与 CPSample 关卡之后的进度审查；确认无活跃 GPU、无 CPU sidecar、无 Platform/Runtime 漂移，以及干净的下一个关卡选择规则。 |
| [cpsample-defense-artifact-gate-20260515.md](cpsample-defense-artifact-gate-20260515.md) | CPSample 防御产物关卡；ICLR OpenReview 补充材料提供扩散/分类器代码和小段攻击损失文本，但无 checkpoint 绑定的行/指标/验证器产物，因此无下载、无 GPU 释放、无已确认行。 |
| [identity-focused-inference-extraction-artifact-gate-20260523.md](identity-focused-inference-extraction-artifact-gate-20260523.md) | Identity-Focused Inference / Extraction 关卡；arXiv `2410.10177` 为纯论文来源的身份级隐私证据，无官方代码、无 checkpoint 绑定的身份/行/score/ROC/metric/验证器产物，无下载、无 GPU 释放、无已确认行。 |
| [rapta-admcd-copying-mitigation-artifact-gate-20260523.md](rapta-admcd-copying-mitigation-artifact-gate-20260523.md) | RAPTA / ADMCD 复制与记忆化缓解关卡；arXiv `2603.13070` 为纯论文来源，无官方代码、无 checkpoint 绑定的行/score/ROC/metric/验证器产物，无下载、无 GPU 释放、无已确认行。 |
| [guard-surgical-mitigation-artifact-gate-20260523.md](guard-surgical-mitigation-artifact-gate-20260523.md) | GUARD 手术式记忆化缓解关卡；官方 `kairanzhao/GUARD` 代码公开，但未发布 checkpoint 绑定的行/score/ROC/metric/验证器产物，因此无下载、无 GPU 释放、无已确认行。 |
| [baf-lora-parameter-space-mitigation-gate-20260523.md](baf-lora-parameter-space-mitigation-gate-20260523.md) | BAF LoRA 参数空间缓解关卡；arXiv `2605.10439` 为仅权重 LoRA 记忆化缓解监视项，仅有补充代码声明，无公开 score/ROC/metric 产物，无下载、无 GPU 释放、无已确认行。 |
| [dsire-lora-wise-dataset-size-boundary-20260515.md](dsire-lora-wise-dataset-size-boundary-20260515.md) | DSiRe / LoRA-WiSE 数据集规模边界关卡；官方代码和公开 LoRA 权重 benchmark 是未来较强的仅权重隐私证据，但其声明为聚合数据集规模恢复而非逐样本 MIA，因此无下载、无 GPU 释放、无已确认行。 |
| [hyperfree-secmi-reproduction-gate-20260515.md](hyperfree-secmi-reproduction-gate-20260515.md) | 无超参 SecMI 复现关卡；第三方 SecMI 系列代码/报告表面，声称有 CIFAR-100 指标，但无可复用的 score 行、ROC 数组、指标 JSON、验证器、下载、GPU 释放或已确认行。 |
| [dme-dual-model-entropy-artifact-gate-20260515.md](dme-dual-model-entropy-artifact-gate-20260515.md) | DME 双模型熵关卡；官方复杂度偏差扩散 MIA 仓库仅 README，无代码、论文链接、划分/checkpoint/score/ROC/metric 产物、验证器、下载、GPU 释放或已确认行。 |
| [fremia-frequency-filter-artifact-gate-20260515.md](fremia-frequency-filter-artifact-gate-20260515.md) | FreMIA 频率过滤关卡；ICML 2026 直接扩散 MIA，有论文表格/图表和存根官方仓库，但无代码、划分/checkpoint/score/ROC/metric 产物、验证器、下载、GPU 释放或已确认行。 |
| [copymark-official-score-artifact-gate-20260515.md](copymark-official-score-artifact-gate-20260515.md) | 官方 CopyMark score 产物关卡；member/nonmember 日志、聚合 ROC/阈值 JSON、选定 score tensor 及 laion_ridar/mixing 结果已公开，但无紧凑的行 ID 绑定 score 清单、checkpoint 哈希、小型不可变数据包、现成验证器、下载、GPU 释放或已确认行。 |
| [cross-box-successor-scope-20260512.md](cross-box-successor-scope-20260512.md) | 纯 CPU 的后续范围界定，将跨盒关闭为 hold 状态，直到出现新的可观测信号或第二个响应合约包。 |
| [black-box-response-strength-preflight.md](black-box-response-strength-preflight.md) | H2 响应强度候选状态与最新验证结论。 |
| [h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md) | 冻结的 CPU 合约，用于判断 H2 低通是否值得再分配一个有边界的 GPU 数据包。 |
| [midfreq-same-noise-residual-preflight-20260512.md](midfreq-same-noise-residual-preflight-20260512.md) | 针对独立中频同噪残差可观测信号的纯 CPU 缓存审计；在有残差缓存之前阻止 GPU。 |
| [midfreq-residual-scorer-contract-20260512.md](midfreq-residual-scorer-contract-20260512.md) | 带通同噪残差评分的 CPU 评分器合约。 |
| [midfreq-residual-collector-contract-20260512.md](midfreq-residual-collector-contract-20260512.md) | CPU 兼容的收集器函数合约，用于匹配的 `x_t` / `tilde_x_t` 残差状态。 |
| [midfreq-residual-tiny-runner-contract-20260512.md](midfreq-residual-tiny-runner-contract-20260512.md) | 纯 CPU 合成微型运行器合约，证明残差缓存模式可行。 |
| [midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md) | 纯 CPU 真实资产 `4/4` 预检，证明残差缓存模式在合作者 750k checkpoint 与 CIFAR10 划分下可行；无 GPU 释放。 |
| [midfreq-residual-signcheck-20260512.md](midfreq-residual-signcheck-20260512.md) | 冻结的 `64/64` GPU 符号检查，针对同噪残差可观测信号；仅候选，非已确认证据。 |
| [midfreq-residual-stability-decision-20260512.md](midfreq-residual-stability-decision-20260512.md) | 纯 CPU 决策，为候选残差线路释放恰好一个种子稳定性数据包。 |
| [midfreq-residual-stability-result-20260512.md](midfreq-residual-stability-result-20260512.md) | 残差线路的仅种子稳定性结果；候选稳定但有界，未提升为已确认。 |
| [midfreq-residual-comparator-audit-20260512.md](midfreq-residual-comparator-audit-20260512.md) | 纯 CPU 比较器审计，表明当前残差信号未被证明具有中频特异性。 |
| [post-midfreq-next-lane-reselection-20260512.md](post-midfreq-next-lane-reselection-20260512.md) | 纯 CPU 重新选择，在残差比较器审计后选择 SecMI 消费者合约审查。 |
| [secmi-consumer-contract-review-20260512.md](secmi-consumer-contract-review-20260512.md) | 纯 CPU 审查，将 SecMI 保留为结构性支持证据，而非系统可消费行。 |
| [tmia-dm-temporal-artifact-gate-20260515.md](tmia-dm-temporal-artifact-gate-20260515.md) | 对已知 TMIA-DM 时态噪声/噪声梯度机制的最新公开表面复查；仅 CRAD 论文/PDF，无官方代码、checkpoint 绑定 score、不可变划分、ROC/metric 产物或验证器输出。 |
| [quantile-diffusion-mia-secmia-terror-replay-20260515.md](quantile-diffusion-mia-secmia-terror-replay-20260515.md) | 来自 `neilkale/quantile-diffusion-mia` 的第三方 SecMI 风格 `t_error` score 数据包回放；仅作支持用途，非官方 Quantile Regression 输出，也非已确认行。 |
| [dualmd-distillmd-defense-artifact-gate-20260515.md](dualmd-distillmd-defense-artifact-gate-20260515.md) | OpenReview DDMD 补充代码关卡；代码和 DDPM 划分索引文件公开，但缺少 checkpoint 绑定的 score/ROC/metric 产物，因此无下载、无 GPU 释放、无已确认行。 |
| [diffence-classifier-defense-artifact-gate-20260515.md](diffence-classifier-defense-artifact-gate-20260515.md) | 官方 DIFFENCE 分类器防御代码关卡；GitHub 和不可变 Zenodo 快照公开了代码/配置/划分索引文件，但扩散模型是推理前防御组件且缺少 checkpoint 绑定 score 产物，因此无模型数据下载、无 GPU 释放、无已确认行。 |
| [miahold-higher-order-langevin-artifact-gate-20260515.md](miahold-higher-order-langevin-artifact-gate-20260515.md) | 官方 MIAHOLD/HOLD++ 防御代码关卡；划分和攻击代码公开，但缺少 checkpoint 绑定 score 产物，因此无下载、无 GPU 释放、无已确认行。 |
| [shake-to-leak-code-artifact-gate-20260515.md](shake-to-leak-code-artifact-gate-20260515.md) | 官方 Shake-to-Leak 代码关卡；微调放大的生成式隐私代码公开，但缺少目标 checkpoint、不可变 member/nonmember 清单、生成的隐私集、score/ROC/metric 产物以及现成验证器输出，因此无下载、无 GPU 释放、无已确认行。 |
| [fseclab-mia-diffusion-code-artifact-gate-20260515.md](fseclab-mia-diffusion-code-artifact-gate-20260515.md) | 官方 FSECLab DDIM/DCGAN 扩散 MIA 代码关卡；攻击/评估代码和 FID 统计公开，但缺少 checkpoint 绑定 score/ROC/metric 产物和不可变划分清单，因此无下载、无 GPU 释放、无已确认行。 |
| [mtmia-relational-diffusion-score-packet-gate-20260515.md](mtmia-relational-diffusion-score-packet-gate-20260515.md) | MT-MIA 关系表格扩散关卡；官方 ClavaDDPM/RelDiff 划分、合成输出和 score/指标数据包公开，但仍为跨模态支持用途，无数据集/模型下载、无 GPU 释放、无已确认行。 |
| [lsaprobe-music-diffusion-mock-data-gate-20260515.md](lsaprobe-music-diffusion-mock-data-gate-20260515.md) | LSA-Probe 音乐/音频扩散关卡；论文和演示公开，但可见的 `data/*.json` score 类文件是从种子随机分布生成的模拟演示数据，因此无数据集/checkpoint 下载、无 GPU 释放、无已确认行。 |
| [h2-cross-asset-contract-preflight.md](h2-cross-asset-contract-preflight.md) | 纯 CPU 的 H2 跨 DDPM/CIFAR10 可移植性检查。 |
| [h2-image-to-image-contract.md](h2-image-to-image-contract.md) | CPU 合约，仅在观测到图到图响应信号时重新开放 H2 可移植性。 |
| [h2-img2img-micro-result.md](h2-img2img-micro-result.md) | 首次冻结的 SD/CelebA 图到图 H2 微数据包结论。 |
| [h2-img2img-simple-distance-review.md](h2-img2img-simple-distance-review.md) | 针对简单高强度图到图响应距离信号的 CPU 审查。 |
| [h2-img2img-simple-distance-stability-contract.md](h2-img2img-simple-distance-stability-contract.md) | 冻结的非重叠稳定性合约，针对简单图到图距离信号。 |
| [h2-img2img-simple-distance-stability-result.md](h2-img2img-simple-distance-stability-result.md) | 简单图到图距离信号的非重叠稳定性结果。 |
| [h2-img2img-simple-distance-admission-contract.md](h2-img2img-simple-distance-admission-contract.md) | 冻结的 25/25 验收规模合约，针对简单图到图距离信号。 |
| [h2-img2img-simple-distance-admission-result.md](h2-img2img-simple-distance-admission-result.md) | 简单图到图距离信号的验收规模结果。 |
| [h2-simple-distance-portability-preflight.md](h2-simple-distance-portability-preflight.md) | 纯 CPU 的第二资产简单距离可移植性预检。 |
| [black-box-next-lane-selection.md](black-box-next-lane-selection.md) | 纯 CPU 的 H2 之后下一条黑盒研究线路重新选择。 |
| [non-clid-black-box-reselection.md](non-clid-black-box-reselection.md) | 取代前者的纯 CPU 重新选择，在 CLiD 提示控制关闭之后。 |
| [non-gray-box-reselection-20260510.md](non-gray-box-reselection-20260510.md) | ReDiffuse 和 I-A 关闭后的 CPU 重新选择；选择响应合约获取审计。 |
| [post-rediffuse-next-lane-reselection.md](post-rediffuse-next-lane-reselection.md) | ReDiffuse 精确回放关闭后的 CPU 重新选择；选择第二个响应合约获取。 |
| [black-box-response-contract-acquisition-audit.md](black-box-response-contract-acquisition-audit.md) | CPU 审计，表明本地缺少第二响应合约资产；无 GPU 释放。 |
| [black-box-response-contract-asset-acquisition-spec.md](black-box-response-contract-asset-acquisition-spec.md) | 重新开放第二条黑盒响应合约所需的最小可移植资产包和 CPU 关卡。 |
| [black-box-response-contract-package-preflight.md](black-box-response-contract-package-preflight.md) | Kandinsky/Pokemon 第二合约候选的可执行包级预检。 |
| [black-box-response-contract-discovery.md](black-box-response-contract-discovery.md) | 仓库级发现扫描，表明当前不存在配对的第二响应合约包。 |
| [black-box-response-contract-second-asset-intake-20260511.md](black-box-response-contract-second-asset-intake-20260511.md) | 三分数合并后的录入刷新，确认不存在就绪的第二响应合约包。 |
| [black-box-response-contract-protocol-scaffold-20260511.md](black-box-response-contract-protocol-scaffold-20260511.md) | 纯 CPU 支架干跑，冻结下一个响应合约包交接布局，但不释放 GPU 工作。 |
| [black-box-response-contract-skeleton-create-20260511.md](black-box-response-contract-skeleton-create-20260511.md) | 纯 CPU 本地骨架创建和探测，表明包现已存在但仍需真实查询图像和响应。 |
| [black-box-response-contract-query-source-audit-20260511.md](black-box-response-contract-query-source-audit-20260511.md) | 纯 CPU 本地资产审计，表明现有 Kandinsky/Pokemon 材料无法填充响应合约查询划分或响应。 |
| [beans-lora-member-denoising-loss-scout-20260513.md](beans-lora-member-denoising-loss-scout-20260513.md) | CUDA 已知划分 Beans member-LoRA 侦察，表明条件去噪损失即使在修复伪成员语义后仍然较弱。 |
| [post-response-contract-reselection-20260511.md](post-response-contract-reselection-20260511.md) | 纯 CPU 重新选择，在响应合约、白盒和 I-A 后续项均未通过释放关卡后，选择已确认证据加固。 |
| [admitted-evidence-bundle-20260511.md](admitted-evidence-bundle-20260511.md) | 纯 CPU 导出全部已确认 Platform/Runtime 消费者集作为经过检查的机器可读包。 |
| [admitted-consumer-drift-audit-20260515.md](admitted-consumer-drift-audit-20260515.md) | 纯 CPU 无漂移审计，证明 2026-05-15 的 watch、watch-plus、support-only 和 candidate-only 关卡未改变已确认的 Platform/Runtime 消费者边界。 |
| [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md) | 纯 CPU 无漂移审计，证明近期候选关闭未改变已确认的 Platform/Runtime 消费者边界。 |
| [secmi-full-split-admission-boundary-review.md](secmi-full-split-admission-boundary-review.md) | 纯 CPU 审查，表明全划分 SecMI 是证据就绪的支持性灰盒证据，但不是已确认的 Platform/Runtime 证据。 |
| [secmi-admission-contract-hardening-20260511.md](secmi-admission-contract-hardening-20260511.md) | 纯 CPU 加固，将 SecMI 统计量和 NNS 保留为仅 Research 支持行。 |
| [post-secmi-next-lane-reselection-20260511.md](post-secmi-next-lane-reselection-20260511.md) | 纯 CPU 重新选择，选择白盒 influence/curvature 可行性侦察。 |
| [white-box-influence-curvature-feasibility-scout-20260511.md](white-box-influence-curvature-feasibility-scout-20260511.md) | 纯 CPU 白盒 influence/curvature 可行性合约；尚无方法结果或 GPU 释放。 |
| [gsa-diagonal-fisher-feasibility-microboard-20260511.md](gsa-diagonal-fisher-feasibility-microboard-20260511.md) | 纯 CPU 选定层 diagonal-Fisher 微面板结果；负面但有用，无 GPU 释放。 |
| [gsa-diagonal-fisher-layer-scope-review-20260511.md](gsa-diagonal-fisher-layer-scope-review-20260511.md) | 纯 CPU 层范围审查，针对 diagonal-Fisher 自影响；混合结果，未达 GPU 就绪。 |
| [gsa-diagonal-fisher-stability-board-20260511.md](gsa-diagonal-fisher-stability-board-20260511.md) | 纯 CPU 稳定性面板，将 diagonal-Fisher 自影响关闭为负面但有用；无 GPU 释放。 |
| [post-fisher-next-lane-reselection-20260511.md](post-fisher-next-lane-reselection-20260511.md) | 纯 CPU 重新选择，在 diagonal-Fisher 关闭后选择 I-A 有限尾部/自适应边界加固。 |
| [ia-finite-tail-adaptive-boundary-audit-20260511.md](ia-finite-tail-adaptive-boundary-audit-20260511.md) | 纯 CPU 无漂移审计，针对已确认严格尾部、自适应以及候选/已确认边界。 |
| [research-boundary-consumability-sync-20260510.md](research-boundary-consumability-sync-20260510.md) | ReDiffuse、三分数合并、GSA LR 和响应合约关闭后的下游消费者边界同步。 |
| [ib-risk-targeted-unlearning-successor-scope.md](ib-risk-targeted-unlearning-successor-scope.md) | CPU 范围审查，将 I-B 风险定向遗忘保持 hold 状态，直到有具体化的防御影子/自适应审查方案。 |
| [ib-defense-aware-reopen-scout-20260512.md](ib-defense-aware-reopen-scout-20260512.md) | CPU 侦察，表明 I-B 仍缺少可执行的防御影子/自适应攻击者重新开放合约。 |
| [ib-defense-reopen-protocol-audit-20260512.md](ib-defense-reopen-protocol-audit-20260512.md) | 代码感知审计，确认当前 I-B 审查路径借用了无防御影子阈值迁移，无法释放 GPU 工作。 |
| [ib-defended-shadow-reopen-protocol-20260512.md](ib-defended-shadow-reopen-protocol-20260512.md) | 机器可检查的 CPU 重新开放协议，用于未来 I-B 防御影子/自适应攻击者工作；仍无 GPU 释放。 |
| [ib-reopen-shadow-reference-guard-20260512.md](ib-reopen-shadow-reference-guard-20260512.md) | CPU 守卫，使防御影子重新开放模式拒绝旧的未防御影子阈值引用。 |
| [ib-defended-shadow-training-manifest-20260512.md](ib-defended-shadow-training-manifest-20260512.md) | 覆盖感知的 CPU 清单，在任何 GPU 运行之前阻断当前 I-B 防御影子训练合约。 |
| [ib-shadow-local-identity-scout-20260512.md](ib-shadow-local-identity-scout-20260512.md) | CPU 语义侦察，表明双影子目标风险重映射在机制上可行，但不是真正的影子本地风险评分。 |
| [ic-cross-permission-successor-scope.md](ic-cross-permission-successor-scope.md) | CPU 范围审查，将 I-C 跨权限/翻译合约工作保持 hold 状态，直到存在同规格评估器。 |
| [post-ib-next-lane-reselection-20260512.md](post-ib-next-lane-reselection-20260512.md) | 纯 CPU 重新选择，在 I-B 协议审计后选择 I-C 同规格评估器可行性侦察。 |
| [ic-same-spec-evaluator-feasibility-scout-20260512.md](ic-same-spec-evaluator-feasibility-scout-20260512.md) | 纯 CPU I-C 可行性侦察，表明当前翻译别名探针不是同规格评估器释放面。 |
| [research-resting-state-audit-20260510.md](research-resting-state-audit-20260510.md) | 当前审计，表明 Research 在资产或新假设到来之前无活跃 GPU 候选或可缩减的 CPU sidecar。 |
| [gsa-loss-score-shadow-stability-review.md](gsa-loss-score-shadow-stability-review.md) | 纯 CPU 留一影子审查，证伪了 GSA loss-score LR 独立评分器救援路径。 |
| [variation-query-contract-audit.md](variation-query-contract-audit.md) | 可执行审计，用于判断 variation 黑盒线路是否有真实查询图像和端点就绪状态。 |
| [semantic-aux-low-fpr-review.md](semantic-aux-low-fpr-review.md) | 纯 CPU 低 FPR 审查，针对语义辅助分类器线路。 |
| [recon-product-validation-contract.md](recon-product-validation-contract.md) | 下一个 recon 产品可消费验证数据包的 CPU 合约。 |
| [recon-product-validation-result.md](recon-product-validation-result.md) | 有边界的 recon 产品验证重新运行与指标来源边界。 |
| [recon-tail-confidence-review.md](recon-tail-confidence-review.md) | 已确认 recon 严格尾部指标的有限样本置信度审查。 |
| [rediffuse-stl10-sima-score-norm-20260525.md](rediffuse-stl10-sima-score-norm-20260525.md) | ReDiffuse STL-10 短目标上的 SimA-style 去噪器输出范数单次评分；结果弱，不释放 GPU 扩展。 |
| [rediffuse-stl10-bounded-scout-20260525.md](rediffuse-stl10-bounded-scout-20260525.md) | ReDiffuse STL-10 官方 DDPM 短目标有界 scout；固定 timestep denoising-loss 结果随机级。 |
| [rediffuse-stl10-split-and-microtrain-preflight-20260525.md](rediffuse-stl10-split-and-microtrain-preflight-20260525.md) | ReDiffuse STL-10 split、低层统计和 CUDA 微训练预检。 |
| [rediffuse-collaborator-integration-report.md](rediffuse-collaborator-integration-report.md) | 合作者 ReDiffuse 包与 750k checkpoint 的录入和运行时集成报告。 |
| [rediffuse-collaborator-bundle-intake.md](rediffuse-collaborator-bundle-intake.md) | 合作者 ReDiffuse 包的资产级录入记录。 |
| [rediffuse-runtime-smoke-result.md](rediffuse-runtime-smoke-result.md) | ReDiffuse 适配器的 CPU 与 CUDA 兼容性 smoke 结果。 |
| [rediffuse-cifar10-small-packet.md](rediffuse-cifar10-small-packet.md) | 有边界的 64/64 CIFAR10 候选数据包，位于直接距离 ReDiffuse 面上。 |
| [rediffuse-800k-runtime-probe.md](rediffuse-800k-runtime-probe.md) | 在 ReDiffuse 适配器下对现有 PIA 800k checkpoint 的 CPU 运行时兼容性探针。 |
| [rediffuse-resnet-parity-packet.md](rediffuse-resnet-parity-packet.md) | ReDiffuse 的 750k ResNet 评分合约一致性数据包——负面但有用。 |
| [rediffuse-direct-distance-boundary-review.md](rediffuse-direct-distance-boundary-review.md) | CPU 边界审查，将 ReDiffuse 直接距离关闭为仅候选，不自动释放 800k GPU。 |
| [rediffuse-checkpoint-portability-gate.md](rediffuse-checkpoint-portability-gate.md) | CPU 关卡，表明 800k checkpoint 可移植性被未解决的评分器合约阻断。 |
| [rediffuse-resnet-contract-scout.md](rediffuse-resnet-contract-scout.md) | CPU 侦察，表明当前 Research ResNet 模式并非精确的合作者回放。 |
| [rediffuse-exact-replay-preflight.md](rediffuse-exact-replay-preflight.md) | 针对显式合作者 checkpoint 选择回放模式的 CPU 预检。 |
| [rediffuse-exact-replay-packet.md](rediffuse-exact-replay-packet.md) | 合作者 ReDiffuse 基线的有边界 750k 精确回放数据包结论。 |
| [gray-box-triscore-consolidation-review.md](gray-box-triscore-consolidation-review.md) | 将现有 CDI/TMIA-DM/PIA 三分数数据包合并为正面但有界的内部证据的 CPU 审查。 |
| [gray-box-triscore-truth-hardening-review.md](gray-box-triscore-truth-hardening-review.md) | CPU 真实性加固关卡，表明三分数保持正面但有界且仅限内部。 |
| [recon-product-row-validation-guard.md](recon-product-row-validation-guard.md) | 已确认 recon 产品行的系统可消费守卫。 |
| [../product-bridge/recon-product-evidence-card.md](../product-bridge/recon-product-evidence-card.md) | 已确认 recon 行的面向产品的机器可读证据卡合约。 |
| [../product-bridge/admitted-evidence-bundle.md](../product-bridge/admitted-evidence-bundle.md) | 完整已确认消费者集的面向产品的机器可读包合约。 |
| [clid-bridge-contract.md](clid-bridge-contract.md) | 本地 CLiD 桥接产物合约与下一个 score 模式关卡。 |
| [clid-score-schema-gate.md](clid-score-schema-gate.md) | CLiD score 汇总模式与低 FPR 提升关卡。 |
| [clid-tiny-score-bridge.md](clid-tiny-score-bridge.md) | 首次 GPU smoke 规模 CLiD score 桥接结论。 |
| [clid-100-score-packet.md](clid-100-score-packet.md) | 首个有边界的 CLiD score 数据包，通过 score 汇总关卡。 |
| [clid-candidate-integrity-review.md](clid-candidate-integrity-review.md) | CLiD 100/100 候选的 CPU 完整性审查。 |
| [clid-repeat-stability.md](clid-repeat-stability.md) | CLiD 100/100 候选的独立重复稳定性。 |
| [clid-prompt-perturbation.md](clid-prompt-perturbation.md) | 提示中性的扰动结果与 CLiD 验收边界。 |
| [clid-prompt-conditioning-boundary.md](clid-prompt-conditioning-boundary.md) | 规范 CLiD 提示条件声明边界与下一个验收测试。 |
| [clid-adaptive-prompt-perturbation-contract.md](clid-adaptive-prompt-perturbation-contract.md) | 下一个 CLiD 验收设计的 CPU 优先提示控制合约。 |
| [clid-swapped-prompt-control.md](clid-swapped-prompt-control.md) | 交换提示的 CLiD 控制与更新后的提示条件解释。 |
| [clid-within-split-shuffle-control.md](clid-within-split-shuffle-control.md) | 划分内提示洗牌 CLiD 控制与提示-图像合约边界。 |
| [clid-prompt-text-only-review.md](clid-prompt-text-only-review.md) | CLiD 100/100 桥接的纯提示文本干扰基线。 |
| [clid-control-attribution.md](clid-control-attribution.md) | 比较严格尾部保留与特征相关性的控制数据包归因。 |
| [research-boundary-card.md](research-boundary-card.md) | 面向下游消费者的限制卡片。 |
| [pia-stochastic-dropout-truth-hardening-review.md](pia-stochastic-dropout-truth-hardening-review.md) | CPU 审查，加固已确认 PIA + stochastic-dropout 的形式化、自适应和低 FPR 边界。 |
| [workspace-evidence-index.md](workspace-evidence-index.md) | 活跃与已归档工作区证据所在位置。 |

证据标签定义了项目边界。不要在未经审查的结论下将 smoke 测试、被阻断的运行或负面结果提升为更强声明。
