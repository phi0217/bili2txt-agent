#!/usr/bin/env python3
"""
飞书文档 API 测试脚本
用于探索和测试文档内容写入的正确 API 调用方式
"""
import logging
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 导入配置
from config import config

# 导入飞书 SDK
from lark_oapi import Client
from lark_oapi.api.docx.v1 import CreateDocumentRequest, CreateDocumentRequestBody


class FeishuDocumentAPITester:
    """飞书文档 API 测试类"""

    def __init__(self):
        """初始化测试器"""
        self.client = None
        self.test_document_id = None

    def setup_client(self):
        """初始化飞书客户端"""
        try:
            self.client = Client.builder() \
                .app_id(config.FEISHU_APP_ID) \
                .app_secret(config.FEISHU_APP_SECRET) \
                .build()

            logger.info("✅ 飞书客户端创建成功")
            return True

        except Exception as e:
            logger.error(f"❌ 创建飞书客户端失败: {e}")
            return False

    def test_create_document(self):
        """测试 1: 创建空文档"""
        logger.info("=" * 60)
        logger.info("测试 1: 创建空文档")
        logger.info("=" * 60)

        try:
            request = CreateDocumentRequest.builder().request_body(
                CreateDocumentRequestBody.builder()
                .title("API 测试文档")
                .build()
            ).build()

            response = self.client.docx.v1.document.create(request)

            if not response.success():
                logger.error(f"❌ 创建文档失败: {response.code} {response.msg}")
                if hasattr(response, 'error') and response.error:
                    logger.error(f"   详细错误: {response.error}")
                return None

            self.test_document_id = response.data.document.document_id
            logger.info(f"✅ 文档创建成功")
            logger.info(f"   文档 ID: {self.test_document_id}")
            return self.test_document_id

        except Exception as e:
            logger.error(f"❌ 创建文档时发生异常: {e}")
            logger.exception("详细错误堆栈")
            return None

    def test_get_document(self):
        """测试 2: 获取文档信息"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试 2: 获取文档信息")
        logger.info("=" * 60)

        if not self.test_document_id:
            logger.error("❌ 没有可用的文档 ID，请先运行测试 1")
            return False

        try:
            from lark_oapi.api.docx.v1 import GetDocumentRequest

            request = GetDocumentRequest.builder() \
                .document_id(self.test_document_id) \
                .build()

            response = self.client.docx.v1.document.get(request)

            if not response.success():
                logger.error(f"❌ 获取文档失败: {response.code} {response.msg}")
                return False

            logger.info("✅ 文档信息获取成功")
            logger.info(f"   文档 ID: {response.data.document.document_id}")
            logger.info(f"   文档标题: {response.data.document.title}")

            # 显示 revision_id
            if hasattr(response.data, 'document') and hasattr(response.data.document, 'revision_id'):
                logger.info(f"   版本 ID: {response.data.document.revision_id}")

            return True

        except Exception as e:
            logger.error(f"❌ 获取文档时发生异常: {e}")
            logger.exception("详细错误堆栈")
            return False

    def test_get_block_children(self):
        """测试 3: 获取文档块结构"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试 3: 获取文档块结构")
        logger.info("=" * 60)

        if not self.test_document_id:
            logger.error("❌ 没有可用的文档 ID，请先运行测试 1")
            return False

        try:
            from lark_oapi.api.docx.v1 import GetDocumentBlockChildrenRequest

            request = GetDocumentBlockChildrenRequest.builder() \
                .document_id(self.test_document_id) \
                .block_id(self.test_document_id) \
                .build()

            response = self.client.docx.v1.document.block.children.get(request)

            if not response.success():
                logger.error(f"❌ 获取块结构失败: {response.code} {response.msg}")
                return False

            logger.info("✅ 块结构获取成功")

            # 显示块信息
            if hasattr(response.data, 'items') and response.data.items:
                blocks = response.data.items
                logger.info(f"   找到 {len(blocks)} 个块")

                for i, block in enumerate(blocks[:3]):  # 只显示前 3 个
                    block_id = block.block_id if hasattr(block, 'block_id') else "unknown"
                    block_type = block.block_type if hasattr(block, 'block_type') else "unknown"
                    logger.info(f"   块 {i+1}: ID={block_id}, Type={block_type}")

                if len(blocks) > 3:
                    logger.info(f"   ... 还有 {len(blocks) - 3} 个块")
            else:
                logger.warning("   ⚠️  没有找到任何块（文档为空）")

            return True

        except Exception as e:
            logger.error(f"❌ 获取块结构时发生异常: {e}")
            logger.exception("详细错误堆栈")
            return False

    def test_create_block_children(self):
        """测试 4: 创建块子节点（写入内容）"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试 4: 创建块子节点（写入内容）")
        logger.info("=" * 60)

        if not self.test_document_id:
            logger.error("❌ 没有可用的文档 ID，请先运行测试 1")
            return False

        try:
            # 导入必要的类
            from lark_oapi.api.docx.v1 import CreateDocumentBlockChildrenRequest, CreateDocumentBlockChildrenRequestBody
            from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun

            # 创建测试文本块
            test_text = "这是一个测试文本，用于验证 API 调用是否正确。"

            logger.info(f"   准备写入测试文本: {test_text}")

            # 方式 1: 创建 TextRun
            text_run = TextRun.builder().content(test_text).build()
            logger.info("   ✅ TextRun 创建成功")

            # 方式 2: 创建 TextElement
            text_element = TextElement.builder().text_run(text_run).build()
            logger.info("   ✅ TextElement 创建成功")

            # 方式 3: 创建 Text
            text = Text.builder().elements([text_element]).build()
            logger.info("   ✅ Text 创建成功")

            # 方式 4: 创建 Block
            block = Block()
            block.text = text
            logger.info("   ✅ Block 创建成功")

            # 尝试不同的调用方式
            blocks = [block]

            logger.info("")
            logger.info("   尝试方式 1: 通过 client.docx.v1.document.block_children.create()")

            try:
                request = CreateDocumentBlockChildrenRequest.builder() \
                    .document_id(self.test_document_id) \
                    .block_id(self.test_document_id) \
                    .request_body(
                        CreateDocumentBlockChildrenRequestBody.builder()
                        .children(blocks)
                        .index(-1)
                        .build()
                    ).build()

                # 尝试不同的调用方式
                logger.info("      - 尝试: client.docx.v1.document.block_children.create()")
                response = self.client.docx.v1.document.block_children.create(request)

                if response.success():
                    logger.info("      ✅ 方式 1 成功！")
                    logger.info(f"      ✅ 成功写入 {len(blocks)} 个块")
                    return True
                else:
                    logger.warning(f"      ⚠️  方式 1 失败: {response.code} {response.msg}")

            except AttributeError as e:
                logger.warning(f"      ⚠️  方式 1 不可用: {e}")

            # 尝试方式 2: 通过 request.create()
            logger.info("")
            logger.info("   尝试方式 2: 通过 request.create()")

            try:
                response = request.create(self.client)

                if response.success():
                    logger.info("      ✅ 方式 2 成功！")
                    logger.info(f"      ✅ 成功写入 {len(blocks)} 个块")
                    return True
                else:
                    logger.warning(f"      ⚠️  方式 2 失败: {response.code} {response.msg}")

            except AttributeError as e:
                logger.warning(f"      ⚠️  方式 2 不可用: {e}")

            # 尝试方式 3: 直接调用 client.docx.v1.block_children.create()
            logger.info("")
            logger.info("   尝试方式 3: 通过 client.docx.v1.block_children.create()")

            try:
                response = self.client.docx.v1.block_children.create(request)

                if response.success():
                    logger.info("      ✅ 方式 3 成功！")
                    logger.info(f"      ✅ 成功写入 {len(blocks)} 个块")
                    return True
                else:
                    logger.warning(f"      ⚠️  方式 3 失败: {response.code} {response.msg}")

            except AttributeError as e:
                logger.warning(f"      ⚠️  方式 3 不可用: {e}")

            logger.error("   ❌ 所有方式都失败了")
            return False

        except Exception as e:
            logger.error(f"❌ 创建块子节点时发生异常: {e}")
            logger.exception("详细错误堆栈")
            return False

    def test_list_available_methods(self):
        """测试 5: 列出可用的 API 方法"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试 5: 探索可用的 API 方法")
        logger.info("=" * 60)

        try:
            # 检查 docx.v1 可用的方法
            docx_v1 = self.client.docx.v1

            logger.info("   docx.v1 可用的属性:")
            for attr in dir(docx_v1):
                if not attr.startswith('_'):
                    obj = getattr(docx_v1, attr)
                    if hasattr(obj, '__class__'):
                        logger.info(f"      - {attr}: {obj.__class__.__name__}")

            # 检查 document 对象
            logger.info("")
            logger.info("   document 对象的方法:")
            document_obj = self.client.docx.v1.document
            for method in dir(document_obj):
                if not method.startswith('_'):
                    logger.info(f"      - document.{method}()")

        except Exception as e:
            logger.error(f"❌ 探索方法时发生异常: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 20 + "飞书文档 API 测试套件" + " " * 20 + "║")
        logger.info("╚" + "=" * 58 + "╝")
        logger.info("")

        results = []

        # 1. 初始化客户端
        results.append(("初始化客户端", self.setup_client()))

        if not results[-1][1]:
            logger.error("❌ 客户端初始化失败，终止测试")
            return False

        # 2. 创建文档
        results.append(("创建空文档", self.test_create_document()))

        if not results[-1][1]:
            logger.error("❌ 文档创建失败，终止测试")
            return False

        # 3. 获取文档信息
        results.append(("获取文档信息", self.test_get_document()))

        # 4. 获取块结构
        results.append(("获取块结构", self.test_get_block_children()))

        # 5. 写入内容
        results.append(("写入内容", self.test_create_block_children()))

        # 6. 探索 API
        results.append(("探索 API", self.test_list_available_methods()))

        # 输出测试结果摘要
        logger.info("")
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 24 + "测试结果摘要" + " " * 24 + "║")
        logger.info("╚" + "=" * 58 + "╝")
        logger.info("")

        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name:30s} : {status}")

        logger.info("")

        # 判断整体测试结果
        passed = sum(1 for _, result in results if result)
        total = len(results)

        logger.info(f"总计: {passed}/{total} 测试通过")

        if passed == total:
            logger.info("🎉 所有测试通过！")
            logger.info("")
            logger.info("下一步：将成功的 API 调用方式应用到 doc_utils.py")
        else:
            logger.info("⚠️  部分测试失败，需要继续探索")

        return passed == total


def main():
    """主测试函数"""
    tester = FeishuDocumentAPITester()

    try:
        success = tester.run_all_tests()

        if success:
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ 测试完成！")
            logger.info("=" * 60)
            logger.info("")
            logger.info("现在可以将成功的 API 调用方式复制到 doc_utils.py")
            logger.info("")
            return 0
        else:
            logger.error("")
            logger.error("=" * 60)
            logger.error("❌ 测试失败")
            logger.error("=" * 60)
            return 1

    except KeyboardInterrupt:
        logger.info("")
        logger.info("测试被用户中断")
        return 1

    except Exception as e:
        logger.error("")
        logger.error(f"❌ 测试过程中发生异常: {e}")
        logger.exception("详细错误堆栈")
        return 1


if __name__ == "__main__":
    sys.exit(main())
