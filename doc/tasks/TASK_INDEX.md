# Task Index

## 2026-04-20.1-docker-image-and-runtime-delivery

- 目标：把当前已完成 `uv run` 基线的 `miot-api-server` 收口成单镜像 Docker 交付物，并冻结本地 `docker build` 与 VPS `docker run` 的最小运行 contract。
- 级别：`A` 类。
- 当前状态：已完成代码落地与本机 Docker 基线验证。
- 已冻结内容：单镜像 `Dockerfile`、`.dockerignore`、`docker-build` / `docker-run` 入口、容器内统一数据目录 `/data/mijia`、`APP_TOKEN` 运行时注入语义、容器内部 `0.0.0.0:8000` 监听 contract、运行时目录自动创建逻辑与最小 Docker 安全边界。
- 未在本任务中解决：`docker compose`、Kubernetes、HTTPS / 反向代理 / 域名证书、镜像仓库发布、CI/CD 与更高层部署编排。

## 2026-04-20-repo-bootstrap-and-spec-foundation

- 目标：作为当前仓库第一阶段的唯一 task snapshot，统一承接立项、技术路线选择、`uv run` 启动基线、最小公网安全约束，以及后续落地后的设备能力导向控制模型。
- 级别：`A` 类。
- 当前状态：已完成代码、页面与文档收口。
- 已冻结内容：项目定位、`mijiaAPI 3.0.5` 验证基线、`uv run` 入口、`APP_TOKEN` 失败语义、`/login` 专用登录页、`/auth/reset` 测试重置、设备为一级资源的控制模型、`/devices/{did}/power/on|off` 正式入口、最小 Bearer 鉴权与文档加载安全口径、同步 provider 业务路由统一使用 `def`。
- 待后续任务解决：Docker 与 VPS 部署链路、HTTPS / 反向代理 / 限流等部署层安全收口、更多设备能力类型与通用能力 DSL。
