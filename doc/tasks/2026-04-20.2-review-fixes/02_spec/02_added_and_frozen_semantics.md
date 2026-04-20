# 新增语义逻辑与冻结语义逻辑

## Added Semantics

- 新增 power-like 属性名白名单。
- 新增“非 power-like 可写布尔属性不进入 `power` 候选”的安全语义。
- 新增 `just check` 与 `just format` 作为仓库正式入口。
- 新增 Docker 构建期 `uv` 版本 pin。
- 新增 README 部署命令块必须可复制执行的文档 contract。

## Frozen Semantics

- 设备仍是一级资源，`power` 仍是设备子路由。
- 不暴露 `siid/piid` 作为主要部署输入。
- `Authorization: Bearer <TOKEN>` 鉴权口径不变。
- `APP_TOKEN` 必填、空白即失败、禁止自动生成的语义不变。
- Docker 容器内 `/data/mijia` 数据目录、`0.0.0.0:8000` 监听与 volume 持久化语义不变。
- 本任务不改变 `mijiaAPI 3.0.5` 验证基线。
