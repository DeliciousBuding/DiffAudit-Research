# Runtime

`Runtime` 是正式的执行控制面，负责 job control plane、runner dispatch、执行状态与健康检查。

当前活跃入口位于：

- `<DIFFAUDIT_ROOT>/Runtime-Server/cmd/runtime`
- `<DIFFAUDIT_ROOT>/Runtime-Server/run-runtime.ps1`

目录名仍是 `Runtime-Server`，是因为本地目录重命名还在进行中；活跃语义已经统一切到 `Runtime`。

`Research` 只负责：

- 研究代码与方法入口
- 实验资产与 admitted 结果
- intake manifests 与 summary schema
- local Python package and CLI validation for research evidence

它不再负责：

- HTTP 服务入口
- job control plane
- 平台控制面语义

Deployment boundary: a teammate can install and validate `Research` with conda,
editable package install, local asset binding, and `diffaudit` CLI commands.
That is different from deploying a service. Service process management,
authentication, public HTTP APIs, and user-facing report delivery must remain in
`Runtime-Server/` and `Platform/`.
