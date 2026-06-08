# Contract Tests

## Provider 认证入口

- 认证文件缺失时，业务接口认证入口返回 `authentication_required`。
- 认证文件无法解析时，业务接口认证入口返回 `authentication_required`。
- 认证文件缺少构造 `mijiaAPI` 会话必要字段时，业务接口认证入口返回 `authentication_required`。
- 认证文件存在且 `api.available=true` 时，业务接口认证入口返回可用 API 实例，不额外创建扫码会话。
- 认证文件存在且 `api.available=false`，但底层刷新成功时，业务接口认证入口返回刷新后的 API 实例，并允许业务请求正常执行。
- 认证文件存在且 `api.available=false`，且底层刷新失败时，业务接口认证入口返回 `authentication_required`。
- 认证文件存在且刷新阶段发生请求异常时，业务接口认证入口返回 `login_process_error`。
- 认证刷新请求小米账号服务和回调地址时显式传入 timeout。

## 路由回归

- `/api/devices` 在刷新成功后返回设备列表。
- `/api/devices/{did}/power/on|off` 在刷新成功后执行 power 控制。
- `/api/auth/login/start` 在旧认证文件可刷新时返回 `already_logged_in=true`。

## 验证边界

本任务只使用本地可控替身验证 Provider 控制流，不访问真实小米云，不执行真实扫码，不控制真实设备。真实环境可能受小米账号风控、网络和设备在线状态影响，但不作为本任务验收输入。
