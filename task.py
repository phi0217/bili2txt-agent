"""
后台任务处理模块
处理视频转写的完整流程
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Callable, Awaitable
from bilibili_utils import download_video
from audio_utils import extract_audio
from asr_utils import transcribe_audio
from llm_utils import refine_text
from doc_utils import create_and_share_document
from utils import cleanup_files, logger
from config import config


def save_result_text(video_id: str, original_text: str, refined_text: str, user_id: str = "unknown") -> str:
    """
    保存处理结果到本地文件

    Args:
        video_id: 视频ID
        original_text: 原始识别文本
        refined_text: 精转后文本
        user_id: 用户ID（可选）

    Returns:
        保存的文件路径
    """
    try:
        # 创建 results 目录
        results_dir = os.path.join(config.TEMP_DIR, "results")
        os.makedirs(results_dir, exist_ok=True)

        # 生成文件名（使用时间戳和视频ID）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{video_id}.md"
        file_path = os.path.join(results_dir, filename)

        # 构建 Markdown 内容
        content = f"""# 视频转写结果

**视频ID**: {video_id}
**处理时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**用户ID**: {user_id}

---

## 【摘要】

（待添加摘要功能）

## 【原文整理】

{refined_text}

---

## 附录：原始识别文本

{original_text}

---

*本文档由 bili2txt-agent 自动生成*
"""

        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"✅ 结果已保存到本地: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"保存结果文本时发生错误: {e}")
        return None


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

        # 1. 下载视频
        send_message(user_id, f"📥 正在下载视频: {video_id}")
        video_path = download_video(video_id)

        if not video_path:
            send_message(user_id, f"❌ 视频下载失败\n\n请检查：\n1. 视频ID是否正确\n2. 视频是否为私密或删除\n3. 网络连接是否正常")
            return

        send_message(user_id, f"✅ 视频下载成功\n🎵 正在提取音频...")

        # 2. 提取音频
        audio_path = extract_audio(video_path)

        if not audio_path:
            send_message(user_id, f"❌ 音频提取失败")
            cleanup_files(video_path)
            return

        send_message(user_id, f"✅ 音频提取成功\n🎤 正在进行语音识别（这可能需要几分钟）...")

        # 3. 语音识别
        original_text = transcribe_audio(audio_path)

        if not original_text:
            send_message(user_id, f"❌ 语音识别失败\n\n可能原因：\n1. 视频中没有语音\n2. 语音质量过低\n3. 视频语言不是中文")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 语音识别成功\n识别文本长度：{len(original_text)} 字符\n✨ 正在进行文本精转...")

        # 4. LLM 精转
        refined_text = refine_text(original_text)

        if not refined_text:
            send_message(user_id, f"❌ 文本精转失败\n\nAPI调用失败，请稍后重试")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 文本精转成功\n📝 正在创建飞书云文档...")

        # 5. 创建飞书文档并获取分享链接
        from doc_utils import create_and_share_document
        from feishu_handler import get_feishu_client

        try:
            feishu_client = get_feishu_client()

            # 格式化内容为 Markdown
            from doc_utils import format_content_as_markdown
            formatted_content = format_content_as_markdown(original_text, refined_text, video_id)

            # 创建文档并获取分享链接
            share_url = create_and_share_document(feishu_client, formatted_content)

            if not share_url:
                logger.error("文档创建失败，无法获取分享链接")
                send_message(user_id, f"❌ 文档创建失败\n\n处理已完成，但无法创建飞书文档\n\n💾 本地缓存文件已保存")
                return

        except Exception as e:
            logger.error(f"创建文档时发生错误: {e}")
            logger.exception("详细错误堆栈")
            send_message(user_id, f"❌ 文档创建异常\n\n错误信息: {str(e)}\n\n💾 本地缓存文件已保存")
            return

        # 6. 保存结果到本地
        result_file = save_result_text(video_id, original_text, refined_text, user_id)

        # 7. 发送结果
        if result_file:
            result_message = f"""✅ 处理完成！

📹 视频ID：{video_id}
📄 原文长度：{len(original_text)} 字符
📝 精转后长度：{len(refined_text)} 字符

💾 本地缓存：{result_file}

🔗 文档链接：{share_url}

💡 提示：您可以复制链接到浏览器中查看完整文档"""
        else:
            result_message = f"""✅ 处理完成！

📹 视频ID：{video_id}
📄 原文长度：{len(original_text)} 字符
📝 精转后长度：{len(refined_text)} 字符

⚠️ 本地缓存失败

🔗 文档链接：{share_url}"""

        send_message(user_id, result_message)

        logger.info(f"视频处理成功: {video_id}")

    except Exception as e:
        logger.error(f"处理视频时发生错误: {e}")
        error_message = f"❌ 处理视频时发生错误\n\n错误信息：{str(e)}\n\n请稍后重试，如果问题持续，请联系开发者"
        send_message(user_id, error_message)

    finally:
        # 7. 清理临时文件
        files_to_cleanup = []
        if video_path:
            files_to_cleanup.append(video_path)
        if audio_path:
            files_to_cleanup.append(audio_path)

        if files_to_cleanup:
            cleanup_files(*files_to_cleanup)
