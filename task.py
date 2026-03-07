"""
后台任务处理模块
处理视频转写的完整流程
"""
import asyncio
import logging
import os
from typing import Callable, Awaitable
from bilibili_utils import download_video
from audio_utils import extract_audio
from asr_utils import transcribe_audio
from llm_utils import refine_text
from doc_utils import create_and_share_document
from utils import cleanup_files, logger


async def process_video(video_id: str, user_id: str, send_message: Callable[[str, str], Awaitable[None]]) -> None:
    """
    处理视频转写的完整流程（异步函数）

    Args:
        video_id: 视频 ID（BV 号或 AV 号）
        user_id: 飞书用户 ID
        send_message: 发送消息的异步函数
    """
    video_path = None
    audio_path = None

    try:
        logger.info(f"开始处理视频: {video_id}, 用户: {user_id}")

        await send_message(user_id, f"正在处理视频 {video_id}，请稍候...")

        # 1. 下载视频（在线程中执行阻塞操作）
        video_path = await asyncio.to_thread(download_video, video_id)

        if not video_path:
            await send_message(user_id, f"❌ 视频下载失败，请检查视频ID是否正确")
            return

        await send_message(user_id, f"✅ 视频下载成功，正在提取音频...")

        # 2. 提取音频（在线程中执行阻塞操作）
        audio_path = await asyncio.to_thread(extract_audio, video_path)

        if not audio_path:
            await send_message(user_id, f"❌ 音频提取失败")
            cleanup_files(video_path)
            return

        await send_message(user_id, f"✅ 音频提取成功，正在进行语音识别...")

        # 3. 语音识别（在线程中执行阻塞操作）
        original_text = await asyncio.to_thread(transcribe_audio, audio_path)

        if not original_text:
            await send_message(user_id, f"❌ 语音识别失败")
            cleanup_files(video_path, audio_path)
            return

        await send_message(user_id, f"✅ 语音识别成功，正在进行文本精转...")

        # 4. LLM 精转（在线程中执行阻塞操作）
        refined_text = await asyncio.to_thread(refine_text, original_text)

        if not refined_text:
            await send_message(user_id, f"❌ 文本精转失败")
            cleanup_files(video_path, audio_path)
            return

        await send_message(user_id, f"✅ 文本精转成功，正在创建飞书文档...")

        # 5. 创建飞书文档并获取分享链接
        # 注意：这里需要飞书客户端，暂时使用占位符
        # 实际实现时需要从 feishu_handler 模块获取客户端实例
        share_url = "https://www.feishu.cn/docx/placeholder"

        # TODO: 实际创建文档
        # from feishu_handler import get_feishu_client
        # client = get_feishu_client()
        # share_url = await asyncio.to_thread(create_and_share_document, client, refined_text)

        if not share_url:
            await send_message(user_id, f"❌ 文档创建失败")
            cleanup_files(video_path, audio_path)
            return

        # 6. 发送结果
        await send_message(user_id, f"✅ 处理完成！\n\n📄 文档链接：{share_url}")

        logger.info(f"视频处理成功: {video_id}")

    except Exception as e:
        logger.error(f"处理视频时发生错误: {e}")
        await send_message(user_id, f"❌ 处理视频时发生错误: {str(e)}")

    finally:
        # 7. 清理临时文件
        files_to_cleanup = []
        if video_path:
            files_to_cleanup.append(video_path)
        if audio_path:
            files_to_cleanup.append(audio_path)

        if files_to_cleanup:
            cleanup_files(*files_to_cleanup)


def process_video_sync(video_id: str, user_id: str, send_message: Callable[[str, str], None]) -> None:
    """
    处理视频转写的完整流程（同步版本，用于在线程中运行）

    Args:
        video_id: 视频 ID（BV 号或 AV 号）
        user_id: 飞书用户 ID
        send_message: 发送消息的同步函数
    """
    video_path = None
    audio_path = None

    try:
        logger.info(f"开始处理视频: {video_id}, 用户: {user_id}")

        send_message(user_id, f"正在处理视频 {video_id}，请稍候...")

        # 1. 下载视频
        video_path = download_video(video_id)

        if not video_path:
            send_message(user_id, f"❌ 视频下载失败，请检查视频ID是否正确")
            return

        send_message(user_id, f"✅ 视频下载成功，正在提取音频...")

        # 2. 提取音频
        audio_path = extract_audio(video_path)

        if not audio_path:
            send_message(user_id, f"❌ 音频提取失败")
            cleanup_files(video_path)
            return

        send_message(user_id, f"✅ 音频提取成功，正在进行语音识别...")

        # 3. 语音识别
        original_text = transcribe_audio(audio_path)

        if not original_text:
            send_message(user_id, f"❌ 语音识别失败")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 语音识别成功，正在进行文本精转...")

        # 4. LLM 精转
        refined_text = refine_text(original_text)

        if not refined_text:
            send_message(user_id, f"❌ 文本精转失败")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 文本精转成功，正在创建飞书文档...")

        # 5. 创建飞书文档并获取分享链接
        # TODO: 实际创建文档
        share_url = "https://www.feishu.cn/docx/placeholder"

        # 6. 发送结果
        send_message(user_id, f"✅ 处理完成！\n\n📄 文档链接：{share_url}")

        logger.info(f"视频处理成功: {video_id}")

    except Exception as e:
        logger.error(f"处理视频时发生错误: {e}")
        send_message(user_id, f"❌ 处理视频时发生错误: {str(e)}")

    finally:
        # 7. 清理临时文件
        files_to_cleanup = []
        if video_path:
            files_to_cleanup.append(video_path)
        if audio_path:
            files_to_cleanup.append(audio_path)

        if files_to_cleanup:
            cleanup_files(*files_to_cleanup)
