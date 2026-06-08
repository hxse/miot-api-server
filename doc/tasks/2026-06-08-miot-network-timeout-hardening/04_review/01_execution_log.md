# 执行记录

## Stage 1

- 已建立 `2026-06-08-miot-network-timeout-hardening` 任务文档。
- 已冻结 timeout contract、失败语义、新增语义逻辑与冻结语义逻辑。
- 已明确本任务只做离线验证，不访问真实小米云。

## Stage 2

- 已新增 `TimeoutSession`，Provider 创建和重新初始化 `mijiaAPI` 实例后都会注入默认 timeout session。
- 已将 timeout session、session 注入和 scoped requests patch 拆入 `miot_api_server/mijia_timeout.py`，避免 `provider.py` 继续承载基础设施细节。
- 已让 `available`、设备列表、共享设备列表、power 控制等依赖 `api.session` 的请求受默认 timeout 约束。
- 已让业务入口和网页登录 start 入口把 `available` 网络异常映射为登录处理失败语义。
- 已让登录 start 初始化米家 API 实例时的损坏认证文件映射为 `login_process_error`。
- 已让登录 start 复用带 timeout 的认证刷新 helper，避免直接调用第三方 `_get_location()`。
- 已让登录 start 创建二维码登录 URL 时的网络异常和返回解析异常映射为 `login_process_error`。
- 已包住登录 finish 的最终回调网络异常，统一映射为 `login_process_error`。
- 已为依赖版 MIoT spec 获取增加 scoped timeout patch。
- 已让 `/api/auth/status` 在认证文件损坏或状态探测网络失败时返回未登录状态，不返回 500。

## Stage 3

- 已新增离线 unittest 覆盖 timeout session 默认注入、显式 timeout 保留、Provider session 注入、业务入口和网页登录 start 的 `available` 网络异常映射、登录 start 损坏认证文件、登录 start 刷新 helper、二维码登录 URL 请求异常和返回解析异常映射、登录 finish 回调异常映射、`/api/auth/status` 损坏文件与网络异常、MIoT spec 依赖请求 timeout 注入。
- 已执行 `git diff --check`。
- 已执行 `uv run --no-project python -m compileall miot_api_server tests`。
- 已执行 `uv run --no-project python -m unittest discover -s tests`。
