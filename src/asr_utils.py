"""
语音识别工具
使用 Whisper 模型将音频转为文字
"""
import logging
import threading
from typing import Optional


logger = logging.getLogger("bili2txt-agent")

# 模块级别加载 Whisper 模型（只加载一次）
_whisper_model = None

# 线程锁，保护 Whisper 模型的并发访问
_whisper_lock = threading.Lock()


def get_whisper_model(model_size: str = "base"):
    """
    获取 Whisper 模型（单例模式，只加载一次）

    Args:
        model_size: 模型大小（tiny, base, small, medium, large）

    Returns:
        Whisper 模型
    """
    global _whisper_model

    if _whisper_model is None:
        logger.info(f"正在加载 Whisper {model_size} 模型...")
        try:
            import whisper
            _whisper_model = whisper.load_model(model_size)
            logger.info(f"Whisper {model_size} 模型加载成功")
        except Exception as e:
            logger.error(f"加载 Whisper 模型失败: {e}")
            raise

    return _whisper_model


def transcribe_audio(audio_path: str, model_size: str = "base", language: str = "zh") -> Optional[str]:
    """
    将音频转换为文字

    Args:
        audio_path: 音频文件路径
        model_size: Whisper 模型大小（默认为 base）
        language: 语言代码（'zh'=中文, 'en'=英文，默认为 'zh'）

    Returns:
        识别的文字，失败则返回 None
    """
    try:
        import os

        if not os.path.exists(audio_path):
            logger.error(f"音频文件不存在: {audio_path}")
            return None

        logger.info(f"开始语音识别: {audio_path}, 语言: {language}")

        # 获取 Whisper 模型
        model = get_whisper_model(model_size)

        # 使用线程锁保护模型调用
        with _whisper_lock:
            logger.debug(f"获取 Whisper 模型锁: {audio_path}")
            # 进行语音识别（支持多语言）
            result = model.transcribe(audio_path, language=language)
            text = result.get("text", "")
            logger.debug(f"释放 Whisper 模型锁: {audio_path}")

        if text:
            logger.info(f"语音识别成功，文本长度: {len(text)} 字符")
            return text
        else:
            logger.warning("语音识别结果为空")
            return None

    except Exception as e:
        logger.error(f"语音识别时发生错误: {e}")
        return None
