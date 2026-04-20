# 阶段验收

## Stage 1：Spec

- 已完成 task 初始化。
- 已冻结镜像、运行时、持久化与安全 contract。

## Stage 2：代码落地

- 已完成 `Dockerfile`、`.dockerignore`、`justfile` Docker 入口与运行时目录创建逻辑落地。
- 已完成真实 `docker build` 与容器内 `/healthz` 运行验证。

## Stage 3：本机 Docker 基线验证

- 已确认 Docker daemon 可访问。
- 已确认镜像可构建。
- 已确认容器内服务启动后可响应 `/healthz`。
