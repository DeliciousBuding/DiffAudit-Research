# 命令参考

本页汇总了可用于本地验证和研究运行的命令配方。

除非命令另有说明，请在 `Research/` 仓库根目录下执行。

## 环境

创建默认环境：

```powershell
conda env create -f environment.yml
conda activate diffaudit-research
python scripts/bootstrap_research_env.py --install
python scripts/verify_env.py
python -m diffaudit --help
```

更新已有环境：

```powershell
conda env update -f environment.yml --prune
conda activate diffaudit-research
python scripts/bootstrap_research_env.py --install
```

仅在默认环境栈出现真实的 CUDA 兼容性错误后，才使用较新 GPU 的可选环境：

```powershell
conda env create -f environment.gpu-cu128.yml
conda activate diffaudit-research
python scripts/bootstrap_research_env.py --install
```

如果 shell 尚未激活 conda，请在命令前添加前缀：

```powershell
conda run -n diffaudit-research python scripts/verify_env.py
conda run -n diffaudit-research python -m diffaudit --help
```

## 本地资产绑定

创建被忽略的本地配置：

```powershell
Copy-Item configs/assets/team.local.template.yaml configs/assets/team.local.yaml
```

在 `configs/assets/team.local.yaml` 中填写路径，然后渲染各线本地配置：

```powershell
python scripts/render_team_local_configs.py
```

不要提交个人机器的绝对路径。共享原始资产放在 `<DIFFAUDIT_ROOT>/Download/` 下；被忽略的上游代码克隆放在 `Research/external/` 下。

## Smoke 流水线

运行最小 smoke 流水线：

```powershell
python -m diffaudit run-smoke --config configs/benchmarks/secmi-smoke.yaml --workspace .
```

运行本地检查包装脚本：

```powershell
python -X utf8 scripts/run_pr_checks.py
python -X utf8 scripts/run_local_checks.py --fast
python -X utf8 scripts/run_local_checks.py
```

## 黑盒

规划 `recon`：

```powershell
python -m diffaudit plan-recon --config configs/attacks/recon-plan.yaml
python -m diffaudit probe-recon-assets --config configs/attacks/recon-plan.yaml
python -m diffaudit dry-run-recon --config configs/attacks/recon-plan.yaml --repo-root external/Reconstruction-based-Attack
```

运行 `recon` smoke 与产物路径：

```powershell
python -m diffaudit run-recon-eval-smoke --workspace experiments/recon-eval-smoke
python -m diffaudit run-recon-mainline-smoke --workspace experiments/recon-mainline-smoke --repo-root external/Reconstruction-based-Attack --method threshold
python -m diffaudit probe-recon-score-artifacts --artifact-dir path/to/recon-scores
python -m diffaudit run-recon-artifact-mainline --artifact-dir path/to/recon-scores --workspace experiments/recon-artifact-mainline --repo-root external/Reconstruction-based-Attack --method threshold
```

运行论文 Stage 0 关卡：

```powershell
python -m diffaudit check-recon-stage0-paper-gate --repo-root external/Reconstruction-based-Attack --bundle-root "$env:DIFFAUDIT_ROOT/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models" --attack-scenario attack-i
```

评估已保存的 H2 响应强度缓存：

```powershell
python scripts/evaluate_h2_response_cache.py `
  --response-cache workspaces/black-box/runs/<run>/response-cache.npz `
  --output workspaces/black-box/runs/<run>/cache-eval-summary.json
```

这是纯 CPU 的候选评分器。它不收集模型响应，也不会将 H2 提升为已确认证据。

写入合成的中频同噪残差缓存模式预检：

```powershell
python -X utf8 -m diffaudit run-midfreq-residual-tiny-cache `
  --workspace tmp/midfreq-residual-tiny-cache-smoke `
  --member-count 4 `
  --nonmember-count 4 `
  --batch-size 4 `
  --seed 12 `
  --timestep 80
```

这会在被忽略的工作区下写入 `summary.json` 和 `residual-cache.npz`。仅作缓存合约 smoke 用途，不是 benchmark，也不释放 GPU。

写入真实资产的中频同噪残差缓存预检：

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-real-asset-preflight `
  --workspace workspaces/black-box/runs/midfreq-real-asset-tiny-20260512-cpu-4 `
  --sample-count-per-split 4 `
  --batch-size 2 `
  --seed 12 `
  --timestep 80
```

