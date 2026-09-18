---
author: Planner
version: 0.1
create_time: 2026-09-17 02:09 +0800
update_time: 2026-09-17 02:09 +0800
status: DRAFT
---

# Castle PERSON 正式送审规则建议

## 1. 建议目的

本建议请 Castle 考虑在顶层 `PERSON工作规范.md` 中补充“正式送审”的最小公共语义，明确 SelfAudit 完成与 Independent Audit 正式接手之间的交接边界。

目标是解决一个通用问题：

> Author 完成 SelfAudit 后，什么事实证明某一个确切版本的成果已经正式交给 Independent Auditor？

本建议不要求所有 Person 使用相同文件名、相同工具或相同审核表格，也不增加新的公共状态。

## 2. 当前规则的缺口

当前公共规范已经正确区分：

- SelfAudit 由 Author 完成，不能产生 `CONFIRM`；
- Independent Audit 由 Auditor 完成，可以产生 `PASS` 或 `REJECT`；
- `PASS` 对应 `CONFIRM`，`CONFIRM` 不等于 `PUBLISH`；
- Artifact 记录成果本身，Process Record 记录过程事实。

但是，现有规则没有明确定义以下过渡：

```text
SelfAudit 已完成
        ↓
正式送审行为
        ↓
TO_AUDIT
        ↓
Independent Auditor 接手
```

现有 `TO_AUDIT` 定义为：

> Author 已完成当前版本的工作，并完成必要的 SelfCheck 与 SelfAudit。文件等待 Independent Audit。

该定义说明了进入 `TO_AUDIT` 的前置条件，但没有说明“等待 Independent Audit”是如何正式成立的。

因此可能出现：

1. Author 将 SelfAudit 通过直接解释为已经正式送审；
2. Artifact 已标记 `TO_AUDIT`，但不存在任何正式 Submission 记录；
3. Auditor 不能无歧义地确认当前审核的成果和确切修订版本；
4. Author 和 Auditor 都可能认为应由对方创建 Audit Record；
5. 对话中的一般性“通过”表达可能被误当成正式 Independent Audit 签署；
6. `PASS` 后如果 Auditor 不允许修改 Artifact，Author 又不允许“自行 `CONFIRM`”，可能不清楚由谁将已发生的 Audit 事实同步到 Artifact Status。

这一缺口不限于 Acquisition。任何会产生可修改文件、数据集、代码、计划或其他正式成果的 Castle Person，都可能遇到同样的送审版本与责任边界问题。

## 3. 建议放置位置

建议在 `PERSON工作规范.md` 第 7 节“SelfAudit 与 Independent Audit”中，放在 `### SelfAudit` 之后、`### Independent Audit` 之前，新增：

```markdown
### 正式送审（Formal Submission）
```

这个位置能够自然表达：

```text
SelfAudit
    ↓
Formal Submission
    ↓
Independent Audit
```

同时建议对第 5 节 `TO_AUDIT` 的定义做一处最小补充，使状态定义与新增小节一致。

## 4. 建议加入公共规范的正文

### 4.1 第 7 节新增小节

建议在 `### SelfAudit` 之后加入以下原文：

```markdown
### 正式送审（Formal Submission）

SelfCheck 和 SelfAudit 完成，只表示 Author 认为当前成果已经具备送交 Independent Audit 的条件，不表示正式送审已经发生。

Author 负责发起正式送审。Author 应在该成果适用的 Independent Audit Record 中建立一次 Submission，并使该 Submission 能够无歧义地确定本次提交的被审成果。

Submission 至少应真实记录：

* Author 的正式署名；
* Submission 时间；
* 被审成果或成果集合的明确引用；
* 能够区分同名成果后续修改的确切修订标识；
* 适用的 SelfAudit Record 引用。

确切修订标识可以是文件哈希、不可变修订 ID、提交 ID、发布包摘要，或该成果类型能够提供同等可靠性的其他方式。具体格式由各 Person 或成果类型的工作约定定义。

如果仅凭被审成果无法准确理解本次工作目的、审核范围或判断依据，Author 还应在 Submission 中直接说明，或引用能够提供这些信息的正式任务资料。Author 不应要求 Auditor 从无关资料或成果内容中猜测 Author 的意图。

Submission 完成并正式交付给 Independent Auditor 后，被审成果才进入 `TO_AUDIT`。

Independent Auditor 接手时，应先确认 Submission 指定的成果、修订标识和必要审核上下文可以正常获取。如果不能无歧义地确定被审对象或审核意图，Auditor 应要求 Author 补齐 Submission，而不应自行猜测、选择或修改被审成果。

Author 不得在 Submission 中预填 Independent Audit 的 Auditor、Audit Time、Audit Result、`CONFIRM` 或 `REJECT`。

Independent Auditor 负责在适用的 Independent Audit Record 中签署 `PASS` 或 `REJECT`，不替 Author 修改被审成果。

如果 Independent Auditor 无权直接修改 Artifact Metadata，Author 可在核对已签署的 Audit Result 后，将被审成果的 `status` 同步为与该结果对应的 `CONFIRM` 或 `REJECT`。该动作只是记录已经发生的 Independent Audit 事实，不构成 Author 自行作出 Audit 结论。
```

