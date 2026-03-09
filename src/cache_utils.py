"""
视频处理结果缓存模块
避免重复处理同一个视频
"""
import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict
from config import config


logger = logging.getLogger("bili2txt-agent")


class VideoCache:
    """视频处理结果缓存"""

    def __init__(self, cache_file: str = None):
        """
        初始化缓存

        Args:
            cache_file: 缓存文件路径，默认为 temp/video_cache.json
        """
        if cache_file is None:
            cache_dir = os.path.join(config.TEMP_DIR, "cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "video_cache.json")

        self.cache_file = cache_file
        self.cache_data: Dict[str, dict] = {}
        self._load_cache()

    def _load_cache(self):
        """从文件加载缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                logger.info(f"✅ 缓存加载成功，共 {len(self.cache_data)} 条记录")
            else:
                self.cache_data = {}
                logger.info("📝 缓存文件不存在，创建新缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            self.cache_data = {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"缓存已保存到: {self.cache_file}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    def get(self, video_id: str) -> Optional[dict]:
        """
        获取视频缓存

        Args:
            video_id: 视频ID

        Returns:
            缓存数据字典，如果不存在则返回 None
            格式：{
                "video_id": "BV1xx411c7mD",
                "video_title": "视频标题",
                "original_text": "原始识别文本",
                "refined_text": "原文精转文本",
                "summary_text": "关键纪要文本",
                "processed_time": "2026-03-08 12:00:00",
                "original_length": 1234,
                "refined_length": 567
            }
        """
        return self.cache_data.get(video_id)

    def set(self, video_id: str, video_title: str, original_text: str, refined_text: str, summary_text: str):
        """
        设置视频缓存

        Args:
            video_id: 视频ID
            video_title: 视频标题
            original_text: 原始识别文本
            refined_text: 原文精转文本
            summary_text: 关键纪要文本
        """
        cache_entry = {
            "video_id": video_id,
            "video_title": video_title,
            "original_text": original_text,
            "refined_text": refined_text,
            "summary_text": summary_text,
            "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_length": len(original_text),
            "refined_length": len(refined_text)
        }

        self.cache_data[video_id] = cache_entry
        self._save_cache()
        logger.info(f"✅ 缓存已保存: {video_id} - {video_title}")

    def exists(self, video_id: str) -> bool:
        """
        检查视频是否已缓存

        Args:
            video_id: 视频ID

        Returns:
            如果存在则返回 True，否则返回 False
        """
        return video_id in self.cache_data

    def delete(self, video_id: str):
        """
        删除视频缓存

        Args:
            video_id: 视频ID
        """
        if video_id in self.cache_data:
            del self.cache_data[video_id]
            self._save_cache()
            logger.info(f"🗑️  缓存已删除: {video_id}")

    def clear(self):
        """清空所有缓存"""
        self.cache_data = {}
        self._save_cache()
        logger.info("🗑️  所有缓存已清空")

    def get_all(self) -> Dict[str, dict]:
        """
        获取所有缓存

        Returns:
            所有缓存数据字典
        """
        return self.cache_data.copy()

    def get_count(self) -> int:
        """
        获取缓存数量

        Returns:
            缓存条目数量
        """
        return len(self.cache_data)


# 全局缓存实例
_cache_instance = None


def get_cache() -> VideoCache:
    """
    获取全局缓存实例（单例模式）

    Returns:
        VideoCache 实例
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = VideoCache()
    return _cache_instance
