# 阶段计划

## Stage 1：冻结 timeout 真值

- 建立当前 task。
- 明确所有已发现无 timeout 网络路径。
- 冻结统一 timeout session 与 scoped timeout patch 的 contract。

验收条件：

- `00_meta.md`、`01_context`、`02_spec` 覆盖任务级别、范围、方案取舍、正式 contract、失败语义、语义新增与冻结清单。

## Stage 2：Provider timeout 收口

- 新增默认 timeout session。
- 在 Provider 创建和重新初始化 `mijiaAPI` session 后注入 timeout session。
- 登录 start 复用带 timeout 的认证刷新 helper。
- 登录 finish 回调异常映射为 `login_process_error`。
- 依赖版 MIoT spec 获取加入 scoped timeout patch。
- `/api/auth/status` 收口损坏认证文件与网络异常边界。

验收条件：

- 已发现的无 timeout 主链都被统一边界覆盖。

## Stage 3：离线验证与最终审阅

- 执行离线 unittest。
- 执行 compileall。
- 回填执行记录与最终验收。

验收条件：

- `04_review` 已记录验证结果、残余风险与最终结论。