### 4.2 第 5 节 `TO_AUDIT` 最小修订

建议将当前文本：

```markdown
Author 已完成当前版本的工作，并完成必要的 SelfCheck 与 SelfAudit。

文件等待 Independent Audit。
```

修订为：

```markdown
Author 已完成当前版本的工作、必要的 SelfCheck 与 SelfAudit，并已按适用工作约定完成 Formal Submission。

被审成果已经正式交付，正在等待 Independent Audit。
```

## 5. 责任边界

采用本建议后，公共责任边界为：

### Author

- 完成成果、SelfCheck 和 SelfAudit；
- 发起 Formal Submission；
- 使 Submission 能够无歧义地确定被审成果和必要审核上下文；
- 在 `REJECT` 后修改成果并重新提交；
- 根据已签署的 Audit Result 同步自己负责的 Artifact Metadata；
- 不自行产生 Independent Audit 结论。

### Independent Auditor

- 核对 Submission 中的被审对象和修订标识；
- 确认审核意图和必要依据可以获取；
- 独立判断成果是否存在影响目标、使用或后续工作的实质问题；
- 在 Independent Audit Record 中签署 `PASS` 或 `REJECT`；
- 不猜测 Author 的意图，不替 Author 修改被审成果。

## 6. 各 Person 仍可自主决定的内容

公共规范只定义 Formal Submission 的语义和责任，不应统一强制：

- Audit Record 必须是 Markdown、Issue、PR、数据库记录或其他特定载体；
- 修订标识必须使用 SHA-256、Git Commit、不可变 ID 或其他特定技术；
- 所有 Person 使用相同的 Audit 表格或审核检查表；
- Auditor 必须能够直接修改 Artifact Metadata；
- 某类成果是否需要 Independent Audit 或 PUBLISH。

这些细节应继续由各 Person 的 `PERSON.md`、工作约定或具体成果类型定义。

## 7. 与现有规则的兼容性

本建议：

- 不改变现有 `DRAFT → TO_AUDIT → REJECT / CONFIRM → PUBLISH` 状态集；
- 不改变 SelfAudit 与 Independent Audit 的权限边界；
- 不要求为历史成果追补不可靠的 Submission 记录；
- 不要求每次 Audit 都修改被审 Artifact 的专业内容；
- 不将 `CONFIRM` 扩张为 `PUBLISH`；
- 只补齐现有公共状态之间已经隐含、但尚未明确记录的正式交接事实。

## 8. 不建议同时加入的内容

为避免将一个简单交接规则扩展成流程系统，本次不建议：

- 增加 `READY_FOR_AUDIT`、`SUBMITTED` 等新状态；
- 强制建立全局 Audit 登记表；
- 为所有成果强制使用 SHA-256；
- 强制所有 Person 使用同一套生成器或自动化工具；
- 要求 Auditor 替 Author 创建 Submission；
- 把 SelfAudit Record 当作 Independent Audit Record。

## 9. 建议结论

建议 Castle 以“Author 发起、Submission 锁定、Auditor 独立裁决”作为正式送审的公共原则：

```text
SelfAudit 完成
    ↓
Author 建立 Formal Submission
    ↓
成果进入 TO_AUDIT
    ↓
Independent Auditor 核对并审核
    ↓
PASS → CONFIRM
REJECT → REJECT
```

这一补充能够让 Castle 中不同 Person 的送审行为具有相同的最小语义，同时保留各 Person 对专业工作方法和审核载体的自主权。
