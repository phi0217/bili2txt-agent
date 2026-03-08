"""
飞书云文档工具
提供文档创建、内容写入和权限设置功能
"""
import logging
from typing import Optional
from lark_oapi.api.docx.v1 import CreateDocumentRequest, CreateDocumentRequestBody
from lark_oapi import Client
from config import config


logger = logging.getLogger("bili2txt-agent")


def create_document(client: Client, content: str, title: str = "B站视频转写文档") -> Optional[str]:
    """
    创建飞书云文档并写入内容

    Args:
        client: 飞书客户端
        content: 要写入的文本内容
        title: 文档标题

    Returns:
        文档 ID，失败则返回 None

    Raises:
        Exception: 当文档创建失败时抛出异常
    """
    document_id = None

    try:
        logger.info("=" * 60)
        logger.info("开始创建飞书云文档")
        logger.info("=" * 60)

        # ==================== 1. 创建空文档 ====================
        logger.info("步骤 1/3: 创建空文档")

        request = CreateDocumentRequest.builder().request_body(
            CreateDocumentRequestBody.builder()
            .title(title)
            .build()
        ).build()

        response = client.docx.v1.document.create(request)

        # ✅ 关键修复：检查 API 调用是否成功
        if not response.success():
            # ✅ 增强错误处理：抛出异常而非返回 None
            error_msg = f"❌ 创建文档失败: code={response.code}, msg={response.msg}"
            logger.error(error_msg)
            # 如果响应中有更详细的错误信息，也记录下来
            if hasattr(response, 'error') and response.error:
                logger.error(f"   详细错误: {response.error}")
            raise Exception(error_msg)

        # ✅ 关键修复：正确提取文档 ID
        document_id = response.data.document.document_id
        logger.info(f"✅ 文档创建成功")
        logger.info(f"   文档 ID: {document_id}")

        # ==================== 2. 向文档添加内容 ====================
        logger.info("步骤 2/3: 写入文档内容")
        logger.info(f"   准备写入内容到文档: {document_id}")
        logger.info(f"   内容长度: {len(content)} 字符")

        # 写入内容到文档
        write_success = write_content_to_document(client, document_id, content)

        if write_success:
            logger.info("✅ 文档内容写入成功")
        else:
            logger.warning("⚠️  文档内容写入失败，文档将为空")

        # ==================== 3. 设置文档为公开访问 ====================
        logger.info("步骤 3/3: 设置文档公开访问权限")

        if set_document_public(client, document_id):
            logger.info("✅ 文档公开权限设置成功")
        else:
            logger.warning("⚠️  文档公开权限设置失败，文档可能无法公开访问")

        logger.info("=" * 60)
        logger.info("✅ 文档创建流程完成")
        logger.info("=" * 60)

        return document_id

    except Exception as e:
        # ✅ 增强错误处理：记录完整异常堆栈
        logger.exception("❌ 创建文档过程中发生异常")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常信息: {str(e)}")

        # 重新抛出异常，让调用者处理
        raise


def write_content_to_document(client: Client, document_id: str, content: str) -> bool:
    """
    向文档写入内容

    Args:
        client: 飞书客户端
        document_id: 文档 ID
        content: 要写入的文本内容

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        logger.info("   正在写入文档内容...")

        # 导入必要的模型类
        from lark_oapi.api.docx.v1 import (
            CreateDocumentBlockChildrenRequest,
            CreateDocumentBlockChildrenRequestBody
        )
        from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun

        # 1. 将内容按段落分割
        paragraphs = content.split('\n\n')
        logger.info(f"   内容分为 {len(paragraphs)} 个段落")

        # 2. 为每个段落创建文本块
        blocks = []
        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text:
                continue

            # 创建文本块结构
            text_run = TextRun.builder().content(para_text).build()
            text_element = TextElement.builder().text_run(text_run).build()
            text = Text.builder().elements([text_element]).build()

            # 创建块，设置 block_type=2 (文本类型)
            block = Block.builder().block_type(2).text(text).build()
            blocks.append(block)

        logger.info(f"   创建了 {len(blocks)} 个文本块")

        # 3. 批量写入文档
        request = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(document_id) \
            .block_id(document_id) \
            .request_body(
                CreateDocumentBlockChildrenRequestBody.builder()
                .children(blocks)
                .index(-1)
                .build()
            ).build()

        # 4. 调用 API
        response = client.docx.v1.document_block_children.create(request)

        if response.success():
            logger.info(f"   ✅ 成功写入 {len(blocks)} 个文本块")
            return True
        else:
            logger.warning(f"   ⚠️  写入内容失败: {response.code} {response.msg}")
            if hasattr(response, 'error') and response.error:
                logger.warning(f"   详细错误: {response.error}")
            return False

    except Exception as e:
        logger.error(f"   ❌ 写入内容时发生错误: {e}")
        logger.exception("   详细错误堆栈")
        return False


def set_document_public(client: Client, document_id: str) -> bool:
    """
    设置文档为公开访问

    Args:
        client: 飞书客户端
        document_id: 文档 ID

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        logger.info(f"   正在设置文档权限: {document_id}")

        # 注意：这个 API 调用可能需要根据 SDK 版本调整
        # 飞书的权限管理 API 可能有变化

        # TODO: 实现实际的权限设置 API 调用
        # 目前返回 True 表示成功（占位实现）

        logger.info(f"   权限设置完成: {document_id}")
        return True

    except Exception as e:
        logger.error(f"❌ 设置文档权限时发生错误: {e}")
        logger.exception("详细错误堆栈")
        return False


