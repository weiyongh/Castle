# Castle：Reboot 核心讨论

## 1. Reboot 要解决的真正问题

Castle 中的 Person 不能依赖某一次 ChatGPT / Codex 会话、某一个
Work、某一台电脑或某一个模型实例才能存在。

例如 `acqplanner` 当前可能运行在 macOS 上的一个 Codex Project
中。但当发生以下情况时：

-   更换电脑；
-   重新 clone Castle；
-   新建 Codex Work；
-   原有 Chat Context 不再可用；
-   更换兼容的 AI / Agent 运行环境；

它仍然应该能够恢复成一个可以继续工作的 `acqplanner`。

因此：

> **Reboot 不是恢复旧会话，而是恢复 Person 的工作能力。**

真正需要保存的不是"昨天那个 AI 坐过的椅子"，而是让一个 Fresh Agent
坐下来以后，能够重新成为这个 Person，并继续把活干下去。

------------------------------------------------------------------------

## 2. Reboot 的核心定义

对于 Castle 中的 Person，可以把 Reboot 定义为：

> **在一个新的、没有可依赖历史会话的兼容 AI 工作环境中，仅依靠 Castle
> 中持久保存的内容，恢复该 Person 的身份、必要
> Context、已有能力和当前工作状态，使其能够继续承担原有职责。**

因此，Reboot 的验收不是"文件是否备份完整"，而是：

> **失忆以后还能不能继续干活。**

------------------------------------------------------------------------

## 3. Self-Reboot：去中心化恢复

最初可以设想一个中央 `Reboot Agent`：

``` text
Reboot Agent
├─ reboot castle
├─ reboot acqplanner
├─ reboot acqanalyst
└─ reboot auditor
```

但进一步讨论后，一个更自然的方向是：

> **每个 Person 应逐渐具备 self-reboot 能力。**

原因很简单：

真正知道一个 Person 恢复时需要什么 Context、哪些
Assets、哪些工具、哪些工作状态的，应该首先是这个 Person 自己。

因此：

``` text
people/
├─ notioner/
│  └─ self reboot
│
├─ acqplanner/
│  └─ self reboot
│
├─ acqanalyst/
│  └─ self reboot
│
└─ auditor/
   └─ self reboot
```

这符合 Castle 的组织方向：

> **去中心化，避免形成一个掌握所有恢复、审批和管理权力的中央 Agent。**

Reboot 因而不一定需要成为 Castle 根目录中的一个独立"政府部门"。

它更适合作为：

> **每个成熟 Person 应具有的一种生存能力。**

------------------------------------------------------------------------

## 4. 以 macOS Codex `acqplanner` 为例

假设：

``` text
Castle
└─ people
   └─ acqplanner
```

当前 `acqplanner` 是 macOS 上的一个 Codex Agent / Project。

发生 Reboot 时，可以是：

``` text
新的 Mac / 新的工作环境
        ↓
clone Castle
        ↓
Fresh Codex
        ↓
进入 people/acqplanner/
        ↓
读取持久 Context 与工作资产
        ↓
恢复：
我是谁
我负责什么
我的边界是什么
我已经会什么
我正在做什么
为什么工作走到了这里
我还需要哪些 Castle Assets
        ↓
继续工作
```

这才是：

``` text
reboot acqplanner
```

真正应该表达的含义。

------------------------------------------------------------------------

## 5. 当前认为至少需要保存的四类内容

讨论中形成了一个重要判断：

对于真实的 Codex Person，要实现 Reboot，至少可能需要以下四类持久内容：

``` text
Person
│
├─ Project Context
├─ src
├─ Task / Trace Context
└─ Chat Context
```

它们分别恢复不同的东西。

### 5.1 Project Context ------ 恢复"我是谁"

Project Context 保存 Person 长期稳定的身份和工作定义，例如：

-   Person 是谁；
-   负责什么；
-   不负责什么；
-   工作原则；
-   与 Castle 的关系；
-   可以使用哪些 Assets；
-   需要哪些 Context；
-   重要的长期边界。

对于 Codex Project，`AGENTS.md` 可以承担其中的重要部分。

Project Context 不应该塞入大量当前任务状态。

否则每换一个任务，都相当于修改 Person 的人格。

------------------------------------------------------------------------

### 5.2 `src/` ------ 恢复"我已经会什么"

Person 在长期工作中会把一部分能力物化为代码。

例如：

