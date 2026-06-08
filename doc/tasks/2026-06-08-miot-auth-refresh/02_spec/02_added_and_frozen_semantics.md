# 新增语义逻辑

- 业务接口入口新增米家登录态刷新尝试。
- 业务接口入口在旧认证文件可刷新时执行原请求。
- 业务接口入口在刷新失败时再返回 `authentication_required`。
- 业务接口入口在认证文件无法解析或缺少必要字段时返回 `authentication_required`。
- 业务接口入口的米家认证刷新请求显式设置 timeout。
- 米家账号刷新请求的网络错误按登录处理失败语义返回。

# 冻结语义逻辑

- `APP_TOKEN` Bearer 鉴权语义不变。
- `/api/auth/status` 响应字段不变。
- `/api/auth/reset` 清理认证文件与待完成扫码会话的语义不变。
- `/api/auth/login/start` 与 `/api/auth/login/finish` 的扫码登录流程不变。
- `MIOT_AUTH_PATH` 与 Docker volume 持久化语义不变。
- `mijiaAPI==3.0.5` 依赖基线不变。
- 设备发现、设备摘要、power 候选属性识别和 power 控制语义不变。
- 不新增旧接口、兼容接口、桥接接口或第二套认证入口。
