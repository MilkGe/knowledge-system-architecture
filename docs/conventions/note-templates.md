# 笔记模板约定

每种笔记类型有建议的内容结构。模板定义了起点，不限制终点——一篇写好的笔记永远可以超越模板。

## Inbox 笔记模板

采集内容写入 Inbox 时的基本结构。

```yaml
---
collected_at: {{date:YYYY-MM-DD HH:mm}}
collected_by: jarvis
source_url: ""
source_platform: ""
source_author: ""
content_type: ""
---

# {{title}}

## 原始内容

（采集到的原文或转录文本）

## 结构化要点

（核心观点、内容梳理、关键数据等结构化整理）
```

Inbox 笔记不设 type 和 status 字段。分类处理时由 classifier 分配 type 和 status。处理后转入对应 PARA 目录，Inbox 中的原始文件按养料消耗模型处理。

## Project 笔记模板

轻量进度板，不写深度知识内容。

```yaml
---
title: "{{title}}"
type: project-note
status: active
created: {{date}}
updated: {{date}}
tags: []
area: ""
deadline:
---

# {{title}}

## Overview

项目背景和目的（2-3 句）。

## Goal

明确的可交付成果。

## Tasks

- [ ] 任务 1
- [ ] 任务 2

## Log

### YYYY-MM-DD
- 做了什么
