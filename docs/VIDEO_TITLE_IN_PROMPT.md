# 视频标题注入到 LLM 提示词

## 修改概述

为了提升 LLM 对视频内容的理解能力，我们将视频标题注入到了 LLM 的提示词中。这样 LLM 可以根据视频标题更好地理解内容的主题、上下文和专业领域。

## 修改的文件

### 1. src/llm_utils.py

#### `generate_summary()` 函数
- **新增参数**: `video_title: str = ""`
- **提示词修改**: 在提示词开头添加了视频标题信息
  - 中文模式: `\n**视频标题**: {video_title}\n\n`
  - 英文模式: `\n**视频标题 / Video Title**: {video_title}\n\n`

#### `generate_refined_text()` 函数
- **新增参数**: `video_title: str = ""`
- **提示词修改**: 在提示词开头添加了视频标题信息
  - 中文模式: 在第4条要求中引用视频标题 `"根据音频内容和视频标题"{video_title}"保持适当的语气"`
  - 英文模式: 在提示词开头添加标题信息

#### `refine_text()` 兼容性函数
- **新增参数**: `video_title: str = ""`
- 保持向后兼容，默认为空字符串

### 2. src/task.py

#### 修改调用方式
```python
# 旧代码（不传递视频标题）
refined_text = generate_refined_text(original_text, language=language)
summary_text = generate_summary(original_text, language=language)

# 新代码（传递视频标题）
refined_text = generate_refined_text(original_text, language=language, video_title=video_title)
summary_text = generate_summary(original_text, language=language, video_title=video_title)
```

## 视频标题获取

视频标题在 [task.py:389-398](../src/task.py#L389-L398) 中获取：

```python
# 4. 获取视频标题（如果可用）
video_title = video_id  # 默认使用视频ID
if VIDEO_INFO_AVAILABLE and get_video_info is not None:
    try:
        video_info = get_video_info(video_id)
        if video_info and video_info.get('title'):
            video_title = video_info['title']
            logger.info(f"视频标题: {video_title}")
    except Exception as e:
        logger.warning(f"获取视频标题失败: {e}")
```

## 提示词示例

### 原文精转 - 中文模式

```
你是一个文本精修助手。请将下面提供的"识别原文"（一段音频的语音转文字，可能含有错别字、缺少标点、口语化表达）改写成"原文精转"版本。要求：

**视频标题**: 深度学习入门：从零开始构建神经网络

1.修正错别字：根据上下文识别并修正明显的错别字。
2.添加标点，合理断句：为整段文字添加恰当的中文标点符号，并根据语义划分句子和段落，使文章结构清晰、易于阅读。
3.理顺语句，提升流畅度：调整不通顺或逻辑跳跃的句子，去除冗余的口头禅（如"对吧"、"然后"等），将口语表达转化为精炼的书面语，同时保留原文的核心信息和整体风格。
4.保留原意和风格：确保改写后的文本不改变原意，并根据音频内容和视频标题"深度学习入门：从零开始构建神经网络"保持适当的语气（如叙述、讨论、讲解等），整体通顺自然。
5.增加自然段的数量，提升可读性：根据音频内容的自然进程（如话题转换、时间顺序、逻辑层次等）进行细致分段，使每一段表达一个相对独立的要点，段落分明，便于读者快速理解。避免长段落，确保阅读节奏舒适。
6.段落缩进：每个自然段的开头必须缩进4个空格，以规范中文排版格式。

识别原文：
{original_text}
```

### 关键纪要 - 英文/双语模式

```
Convert the following speech recognition text (which may be in English or Chinese) into a structured, concise bilingual (Chinese and English) summary. Extract core information and organize according to the requirements below.

将一段语音识别转换的原始文本（如会议、讲座、访谈、课程、直播、新闻等音频内容，可能是英文或中文）转化为一份结构清晰、内容精炼的中英双语关键纪要。请提炼核心信息，忽略无关细节和口语化冗余，并按以下要求整理。

**视频标题 / Video Title**: AI Development with Python - Complete Guide

写作要求 Requirements:
- 语言简洁、条理清晰，避免口语化和重复内容 / Concise and clear, avoid colloquialism and repetition
- 每个模块用标题明确分隔，中英双语呈现 / Use clear headings for each section, present in both Chinese and English
- 关键信息要准确，术语解释要通俗易懂 / Key information should be accurate, terms should be easy to understand

原始文本 / Original Text:
{original_text}
```

## 预期效果

### 1. 提升内容理解
- LLM 可以根据视频标题预判内容主题
- 对于专业术语有更好的理解和处理
- 能够更好地保持内容的专业性和连贯性

### 2. 提高精转质量
- 根据标题判断内容类型（教程、演讲、访谈等）
- 调整语气和表达方式以匹配视频主题
- 减少对专业术语的错误修正

### 3. 优化摘要准确性
- 根据标题抓住核心主题
- 提炼与标题相关的关键信息
- 生成更精准的内容摘要

## 测试验证

运行测试脚本验证修改：

```bash
python test_video_title_simple.py
```

预期输出：
```
generate_refined_text 参数:
  1. original_text
  2. max_tokens
  3. language
  4. video_title
[OK] generate_refined_text 参数正确

generate_summary 参数:
  1. original_text
  2. max_tokens
  3. language
  4. video_title
[OK] generate_summary 参数正确

[OK] 所有测试通过！
```

## 兼容性说明

- **向后兼容**: 所有新增的 `video_title` 参数都是可选的，默认为空字符串
- **不影响现有功能**: 如果不传递视频标题，系统仍然正常工作
- **渐进式增强**: 只有在能够获取到视频标题时，才会将其注入到提示词中

## 相关文件

- [src/llm_utils.py](../src/llm_utils.py) - LLM 工具函数
- [src/task.py](../src/task.py) - 任务处理流程
- [test_video_title_simple.py](../test_video_title_simple.py) - 测试脚本
- [src/bilibili_downloader.py](../src/bilibili_downloader.py) - 视频信息获取

## 未来优化方向

1. **视频标签**: 可以考虑将视频的标签也注入到提示词中
2. **视频描述**: 对于有详细描述的视频，可以提取关键信息
3. **UP主信息**: 根据UP主的领域特点调整处理策略
4. **动态调整**: 根据视频标题的特点，动态调整 LLM 的参数（如 temperature）