-   数据解析器；
-   Acquisition Plan 生成工具；
-   Script Generator；
-   验证程序；
-   辅助算法；
-   格式转换工具；
-   其他已经通过真实工作形成的程序能力。

这些东西不应该在每次 Reboot 后重新发明。

因此：

> **`src/` 是 Person 已经物化的能力。**

------------------------------------------------------------------------

### 5.3 Task / Trace Context ------ 恢复"我正在干什么，以及为什么走到了这里"

Git 可以保存"改了什么"，但并不一定能够解释：

> **为什么这样做。**

Task Context 需要让 Fresh Agent 理解：

-   当前任务是什么；
-   输入是什么；
-   已经完成了什么；
-   当前输出是什么；
-   下一步是什么。

Trace Context 则只保存那些：

> **如果丢失，新 Agent
> 很可能重新踩坑或无法理解当前工作状态的重要决策轨迹。**

例如：

-   为什么删除某个采集步骤；
-   为什么选择当前实验结构；
-   某个方案为什么已经被否定；
-   某个重要边界是怎样形成的。

Trace 不是完整工作日志。

否则很快会重新形成沉重的流程和文书系统。

------------------------------------------------------------------------

### 5.4 Chat Context ------ 恢复"尚未完全物化的脑子"

这是 Reboot 中很容易被忽视、但可能非常重要的一层。

一个 AI Person 的部分能力，可能是在长期交互过程中逐渐形成的。

这些能力未必已经完全进入：

-   `AGENTS.md`
-   `src/`
-   `doc/`
-   Task
-   Trace
-   Castle Assets

如果 Reboot 时把 Chat Context 全部删除，Fresh Agent
即使看到完全相同的工程文件，也可能发生明显的能力退化。

因此 Chat Context 在当前阶段可以作为：

> **Person 尚未完全物化能力的恢复保险层。**

但是：

> **Chat Context ≠ 永久保存全部聊天。**

理想的长期流动应该是：

``` text
Raw Chat
   ↓
近期有效工作 Context
   ↓
逐渐沉淀
   ├─ Project Context
   ├─ src
   ├─ doc
   ├─ Task / Trace
   └─ Castle Assets
```

Person 越成熟，越应该减少对古老 Chat 的依赖。

------------------------------------------------------------------------

## 6. 当前候选最小 Reboot Set

基于目前讨论，可以暂时提出：

``` text
Project Context
        +
       src
        +
Task / Trace Context
        +
必要的 Chat Context
        +
所需 Castle Assets
        ↓
     Fresh Agent
        ↓
 Person Restored
```

即：

> **Project Context + src + Task / Trace Context + 必要 Chat Context +
> Required Castle Assets**

但这不是固定 Schema。

它只是当前的候选最小集。

真正需要什么，应通过真实 Reboot Test 验证。

------------------------------------------------------------------------

## 7. Agent Reference Folder

为了让 Person 同时能够工作和逐渐形成 Reboot 能力，目前形成的参考目录为：

``` text
<person>/
├─ AGENTS.md
├─ README.md
├─ src/
├─ doc/
├─ work/
├─ tasks/
└─ context/
   ├─ trace/
   └─ chat/
```

各目录承担不同职责：

``` text
AGENTS.md       Project Context / 身份与长期规则

README.md       工作区入口

src/            已物化的可复用能力

doc/            Person 已沉淀的长期文档与认知

work/           当前工作的桌面、中间物和探索区

tasks/          有明确目标的正式工作单元

context/trace/  必要而不可轻易重建的决策轨迹

context/chat/   尚未充分物化的必要 Chat Context
```

其中 `work/` 非常重要。

AI 工作天然会产生大量尚不知道最终身份的中间物。

因此不应该要求 Person
每产生一个文件，就立即决定它究竟属于永久资产、文档、代码还是任务成果。

可以允许：

``` text
                  work/
                    │
              真实工作 / 探索
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      src/         doc/       tasks/
   成熟工具      成熟认知      正式成果
        │           │           │
        └───────────┼───────────┘
                    ↓
               Person 能力增长
```

必要时，成熟成果还可以进一步成为 Castle Assets。

------------------------------------------------------------------------

## 8. Reboot Test 才是真正的设计方法

不应该一开始就设计一个庞大的 Reboot Framework。

更可靠的方法是：

### 第一步：让 Person 真实工作

例如先建立 `acqplanner`，让它真正完成慢充 Acquisition Planning。

### 第二步：保存自然产生的持久内容

包括：

-   Project Context；
-   已形成的 `src`；
-   Task；
-   必要 Trace；
-   必要 Chat；
-   它所依赖的 Castle Assets。

