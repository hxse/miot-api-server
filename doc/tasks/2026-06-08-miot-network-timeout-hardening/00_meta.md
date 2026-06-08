# 任务描述

本任务用于彻底收口米家网络请求无 timeout 导致 curl 或网页登录卡住的问题。修复范围覆盖 `mijiaAPI.available` 探测、设备列表、power 控制、MIoT spec 依赖获取、网页登录启动刷新路径与登录完成回调异常处理。

# 任务级别

本任务定级为 `A` 类。原因是它调整 Provider 到第三方米家库的核心网络边界，影响认证探测、认证刷新、设备发现、设备控制与网页登录恢复体验；这些路径属于高耦合状态流与自动化调用主链，网络黑洞时 quietly hang 风险高。

# 任务范围

## In Scope

- 为 Provider 创建的 `mijiaAPI` 实例注入默认 timeout 网络会话。
- 让 `api.available`、设备列表、power 控制等底层 `api.session` 请求受默认 timeout 约束。
- 让业务认证刷新路径、网页登录启动刷新路径、登录完成回调路径具备明确 timeout 与异常映射。
- 让依赖版 `get_device_info()` 读取 MIoT spec 时受 timeout 约束。
- 保持 `APP_TOKEN` Bearer 鉴权、接口形态、认证文件路径、扫码登录 contract 与 power 控制语义不变。
- 使用离线测试覆盖 timeout 注入、请求 timeout 参数、异常映射与关键调用路径。
- 更新 task index，并在验收中记录残余风险。

## Out of Scope

- 不访问真实小米云，不扫码，不控制真实设备。
- 不升级或替换 `mijiaAPI==3.0.5`。
- 不新增第二套完整小米登录协议。
- 不扩展设备能力或通用 MIoT DSL。
- 不改造部署、反向代理、防火墙、HTTP 客户端重试或全局异步执行模型。
