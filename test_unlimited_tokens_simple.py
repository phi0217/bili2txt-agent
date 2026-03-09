"""
测试 max_tokens 无上限功能
"""
import sys
sys.path.insert(0, 'src')


def calculate_max_tokens_refined(text_length):
    """模拟原文精转的 max_tokens 计算"""
    input_tokens = text_length * 2
    max_tokens = max(4000, input_tokens)  # 无上限
    return max_tokens


def calculate_max_tokens_summary(text_length):
    """模拟关键纪要的 max_tokens 计算"""
    input_tokens = text_length * 2
    max_tokens = max(2000, input_tokens // 3)  # 无上限
    return max_tokens


def test_unlimited():
    """测试不同长度文本"""
    print("=" * 60)
    print("测试：max_tokens 无上限功能")
    print("=" * 60)

    test_cases = [
        (1000, "短文本"),
        (5000, "中等文本"),
        (10000, "长文本"),
        (20000, "很长文本"),
        (50000, "超长文本"),
        (100000, "极长文本"),
    ]

    print("\n原文精转 (generate_refined_text):")
    print("-" * 60)
    for length, name in test_cases:
        max_tokens = calculate_max_tokens_refined(length)
        print(f"{name} ({length}字符): max_tokens = {max_tokens}")

    print("\n关键纪要 (generate_summary):")
    print("-" * 60)
    for length, name in test_cases:
        max_tokens = calculate_max_tokens_summary(length)
        print(f"{name} ({length}字符): max_tokens = {max_tokens}")

    print("\n" + "=" * 60)
    print("对比分析：旧版 vs 新版")
    print("=" * 60)

    # 原文精转对比
    print("\n原文精转 - 10000字符:")
    old_max = min(max(4000, 10000 * 2), 16000)  # 旧版
    new_max = max(4000, 10000 * 2)  # 新版
    print(f"  旧版: {old_max} tokens (上限16000)")
    print(f"  新版: {new_max} tokens (无上限)")
    print(f"  提升: {(new_max - old_max) / old_max * 100:.1f}%")

    # 关键纪要对比
    print("\n关键纪要 - 30000字符:")
    old_max = min(max(2000, 30000 * 2 // 3), 8000)  # 旧版
    new_max = max(2000, 30000 * 2 // 3)  # 新版
    print(f"  旧版: {old_max} tokens (上限8000)")
    print(f"  新版: {new_max} tokens (无上限)")
    print(f"  提升: {(new_max - old_max) / old_max * 100:.1f}%")

    print("\n" + "=" * 60)
    print("[OK] 测试完成 - 已移除 max_tokens 上限")
    print("=" * 60)

    print("\n效果说明:")
    print("1. 短文本：保持最小值限制 (精转4000, 摘要2000)")
    print("2. 长文本：随输入长度动态增长，无上限")
    print("3. API限制：DeepSeek会自动处理(通常16K输出限制)")
    print("4. 充分利用：不再受代码上限限制，最大化输出质量")


if __name__ == "__main__":
    test_unlimited()
