---
author: Planner
version: 0.1
create_time: 2026-09-17 02:19 +0800
update_time: 2026-09-17 02:19 +0800
status: TO_AUDIT
---

# 002-直流快充-控制主线采集 Audit

## Submission 1 — Planner

Submission Time: 2026-09-17 02:19 +0800

### Audit Request

- Purpose: 审核本次正常直流快充采集能否取得从未连接、车桩通信与功率建立、稳态快充到正常退出的连续 CAN 数据，并以必要现场取证支持后续 L3 控制主线分析。
- Scope: 未连接基线、插枪与连接确认、充电发起、车桩通信与充电准备、功率建立、稳态快充、正常停止、高压与功率退出、安全解锁及拔枪后的断开状态。
- Out of Scope: 不主动制造故障或保护分支；不执行 DTC 读取；不在本轮解释或诊断采集所得 Signal。
- Audit Basis: L3 Knowledge `新能源汽修L3学习-直流快充`；`doc/采集输出规范.md`。

### Submitted Artifacts

- `002-直流快充-控制主线采集.source.json` — SHA-256 `d6e7a397cc1980d8c1237f23abb3f8dce0803c05e43c278f80d2280daf751d54`
- `002-直流快充-控制主线采集.txt` — SHA-256 `039d1c9c1ab25dd49f86f322d78602692f0050cadda639b3f15d3d7ac72e72d7`
- `002-直流快充-控制主线采集.md` — SHA-256 `9f09dd66d8ae25efe87499f4f408b3cc849e0b9b0e790425105feaa1511ff21e`

### SelfAudit

- `002-直流快充-控制主线采集_SelfAudit.md`
