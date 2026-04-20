# 执行记录

- 已新增 `2026-04-20.3-pydantic-input-contract` task。
- 已在 `schemas.py` 中新增 `SessionId` 与 `PowerPropertyName` 约束类型。
- 已将 `LoginFinishRequest.session_id` 收紧为去空白、非空、最大长度 `128`。
- 已将 `DevicePowerRequest.property_name` 收紧为去空白、非空，同时保留缺省与 `null`。
- 已保留 `timeout_seconds` 的非 strict int 解析；`"120"` 仍可解析为 `120`。
- 已执行 schema 级验证，覆盖正常去空白、空字符串、全空白、超长 `session_id`、数字字符串 `timeout_seconds`、`property_name=None` 与请求体缺省。
- 已执行 `just format`，格式化 `schemas.py`。
- 已执行 `uv run --no-project python -m compileall miot_api_server`，通过。
- 已执行 `just check`，通过。
