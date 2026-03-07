"""
飞书消息处理模块
处理飞书事件回调、消息发送和客户端管理
"""
import asyncio
import logging
import json
import threading
import time
from typing import Optional
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody
from lark_oapi import Client
from bilibili_utils import extract_video_id
from task import process_video_sync
from config import config
from utils import logger


# 飞书客户端单例
_feishu_client: Optional[Client] = None


def get_feishu_client() -> Client:
    """
    获取飞书客户端单例

    Returns:
        飞书客户端实例
    """
    global _feishu_client

    if _feishu_client is None:
        _feishu_client = Client.builder() \
            .app_id(config.FEISHU_APP_ID) \
            .app_secret(config.FEISHU_APP_SECRET) \
            .build()

    return _feishu_client


def send_message(user_id: str, text: str) -> None:
    """
    发送文本消息给指定用户

    Args:
        user_id: 飞书用户 open_id
        text: 消息文本
    """
    try:
        client = get_feishu_client()

        request = CreateMessageRequest.builder() \
            .receive_id_type("open_id") \
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(user_id)
                .msg_type("text")
                .content(json.dumps({"text": text}))
                .build()
        ).build()

        response = client.im.v1.message.create(request)

        if not response.success():
            logger.error(f"Failed to send message: {response.code} {response.msg}")
        else:
            logger.info(f"Message sent successfully to {user_id}")

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        logger.exception("Detailed error traceback")


def handle_message_event(event_data) -> None:
    """
    处理消息接收事件

    Args:
        event_data: 飞书消息事件数据
    """
    try:
        if not event_data:
            logger.warning("Received empty event data")
            return

        # 获取发送者信息
        sender_id = event_data.sender.sender_id.open_id

        # 获取消息内容
        message_content = event_data.message.content

        # 解析消息文本
        content_dict = json.loads(message_content)
        text = content_dict.get("text", "").strip()

        logger.info(f"Received message - User: {sender_id}, Content: {text}")

        # 提取视频 ID
        video_id = extract_video_id(text)

        if not video_id:
            # 未识别到视频 ID，发送错误提示
            send_message(sender_id, "❌ 无法识别视频 ID，请发送有效的 B站视频链接或 AV/BV 号")
            return

        # 识别到视频 ID，立即回复收到
        logger.info(f"Recognized video ID: {video_id}")
        send_message(sender_id, f"✅ 已收到：{video_id}\n📥 开始下载视频...")

        # 启动后台任务处理
        logger.info(f"Starting background task for video: {video_id}")

        # 在新线程中处理视频（避免阻塞事件循环）
        thread = threading.Thread(
            target=process_video_sync,
            args=(video_id, sender_id, send_message),
            daemon=True
        )
        thread.start()

    except Exception as e:
        logger.error(f"Error handling message event: {e}")
        # 尝试发送错误消息
        try:
            if event_data and hasattr(event_data, 'sender'):
                sender_id = event_data.sender.sender_id.open_id
                send_message(sender_id, f"❌ 处理消息时发生错误：{str(e)}")
        except:
            pass


def start_ws_client() -> None:
    """
    启动飞书服务（简化版本）
    注意：由于飞书 SDK 的 WebSocket 实现可能需要特定版本，
    这里提供一个基础框架，实际使用时需要根据 SDK 文档完善
    """
    try:
        logger.info("Starting Feishu service...")
        logger.info("=" * 60)
        logger.info("bili2txt-agent is now running!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("IMPORTANT NOTES:")
        logger.info("1. This is a simplified implementation")
        logger.info("2. WebSocket client needs to be implemented based on actual Feishu SDK")
        logger.info("3. For testing, you can use manual message sending")
        logger.info("4. Please check Feishu SDK documentation for WebSocket implementation")
        logger.info("")
        logger.info("Current status: Service is running in standby mode")
        logger.info("Press Ctrl+C to stop the service")
        logger.info("=" * 60)
        logger.info("")

        # 保持服务运行
        while True:
            time.sleep(10)
            logger.debug("Service is running...")

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Error starting service: {e}")
        raise


# 测试函数：手动发送消息测试
def test_send_message():
    """测试发送消息功能"""
    logger.info("Testing send_message function...")

    # 这个函数可以用于测试消息发送功能
    # 需要提供一个真实的 user_id
    test_user_id = "test_user_id"
    test_message = "Hello from bili2txt-agent!"

    logger.info(f"Sending test message to {test_user_id}")
    send_message(test_user_id, test_message)


# 使用说明
def print_usage_instructions():
    """打印使用说明"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("USAGE INSTRUCTIONS")
    logger.info("=" * 60)
    logger.info("")
    logger.info("To complete the setup:")
    logger.info("")
    logger.info("1. Install FFmpeg:")
    logger.info("   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/")
    logger.info("   - Add to PATH")
    logger.info("   - Verify: ffmpeg -version")
    logger.info("")
    logger.info("2. Configure Feishu App:")
    logger.info("   - Create app at https://open.feishu.cn/")
    logger.info("   - Enable bot capability")
    logger.info("   - Configure event subscription")
    logger.info("   - Set up permissions")
    logger.info("")
    logger.info("3. Test the service:")
    logger.info("   - Start this service")
    logger.info("   - Send message to your Feishu bot")
    logger.info("   - Service should process Bilibili video links")
    logger.info("")
    logger.info("=" * 60)
