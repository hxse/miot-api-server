# 问题背景

当前项目存在两条米家认证相关路径：

- 业务接口路径：curl 或页面控制请求访问 `/api/devices`、`/api/devices/{did}`、`/api/devices/{did}/power/on|off`。
- 登录页路径：网页登录页访问 `/api/auth/login/start`，必要时生成二维码，或者在旧认证文件仍可刷新时直接刷新认证文件。

业务接口路径会先调用 `MijiaProvider._require_api()`。当前实现只检查 `api.available`，如果 `mijiaAPI` 的可用性探测失败，就直接返回 `authentication_required`。这个入口没有给底层 `_refresh_token()` 机会。

登录页路径在 `api.available` 失败后会继续调用 `api._get_location()`。当旧认证文件中的 `passToken` 仍可用于刷新时，这条路径会保存新的米家认证数据，随后 curl 调用又恢复可用。

因此，用户观察到的现象可以由源码解释：一段时间后 curl 业务请求失效，回网页登录页触发登录初始化后，curl 又恢复可用。

# 现有范式

当前仓库已经把米家第三方库调用集中在 Provider 层：

- FastAPI 路由只负责鉴权、请求响应模型与 Provider 调用。
- Provider 负责米家登录态、设备列表、设备能力解析与设备控制。
- 认证文件由 `MIOT_AUTH_PATH` 指定，Docker 默认持久化到 `/data/mijia/auth.json`。
- 底层依赖冻结为 `mijiaAPI==3.0.5`，当前登录初始化已经复用该库的私有方法。

本任务应扩展 Provider 现有认证入口，不在路由层、前端页面或调用方新增临时刷新旁路。
