# 任务描述

本任务用于把当前已经完成 `uv run` 基线的 `miot-api-server` 收口成可构建、可运行、可在 VPS 上直接 `docker run` 部署的单镜像交付物。当前 task 的目标不是扩展业务能力，而是把既有应用封装成一致的容器运行时。

# 任务级别

本任务定级为 `A` 类。原因是它会冻结镜像构建 contract、容器启动入口、运行时数据持久化路径、端口暴露语义、`docker run` 参数口径与部署层最小安全边界，直接影响公开部署方式、运行时行为与后续 VPS 交付基线。

# 任务范围

## In Scope

- 冻结单镜像 Docker 交付模型。
- 冻结容器启动入口、默认监听地址、默认容器端口与环境变量 contract。
- 冻结认证文件与 spec 缓存的容器内持久化路径。
- 冻结本地 `docker build` 与 VPS `docker run` 的最小使用路径。
- 冻结 Docker 场景下的最小安全边界，包括 token 注入方式、端口暴露前提与镜像不内置敏感配置的约束。
- 规划并落地 Docker 相关文件，如 `Dockerfile`、`.dockerignore` 与必要的仓库入口更新。

## Out of Scope

- 不引入 `docker compose`、Kubernetes、systemd 单元、镜像仓库发布流程或 CI/CD。
- 不冻结 HTTPS、反向代理、域名、证书、限流和公网防火墙编排细节。
- 不改变当前 HTTP 路由、登录流程、设备能力模型或鉴权口径。
- 不在本任务中扩展新的设备能力类型或通用 MIoT DSL。
