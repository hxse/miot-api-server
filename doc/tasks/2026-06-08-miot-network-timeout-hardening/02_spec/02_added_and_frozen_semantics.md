# 新增语义逻辑

- 新增 Provider 统一 `Timeout Session`。
- 新增依赖版 MIoT spec 获取的 `Scoped Timeout Patch`。
- 新增业务入口和登录 start 对认证探测网络异常的登录处理失败语义。
- 新增登录 start 对损坏认证文件的登录处理失败语义。
- 新增登录 start 对二维码登录 URL 请求网络异常与返回解析异常的登录处理失败语义。
- 新增 `/api/auth/status` 对损坏认证文件、认证探测网络异常的显式失败边界。
- 新增登录完成回调网络异常到 `login_process_error` 的映射。
- 新增离线测试覆盖第三方库内部请求 timeout 注入。

# 冻结语义逻辑

- `APP_TOKEN` Bearer 鉴权语义不变。
- 米家认证文件路径与持久化语义不变。
- 二维码登录与登录会话基本流程不变。
- 设备列表、设备摘要、power 候选属性识别与 power 控制语义不变。
- `mijiaAPI==3.0.5` 依赖基线不变。
- 不新增公开接口、兼容接口、桥接接口或第二套认证入口。
