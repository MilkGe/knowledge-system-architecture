# YAML 元数据规范

每篇笔记的 YAML frontmatter 是知识系统结构化的核心载体。

## 最小必填字段

```yaml
type: [inbox | project-note | area-note | resource | daily]
status: [raw | seed | developed | stable | archived]
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

## 可选情境字段

```yaml
source: "来源 URL"
tags: [标签1, 标签2]
project: 所属项目名
area: 所属领域名
stage: [按需使用]
```

不再增加其他字段。YAML 保持最小集。

## 采集管线产出字段

采集管线自动写入的扩展元数据。在 raw 阶段有溯源价值，笔记加工后可选择性删除：

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

**设计意图**：这些字段在采集初期有价值（让 AI 和人知道内容来源），但不应永久保留。笔记加工到 seed 或 developed 阶段后，可以考虑删除 source 类字段，让笔记读起来像自己写的。

## type 字段可选值

| 值 | 含义 | 使用位置 |
|----|------|---------|
| `inbox` | 原始采集笔记 | Inbox |
| `project-note` | 项目笔记 | Projects |
| `area-note` | 领域笔记 | Areas |
| `resource` | 资源笔记 | Resources |
| `daily` | 日记 | Daily |
| `dashboard` | 看板 | vault 根目录 |
| `system-mechanism` | 系统机制定义 | .claude/system/ |
| `system-state` | 系统状态追踪 | .claude/system/ |

## status 字段可选值

| 值 | 含义 | 行为 |
|----|------|------|
| `raw` | 原始采集，未加工 | 在 Inbox 中等待处理 |
| `seed` | 已初步处理，有潜力 | 已添加元数据、要点提炼 |
| `developed` | 已系统化整理 | 已建立关联、有个人理解 |
| `stable` | 形成稳定认知 | 已被多次引用或复用 |
| `archived` | 已归档 | 不再活跃参与关联 |

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

## 关于标签

标签是 YAML 的一个字段，但其规范独立：

- 平级结构，不建层级
- 每篇 1-3 个标签为宜
- 标签是检索工具，不是分类树
- 避免将 status 信息重复写进标签（已有 status 字段）
- 优先使用以后真正会拿来搜索的词：产品名、错误码、关键转折点
