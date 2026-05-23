# 下一轮执行准入索引

本页是可执行的"下一轮"入口点及其准入/输出合约的索引。
它旨在作为一行条目挂接到 `GLOBAL_TASK_BOARD`，而无需引入每条 track 的 notebook。

## GSA（白盒）下一轮准入门控

Board 一行摘要：
`GSA next-run: tools/gsa_next_run 产出 manifest+provenance（输入哈希 + git + host）作为准入门控。`

命令（无需安装）：

```powershell
cd Research/tools/gsa_next_run
.\run.ps1 --assets-root .\examples\minimal\assets_root --repo-root .\examples\minimal\repo_root --config .\examples\minimal\config --out-dir ..\..\tmp\gsa_next_run_smoke
```

输入：
- `--assets-root <dir>`：运行时资产目录（以目录树形式哈希）
- `--config <file|dir>`：运行配置（以内容形式哈希）
- `--repo-root <dir>`：用于记录 git commit（并可选通过 `--strict` 强制要求仓库干净）

输出（位于 `--out-dir` 下）：
- `manifest.json`：输入 + 哈希 + git + 验证
- `provenance.json`：主机 + 时间戳 + manifest sha256 + 验证

退出码：
- `0`：验证通过
- `2`：验证失败（准入被阻止）

参考资料：
- gate README: [../tools/gsa_next_run/README.md](../tools/gsa_next_run/README.md)

## PIA（灰盒）下一轮准入门控

Board 一行摘要：
`PIA next-run: tools/pia_next_run emits manifest+provenance (config + member split + git + host) before runtime mainline.`

命令（无需安装）：

```powershell
cd Research/tools/pia_next_run
.\run.ps1 --config ..\..\tmp\configs\pia-cifar10-graybox-assets.local.yaml --member-split-root ..\..\external\PIA\DDPM --repo-root ..\..\external\PIA --out-dir ..\..\tmp\pia_next_run_smoke
```

输入：
- `--config <file|dir>`：PIA 运行时配置
- `--member-split-root <dir>`：member split 目录
- `--repo-root <dir>`：用于记录 git commit（并可选通过 `--strict` 强制要求仓库干净）

输出（位于 `--out-dir` 下）：
- `manifest.json`
- `provenance.json`

参考资料：
- gate README: [../tools/pia_next_run/README.md](../tools/pia_next_run/README.md)
- runtime evidence note: [../workspaces/gray-box/2026-04-07-pia-runtime-mainline.md](../workspaces/gray-box/2026-04-07-pia-runtime-mainline.md)
