# Castle

## 目标

**建立新能源 AI 诊断能力。**

------------------------------------------------------------------------

## 宗旨

Castle 的存在，是为了持续建立真实、可工作的新能源 AI
诊断能力，而不是为了建设一个软件系统，也不以 Agent
数量、工程规模或架构完整性本身为目标。

Castle 遵循以下建城原则：

1.  **能力优先于形式**\
    AI、Agent、Project、Legacy System
    或其他技术载体，都只是能力的实现方式。Castle
    关注的是它能否承担真实工作。

2.  **允许能力在真实工作中生长**\
    不以过度工程化、流程化和治理约束，提前固化尚未成熟的 AI
    能力。先让能力在真实任务中工作，再根据实际需要沉淀和建设。

3.  **Top-down 定方向，Bottom-up 建能力**\
    Castle
    从顶层明确目标、边界和位置；具体能力通过一个个真实任务建立、验证和积累。不为尚未发生的问题提前建设复杂系统。

4.  **持久资产与工作环境分离**\
    Castle 不依赖某一台电脑、某一个 Codex Work、某一次 ChatGPT
    会话、某一个 AI 或某一种当前工具。

5.  **重要能力必须能够 Reboot**\
    不追求保存 AI 的全部运行现场，而保存足够的定义、Context 与
    Assets，使 Castle 及其中重要的 People
    能够在新的工作环境中恢复到可继续工作的状态。

6.  **Root 保持简单**\
    本 README 是 Castle 的最高层 Context 和入口。它负责说明 Castle
    是什么、遵循什么原则、拥有什么 Assets、有哪些
    People，以及如何找到它们，而不是承载所有具体知识和工作细节。

------------------------------------------------------------------------

## Castle Structure

``` text
Castle
│
├─ Root / README.md
│
├─ Assets
│  ├─ L3 Knowledge
│  └─ Vehicle Evidence
│
├─ Reboot
│
└─ People
```

Castle 当前以 GitHub Repository 作为持久化载体。

GitHub 是 Castle 当前的实现载体，而不是 Castle 本身的定义。Castle
的结构、能力和原则不应依赖 GitHub、Codex、ChatGPT、Notion
或其他特定产品才能成立。

------------------------------------------------------------------------

## Assets

Assets 是 Castle 长期拥有、可以被不同 People
和不同任务反复使用的持久资产。

当前 Castle 有两类核心 Assets：

``` text
Assets
│
├─ L3 Knowledge
└─ Vehicle Evidence
```

### L3 Knowledge

L3 Knowledge 是 Castle 关于新能源车辆及诊断对象的系统知识资产。

它包括随着 L3
学习和真实诊断工作不断形成、验证和修正的系统结构、控制主线、控制树、状态、Evidence、诊断知识以及其他经过沉淀的认知资产。

它主要回答：

> **我们理解车辆应该怎样工作。**

L3 Knowledge 当前主要承载于 Notion，但 L3 Knowledge 本身不等于 Notion。

载体可以改变，Asset 的身份不因此改变。

### Vehicle Evidence

Vehicle Evidence
是来自真实车辆、真实实验和真实诊断工作的事实与证据资产。

它主要回答：

> **真实车辆实际上发生了什么。**

当前规划结构：

``` text
Vehicle Evidence
│
├─ Acquisition
│  ├─ Common Baseline
│  └─ Vehicle Model
│     ├─ Baseline
│     └─ Experiments
│
├─ Cases
│
└─ Diagnostics
```

其中：

-   `Common Baseline`：跨车型可复用的通用采集基线。
-   `Vehicle Model / Baseline`：具体车型积累的车型基线。
-   `Vehicle Model / Experiments`：围绕明确目标实施的真实车辆采集实验。
-   `Cases`：真实案例形成的 Evidence Assets。
-   `Diagnostics`：真实诊断工作形成的 Evidence Assets。

Castle 0.1 优先建设 `Acquisition`。

`Cases` 与 `Diagnostics` 当前只确定其在 Castle
中的位置，不因此提前建设。

### Assets 与 Context

Assets 回答：

> **Castle 有什么？**

Context 回答：

> **某个 Person 为完成当前工作，需要知道什么？**

公共 Asset 不等于所有 People 都应读取。

不同 People 根据自己的职责和当前任务，从 Assets 中取得必要的
Context；某些 People 也可以因为职责或工作方法的需要，被明确禁止读取某些
Assets。

Castle 不追求建立一个包含全部知识的巨大公共 Context。

------------------------------------------------------------------------

## Reboot

Reboot 是 Castle 的顶层能力。

它负责使 Castle 本身，或 Castle 中指定的
Person，在新的工作环境中恢复到可继续工作的状态。

概念操作为：

``` text
reboot castle
reboot <person>
```

例如：

``` text
reboot acqplanner
```

Reboot
恢复的是目标所代表的**工作能力**，而不是机械恢复某一个历史会话、某一个
Work、某一台电脑或某一种技术载体。

Reboot 的具体实现，根据 Castle 中真实 People
和真实工作的需要逐步形成，不在纲领中提前规定。

------------------------------------------------------------------------

## People

People 是 Castle 中具有明确职责、能够独立承担一类工作的能力实体。

Person 的实现形式不受限制，可以是：

-   AI
-   Agent
-   Codex Project
-   Legacy System
-   其他能够承担其职责的技术载体

Person 的身份由它在 Castle
中承担的职责和能力定义，而不是由当前使用的产品、模型或运行环境定义。

同一个 Person 可以随着技术变化更换实现载体，而继续保持其在 Castle
中的身份。

Castle 只在真实工作需要一种独立能力时建立相应的 Person。

Person
通过真实任务成长和验证，而不是先追求完整设计，再寻找任务证明其存在价值。

### Castle 0.1 People

``` text
People
│
├─ Acquisition Planner
│  └─ alias: acqplanner
│
├─ Acquisition Analyst
│  └─ alias: acqanalyst
│
└─ Auditor
```

#### Acquisition Planner

负责把已经明确的诊断或学习采集意图，转化为真实车辆上可执行、能够产生有效
Evidence 的采集实验。

它回答：

> **为了得到需要的 Evidence，应该怎样采？**

#### Acquisition Analyst

负责从采集实验及其 Evidence
中进行分析、发现和推理，形成可复用的分析结果，并推动新的 Vehicle
Evidence 产生。

它回答：

> **我们采到了什么？这些 Evidence 能够支持什么？**

#### Auditor

负责独立检查工作所依据的 Evidence
是否足以支持相应判断，并检查结论是否越过 Evidence 所允许的边界。

它回答：

> **这个判断真的被现有 Evidence 支持吗？边界在哪里？**

Auditor 是独立的证据与结论审查能力，而不是其他 People 的行政管理者。

------------------------------------------------------------------------

## Castle 0.1

Castle 0.1 首先建立一条最小、真实、可工作的采集闭环：

``` text
L3 Knowledge
      ↓
Acquisition Planner
      ↓
Acquisition Experiment
      ↓
真实车辆采集
      ↓
Vehicle Evidence
      ↓
Acquisition Analyst
      ↓
分析 / 发现 / 推理
      ↓
Auditor
      ↓
可信的 Evidence 与结论
```

第一项真实任务：

> **从已经完成的慢充控制树采集定义出发，由 Acquisition Planner
> 产生第一份可实际执行的慢充采集实验与采集脚本。**

Castle 后续的 People、Assets、结构和能力，根据真实工作的需要逐步生长。

**不为未来可能需要的东西提前建城。**
