#!/usr/bin/env python3
"""
receive_url.py — 多平台 URL 采集包装器

接收 URL → 爬取元数据 → 下载音频 → SenseVoice 转录 → 输出 JSON

用法:
    python receive_url.py <url> [选项]
    stdout 输出 JSON，可被其他工具消费

支持的平台:
    B站 bilibili.com
    抖音 douyin.com / v.douyin.com
    小红书 xiaohongshu.com
    微博 weibo.com
    知乎 zhihu.com
    贴吧 tieba.baidu.com

依赖:
    - httpx, yt-dlp (必须)
    - SenseVoice + funasr (转录, 可选)
    - ffmpeg (音频处理, 必须)
    - MediaCrawler (增强采集, 可选 — 通过 MC_PATH 环境变量指定)
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# --- 路径配置 ---
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
VIDEO_DIR = DATA_DIR / "video"
TRANSCRIPT_DIR = DATA_DIR / "transcript"
SEGMENTS_DIR = DATA_DIR / "segments"

# MediaCrawler 路径（可选），通过环境变量 MC_PATH 指定
MC_PATH = os.environ.get("MC_PATH", "")
if MC_PATH:
    MC_PATH = str(Path(MC_PATH).resolve())

# Python 解释器
VENV_PYTHON = os.environ.get("PIPELINE_PYTHON", sys.executable)


def _cache_path(base_dir: Path, platform: str, cache_key: str, ext: str) -> Path:
    """生成带平台前缀的缓存文件路径"""
    return base_dir / f"{platform}_{cache_key}{ext}"


# 强制 stdout 用 utf-8（Windows GBK 吞 emoji 和生僻字）
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- 平台检测 ---
PLATFORM_PATTERNS = [
    ("bilibili", r"bilibili\.com/video/(?:av)?([A-Za-z0-9]+)", "bili"),
    ("douyin", r"(?:douyin\.com/video/(\d+)|douyin\.com/.*?modal_id=(\d+)|v\.douyin\.com/(\w+))", "dy"),
    ("xiaohongshu", r"xiaohongshu\.com/(?:explore|discovery/item)/([a-zA-Z0-9]+)", "xhs"),
    ("weibo", r"weibo\.(?:com|cn)/", "wb"),
    ("zhihu", r"zhihu\.com/(?:question|answer|p|pin)/", "zhihu"),
    ("tieba", r"tieba\.baidu\.com/", "tieba"),
]

PLATFORM_NAMES = {
    "bili": "B站", "dy": "抖音", "xhs": "小红书",
    "wb": "微博", "zhihu": "知乎", "tieba": "贴吧",
}

DATA_DIR_MAP = {
    "bili": "bili", "dy": "douyin", "xhs": "xhs",
    "wb": "weibo", "zhihu": "zhihu", "tieba": "tieba",
}

CST = timezone(timedelta(hours=8))
LOGIN_REQUIRED = {"dy", "xhs", "wb", "zhihu", "tieba"}


def detect_platform(url: str) -> Optional[tuple[str, str]]:
    for _, pat, pid in PLATFORM_PATTERNS:
        m = re.search(pat, url, re.IGNORECASE)
        if m:
            return pid, next((g for g in m.groups() if g is not None), url)
    return None, None


def _has_mc() -> bool:
    """检查 MediaCrawler 是否可用"""
    if not MC_PATH:
        return False
    mc_main = Path(MC_PATH) / "main.py"
    return mc_main.exists()


def run_crawler(platform_id: str, url: str, headless: bool = True) -> Optional[subprocess.CompletedProcess]:
    """通过 MediaCrawler 采集（若可用）"""
    if not _has_mc():
        return None

    mc_dir = Path(MC_PATH)
    mc_python = mc_dir / ".venv" / "Scripts" / "python.exe"
    if not mc_python.exists():
        mc_python = Path(VENV_PYTHON)

    cmd = [
        str(mc_python), "main.py",
        "--platform", platform_id,
        "--type", "detail",
        "--lt", "cookie",
        "--specified_id", url,
        "--save_data_option", "jsonl",
        "--max_concurrency_num", "1",
        "--get_comment", "false",
        "--headless", str(headless).lower(),
    ]
    print(f"[receive_url] {' '.join(cmd)}", file=sys.stderr)
    return subprocess.run(
        cmd, cwd=str(mc_dir), capture_output=True, text=True,
        timeout=300, encoding="utf-8",
        env={**os.environ, "PLAYWRIGHT_CHROMIUM_HEADLESS": "1" if headless else "0"},
    )


def find_output(platform: str, url: str) -> Optional[dict]:
    """从 MediaCrawler 输出目录查找结果"""
    if not MC_PATH:
        return None
    dir_name = DATA_DIR_MAP.get(platform, platform)
    data_dir = Path(MC_PATH) / "data" / dir_name / "jsonl"
    if not data_dir.exists():
        return None
    content_files = sorted(data_dir.glob("detail_contents_*.jsonl"), reverse=True)
    if not content_files:
        return None
    for f in content_files:
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                item = json.loads(line)
                item_url = item.get("note_url") or item.get("aweme_url") or item.get("video_url") or ""
                if item_url and url in item_url:
                    return item
    with open(content_files[0], "r", encoding="utf-8") as fh:
        last = None
        for line in fh:
            if line.strip():
                last = json.loads(line)
        return last


def fmt_ts(ts):
    if not ts:
        return ""
    try:
        ts = float(ts)
        if ts > 1e12:
            ts /= 1000
        return datetime.fromtimestamp(ts, tz=CST).isoformat()
    except Exception:
        return str(ts)


def get_audio_url(item: dict) -> Optional[str]:
    audio = item.get("music_download_url")
    if audio and audio.startswith("http"):
        return audio
    return None


def get_video_url(item: dict) -> Optional[str]:
    return item.get("video_url") or item.get("video_download_url") or None


def download_audio(url: str, cache_key: str, platform: str = "") -> Optional[Path]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".mp3" if ".mp3" in url else ".mp4" if ".mp4" in url else ".bin"
    out = _cache_path(AUDIO_DIR, platform, cache_key, ext)
    if out.exists() and out.stat().st_size > 1000:
        print(f"[receive_url] 音频已缓存: {out}", file=sys.stderr)
        return out

    print(f"[receive_url] 📥 下载音频...", file=sys.stderr)
    r = subprocess.run(
        ["curl", "-L", "-o", str(out), "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 100:
        print(f"[receive_url] ⚠️ 下载失败", file=sys.stderr)
        return None
    print(f"[receive_url] 已下载 {out.stat().st_size/1024:.0f}KB", file=sys.stderr)
    return out


def download_video(url: str, cache_key: str, platform: str = "") -> Optional[Path]:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".mp4" if ".mp4" in url else ".bin"
    out = _cache_path(VIDEO_DIR, platform, cache_key, ext)
    if out.exists() and out.stat().st_size > 1000:
        print(f"[receive_url] 视频已缓存: {out}", file=sys.stderr)
        return out

    print(f"[receive_url] 📥 下载视频...", file=sys.stderr)
    r = subprocess.run(
        ["curl", "-L", "-o", str(out), "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 100:
        print(f"[receive_url] ⚠️ 下载失败", file=sys.stderr)
        return None
    print(f"[receive_url] 已下载 {out.stat().st_size/1024:.0f}KB", file=sys.stderr)
    return out


def download_bili_audio(url: str, cache_key: str, platform: str = "") -> Optional[Path]:
    """用 yt-dlp 下载 B 站音频并提取为 mp3"""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out = _cache_path(AUDIO_DIR, platform, cache_key, ".mp3")
    if out.exists() and out.stat().st_size > 1000:
        print(f"[receive_url] 音频已缓存: {out}", file=sys.stderr)
        return out

    print(f"[receive_url] 📥 yt-dlp 下载 B站音频...", file=sys.stderr)
    r = subprocess.run(
        [VENV_PYTHON, "-m", "yt_dlp", "-x", "--audio-format", "mp3",
         "-o", str(_cache_path(AUDIO_DIR, platform, cache_key, ".%(ext)s")),
         "--no-update", url],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 100:
        err = r.stderr.strip()[-300:] if r.stderr else ""
        print(f"[receive_url] ⚠️ yt-dlp 失败: {err}", file=sys.stderr)
        return None
    print(f"[receive_url] 已下载 {out.stat().st_size/1024:.0f}KB", file=sys.stderr)
    return out


def extract_audio_from_video(video_path: Path, cache_key: str, platform: str = "") -> Optional[Path]:
    """用 ffmpeg 从视频中提取音频"""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out = _cache_path(AUDIO_DIR, platform, cache_key, ".mp3")
    if out.exists() and out.stat().st_size > 1000:
        return out
    print(f"[receive_url] 🎬 提取音频...", file=sys.stderr)
    r = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", "-q:a", "4", str(out), "-y"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0 or not out.exists():
        print(f"[receive_url] ⚠️ ffmpeg 提取失败", file=sys.stderr)
        return None
    return out


def transcribe_sensevoice(audio_path: Path) -> Optional[tuple[str, dict]]:
    """用本地 transcribe_sensevoice.py 转录"""
    sv_script = PROJECT_DIR / "transcribe_sensevoice.py"
    if not sv_script.exists():
        print(f"[receive_url] ⚠️ 未找到 transcribe_sensevoice.py", file=sys.stderr)
        return None

    print(f"[receive_url] 🎙️ SenseVoice 转录中...", file=sys.stderr)
    t0 = time.time()

    r = subprocess.run(
        [VENV_PYTHON, str(sv_script), str(audio_path)],
        cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=600,
    )
    elapsed = time.time() - t0

    if r.returncode != 0 or not r.stdout.strip():
        err = r.stderr.strip()[-300:] if r.stderr else "no output"
        print(f"[receive_url] ⚠️ 转录失败: {err}", file=sys.stderr)
        return None

    transcript = r.stdout.strip()
    print(f"[receive_url] SenseVoice 完成 | {elapsed:.1f}s", file=sys.stderr)
    return transcript, {"model": "SenseVoiceSmall", "elapsed": elapsed}


def build_output(item: dict, platform_id: str, url: str,
                 transcript: Optional[str] = None,
                 transcript_meta: Optional[dict] = None) -> dict:
    """组装最终 JSON 输出"""
    tags_raw = item.get("tag_list") or ""
    if isinstance(tags_raw, str):
        tags = [t.strip().replace("#", "") for t in tags_raw.split(",") if t.strip()]
    else:
        tags = list(tags_raw) if tags_raw else []

    is_douyin_image_post = platform_id == "dy" and str(item.get("aweme_type", "")) == "68"
    note_images_raw = item.get("note_download_url") or ""
    note_images = [u.strip() for u in note_images_raw.split(",") if u.strip()] if note_images_raw else []

    out = {
        "platform": platform_id,
        "platform_name": PLATFORM_NAMES.get(platform_id, platform_id),
        "source_url": url,
        "title": item.get("title") or item.get("desc", "")[:60] or "无标题",
        "desc": item.get("desc") or "",
        "author": item.get("nickname") or "",
        "author_id": item.get("user_id") or "",
        "created_time": fmt_ts(item.get("create_time") or item.get("time")),
        "stats": {
            "likes": item.get("liked_count") or "0",
            "collects": item.get("collected_count", item.get("video_favorite_count")) or "0",
            "comments": item.get("comment_count", item.get("video_comment")) or "0",
        },
        "cover_url": item.get("video_cover_url") or item.get("cover_url") or item.get("image_list") or "",
        "content_type": "图文" if is_douyin_image_post else (
            "video" if (item.get("video_url") or item.get("video_download_url") or item.get("music_download_url")) else "图文"
        ),
        "tags": tags,
    }

    if note_images:
        out["images"] = note_images

    audio_url = get_audio_url(item)
    video_url = get_video_url(item)

    if transcript:
        out["transcript"] = transcript
        out["transcript_model"] = transcript_meta.get("model", "") if transcript_meta else ""
        out["transcribed"] = True
    elif audio_url or video_url:
        out["needs_transcription"] = True
        if audio_url:
            out["audio_url"] = audio_url
        if video_url:
            out["video_url"] = video_url

    return out


def main():
    import argparse
    parser = argparse.ArgumentParser(description="URL → 结构化 JSON")
    parser.add_argument("url", help="要采集的 URL")
    parser.add_argument("--no-headless", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--no-transcribe", action="store_true", help="跳过转录，仅返回元数据")
    parser.add_argument("--mc-path", help="MediaCrawler 目录路径（覆盖 MC_PATH 环境变量）")
    args = parser.parse_args()

    # 环境变量覆盖
    global MC_PATH
    if args.mc_path:
        MC_PATH = str(Path(args.mc_path).resolve())

    platform_id, _ = detect_platform(args.url)
    if not platform_id:
        print(json.dumps({"error": "unrecognized_platform", "url": args.url}, ensure_ascii=False))
        sys.exit(1)

    name = PLATFORM_NAMES.get(platform_id, platform_id)
    print(f"[receive_url] 🔍 {name} {args.url}", file=sys.stderr)

    item = None

    if _has_mc():
        headless = not args.no_headless
        result = run_crawler(platform_id, args.url, headless=headless)

        if result and result.returncode == 0:
            item = find_output(platform_id, args.url)

        # 登录态检测
        if result:
            combined = result.stdout + result.stderr
            login_failed = platform_id in LOGIN_REQUIRED and (
                "Login state result: False" in combined
                or "账号未登录" in combined or "cookie失效" in combined
            )
            if login_failed:
                print(f"[receive_url] ⚠️ {name} 登录态无效", file=sys.stderr)
                print(json.dumps({
                    "login_required": True,
                    "platform": platform_id,
                    "platform_name": name,
                    "source_url": args.url,
                    "message": f"{name} 登录已过期，请重新扫码登录后再试",
                }, ensure_ascii=False))
                sys.exit(0)

        if not item and platform_id in LOGIN_REQUIRED:
            print(json.dumps({
                "login_required": True,
                "platform": platform_id,
                "platform_name": name,
                "source_url": args.url,
                "message": f"{name} 可能登录已过期（无有效输出），请重新扫码登录",
            }, ensure_ascii=False))
            sys.exit(0)

    if not item:
        print(json.dumps({
            "error": "no_output",
            "message": "无法获取内容。如果已安装 MediaCrawler，请设置 MC_PATH 环境变量或使用 --mc-path 指定路径。",
            "platform": platform_id,
            "source_url": args.url,
        }, ensure_ascii=False))
        sys.exit(1)

    # --- 转录 ---
    transcript = None
    transcript_meta = None

    is_douyin_image_post = platform_id == "dy" and str(item.get("aweme_type", "")) == "68"
    skip_transcribe = is_douyin_image_post

    if not args.no_transcribe and not skip_transcribe:
        audio_url = get_audio_url(item)
        video_url = get_video_url(item) if not audio_url else None
        content_hash = hashlib.md5((audio_url or video_url or args.url).encode()).hexdigest()[:12]

        audio_path = None

        if platform_id == "bili":
            audio_path = download_bili_audio(args.url, content_hash, platform_id)
        elif audio_url:
            audio_path = download_audio(audio_url, content_hash, platform_id)
        elif video_url:
            video_path = download_video(video_url, content_hash, platform_id)
            if video_path:
                audio_path = extract_audio_from_video(video_path, content_hash, platform_id)

        if audio_path:
            tx = transcribe_sensevoice(audio_path)
            if tx:
                transcript, transcript_meta = tx

        if transcript:
            TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
            tpath = _cache_path(TRANSCRIPT_DIR, platform_id, content_hash, ".txt")
            tpath.write_text(transcript, encoding="utf-8")
            print(f"[receive_url] 转录已保存: {tpath}", file=sys.stderr)

        seg_dir = SEGMENTS_DIR / f"_{content_hash}"
        if seg_dir.exists():
            import shutil
            shutil.rmtree(seg_dir, ignore_errors=True)

    output = build_output(item, platform_id, args.url, transcript, transcript_meta)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
