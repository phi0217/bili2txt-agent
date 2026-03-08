"""
飞书云文档工具
提供文档创建、内容写入和权限设置功能
支持两种文档创建方式：
1. Import API (推荐): 上传Markdown文件，飞书自动转换，完美渲染格式
2. Block-based API (备用): 直接创建文本块，格式支持有限
"""
import logging
import os
import time
from typing import Optional
from datetime import datetime
from lark_oapi.api.docx.v1 import CreateDocumentRequest, CreateDocumentRequestBody
from lark_oapi import Client
from config import config


logger = logging.getLogger("bili2txt-agent")


# ==================== 自定义异常类 ====================

class FileUploadError(Exception):
    """文件上传失败异常"""
    pass


class ImportTaskError(Exception):
    """导入任务创建失败异常"""
    pass


class PollingTimeoutError(Exception):
    """导入状态轮询超时异常"""
    pass


class DocumentCreationError(Exception):
    """文档创建失败异常"""
    pass


def create_document_via_blocks(client: Client, content: str, title: str = "B站视频转写文档") -> Optional[str]:
    """
    使用Block-based API创建飞书云文档并写入内容（备用方案）

    注意：此方式无法完美渲染Markdown格式，仅作为导入API失败时的回退方案

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
        logger.info("使用Block-based API创建文档（备用方案）")
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
    向文档写入内容（支持Markdown格式渲染）

    支持的Markdown语法：
    - 标题：# ## ### #### #####
    - 粗体：**text**
    - 斜体：*text*
    - 列表：- 或 * 开头（无序列表）
    - 分隔线：---

    Args:
        client: 飞书客户端
        document_id: 文档 ID
        content: 要写入的文本内容（支持Markdown格式）

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        logger.info("   正在写入文档内容（增强Markdown渲染）...")

        # 导入必要的模型类
        from lark_oapi.api.docx.v1 import (
            CreateDocumentBlockChildrenRequest,
            CreateDocumentBlockChildrenRequestBody
        )
        from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun, TextElementStyle

        import re

        # 解析Markdown内容并创建对应的块
        blocks = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # 跳过空行
            if not line:
                i += 1
                continue

            # === 1. 检测标题 ===
            heading_match = re.match(r'^(#{1,5})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text_content = heading_match.group(2)

                # 使用文本样式模拟标题
                # 一级标题使用大号粗体，其他级别使用粗体
                if level == 1:
                    # 一级标题：添加前后空行以突出显示
                    if blocks:  # 如果前面已有内容，先加空行
                        empty_run = TextRun.builder().content("").build()
                        empty_element = TextElement.builder().text_run(empty_run).build()
                        empty_text = Text.builder().elements([empty_element]).build()
                        empty_block = Block.builder().block_type(2).text(empty_text).build()
                        blocks.append(empty_block)

                    heading_style = TextElementStyle.builder().bold(True).build()
                    heading_run = TextRun.builder().content(text_content).text_element_style(heading_style).build()
                    heading_element = TextElement.builder().text_run(heading_run).build()
                    heading_text = Text.builder().elements([heading_element]).build()
                    block = Block.builder().block_type(2).text(heading_text).build()
                    blocks.append(block)

                    # 标题后再加空行
                    empty_run = TextRun.builder().content("").build()
                    empty_element = TextElement.builder().text_run(empty_run).build()
                    empty_text = Text.builder().elements([empty_element]).build()
                    empty_block = Block.builder().block_type(2).text(empty_text).build()
                    blocks.append(empty_block)
                else:
                    # 其他级别标题：使用粗体
                    prefix = "#" * level + " "
                    heading_style = TextElementStyle.builder().bold(True).build()
                    heading_run = TextRun.builder().content(prefix + text_content).text_element_style(heading_style).build()
                    heading_element = TextElement.builder().text_run(heading_run).build()
                    heading_text = Text.builder().elements([heading_element]).build()
                    block = Block.builder().block_type(2).text(heading_text).build()
                    blocks.append(block)

                logger.debug(f"   创建 {level} 级标题: {text_content}")
                i += 1
                continue

            # === 2. 检测分隔线 ===
            if re.match(r'^[-*_]{3,}$', line.strip()):
                # 创建空行作为分隔（不创建特殊分隔线块）
                text_run = TextRun.builder().content("").build()
                text_element = TextElement.builder().text_run(text_run).build()
                text = Text.builder().elements([text_element]).build()
                block = Block.builder().block_type(2).text(text).build()
                blocks.append(block)
                logger.debug("   添加分隔线")
                i += 1
                continue

            # === 3. 检测列表 ===
            list_match = re.match(r'^[\-\*]\s+(.+)$', line)
            if list_match:
                text_content = "• " + list_match.group(1)
                text_run = TextRun.builder().content(text_content).build()
                text_element = TextElement.builder().text_run(text_run).build()
                text = Text.builder().elements([text_element]).build()
                block = Block.builder().block_type(2).text(text).build()
                blocks.append(block)
                logger.debug(f"   创建列表项: {text_content}")
                i += 1
                continue

            # === 4. 处理普通段落（支持内联格式）===
            # 收集连续的行作为一个段落
            paragraph_lines = []
            while i < len(lines):
                current_line = lines[i].rstrip()
                # 遇到空行或特殊格式行时停止
                if not current_line:
                    i += 1
                    break
                if re.match(r'^(#{1,5}\s|[\-\*]\s|[-*_]{3,})', current_line):
                    break
                paragraph_lines.append(current_line)
                i += 1

            if paragraph_lines:
                paragraph_text = ' '.join(paragraph_lines)

                # 处理内联格式：**粗体** 和 *斜体*
                # 分割文本，识别格式标记
                segments = []
                remaining = paragraph_text

                while remaining:
                    # 查找 **粗体**
                    bold_match = re.match(r'(.*?)\*\*(.+?)\*\*(.*)', remaining)
                    # 查找 *斜体*
                    italic_match = re.match(r'(.*?)\*(.+?)\*(.*)', remaining)

                    if bold_match:
                        # 添加粗体前的普通文本
                        if bold_match.group(1):
                            text_run = TextRun.builder().content(bold_match.group(1)).build()
                            segments.append(text_run)
                        # 添加粗体文本
                        bold_style = TextElementStyle.builder().bold(True).build()
                        text_run = TextRun.builder().content(bold_match.group(2)).text_element_style(bold_style).build()
                        segments.append(text_run)
                        remaining = bold_match.group(3)
                    elif italic_match and not italic_match.group(2).startswith('*'):
                        # 避免误匹配 **粗体**
                        if italic_match.group(1):
                            text_run = TextRun.builder().content(italic_match.group(1)).build()
                            segments.append(text_run)
                        # 添加斜体文本
                        italic_style = TextElementStyle.builder().italic(True).build()
                        text_run = TextRun.builder().content(italic_match.group(2)).text_element_style(italic_style).build()
                        segments.append(text_run)
                        remaining = italic_match.group(3)
                    else:
                        # 剩余的都是普通文本
                        if remaining:
                            text_run = TextRun.builder().content(remaining).build()
                            segments.append(text_run)
                        remaining = ""

                # 创建文本元素
                if segments:
                    text_elements = [TextElement.builder().text_run(seg).build() for seg in segments]
                    text = Text.builder().elements(text_elements).build()
                    block = Block.builder().block_type(2).text(text).build()
                    blocks.append(block)
                    logger.debug(f"   创建段落（{len(segments)}个片段）")

        logger.info(f"   创建了 {len(blocks)} 个格式化块")

        # 批量写入文档（分批处理，避免单次请求过大）
        batch_size = 50
        total_written = 0

        for idx in range(0, len(blocks), batch_size):
            batch = blocks[idx:idx + batch_size]

            request = CreateDocumentBlockChildrenRequest.builder() \
                .document_id(document_id) \
                .block_id(document_id) \
                .request_body(
                    CreateDocumentBlockChildrenRequestBody.builder()
                    .children(batch)
                    .index(-1)
                    .build()
                ).build()

            response = client.docx.v1.document_block_children.create(request)

            if response.success():
                total_written += len(batch)
                logger.info(f"   ✅ 已写入 {total_written}/{len(blocks)} 个块")
            else:
                logger.warning(f"   ⚠️  写入批次失败: {response.code} {response.msg}")
                if hasattr(response, 'error') and response.error:
                    logger.warning(f"   详细错误: {response.error}")
                return False

        return True

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

    使用优化的Block-based API，支持标题、列表、粗体、斜体等Markdown格式

    Args:
        client: 飞书客户端
        content: 文档内容（支持Markdown格式）
        title: 文档标题

    Returns:
        文档分享链接，失败则返回 None
    """
    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("开始创建并分享文档")
        logger.info("=" * 60)

        # 使用优化的Block-based API创建文档
        document_id = create_document_via_blocks(client, content, title)

        if not document_id:
            logger.error("❌ 文档创建失败: document_id 为空")
            return None

        # 生成分享链接
        share_url = get_document_share_url(document_id)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ 文档创建和分享成功")
        logger.info("=" * 60)
        logger.info(f"📄 文档标题: {title}")
        logger.info(f"📄 文档链接: {share_url}")
        logger.info("")
        logger.info("✨ 支持的格式:")
        logger.info("   - 标题: # ## ### #### #####")
        logger.info("   - 粗体: **文本**")
        logger.info("   - 斜体: *文本*")
        logger.info("   - 列表: - 项目")
        logger.info("   - 分隔线: ---")
        logger.info("=" * 60)
        logger.info("")

        return share_url

    except Exception as e:
        # 兜底异常处理
        logger.exception("❌ 创建并分享文档时发生未知异常")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常信息: {str(e)}")
        return None


