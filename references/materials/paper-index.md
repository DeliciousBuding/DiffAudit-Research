# 论文索引

这份文档按“每篇论文一个小标题”的方式整理，用来同步 GitHub 与飞书中的论文阅读索引。

字段说明：

- `文件`：仓库内 PDF 的规范化路径
- `论文大意`：用人话解释这篇论文主要在解决什么问题
- `和 DiffAudit 的关系`：说明它为什么值得被纳入当前课题
- `开源仓库`：优先给官方或作者公开实现；找不到就明确写“暂未找到”

## 黑盒

### Towards Black-Box Membership Inference Attack for Diffusion Models

- 文件：[2024-arxiv-towards-black-box-membership-inference-diffusion-models.pdf](black-box/2024-arxiv-towards-black-box-membership-inference-diffusion-models.pdf)
- 论文大意：这篇工作研究最严格的黑盒场景，也就是攻击者拿不到模型内部结构，只能调用图像变体接口。作者提出 `REDIFFUSE`，通过多次图像变换后再和原图比较，判断这张图是不是训练样本。
- 和 DiffAudit 的关系：它是最贴近“外部 API 审计”场景的基线论文，对应仓库里的 `variation` 路线。
- 开源仓库：暂未找到

### Membership Inference on Text-to-Image Diffusion Models via Conditional Likelihood Discrepancy

