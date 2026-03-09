# 删除 max_tokens 控制代码

## 修改概述

完全删除了所有试图动态计算和控制 `max_tokens` 的代码。这些代码实际上无法真正控制 DeepSeek API 的输出长度，反而会让代码更难理解。现在让 DeepSeek API 使用其默认行为。

## 为什么删除这些代码？

### 1. 无法真正控制 API 输出
代码中设置的 `max_tokens` 参数实际上不能保证输出达到指定长度：
- DeepSeek API 有自己的模型输出限制（通常 4K-16K tokens）
- 即使设置 `max_tokens=100000`，API 也只会输出到模型允许的最大长度
- 动态计算的值（如 `max(2000, input_tokens // 3)`）实际上没有意义

### 2. 误导性的代码逻辑
之前的代码给用户一种"可以控制输出长度"的错误印象：
```python
# 旧代码 - 误导性
input_tokens = len(original_text) * 2
max_tokens = max(2000, input_tokens // 3)  # 实际上无法保证输出这么多
```

实际上，API 会根据模型自己的限制输出，不受这个值的影响（除非设置的值小于模型限制）。

### 3. 代码复杂度增加
动态计算、日志输出、长度警告等代码增加了复杂度，但没有实际价值。

## 修改内容

### 删除的代码

#### generate_summary() 函数
```python
# 删除了以下代码
if max_tokens is None:
    input_tokens = len(original_text) * 2
    max_tokens = max(2000, input_tokens // 3)
    logger.info(f"自动计算 max_tokens: {max_tokens} ...")

# 删除了文本长度警告
if text_length > 50000:
    logger.info(f"ℹ️  原始文本很长 ...")
elif text_length > 20000:
    logger.info(f"ℹ️  原始文本较大 ...")
```

#### generate_refined_text() 函数
```python
# 删除了以下代码
if max_tokens is None:
    input_tokens = len(original_text) * 2
    max_tokens = max(4000, input_tokens)
    logger.info(f"自动计算 max_tokens: {max_tokens} ...")

# 删除了文本长度警告
if text_length > 50000:
    logger.info(f"ℹ️  原始文本很长 ...")
```

### 修改后的代码

#### API 调用方式
```python
# 新代码 - 简洁明了
api_params = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.7
}

# 只有在明确指定 max_tokens 时才设置
if max_tokens is not None:
    api_params["max_tokens"] = max_tokens
    logger.info(f"设置 max_tokens: {max_tokens}")

response = client.chat.completions.create(**api_params)
```

## 实际效果

### 1. 默认行为（推荐）
```python
# 不指定 max_tokens，使用 DeepSeek 默认值
summary_text = generate_summary(original_text, language="zh")
refined_text = generate_refined_text(original_text, language="zh")
```

**效果**：
- 不向 API 传递 `max_tokens` 参数
- DeepSeek API 使用模型的默认输出限制
- 通常 `deepseek-chat` 模型的默认输出限制是 **4K-16K tokens**
- 充分利用模型的输出能力

### 2. 手动指定（特殊情况）
```python
# 如果需要明确限制输出长度（罕见）
summary_text = generate_summary(original_text, max_tokens=8000, language="zh")
```

**效果**：
- 向 API 传递 `max_tokens=8000`
- DeepSeek API 会限制输出到最多 8000 tokens
- 仅在特殊需求时使用（如测试、费用控制等）

## DeepSeek API 的实际行为

### 不设置 max_tokens
```
API 请求: {model: "deepseek-chat", messages: [...], temperature: 0.7}
API 响应: 输出最多到模型默认限制（通常 4K-16K tokens）
```

### 设置 max_tokens=100000
```
API 请求: {model: "deepseek-chat", messages: [...], max_tokens: 100000, temperature: 0.7}
API 响应: 输出最多到模型默认限制（通常 4K-16K tokens）
注意: 设置超过模型限制的值不会增加输出，API 会自动截断
```

### 设置 max_tokens=2000
```
API 请求: {model: "deepseek-chat", messages: [...], max_tokens: 2000, temperature: 0.7}
API 响应: 输出最多 2000 tokens
注意: 这会限制输出长度，可能丢失内容
```

## 代码简化效果

### 代码行数减少
- `generate_summary()`: 减少 ~15 行代码
- `generate_refined_text()`: 减少 ~15 行代码
- 总计减少 **~30 行代码**

### 代码清晰度提升
- ✅ 删除了误导性的动态计算逻辑
- ✅ 删除了无意义的长度警告
- ✅ 更直接地表达代码意图
- ✅ 更容易理解和维护

## 函数文档更新

### max_tokens 参数说明
```python
# 旧文档
max_tokens: 最大 token 数（None表示自动计算）

# 新文档
max_tokens: 最大 token 数（None表示不设置，使用DeepSeek默认值）
```

## 测试验证

运行测试脚本：
```bash
python test_remove_max_tokens.py
```

预期输出：
```
函数签名验证:
  generate_summary 参数:
    - original_text: 必需
    - max_tokens: None
    - language: zh
    - video_title:

  generate_refined_text 参数:
    - original_text: 必需
    - max_tokens: None
    - language: zh
    - video_title:

[OK] 测试完成 - 已删除所有 max_tokens 控制代码
```

## 好处总结

1. **代码更简洁** - 减少 ~30 行无效代码
2. **逻辑更清晰** - 删除误导性的动态计算
3. **行为更明确** - 充分利用 DeepSeek API 默认行为
4. **更易维护** - 减少不必要的复杂度
5. **避免误解** - 不再给用户错误的预期

## 兼容性

- ✅ **完全向后兼容** - 函数签名保持不变
- ✅ **默认行为改进** - 不指定 `max_tokens` 时效果更好
- ✅ **保留手动控制** - 仍可手动指定 `max_tokens`（特殊情况）

## 相关文件

- [src/llm_utils.py](../src/llm_utils.py) - 主要修改
- [test_remove_max_tokens.py](../test_remove_max_tokens.py) - 测试脚本

## 总结

这次修改是一次重要的**代码简化**和**认知修正**：

**核心思想**：承认我们无法（也不应该）通过代码控制 LLM 的输出长度，让 API 使用其最优的默认行为。

**效果**：代码更简洁、更清晰、更诚实，用户体验反而更好。