### 第三步：制造真正的"失忆"

关闭旧 Work。

建立一个完全 Fresh 的 Codex 环境。

不给它旧会话记忆，只给它 Castle 中持久存在的内容。

### 第四步：执行 Reboot

让 Fresh Codex 进入：

``` text
people/acqplanner/
```

然后测试它是否能够：

1.  正确认出自己的身份；
2.  理解职责和边界；
3.  找到所需 Assets；
4.  理解当前任务；
5.  理解已经完成的工作；
6.  使用已有 `src`；
7.  继续产生符合职责的工作成果。

### 第五步：只补失败暴露出来的缺口

如果它不知道自己是谁：

> 补 Project Context。

如果知道自己是谁，但不知道当前任务：

> 补 Task Context。

如果知道任务，却无法理解为什么形成当前方案：

> 补必要 Trace。

如果文件都完整，但能力明显退化：

> 检查是否存在尚未物化的必要 Chat Context。

如果恢复正常：

> **不要继续加结构。**

------------------------------------------------------------------------

## 9. Person 成熟度的一个重要指标

Reboot 提供了一个非常有价值的能力成熟度判断：

> **这个 Person 有多少能力已经真正成为持久资产，而不是仍然泡在某一次
> Chat / Work 中？**

可以做一个很直接的实验：

``` text
完整历史 Chat
      ↓
逐渐减少
      ↓
Project Context + src + Task/Trace + Assets
      ↓
观察还能恢复多少能力
```

如果删除历史 Chat 后能力严重下降：

> 说明大量能力仍然存在于会话中，尚未充分物化。

如果删除大部分 Chat 后仍然可以稳定工作：

> 说明这个 Person 已经形成了较成熟、可迁移、可持续的工作能力。

因此，成熟 Person 的理想方向是：

``` text
Project Context     必须
src                 必须
Current Task        当前工作必须
Trace               按需
Chat                恢复保险，依赖逐渐降低
```

------------------------------------------------------------------------

## 10. M_Reborn 带来的启示

M_Reborn（mr）的价值让 Reboot 问题变得非常具体。

如果 mr 当前表现出了很强的 Acquisition Analysis / 审计 /
主动探索能力，但这些能力只能存在于某一个偶然形成的 Work 或长期 Chat
中，那么它仍然属于：

> **野生能力。**

真正的 Castle Asset 化应该达到：

``` text
mr 当前表现出的能力
        ↓
识别真正有价值的能力
        ↓
沉淀为 Person 的持久 Context / src / doc / 工作方法
        ↓
Fresh Agent
        ↓
self-reboot
        ↓
再次表现出相近的有效工作能力
```

到这个阶段，能力才真正从：

> "某一次 AI 会话很牛"

转变为：

> **"Castle 拥有这种能力。"**

------------------------------------------------------------------------

## 11. Reboot 的最终目标：能力可遗传

因此，Reboot 最终并不是一个传统意义上的：

-   备份系统；
-   会话恢复系统；
-   Agent 状态复制系统；
-   灾难恢复系统。

它真正想解决的是：

> **AI Person
> 的能力如何脱离一次性的运行现场，成为可持续、可迁移、可恢复的 Castle
> 能力。**

可以把它概括成一句话：

> **保存的不是 AI 昨天坐过的椅子，而是让明天坐下来的人还能把活干对。**

或者更进一步：

> **Reboot 是 Castle 中 AI 能力的可遗传性。**

------------------------------------------------------------------------

## 12. 当前原则

Castle 0.1 对 Reboot 暂时只坚持以下原则：

1.  Person 不应依赖单一机器、单一 Work 或单一历史会话才能存在。
2.  Reboot 恢复的是工作能力，不是旧运行现场。
3.  优先采用 self-reboot，而不是建设中央 Reboot 管理者。
4.  Project Context、`src`、Task / Trace Context、必要 Chat Context 和
    Castle Assets 是当前候选恢复基础。
5.  Chat 是保险层，不是最终知识库。
6.  Person 应通过真实工作不断把隐性能力物化。
7.  Reboot 的完整性必须通过 Fresh Agent 实测，而不是通过架构想象证明。
8.  Reboot 失败时，只补真实暴露出来的缺口。
9.  不提前建设复杂的
    Registry、Schema、状态机、Gate、生命周期或中央治理体系。
10. Reboot 的最终目标，是让重要 AI 能力真正成为 Castle
    可以持续拥有的能力。
