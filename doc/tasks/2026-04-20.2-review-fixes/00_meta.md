# 任务描述

本任务用于修复上一轮全面审查发现的问题：收紧第一阶段 `power` 能力识别语义，补齐 Docker 交付验证记录口径，修正 README 部署命令可复制性，正式纳入 `just check` / `just format` 仓库入口，并提升 Docker 构建工具链可复现性。

# 任务级别

本任务定级为 `A` 类。原因是它会调整设备控制的安全判定语义，影响 `/devices/{did}/power/on|off` 是否允许执行；同时更新仓库正式入口、Docker 构建 contract 与部署文档，影响公开使用路径、验证方式和后续交付基线。

# 任务范围

## In Scope

- 收紧 `power` 候选属性识别规则，避免把非电源语义的可写布尔属性静默当成电源开关。
- 冻结明确 power-like 属性名集合与默认属性选择规则。
- 补充可执行验证，覆盖单个非 power 布尔属性、单个明确 power 属性、多个候选属性需要选择。
- 修正 README 中 VPS 部署命令块的可复制性。
- 正式记录 `just check` 与 `just format` 仓库入口。
- pin Docker 构建期 `uv` 版本，并明确基础镜像仍暂按 Python minor tag 跟随。
- 用当前任务记录 Docker 补充验证结果，不反向改写旧 task 的历史验收事实。

## Out of Scope

- 不扩展 `power` 之外的新设备能力。
- 不引入通用 MIoT DSL。
- 不改造底层 `mijiaAPI` 登录流程。
- 不引入 `docker compose`、Kubernetes、反向代理、HTTPS、CI/CD 或镜像仓库发布。
- 不把真实米家扫码、真实设备控制、VPS 防火墙和域名证书纳入本轮验证范围。
