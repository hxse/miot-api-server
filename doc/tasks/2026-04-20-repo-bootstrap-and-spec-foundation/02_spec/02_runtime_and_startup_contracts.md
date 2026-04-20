# 运行时与启动 Contract

## Provider 边界

- 所有直接调用 `mijia-api` 的逻辑只能放在 Provider 层。
- API 层不直接处理第三方库的登录细节、设备枚举细节、`siid/piid` 解析细节。
- 当前对外不要求用户手工填写 `siid/piid`；这些细节必须封装在 Provider 内部。

## 第一阶段能力 Contract

- 服务必须提供 `Login Init` 能力，用于建立米家帐号会话并持久化认证文件。
- 服务必须提供设备发现能力，并显式暴露设备的 `power` 能力描述。
- 服务必须提供面向设备级 `power` 能力的开/关控制能力。
- 服务必须提供测试重置能力，用于删除认证文件并清理待完成扫码会话。
- 服务必须提供健康检查能力。
- 当前 HTTP 入口冻结为：
  - `GET /auth/status`
  - `POST /auth/reset`
  - `POST /auth/login/start`
  - `POST /auth/login/finish`
  - `GET /devices`
  - `GET /devices/{did}`
  - `POST /devices/{did}/power/on`
  - `POST /devices/{did}/power/off`
  - `GET /healthz`
- 当前辅助页面入口冻结为：
  - `GET /login`
  - `GET /docs`
  - `GET /redoc`
- `/login` 页面在生成二维码后必须立即开始等待扫码确认，不把等待动作推迟到“扫码完成之后再手动触发”。
- `/login` 页面在登录成功后必须能够展示设备列表与设备级 `power` 控制入口。
- `/login` 页面必须为每个支持 `power` 的设备展示可切换的请求示例代码，作为页面联调通过后的自动化调用出口。
- 示例代码必须满足以下约束：
  - 默认显示 `curl`。
  - 点击 `js` 后切换为 JS `fetch` 示例。
  - 统一使用占位 token `YOUR_APP_TOKEN`，不直接回显当前浏览器会话中的真实 token。
  - 自动带入当前设备的 `did`。
  - 当页面上已经选定 `property_name` 时，自动带入当前属性名。
  - 输出为可直接复制执行的单行 curl 命令，不依赖 shell 多行续行格式。
  - 输出为可直接复制的 JS `fetch` 示例代码，不要求用户手工补全 URL、请求头或请求体。

## 路由执行模型 Contract

- `GET /auth/status`
- `POST /auth/reset`
- `POST /auth/login/start`
- `POST /auth/login/finish`
- `GET /devices`
- `GET /devices/{did}`
- `POST /devices/{did}/power/on`
- `POST /devices/{did}/power/off`

以上路由当前都直接调用同步版 `MijiaProvider`，实现上统一使用普通 `def`。

- FastAPI 在线程池中执行这些同步 provider 调用。
- 当前运行时 contract 只约束阻塞归属与执行模型，不承诺改变单次米家云请求耗时。

## 启动方式 Contract

当前任务只冻结 `uv run` 入口：

- `just uv-run` 是当前唯一正式的启动命令入口。
- `just uv-run` 必须启动统一的 FastAPI 应用，而不是临时测试脚本。
- `just uv-run` 当前通过 `uv run --no-project` 从源码树启动应用，不把项目打包构建作为启动前置。
- `just uv-run` 默认显式传入 `--host 0.0.0.0`。
- `just uv-run` 使用 `0.0.0.0` 的理由仅限于当前阶段联调方便；这不是应用级默认 host 语义。
- 其他未显式传 `--host` 的启动入口默认保持 `127.0.0.1`，不复用 `just uv-run` 的绑定语义。
- “其他入口默认 `127.0.0.1`”属于安全 contract，用于防止测试期的公网绑定策略扩散成一般启动默认值。
- `just uv-run` 必须要求显式传入 `APP_TOKEN`。
- `just uv-run` 在 `APP_TOKEN` 缺失或仅包含空白字符时必须立即失败。
- `just uv-run` 不自动生成默认 token。

## 配置与失败语义

- `APP_TOKEN` 是所有入口共享的必填配置。
- `APP_TOKEN` 如果未提供、为空字符串，或去掉空白字符后为空，服务启动应直接报错并拒绝继续启动。
- 认证文件路径需要能通过显式环境变量指定，以保证后续登录结果可复用。
- 设备 spec 缓存路径需要能通过显式环境变量指定。
- 生产环境对外认证头口径默认仍使用 `Authorization: Bearer <TOKEN>`。
