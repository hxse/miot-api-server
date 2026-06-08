# Contract Tests

## Timeout Session

- 未显式传 `timeout` 的 `session.get()` 自动注入默认 timeout。
- 未显式传 `timeout` 的 `session.post()` 自动注入默认 timeout。
- 已显式传 `timeout` 的请求保留调用方指定值。
- `mijiaAPI` 实例构造后已有 session 时会被替换为 `Timeout Session`。
- `api._init_session()` 之后 Provider 必须重新注入 `Timeout Session`。

## Provider 主链

- `api.available` 探测通过 timeout session 发起请求。
- 业务入口和登录 start 的 `api.available` 网络异常返回登录处理失败语义。
- 设备列表请求通过 timeout session 发起请求。
- power 控制请求通过 timeout session 发起请求。
- 登录 start 遇到损坏认证文件时返回 `login_process_error`。
- 登录 start 的旧认证刷新路径复用带 timeout helper。
- 登录 start 的二维码登录 URL 请求网络异常返回 `login_process_error`。
- 登录 start 的二维码登录 URL 返回解析异常返回 `login_process_error`。
- 登录 finish 的回调请求异常返回 `login_process_error`。
- `/api/auth/status` 遇到损坏认证文件或认证探测网络异常时返回可用响应，不抛 500。

## MIoT Spec

- 依赖版 `get_device_info()` 内部无 timeout 的 `requests.get()` 被注入默认 timeout。
- 依赖版 spec 请求 timeout 时，设备型号能力探测降级为空候选。

## 验证边界

本任务只使用离线替身和 mock 验证，不访问真实小米云、不扫码、不控制真实设备。