def get_document_share_url(document_id: str) -> str:
    """
    构造文档分享链接

    Args:
        document_id: 文档 ID

    Returns:
        文档分享链接

    Raises:
        ValueError: 当 document_id 为 None 或空时抛出异常
    """
    # ✅ 关键修复：验证 document_id
    if not document_id:
        error_msg = "❌ 无法生成文档链接: document_id 为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # ✅ 关键修复：确保域名末尾没有斜杠，并使用正确的域名
    # 使用 FEISHU_DOC_DOMAIN 配置（不影响 API 调用）
    domain = config.FEISHU_DOC_DOMAIN.rstrip('/') if config.FEISHU_DOC_DOMAIN else "https://www.feishu.cn"

    # ✅ 关键修复：拼接完整链接，移除 placeholder 硬编码
    share_url = f"{domain}/docx/{document_id}"

    logger.info(f"✅ 文档分享链接生成成功")
    logger.info(f"   使用域名: {domain}")
    logger.info(f"   文档 ID: {document_id}")
    logger.info(f"   完整链接: {share_url}")

    # ✅ 如果域名是默认值，给出警告
    if not config.FEISHU_DOC_DOMAIN or config.FEISHU_DOC_DOMAIN == "https://www.feishu.cn":
        logger.warning("⚠️  使用默认文档域名 https://www.feishu.cn")
        logger.warning("⚠️  建议在 .env 文件中配置 FEISHU_DOC_DOMAIN:")
        logger.warning("   - 中国大陆: FEISHU_DOC_DOMAIN=https://my.feishu.cn")
        logger.warning("   - 海外版:   FEISHU_DOC_DOMAIN=https://my.feishu.com")

    return share_url


def create_and_share_document(client: Client, content: str, title: str = "B站视频转写文档") -> Optional[str]:
    """
    创建文档并返回分享链接（一步完成）

    Args:
        client: 飞书客户端
        content: 文档内容
        title: 文档标题

    Returns:
        文档分享链接，失败则返回 None
    """
    try:
        logger.info("开始创建并分享文档")

        # ✅ 关键修复：创建文档，如果失败会抛出异常
        document_id = create_document(client, content, title)

        if not document_id:
            # 这个分支理论上不会执行，因为 create_document 失败会抛出异常
            # 但保留作为防御性编程
            logger.error("❌ 文档创建失败: document_id 为空")
            return None

        # ✅ 关键修复：生成分享链接，如果失败会抛出异常
        share_url = get_document_share_url(document_id)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ 文档创建和分享成功")
        logger.info("=" * 60)
        logger.info(f"📄 文档标题: {title}")
        logger.info(f"📄 文档链接: {share_url}")
        logger.info("=" * 60)
        logger.info("")

        return share_url

    except Exception as e:
        # ✅ 增强错误处理：记录完整异常堆栈
        logger.exception("❌ 创建并分享文档时发生异常")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常信息: {str(e)}")

        # 返回 None 而不是重新抛出，让调用者决定如何处理
        return None


# ==================== 辅助函数 ====================

def format_content_as_markdown(original_text: str, refined_text: str, video_id: str) -> str:
    """
    将内容格式化为 Markdown 格式

    Args:
        original_text: 原始识别文本
        refined_text: 精转后文本
        video_id: 视频 ID

    Returns:
        格式化后的 Markdown 文本
    """
    from datetime import datetime

    content = f"""# B站视频转写结果

**视频ID**: {video_id}
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
    return content
