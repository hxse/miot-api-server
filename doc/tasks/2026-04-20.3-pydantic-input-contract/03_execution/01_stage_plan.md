# 阶段计划

## Stage 1：冻结输入 contract

- 建立当前 task。
- 明确请求输入收紧范围与非目标。

验收条件：

- `00_meta.md`、`01_context`、`02_spec` 与当前修复目标一致。

## Stage 2：代码落地

- 修改 `miot_api_server/schemas.py`。
- 更新 task index。

验收条件：

- `LoginFinishRequest` 与 `DevicePowerRequest` 符合当前 spec。

## Stage 3：验证与验收

- 执行 schema 级验证。
- 执行静态 / 类型检查。
- 回填执行记录与最终验收。

验收条件：

- `04_review` 记录验证结果与残余风险。
