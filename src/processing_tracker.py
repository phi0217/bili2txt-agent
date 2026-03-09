"""
处理中的任务跟踪器
避免重复处理同一个视频
"""
import threading
import logging
from typing import Optional, Set
from datetime import datetime, timedelta


logger = logging.getLogger("bili2txt-agent")


class ProcessingTracker:
    """处理中的任务跟踪器（线程安全）"""

    def __init__(self):
        """初始化跟踪器"""
        # 正在处理的视频ID集合（线程安全）
        self._processing: Set[str] = set()
        # 线程锁
        self._lock = threading.Lock()
        # 处理开始时间记录
        self._start_times = {}

    def start_processing(self, video_id: str) -> bool:
        """
        开始处理视频

        Args:
            video_id: 视频ID

        Returns:
            True 如果可以开始处理，False 如果已经在处理中
        """
        with self._lock:
            if video_id in self._processing:
                logger.warning(f"视频 {video_id} 已在处理中，忽略重复请求")
                return False

            self._processing.add(video_id)
            self._start_times[video_id] = datetime.now()
            logger.info(f"开始处理视频: {video_id}")
            return True

    def finish_processing(self, video_id: str):
        """
        完成处理视频

        Args:
            video_id: 视频ID
        """
        with self._lock:
            if video_id in self._processing:
                self._processing.remove(video_id)
                start_time = self._start_times.pop(video_id, None)
                if start_time:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(f"完成处理视频: {video_id}，耗时: {elapsed:.2f}秒")
                else:
                    logger.info(f"完成处理视频: {video_id}")

    def is_processing(self, video_id: str) -> bool:
        """
        检查视频是否正在处理中

        Args:
            video_id: 视频ID

        Returns:
            True 如果正在处理中
        """
        with self._lock:
            return video_id in self._processing

    def get_processing_time(self, video_id: str) -> Optional[float]:
        """
        获取视频已处理的时间（秒）

        Args:
            video_id: 视频ID

        Returns:
            已处理的秒数，如果不在处理中则返回 None
        """
        with self._lock:
            if video_id not in self._processing:
                return None

            start_time = self._start_times.get(video_id)
            if start_time:
                return (datetime.now() - start_time).total_seconds()
            return None

    def get_all_processing(self) -> list:
        """
        获取所有正在处理的视频ID列表

        Returns:
            视频ID列表
        """
        with self._lock:
            return list(self._processing)

    def get_count(self) -> int:
        """
        获取正在处理的任务数量

        Returns:
            任务数量
        """
        with self._lock:
            return len(self._processing)

    def cleanup_stale(self, max_seconds: int = 3600):
        """
        清理超时的处理任务（防止意外退出导致的死锁）

        Args:
            max_seconds: 最大处理时间（秒），默认1小时
        """
        with self._lock:
            current_time = datetime.now()
            stale_videos = []

            for video_id, start_time in self._start_times.items():
                elapsed = (current_time - start_time).total_seconds()
                if elapsed > max_seconds:
                    stale_videos.append(video_id)

            for video_id in stale_videos:
                logger.warning(f"清理超时处理任务: {video_id}，已处理 {max_seconds} 秒")
                self._processing.remove(video_id)
                del self._start_times[video_id]

            if stale_videos:
                logger.info(f"清理了 {len(stale_videos)} 个超时任务")


# 全局单例
_tracker_instance = None


def get_processing_tracker() -> ProcessingTracker:
    """
    获取全局处理跟踪器实例（单例模式）

    Returns:
        ProcessingTracker 实例
    """
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ProcessingTracker()
    return _tracker_instance
