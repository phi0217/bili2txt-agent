"""
B站视频下载模块 - 使用 yt-dlp

支持：
1. 下载视频（指定清晰度）
2. 只下载音频（推荐用于语音识别）
"""

import logging
import os
from typing import Optional
import subprocess

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

logger = logging.getLogger(__name__)


class BiliBiliDownloader:
    """B站视频下载器（使用 yt-dlp）"""

    def __init__(self, temp_dir: str = "./temp"):
        """
        初始化下载器

        Args:
            temp_dir: 临时文件目录
        """
        self.temp_dir = temp_dir
        self.ensure_temp_dir()

        if not YT_DLP_AVAILABLE:
            logger.warning("yt-dlp 未安装，请运行: pip install yt-dlp")

    def ensure_temp_dir(self):
        """确保临时目录存在"""
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_audio(self, video_id: str, audio_quality: str = "128") -> Optional[str]:
        """
        只下载音频（推荐用于语音识别）

        Args:
            video_id: 视频ID（BV号或AV号）
            audio_quality: 音频质量（kbps），默认128，可选64/96/128/192/320

        Returns:
            下载的音频文件路径（MP3格式），失败返回 None
        """
        if not YT_DLP_AVAILABLE:
            logger.error("yt-dlp 未安装")
            return None

        # 构造URL
        if video_id.startswith('av'):
            url = f"https://www.bilibili.com/video/{video_id}"
        else:
            url = f"https://www.bilibili.com/video/{video_id}"

        logger.info(f"开始下载音频: {video_id}")
        logger.info(f"音频质量: {audio_quality}kbps")

        # yt-dlp 配置
        ydl_opts = {
            'format': 'bestaudio/best',  # 最佳音频
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 获取信息
                logger.info("正在获取视频信息...")
                info = ydl.extract_info(url, download=False)

                if info:
                    duration = info.get('duration', 0)
                    title = info.get('title', 'Unknown')
                    logger.info(f"视频标题: {title}")
                    logger.info(f"视频时长: {duration}秒")

                # 下载音频
                logger.info("正在下载音频...")
                info = ydl.extract_info(url, download=True)

                # 获取文件路径
                filename = ydl.prepare_filename(info)

                # yt-dlp 可能会改变扩展名（.mp3），所以我们需要查找实际的文件
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    file_size_mb = file_size / (1024 * 1024)

                    logger.info(f"✅ 音频下载成功")
                    logger.info(f"   文件: {filename}")
                    logger.info(f"   大小: {file_size_mb:.2f}MB")

                    return filename
                else:
                    # 尝试查找 .mp3 文件
                    mp3_file = filename.rsplit('.', 1)[0] + '.mp3'
                    if os.path.exists(mp3_file):
                        file_size = os.path.getsize(mp3_file)
                        file_size_mb = file_size / (1024 * 1024)

                        logger.info(f"✅ 音频下载成功")
                        logger.info(f"   文件: {mp3_file}")
                        logger.info(f"   大小: {file_size_mb:.2f}MB")

                        return mp3_file
                    else:
                        logger.error("文件下载失败，未找到输出文件")
                        return None

        except Exception as e:
            logger.error(f"下载音频失败: {e}")
            return None

    def download_video(self, video_id: str, max_height: int = 480) -> Optional[str]:
        """
        下载视频（指定最高清晰度）

        Args:
            video_id: 视频ID（BV号或AV号）
            max_height: 最高清晰度（高度像素），默认480，可选360/480/720/1080

        Returns:
            下载的视频文件路径，失败返回 None
        """
        if not YT_DLP_AVAILABLE:
            logger.error("yt-dlp 未安装")
            return None

        # 构造URL
        if video_id.startswith('av'):
            url = f"https://www.bilibili.com/video/{video_id}"
        else:
            url = f"https://www.bilibili.com/video/{video_id}"

        logger.info(f"开始下载视频: {video_id}")
        logger.info(f"最高清晰度: {max_height}p")

        # yt-dlp 配置
        format_spec = f'bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]'

        ydl_opts = {
            'format': format_spec,
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 获取信息
                logger.info("正在获取视频信息...")
                info = ydl.extract_info(url, download=False)

                if info:
                    duration = info.get('duration', 0)
                    title = info.get('title', 'Unknown')
                    logger.info(f"视频标题: {title}")
                    logger.info(f"视频时长: {duration}秒")

                # 下载视频
                logger.info("正在下载视频...")
                info = ydl.extract_info(url, download=True)

                # 获取文件路径
                filename = ydl.prepare_filename(info)

                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    file_size_mb = file_size / (1024 * 1024)

                    logger.info(f"✅ 视频下载成功")
                    logger.info(f"   文件: {filename}")
                    logger.info(f"   大小: {file_size_mb:.2f}MB")

                    return filename
                else:
                    logger.error("文件下载失败，未找到输出文件")
                    return None

        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            return None

    def _progress_hook(self, d):
        """进度回调"""
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or 0

                if total > 0:
                    percent = downloaded / total * 100
                    logger.debug(f"下载进度: {percent:.1f}%")
            except:
                pass

        elif d['status'] == 'finished':
            logger.info("下载完成")


# 便捷函数
def download_audio_only(video_id: str, audio_quality: str = "128") -> Optional[str]:
    """
    只下载音频（推荐用于语音识别）

    这是 bili2txt-agent 项目的推荐方式。

    Args:
        video_id: 视频ID（BV号或AV号）
        audio_quality: 音频质量（kbps），默认128

    Returns:
        下载的音频文件路径（MP3格式）
    """
    downloader = BiliBiliDownloader()
    return downloader.download_audio(video_id, audio_quality)


def download_video_low_quality(video_id: str, max_height: int = 480) -> Optional[str]:
    """
    下载低清晰度视频

    Args:
        video_id: 视频ID（BV号或AV号）
        max_height: 最高清晰度，默认480p

    Returns:
        下载的视频文件路径
    """
    downloader = BiliBiliDownloader()
    return downloader.download_video(video_id, max_height)
