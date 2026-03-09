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

                # 检查缓存版本：清理旧格式的缓存（没有 language 字段的）
                invalid_keys = []
                for key, value in self.cache_data.items():
                    if not isinstance(value, dict) or 'language' not in value:
                        invalid_keys.append(key)
                        logger.warning(f"发现旧格式缓存，将清理: {key}")

                if invalid_keys:
                    for key in invalid_keys:
                        del self.cache_data[key]
                    # 保存清理后的缓存
                    self._save_cache()
                    logger.info(f"🗑️  已清理 {len(invalid_keys)} 条旧格式缓存")

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

    def get(self, video_id: str, language: str = "zh") -> Optional[dict]:
        """
        获取视频缓存

        Args:
            video_id: 视频ID
            language: 语言代码（'zh'=中文, 'en'=英文，默认 'zh'）

        Returns:
            缓存数据字典，如果不存在则返回 None
            格式：{
                "video_id": "BV1xx411c7mD",
                "language": "zh",
                "video_title": "视频标题",
                "original_text": "原始识别文本",
                "refined_text": "原文精转文本",
                "summary_text": "关键纪要文本",
                "processed_time": "2026-03-08 12:00:00",
                "original_length": 1234,
                "refined_length": 567
            }
        """
        cache_key = f"{video_id}#{language}"
        return self.cache_data.get(cache_key)

    def set(self, video_id: str, video_title: str, original_text: str, refined_text: str, summary_text: str, language: str = "zh"):
        """
        设置视频缓存

        Args:
            video_id: 视频ID
            video_title: 视频标题
            original_text: 原始识别文本
            refined_text: 原文精转文本
            summary_text: 关键纪要文本
            language: 语言代码（'zh'=中文, 'en'=英文，默认 'zh'）
        """
        cache_key = f"{video_id}#{language}"
        cache_entry = {
            "video_id": video_id,
            "language": language,
            "video_title": video_title,
            "original_text": original_text,
            "refined_text": refined_text,
            "summary_text": summary_text,
            "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_length": len(original_text),
            "refined_length": len(refined_text)
        }

        self.cache_data[cache_key] = cache_entry
        self._save_cache()
        lang_label = "英文/双语" if language == "en" else "中文"
        logger.info(f"✅ 缓存已保存: {video_id} ({lang_label}) - {video_title}")

    def exists(self, video_id: str, language: str = "zh") -> bool:
        """
        检查视频是否已缓存

        Args:
            video_id: 视频ID
            language: 语言代码（'zh'=中文, 'en'=英文，默认 'zh'）

        Returns:
            如果存在则返回 True，否则返回 False
        """
        cache_key = f"{video_id}#{language}"
        return cache_key in self.cache_data

    def delete(self, video_id: str, language: str = "zh"):
        """
        删除视频缓存

        Args:
            video_id: 视频ID
            language: 语言代码（'zh'=中文, 'en'=英文，默认 'zh'）
        """
        cache_key = f"{video_id}#{language}"
        if cache_key in self.cache_data:
            del self.cache_data[cache_key]
            self._save_cache()
            lang_label = "英文/双语" if language == "en" else "中文"
            logger.info(f"🗑️  缓存已删除: {video_id} ({lang_label})")

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
