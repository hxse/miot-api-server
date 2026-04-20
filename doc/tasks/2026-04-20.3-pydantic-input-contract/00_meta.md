# 任务描述

本任务用于收紧公开请求体的 Pydantic 输入 contract：对登录完成请求的 `session_id` 与设备电源控制请求的 `property_name` 增加非空、去空白与长度约束，同时保留当前响应模型、Provider 归一化策略和 `timeout_seconds` 的宽松数字解析。

# 任务级别

本任务定级为 `A` 类。原因是它调整公开 HTTP 请求体的校验 contract，直接影响 `/auth/login/finish` 与 `/devices/{did}/power/on|off` 的失败语义；虽然改动范围局部，但属于公开 API 边界变化。

# 任务范围

## In Scope

- 为 `LoginFinishRequest.session_id` 增加去空白、非空与最大长度约束。
- 为 `DevicePowerRequest.property_name` 增加去空白与非空约束，并保留可缺省 / `null` 语义。
- 明确 `timeout_seconds` 暂不使用 strict int，保留数字字符串到整数的解析兼容性。
- 明确不对响应模型全局开启 Pydantic strict。
- 补充验证，覆盖空字符串、全空白、超长 `session_id`、正常请求与数字字符串 `timeout_seconds`。

## Out of Scope

- 不引入 `pydantic-settings`。
- 不全局启用 `ConfigDict(strict=True)`。
- 不把所有字段替换为 `StrictStr` / `StrictBool`。
- 不修改 Provider 与米家上游数据归一化策略。
- 不改变路由集合、鉴权口径、Docker 交付路径或设备能力模型。
