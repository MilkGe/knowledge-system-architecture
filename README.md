# Knowledge System Architecture

一个面向 AI 协作的个人知识系统参考设计。

## 这是什么

这是一个可运行的知识系统设计蓝本，不是一套 "clone 即用" 的 Obsidian 模板。

它公开了我个人知识系统的三层架构设计、AI 协作协议、采集管线配置和全部规范规则——任何技术用户都可以参考这套设计，借助 AI 搭建自己的知识系统。

## 系统哲学

这个系统基于三个核心判断：

**知识系统的本质问题是三个**：信息怎么进入（采集）、知识单元怎么稳定存在（结构）、认知怎么逐渐成熟（演化）。一个层解决一个问题，不多不少。

**AI 的介入不是为了自动化一切**，而是在确定的权限边界内辅助。AI 知道什么可以自主做（Tier 3）、什么需要告知用户（Tier 2）、什么必须确认（Tier 1）。

**笔记应该是消耗品，也是自己的认知成果**。外源采集的信息是基础养料，加工后不保留原始文件。笔记要读起来像自己写的，不是来源索引。

## 仓库结构

```
docs/                   文档 —— 架构、协作协议、规则
├── architecture/       三层架构设计文档
├── collaboration/      AI 协作协议
└── conventions/        命名规则、YAML 规范、模板约定

pipeline/               采集管线 —— 可独立运行的代码
├── receive_url.py      URL → 元数据 → 转录 → 结构化输出的调度器
├── transcribe_sensevoice.py  SenseVoice 中文转录引擎封装
├── requirements.txt    管线核心依赖
├── .env.example        环境变量模板
└── media-crawler-setup.md  MediaCrawler 可选集成指南
```

## 快速导航

| 如果你 | 从这里开始 |
|-------|-----------|
| 想理解整体架构设计 | `docs/architecture/overview.md` |
| 想了解采集管线怎么工作 | `docs/architecture/layer-1-capture.md` |
| 想看 AI 协作的权限设计 | `docs/collaboration/tier-boundary.md` |
| 想直接用管线代码 | `pipeline/README.md` |
| 想了解命名和 YAML 规范 | `docs/conventions/naming.md` |

## 使用方式

这个仓库的核心交付物是**文档和参考代码**。

如果你是自己搭建知识系统：

1. 读 `docs/architecture/overview.md` 理解整体设计
2. 按自己需求实现 vault 结构
3. 参考 `docs/collaboration/` 配置 AI 协作协议
4. 如需自动采集管线，参考 `pipeline/README.md` 搭建

如果你只关心设计方法：

1. 读 `docs/architecture/` 全部
2. 读 `docs/architecture/design-decisions.md` 了解关键设计取舍

## 前置知识

- **Obsidian**：个人知识库载体，本文档假设你对其操作有基本了解
- **PARA 方法**：由 Tiago Forte 提出的项目管理方法——本文档假设你了解 Projects/Areas/Resources/Archive 四分类的基本概念
- **Python**：采集管线需要 Python 3.11+ 环境
- **ffmpeg**：音频处理工具，采集管线依赖

## 许可证

MIT © 2026
