# 认证刷新 Contract

## 术语

- `APP_TOKEN`：服务自身的 Bearer 鉴权密钥，用于保护本服务 API。
- `Mijia Auth File`：由 `MIOT_AUTH_PATH` 指向的米家认证文件，默认包含 `passToken`、`serviceToken`、`ssecurity` 等米家云认证字段。
- `Mijia Refresh`：使用现有米家认证文件中的账号凭据向小米账号服务换取新的米家云认证数据，并写回认证文件。

## 业务入口认证语义

- 所有业务接口必须先通过 `APP_TOKEN` Bearer 鉴权。
- Provider 获取业务用 `mijiaAPI` 实例时，必须保证该实例处于可用于当前业务请求的认证状态。
- 当认证文件缺失时，Provider 必须返回 `authentication_required`，并要求用户完成扫码登录。
- 当认证文件存在但无法解析或缺少构造 `mijiaAPI` 会话所需字段时，Provider 必须返回 `authentication_required`，并要求用户重新扫码登录。
- 当认证文件存在但米家云认证状态不可用时，Provider 必须尝试一次 `Mijia Refresh`。
- `Mijia Refresh` 成功时，Provider 必须复用刷新后的 `mijiaAPI` 实例执行当前业务请求。
- `Mijia Refresh` 失败时，Provider 必须返回 `authentication_required`，并要求用户重新扫码登录。
- `Mijia Refresh` 请求小米账号服务和回调地址时必须显式设置 timeout。
- 米家账号服务网络请求失败时，Provider 必须返回登录处理失败语义，而不是静默降级为业务控制失败。

## 登录页语义

- `/api/auth/login/start` 允许在旧认证文件可刷新时直接刷新认证文件并返回 `already_logged_in=true`。
- `/api/auth/login/start` 在旧认证文件不可刷新时创建扫码登录会话。
- 登录页和业务接口共享同一个 `MIOT_AUTH_PATH`，不得产生两份米家认证真值。

## 失败语义

- 无认证文件：返回 `authentication_required`。
- 认证文件无法解析或缺少必要字段：返回 `authentication_required`。
- 旧认证文件可刷新：当前业务请求正常执行。
- 旧认证文件不可刷新：返回 `authentication_required`。
- 米家账号刷新请求发生网络错误：返回 `login_process_error`。
- 米家账号刷新请求超时：返回 `login_process_error`。
- 业务控制请求发生米家 API 业务错误：保持现有设备能力错误语义。
