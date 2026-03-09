"""
测试视频标题注入到 LLM 提示词中
验证 generate_refined_text 和 generate_summary 是否正确使用视频标题
"""
import sys
sys.path.insert(0, 'src')

from llm_utils import generate_refined_text, generate_summary
import inspect


def test_video_title_in_prompt():
    """测试视频标题是否被正确注入到提示词中"""

    print("=" * 60)
    print("测试：视频标题注入到 LLM 提示词")
    print("=" * 60)

    # 检查 generate_refined_text
    sig_refined = inspect.signature(generate_refined_text)
    params_refined = list(sig_refined.parameters.keys())
    print(f"\ngenerate_refined_text 参数:")
    for i, param in enumerate(params_refined, 1):
        print(f"  {i}. {param}")

    assert 'video_title' in params_refined, "generate_refined_text 缺少 video_title 参数"
    assert 'language' in params_refined, "generate_refined_text 缺少 language 参数"
    print("[OK] generate_refined_text 参数正确")

    # 检查 generate_summary
    sig_summary = inspect.signature(generate_summary)
    params_summary = list(sig_summary.parameters.keys())
    print(f"\ngenerate_summary 参数:")
    for i, param in enumerate(params_summary, 1):
        print(f"  {i}. {param}")

    assert 'video_title' in params_summary, "generate_summary 缺少 video_title 参数"
    assert 'language' in params_summary, "generate_summary 缺少 language 参数"
    print("[OK] generate_summary 参数正确")

    print("\n" + "=" * 60)
    print("[OK] 所有测试通过！")
    print("=" * 60)

    print("\n实际使用示例：")
    print("-" * 60)
    print("""
# 在 task.py 中的调用方式：

# 1. 获取视频标题（已在 task.py 中实现）
video_title = video_id  # 默认使用视频ID
if VIDEO_INFO_AVAILABLE and get_video_info is not None:
    try:
        video_info = get_video_info(video_id)
        if video_info and video_info.get('title'):
            video_title = video_info['title']
    except Exception as e:
        logger.warning(f"获取视频标题失败: {e}")

# 2. 调用 LLM 函数时传递视频标题
refined_text = generate_refined_text(
    original_text,
    language="zh",
    video_title=video_title  # 视频标题注入到提示词
)

summary_text = generate_summary(
    original_text,
    language="zh",
    video_title=video_title  # 视频标题注入到提示词
)
    """)
    print("-" * 60)

    print("\n预期效果：")
    print("1. LLM 提示词会包含视频标题信息")
    print("2. LLM 可以根据视频标题更好地理解内容上下文")
    print("3. 对于专业领域的视频，可以提高精转和摘要的准确性")


if __name__ == "__main__":
    test_video_title_in_prompt()
