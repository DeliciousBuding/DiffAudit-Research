# Scripts

可复用的工具与实验脚本。所有路径默认从脚本位置推导 repo 结构，可通过 `DIFFAUDIT_DATA` / `DIFFAUDIT_OUTPUT` 覆盖。

## DDPM 训练 + MIA 攻击流水线（2026-05-24 新增）

### 数据准备

| 脚本 | 用途 |
|---|---|
| `prep_cifar10.py` | 从 torchvision 下载 CIFAR-10，按 ReDiffuse split 提取 member 图像 → `.pt` |

### 训练

| 脚本 | 数据集 | 步数 |
|---|---|---|
| `train_stl10_pt.py` | STL-10 (50k members) | 10k |
| `train_cifar10_pt.py` | CIFAR-10 (25k members) | 10k |
| `train_cifar10_100k.py` | CIFAR-10 (25k members) | 100k |

特性：AMP、EMA/10step、梯度裁剪、checkpoint + sample 定期保存。

### 攻击评分

| 脚本 | 目标 | 方法 |
|---|---|---|
| `score_stl10_pia.py` | STL-10 | simple denoising loss |
| `score_stl10_pia_v2.py` | STL-10 | PIA DDIM trajectory |
| `score_cifar10_pia_v2.py` | CIFAR-10 10k/100k | PIA |
| `score_cifar10_secmi.py` | CIFAR-10 10k/100k | SecMI multi-config |
| `score_800k_pia.py` | CIFAR-10 800k | PIA single |
| `score_800k_pia_sweep.py` | CIFAR-10 800k | PIA sweep (i200/i100/i50) |
| `score_800k_secmi.py` | CIFAR-10 800k | SecMI sweep |
| `score_800k_nns.py` | CIFAR-10 800k | ResNet18 on PIA features |
| `score_750k_ddim.py` | CIFAR-10 750k DDIM | PIA + SecMI |
| `score_750k_nns.py` | CIFAR-10 750k DDIM | ResNet18 on PIA features |
| `score_openai_cifar10.py` | OpenAI 500k | incompatible arch |
| `score_hf_ddpm.py` | HF DDPM | incompatible arch |

### 典型流程

```powershell
conda activate diffaudit-research
$env:DIFFAUDIT_OUTPUT = "$env:USERPROFILE\DiffAudit\outputs\my-run"
python scripts/train_cifar10_pt.py           # 训练
python scripts/score_cifar10_pia_v2.py       # 评分
```

### 已知 Checkpoint

| Checkpoint | 兼容 |
|---|---|
| `workspaces/gray-box/assets/pia/checkpoints/cifar10_ddpm/checkpoint.pt` (800k) | PIA/SecMI/NNS |
| `Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt` (750k) | PIA/NNS |

### 结果（2026-05-24）

| Checkpoint | PIA AUC | NNS AUC |
|---|---|---|
| 800k DDPM | 0.885 | 0.990 |
| 750k DDIM | 0.875 | 0.989 |
| 自训练 ≤100k | ≈0.5 | — |

---

## 原有脚本

| 脚本 | 用途 |
|---|---|
| `run_pr_checks.py` | GitHub PR 快速门禁 |
| `run_local_checks.py` | 本地质量检查 |
| `audit_local_storage.py` | 审计本地大文件 |
| `validate_attack_defense_table.py` | 校验攻击-防御汇总表 |
| `export_admitted_evidence_bundle.py` | 导出 admitted evidence bundle |
| `validate_intake_index.py` | 校验 intake index |
| `validate_local_api_registry_alignment.py` | Runtime-Server 注册表一致性 |
| `monitor_gsa_sequence.py` | 监控 GSA 训练进度 |
| `prepare_clid_local_bridge.py` | CLiD 本地运行配置 |
| `launch_dpdm_training.ps1` | 启动 DPDM 训练 |
| `launch_dpdm_target_and_shadows.ps1` | target + shadow 训练 |
| `launch_dpdm_shadow_sequence.ps1` | shadow 训练序列 |
| `run_x90_larger_surface_triscore.py` | X-90 tri-score 复算 |
| `run_x90_tmiadm512_assets.py` | X-90 TMIA-DM 512-surface |
| `run_beans_lora_member_scout.py` | Beans LoRA member scout |
