# 术语与当前真值

## 术语

- `docker image`：本任务产出的单镜像交付物。
- `container runtime`：镜像启动后的容器运行时语义。
- `runtime data dir`：容器内承接认证文件与 spec 缓存的稳定目录。
- `docker delivery path`：`docker build` 与 `docker run` 组成的最小交付路径。

## 当前真值

- 当前业务 HTTP contract 继续以 `2026-04-20-repo-bootstrap-and-spec-foundation` 与当前源码为准。
- Docker task 不改变当前路由集合、Bearer 鉴权口径、登录页能力与设备控制模型。
- 本任务的正式目标是新增单镜像交付路径，而不是替换现有 `uv run` 开发入口。
- 容器内运行时数据根目录冻结为 `/data/mijia`。
- 容器内认证文件路径冻结为 `/data/mijia/auth.json`。
- 容器内 spec 缓存目录冻结为 `/data/mijia/spec-cache`。
- 容器内部默认监听地址冻结为 `0.0.0.0`。
- 容器内部默认服务端口冻结为 `8000`。
