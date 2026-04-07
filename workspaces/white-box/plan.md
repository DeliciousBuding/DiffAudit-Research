# 白盒方向计划

## 状态面板

- `owner`: `research_leader`
- `scope`: 白盒成员推断、梯度级攻击、记忆定位与内部信号审计
- `status`: `GSA real-asset closed-loop ready; W-1 pending`
- `blocked by`: `GSA` 当前统计结果仍接近随机；`W-1` 还未接成正式 baseline；`W-2` 仍缺稳定训练目标与实现
- `next step`: 继续扩大 `GSA` bucket 与 checkpoint 训练强度，并把 `DPDM` 接成正式 `W-1`
- `last updated`: `2026-04-08`

## 推荐论文

- `2025-popets-white-box-membership-inference-diffusion-models.pdf`
- `2025-local-mirror-white-box-membership-inference-diffusion-models.pdf`
- `2024-neurips-finding-nemo-localizing-memorization-neurons-diffusion-models.pdf`
- `2023-tmlr-differentially-private-diffusion-models.pdf`
- `2023-arxiv-differentially-private-diffusion-models-generate-useful-synthetic-images.pdf`

## 当前主线与防御候选

- 主线：`GSA`
- 防御候选：`W-1 = DPDM / Diffusion-DP`
- 扩展研究：`Finding NeMo`

## 当前可执行证据

- `workspaces/white-box/2026-04-07-gsa-runtime-mainline.md`
- `workspaces/white-box/2026-04-07-gsa-asset-intake.md`
- `workspaces/white-box/2026-04-07-gsa-closed-loop-smoke.md`
- `workspaces/white-box/2026-04-06-gsa-kickoff.md`
- `workspaces/white-box/assets/gsa/manifests/cifar10-ddpm-mainline.json`
- `workspaces/white-box/runs/gsa-runtime-mainline-20260407-cpu/summary.json`

## 本地代码上下文

- `workspaces/white-box/external/GSA`
- `external/DPDM`

## 当前推荐执行顺序

1. 继续扩大 `GSA` 的 `target/shadow/member/non-member` bucket
2. 提高 `checkpoint-*` 训练强度与 epoch
3. 重新跑 `GSA` closed loop，看指标是否脱离随机附近
4. 用 `DPDM` 建立 `W-1` 的第一版白盒防御 baseline
5. 暂不优先做 `W-2`

## 当前阻塞项

- 现在能证明“闭环已通”，还不能证明“攻击已稳定成立”
- `W-1` 还没有正式 run 结果
- `Finding NeMo` 仍缺 neuron-level 分析接口与资产
- 白盒 attack-defense 总表还不存在

## 当前最短路径

1. `GSA` 扩样本、提训练强度
2. `DPDM -> W-1`
3. 把白盒结果接入统一总表
