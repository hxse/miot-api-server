# 新增语义逻辑与冻结语义逻辑

## Added Semantics

- 新增请求字符串字段的去空白校验。
- 新增 `session_id` 非空与最大长度约束。
- 新增 `property_name` 非空约束。

## Frozen Semantics

- `timeout_seconds` 的范围仍是 `1..180`。
- `timeout_seconds` 仍允许 Pydantic 的默认数字解析，不强制 strict int。
- `DevicePowerRequest` 仍允许请求体缺省或 `property_name=null`。
- 请求体额外字段仍然禁止。
- 响应模型与 Provider 上游数据归一化策略不变。
- 路由集合、鉴权口径、Docker 交付路径与设备能力模型不变。
