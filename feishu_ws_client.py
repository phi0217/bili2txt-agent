"""
飞书 WebSocket 长连接客户端
处理飞书事件订阅和消息接收
使用官方推荐的 EventDispatcherHandler 方式
"""
import logging
import threading
from typing import Optional
import lark_oapi as lark
from lark_oapi import EventDispatcherHandler, ws, im, LogLevel
from config import config
from utils import logger


class FeishuWSClient:
    """飞书 WebSocket 客户端（使用官方 EventDispatcherHandler）"""

    def __init__(self):
        """初始化客户端"""
        self.client = lark.Client.builder() \
            .app_id(config.FEISHU_APP_ID) \
            .app_secret(config.FEISHU_APP_SECRET) \
            .build()

        self.ws_client = None
        self.is_running = False

        # 代理配置（从环境变量读取）
        import os
        self.http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        self.https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    def handle_p2_im_message(self, data: im.v1.P2ImMessageReceiveV1) -> None:
        """
        处理接收消息 v2.0 事件（官方推荐方式）

        Args:
            data: 飞书消息事件数据
        """
        try:
            logger.info("Received P2 IM message event")

            # 解析消息内容
            message = data.event.message
            sender_id = data.event.sender.sender_id.open_id

            # 飞书的 content 是 JSON 字符串，需要用 eval 解析
            content_dict = eval(message.content)
            text = content_dict.get("text", "").strip()

            logger.info(f"Received message - User: {sender_id}, Content: {text}")

            # 导入处理函数
            from bilibili_utils import extract_video_id
            from feishu_handler import send_message

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
            from task import process_video_sync
            thread = threading.Thread(
                target=process_video_sync,
                args=(video_id, sender_id, send_message),
                daemon=True
            )
            thread.start()

        except Exception as e:
            logger.error(f"Error handling message event: {e}")
            logger.exception("Detailed error traceback")

    def start(self) -> None:
        """启动 WebSocket 客户端（使用官方 EventDispatcherHandler 方式）"""
        try:
            logger.info("Starting Feishu WebSocket client...")

            # 显示代理配置（如果有）
            if self.http_proxy or self.https_proxy:
                logger.info(f"Using proxy - HTTP: {self.http_proxy}, HTTPS: {self.https_proxy}")

            # 1. 创建事件处理器（两个参数必须填空字符串）
            event_handler = EventDispatcherHandler.builder("", "") \
                .register_p2_im_message_receive_v1(self.handle_p2_im_message) \
                .build()

            logger.info("Event handler created successfully")

            # 2. 初始化 WebSocket 客户端
            self.ws_client = ws.Client(
                app_id=config.FEISHU_APP_ID,
                app_secret=config.FEISHU_APP_SECRET,
                event_handler=event_handler,
                log_level=LogLevel.INFO
            )

            logger.info("WebSocket client created successfully")

            # 3. 启动（阻塞）
            logger.info("Starting WebSocket connection...")
            logger.info("Press Ctrl+C to stop the service")

            self.is_running = True
            self.ws_client.start()

        except Exception as e:
            logger.error(f"Error starting WebSocket client: {e}")
            logger.exception("Detailed error traceback")

            error_msg = f"""
            ============================================================
            启动 WebSocket 客户端时发生错误！
            ============================================================

            错误类型: {type(e).__name__}
            错误信息: {e}

            请检查：
            1. 飞书应用配置（APP_ID 和 APP_SECRET 是否正确）
            2. 网络连接（是否需要配置代理）
            3. 飞书开放平台的事件订阅设置
               - 确保订阅了 'im.message.receive_v1' 事件
               - 确保创建了并发布了版本
               - 确保选择了「使用长连接接收事件」

            详细配置指南：PROXY_SETUP.md
            ============================================================
            """
            logger.error(error_msg)
            raise

    def stop(self) -> None:
        """停止客户端"""
        logger.info("Stopping WebSocket client...")
        self.is_running = False

        if self.ws_client:
            if hasattr(self.ws_client, 'close'):
                self.ws_client.close()
            elif hasattr(self.ws_client, 'stop'):
                self.ws_client.stop()

        logger.info("WebSocket client stopped")


# 全局客户端实例
_ws_client: Optional[FeishuWSClient] = None


def get_ws_client() -> FeishuWSClient:
    """
    获取 WebSocket 客户端单例

    Returns:
        WebSocket 客户端实例
    """
    global _ws_client

    if _ws_client is None:
        _ws_client = FeishuWSClient()

    return _ws_client


def start_feishu_ws() -> None:
    """启动飞书 WebSocket 服务（阻塞运行）"""
    try:
        logger.info("=" * 60)
        logger.info("Feishu WebSocket Service Starting...")
        logger.info("=" * 60)
        logger.info("")
        logger.info(f"App ID: {config.FEISHU_APP_ID}")
        logger.info(f"Temp Dir: {config.TEMP_DIR}")
        logger.info("")
        logger.info("Using EventDispatcherHandler (Official Recommended)")
        logger.info("")
        logger.info("Important: Please ensure:")
        logger.info("  1. Event subscription is configured in Feishu Open Platform")
        logger.info("  2. Subscribed to 'im.message.receive_v1' event")
        logger.info("  3. Version is created and published")
        logger.info("  4. 'Use long connection to receive events' is selected")
        logger.info("")
        logger.info("Initializing WebSocket client...")
        logger.info("")

        # 获取客户端
        client = get_ws_client()

        # 启动客户端
        client.start()

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Received stop signal, shutting down...")
        if _ws_client:
            _ws_client.stop()
        logger.info("Service stopped")
    except Exception as e:
        logger.error(f"Error in WebSocket service: {e}")
        raise
