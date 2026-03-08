"""
LLM 工具
调用 DeepSeek API 对文本进行精转
"""
import logging
from typing import Optional
from openai import OpenAI
from config import config


logger = logging.getLogger("bili2txt-agent")


def generate_summary(original_text: str, max_tokens: int = 1000) -> Optional[str]:
    """
    使用 DeepSeek API 生成关键纪要

    Args:
        original_text: 原始文本
        max_tokens: 最大 token 数

    Returns:
        关键纪要文本，失败则返回 None
    """
    if not original_text:
        logger.warning("原始文本为空，跳过生成纪要")
        return None

    try:
        logger.info(f"开始生成关键纪要，原始文本长度: {len(original_text)} 字符")

        # 创建 OpenAI 客户端（连接到 DeepSeek API）
        client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )

        # Prompt 模板 - 生成关键纪要
        prompt = f"""将一段语音识别转换的原始文本（如会议、讲座、访谈、课程、直播、新闻等音频内容）转化为一份结构清晰、内容精炼的关键纪要。请提炼核心信息，忽略无关细节和口语化冗余，并按以下要求整理。

写作要求：

语言简洁、条理清晰，避免口语化和重复内容。

每个模块用标题明确分隔，内容采用项目符号或编号，便于阅读。

关键信息要准确，术语解释要通俗易懂。

深度洞察部分要体现思维深度，启发和应用要有实际价值。

注意事项：

如果原始文本中有明显的错误或无关内容，可以适当忽略或修正。

输出格式：

1.核心摘要
用一段话概括整个内容的核心主题和主要结论。

2.内容拆解
将内容按逻辑顺序拆分为若干部分，每个部分列出关键点。可用小标题划分不同话题或阶段。

3.关键要点
提炼出最核心的观点、事实或行动建议，以要点形式列出（每条可带简要解释）。

4.深度洞察

    理论关联：将内容与现实理论、模型或常见问题相关联，指出其背后的原理或规律。

    思维模型：指出所体现的思维方式（如系统思维、优先级思维等）。

    生动比喻：如果有，可以用一个比喻帮助理解核心概念。

5.启发

    个人层面：对个人成长、工作或学习的启发。

    团队/行业层面：对团队协作、组织管理或行业发展的启示。

6.应用场景
    提供至少两个不同场景下如何应用内容中的观点或方法，说明其迁移价值。

7.术语解释
    列出原文中出现的专业术语或关键词，为每个术语提供简要解释并标注其重要性（高/中/低）。

8.加深印象
    设计几个问答（Q&A），帮助读者回顾和巩固纪要中的关键信息。问题应覆盖核心观点、重要细节和潜在应用。


原始文本：
{original_text}"""

        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        # 提取结果
        summary_text = response.choices[0].message.content

        if summary_text:
            logger.info(f"关键纪要生成成功，纪要长度: {len(summary_text)} 字符")
            return summary_text
        else:
            logger.error("LLM 返回结果为空")
            return None

    except Exception as e:
        logger.error(f"生成关键纪要时发生错误: {e}")
        return None


def generate_refined_text(original_text: str, max_tokens: int = 3000) -> Optional[str]:
    """
    使用 DeepSeek API 对文本进行精转

    Args:
        original_text: 原始文本
        max_tokens: 最大 token 数

    Returns:
        精转后的文本，失败则返回 None
    """
    if not original_text:
        logger.warning("原始文本为空，跳过精转")
        return None

    try:
        logger.info(f"开始原文精转，原始文本长度: {len(original_text)} 字符")

        # 创建 OpenAI 客户端（连接到 DeepSeek API）
        client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )

        # Prompt 模板 - 原文精转（不含摘要）
        prompt = f"""你是一个文本精修助手。请将下面提供的"识别原文"（一段音频的语音转文字，可能含有错别字、缺少标点、口语化表达）改写成"原文精转"版本。要求：

1.修正错别字：根据上下文识别并修正明显的错别字。
2.添加标点，合理断句：为整段文字添加恰当的中文标点符号，并根据语义划分句子和段落，使文章结构清晰、易于阅读。
3.理顺语句，提升流畅度：调整不通顺或逻辑跳跃的句子，去除冗余的口头禅（如"对吧"、"然后"等），将口语表达转化为精炼的书面语，同时保留原文的核心信息和整体风格。
4.保留原意和风格：确保改写后的文本不改变原意，并根据音频内容保持适当的语气（如叙述、讨论、讲解等），整体通顺自然。
5.增加自然段的数量，提升可读性：根据音频内容的自然进程（如话题转换、时间顺序、逻辑层次等）进行细致分段，使每一段表达一个相对独立的要点，段落分明，便于读者快速理解。避免长段落，确保阅读节奏舒适。
6.段落缩进：每个自然段的开头必须缩进4个空格，以规范中文排版格式。

识别原文：
{original_text}"""

        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        # 提取结果
        refined_text = response.choices[0].message.content

        if refined_text:
            logger.info(f"原文精转成功，精转文本长度: {len(refined_text)} 字符")
            return refined_text
        else:
            logger.error("LLM 返回结果为空")
            return None

    except Exception as e:
        logger.error(f"原文精转时发生错误: {e}")
        return None


def refine_text(original_text: str, max_tokens: int = 3000) -> Optional[str]:
    """
    使用 DeepSeek API 对文本进行精转（旧版本，保留兼容性）

    Args:
        original_text: 原始文本
        max_tokens: 最大 token 数

    Returns:
        精转后的文本，失败则返回 None
    """
    return generate_refined_text(original_text, max_tokens)
