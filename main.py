"""
bili2txt-agent - B站视频转飞书云文档机器人

采用飞书WebSocket长连接模式，接收用户发送的B站视频链接，
自动完成：视频下载 → 音频提取 → Whisper语音识别 → DeepSeek API精转 → 上传飞书云文档 → 返回分享链接
"""
import logging
from config import config
from utils import setup_logging
from feishu_ws_client import start_feishu_ws


def main():
    """程序入口"""
    try:
        # 1. 初始化日志
        logger = setup_logging()
        logger.info("=" * 60)
        logger.info("bili2txt-agent 启动中...")
        logger.info("=" * 60)

        # 2. 验证配置
        try:
            config.validate()
            logger.info("配置验证通过")
        except ValueError as e:
            logger.error(f"配置验证失败: {e}")
            return

        # 3. 确保临时目录存在
        config.ensure_temp_dir()
        logger.info(f"临时目录: {config.TEMP_DIR}")

        # 4. 启动飞书 WebSocket 客户端
        logger.info("正在启动飞书 WebSocket 客户端...")
        logger.info("提示：请确保已在飞书开放平台配置好应用权限和事件订阅")
        start_feishu_ws()

    except KeyboardInterrupt:
        logger.info("收到退出信号，程序正在关闭...")
    except Exception as e:
        logger.error(f"程序运行时发生错误: {e}")
        raise
    finally:
        logger.info("bili2txt-agent 已停止")


if __name__ == "__main__":
    main()
