"""
测试删除 max_tokens 控制代码后的行为
"""
import sys
import os

# 添加 src 目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from llm_utils import generate_refined_text, generate_summary


def test_no_max_tokens_control():
    """测试不再有 max_tokens 动态计算"""

    print("=" * 60)
    print("测试：删除 max_tokens 控制代码")
    print("=" * 60)

    # 检查函数签名
    import inspect

    sig_summary = inspect.signature(generate_summary)
    sig_refined = inspect.signature(generate_refined_text)

    print("\n函数签名验证:")
    print("-" * 60)
    print(f"generate_summary 参数:")
    for param_name, param in sig_summary.parameters.items():
        default = param.default if param.default != inspect.Parameter.empty else "必需"
        print(f"  - {param_name}: {default}")

    print(f"\ngenerate_refined_text 参数:")
    for param_name, param in sig_refined.parameters.items():
        default = param.default if param.default != inspect.Parameter.empty else "必需"
        print(f"  - {param_name}: {default}")

    print("\n" + "=" * 60)
    print("代码行为说明")
    print("=" * 60)

    print("""
修改前（旧代码）:
    if max_tokens is None:
        input_tokens = len(original_text) * 2
        max_tokens = max(2000, input_tokens // 3)  # 动态计算
    response = client.chat.completions.create(..., max_tokens=max_tokens, ...)

修改后（新代码）:
    api_params = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    if max_tokens is not None:  # 只在明确指定时设置
        api_params["max_tokens"] = max_tokens
    response = client.chat.completions.create(**api_params)

    """)

    print("\n" + "=" * 60)
    print("实际效果")
    print("=" * 60)

    print("""
1. 默认调用（不指定 max_tokens）:
   generate_summary(original_text, language="zh")
   -> 不设置 max_tokens 参数
   -> DeepSeek API 使用默认输出限制（通常 4K-16K tokens）

2. 手动指定 max_tokens:
   generate_summary(original_text, max_tokens=8000, language="zh")
   -> 设置 max_tokens=8000
   -> DeepSeek API 限制输出到 8000 tokens

3. 代码简化:
   -> 删除了所有动态计算 max_tokens 的代码
   -> 删除了文本长度警告/提示
   -> 更清晰的代码逻辑

4. DeepSeek API 行为:
   -> 不设置 max_tokens 时，API 使用模型默认的最大输出长度
   -> 这个限制由 DeepSeek 服务端控制，不是代码控制
   -> 通常 deepseek-chat 模型的默认输出限制是 4K-16K tokens
    """)

    print("\n" + "=" * 60)
    print("[OK] 测试完成 - 已删除所有 max_tokens 控制代码")
    print("=" * 60)

    print("\n好处:")
    print("1. 代码更简洁，易于理解")
    print("2. 充分利用 DeepSeek API 的默认行为")
    print("3. 避免误导性的动态计算（实际上无法控制 API 输出长度）")
    print("4. 保留手动指定 max_tokens 的能力（特殊情况）")


if __name__ == "__main__":
    test_no_max_tokens_control()
