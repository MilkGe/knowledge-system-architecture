# MediaCrawler 可选集成指南

MediaCrawler 是知识系统采集管线的推荐后端。它提供了多平台社交媒体爬取的完整能力。

## 安装 MediaCrawler

```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler

# 创建虚拟环境（Python 3.11+）
python -m venv .venv

# 安装依赖
.venv/Scripts/pip install -r requirements.txt

# 安装 Playwright 浏览器
.venv/Scripts/playwright install chromium
```

## 配置

### 1. 数据库（可选）

MediaCrawler 支持 MySQL、MongoDB、PostgreSQL、SQLite。对于采集管线的基本使用，可以不配置数据库——管线不依赖数据库存储。

### 2. 平台 Cookie

需要为每个平台准备登录 Cookie，MediaCrawler 才能采集内容。

**抖音**：浏览器登录抖音 → 开发者工具 → Application → Cookies → 复制 Cookie 字符串
**小红书**：同上
**知乎/微博/贴吧**：同上

将 Cookie 放入 MediaCrawler 对应的 Cookie 配置目录。

### 3. 环境变量

在 MediaCrawler 目录下创建 `.env`，参考 `.env.example` 填写。

## 集成

将 MediaCrawler 目录路径设置为环境变量：

```bash
# Windows
set MC_PATH=D:\MediaCrawler

# macOS / Linux
export MC_PATH=/path/to/MediaCrawler
```

或通过命令行参数：

```bash
python receive_url.py "https://..." --mc-path /path/to/MediaCrawler
```

## 验证

```bash
python receive_url.py "https://www.bilibili.com/video/BV1GJ411x7h7"
```

如果 MediaCrawler 配置正确，会输出包含元数据和转录文本的 JSON。

## 注意事项

- 抖音、小红书等平台需要登录 Cookie 才能采集，Cookie 会过期需要定期更新
- 首次转录会自动下载 SenseVoice-Small 模型（约 200MB）
- 超长音频（>120s）会被分段转录
- 数据文件（音频/视频/转录）缓存在 `pipeline/data/` 目录
