# 停电恢复后记 — DDPM-750k 训练工程改进

日期：2026-06-22

## 事件时间线

| 时间 | 事件 |
|------|------|
| 06-22 05:13 | 最后 checkpoint 保存（step 260,000） |
| 06-22 ~05:30 | 宿舍停电，训练进程 + DataLoader workers 被 kill |
| 06-22 ~10:30 | 恢复供电，手动恢复训练 |
| 06-22 10:50 | 从 260k checkpoint 成功恢复，丢失 ~7,600 步 |

## 暴露的问题

### 1. stdout 缓冲导致监控失明
- **症状**：训练恢复后 monitor.py 多次读取日志无新内容（卡在旧 crash 日志）
- **根因**：`python train.py --resume >> training.log` 重定向时 Python 默认全缓冲
- **修复**：强制使用 `python -u`（无缓冲）；在 print 语句加 `flush=True`

### 2. 旧 crash 错误残留混淆 monitor
- **症状**：monitor 报告 4 个 Error，实际是上一次 crash 的 stack trace
- **根因**：monitor 扫描整个 log 文件，不区分新旧 session
- **修复**：训练脚本加 `--- SESSION START ---` 标记；monitor 改为 session-aware（只扫描最新 session 之后的错误）

### 3. 无心跳检测，无法判断死/活
- **症状**：恢复后多次 monitor 读到的都是旧数据，无法区分是"缓冲未刷新"还是"进程已死"
- **根因**：没有独立于 stdout 的存活信号
- **修复**：每 100 步写 `heartbeat.json`（含 timestamp + step），monitor 读心跳判断存活（>5min 无心跳 = DEAD）

### 4. DataLoader worker 无自动恢复
- **症状**：停电 kill 掉 4 个 DataLoader worker 后训练进程 crash
- **根因**：`next(data_iter)` 遇到 RuntimeError 直接向上抛，无重试逻辑
- **修复**：加 try/except RuntimeError 在 data loading 处，捕获后重建 DataLoader

### 5. 手动恢复流程不标准
- **症状**：尝试了 5 次才恢复成功（两次后台进程、一次 stdout 重定向问题）
- **根因**：没有标准化恢复流程文档
- **修复**：恢复流程写入 train script docstring 作为注释参考

## 改进汇总

| # | 文件 | 改进 | 效果 |
|---|------|------|------|
| 1 | `train_*.py` | 加 `flush=True` + 文档加 `python -u` 要求 | stdout 实时刷新 |
| 2 | `train_*.py` | 加 `--- SESSION START ---` 标记 | 日志 session 边界清晰 |
| 3 | `train_*.py` | 加 `write_heartbeat()` + `heartbeat.json` | 独立存活信号 |
| 4 | `train_*.py` | 加 `resilient_dataloader()` + mid-loop recovery | DataLoader 崩溃自动恢复 |
| 5 | `monitor.py` | Session-aware 错误检测 | 不误报旧 crash |
| 6 | `monitor.py` | Heartbeat liveness 检测 | 区分缓冲延迟 vs 进程死亡 |
| 7 | `monitor.py` | 加 `alive` 字段到 monitor.json | 外部 cron 可判断健康 |

## 当前训练恢复步骤（标准化）

```powershell
# 1. 检查最新 checkpoint
ls D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-750k/checkpoint-step*.pt

# 2. 杀掉所有僵尸进程
powershell -Command "Stop-Process -Name python -Force"

# 3. 确认 GPU 空闲
nvidia-smi

# 4. 一键恢复（自动找最新 ckpt）
python -u train_ddpm_cifar10_750k.py --resume >> training.log 2>&1 &

# 5. 验证存活
python monitor.py
# 应看到: [261xxx/750000] loss=... DEAD? 消失即活
```

## 经验教训

1. **日志不是心跳**：不能靠 stdout 判断训练死活，需要独立的 heartbeat 信号
2. **重定向缓冲是陷阱**：Python 非 TTY 输出默认全缓冲，`-u` 或 `flush=True` 必须
3. **日志要分 session**：追加模式的日志需要内部边界标记
4. **Checkpoint 是生命线**：每 10k 步保存意味着最多丢失 ~40 分钟，在可接受范围
5. **恢复流程要文档化**：紧急时刻的慌乱会放大简单问题的解决时间
