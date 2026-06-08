# 执行记录

- 已在 `MijiaProvider` 中新增业务认证入口 `_new_business_api()` 与 `_refresh_business_api()`。
- 已新增带 timeout 的认证刷新请求路径 `_request_auth_refresh_location()`，替代业务入口直接调用底层 `_refresh_token()`。
- 业务接口调用 `_require_api()` 时，认证文件存在但 `api.available=false` 会先尝试一次带 timeout 的认证刷新路径；刷新成功后复用当前 `mijiaAPI` 实例继续业务请求。
- 认证文件缺失、认证文件无法解析、认证文件缺少必要字段、刷新失败均返回 `authentication_required`。
- 刷新阶段发生 `requests` 网络异常时返回 `login_process_error`。
- 认证刷新请求小米账号服务和回调地址时均显式传入 `MIJIA_AUTH_REFRESH_TIMEOUT_SECONDS`。
- 已新增 `tests/test_provider_auth_refresh.py`，使用离线替身覆盖 Provider 控制流与 `/api/devices` 路由函数回归。
- 路由回归测试不使用 `fastapi.testclient.TestClient`，因为当前依赖未安装 `httpx`；最终测试改为直接调用路由函数并注入离线 request 替身。
- 已执行 `uv run --no-project python -m unittest discover -s tests`，9 个离线测试通过。
- 已执行 `uv run --no-project python -m compileall miot_api_server tests`，通过。
