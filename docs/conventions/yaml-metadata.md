# YAML 元数据规范

每篇笔记的 YAML frontmatter 是知识系统结构化的核心载体。以下规范反映 vault 实际运行状态。

## 标准模板

```yaml
---
title: <string>                # 笔记标题
type: resource-note             # 见 type 表
status: active                  # active / in-progress / completed / draft / archived
created: YYYY-MM-DD [HH:MM]    # 创建日期
updated: YYYY-MM-DD HH:MM      # 最后更新
source: <string>                # 来源（resource-note 必填）
description: <string>           # 一句话描述
tags:                           # 列表格式，不用内联
  - tag1
  - tag2
---
```

## type 字段可选值

| 值 | 含义 | 使用位置 |
|----|------|---------|
| `project-note` | 项目笔记 | 01-Projects/ |
| `area-note` | 领域笔记 | 02-Areas/ |
| `resource-note` | 资源笔记 | 03-Resources/ |
| `daily` | 日记 | 07-Daily/ |
| `dashboard` | 看板 | vault 根目录 |
| `archive-note` | 归档笔记 | 04-Archive/ |
| `template` | 模板 | 05-Templates/ |
| `config` | 配置文件 | vault 根目录 |
| `system-mechanism` | 系统机制定义 | .claude/system/ |
| `system-state` | 系统状态追踪 | .claude/system/ |

> Inbox 笔记（00-Inbox/）不设 type 字段，由采集管线自动写入扩展元数据，分类处理时由 classifier 分配 type。

## status 字段可选值

| 值 | 含义 | 使用场景 |
|----|------|---------|
| `active` | 活跃内容，持续更新 | resource-note、area-note |
| `in-progress` | 正在进行中 | project-note（项目进行中） |
| `completed` | 内容完整，不再更新 | 任何已完成的笔记 |
| `draft` | 刚创建，内容为框架或片段 | 任何笔记 |
| `archived` | 已归档 | 移入 04-Archive/ 的笔记 |

> status 四个含义不重叠：draft → in-progress/active → completed → archived。

## 按 type 的必填组合

| type | 额外必填 | 说明 |
|------|---------|------|
| `project-note` | `project: [子目录名]` | 与 01-Projects/ 下子目录名一致 |
| `area-note` | `area: [领域名]` | 与 02-Areas/ 下子目录名一致 |
| `resource-note` | `source: [来源]` | 来源平台或类型 |
| `daily` | 无 | 日记插件自动生成 |

## tags 格式

**使用列表格式，不用内联格式。**

```yaml
# ✅ 正确
tags:
  - 光固化树脂
  - 实验记录

# ❌ 错误
tags: [光固化树脂, 实验记录]
```

内联格式在 YAML 中容易被误解析为字符串而非数组。

## 采集管线产出字段

采集管线自动写入 Inbox 笔记的扩展元数据。在原始采集阶段有溯源价值，笔记加工后可选择性删除：

```yaml
source_url: "https://..."         # 原文链接
source_platform: "抖音"            # 中文平台名
source_author: "作者名"            # 作者/账号
collected_at: 2026-05-12T20:43:00+08:00  # ISO 8601，含时区
collected_by: "jarvis"            # 采集者
content_type: "视频"               # 内容形态：视频/图文/文章
transcribed: true                 # 是否经 ASR 转录
transcript_model: "SenseVoice-Small"  # 转录引擎
```

在笔记从 Inbox 分类移入 03-Resources/ 后，这些字段会被折叠为 `source: "<平台> @<作者>"` 单字段形式。

## 中英边界

属性名用英文，属性值用中文自然语言。

```yaml
# ✅ 正确
source_platform: "抖音"
content_type: "视频"

# ❌ 错误
来源平台: "抖音"
source_platform: "dy"
```

中文值在 Obsidian Properties 视图中可读性更好，但 Dataview 查询需要精确匹配。可读性优先于查询便利性。

## 关于 description

resource-note 应包含 `description` 字段，写一句话摘要（不超过 30 字），辅助预览和检索。

## 不再使用的字段

| 字段 | 移除原因 |
|------|---------|
| `priority` | 状态已由 status 管理，无需额外优先级标记 |
| `related` | 改为正文内 wikilink |
| `project` | 限制 project-note 专用 |
| `stage` | 未落地，废弃 |
