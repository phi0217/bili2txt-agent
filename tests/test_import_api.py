"""
测试Import API功能

验证飞书文档导入API的完整流程：
1. 保存Markdown临时文件
2. 上传文件到飞书云空间
3. 创建导入任务
4. 轮询导入状态
5. 获取文档链接
"""
import sys
import os

# 设置控制台输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录和src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from doc_utils import (
    save_markdown_temp_file,
    upload_file_to_feishu,
    create_import_task,
    poll_import_status,
    create_document_via_import,
    create_and_share_document,
)
from src.config import config
from lark_oapi import Client


def test_save_markdown_temp_file():
    """测试1: 保存Markdown临时文件"""
    print("\n" + "=" * 60)
    print("测试1: 保存Markdown临时文件")
    print("=" * 60)

    test_content = """# 测试标题

这是一个**测试**文档，用于验证Markdown格式渲染。

## 二级标题

- 列表项1
- 列表项2
- 列表项3

### 三级标题

这是一段普通文本，包含**加粗**和*斜体*内容。
"""

    try:
        # 保存文件
        file_path = save_markdown_temp_file(
            content=test_content,
            video_id="test123",
            doc_type="refined"
        )

        print(f"✅ 测试通过: 文件保存成功")
        print(f"   文件路径: {file_path}")

        # 验证文件存在
        if os.path.exists(file_path):
            print(f"✅ 文件存在验证通过")

            # 读取并验证内容
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                if saved_content == test_content:
                    print(f"✅ 文件内容验证通过")
                else:
                    print(f"❌ 文件内容不匹配")
            return file_path
        else:
            print(f"❌ 文件不存在")
            return None

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_upload_file_to_feishu(client, file_path):
    """测试2: 上传文件到飞书云空间"""
    print("\n" + "=" * 60)
    print("测试2: 上传文件到飞书云空间")
    print("=" * 60)

    if not file_path or not os.path.exists(file_path):
        print("❌ 跳过测试: 文件不存在")
        return None

    try:
        # 上传文件
        file_token = upload_file_to_feishu(client, file_path)

        print(f"✅ 测试通过: 文件上传成功")
        print(f"   file_token: {file_token}")

        return file_token

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_create_import_task(client, file_token):
    """测试3: 创建导入任务"""
    print("\n" + "=" * 60)
    print("测试3: 创建导入任务")
    print("=" * 60)

    if not file_token:
        print("❌ 跳过测试: file_token为空")
        return None

    try:
        # 创建导入任务
        task_id = create_import_task(
            client,
            file_token=file_token,
            title="测试文档-ImportAPI"
        )

        print(f"✅ 测试通过: 导入任务创建成功")
        print(f"   task_id: {task_id}")

        return task_id

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_poll_import_status(client, task_id):
    """测试4: 轮询导入状态"""
    print("\n" + "=" * 60)
    print("测试4: 轮询导入状态")
    print("=" * 60)

    if not task_id:
        print("❌ 跳过测试: task_id为空")
        return None

    try:
        # 轮询导入状态
        document_id = poll_import_status(client, task_id, timeout=30)

        print(f"✅ 测试通过: 导入完成")
        print(f"   document_id: {document_id}")

        return document_id

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_create_document_via_import(client):
    """测试5: 完整流程测试"""
    print("\n" + "=" * 60)
    print("测试5: 完整流程测试（端到端）")
    print("=" * 60)

    test_content = """# 原文精转测试

**视频ID**: test123
**测试时间**: 2026-03-08

---

## 核心内容

这是测试内容，用于验证**Markdown格式**能否正确渲染。

### 测试列表

- 列表项1
- 列表项2
- 列表项3

### 测试文本

这段文字包含**加粗**、*斜体*、`代码`等格式。

---

*本文档由 bili2txt-agent 自动生成*
"""

    try:
        # 完整流程测试
        document_id = create_document_via_import(
            client,
            content=test_content,
            title="原文精转-测试视频"
        )

        print(f"✅ 测试通过: 完整流程成功")
        print(f"   document_id: {document_id}")

        return document_id

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_create_and_share_document(client):
    """测试6: 带回退机制的完整流程"""
    print("\n" + "=" * 60)
    print("测试6: 带回退机制的完整流程")
    print("=" * 60)

    test_content = """# 关键纪要测试

## 1. 核心摘要

这是一个测试摘要。

## 2. 内容拆解

- 要点1
- 要点2

## 3. 关键要点

测试关键要点。

---

*本文档由 bili2txt-agent 自动生成*
"""

    try:
        # 测试带回退的文档创建
        share_url = create_and_share_document(
            client,
            content=test_content,
            title="关键纪要-测试视频"
        )

        if share_url:
            print(f"✅ 测试通过: 文档创建成功")
            print(f"   分享链接: {share_url}")
            return share_url
        else:
            print(f"❌ 测试失败: 返回链接为空")
            return None

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("飞书文档Import API功能测试")
    print("=" * 80)

    # 检查配置
    if not config.FEISHU_APP_ID or not config.FEISHU_APP_SECRET:
        print("❌ 飞书配置缺失，请检查 .env 文件")
        print("   需要配置: FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        return

    # 创建飞书客户端
    client = Client.builder() \
        .app_id(config.FEISHU_APP_ID) \
        .app_secret(config.FEISHU_APP_SECRET) \
        .build()

    print(f"✅ 飞书客户端创建成功")
    print(f"   App ID: {config.FEISHU_APP_ID}")

    # 运行测试
    results = {}

    # 测试1: 保存文件（独立测试）
    file_path = test_save_markdown_temp_file()
    results["test1_save_file"] = file_path is not None

    # 如果前面测试失败，跳过后续测试
    if not file_path:
        print("\n⚠️  测试1失败，跳过后续需要飞书API的测试")
        print("   请检查文件系统权限和TEMP_DIR配置")
        return

    # 测试2-4: 上传、导入、轮询（顺序测试，依赖前一个测试的结果）
    file_token = test_upload_file_to_feishu(client, file_path)
    results["test2_upload"] = file_token is not None

    if file_token:
        task_id = test_create_import_task(client, file_token)
        results["test3_import_task"] = task_id is not None

        if task_id:
            document_id = test_poll_import_status(client, task_id)
            results["test4_poll_status"] = document_id is not None

    # 测试5: 完整流程（独立测试）
    try:
        doc_id = test_create_document_via_import(client)
        results["test5_full_flow"] = doc_id is not None
    except Exception as e:
        print(f"⚠️  测试5异常: {e}")
        results["test5_full_flow"] = False

    # 测试6: 带回退机制的完整流程
    try:
        url = test_create_and_share_document(client)
        results["test6_with_fallback"] = url is not None
    except Exception as e:
        print(f"⚠️  测试6异常: {e}")
        results["test6_with_fallback"] = False

    # 打印测试结果总结
    print("\n" + "=" * 80)
    print("测试结果总结")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")

    print("=" * 80)


if __name__ == "__main__":
    main()