当本地资产清单路径存在时，此命令使用合作者 750k checkpoint 和 CIFAR10 ratio0.5 划分。仍为 `4/4` 缓存合约预检，不是 benchmark 证据，也不释放 GPU。

运行有限规模的中频同噪残差符号检查：

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-sign-check `
  --workspace workspaces/black-box/runs/midfreq-residual-signcheck-20260512-gpu-64 `
  --sample-count-per-split 64 `
  --batch-size 8 `
  --seed 12 `
  --timestep 80 `
  --device cuda
```

这是冻结的 `64/64` 候选数据包。它会在被忽略的本地运行目录下写入产物，必须通过证据说明总结后才能影响路线图，不是已确认结果。

运行已释放的中频同噪残差种子稳定性探针：

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-midfreq-residual-sign-check `
  --workspace workspaces/black-box/runs/midfreq-residual-stability-seed23-20260512-gpu-64 `
  --sample-count-per-split 64 `
  --batch-size 8 `
  --seed 23 `
  --timestep 80 `
  --device cuda
```

这是 [midfreq-residual-stability-decision-20260512.md](../evidence/midfreq-residual-stability-decision-20260512.md) 唯一释放的数据包。仅测试种子/噪声配对的稳定性，不是 sweep。

运行有限规模的 H2 响应强度验证候选：

```powershell
python scripts/run_h2_response_strength_validation.py `
  --packet-size 512 `
  --split-offset 512 `
  --primary-scorer raw_h2_logistic `
  --device cuda:0
```

这是 GPU 验证候选，不是已确认 benchmark。

审查已保存 H2 缓存的低通截止灵敏度：

```powershell
python scripts/review_h2_lowpass_cutoffs.py `
  --response-cache workspaces/black-box/runs/<run>/response-cache.npz `
  --output workspaces/black-box/runs/<run>/lowpass-cutoff-review.json
```

审查已保存 H2 缓存的简单图到图响应距离：

```powershell
python scripts/review_h2_img2img_simple_distance.py `
  --response-cache workspaces/black-box/runs/<run>/response-cache.npz `
  --evaluation-summary workspaces/black-box/runs/<run>/summary.json `
  --output workspaces/black-box/runs/<run>/simple-distance-review.json
```

探测 H2 是否能迁移到非 DDPM 的黑盒资产合约：

```powershell
python scripts/probe_h2_cross_asset_contract.py
```

默认的 SD/CelebA 文生图模式预计会被 H2 响应强度协议阻断。仅当目标界面确实支持基于图像条件的重复查询时，才使用 `--endpoint-mode image_to_image`。

准备冻结的 H2 SD/CelebA 图到图微数据包（不运行 GPU）：

```powershell
python scripts/collect_h2_img2img_response_cache.py
```

确认 GPU 显存后，收集有限规模的 10/10 GPU 微数据包：

```powershell
python scripts/collect_h2_img2img_response_cache.py `
  --execute `
  --packet-size 10 `
  --strengths 0.35 0.55 0.75 `
  --repeats 2 `
  --device cuda:0
```

脚本在被忽略的工作区运行目录下写入本地运行产物。仅提交经过审查的摘要和证据说明，不要提交响应缓存或生成图像。

试运行不重叠的简单距离稳定性数据包：

```powershell
python scripts/collect_h2_img2img_response_cache.py `
  --split-name derived-public-25 `
  --sample-offset 10 `
  --packet-size 10 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-stability-20260501-r1
```

试运行冻结的 25/25 简单距离验收数据包：

```powershell
python scripts/collect_h2_img2img_response_cache.py `
  --split-name derived-public-50 `
  --sample-offset 20 `
  --packet-size 25 `
  --strengths 0.75 `
  --repeats 2 `
  --num-inference-steps 30 `
  --run-root workspaces/black-box/runs/h2-img2img-simple-distance-admission-20260501-r1
```

验证已准备的本地 CLiD 桥接合约：

```powershell
python scripts/review_clid_bridge_contract.py `
  --run-root workspaces/black-box/runs/<clid-bridge-run>
```

在提升前验证 CLiD 分数汇总关卡：

```powershell
python scripts/review_clid_score_schema.py `
  --summary workspaces/black-box/runs/<clid-score-run>/score-summary.json
```

汇总本地双文件 CLiD 桥接输出对：

```powershell
python scripts/summarize_clid_bridge_pair_outputs.py `
  --artifact-dir workspaces/black-box/runs/<clid-bridge-run>/outputs `
  --workspace workspaces/black-box/runs/<clid-bridge-run>/score-summary-workspace
```

