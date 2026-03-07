"""
音频处理工具
提供从视频中提取音频的功能
"""
import subprocess
import os
import logging
from typing import Optional


logger = logging.getLogger("bili2txt-agent")


def extract_audio(video_path: str, timeout: int = 300) -> Optional[str]:
    """
    从视频中提取音频

    Args:
        video_path: 视频文件路径
        timeout: 超时时间（秒）

    Returns:
        提取的音频文件路径（MP3格式），失败则返回 None
    """
    try:
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return None

        # 构造音频文件路径（与视频同目录，扩展名改为 .mp3）
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        logger.info(f"开始提取音频: {video_path} -> {audio_path}")

        # 调用 ffmpeg 提取音频
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-q:a", "0",
            "-map", "a",
            audio_path,
            "-y"  # 覆盖已存在的文件
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            logger.error(f"提取音频失败: {result.stderr}")
            return None

        # 检查音频文件是否成功创建
        if os.path.exists(audio_path):
            logger.info(f"音频提取成功: {audio_path}")
            return audio_path
        else:
            logger.error("音频文件未成功创建")
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"提取音频超时（超过 {timeout} 秒）")
        return None
    except Exception as e:
        logger.error(f"提取音频时发生错误: {e}")
        return None
