---
author: Analyst
version: 0.1
create_time: 2026-09-17
update_time: 2026-09-17
status: DRAFT
---

# S0035 Acquisition Package Validation

## Scope

本次只验证采集包格式、采集脚本与 VoiceRunner Event 的一致性，以及 Event Clock 是否落入 ASC 文件级时间范围。

未解析 CAN Payload，未进行 DBC 解码、Signal 分析、Recognition 或 Evidence Assessment。

时间映射依据采集包内《can采集时间段与采集脚本的时间差异.txt》：脚本 0 秒不是 CAN 起点；CAN 在 E02 附近开始，在 E10 附近结束。

## Inputs

- Vehicle：`TESLA-M3-SOP5`（采集包直属上层目录）
- Round：`S0035`
- Script：`001-慢充-控制主线采集.txt`
- VoiceRunner JSON：`session.json`
- Event Timeline：`event_timeline.csv`
- ASC：`can/can_20260917132305.asc`

## Package Validation

- Result：`PASS`
- Issues：无
- Events：11
- Resources：5 张照片
- ASC files：1

采集脚本、JSON 和 CSV 均包含 11 个相同顺序的 Event。每个 Event 的动作、详细说明、计划秒数及 JSON/CSV 触发时间逐项一致。

`session.json` 中的 `source_script_name` 为 `001-慢充-控制主线采集_2.txt`，实际随包脚本文件名为 `001-慢充-控制主线采集.txt`。内容逐项一致，但文件名不一致，保留为追溯提示。

## ASC Coverage

- ASC start：`2026-09-17T13:24:06.000+08:00`
- ASC end：`2026-09-17T13:30:50.968+08:00`
- ASC duration：`404.9687 s`

| Event | Plan | Actual deviation | Relative to ASC start | Remaining to ASC end | Covered |
|---|---:|---:|---:|---:|---|
| E01 | 0 s | +0.061575 s | -17.783 s | 422.751 s | No |
| E02 | 15 s | +0.065460 s | -2.780 s | 407.748 s | No |
| E03 | 30 s | +0.074544 s | 12.230 s | 392.738 s | Yes |
| E04 | 60 s | +0.051364 s | 42.206 s | 362.762 s | Yes |
| E05 | 150 s | +0.000442 s | 132.155 s | 272.813 s | Yes |
| E06 | 270 s | +0.085613 s | 252.241 s | 152.727 s | Yes |
| E07 | 345 s | +0.096251 s | 327.251 s | 77.717 s | Yes |
| E08 | 360 s | +0.080016 s | 342.235 s | 62.733 s | Yes |
| E09 | 375 s | +0.088738 s | 357.244 s | 47.724 s | Yes |
| E10 | 420 s | +0.003966 s | 402.159 s | 2.809 s | Yes |
| E11 | 435 s | +0.105433 s | 417.260 s | -12.292 s | No |

## Conclusion

采集包格式良好。ASC 时间范围符合时间差异说明：它不是从脚本 E01 开始，也不是到 E11 结束，而是从 E02 后约 2.780 秒开始，到 E10 后约 2.809 秒结束。

E03 至 E10 的 Event Clock 位于 ASC 范围内；E01、E02 和 E11 不在 ASC 范围内。E10 虽被覆盖，但只有约 2.809 秒后置数据，若后续分析需要更长的 Event 后窗口，应明确标记为窗口截断。