规划 `variation`：

```powershell
python -m diffaudit plan-variation --config configs/attacks/variation-plan.yaml
python -m diffaudit probe-variation-assets --config configs/attacks/variation-plan.yaml
python -m diffaudit dry-run-variation --config configs/attacks/variation-plan.yaml
python -m diffaudit run-variation-synth-smoke --workspace experiments/variation-synth-smoke
```

规划 `CLiD`：

```powershell
python -m diffaudit plan-clid --config configs/attacks/clid-plan.yaml
python -m diffaudit probe-clid-assets --config configs/attacks/clid-plan.yaml
python -m diffaudit dry-run-clid --config configs/attacks/clid-plan.yaml --repo-root external/CLiD
python -m diffaudit run-clid-dry-run-smoke --workspace experiments/clid-dry-run-smoke --repo-root external/CLiD
python -m diffaudit summarize-clid-artifacts --artifact-dir "$env:DIFFAUDIT_ROOT/Download/black-box/supplementary/clid-mia-supplementary/contents/CLID_MIA/inter_output/CLID" --workspace experiments/clid-artifact-summary
```

## 灰盒

规划并探测 `PIA`：

```powershell
python -m diffaudit plan-pia --config configs/attacks/pia-plan.yaml
python -m diffaudit probe-pia-assets --config configs/attacks/pia-plan.yaml --member-split-root external/PIA/DDPM
python -m diffaudit dry-run-pia --config configs/attacks/pia-plan.yaml --repo-root external/PIA --member-split-root external/PIA/DDPM
```

运行小型 `PIA` 预览：

```powershell
python -m diffaudit runtime-probe-pia --config configs/attacks/pia-plan.yaml --repo-root external/PIA --member-split-root external/PIA/DDPM --device cpu
python -m diffaudit runtime-preview-pia --config configs/attacks/pia-plan.yaml --repo-root external/PIA --member-split-root external/PIA/DDPM --device cpu --preview-batch-size 4
python -m diffaudit run-pia-runtime-smoke --workspace experiments/pia-runtime-smoke-cpu --repo-root external/PIA --device cpu
python -m diffaudit run-pia-synth-smoke --workspace experiments/pia-synth-smoke-cpu --repo-root external/PIA --device cpu
```

规划并探测 `SecMI`：

```powershell
python -m diffaudit plan-secmi --config configs/attacks/secmi-plan.yaml
python -m diffaudit probe-secmi-assets --config configs/attacks/secmi-plan.yaml
python -m diffaudit prepare-secmi --config configs/attacks/secmi-plan.yaml --repo-root third_party/secmi
python -m diffaudit dry-run-secmi --config configs/attacks/secmi-plan.yaml --repo-root third_party/secmi
python -m diffaudit runtime-probe-secmi --config configs/attacks/secmi-plan.yaml --repo-root third_party/secmi
```

引导本地 `SecMI` smoke 资产：

```powershell
python -m diffaudit bootstrap-secmi-smoke-assets --target-dir tmp/secmi-smoke-assets
```

## 白盒

探测并运行 `GSA`：

```powershell
python -m diffaudit probe-gsa-assets --repo-root external/GSA --assets-root workspaces/white-box/assets/gsa
python -m diffaudit run-gsa-runtime-mainline --workspace workspaces/white-box/runs/gsa-runtime-mainline --repo-root external/GSA --assets-root workspaces/white-box/assets/gsa --resolution 32 --ddpm-num-steps 20 --sampling-frequency 2 --attack-method 1
```

探测并采样 `DiT`：

```powershell
python -m diffaudit probe-dit-assets --repo-root external/DiT --model "DiT-XL/2" --image-size 256
python -m diffaudit run-dit-sample-smoke --workspace experiments/dit-sample-smoke --repo-root external/DiT --model "DiT-XL/2" --image-size 256 --num-sampling-steps 2 --seed 0
```

## Runtime 边界

当前运行的 Runtime 服务位于同级仓库 (`Runtime-Server/`)，不在这里：

```powershell
cd ../Runtime-Server
go run ./cmd/runtime --host 127.0.0.1 --port 8765
```

Research 命令可以写出 Runtime 或 Platform 后续消费的摘要和清单，但服务部署和 HTTP API 工作应保留在 `Runtime-Server/` 或 `Platform/` 中。
