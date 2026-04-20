# 请求输入 Contract

## LoginFinishRequest

- `session_id` 必填。
- `session_id` 在校验前会去除首尾空白。
- 去除空白后的 `session_id` 不得为空。
- 去除空白后的 `session_id` 最大长度为 `128`。
- `timeout_seconds` 默认值为 `120`。
- `timeout_seconds` 必须落在 `1..180` 闭区间。
- `timeout_seconds` 不使用 strict int；JSON 字符串数字允许由 Pydantic 解析为整数。
- 请求体额外字段仍然禁止。

## DevicePowerRequest

- 请求体可以缺省，表示让 Provider 使用默认 `power` 属性。
- `property_name` 可以缺省或为 `null`。
- `property_name` 如果提供字符串，会先去除首尾空白。
- 去除空白后的 `property_name` 不得为空。
- 请求体额外字段仍然禁止。

## 非目标

- 响应模型不启用全局 strict。
- Provider 对米家上游字段的归一化策略不变。
- 当前 API 鉴权、路由集合与错误包装格式不变。