- 文件：[2024-neurips-clid-membership-inference-text-to-image-diffusion.pdf](black-box/2024-neurips-clid-membership-inference-text-to-image-diffusion.pdf)
- 论文大意：这篇论文指出，文生图模型更容易在“给定文本条件之后的图像分布”上发生过拟合，而不是单纯记住图像边缘分布。作者据此提出 `CLiD`，用条件似然差异做成员推断。
- 和 DiffAudit 的关系：它是当前最重要的文生图黑盒论文之一，对 caption 条件存在的场景尤其关键。
- 开源仓库：[zhaisf/CLiD](https://github.com/zhaisf/CLiD)

### Black-box Membership Inference Attacks against Fine-tuned Diffusion Models

- 文件：[2025-ndss-black-box-membership-inference-fine-tuned-diffusion-models.pdf](black-box/2025-ndss-black-box-membership-inference-fine-tuned-diffusion-models.pdf)
- 论文大意：这篇工作聚焦现实里更常见的“预训练扩散模型被下游微调”场景，研究黑盒条件下如何判断某张图是否来自微调数据集。论文给出了一套系统攻击框架，并且效果很强。
- 和 DiffAudit 的关系：这是当前 DiffAudit 黑盒主线最核心的目标论文，对应仓库里的 `recon` 路线。
- 开源仓库：[py85252876/Reconstruction-based-Attack](https://github.com/py85252876/Reconstruction-based-Attack)

### Membership Inference Attacks for Face Images Against Fine-tuned Latent Diffusion Models

- 文件：[2025-visapp-membership-inference-face-fine-tuned-latent-diffusion-models.pdf](black-box/2025-visapp-membership-inference-face-fine-tuned-latent-diffusion-models.pdf)
- 论文大意：这篇工作把问题缩到人脸领域，研究能否判断一组人脸是否被用于微调 latent diffusion 模型。论文还分析了 watermark、guidance scale 和 prompt 等因素对攻击的影响。
- 和 DiffAudit 的关系：它展示了“面向敏感数据的人脸隐私审计”这一具体落地场景，有助于未来把实验扩展到更接近合规需求的领域。
- 开源仓库：[osquera/MIA_SD](https://github.com/osquera/MIA_SD)

## 灰盒

### Are Diffusion Models Vulnerable to Membership Inference Attacks?

- 文件：[2023-icml-secmi-membership-inference-diffusion-models.pdf](gray-box/2023-icml-secmi-membership-inference-diffusion-models.pdf)
- 论文大意：这是较早系统研究扩散模型成员推断的代表作。作者提出 `SecMI`，通过比较扩散过程中的后验估计误差来判断成员关系。
- 和 DiffAudit 的关系：它是当前灰盒路线最基础的基线之一，对应仓库里的 `secmi` 实现。
- 开源仓库：[jinhaoduan/SecMI](https://github.com/jinhaoduan/SecMI)

### SIDE: Surrogate Conditional Data Extraction from Diffusion Models

- 文件：[2024-arxiv-side-extracting-training-data-unconditional-diffusion-models.pdf](gray-box/2024-arxiv-side-extracting-training-data-unconditional-diffusion-models.pdf)
- 论文大意：这篇工作关注的不只是“是不是成员”，而是更进一步的“能不能把训练数据抽出来”。作者提出代理条件，说明即便是无条件扩散模型，也可能被变成可控的数据提取对象。
- 和 DiffAudit 的关系：它提醒我们审计不能只盯住成员推断，还要关注更强的数据泄露风险。
- 开源仓库：暂未找到

### Unveiling Structural Memorization: Structural Membership Inference Attack for Text-to-Image Diffusion Models

- 文件：[2024-arxiv-structural-memorization-membership-inference-text-to-image-diffusion.pdf](gray-box/2024-arxiv-structural-memorization-membership-inference-text-to-image-diffusion.pdf)
- 论文大意：这篇论文认为大模型不一定完整记住像素细节，但会更强地记住结构。作者利用“结构保持”这个现象做成员推断。
- 和 DiffAudit 的关系：它说明审计证据不一定只能来自重建误差，也可以来自更中层的结构信号。
- 开源仓库：暂未找到

### An Efficient Membership Inference Attack for the Diffusion Model by Proximal Initialization

- 文件：[2024-iclr-pia-proximal-initialization.pdf](gray-box/2024-iclr-pia-proximal-initialization.pdf)
- 论文大意：这篇论文提出 `PIA`，通过更接近真实轨迹的初始化方式，用更少查询提取成员信号。它还扩展到了 TTS 等非视觉任务。
- 和 DiffAudit 的关系：它是当前灰盒实现主线之一，对应仓库里的 `pia` 路线。
- 开源仓库：[kong13661/PIA](https://github.com/kong13661/PIA)

### Score-based Membership Inference on Diffusion Models

- 文件：[2025-arxiv-sima-score-based-membership-inference-diffusion-models.pdf](gray-box/2025-arxiv-sima-score-based-membership-inference-diffusion-models.pdf)
- 论文大意：这篇工作从理论和实验两方面说明，模型预测的 score / noise 范数本身就会泄露成员关系，并提出单次查询攻击 `SimA`。
- 和 DiffAudit 的关系：它适合作为未来灰盒基准里的高效 score-based 参照方法。
- 开源仓库：[mx-ethan-rao/SimA](https://github.com/mx-ethan-rao/SimA)

### Noise Aggregation Analysis Driven by Small-Noise Injection: Efficient Membership Inference for Diffusion Models

- 文件：[2025-arxiv-small-noise-injection-membership-inference-diffusion-models.pdf](gray-box/2025-arxiv-small-noise-injection-membership-inference-diffusion-models.pdf)
- 论文大意：论文通过注入小噪声后观察预测噪声的聚合程度来区分成员与非成员。核心想法是成员样本在轻微扰动下会表现得更稳定。
- 和 DiffAudit 的关系：这是一个查询成本较低的候选方法，适合未来做批量审计实验。
- 开源仓库：暂未找到

### CDI: Copyrighted Data Identification in Diffusion Models

- 文件：[2025-cvpr-cdi-copyrighted-data-identification-diffusion-models.pdf](gray-box/2025-cvpr-cdi-copyrighted-data-identification-diffusion-models.pdf)
- 论文大意：这篇工作不再只问“某张图是不是成员”，而是更接近现实合规场景地问“某个数据集是否被模型使用”。它通过聚合信号和统计检验，给出更适合举证的数据集级证据。
- 和 DiffAudit 的关系：这条路线和未来产品化、报告化非常契合，因为企业真正需要的常常是“数据集是否被用了”的判断。
- 开源仓库：[sprintml/copyrighted_data_identification](https://github.com/sprintml/copyrighted_data_identification)

### Noise as a Probe: Membership Inference Attacks on Diffusion Models Leveraging Initial Noise

- 文件：[2026-arxiv-noise-as-a-probe-membership-inference-diffusion-models.pdf](gray-box/2026-arxiv-noise-as-a-probe-membership-inference-diffusion-models.pdf)
- 论文大意：这篇工作把初始噪声当成探针，利用扩散噪声中残留的语义信息做成员推断，特别关注小数据集微调模型。
- 和 DiffAudit 的关系：它提供了不依赖中间层显式输出的另一条灰盒路径。
- 开源仓库：暂未找到

### No Caption, No Problem: Caption-Free Membership Inference via Model-Fitted Embeddings

- 文件：[2026-openreview-mofit-caption-free-membership-inference.pdf](gray-box/2026-openreview-mofit-caption-free-membership-inference.pdf)
- 论文大意：这篇论文正面解决“真实场景里通常拿不到训练 caption”这个问题。它构造 model-fitted embedding，让没有 caption 的图像也能被用来做成员推断。
- 和 DiffAudit 的关系：非常实用，因为很多真实审计场景里，手上只有图，没有训练元数据。
- 开源仓库：[JoonsungJeon/MoFit](https://github.com/JoonsungJeon/MoFit)

## 白盒

### Finding NeMo: Localizing Neurons Responsible for Memorization in Diffusion Models

- 文件：[2024-neurips-finding-nemo-localizing-memorization-neurons-diffusion-models.pdf](white-box/2024-neurips-finding-nemo-localizing-memorization-neurons-diffusion-models.pdf)
- 论文大意：这篇工作不只是判断模型有没有泄露，而是进一步定位“到底是哪些神经元在记住训练样本”。作者提出 `NEMO`，并展示停用这些神经元后可以降低记忆泄露。
- 和 DiffAudit 的关系：它是白盒解释和白盒缓解路线的重要参考。
- 开源仓库：[ml-research/localizing_memorization_in_diffusion_models](https://github.com/ml-research/localizing_memorization_in_diffusion_models)

### White-box Membership Inference Attacks against Diffusion Models

- 文件：[2025-local-mirror-white-box-membership-inference-diffusion-models.pdf](white-box/2025-local-mirror-white-box-membership-inference-diffusion-models.pdf)
- 论文大意：这篇工作系统比较扩散模型上的成员推断特征，强调梯度特征在白盒场景下非常有效。这份文件是本地镜像版。
- 和 DiffAudit 的关系：它是未来白盒攻击引擎的直接技术来源之一。
- 开源仓库：[py85252876/GSA](https://github.com/py85252876/GSA)

### White-box Membership Inference Attacks against Diffusion Models

- 文件：[2025-popets-white-box-membership-inference-diffusion-models.pdf](white-box/2025-popets-white-box-membership-inference-diffusion-models.pdf)
- 论文大意：这是上面同一工作的正式 PoPETs 版本，核心结论仍然是梯度特征比单纯的 loss 更适合做扩散模型白盒成员推断。
- 和 DiffAudit 的关系：如果后续白盒只选一篇主论文，这篇应作为 canonical copy。
- 开源仓库：[py85252876/GSA](https://github.com/py85252876/GSA)

## 背景与上下文

### DiffAudit 产品需求文档（PRD）

- 文件：[diffaudit-product-requirements.pdf](context/diffaudit-product-requirements.pdf)
- 论文大意：这不是论文，而是产品文档。它解释了 DiffAudit 为什么要从“单篇论文复现”往“可交付的审计系统”走，并定义了白盒、灰盒、黑盒和报告输出等模块。
- 和 DiffAudit 的关系：这是系统定位和产品边界的内部依据。
- 开源仓库：[DeliciousBuding/DiffAudit](https://github.com/DeliciousBuding/DiffAudit/)

### DiffAudit 团队入门扫盲文档

- 文件：[diffaudit-team-onboarding.pdf](context/diffaudit-team-onboarding.pdf)
- 论文大意：这份文档面向新成员，用更易懂的方式解释“扩散模型隐私审计”到底在做什么，并统一团队术语。
- 和 DiffAudit 的关系：这是内部共识和团队 onboarding 材料。
- 开源仓库：[DeliciousBuding/DiffAudit](https://github.com/DeliciousBuding/DiffAudit/)

## 综述与归档

### Tracing the Roots: Leveraging Temporal Dynamics in Diffusion Trajectories for Origin Attribution

- 文件：[2025-neurips-tracing-the-roots-origin-attribution-diffusion-trajectories.pdf](survey/2025-neurips-tracing-the-roots-origin-attribution-diffusion-trajectories.pdf)
- 论文大意：这篇工作利用整条 diffusion trajectory 的时间动态去做来源归因，统一讨论训练集成员、模型生成样本和外部样本三类来源。
- 和 DiffAudit 的关系：它对“成员推断只是更广义溯源问题的一部分”这个视角很有帮助。
- 开源仓库：暂未找到

### DP-DocLDM: Differentially Private Document Image Generation Using Latent Diffusion Models

- 文件：[2025-icdar-dp-docldm-private-document-image-generation-latent-diffusion.pdf](survey/2025-icdar-dp-docldm-private-document-image-generation-latent-diffusion.pdf)
- 论文大意：这篇工作把差分隐私引入文档图像生成，用私有 latent diffusion 来生成可用于下游任务的合成数据。
- 和 DiffAudit 的关系：它属于防御与隐私保护方向的参考材料。
- 开源仓库：暂未找到

### Privacy-Preserving Low-Rank Adaptation Against Membership Inference Attacks for Latent Diffusion Models

- 文件：[2025-aaai-privacy-preserving-lora-membership-inference-latent-diffusion-models.pdf](survey/2025-aaai-privacy-preserving-lora-membership-inference-latent-diffusion-models.pdf)
- 论文大意：这篇工作围绕 LoRA 微调的隐私风险，提出在低秩适配过程中同时压制成员推断能力的防御思路。
- 和 DiffAudit 的关系：它更偏“怎么防”而不是“怎么攻”，适合用来对照攻击路线。
- 开源仓库：暂未找到

### Dual-Model Defense: Safeguarding Diffusion Models from Membership Inference Attacks through Disjoint Data Splitting

- 文件：[2024-arxiv-dual-model-defense-diffusion-membership-inference-disjoint-data-splitting.pdf](survey/2024-arxiv-dual-model-defense-diffusion-membership-inference-disjoint-data-splitting.pdf)
- 论文大意：这篇工作通过双模型训练、私有推理和蒸馏来减弱成员推断风险，属于比较典型的部署级防御策略。
- 和 DiffAudit 的关系：它适合作为防御路线的归档材料，不是当前主线攻击基线。
- 开源仓库：暂未找到

### DIFFENCE: Fencing Membership Privacy With Diffusion Models

- 文件：[2025-ndss-diffence-fencing-membership-privacy-diffusion-models.pdf](survey/2025-ndss-diffence-fencing-membership-privacy-diffusion-models.pdf)
- 论文大意：这篇工作在推理前先用扩散模型重生成输入，削弱成员与非成员之间容易被攻击利用的差异。
- 和 DiffAudit 的关系：它是扩散模型防御路线里很有代表性的一篇论文。
- 开源仓库：暂未找到

### Defending Diffusion Models Against Membership Inference Attacks via Higher-Order Langevin Dynamics

- 文件：[2025-arxiv-defending-diffusion-models-membership-inference-higher-order-langevin-dynamics.pdf](survey/2025-arxiv-defending-diffusion-models-membership-inference-higher-order-langevin-dynamics.pdf)
- 论文大意：这篇工作利用高阶 Langevin 动力学引入额外随机性，以削弱扩散模型的成员推断风险。
- 和 DiffAudit 的关系：它提供了另一种偏理论化的防御思路。
- 开源仓库：暂未找到

### Inference Attacks Against Graph Generative Diffusion Models

- 文件：[2026-arxiv-inference-attacks-graph-generative-diffusion-models.pdf](survey/2026-arxiv-inference-attacks-graph-generative-diffusion-models.pdf)
- 论文大意：这篇工作把隐私攻击扩展到了图生成扩散模型，说明扩散隐私问题并不只存在于图像领域。
- 和 DiffAudit 的关系：它有助于团队理解未来跨模态、跨数据结构扩展的可能方向。
- 开源仓库：暂未找到

### Perturb a Model, Not an Image: Towards Robust Privacy Protection via Anti-Personalized Diffusion Models

- 文件：[2025-arxiv-perturb-a-model-not-an-image-anti-personalized-diffusion-models.pdf](survey/2025-arxiv-perturb-a-model-not-an-image-anti-personalized-diffusion-models.pdf)
- 论文大意：这篇工作不再去保护图像本身，而是直接让模型变得更难被用来做针对特定主体的个性化生成。
- 和 DiffAudit 的关系：它更偏“反个性化/隐私保护”方向，是成员推断之外的重要补充。
- 开源仓库：暂未找到

### Diffusion Privacy Literature Survey Index

- 文件：[survey-index-diffusion-privacy-literature.pdf](survey/survey-index-diffusion-privacy-literature.pdf)
- 论文大意：这是本地整理的归档索引文件，用来记录一些补充性的综述和归档材料。
- 和 DiffAudit 的关系：主要是维护和整理用途，不是直接的研究主线论文。
- 开源仓库：不适用
