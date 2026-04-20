# 验证与测试计划

## 快速验证

- `uv run --no-project python -m compileall miot_api_server`
- `just check`
- `just --list`

## 语义验证

- 单个非 power-like 可写布尔属性不应支持 `power`。
- 单个明确 power-like 可写布尔属性应支持 `power`，并自动作为默认属性。
- 多个明确 power-like 可写布尔属性应按正式优先级选择默认属性。
- 非候选 `property_name` 应返回 `device_capability_error`。
- 无候选设备执行控制应返回 `device_capability_not_supported`。

## Docker 验证

- `docker build` 成功。
- 缺失 `APP_TOKEN` 时容器启动失败。
- 带 `APP_TOKEN` 启动后，容器内 `/healthz` 可访问。
- `/openapi.json` 未鉴权返回 `401`，带 Bearer token 返回 `200`。

## 残余风险

- 本任务不覆盖真实米家扫码登录。
- 本任务不覆盖真实设备云控执行。
- 本任务不覆盖 VPS 防火墙、HTTPS、域名与反向代理。
