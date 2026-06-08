# 方案取舍

## 方案 1：继续逐点给显式请求补 timeout

这种方式改动局部，但无法覆盖 `mijiaAPI.available` 和 `_request()` 这类第三方库内部请求。后续每发现一个内部调用点都要补洞，容易遗漏。

本任务不选择该方案。

## 方案 2：给 `mijiaAPI` 实例注入默认 timeout session

Provider 创建 `mijiaAPI` 后，把其 `session` 替换为默认 timeout session。该 session 在调用方没有显式传 `timeout` 时自动补入默认值；已有显式 timeout 的请求保持原值。

该方案能覆盖 `available`、设备列表、power 控制和底层 `_request()`，并保持第三方库 API 不变。缺点是仍依赖第三方库内部使用 `api.session` 而不是直接全局 `requests`。

本任务选择该方案作为主方案。

## 方案 3：在依赖版 spec 获取期间临时 patch `requests.get`

`get_device_info()` 是独立函数，不接收 session 参数。为避免引入第二套完整 spec 下载逻辑，本任务只在调用该函数期间临时给无 timeout 的 `requests.get()` 补默认 timeout。

该方案作用范围短，能覆盖依赖内部无 timeout 请求；若依赖已经显式传 timeout，则保持依赖原值。

本任务选择该方案作为 MIoT spec 读取的补充方案。

## 方案 4：fork 或升级 `mijiaAPI`

fork 或升级能从源头修复 timeout，但会改变依赖基线，需要重新验证登录、设备发现与控制链路。

本任务不选择该方案。
