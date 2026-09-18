# Castle PERSON 工作规范

## 1. 目的

本规范定义 Castle（牛堡）中各 Person 产生正式工作成果时共同遵守的最小工作约定。

目标是让 Castle 中的重要工作成果及其正式工作记录能够明确回答：

* 谁创建；
* 当前版本；
* 何时创建；
* 何时更新；
* 当前处于什么状态；
* 是否完成 SelfAudit；
* 是否经过 Independent Audit；
* Audit 结果是什么。

本规范将“成果自身的身份与当前状态”和“SelfAudit / Independent Audit 等过程事实”分开记录，避免为了审计留痕反复修改已经提交审查的成果本体。

本规范只定义公共的文件身份、署名、状态和过程留痕规则。

各 Person 如何完成自己的专业工作，由各自工作区决定。

---

## 2. Person 身份

每个 Person 使用独立的 `PERSON.md` 对外说明自己的身份。

至少包括：

```text
Name
NickName
System
Role
Produces
Signature
```

其中：

* `Name`：正式角色名称；
* `NickName`：Castle 内部日常交流使用的昵称；
* `Signature`：正式工作行为使用的署名。

例如：

```text
Name: Acquisition Planner
NickName: 牛二
Signature: Planner
```

日常交流可以使用 `牛二`。

正式文件创建、修改、SelfAudit、Audit、PUBLISH 等留下持久记录的行为，使用 `Signature`，不使用 `NickName`。

---

## 3. 元数据分层

Castle 将正式元数据分为两类：

### 3.1 Artifact Metadata

Artifact Metadata 描述成果自身的身份和当前工作状态。

正式 Markdown 文档和代码文件应包含：

```yaml
author:
version:
create_time:
update_time:
status:
```

示例：

```yaml
author: Planner
version: 0.1
create_time: 2026-09-16 22:00
update_time: 2026-09-16 22:00
status: DRAFT
```

Artifact Metadata 随成果本体维护。

### 3.2 Process Metadata

Process Metadata 描述围绕成果发生的正式工作过程。

公共字段包括：

```yaml
self_audit_time:
auditor:
audit_time:
audit_result:
```

这些字段必须在适用的正式工作记录中得到真实记录，但**不强制内嵌到每一个 Artifact 本体**。

Process Metadata 可以由以下一种或多种正式记录承载：

* Source / `.source.json`；
* SelfAudit Record；
* Independent Audit Record；
* Manifest 或成果索引；
* Castle 为具体成果类型规定的其他结构化工作记录。

不得为了字段完整而制造尚未发生的 SelfAudit、Independent Audit、Audit Result 或 PUBLISH。

### 3.3 特殊文件类型

#### Markdown

正式 Markdown 文档必须包含 Artifact Metadata。

Process Metadata 按本规范通过适用的正式工作记录承载，不要求全部写入 Markdown 本体。

#### Code

正式代码文件必须包含 Artifact Metadata。

元数据应使用该语言合法且不会影响运行的注释形式表达。

Process Metadata 不要求全部写入代码本体。

#### TXT

面向现场执行的纯 `.txt` 脚本应保持执行内容纯净，不强制内嵌 Artifact Metadata 或 Process Metadata。

其身份、版本、状态及相关过程信息由对应 Source、Manifest 或其他正式工作记录承载。

#### source.json

`.source.json` 使用 JSON 字段记录对应 Artifact 的 Artifact Metadata，并可直接记录或引用 Process Metadata。

具体 JSON Schema 可以由具体成果类型进一步约定，但不得改变本规范中各公共字段的语义。

### 3.4 历史文件迁移

本规范生效后：

* 新创建的正式文件立即遵守本规范；
* 已有正式文件不进行无目的的批量整改；
* 已有正式文件下一次发生实质内容修改时，应按本规范补齐适用的 Artifact Metadata；
* 历史 Process Metadata 只记录能够确认真实发生的事实，不追补或推测不存在可靠记录的过程。
---

## 4. 字段定义

### 4.1 Artifact Metadata 字段

#### author

创建或当前负责该成果的 Person。

必须使用该 Person 在 `PERSON.md` 中声明的 `Signature`。

例如：

```yaml
author: Planner
```

不使用：

```yaml
author: 牛二
```

#### version

成果当前版本。

例如：

```yaml
version: 0.1
```

版本规则可由具体 Person 或具体成果类型根据实际需要进一步约定。

本规范不定义复杂版本生命周期。

#### create_time

成果首次创建时间。

首次创建后保持不变。

#### update_time

成果最近一次发生有效内容修改的时间。

修改成果内容时同步更新。

仅更新独立的 Audit Record，不应因此修改被审 Artifact 的 `update_time`。

#### status

成果当前工作状态。

允许值：

```text
DRAFT
TO_AUDIT
REJECT
CONFIRM
PUBLISH
```

### 4.2 Process Metadata 字段

#### self_audit_time

Author 最近一次完成 SelfAudit 的时间。

SelfAudit 是生产者对自己成果进行的专业自审。

SelfAudit 不属于 Independent Audit，也不能产生 `CONFIRM`。

#### auditor

最近一次执行 Independent Audit 的 Person。

使用 Auditor 自己 `PERSON.md` 中声明的 `Signature`。

例如：

```yaml
auditor: Auditor
```

#### audit_time

最近一次 Independent Audit 完成时间。

#### audit_result

最近一次 Independent Audit 的结果。

允许值：

```text
PASS
REJECT
```

Process Metadata 应记录在适用的正式过程记录中，不要求因为 Audit 的发生而修改已经提交审查的 Artifact 本体。
---

## 5. 文件状态

### DRAFT

文件正在创建或修改。

此时内容尚未准备提交 Independent Audit。

### TO_AUDIT

