# 采集管线 (Pipeline)

URL → 元数据 → 转录 → 结构化 JSON。

这是知识系统采集层的参考实现。支持抖音、B站、小红书、微博、知乎、贴吧，通过 MediaCrawler（可选）或独立资源下载 + SenseVoice 转录完成内容采集。

## 工作流

```
URL → 平台检测 → 元数据提取 → 音频下载 → 转录 → 结构化 JSON
```

输出 JSON 包含：标题、作者、统计数据、封面图、标签、转录文本等。可被 AI Agent 或其他工具消费用于生成结构化笔记。

## 前置依赖

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| Python 3.11+ | 运行环境 | python.org |
| ffmpeg | 音频提取 + 分段 | 包管理器 或 ffmpeg.org |
| curl | 文件下载（一般已预装） | — |

安装 ffmpeg:

```bash
# Windows (winget)
winget install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 安装依赖
.venv/Scripts/pip install -r requirements.txt

# 3. 运行（示例：B站视频）
.venv/Scripts/python receive_url.py "https://www.bilibili.com/video/BV1GJ411x7h7"

# 4. 输出为 JSON
# json 字段说明见下方
```

## JSON 输出字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `platform` | 平台 ID | `"bili"` |
| `platform_name` | 平台中文名 | `"B站"` |
| `source_url` | 原文链接 | `"https://..."` |
| `title` | 标题 | `"..."` |
| `desc` | 描述/简介 | `"..."` |
| `author` | 作者名 | `"用户名"` |
| `created_time` | 创建时间(ISO 8601) | `"2026-05-12T20:43:00+08:00"` |
| `stats` | 互动统计 | `{"likes": "100", "collects": "50", "comments": "10"}` |
| `cover_url` | 封面图链接 | `"https://..."` |
| `content_type` | 内容类型 | `"video"` / `"图文"` |
| `transcribed` | 是否已转录 | `true` |
| `transcript` | 转录文本 | `"..."` |
| `login_required` | 是否需要登录 | `true`（登录态失效时出现） |

## 转录引擎

默认使用 **SenseVoice-Small**（阿里通义），中文转录质量和速度优于 Whisper。首次运行时自动从 ModelScope 下载模型（约 200MB）。

## 可选增强：MediaCrawler

**MediaCrawler**（[GitHub](https://github.com/NanmiCoder/MediaCrawler)）是本管线的推荐采集后端。安装后可以获取更完整的元数据（标签、统计数据、评论等）和更稳定的平台兼容性。

启用方式：设置环境变量 `MC_PATH` 指向 MediaCrawler 目录。

```bash
# Windows
set MC_PATH=D:\MediaCrawler

# macOS / Linux
export MC_PATH=/path/to/MediaCrawler
```

安装和配置详见 `media-crawler-setup.md`。

## 不安装 MediaCrawler 时的限制

receive_url.py 的核心功能（元数据提取、音频下载、转录）依赖 MediaCrawler。如果未安装 MediaCrawler，脚本会输出提示并退出。

**计划**：后续版本将 fallback 到直接通过 httpx 提取元数据，让不安装 MediaCrawler 也能获得基础的元数据。
