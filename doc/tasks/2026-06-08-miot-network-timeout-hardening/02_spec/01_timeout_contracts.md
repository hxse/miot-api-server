# Timeout Contract

## 术语

- `Default Network Timeout`：Provider 对第三方米家网络请求施加的默认超时时间。
- `Timeout Session`：在没有显式 `timeout` 参数时自动注入 `Default Network Timeout` 的 requests session。
- `Scoped Timeout Patch`：只在调用指定第三方函数期间，为无 timeout 的 `requests.get()` 注入默认 timeout 的局部补丁。

## 网络边界

- Provider 创建的业务用 `mijiaAPI` 实例必须使用 `Timeout Session`。
- `Timeout Session` 必须覆盖 `get`、`post` 与通用 `request`。
- 当调用方显式传入 `timeout` 时，`Timeout Session` 不得覆盖该值。
- 当调用方未显式传入 `timeout` 时，`Timeout Session` 必须注入 `Default Network Timeout`。
- `api.available`、设备列表、共享设备列表、power 控制等通过 `api.session` 发出的请求必须受 `Timeout Session` 约束。
- Provider 调用依赖版 `get_device_info()` 时必须使用 `Scoped Timeout Patch`，让依赖内部无 timeout 的 `requests.get()` 受默认 timeout 约束。
- Provider 自己发起的米家账号服务、二维码登录、扫码轮询、登录回调、当前 MIoT spec fallback 请求必须保留或补齐显式 timeout。

## 失败语义

- 米家认证探测、认证刷新、二维码登录 URL 获取、设备列表请求发生网络异常或 timeout 时，返回登录处理失败语义。
- 登录 start 初始化米家 API 实例遇到损坏认证文件时，返回登录处理失败语义。
- 二维码登录 URL 返回解析发生 `LoginError`、`JSONDecodeError`、`KeyError` 或 `TypeError` 时，返回登录处理失败语义。
- power 控制请求发生网络异常或 timeout 时，返回设备能力错误语义。
- spec 获取发生网络异常或 timeout 时，只降级当前设备型号的能力探测，不拖垮设备列表主响应。
- 登录完成回调发生网络异常或 timeout 时，返回 `login_process_error`。
- `/api/auth/status` 在认证文件损坏或米家状态探测网络失败时不得返回 500。

## 冻结语义

- `APP_TOKEN` Bearer 鉴权不变。
- `/api/auth/login/start`、`/api/auth/login/finish`、`/api/auth/status` 的响应模型不变。
- 认证文件路径、Docker volume、扫码登录会话、设备发现和 power 控制接口形态不变。
