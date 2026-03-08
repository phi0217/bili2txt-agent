"""
通用工具模块
提供日志配置和文件清理等通用功能
"""
import os
import logging
import glob
from typing import List


def setup_logging(name: str = "bili2txt-agent") -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 控制台处理器
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def cleanup_files(*file_paths: str) -> None:
    """
    清理文件或目录，忽略不存在的文件

    Args:
        *file_paths: 要清理的文件路径列表
    """
    logger = logging.getLogger("bili2txt-agent")

    for path in file_paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.info(f"已删除文件: {path}")
            elif os.path.isdir(path):
                # 删除目录及其所有内容
                import shutil
                shutil.rmtree(path)
                logger.info(f"已删除目录: {path}")
            else:
                logger.debug(f"文件/目录不存在，跳过: {path}")
        except Exception as e:
            logger.error(f"清理文件失败 {path}: {e}")


def find_latest_file(directory: str, pattern: str = "*") -> str:
    """
    在指定目录中查找最新创建的文件

    Args:
        directory: 要搜索的目录
        pattern: 文件匹配模式（如 "*.mp4"）

    Returns:
        最新文件的完整路径，如果没有找到则返回 None
    """
    logger = logging.getLogger("bili2txt-agent")

    try:
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)

        if not files:
            return None

        # 按创建时间排序，返回最新的文件
        latest_file = max(files, key=os.path.getctime)
        logger.info(f"找到最新文件: {latest_file}")
        return latest_file
    except Exception as e:
        logger.error(f"查找文件失败: {e}")
        return None


# 创建全局日志记录器
logger = setup_logging()
