---
author: Planner
version: 0.4
create_time: 2026-09-16 18:44 +0800
update_time: 2026-09-17 02:19 +0800
status: DRAFT
---

Acquisition 工作约定

这份文档约定 Castle 中 Acquisition 的编号、命名、审计和入库方式。

它只负责 Planner 与其他 People 之间的工作交接，不规定具体实验应该怎样设计。

1. 编号与命名

每个正式 Acquisition 从创建时获得一个编号，并使用同名的采集脚本和说明：

NNN-L3名称-采集内容.txt
NNN-L3名称-采集内容.md

例如：

001-慢充-控制主线采集.txt
001-慢充-控制主线采集.md

编号只用于稳定识别这一次 Acquisition。

原则：

编号简单、唯一、稳定；
从 001、002、003 顺序使用；
修改、REJECT、再次审计不会产生新编号；
同一个 Acquisition 后续实际执行多次，编号仍然不变；
名称优先使用 L3 笔记中已有的名称；
不把版本、审计轮次、状态等信息塞进编号。
2. Planner 与 Auditor

成果的 Artifact Status、Independent Audit Result 及其状态转换统一遵循 Castle 顶层 `PERSON工作规范.md`，本文不重复定义。

提交审计前，Planner 应按 `doc/采集输出规范.md` 从同名 `.source.json` 生成两份输出，并通过跨平台校验。校验只证明格式、内容边界和生成一致性符合约定，不替代 Auditor 的独立审查。

Planner 还应在提交审计前完成内容自审，并在同名 `_SelfAudit.md` 中留下必要结果。内容自审至少确认：

1. 脚本是否覆盖本次采集目的；
2. 每个步骤是否必要，有无为了完整而加入的无关操作；
3. 一个人在现场是否能顺畅执行；
4. 状态变化和等待时间是否合理；
5. 时间标记和现场说明是否足够支持后续数据分析；
6. 内容是否保持车型无关，并未超出可追溯资料的支持范围。

形式自检和内容自审都通过，只表示当前成果具备正式送审条件。此时成果仍为 `DRAFT`；它们是 Planner 的前置质量控制，不是 Formal Submission，也不是 Independent Audit。

Planner 负责发起正式送审。在同名 `_Audit.md` 中建立一轮 Submission，至少记录：

1. Planner 的正式署名和 Submission 时间；
2. 本次审核目的、范围、不在范围内的内容和审核依据；
3. 被审 `.source.json`、`.txt`、`.md` 的文件名及各自 SHA-256；
4. 对应 `_SelfAudit.md` 的引用。

Submission 使用哈希锁定本次被审修订。Planner 不在 Submission 中预填 `auditor`、`audit_time`、`audit_result`、`CONFIRM`、`REJECT` 或 `PUBLISH`。

Planner 完成 Submission、将对应成果状态改为 `TO_AUDIT`，并把该 Submission 实际交付给 Independent Auditor 后，本轮成果才正式进入 `TO_AUDIT`。Auditor 接手时应看到 `_Audit.md`、其中指定的被审文件和 SelfAudit 记录，并能够按哈希确认自己审核的是哪一版成果。

Auditor 从另一个实际执行者的角度看这份脚本有没有实质问题，在 `_Audit.md` 中签署 `PASS` 或 `REJECT`，不直接修改被审的 `.source.json`、`.txt`、`.md` 或 `_SelfAudit.md`。

独立审查提出实质问题时，Planner 根据问题自行判断怎样修改原来的 `.txt` 或 `.md`，完成后重新执行 SelfCheck 和 SelfAudit，再次提交独立审查。

Auditor 负责发现问题和给出结果，不替 Planner 重写脚本。Planner 只能依据 Auditor 已签署的结果同步自己负责成果的状态，不得自行产生 Independent Audit 结论。

3. Audit 记录

每个 Acquisition 只使用一份 Audit 文档：

001-慢充-控制主线采集.txt
001-慢充-控制主线采集.md
001-慢充-控制主线采集_SelfAudit.md
001-慢充-控制主线采集_Audit.md

`_SelfAudit.md` 是 Planner 内部工作记录，保存设计调整、SelfCheck 和 SelfAudit。

`_Audit.md` 是正式提交 Independent Audit 的文件，由 Planner 和 Auditor 记录提交、Auditor 意见、Planner 对 Audit Finding 的响应、重新提交和发布事实。

每轮 Auditor 意见、Planner 响应、重新提交和发布事实继续记录在同一份 _Audit.md 中，不另外建立 Review、Response 或 Re-Audit 文件。其中的 Artifact Status 和 Independent Audit Result 按 Castle 顶层公共规范记录。

`.txt` 始终只保存最终要拿到现场执行的时间、操作和必要说明，不包含标题、采集条件或表头。

每个时间点的第一行是可用于文本转语音的事件文本，不加“播报”或引号；后续缩进行是状态、操作或必要说明。

同名 `.md` 只补充能帮助完成采集、但不适合放入纯脚本的必要内容。说明应简洁有效，不写成长篇计划或分析文档。

通用汽车知识可用于设计车型无关的过程，但不得自行在输出中加入车企、品牌、具体车型、品牌 App 或专属操作路径。

_SelfAudit.md 和 _Audit.md 都不属于正式 Acquisition Asset。

4. 发布入库

Independent Audit 通过且成果进入顶层规范定义的已审查未发布状态后，Planner 确认当前 `.txt` 和同名 `.md` 是通过审计的最终版本，并将它们保存在本地工作目录。

在发布授权完成前，不得写入 Castle Assets。

按顶层规范完成发布授权后，Planner 才将两份最终输出物放入：

Castle/assets/Acquisition/

例如：

Castle/assets/Acquisition/
├─ 001-慢充-控制主线采集.txt
└─ 001-慢充-控制主线采集.md

进入 Assets 的只有已通过 Independent Audit 并完成发布授权的正式 `.txt` 和同名 `.md`。

以下内容不进入：

_SelfAudit.md；
_Audit.md；
尚未通过审计的脚本；
临时草稿和工作过程文件。

入库后，这两份文件共同成为 Castle 可以被其他 People 查找、引用和执行的 Acquisition Asset。

到这里，这一次 Acquisition 工作结束。

不需要另外生成入库报告、确认报告或其他收尾文件。
