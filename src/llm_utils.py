"""
LLM 工具
调用 DeepSeek API 对文本进行精转
"""
import logging
from typing import Optional
from openai import OpenAI
from config import config


logger = logging.getLogger("bili2txt-agent")


def refine_text(original_text: str, max_tokens: int = 3000) -> Optional[str]:
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
        logger.info(f"开始 LLM 精转，原始文本长度: {len(original_text)} 字符")

        # 创建 OpenAI 客户端（连接到 DeepSeek API）
        client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )

        # Prompt 模板
        prompt = f"""请将以下语音转写的文本整理成一篇可读性强的文章，修正错别字和不通顺之处，使其符合书面语表达。然后在文章开头用"【摘要】"开头添加一个简短的摘要，概括核心内容。换行后，用"【原文整理】"开头输出精转后的全文。

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
            logger.info(f"LLM 精转成功，精转文本长度: {len(refined_text)} 字符")
            return refined_text
        else:
            logger.error("LLM 返回结果为空")
            return None

    except Exception as e:
        logger.error(f"LLM 精转时发生错误: {e}")
        return None
