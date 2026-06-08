# 验证计划

## 命令

- `uv run --no-project python -m unittest discover -s tests`
- `uv run --no-project python -m compileall miot_api_server tests`

## 离线测试覆盖

- 默认 timeout session 的 get/post/request 参数注入。
- `mijiaAPI` session 注入与 `_init_session()` 后重新注入。
- `available`、设备列表、power 控制通过 timeout session 发出请求。
- `start_login()` 损坏认证文件被映射为 `login_process_error`。
- `start_login()` 旧认证刷新路径不调用底层无 timeout `_get_location()`。
- `start_login()` 二维码登录 URL 请求异常和返回解析异常被映射为 `login_process_error`。
- `finish_login()` 回调异常被映射为 `login_process_error`。
- 依赖版 MIoT spec 获取使用 scoped timeout patch。
- `/api/auth/status` 损坏认证文件和网络异常边界。
