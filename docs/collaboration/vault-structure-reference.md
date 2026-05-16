# Vault 结构参考

知识系统的目录结构设计参考。不要求完全照搬 —— 但各层的功能分界和目录逻辑可以参考。

## 顶层目录结构

```
00-Inbox/        采集层产出，所有新内容先进这里
01-Projects/     有具体目标和截止日期的项目
02-Areas/        需长期维护的知识领域
03-Resources/    可反复查阅的参考资料
04-Archive/      已完成/过期的项目、知识
05-Templates/    笔记模板
06-Attachments/  附件（图片、PDF 等）
07-Daily/        日记、日常记录
```

## PARA 四分类详解

### 00-Inbox

所有外部内容首先进入 Inbox。不做分类、标签、深度加工。Inbox 是消耗品的暂存区，不是永久存储。

**需要什么**：Inbox 本身就是一个文件夹，不需要插件。但借助 Dataview 可以快速查看积压数量和来源统计。

### 01-Projects

Project 是有具体目标和截止日期的工作项。每个项目有一个索引笔记（置于项目文件夹顶层），记录 Overview、Goal、Tasks 和 Log。

**注意事项**：Project 笔记不承载深度知识内容。深度内容放在 Resources 或 Areas 中，Project 通过 wikilink 引用它 们。

**可能需要**：Dataview（显示项目进度）、Calendar（关联时间线）

### 02-Areas

Area 是需要长期维护的知识领域。每个 Area 有一个索引笔记，汇总该领域下的资源。

**典型使用**：一个领域一篇索引笔记，下属内容按子主题组织为独立笔记。不按时间线归档。

### 03-Resources

Resource 是参考资料和文献笔记。按主题组织，内容可以是外部资料的摘要、文献综述、调研报告。

**与 Areas 的区别**：Areas 是"我懂的东西"，Resources 是"我参考的东西"。

### 04-Archive

已完成的项目、不再活跃的笔记。归档前做一次知识提取——行动日志→Archive，知识收获→Areas/Resources。

## 辅助目录

### 05-Templates

笔记模板。每条模板定义一篇笔记的初始 YAML 结构和正文框架。

**可能需要**：Templater 插件（自动填充日期和标题）

### 06-Attachments

图片、PDF 等二进制附件。

### 07-Daily

日记、日常记录。按日期组织。

**可能需要**：Calendar 插件（日历视图跳转日期）、Daily Notes 核心插件

## 隐式目录：系统配置

以下目录不直接出现在 PARA 结构中，但存在于 vault 根目录，用于 AI 协作配置：

| 文件/目录 | 作用 |
|-----------|------|
| `CLAUDE.md` | AI 入口文件，定义系统是什么、核心约定、文件索引 |
| `AGENTS.md` | AI 代理操作协议 |
| `.claude/agents/` | 各 AI 代理的定义文件 |
| `.claude/system/` | 系统架构和策略文档 |
| `.claude/skills/` | AI 技能定义 |

这些文件和目录的命名取决于你使用的 AI 平台。原理通用：**让 AI 在启动时读取一份系统定义，了解自己在什么样的知识体系中工作**。

## 需要哪些 Obsidian 插件

| 插件 | 用途 | 必要性 |
|------|------|--------|
| Dataview | Inbox 统计、Dashboard 查询、项目状态追踪 | 强烈推荐 |
| Templater | 模板填充、动态日期和标题 | 推荐 |
| Calendar | 日记视图、时间线导航 | 推荐 |
| Advanced Canvas | 思维导图和架构图 | 可选 |
| Excalidraw 或 Drawing | 白板绘图 | 可选 |
| Obsidian Git | 自动备份到 Git | 可选 |

其余插件按实际需求安装。系统设计本身不依赖任何第三方插件——Dataview 和 Templater 是提升体验的，不是必需的。
