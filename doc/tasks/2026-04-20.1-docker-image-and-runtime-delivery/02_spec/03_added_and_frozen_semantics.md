# 新增语义逻辑与冻结语义逻辑

## Added Semantics

- 新增单镜像 Docker 交付物。
- 新增容器内统一数据目录 `/data/mijia`。
- 新增容器内部默认监听 `0.0.0.0:8000` 的运行时 contract。
- 新增本地 `docker build` 与 VPS `docker run` 两条正式交付路径。
- 新增镜像不依赖宿主机源码挂载的交付约束。

## Frozen Semantics

- 当前 HTTP 路由集合保持不变。
- 当前 `/login` 登录与设备控制页语义保持不变。
- 当前设备为一级资源、`power` 为子路由的控制模型保持不变。
- `APP_TOKEN` 必填、空白即失败、禁止自动生成的语义保持不变。
- `uv run` 仍然是源码态调试入口，不因 Docker 任务而被替换或弱化。
