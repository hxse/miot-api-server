# 术语与正式真值

## 术语

- `miot-api-server`：当前仓库与对外项目名称。
- `mijia-api`：底层第三方依赖名称。
- `Provider Layer`：仓库中唯一允许直接调用 `mijia-api` 的边界层。
- `Login Init`：用于建立米家帐号会话并持久化认证文件的初始化能力。
- `Device-Centric Control`：以设备为一级资源、以能力为设备子路由的控制模型。
- `Power Capability`：设备上可被识别为开关控制的布尔写属性集合。
- `Default Power Property`：Provider 在无需调用方额外指定时可自动选择的默认电源属性名。
- `Selection Required`：某设备存在多个可写布尔属性，且 Provider 无法安全自动裁决时，必须由调用方显式选择属性名的状态。

## 正式真值

- 当前项目定位是“基于 `mijia-api` 的薄 `FastAPI` 封装”。
- 当前底层依赖验证基线是 `uv.lock` 中已解析的 `mijiaAPI 3.0.5`。
- 当前默认控制链路是 `Tasker/HTTP Client -> FastAPI -> Service -> Provider -> mijia-api -> Xiaomi Cloud -> Device`。
- 第一阶段能力范围至少包括：米家帐号登录初始化、设备发现、设备能力描述、设备级 `power` 控制、测试重置与健康检查。
- 第一阶段将扫码登录接口与设备发现能力视为最小闭环的一部分。
- 第一阶段不要求用户手工填写 `siid/piid` 作为主要部署输入；相关规格细节必须封装在 Provider 层内部。
- 第一阶段正式路由集合冻结为：`GET /auth/status`、`POST /auth/reset`、`POST /auth/login/start`、`POST /auth/login/finish`、`GET /devices`、`GET /devices/{did}`、`POST /devices/{did}/power/on`、`POST /devices/{did}/power/off`、`GET /healthz`。
- 第一阶段辅助页面入口冻结为：`GET /login`、`GET /docs`、`GET /redoc`。
- 运行时本地持久化内容冻结为认证文件与设备 spec 缓存。
- 当前执行任务已落地本地 `uv run` 路线；Docker 与 VPS 部署链路留待后续任务冻结。
- `APP_TOKEN` 是显式必填配置，服务不得自动生成默认 token。
- 当前直接调用同步 `MijiaProvider` 的业务路由统一使用普通 `def` 声明，由 FastAPI 线程池承接同步 provider 调用。
- `todo.md` 的角色是立项讨论输入；一旦任务建立，当前任务的 `02_spec` 与当前源码共同构成正式真值。

## 待确认外部条件

- Docker 部署入口、容器镜像与完整项目目录结构。
- HTTPS、反向代理、限流与公网防火墙收口策略。

这些内容在未确认前只能写为待确认项、假设或风险，不能在本任务中伪装成已冻结真值。
