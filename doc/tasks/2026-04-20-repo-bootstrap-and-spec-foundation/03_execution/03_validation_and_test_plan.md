# 验证与测试计划

## 快速验证

- 使用 `just --list` 确认仓库级命令入口只保留当前需要的 recipe。
- 使用 `just uv-run` 验证缺失 `APP_TOKEN` 时会立即失败。
- 使用 `uv run --no-project python -c ...` 验证应用可导入、Provider 可初始化、路由集合与当前 Spec 一致。
- 验证直接调用同步 provider 的业务路由已不再是 coroutine function。

## 运行时检查点

- `/login` 页面存在，且能在不使用 query string 的前提下输入 token、发起扫码登录请求与完成登录请求。
- `/login` 页面在生成二维码后会立即进入等待扫码确认状态。
- `/login` 页面在登录成功后可加载设备列表并按设备发起 `power` 控制。
- `/login` 页面在设备卡片中提供 `curl / js` 切换按钮与复制按钮；默认显示单行 curl 示例，切到 `js` 后显示 JS `fetch` 示例代码。
- 两种示例都使用占位 token，并自动带入当前设备 `did` 与当前属性选择结果。
- `GET /healthz` 返回最小存活信息。
- `/docs` 与 `/redoc` 页面存在，但只有提供 token 后才会加载文档内容。
- `/openapi.json` 在缺失或错误 Bearer token 时返回未授权错误。
- 除 `/healthz`、`/login`、`/docs`、`/redoc` 壳页外，其余请求在缺失或错误 Bearer token 时返回未授权错误。
- `GET /auth/status` 在已授权但未登录时返回 `logged_in=false`。
- `GET /devices` 在已授权但尚未完成米家登录时返回 `409 authentication_required`。
- 当设备存在多个 `power` 候选属性且未选择时，返回 `409 device_capability_selection_required`。
- 当设备不支持 `power` 时，返回 `409 device_capability_not_supported`。
- `POST /auth/reset` 会删除认证文件并清空待完成扫码会话。
- `GET /auth/status`、`POST /auth/reset`、`POST /auth/login/start`、`POST /auth/login/finish`、`GET /devices`、`GET /devices/{did}`、`POST /devices/{did}/power/on`、`POST /devices/{did}/power/off` 必须全部被识别为普通 `def` endpoint。

## 当前限制

- 若 `uv run` 需要下载依赖，则验证结果受本机网络与缓存状态影响。
- 当前环境缺少 `httpx` 且不能稳定联网，因此使用直接 ASGI 调用做进程内校验，而不是依赖 `TestClient`。
- 本任务不包含 Docker、反向代理、HTTPS 或公网端口层验证。