Author 已完成当前版本的工作，并完成必要的 SelfCheck 与 SelfAudit。

文件等待 Independent Audit。

### REJECT

Independent Audit 发现需要处理的实质问题。

文件退回 Author。

Author 开始修改后，文件可重新进入 `DRAFT`。

修改完成并再次完成 SelfAudit 后，可重新进入 `TO_AUDIT`。

### CONFIRM

Independent Audit 已通过。

此状态表示当前成果已经完成独立审查，但尚未表示已经发布为 Castle Asset。

### PUBLISH

已经完成发布授权。

只有适用于 Castle Asset 发布流程的成果才需要进入此状态。

---

## 6. Status 与 Audit Result 的区别

`status` 表示：

> 文件现在处于哪里。

`audit_result` 表示：

> 最近一次 Independent Audit 得出了什么结果。

两者不是同一个概念，也不要求必须存放在同一个文件中。

下面的 YAML 仅用于展示 Artifact 当前状态与最近一次 Audit 事实合并查看时的逻辑关系，不表示这些字段必须全部内嵌于 Artifact 本体。

例如，一份成果被 Auditor `REJECT` 后，Author 已经重新开始修改：

```yaml
status: DRAFT
audit_result: REJECT
```

表示：

* 最近一次 Independent Audit 的结果仍然是 `REJECT`；
* 但文件当前已经回到修改状态。

重新修改并完成 SelfAudit 后：

```yaml
status: TO_AUDIT
self_audit_time: 2026-09-16 22:30
audit_result: REJECT
```

表示当前版本已经重新等待 Independent Audit，而 `REJECT` 仍然记录最近一次 Audit 的历史事实。

再次 Audit 通过后：

```yaml
status: CONFIRM
auditor: Auditor
audit_time: 2026-09-16 22:40
audit_result: PASS
```

发布后：

```yaml
status: PUBLISH
auditor: Auditor
audit_time: 2026-09-16 22:40
audit_result: PASS
```

---

## 7. SelfAudit 与 Independent Audit

### SelfAudit

由成果生产者自己完成。

主要回答：

> 我自己的成果是否已经达到可以交给独立 Auditor 检查的程度？

SelfAudit 可以发现问题并继续修改。

SelfAudit 没有 Independent Audit 的裁决权。

### Independent Audit

由独立 Auditor 完成。

Auditor 独立判断成果是否存在影响其目标、实际使用或后续工作的实质问题。

Independent Audit 可以产生：

```text
PASS
REJECT
```

对应文件状态可以进入：

```text
PASS   → CONFIRM
REJECT → REJECT
```

Auditor 不替 Author 修改被审成果。

---

## 8. 正式署名

Person 对正式文件产生可持久化影响时，使用自己的 `Signature`。

包括但不限于：

* 创建正式文件；
* 修改正式文件；
* 完成 SelfAudit；
* 执行 Independent Audit；
* 改变正式 Audit 状态；
* 执行 PUBLISH。

`NickName` 用于 Castle 内部人与 Person 之间的日常交流，不作为正式署名。

---

## 9. Person 工作目录

每个 Castle Person 应具有自己的 `work/` 目录。

```text
people/
└─ <person>/
   └─ work/
```

`work/` 是该 Person 的当前工作空间，用于保存其执行任务过程中产生和使用的工作文件。

根据具体 Person 的职责，内容可以包括：

* 当前任务的工作源文件；
* 中间结果；
* 待确认或待审成果；
* SelfAudit 留痕；
* Independent Audit 留痕；
* 为完成当前工作所必需的其他过程文件。

`work/` 中存在文件，不表示该文件已经成为 Castle Asset。

正式成果是否进入 Castle Assets，由该成果适用的 Audit 与 PUBLISH 过程决定。

### 工作所有权

每个 Person 对自己的 `work/` 负责。

其他 Person 不因为能够看到该目录而自动获得修改权。

跨 Person 的读取和写入范围由访问者自己的 `manifest.yaml` 明确声明。

例如，Auditor 可以被允许读取另一个 Person 的待审工作成果，同时只允许修改符合其 Audit 输出规则的文件。

Person 不应默认读取或修改其他 Person 的 `work/`。

### 正式工作留痕

`work/` 中属于正式工作过程的成果和记录，应遵循本规范的元数据分层。

Artifact 本体根据文件类型记录适用的 Artifact Metadata：

* `author`
* `version`
* `create_time`
* `update_time`
* `status`

过程记录根据实际发生的工作记录适用的 Process Metadata：

* `self_audit_time`
* `auditor`
* `audit_time`
* `audit_result`

Process Metadata 不要求复制到每一个 Artifact 本体。

对于纯现场 `.txt` 脚本，其元数据由对应 Source、Manifest 或其他正式记录承载，脚本本体保持纯净。

对于 `.source.json`，应以结构化 JSON 方式记录对应 Artifact Metadata，并可记录或引用 Process Metadata。

具体字段根据成果和记录实际经历的工作过程填写。

不得为了字段完整而制造并未实际发生的 SelfAudit、Independent Audit 或 PUBLISH。

已有正式文件不进行无目的批量整改；下一次发生实质内容修改时，再按本规范补齐适用的 Artifact Metadata。


## 10. 原则

本规范解决的是：

> Castle 的成果是谁做的、现在是什么状态、经过了什么正式检查。

本规范不解决：

> Person 应该如何思考和完成自己的专业工作。

不要因为存在公共状态和元数据，就要求所有 Person 使用相同的工作方法。

不要为了审计留痕而要求每次 Audit 都修改被审 Artifact 本体。

不要为了填写字段而制造没有实际发生的 SelfAudit、Audit 或 PUBLISH。

**Artifact 记录成果本身，Process Record 记录过程事实；记录真实发生的工作，不为了完整而制造流程。**
