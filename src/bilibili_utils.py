"""
B站视频处理工具
提供视频ID提取和视频下载功能
支持短链接解析（b23.tv）
"""
import re
import subprocess
import os
import logging
from typing import Optional
from urllib.parse import urlparse
import requests
from config import config
from utils import find_latest_file


logger = logging.getLogger("bili2txt-agent")


def extract_video_id(text: str) -> tuple[Optional[str], str]:
    """
    从用户输入的文本中提取B站视频ID（BV号或AV号）和语言标记
    支持短链接解析（b23.tv）

    Args:
        text: 用户发送的文本内容

    Returns:
        (视频ID, 语言代码) 元组
        - 视频ID: 如 "BV1GJ411x7h7" 或 "av123456"；若无法提取则返回 None
        - 语言代码: "zh"=中文, "en"=英文，默认 "zh"

    使用示例:
        BV1xx411c7mD        -> ("BV1xx411c7mD", "zh")
        BV1xx411c7mD#en     -> ("BV1xx411c7mD", "en")
        BV1xx411c7mD#zh     -> ("BV1xx411c7mD", "zh")
    """
    if not text:
        return (None, "zh")

    # 默认语言为中文
    language = "zh"

    # 检查语言标记（支持 #en 或 #zh 后缀）
    # 可能的格式：BV1xx411c7mD#en, BV1xx411c7mD #en, https://...#en
    lang_pattern = r'#(en|zh)\b'
    lang_match = re.search(lang_pattern, text, re.IGNORECASE)

    if lang_match:
        language = lang_match.group(1).lower()
        logger.info(f"检测到语言标记: {language}")
        # 从文本中移除语言标记，避免影响后续匹配
        text = re.sub(lang_pattern, '', text).strip()

    # 1. 优先使用正则表达式直接匹配 BV号 和 AV号

    # 1. 优先使用正则表达式直接匹配 BV号 和 AV号
    bv_pattern = r'BV[a-zA-Z0-9]+'
    bv_match = re.search(bv_pattern, text)

    if bv_match:
        video_id = bv_match.group(0)
        logger.info(f"直接匹配到BV号: {video_id}, 语言: {language}")
        return (video_id, language)

    av_pattern = r'av\d+'
    av_match = re.search(av_pattern, text, re.IGNORECASE)

    if av_match:
        video_id = av_match.group(0).lower()
        logger.info(f"直接匹配到AV号: {video_id}, 语言: {language}")
        return (video_id, language)

    # 2. 如果未直接匹配到，尝试从文本中提取 URL
    urls = extract_urls(text)

    if not urls:
        logger.warning(f"未能从文本中提取到URL: {text}")
        return (None, language)

    # 3. 遍历 URL，尝试提取视频ID
    for url in urls:
        video_id = extract_id_from_url(url)
        if video_id:
            logger.info(f"从URL提取到视频ID: {video_id} (源URL: {url}), 语言: {language}")
            return (video_id, language)

    logger.warning(f"未能从任何URL中提取视频ID: {text}")
    return (None, language)


def extract_urls(text: str) -> list[str]:
    """
    从文本中提取所有 URL（以 http:// 或 https:// 开头）

    Args:
        text: 要搜索的文本

    Returns:
        URL 列表，按出现顺序排列
    """
    # 匹配 http:// 或 https:// 开头的 URL，直到遇到空格或行尾
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)

    if urls:
        logger.debug(f"提取到 {len(urls)} 个URL: {urls}")

    return urls


def extract_id_from_url(url: str) -> Optional[str]:
    """
    从 URL 中提取B站视频ID
    支持短链接解析（b23.tv）

    Args:
        url: 视频 URL

    Returns:
        视频ID字符串，如 "BV1GJ411x7h7" 或 "av123456"；若无法提取则返回 None
    """
    try:
        parsed = urlparse(url)

        # 1. 检查是否为 b23.tv 短链接，需要解析重定向
        if 'b23.tv' in parsed.netloc or 'b23.url.cn' in parsed.netloc:
            logger.debug(f"检测到b23.tv短链接，开始解析: {url}")
            resolved_url = resolve_short_link(url)

            if resolved_url:
                # 递归处理解析后的 URL
                return extract_id_from_url(resolved_url)
            else:
                logger.warning(f"短链接解析失败: {url}")
                return None

        # 2. 从 B站完整 URL 中提取视频ID
        # 支持的路径格式：
        # - /video/BVxxxx
        # - /video/avxxxx
        # - /BVxxxx
        # - /avxxxx

        # 检查是否为 B站相关域名
        bilibili_domains = ['bilibili.com', 'www.bilibili.com', 'm.bilibili.com', 'b23.tv']
        if parsed.netloc not in bilibili_domains:
            logger.debug(f"非B站域名，跳过: {parsed.netloc}")
            return None

        # 提取路径
        path = parsed.path

        # 匹配 /video/BVxxxx 或 /video/avxxxx
        video_pattern = r'/video/(BV[a-zA-Z0-9]+|av\d+)'
        video_match = re.search(video_pattern, path, re.IGNORECASE)

        if video_match:
            video_id = video_match.group(1)
            # BV号区分大小写，保持原样；AV号统一转小写
            if video_id.upper().startswith('BV'):
                return video_id  # 保持原始大小写
            else:
                return video_id.lower()

        # 匹配 /BVxxxx 或 /avxxxx（直接在根路径）
        direct_pattern = r'/(BV[a-zA-Z0-9]+|av\d+)'
        direct_match = re.search(direct_pattern, path, re.IGNORECASE)

        if direct_match:
            video_id = direct_match.group(1)
            # BV号区分大小写，保持原样；AV号统一转小写
            if video_id.upper().startswith('BV'):
                return video_id  # 保持原始大小写
            else:
                return video_id.lower()

        logger.debug(f"未能从URL路径中提取视频ID: {path}")
        return None

    except Exception as e:
        logger.error(f"解析URL时发生错误: {url}, 错误: {e}")
        return None


def resolve_short_link(short_url: str, timeout: int = 5) -> Optional[str]:
    """
    解析 b23.tv 短链接，获取重定向后的真实 URL

    Args:
        short_url: 短链接 URL
        timeout: 请求超时时间（秒）

    Returns:
        解析后的真实 URL，失败则返回 None
    """
    try:
        logger.debug(f"发起 HEAD 请求解析短链接: {short_url}")

        response = requests.head(
            short_url,
            allow_redirects=True,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        if response.status_code == 200:
            resolved_url = response.url
            logger.debug(f"短链接解析成功: {short_url} → {resolved_url}")
            return resolved_url
        else:
            logger.warning(f"短链接返回非200状态码: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"解析短链接超时（超过 {timeout} 秒）: {short_url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"解析短链接时发生网络错误: {short_url}, 错误: {e}")
        return None
    except Exception as e:
        logger.error(f"解析短链接时发生未知错误: {short_url}, 错误: {e}")
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
