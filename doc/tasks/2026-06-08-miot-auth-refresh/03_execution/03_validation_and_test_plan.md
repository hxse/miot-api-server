# 验证计划

## 静态与构建验证

- `uv run --no-project python -m compileall miot_api_server`
- `uv run --no-project python -m unittest discover -s tests`

## Provider 控制流验证

- 用离线替身 `mijiaAPI` 验证认证文件缺失时返回 `authentication_required`。
- 用离线替身 `mijiaAPI` 验证认证文件无法解析时返回 `authentication_required`。
- 用离线替身 `mijiaAPI` 验证认证文件缺少必要字段时返回 `authentication_required`。
- 用离线替身 `mijiaAPI` 验证 `available=true` 时不触发刷新。
- 用离线替身 `mijiaAPI` 验证 `available=false` 且刷新成功时返回刷新后的实例。
- 用离线替身 `mijiaAPI` 验证 `available=false` 且刷新失败时返回 `authentication_required`。
- 用离线替身 `mijiaAPI` 验证刷新阶段网络异常时返回 `login_process_error`。
- 用离线替身 `mijiaAPI` 验证认证刷新请求显式传入 timeout。

## 路由级验证

- 本任务验收只使用离线测试，不访问真实小米云。
- 真实扫码与真实设备控制不作为本轮验证内容。
