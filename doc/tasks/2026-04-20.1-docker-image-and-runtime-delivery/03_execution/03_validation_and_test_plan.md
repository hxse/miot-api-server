# 验证与测试计划

## 构建验证

- `docker build` 成功。
- 镜像不依赖宿主机源码挂载即可启动。

## 运行验证

- 缺失 `APP_TOKEN` 时容器启动失败。
- 带 `APP_TOKEN` 启动后，`GET /healthz` 返回 `200`。
- `/login`、`/docs`、`/redoc` 页面可打开，且鉴权口径与源码态一致。

## 持久化验证

- 镜像声明的 `/data/mijia` volume 可被 Docker 正常创建。
- 复用同一个 volume 时，重启容器后认证文件与 spec 缓存可复用。
- `just docker-run` 默认使用命名 volume `miot-api-server-data`。

## 本地入口验证

- `just docker-run` 展开的 `docker run` 命令必须包含固定容器名 `miot-api-server`。
- `just docker-run` 展开的 `docker run` 命令必须显式挂载 `miot-api-server-data:/data/mijia`。

## 回归验证

- 当前 HTTP 路由集合不变。
- 当前 Bearer token 语义不变。
- 当前设备控制路径与失败语义不变。
