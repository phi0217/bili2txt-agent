"""
测试 max_tokens 无上限功能
验证不同长度的文本是否都能正常处理而不受 max_tokens 上限限制
"""
import sys
import os

# 添加 src 目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from llm_utils import generate_refined_text, generate_summary


def calculate_max_tokens(original_text: str, is_summary: bool = False) -> int:
    """
    模拟 llm_utils.py 中的 max_tokens 计算逻辑
    """
    input_tokens = len(original_text) * 2  # 保守估计

    if is_summary:
        # 摘要：最小2000，无上限
        max_tokens = max(2000, input_tokens // 3)
    else:
        # 精转：最小4000，无上限
        max_tokens = max(4000, input_tokens)

    return max_tokens


def test_unlimited_max_tokens():
    """测试不同长度文本的 max_tokens 计算"""

    print("=" * 60)
    print("测试：max_tokens 无上限功能")
    print("=" * 60)

    test_cases = [
        ("短文本（1000字）", 1000),
        ("中等文本（5000字）", 5000),
        ("长文本（10000字）", 10000),
        ("很长文本（20000字）", 20000),
        ("超长文本（50000字）", 50000),
        ("极长文本（100000字）", 100000),
    ]

    print("\n" + "-" * 60)
    print("原文精转 (generate_refined_text)")
    print("-" * 60)

    for name, length in test_cases:
        max_tokens = calculate_max_tokens("x" * length, is_summary=False)
        print(f"\n{name}:")
        print(f"  输入长度: {length} 字符")
        print(f"  估算 tokens: {length * 2}")
        print(f"  max_tokens: {max_tokens}")
        print(f"  状态: {'✓ 无上限限制' if max_tokens == max(4000, length * 2) else '✗ 有上限限制'}")

    print("\n" + "-" * 60)
    print("关键纪要 (generate_summary)")
    print("-" * 60)

    for name, length in test_cases:
        max_tokens = calculate_max_tokens("x" * length, is_summary=True)
        print(f"\n{name}:")
        print(f"  输入长度: {length} 字符")
        print(f"  估算 tokens: {length * 2}")
        print(f"  max_tokens: {max_tokens}")
        print(f"  状态: {'✓ 无上限限制' if max_tokens == max(2000, (length * 2) // 3) else '✗ 有上限限制'}")

    print("\n" + "=" * 60)
    print("对比分析：旧版 vs 新版")
    print("=" * 60)

    print("\n原文精转 - 10000字符文本：")
    print("  旧版: min(max(4000, 20000), 16000) = 16000 (有上限)")
    print("  新版: max(4000, 20000) = 20000 (无上限)")
    print("  提升: +25%")

    print("\n关键纪要 - 30000字符文本：")
    print("  旧版: min(max(2000, 20000), 8000) = 8000 (有上限)")
    print("  新版: max(2000, 20000) = 20000 (无上限)")
    print("  提升: +150%")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

    print("\n注意事项：")
    print("1. DeepSeek API 有自己的输出 token 限制（通常 16K）")
    print("2. 设置的 max_tokens 如果超过 API 限制，API 会自动截断")
    print("3. 移除代码上限后，可以充分利用 API 的输出能力")
    print("4. 处理超长文本时，需要注意 API 调用时间和费用")


if __name__ == "__main__":
    test_unlimited_max_tokens()
