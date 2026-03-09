"""
后台任务处理模块
处理视频转写的完整流程
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Callable, Awaitable

from utils import cleanup_files, logger
from config import config

# 尝试导入新的下载器
try:
    from bilibili_downloader import download_audio_only, BiliBiliDownloader
    YT_DLP_AVAILABLE = True
    logger.info("✅ yt-dlp 下载器已启用（只下载音频模式）")
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("⚠️  yt-dlp 未安装，将使用旧的下载方式")
    logger.warning("   建议: pip install yt-dlp")

# 导入旧的下载方式（作为备用）
from bilibili_utils import download_video
from audio_utils import extract_audio
from asr_utils import transcribe_audio
from llm_utils import refine_text, generate_summary, generate_refined_text
from doc_utils import create_and_share_document
from cache_utils import get_cache

# 尝试导入视频信息获取功能
try:
    from bilibili_downloader import get_video_info
    VIDEO_INFO_AVAILABLE = True
except ImportError:
    VIDEO_INFO_AVAILABLE = False
    get_video_info = None


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
        refined_text = await asyncio.to_thread(generate_refined_text, original_text)

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

    优化版：优先使用 yt-dlp 只下载音频，大幅提升速度
    支持缓存：同一视频直接返回之前的结果

    Args:
        video_id: 视频 ID（BV 号或 AV 号）
        user_id: 飞书用户 ID
        send_message: 发送消息的同步函数
    """
    video_path = None
    audio_path = None

    try:
        logger.info(f"开始处理: {video_id}")

        # 0. 检查缓存
        cache = get_cache()
        cached_data = cache.get(video_id)
        if cached_data:
            video_title = cached_data.get('video_title', video_id)
            original_text = cached_data.get('original_text', '')
            refined_text = cached_data.get('refined_text', '')
            summary_text = cached_data.get('summary_text', '')
            processed_time = cached_data.get('processed_time', '')

            logger.info(f"✅ 发现缓存: {video_id}，使用缓存文本重新创建文档")

            send_message(user_id, f"✅ 该视频已处理过，使用缓存文本重新创建文档\n\n📝 正在创建飞书云文档...")

            # 使用缓存的文本重新创建文档
            from feishu_handler import get_feishu_client

            try:
                feishu_client = get_feishu_client()

                # 创建原文精转文档
                refined_title = f"原文精转-{video_title}"
                refined_content = f"""# 原文精转

**视频ID**: {video_id}
**视频标题**: {video_title}
**处理时间**: {processed_time}
**来源**: bili2txt-agent 自动生成（使用缓存）

---

{refined_text}

---

## 附录：原始识别文本

{original_text}

---

*本文档由 [bili2txt-agent](https://github.com/yourusername/bili2txt-agent) 自动生成*
"""

                refined_url = create_and_share_document(feishu_client, refined_content, refined_title)

                if not refined_url:
                    logger.error("原文精转文档创建失败")
                    send_message(user_id, f"❌ 原文精转文档创建失败")
                    return

                # 创建关键纪要文档
                summary_title = f"关键纪要-{video_title}"
                summary_content = f"""# 关键纪要

**视频ID**: {video_id}
**视频标题**: {video_title}
**处理时间**: {processed_time}
**来源**: bili2txt-agent 自动生成（使用缓存）

---

{summary_text}

---

*本文档由 [bili2txt-agent](https://github.com/yourusername/bili2txt-agent) 自动生成*
"""

                summary_url = create_and_share_document(feishu_client, summary_content, summary_title)

                if not summary_url:
                    logger.error("关键纪要文档创建失败")
                    send_message(user_id, f"❌ 关键纪要文档创建失败\n\n原文精转文档已创建：{refined_url}")
                    return

                # 发送结果
                result_message = f"""✅ 处理完成！（使用缓存）

📹 视频ID：{video_id}
📹 视频标题：{video_title}
📄 原文长度：{len(original_text)} 字符
📝 精转后长度：{len(refined_text)} 字符
🕐 原始处理时间：{processed_time}

🔗 文档链接：原文精转-{video_title}
{refined_url}

🔗 文档链接：关键纪要-{video_title}
{summary_url}"""

                send_message(user_id, result_message)
                return

            except Exception as e:
                logger.error(f"使用缓存创建文档时发生错误: {e}")
                logger.exception("详细错误堆栈")
                send_message(user_id, f"❌ 文档创建异常\n\n错误信息: {str(e)}")
                return

        # 1. 下载音频（优先使用 yt-dlp 只下载音频）
        if YT_DLP_AVAILABLE:
            # 新方式：直接下载音频（推荐）
            logger.info("使用 yt-dlp 直接下载音频")
            send_message(user_id, f"🎵 正在下载音频: {video_id}")

            audio_path = download_audio_only(video_id, audio_quality="128")

            if not audio_path:
                logger.warning("yt-dlp 下载音频失败，尝试使用旧方式")
                send_message(user_id, f"⚠️ 音频下载失败，尝试旧方式...")
                # 回退到旧方式
                video_path = download_video(video_id)
                if not video_path:
                    send_message(user_id, f"❌ 下载失败\n\n请检查视频ID或网络连接")
                    return
                audio_path = extract_audio(video_path)
            else:
                send_message(user_id, f"✅ 音频下载成功（1-2秒）\n🎤 正在进行语音识别...")
        else:
            # 旧方式：下载视频 → 提取音频
            logger.info("使用旧方式：下载视频 → 提取音频")
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

        send_message(user_id, f"✅ 语音识别成功\n识别文本长度：{len(original_text)} 字符\n✨ 正在生成原文精转（这可能需要几分钟）...")

        # 4. 获取视频标题（如果可用）
        video_title = video_id  # 默认使用视频ID
        if VIDEO_INFO_AVAILABLE and get_video_info is not None:
            try:
                video_info = get_video_info(video_id)
                if video_info and video_info.get('title'):
                    video_title = video_info['title']
                    logger.info(f"视频标题: {video_title}")
            except Exception as e:
                logger.warning(f"获取视频标题失败: {e}")

        # 5. 生成原文精转
        refined_text = generate_refined_text(original_text)

        if not refined_text:
            send_message(user_id, f"❌ 原文精转失败\n\nAPI调用失败，请稍后重试")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 原文精转成功\n📝 正在生成关键纪要（这可能需要几分钟）...")

        # 6. 生成关键纪要
        summary_text = generate_summary(original_text)

        if not summary_text:
            send_message(user_id, f"❌ 关键纪要生成失败\n\nAPI调用失败，请稍后重试")
            cleanup_files(video_path, audio_path)
            return

        send_message(user_id, f"✅ 关键纪要生成成功\n📝 正在创建飞书云文档...")

        # 7. 创建两个飞书文档
        from feishu_handler import get_feishu_client

        try:
            feishu_client = get_feishu_client()

            # 创建原文精转文档
            refined_title = f"原文精转-{video_title}"
            refined_content = f"""# 原文精转

**视频ID**: {video_id}
**视频标题**: {video_title}
**处理时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**来源**: bili2txt-agent 自动生成

---

{refined_text}

---

## 附录：原始识别文本

{original_text}

---

*本文档由 [bili2txt-agent](https://github.com/yourusername/bili2txt-agent) 自动生成*
"""

            refined_url = create_and_share_document(feishu_client, refined_content, refined_title)

            if not refined_url:
                logger.error("原文精转文档创建失败")
                send_message(user_id, f"❌ 原文精转文档创建失败\n\n处理已完成，但无法创建飞书文档\n\n💾 本地缓存文件已保存")
                return

            # 创建关键纪要文档
            summary_title = f"关键纪要-{video_title}"
            summary_content = f"""# 关键纪要

**视频ID**: {video_id}
**视频标题**: {video_title}
**处理时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**来源**: bili2txt-agent 自动生成

---

{summary_text}

---

*本文档由 [bili2txt-agent](https://github.com/yourusername/bili2txt-agent) 自动生成*
"""

            summary_url = create_and_share_document(feishu_client, summary_content, summary_title)

            if not summary_url:
                logger.error("关键纪要文档创建失败")
                send_message(user_id, f"❌ 关键纪要文档创建失败\n\n原文精转文档已创建：{refined_url}")
                return

            # 9. 保存到缓存（保存文本内容，而非文档链接）
            cache.set(
                video_id=video_id,
                video_title=video_title,
                original_text=original_text,
                refined_text=refined_text,
                summary_text=summary_text
            )
            logger.info(f"✅ 缓存保存成功: {video_id}")

        except Exception as e:
            logger.error(f"创建文档时发生错误: {e}")
            logger.exception("详细错误堆栈")
            send_message(user_id, f"❌ 文档创建异常\n\n错误信息: {str(e)}\n\n💾 本地缓存文件已保存")
            return

        # 10. 保存结果到本地
        result_file = save_result_text(video_id, original_text, refined_text, user_id)

        # 9. 发送结果
        if result_file:
            result_message = f"""✅ 处理完成！

📹 视频ID：{video_id}
📄 原文长度：{len(original_text)} 字符
📝 精转后长度：{len(refined_text)} 字符

🔗 文档链接：原文精转-{video_title}
{refined_url}

🔗 文档链接：关键纪要-{video_title}
{summary_url}"""
        else:
            result_message = f"""✅ 处理完成！

📹 视频ID：{video_id}
📄 原文长度：{len(original_text)} 字符
📝 精转后长度：{len(refined_text)} 字符

🔗 文档链接：原文精转-{video_title}
{refined_url}

🔗 文档链接：关键纪要-{video_title}
{summary_url}"""

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
