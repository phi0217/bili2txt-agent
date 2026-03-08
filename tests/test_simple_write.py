#!/usr/bin/env python3
"""
简化的飞书文档写入测试
"""
import logging
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志（避免 Windows 控制台编码问题）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_write.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 导入配置
from config import config

# 导入飞书 SDK
from lark_oapi import Client
from lark_oapi.api.docx.v1 import (
    CreateDocumentRequest,
    CreateDocumentRequestBody,
    CreateDocumentBlockChildrenRequest,
    CreateDocumentBlockChildrenRequestBody
)
from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("开始测试文档内容写入")
    logger.info("=" * 60)

    # 1. 初始化客户端
    logger.info("步骤 1: 初始化飞书客户端")
    client = Client.builder() \
        .app_id(config.FEISHU_APP_ID) \
        .app_secret(config.FEISHU_APP_SECRET) \
        .build()
    logger.info("客户端初始化成功")

    # 2. 创建测试文档
    logger.info("")
    logger.info("步骤 2: 创建测试文档")
    create_request = CreateDocumentRequest.builder().request_body(
        CreateDocumentRequestBody.builder()
        .title("API 写入测试")
        .build()
    ).build()

    create_response = client.docx.v1.document.create(create_request)

    if not create_response.success():
        logger.error(f"创建文档失败: {create_response.code} {create_response.msg}")
        return 1

    document_id = create_response.data.document.document_id
    logger.info(f"文档创建成功，ID: {document_id}")

    # 3. 准备写入内容
    logger.info("")
    logger.info("步骤 3: 准备文本块结构")

    test_text = "这是通过 API 写入的测试文本。"
    logger.info(f"测试文本: {test_text}")

    # 创建正确的数据结构
    text_run = TextRun.builder().content(test_text).build()
    logger.info("TextRun 创建成功")

    text_element = TextElement.builder().text_run(text_run).build()
    logger.info("TextElement 创建成功")

    text = Text.builder().elements([text_element]).build()
    logger.info("Text 创建成功")

    block = Block.builder().block_type(2).text(text).build()
    logger.info("Block 创建成功 (block_type=2 for text)")

    # 4. 创建块子节点请求
    logger.info("")
    logger.info("步骤 4: 创建块子节点请求")

    request = CreateDocumentBlockChildrenRequest.builder() \
        .document_id(document_id) \
        .block_id(document_id) \
        .request_body(
            CreateDocumentBlockChildrenRequestBody.builder()
            .children([block])
            .index(-1)
            .build()
        ).build()

    logger.info("请求对象创建成功")

    # 5. 尝试正确的 API 调用方式
    logger.info("")
    logger.info("步骤 5: 调用 API 写入内容")
    logger.info("调用方式: client.docx.v1.document_block_children.create(request)")

    try:
        response = client.docx.v1.document_block_children.create(request)

        if response.success():
            logger.info("=" * 60)
            logger.info("成功！内容写入成功")
            logger.info("=" * 60)

            # 显示创建的块信息
            if hasattr(response.data, 'items') and response.data.items:
                logger.info(f"创建了 {len(response.data.items)} 个块")
                for i, block in enumerate(response.data.items):
                    block_id = block.block_id if hasattr(block, 'block_id') else "unknown"
                    logger.info(f"  块 {i+1}: {block_id}")

            logger.info("")
            logger.info("文档链接:")
            from doc_utils import get_document_share_url
            share_url = get_document_share_url(document_id)
            logger.info(share_url)

            return 0
        else:
            logger.error("=" * 60)
            logger.error("失败")
            logger.error("=" * 60)
            logger.error(f"错误码: {response.code}")
            logger.error(f"错误信息: {response.msg}")
            if hasattr(response, 'error') and response.error:
                logger.error(f"详细错误: {response.error}")
            return 1

    except AttributeError as e:
        logger.error(f"API 调用路径错误: {e}")
        logger.error("尝试列出可用的方法...")

        # 列出可用的方法
        logger.info("")
        logger.info("client.docx.v1 可用的属性:")
        for attr in dir(client.docx.v1):
            if not attr.startswith('_'):
                logger.info(f"  - {attr}")

        return 1

    except Exception as e:
        logger.error(f"发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
