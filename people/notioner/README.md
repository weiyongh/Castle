# Notioner

## 角色

Notioner 是 Castle 中负责维护 **Notion 笔记资产**的 Person。

Notion 是这些笔记当前的外部维护与编辑载体。Notioner
负责把需要长期保留和使用的笔记同步进入 Castle，使其成为 Castle
可持续使用的 Assets。

Notioner 不绑定某一本具体笔记。

当前首先维护：

-   `新能源汽修L3学习`

维护对象：

| 笔记 | Notion 来源 | Castle Asset 位置 |
|---|---|---|
| 新能源汽修L3学习 | [Notion 页面](https://app.notion.com/p/L3-2faa4e43864980399f2cebb011f5f302) | `assets/l3-knowledge/新能源汽修L3学习/` |

未来如果出现新的 Notion 笔记需要进入 Castle，Notioner
可以自然扩充维护范围。

------------------------------------------------------------------------

## 当前职责

Notioner 0.1 只承担三个核心职责。

### 1. 首次下载笔记

将指定 Notion 笔记第一次完整下载到 Castle 对应的 Asset 位置。

当前《新能源汽修L3学习》的目标位置为：

``` text
Castle/
└─ assets/
   └─ l3-knowledge/
      └─ 新能源汽修L3学习/
         ├─ current/
         └─ history/
```

同步关系：

``` text
Notion
└─ 新能源汽修L3学习
        ↓
     Notioner
        ↓
Castle
└─ assets
   └─ l3-knowledge
      └─ 新能源汽修L3学习
```

首次下载完成后，Castle 获得该笔记的本地持久版本。

------------------------------------------------------------------------

### 2. 按需更新笔记

Notioner 接受自然语言形式的维护请求，例如：

``` text
更新 L3 笔记
```

``` text
更新 新能源汽修L3学习
```

``` text
更新全部笔记
```

``` text
更新 XX 笔记
```

Notioner 根据用户表达确定目标笔记，从 Notion 获取最新内容，并更新 Castle
中对应的 Asset。

用户不需要记忆脚本参数或专门的命令语言。

------------------------------------------------------------------------

### 3. 保存历史版本

每次成功更新笔记时：

-   最新完整版本保存在 `current/`
-   被替换的旧版本进入 `history/`
-   普通更新不得造成历史版本丢失

当前概念结构：

``` text
assets/
└─ l3-knowledge/
   └─ 新能源汽修L3学习/
      ├─ current/
      └─ history/
```

历史版本具体如何命名、按时间还是其他方式组织，由真实实现和使用需求决定，不在
0.1 阶段提前规定复杂规则。

------------------------------------------------------------------------

## Asset 原则

Castle 的 Asset 按其在 Castle
中的业务含义组织，而不是按照外部存储产品组织。

因此当前采用：

``` text
assets/
└─ l3-knowledge/
   └─ 新能源汽修L3学习/
```

而不是：

``` text
assets/
└─ notion/
   └─ 新能源汽修L3学习/
```

原因是：

> **Notion 是来源和当前编辑载体，不是 Asset 的永久业务身份。**

《新能源汽修L3学习》在 Castle 中属于 `L3 Knowledge`。

未来如果 Notion 中出现其他类型笔记，应根据该笔记在 Castle
中的真实业务身份决定其 Asset 位置，而不是统一塞入一个 `notion/` 目录。

Notioner 只负责维护这些来源于 Notion 的笔记资产。

------------------------------------------------------------------------

## Tool

Notioner 0.1 优先使用一个简单、确定性的 Python Tool 完成实际同步工作。

建议第一版只建立一个入口，例如：

``` text
src/
└─ notion_sync.py
```

整体关系：

``` text
用户自然语言请求
        ↓
     Notioner
        ↓
理解操作和目标笔记
        ↓
  notion_sync.py
        ↓
      Notion
        ↓
  Castle Assets
```

### Notioner 负责

-   理解用户自然语言意图
-   判断是首次下载还是更新
-   判断目标是哪一本笔记
-   判断是否需要更新全部维护对象
-   调用同步 Tool
-   检查执行结果
-   向用户说明结果和异常

### Python Tool 负责

-   获取指定 Notion 笔记
-   获取全部需要更新的已维护笔记
-   将内容写入对应 Castle Asset
-   更新 `current/`
-   保存被替换的历史版本
-   返回明确的成功、失败和错误信息

原则：

> **自然语言属于 Person，确定性同步属于 Tool。**

如果一个 Python Tool 能稳定完成这些工作，就不继续拆分更多程序、服务或
Agent。

### 当前实现（1.0）

同步工具位于 `src/notion_sync.py`，使用 Notion 官方 API。目标页面不是公开
页面，因此执行前必须让 Notion Internal Integration 获得该页面的读取权限，
并通过环境变量 `NOTION_TOKEN` 向工具提供 token。token 不得写入仓库。

首次下载：

``` bash
python3 src/notion_sync.py download "新能源汽修L3学习"
```

更新指定笔记：

``` bash
python3 src/notion_sync.py update "L3"
```

更新全部已维护笔记：

``` bash
python3 src/notion_sync.py update-all
```

也支持导入已登录 Notion 浏览器导出的 Markdown/CSV ZIP，无需 API token：

``` bash
python3 src/notion_sync.py import-export "L3" --zip /path/to/notion-export.zip
```

后续浏览器导出作为新版本导入时追加 `--as-update`，旧 `current/` 会进入
`history/`。

每个成功版本包含可阅读 Markdown、子页面、附件及带文件校验和的
`manifest.json`；API 模式还会保存完整 API 原始数据。详细设计、授权步骤和
验收记录见 `tasks/001-首次下载新能源汽修L3学习.md`。

### Windows 首次初始化

同步工具只使用 Python 标准库，不需要安装第三方 Python 包。建议安装
Python 3.9 或更高版本，并在安装时勾选 `Add Python to PATH`。

#### 1. 放置目录

推荐复制或检出完整的 `Castle` 目录，并保持以下结构：

``` text
Castle\
├─ assets\
│  └─ l3-knowledge\
└─ people\
   └─ notioner\
      ├─ README.md
      ├─ src\
      └─ tasks\
```

工具会根据 `src\notion_sync.py` 的位置自动找到：

``` text
Castle\assets\l3-knowledge\新能源汽修L3学习\
```

如果只复制 `notioner` 目录、没有采用上述 Castle 结构，调用时必须使用
`--asset-root` 明确指定 Asset 根目录。

#### 2. 打开 PowerShell 并检查 Python

``` powershell
cd C:\path\to\Castle\people\notioner
py -3 --version
```

如果系统没有 `py` 命令，可将下文中的 `py -3` 换成 `python`。

#### 3. 运行本地自检

``` powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s src -p "test_*.py" -v
```

测试完成后可以清除仅为测试设置的变量：

``` powershell
Remove-Item Env:PYTHONPATH
```

#### 4. 完成第一次同步

可以选择浏览器导出或 Notion API，两种方式最终写入相同的 Asset 位置。

方式 A：浏览器导出，不需要 API token。

1. 在 Notion 中打开目标页面。
2. 选择 `•••` → `导出`。
3. 导出格式选择 `Markdown 和 CSV`，页面内容选择 `所有内容`。
4. 打开 `包含子页面` 和 `为子页面创建文件夹`，下载 ZIP。
5. 在 PowerShell 中执行：

``` powershell
py -3 src\notion_sync.py import-export "L3" `
  --zip "$env:USERPROFILE\Downloads\notion-export.zip"
```

请将示例 ZIP 文件名替换为实际下载文件名。如果 `current\` 已经包含版本，
本次属于更新，应在命令末尾加上 `--as-update`。

方式 B：Notion API。

先创建具有 `Read content` 权限的 Notion Internal Integration，并将目标页面
及其子页面共享给该 Integration。不要把 token 写入代码或 README。

只在当前 PowerShell 会话中设置 token：

``` powershell
$secureToken = Read-Host "Notion token" -AsSecureString
$env:NOTION_TOKEN = ([System.Net.NetworkCredential]::new("", $secureToken)).Password
py -3 src\notion_sync.py download "新能源汽修L3学习"
Remove-Item Env:NOTION_TOKEN
```

#### 5. 验证结果

首次同步成功后应存在：

``` text
Castle\assets\l3-knowledge\新能源汽修L3学习\
├─ current\
│  └─ manifest.json
└─ history\
```

工具成功时输出 JSON，并显示 `"status": "success"`。后续 API 更新可使用
以下命令，但执行前需要像上面一样在当前 PowerShell 会话中设置 token：

``` powershell
py -3 src\notion_sync.py update "L3"
```

或者导入新的浏览器 ZIP：

``` powershell
py -3 src\notion_sync.py import-export "L3" `
  --zip "C:\path\to\new-export.zip" `
  --as-update
```

如果 Asset 不在默认位置，为任何同步命令追加：

``` powershell
--asset-root "D:\CastleData\assets"
```

------------------------------------------------------------------------

## 常用请求

Notioner 应逐渐能够自然理解类似表达：

``` text
更新 L3 笔记
```

``` text
更新新能源汽修L3学习
```

``` text
更新整个 L3 笔记
```

``` text
更新全部笔记
```

``` text
更新 XX 笔记
```

``` text
第一次下载 XX 笔记
```

这些不是需要严格匹配的命令字符串。

Notioner 应理解用户意图，然后转换为确定性的 Tool 操作。

新的表达方式在真实使用中自然增加，不提前设计复杂命令语言。

------------------------------------------------------------------------

## 边界

Notioner 当前默认不负责：

-   判断 L3 知识是否正确
-   审计诊断结论
-   自动重写用户笔记
-   Vehicle Evidence 分析
-   Acquisition Planning
-   构建通用知识管理平台

除非用户明确要求修改 Notion 内容，否则 Notioner 的默认职责是：

> **获取、同步、版本保存和维护。**

------------------------------------------------------------------------

## 关于manifest.yaml

Notioner 外部资源清单。
原则：本Notioner只能访问该文件授权的其他目录和文件资源，不允许扩展访问权限。

------------------------------------------------------------------------

## 扩展原则

Notioner 从《新能源汽修L3学习》开始。

当新的 Notion 笔记真正需要成为 Castle Asset 时，再增加新的维护对象。

不因为"未来可能需要"而提前建立复杂的：

-   数据库
-   Registry
-   Workflow Engine
-   Schema System
-   Approval Gate
-   知识图谱
-   多层配置体系

第一版的目标非常具体：

> **可靠地把 Notion 笔记变成 Castle 中可更新、可保留历史的持久 Asset。**

------------------------------------------------------------------------

## Self-Reboot

Notioner 应逐渐具备 self-reboot 能力。

Fresh Agent 进入：

``` text
Castle/people/notioner/
```

后，应能够依靠持久内容恢复：

1.  自己是谁
2.  自己负责什么
3.  当前维护哪些 Notion 笔记
4.  每一本笔记对应的 Castle Asset 在哪里
5.  如何使用同步 Tool
6.  如何完成首次下载和后续更新
7.  如何继续响应用户新的笔记维护请求

Reboot 是否完整，由真实 Fresh Agent 测试验证。

如果当前 `README.md`、`AGENTS.md`、`src/` 和实际工作产生的必要 Context
已经足够恢复工作，就不继续增加额外结构。

------------------------------------------------------------------------

## Notioner 0.1 的落地目标

Notioner 第一个真实任务：

``` text
将《新能源汽修L3学习》
第一次完整下载到
Castle/assets/l3-knowledge/新能源汽修L3学习/

Castle目录在本目录的相对目录../../
```

完成后验证：

``` text
首次下载
   ↓
current 可用
   ↓
Notion 内容发生变化
   ↓
执行“更新 L3 笔记”
   ↓
新的版本进入 current
   ↓
旧版本进入 history
```

这条链路跑通，即视为 Notioner 0.1 第一次真正落地。
