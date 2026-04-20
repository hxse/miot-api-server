# 阶段计划

## Stage 1：冻结修复真值

- 建立当前修复 task。
- 明确 `power` 识别、仓库入口、Docker pin 与 README 部署文档 contract。

验收条件：

- `00_meta.md`、`01_context`、`02_spec` 与审查 findings 对齐。

## Stage 2：代码与文档修复

- 修改 Provider 的 `power` 候选筛选逻辑。
- 修正 README 部署命令块。
- pin Dockerfile 中构建期 `uv` 版本。
- 更新 task index。

验收条件：

- 代码与文档符合当前 `02_spec`。

## Stage 3：验证与最终审阅

- 执行静态/类型/构建类验证。
- 执行函数级语义验证，覆盖 power 候选筛选关键分支。
- 执行 Docker 基线验证。
- 回填执行记录与最终验收。

验收条件：

- `04_review` 已记录验证结果、残余风险与最终结论。
