# 问题背景

上一任务修复了 curl 业务路径不触发米家认证刷新的问题，并给业务认证刷新 helper 加了 timeout。但审查发现网络黑洞风险仍存在于更早和更广的调用点：

- `mijiaAPI.available` 会调用 `check_new_msg(refresh_token=False)`，底层 `session.post()` 没有 timeout。
- 设备列表和 power 控制会走 `mijiaAPI._request()`，底层 `session.post()` 没有 timeout。
- 依赖版 `get_device_info()` 可能先用无 timeout 的 `requests.get()` 获取 MIoT spec。
- `/api/auth/login/start` 仍可能调用底层 `_get_location()`，其中账号服务请求和 STS 回调没有 timeout。
- `/api/auth/login/finish` 的最终回调请求虽然传了 timeout，但位于 try 块之外，网络异常可能冒成 500。
- `/api/auth/status` 构造 `mijiaAPI` 或检查 `available` 时，损坏认证文件与网络黑洞都缺少统一边界。

这些问题的共同根源不是认证策略，而是第三方库内部网络请求缺少默认 timeout。

# 现有范式

当前仓库的第三方米家访问统一集中在 `MijiaProvider`。FastAPI 路由不直接处理米家网络细节，Provider 是合适的统一边界。

本任务选择扩展 Provider 的 `mijiaAPI` 实例创建与网络会话注入能力，而不是在每个业务调用点周围散落临时 timeout 包装。
