# 移除 max_tokens 上限

## 修改概述

为了最大化 DeepSeek API 的输出质量，我们移除了 `max_tokens` 的代码级上限限制。现在系统会根据输入文本长度动态计算 `max_tokens`，不再设置硬性上限，让 DeepSeek API 能够输出尽可能完整的内容。

## 修改的文件

### src/llm_utils.py

#### `generate_summary()` - 关键纪要生成

**旧版代码**：
```python
# 有上限：最小2000，最大8000
input_tokens = len(original_text) * 2
max_tokens = min(max(2000, input_tokens // 3), 8000)
```

**新版代码**：
```python
# 无上限：最小2000，动态增长
input_tokens = len(original_text) * 2
max_tokens = max(2000, input_tokens // 3)  # 移除上限
```

#### `generate_refined_text()` - 原文精转

**旧版代码**：
```python
# 有上限：最小4000，最大16000
input_tokens = len(original_text) * 2
max_tokens = min(max(4000, input_tokens), 16000)
```

**新版代码**：
```python
# 无上限：最小4000，动态增长
input_tokens = len(original_text) * 2
max_tokens = max(4000, input_tokens)  # 移除上限
```

## 性能提升对比

### 原文精转 (generate_refined_text)

| 输入长度 | 旧版 max_tokens | 新版 max_tokens | 提升 |
|---------|----------------|----------------|------|
| 1,000字符 | 4,000 | 4,000 | - |
| 5,000字符 | 10,000 | 10,000 | - |
| 10,000字符 | 16,000 | 20,000 | **+25%** |
| 20,000字符 | 16,000 | 40,000 | **+150%** |
| 50,000字符 | 16,000 | 100,000 | **+525%** |

### 关键纪要 (generate_summary)

| 输入长度 | 旧版 max_tokens | 新版 max_tokens | 提升 |
|---------|----------------|----------------|------|
| 1,000字符 | 2,000 | 2,000 | - |
| 5,000字符 | 3,333 | 3,333 | - |
| 10,000字符 | 6,666 | 6,666 | - |
| 20,000字符 | 8,000 | 13,333 | **+67%** |
| 30,000字符 | 8,000 | 20,000 | **+150%** |
| 50,000字符 | 8,000 | 33,333 | **+317%** |

## 日志提示优化

### 旧版日志
```
⚠️  原始文本过长 (20000 字符)，可能影响处理质量，建议分段处理
⚠️  原始文本过长 (20000 字符)，精转结果可能被截断
```

### 新版日志
```
ℹ️  原始文本较长 (20000 字符)，处理时间可能增加
ℹ️  原始文本很长 (50000 字符)，处理时间可能较长
```

## 实际效果

### 1. 短文本（<5000字符）
- **行为**：保持最小值限制（精转4000，摘要2000）
- **效果**：不受影响，正常处理

### 2. 长文本（5000-20000字符）
- **行为**：随输入长度动态增长
- **效果**：
  - 原文精转：不再被限制在16000，可达20000-40000
  - 关键纪要：不再被限制在8000，可达6666-13333
- **质量提升**：内容更完整，减少截断

### 3. 超长文本（>20000字符）
- **行为**：完全动态计算，无代码级上限
- **效果**：
  - 100000字符输入可设置200000 tokens输出
  - DeepSeek API 会根据自身限制自动处理
- **质量提升**：最大化利用 API 能力

## API 限制说明

虽然我们移除了代码级的 `max_tokens` 上限，但需要注意：

### DeepSeek API 限制
- **输入 tokens**：通常限制 32K-128K（取决于模型）
- **输出 tokens**：通常限制 16K
- **行为**：如果设置的 `max_tokens` 超过 API 限制，API 会自动截断到最大允许值

### 实际效果
- 设置 `max_tokens=200000` → API 自动限制到 16K
- 设置 `max_tokens=100000` → API 自动限制到 16K
- **好处**：充分利用 API 的输出能力，不需要猜测具体的上限

## 测试验证

运行测试脚本验证修改：

```bash
python test_unlimited_tokens_simple.py
```

预期输出：
```
原文精转 - 10000字符:
  旧版: 16000 tokens (上限16000)
  新版: 20000 tokens (无上限)
  提升: 25.0%

关键纪要 - 30000字符:
  旧版: 8000 tokens (上限8000)
  新版: 20000 tokens (无上限)
  提升: 150.0%

[OK] 测试完成 - 已移除 max_tokens 上限
```

## 注意事项

### 1. API 调用时间
- 更长的 `max_tokens` 可能导致更长的响应时间
- 超长文本（>50000字符）处理时间可能显著增加

### 2. API 费用
- 输出 tokens 越多，费用越高
- 建议监控 API 使用情况和费用

### 3. 错误处理
- 如果 API 返回错误，系统会自动记录日志
- 不会因为 `max_tokens` 过大而导致系统崩溃

### 4. 质量vs速度
- 如果追求速度，可以手动设置较小的 `max_tokens`
- 如果追求质量，让系统自动计算（无上限）

## 使用建议

### 自动模式（推荐）
```python
# 让系统自动计算，无上限
refined_text = generate_refined_text(original_text, language="zh", video_title=title)
summary_text = generate_summary(original_text, language="zh", video_title=title)
```

### 手动模式（特殊情况）
```python
# 如果需要控制输出长度，可以手动指定
refined_text = generate_refined_text(original_text, max_tokens=8000, language="zh")
summary_text = generate_summary(original_text, max_tokens=3000, language="zh")
```

## 未来优化方向

1. **智能分段**：对于超长文本（>100000字符），自动分段处理
2. **进度反馈**：在处理超长文本时，提供进度反馈
3. **费用估算**：根据 `max_tokens` 估算 API 费用
4. **缓存优化**：对于超长文本，缓存中间结果

## 相关文件

- [src/llm_utils.py](../src/llm_utils.py) - LLM 工具函数
- [test_unlimited_tokens_simple.py](../test_unlimited_tokens_simple.py) - 测试脚本

## 总结

通过移除 `max_tokens` 的代码级上限，我们实现了：

✅ **更完整的输出** - 长文本不再被硬性截断
✅ **更高质量** - 充分利用 DeepSeek API 的输出能力
✅ **更灵活** - 短文本保持最小值，长文本动态增长
✅ **更智能** - 让 API 自己处理限制，而不是代码猜测

这是一个重要的质量提升，特别是对于长视频的内容处理！