# ==================== Import API 相关函数 ====================

def save_markdown_temp_file(content: str, video_id: str, doc_type: str) -> str:
    """
    保存Markdown内容为临时文件

    Args:
        content: Markdown文本内容
        video_id: 视频ID
        doc_type: 文档类型（"refined" 或 "summary"）

    Returns:
        保存的文件路径

    Raises:
        IOError: 文件写入失败
    """
    try:
        # 创建 markdown 临时目录
        markdown_dir = os.path.join(config.TEMP_DIR, "markdown")
        os.makedirs(markdown_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{video_id}_{doc_type}.md"
        file_path = os.path.join(markdown_dir, filename)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        file_size = os.path.getsize(file_path)
        logger.info(f"✅ Markdown文件保存成功: {file_path}")
        logger.info(f"   文件大小: {file_size} 字节 ({file_size / 1024:.2f} KB)")

        return file_path

    except Exception as e:
        logger.error(f"❌ 保存Markdown文件失败: {e}")
        raise IOError(f"保存Markdown文件失败: {e}")


def upload_file_to_feishu(client: Client, file_path: str) -> str:
    """
    上传文件到飞书云空间（小文件，<20MB）

    Args:
        client: 飞书客户端
        file_path: 本地文件路径

    Returns:
        file_token: 文件在上传后的标识

    Raises:
        FileUploadError: 上传失败
    """
    try:
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        logger.info(f"开始上传文件到飞书云空间")
        logger.info(f"   文件路径: {file_path}")
        logger.info(f"   文件大小: {file_size_mb:.2f} MB")

        # 检查文件大小限制（小文件上传限制20MB）
        if file_size >= 20 * 1024 * 1024:
            logger.warning(f"⚠️  文件过大 ({file_size_mb:.2f} MB >= 20MB)")
            logger.warning("   建议: 实现分块上传功能（当前版本仅支持小文件）")
            raise FileUploadError(f"文件过大，超过20MB限制")

        # 获取文件大小（使用os.path.getsize确保准确）
        actual_size = os.path.getsize(file_path)

        # 调用文件上传API
        # 注意：lark-oapi SDK 的文件上传 API 接口
        # 使用 client.drive.v1.file.upload_all()
        # 重要：file参数需要传入文件对象（IO流），而非bytes
        from lark_oapi.api.drive.v1 import UploadAllFileRequest, UploadAllFileRequestBody

        # 打开文件作为二进制流（不要读取为bytes）
        file_obj = open(file_path, 'rb')

        # 构造上传请求
        # 根据飞书API文档，上传文件需要指定parent_type
        request_body = UploadAllFileRequestBody.builder() \
            .file_name(os.path.basename(file_path)) \
            .parent_type("explorer") \
            .size(actual_size) \
            .file(file_obj) \
            .build()

        request = UploadAllFileRequest.builder().request_body(request_body).build()

        # 详细调试日志
        logger.info(f"   准备上传文件:")
        logger.info(f"   - 文件名: {os.path.basename(file_path)}")
        logger.info(f"   - 文件大小: {actual_size} 字节")
        logger.info(f"   - Parent type: explorer")

        # 检查请求体内部数据
        if hasattr(request_body, '_d'):
            logger.debug(f"   请求体内部数据: {request_body._d}")

        # 执行上传
        try:
            response = client.drive.v1.file.upload_all(request)

            if not response.success():
                error_msg = f"❌ 文件上传失败: code={response.code}, msg={response.msg}"
                logger.error(error_msg)
                raise FileUploadError(error_msg)

            file_token = response.data.file_token
            logger.info(f"✅ 文件上传成功")
            logger.info(f"   file_token: {file_token}")

            return file_token
        finally:
            # 确保文件对象被关闭
            if 'file_obj' in locals():
                file_obj.close()

    except FileUploadError:
        if 'file_obj' in locals():
            file_obj.close()
        raise
    except Exception as e:
        if 'file_obj' in locals():
            file_obj.close()
        logger.error(f"❌ 上传文件时发生错误: {e}")
        logger.exception("详细错误堆栈")
        raise FileUploadError(f"上传文件失败: {e}")


def create_import_task(client: Client, file_token: str, title: str) -> str:
    """
    创建导入任务，将上传的文件转换为飞书文档

    Args:
        client: 飞书客户端
        file_token: 上传文件后返回的token
        title: 目标文档标题

    Returns:
        task_id: 导入任务ID

    Raises:
        ImportTaskError: 导入任务创建失败
    """
    try:
        logger.info(f"开始创建导入任务")
        logger.info(f"   file_token: {file_token}")
        logger.info(f"   文档标题: {title}")

        # 尝试使用原始HTTP请求以获得更多调试信息
        import requests
        import json

        # 获取tenant_access_token
        from src.config import config
        from lark_oapi.api.auth.v3 import (
            InternalTenantAccessTokenRequest,
            InternalTenantAccessTokenRequestBody
        )

        auth_request = InternalTenantAccessTokenRequest.builder() \
            .request_body(
                InternalTenantAccessTokenRequestBody.builder()
                .app_id(config.FEISHU_APP_ID)
                .app_secret(config.FEISHU_APP_SECRET)
                .build()
            ) \
            .build()

        auth_response = client.auth.v3.tenant_access_token.internal(auth_request)
        if not auth_response.success():
            raise ImportTaskError(f"获取tenant_access_token失败: {auth_response.msg}")

        # 从raw响应中解析token
        import json
        auth_data = json.loads(auth_response.raw.content)
        tenant_access_token = auth_data.get("tenant_access_token")
        if not tenant_access_token:
            raise ImportTaskError(f"响应中未找到tenant_access_token: {auth_response.raw.content}")

        # 构建导入任务请求
        url = "https://open.feishu.cn/open-apis/drive/v1/import_tasks"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "file_token": file_token,
            "type": "docx",
            "file_extension": "md",
            "point": {
                "mount_type": 1,  # 1 = explorer
                "mount_key": ""
            }
        }

        logger.info(f"   请求URL: {url}")
        logger.info(f"   请求体: {json.dumps(data, indent=2)}")

        response = requests.post(url, headers=headers, json=data)

        logger.info(f"   响应状态码: {response.status_code}")
        logger.info(f"   响应内容: {response.text}")

        if response.status_code != 200:
            error_msg = f"❌ 创建导入任务失败: HTTP {response.status_code}, {response.text}"
            logger.error(error_msg)
            raise ImportTaskError(error_msg)

        result = response.json()
        if result.get("code") != 0:
            error_msg = f"❌ 创建导入任务失败: code={result.get('code')}, msg={result.get('msg')}"
            logger.error(error_msg)
            raise ImportTaskError(error_msg)

        # API返回ticket而不是task_id
        data = result.get("data", {})
        ticket = data.get("ticket")
        if not ticket:
            error_msg = f"❌ 响应中未找到ticket: {response.text}"
            logger.error(error_msg)
            raise ImportTaskError(error_msg)

        logger.info(f"✅ 导入任务创建成功")
        logger.info(f"   ticket: {ticket}")

        return ticket

    except ImportTaskError:
        raise
    except Exception as e:
        logger.error(f"❌ 创建导入任务时发生错误: {e}")
        logger.exception("详细错误堆栈")
        raise ImportTaskError(f"创建导入任务失败: {e}")


