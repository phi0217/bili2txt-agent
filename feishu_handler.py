"""
飞书消息处理模块
处理飞书事件回调、消息发送和客户端管理
"""
import asyncio
import logging
from typing import Optional
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody, MessageReceiveEventHandler
from lark_oapi.api.ws.v1 import WebSocketClient, HandshakeRequestBuilder, HandshakeRequestBody
from lark_oapi import Client, JSON
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

        request = CreateMessageRequest.builder().request_body(
            CreateMessageRequestBody.builder()
            .receive_id(user_id)
            .msg_type("text")
            .content(JSON.dumps({"text": text}))
            .build()
        ).build()

        response = client.im.v1.message.create(request)

        if not response.success():
            logger.error(f"发送消息失败: {response.code} {response.msg}")
        else:
            logger.info(f"消息发送成功: {user_id}")

    except Exception as e:
        logger.error(f"发送消息时发生错误: {e}")


async def send_message_async(user_id: str, text: str) -> None:
    """
    发送文本消息给指定用户（异步版本）

    Args:
        user_id: 飞书用户 open_id
        text: 消息文本
    """
    # 在线程中执行同步的发送操作
    await asyncio.to_thread(send_message, user_id, text)


def send_document_link(user_id: str, doc_url: str) -> None:
    """
    发送文档链接给指定用户

    Args:
        user_id: 飞书用户 open_id
        doc_url: 文档链接
    """
    message = f"📄 文档链接：{doc_url}"
    send_message(user_id, message)


async def send_document_link_async(user_id: str, doc_url: str) -> None:
    """
    发送文档链接给指定用户（异步版本）

    Args:
        user_id: 飞书用户 open_id
        doc_url: 文档链接
    """
    await send_message_async(user_id, f"📄 文档链接：{doc_url}")


def handle_message_event(event) -> None:
    """
    处理消息接收事件

    Args:
        event: 飞书消息事件
    """
    try:
        # 解析事件
        event_data = event.event

        # 获取发送者信息
        sender_id = event_data.sender.sender_id.open_id

        # 获取消息内容
        message_content = event_data.message.content

        # 解析消息文本
        import json
        content_dict = json.loads(message_content)
        text = content_dict.get("text", "").strip()

        logger.info(f"收到消息 - 用户: {sender_id}, 内容: {text}")

        # 提取视频 ID
        video_id = extract_video_id(text)

        if not video_id:
            # 未识别到视频 ID，发送错误提示
            send_message(sender_id, "❌ 无法识别视频ID，请发送正确的B站链接或AV/BV号")
            return

        # 识别到视频 ID，启动后台任务处理
        logger.info(f"识别到视频ID: {video_id}，启动后台任务处理")

        # 在新线程中处理视频（避免阻塞事件循环）
        import threading
        thread = threading.Thread(
            target=process_video_sync,
            args=(video_id, sender_id, send_message),
            daemon=True
        )
        thread.start()

    except Exception as e:
        logger.error(f"处理消息事件时发生错误: {e}")


def create_ws_client() -> WebSocketClient:
    """
    创建飞书 WebSocket 客户端

    Returns:
        WebSocket 客户端实例
    """
    try:
        logger.info("正在创建飞书 WebSocket 客户端...")

        # 创建 WebSocket 客户端
        client = WebSocketClient(
            app_id=config.FEISHU_APP_ID,
            app_secret=config.FEISHU_APP_SECRET
        )

        # 注册事件处理器
        client.set_message_receive_handler(handle_message_event)

        logger.info("飞书 WebSocket 客户端创建成功")
        return client

    except Exception as e:
        logger.error(f"创建 WebSocket 客户端时发生错误: {e}")
        raise


def start_ws_client() -> None:
    """
    启动飞书 WebSocket 客户端（阻塞运行）
    """
    try:
        logger.info("正在启动飞书 WebSocket 客户端...")

        client = create_ws_client()

        # 启动客户端（阻塞运行）
        client.start()

    except Exception as e:
        logger.error(f"启动 WebSocket 客户端时发生错误: {e}")
        raise


async def start_ws_client_async() -> None:
    """
    启动飞书 WebSocket 客户端（异步版本）
    """
    # 在线程中运行同步的客户端启动
    await asyncio.to_thread(start_ws_client)
