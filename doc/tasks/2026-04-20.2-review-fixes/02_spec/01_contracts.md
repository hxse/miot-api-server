# 修复后 Contract

## Power Capability Contract

- `Power Capability` 只由明确 power-like 的可写布尔属性构成。
- 可写布尔属性必须同时满足：
  - `type` 等于 `bool`。
  - `rw` 包含写权限 `w`。
  - 属性名属于正式允许集合。
- 正式允许集合为：`on`、`switch_status`、`switch`、`power`、`status`。
- 不在正式允许集合内的可写布尔属性不得进入 `power` 候选列表。
- 只有一个明确 power-like 候选时，该候选可作为默认 `power` 属性。
- 存在多个明确 power-like 候选时，Provider 按正式优先级选择默认属性；若无法选择默认属性，则要求调用方显式传入 `property_name`。
- 调用方传入的 `property_name` 只允许匹配当前设备已识别的 `power` 候选属性名。
- 设备没有任何明确 power-like 候选时，`power.supported=false`，控制接口返回 `device_capability_not_supported`。

## 仓库入口 Contract

- `just uv-run` 仍是源码态运行入口。
- `just docker-build` 与 `just docker-run` 仍是 Docker 本地构建与运行入口。
- `just check` 是正式类型检查入口，当前执行 `uvx ty check`。
- `just format` 是正式格式化入口，当前执行 `uvx ruff format`。

## Docker 构建 Contract

- Docker 构建期安装固定版本 `uv`。
- Python 基础镜像当前仍按 `python:3.12-slim` 跟随 Python 3.12 slim minor 更新，不在本任务 pin digest。
- 镜像仍不内置 `APP_TOKEN` 或真实认证文件。
- 容器运行时仍通过环境变量注入 `APP_TOKEN`。

## README 部署 Contract

- README 的 VPS 部署命令块必须可直接复制执行。
- Git clone 的默认分支路径与 backup 分支路径必须以明确二选一方式表达，不得在命令块中放置裸 `or`。