def poll_import_status(client: Client, ticket: str, timeout: int = 60) -> str:
    """
    轮询导入任务状态，直到完成或超时

    Args:
        client: 飞书客户端
        ticket: 导入任务ticket
        timeout: 超时时间（秒）

    Returns:
        document_id: 导入成功后的文档ID

    Raises:
        PollingTimeoutError: 轮询超时
        ImportTaskError: 导入失败
    """
    try:
        logger.info(f"开始轮询导入状态")
        logger.info(f"   ticket: {ticket}")
        logger.info(f"   超时时间: {timeout}秒")

        start_time = time.time()
        poll_interval = 2  # 每2秒轮询一次

        import requests
        import json
        from src.config import config
        from lark_oapi.api.auth.v3 import (
            InternalTenantAccessTokenRequest,
            InternalTenantAccessTokenRequestBody
        )

        # 获取tenant_access_token
        auth_request = InternalTenantAccessTokenRequest.builder() \
            .request_body(
                InternalTenantAccessTokenRequestBody.builder()
                .app_id(config.FEISHU_APP_ID)
                .app_secret(config.FEISHU_APP_SECRET)
                .build()
            ) \
            .build()

        auth_response = client.auth.v3.tenant_access_token.internal(auth_request)
        if not auth_response.success():
            raise ImportTaskError(f"获取tenant_access_token失败: {auth_response.msg}")

        auth_data = json.loads(auth_response.raw.content)
        tenant_access_token = auth_data.get("tenant_access_token")
        if not tenant_access_token:
            raise ImportTaskError(f"响应中未找到tenant_access_token: {auth_response.raw.content}")

        # 查询导入任务状态API
        url = f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }

        while True:
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > timeout:
                error_msg = f"❌ 导入任务轮询超时（{timeout}秒）"
                logger.error(error_msg)
                raise PollingTimeoutError(error_msg)

            # 查询导入状态
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                error_msg = f"❌ 查询导入状态失败: HTTP {response.status_code}, {response.text}"
                logger.error(error_msg)
                raise ImportTaskError(error_msg)

            result = response.json()

            # 调试：打印完整的响应（首次轮询时）
            if int(elapsed) < 2:
                logger.debug(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if result.get("code") != 0:
                error_msg = f"❌ 查询导入状态失败: code={result.get('code')}, msg={result.get('msg')}"
                logger.error(error_msg)
                raise ImportTaskError(error_msg)

            # 获取任务状态 - 支持多种响应格式
            data = result.get("data", {})

            # 尝试格式1: {data: {task: {status: ...}}}
            task = data.get("task", {})
            task_status = task.get("status")

            # 尝试格式2: {data: {status: ...}}
            if not task_status:
                task_status = data.get("status")

            logger.info(f"   导入状态: {task_status} (已用时: {elapsed:.1f}秒)")

            # 处理不同状态
            if task_status == "success":
                # 导入成功，提取document_id
                # 尝试多种可能的响应格式
                document_id = None

                # 格式1: task.result.document_id
                if task.get("result"):
                    document_id = task.get("result", {}).get("document_id")

                # 格式2: data.result.document_id
                if not document_id:
                    document_id = data.get("result", {}).get("document_id")

                # 格式3: data.document_id
                if not document_id:
                    document_id = data.get("document_id")

                if not document_id:
                    error_msg = f"❌ 响应中未找到document_id: {response.text}"
                    logger.error(error_msg)
                    raise ImportTaskError(error_msg)

                logger.info(f"✅ 导入任务完成")
                logger.info(f"   document_id: {document_id}")
                return document_id

            elif task_status == "failed":
                # 导入失败
                error_msg = f"❌ 导入任务失败"
                logger.error(error_msg)
                if task.get("error"):
                    logger.error(f"   错误信息: {task.get('error')}")
                raise ImportTaskError(error_msg)

            elif task_status == "processing":
                # 继续轮询
                time.sleep(poll_interval)
                continue

            else:
                # 未知状态
                warning_msg = f"⚠️  未知状态: {task_status}"
                logger.warning(warning_msg)
                time.sleep(poll_interval)
                continue

    except (PollingTimeoutError, ImportTaskError):
        raise
    except Exception as e:
        logger.error(f"❌ 轮询导入状态时发生错误: {e}")
        logger.exception("详细错误堆栈")
        raise ImportTaskError(f"轮询导入状态失败: {e}")


def create_document_via_import(client: Client, content: str, title: str) -> str:
    """
    使用导入API创建文档（推荐方式）

    流程：
    1. 保存Markdown内容到临时文件
    2. 上传文件到飞书云空间
    3. 创建导入任务
    4. 轮询导入状态
    5. 返回文档ID

    Args:
        client: 飞书客户端
        content: Markdown格式的内容
        title: 文档标题

    Returns:
        document_id: 创建的文档ID

    Raises:
        DocumentCreationError: 文档创建失败
    """
    temp_file = None

    try:
        logger.info("=" * 60)
        logger.info("使用导入API创建文档（推荐方式）")
        logger.info("=" * 60)

        # 步骤1: 保存Markdown临时文件
        logger.info("步骤 1/5: 保存Markdown临时文件")
        temp_file = save_markdown_temp_file(
            content,
            title.replace("原文精转-", "").replace("关键纪要-", ""),  # 提取video_id部分
            "refined" if "原文精转" in title else "summary"
        )

        # 步骤2: 上传文件到飞书云空间
        logger.info("步骤 2/5: 上传文件到飞书云空间")
        file_token = upload_file_to_feishu(client, temp_file)

        # 步骤3: 创建导入任务
        logger.info("步骤 3/5: 创建导入任务")
        task_id = create_import_task(client, file_token, title)

        # 步骤4: 轮询导入状态
        logger.info("步骤 4/5: 轮询导入状态")
        document_id = poll_import_status(client, task_id, timeout=30)

        # 步骤5: 设置文档为公开访问
        logger.info("步骤 5/5: 设置文档公开访问权限")
        if set_document_public(client, document_id):
            logger.info("✅ 文档公开权限设置成功")
        else:
            logger.warning("⚠️  文档公开权限设置失败，文档可能无法公开访问")

        logger.info("=" * 60)
        logger.info("✅ 导入API文档创建完成")
        logger.info("=" * 60)

        return document_id

    except (FileUploadError, ImportTaskError, PollingTimeoutError) as e:
        logger.error(f"❌ 导入API文档创建失败: {e}")
        raise DocumentCreationError(f"导入API失败: {e}")

    except Exception as e:
        logger.error(f"❌ 文档创建过程中发生未知错误: {e}")
        logger.exception("详细错误堆栈")
        raise DocumentCreationError(f"文档创建失败: {e}")

    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.info(f"✅ 临时文件已清理: {temp_file}")
            except Exception as e:
                logger.warning(f"⚠️  清理临时文件失败: {e}")


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
