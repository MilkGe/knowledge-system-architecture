#!/usr/bin/env python3
"""
transcribe_sensevoice.py — SenseVoice 转录工具

阿里通义 SenseVoice-Small 引擎，中文优化，比 faster-whisper 快 10-20 倍。

用法:
    python transcribe_sensevoice.py <audio_file>
    python transcribe_sensevoice.py <audio_file> --output transcript.txt

依赖:
    funasr, modelscope (自动下载 SenseVoice-Small 模型 ~200MB)
    ffmpeg (用于音频分段，仅超长音频需要)
"""

import json
import os
import re
import sys
import time
from pathlib import Path


def transcribe(audio_path: Path) -> tuple[str, dict]:
    """Run SenseVoice transcription (分段处理超长音频)"""
    cache_dir = Path.home() / ".cache" / "modelscope" / "hub"
    model_path = cache_dir / "models" / "iic" / "SenseVoiceSmall"
    if model_path.exists():
        os.environ["MODELSCOPE_CACHE"] = str(cache_dir)

    from funasr import AutoModel

    print(f"[sensevoice] 加载 SenseVoiceSmall...", file=sys.stderr)
    t0 = time.time()

    model_id = str(model_path) if model_path.exists() else "iic/SenseVoiceSmall"
    model = AutoModel(model=model_id, disable_update=True, hub="modelscope")

    model_time = time.time() - t0
    print(f"[sensevoice] 模型加载: {model_time:.1f}s", file=sys.stderr)

    # SenseVoice 对超长音频处理不稳定，分段处理（每段 60s）
    import subprocess as _sp
    duration_s = 0
    probe = _sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(audio_path)],
                    capture_output=True, text=True, timeout=10)
    if probe.returncode == 0 and probe.stdout.strip():
        duration_s = float(probe.stdout.strip())

    if duration_s > 120:
        print(f"[sensevoice] 音频 {duration_s:.0f}s 过长，分段转录...", file=sys.stderr)
        seg_dir = Path(__file__).resolve().parent / "data" / "segments" / audio_path.stem
        seg_dir.mkdir(parents=True, exist_ok=True)
        segments = []
        chunk_s = 60
        for i in range(0, int(duration_s), chunk_s):
            seg_file = seg_dir / f"seg_{i:04d}.wav"
            if not seg_file.exists():
                _sp.run(["ffmpeg", "-y", "-i", str(audio_path),
                         "-ss", str(i), "-t", str(chunk_s),
                         "-ar", "16000", "-ac", "1", str(seg_file)],
                        capture_output=True, timeout=30)
            seg_text = ""
            try:
                res = model.generate(input=str(seg_file), language="zh", use_itn=True, batch_size_s=0)
                if res and len(res) > 0:
                    seg_text = res[0].get("text", "") if isinstance(res[0], dict) else str(res[0])
                    seg_text = re.sub(r"<\|[^|]+\|>", "", seg_text).strip()
            except Exception as e:
                print(f"[sensevoice]   segment {i}s 失败: {e}", file=sys.stderr)
            if seg_text:
                segments.append(seg_text)
                print(f"[sensevoice]   segment {i}s: {len(seg_text)} 字符", file=sys.stderr)
        text = "\n".join(segments)
    else:
        res = model.generate(input=str(audio_path), language="zh", use_itn=True)
        if not res or len(res) == 0:
            raise RuntimeError("转录无输出")
        text = res[0].get("text", "") if isinstance(res[0], dict) else str(res[0])
        text = re.sub(r"<\|[^|]+\|>", "", text).strip()

    elapsed = time.time() - t0

    meta = {
        "model": "SenseVoice-Small",
        "duration": audio_path.stat().st_size,
        "time_seconds": elapsed,
        "load_time": model_time,
    }

    print(
        f"[sensevoice] 转录完成 | {len(text)} 字符 | "
        f"{elapsed:.2f}s 处理",
        file=sys.stderr,
    )
    return text, meta


def main():
    import argparse

    parser = argparse.ArgumentParser(description="SenseVoice 音频转录工具")
    parser.add_argument("input", help="音频文件路径")
    parser.add_argument("--output", "-o", help="输出到文件 (默认: stdout)")
    args = parser.parse_args()

    audio_path = Path(args.input)
    if not audio_path.exists():
        print(f"文件不存在: {audio_path}", file=sys.stderr)
        sys.exit(1)

    transcript, meta = transcribe(audio_path)

    if args.output:
        Path(args.output).write_text(transcript, encoding="utf-8")
        print(f"[sensevoice] 已保存: {args.output}", file=sys.stderr)
    else:
        print(transcript)


if __name__ == "__main__":
    main()
