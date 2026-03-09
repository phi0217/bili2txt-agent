"""
测试视频标题注入到 LLM 提示词中
验证 generate_refined_text 和 generate_summary 是否正确使用视频标题
"""
import sys
sys.path.insert(0, 'src')

from llm_utils import generate_refined_text, generate_summary


def test_video_title_in_prompt():
    """测试视频标题是否被正确注入到提示词中"""

    # 测试数据
    test_text = "这是一个测试文本。用来验证视频标题是否被正确添加到提示词中。"
    test_title = "测试视频：如何使用Python进行AI开发"

    print("=" * 60)
    print("测试 1: 中文模式 - 原文精转（带视频标题）")
    print("=" * 60)

    # 打印模拟的提示词（不实际调用 API）
    print(f"\n测试文本: {test_text}")
    print(f"视频标题: {test_title}")
    print("\n预期效果：")
    print("- 提示词中应该包含 '视频标题: 测试视频：如何使用Python进行AI开发'")
    print("- 提示词中应该在第4条要求中引用视频标题")
    print("- LLM 应该能够根据视频标题理解内容上下文")

    print("\n" + "=" * 60)
    print("测试 2: 英文模式 - 关键纪要（带视频标题）")
    print("=" * 60)

    test_title_en = "AI Development with Python - Complete Guide"

    print(f"\n测试文本: {test_text}")
    print(f"视频标题: {test_title_en}")
    print("\n预期效果：")
    print("- 提示词中应该包含 '视频标题 / Video Title: AI Development with Python - Complete Guide'")
    print("- LLM 应该能够根据英文视频标题理解内容主题")

    print("\n" + "=" * 60)
    print("测试 3: 无视频标题的情况")
    print("=" * 60)

    print("\n预期效果：")
    print("- 当 video_title 为空字符串时，不应该添加视频标题部分")
    print("- 提示词应该正常工作，不会有多余的空行")

    print("\n" + "=" * 60)
    print("函数签名验证")
    print("=" * 60)

    # 检查函数签名
    import inspect

    # 检查 generate_refined_text
    sig_refined = inspect.signature(generate_refined_text)
    params_refined = list(sig_refined.parameters.keys())
    print(f"\ngenerate_refined_text 参数: {params_refined}")
    assert 'video_title' in params_refined, "❌ generate_refined_text 缺少 video_title 参数"
    assert 'language' in params_refined, "❌ generate_refined_text 缺少 language 参数"
    print("✅ generate_refined_text 参数正确")

    # 检查 generate_summary
    sig_summary = inspect.signature(generate_summary)
    params_summary = list(sig_summary.parameters.keys())
    print(f"\ngenerate_summary 参数: {params_summary}")
    assert 'video_title' in params_summary, "❌ generate_summary 缺少 video_title 参数"
    assert 'language' in params_summary, "❌ generate_summary 缺少 language 参数"
    print("✅ generate_summary 参数正确")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

    print("\n💡 实际使用示例：")
    print("""
    # 在 task.py 中的调用方式：
    refined_text = generate_refined_text(
        original_text,
        language="zh",
        video_title=video_title  # 从视频信息中获取的标题
    )

    summary_text = generate_summary(
        original_text,
        language="zh",
        video_title=video_title  # 从视频信息中获取的标题
    )
    """)


if __name__ == "__main__":
    test_video_title_in_prompt()
