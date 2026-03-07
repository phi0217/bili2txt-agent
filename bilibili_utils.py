"""
B站视频处理工具
提供视频ID提取和视频下载功能
"""
import re
import subprocess
import os
import logging
from typing import Optional
from config import config
from utils import find_latest_file


logger = logging.getLogger("bili2txt-agent")


def extract_video_id(text: str) -> Optional[str]:
    """
    从文本中提取B站视频ID（BV号或AV号）
    只返回第一个匹配项

    Args:
        text: 要搜索的文本

    Returns:
        视频ID（BV号或AV号），如果没有匹配则返回 None
    """
    if not text:
        return None

    # 匹配 BV 号：BV[a-zA-Z0-9]+
    bv_pattern = r'BV[a-zA-Z0-9]+'
    bv_match = re.search(bv_pattern, text)

    if bv_match:
        video_id = bv_match.group(0)
        logger.info(f"提取到BV号: {video_id}")
        return video_id

    # 匹配 AV 号：av\d+（忽略大小写）
    av_pattern = r'av\d+'
    av_match = re.search(av_pattern, text, re.IGNORECASE)

    if av_match:
        video_id = av_match.group(0).lower()  # 统一转为小写
        logger.info(f"提取到AV号: {video_id}")
        return video_id

    logger.warning(f"未能从文本中提取视频ID: {text}")
    return None


def download_video(video_id: str, timeout: int = 300) -> Optional[str]:
    """
    下载B站视频

    Args:
        video_id: 视频ID（BV号或AV号）
        timeout: 超时时间（秒）

    Returns:
        下载的视频文件路径，失败则返回 None
    """
    try:
        # 构造视频URL
        video_url = f"https://www.bilibili.com/video/{video_id}"
        logger.info(f"开始下载视频: {video_url}")

        # 确保临时目录存在
        config.ensure_temp_dir()

        # 调用 you-get 下载视频
        cmd = [
            "you-get",
            "-o", config.TEMP_DIR,
            video_url
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
            logger.error(f"下载视频失败: {result.stderr}")
            return None

        # 查找最新下载的视频文件
        video_path = find_latest_file(config.TEMP_DIR, "*.mp4")

        if video_path:
            logger.info(f"视频下载成功: {video_path}")
            return video_path
        else:
            logger.error("未能找到下载的视频文件")
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"下载视频超时（超过 {timeout} 秒）")
        return None
    except Exception as e:
        logger.error(f"下载视频时发生错误: {e}")
        return None
