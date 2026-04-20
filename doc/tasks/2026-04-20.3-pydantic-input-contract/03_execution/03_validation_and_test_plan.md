# 验证与测试计划

## Schema 验证

- `LoginFinishRequest(session_id=" abc ")` 应得到 `session_id == "abc"`。
- `LoginFinishRequest(session_id="")` 应失败。
- `LoginFinishRequest(session_id="   ")` 应失败。
- `LoginFinishRequest(session_id="a" * 129)` 应失败。
- `LoginFinishRequest(session_id="abc", timeout_seconds="120")` 应解析通过。
- `DevicePowerRequest(property_name=" on ")` 应得到 `property_name == "on"`。
- `DevicePowerRequest(property_name="")` 应失败。
- `DevicePowerRequest(property_name="   ")` 应失败。
- `DevicePowerRequest(property_name=None)` 应通过。

## 快速验证

- `uv run --no-project python -m compileall miot_api_server`
- `just check`
- `just format`

## 残余风险

- 本任务不覆盖真实 HTTP 端到端请求。
- 本任务不覆盖真实米家扫码登录与设备控制。
