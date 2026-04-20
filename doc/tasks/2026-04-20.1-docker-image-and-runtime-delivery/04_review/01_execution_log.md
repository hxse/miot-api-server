# 执行记录

- 已将 task 目录名收口为 `2026-04-20.1-docker-image-and-runtime-delivery`，用于表达与同日主 task 的顺序关系。
- 已新增 `Dockerfile`，当前采用构建期 `uv sync --locked --no-dev --no-editable`、运行期直接执行 `uvicorn` 的单镜像模型。
- 已新增 `.dockerignore`，避免把 `.git`、`.jj`、`.venv`、`.data` 与 task 文档打进镜像构建上下文。
- 已扩展 `justfile`，新增 `docker-build` 与 `docker-run` 入口。
- 已将 `just docker-run` 的默认容器名收口为 `miot-api-server`，避免随机容器名污染本地联调体验。
- 已将 `just docker-run` 的默认持久化方式收口为命名 volume `miot-api-server-data:/data/mijia`。
- 已把 Docker 入口继续收简为一条固定 `docker build` 和一条固定 `docker run`，不再为镜像名、容器名、端口与 volume 暴露 just 层配置变量。
- 已把运行时目录创建逻辑收口到应用启动阶段，避免再引入单独的脚本型 Docker entrypoint。
- 已恢复 `Dockerfile` 中的 `VOLUME /data/mijia`，统一 Docker 路线下的数据目录挂载语义。
- 已验证 `docker info` 可访问宿主机 Docker daemon。
- 已实际执行 `docker build -t miot-api-server:test .`，镜像构建成功。
- 已实际启动临时容器 `miot-api-server-test`，并在容器内验证 `GET /healthz` 返回 `{"status":"ok"}`。
- 已通过容器日志确认 `uvicorn` 监听 `0.0.0.0:8000`。
- 已清理临时验证容器。
