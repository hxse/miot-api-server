# 文件修改清单

## Task 文档

- `doc/tasks/2026-06-08-miot-network-timeout-hardening/00_meta.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/01_context/01_problem_context.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/01_context/02_options_and_tradeoffs.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/02_spec/01_timeout_contracts.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/02_spec/02_added_and_frozen_semantics.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/02_spec/03_contract_tests.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/03_execution/01_stage_plan.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/03_execution/02_file_change_list.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/03_execution/03_validation_and_test_plan.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/04_review/01_execution_log.md`
- `doc/tasks/2026-06-08-miot-network-timeout-hardening/04_review/02_final_acceptance.md`
- `doc/tasks/TASK_INDEX.md`

## 生产代码

- `miot_api_server/mijia_timeout.py`
- `miot_api_server/provider.py`

## 模块拆分判断

- timeout session、session 注入与 scoped requests patch 拆入 `miot_api_server/mijia_timeout.py`。
- `provider.py` 已存在登录、设备、spec 解析三类职责；完整拆分会扩大到业务模块边界重构，本任务只拆出本次新增的 timeout 基础设施。

## 测试

- `tests/test_provider_auth_refresh.py`
- `tests/test_provider_timeout_hardening.py`
