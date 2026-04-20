# 容器与运行时 Contract

## 镜像 Contract

- 仓库必须产出一个可直接运行的单镜像 `Dockerfile`。
- 镜像运行时不得依赖宿主机源码挂载。
- 镜像必须包含启动应用所需的项目依赖和应用代码。
- 镜像入口必须直接运行统一的 `uvicorn` 应用入口，而不是额外发明第二套服务启动器。

## 运行时环境变量 Contract

- `APP_TOKEN` 仍然是必填环境变量。
- 容器在 `APP_TOKEN` 缺失、为空字符串或去除空白后为空时必须启动失败。
- `MIOT_AUTH_PATH` 默认值冻结为 `/data/mijia/auth.json`。
- `MIOT_SPEC_CACHE_DIR` 默认值冻结为 `/data/mijia/spec-cache`。
- `MIOT_PORT` 默认值冻结为 `8000`。

## 监听与端口 Contract

- 容器内部服务必须监听 `0.0.0.0`。
- 容器内部默认端口必须为 `8000`。
- 对外端口暴露不是镜像默认行为，而是 `docker run -p` 的显式行为。
- 本任务的推荐运行示例应以 `-p <HOST_PORT>:8000` 形式表达宿主机映射。

## 持久化 Contract

- 容器启动时必须确保认证文件父目录与 spec 缓存目录存在。
- 镜像必须声明 `/data/mijia` 为 volume 挂载点。
- Docker 路线统一把认证文件与 spec 缓存放在 `/data/mijia` 对应的 volume 中。
- 需要复用登录状态或缓存时，部署者应继续复用同一个 volume。
- `just docker-run` 的默认数据卷名冻结为 `miot-api-server-data`。

## 本地入口 Contract

- `just docker-run` 默认容器名冻结为 `miot-api-server`。
- `just docker-build` 的镜像名冻结为 `miot-api-server:local`。
- `just docker-run` 的默认宿主机端口映射冻结为 `-p 8000:8000`。
- `just docker-run` 展开的默认挂载口径冻结为 `-v miot-api-server-data:/data/mijia`。
- Docker 路线不再为镜像名、容器名、端口或 volume 暴露额外 just 层配置变量；需要变体时直接手写 `docker build` / `docker run`。

## 交付路径 Contract

- 本任务至少冻结两条路径：
  - 本地 `docker build`。
  - VPS `docker run`。
- 两条路径使用相同镜像与相同应用入口，只允许外层参数不同。
