# 测试文件夹

这个文件夹包含 bili2txt-agent 项目的所有测试脚本。

## 测试文件列表

### 1. test_remove_max_tokens.py
测试删除 max_tokens 控制代码后的行为。

验证：
- 函数签名正确（保留 max_tokens 参数）
- API 调用逻辑正确（默认不设置 max_tokens）
- 只有明确指定时才设置 max_tokens

运行：
```bash
cd tests
python test_remove_max_tokens.py
```

### 2. test_video_title_simple.py
测试视频标题注入到 LLM 提示词中。

验证：
- `generate_refined_text()` 包含 `video_title` 参数
- `generate_summary()` 包含 `video_title` 参数
- 参数顺序正确

运行：
```bash
cd tests
python test_video_title_simple.py
```

### 3. test_unlimited_tokens_simple.py
测试 max_tokens 无上限功能。

验证：
- 不同长度文本的 max_tokens 计算
- 无代码级上限限制
- 充分利用 API 能力

运行：
```bash
cd tests
python test_unlimited_tokens_simple.py
```

### 4. test_max_tokens_unlimited.py
完整的 max_tokens 无上限功能测试。

包含详细的对比分析和效果说明。

运行：
```bash
cd tests
python test_max_tokens_unlimited.py
```

### 5. test_video_title_prompt.py
测试视频标题在提示词中的显示。

验证：
- 视频标题正确注入到提示词
- 提示词格式正确
- 无标题时正常工作

运行：
```bash
cd tests
python test_video_title_prompt.py
```

## 运行所有测试

从项目根目录运行：
```bash
# Windows PowerShell
cd tests
Get-ChildItem test_*.py | ForEach-Object { python $_.Name }

# Windows CMD
cd tests
for %f in (test_*.py) do python %f

# Linux/Mac
cd tests
for file in test_*.py; do python "$file"; done
```

## 测试输出说明

测试输出包含中文，可能需要在支持 UTF-8 的终端中运行：
- Windows PowerShell: 通常支持 UTF-8
- Windows CMD: 可能显示乱码，但不影响测试逻辑
- Linux/Mac Terminal: 完全支持

## 注意事项

1. **不需要 API 密钥**: 这些测试只验证函数签名和逻辑，不实际调用 API
2. **无网络依赖**: 所有测试都是离线测试
3. **快速执行**: 每个测试通常在 1-2 秒内完成

## 测试状态

| 测试文件 | 状态 | 说明 |
|---------|------|------|
| test_remove_max_tokens.py | ✅ | 验证 max_tokens 代码已删除 |
| test_video_title_simple.py | ✅ | 验证视频标题参数已添加 |
| test_unlimited_tokens_simple.py | ✅ | 验证无上限逻辑 |
| test_max_tokens_unlimited.py | ✅ | 详细对比测试 |
| test_video_title_prompt.py | ✅ | 验证提示词格式 |

## 添加新测试

如果要添加新的测试脚本：

1. 在 tests 文件夹中创建 `test_新功能.py`
2. 使用以下模板：
   ```python
   """
   测试描述
   """
   import sys
   import os

   # 添加 src 目录到 Python 路径
   project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   sys.path.insert(0, os.path.join(project_root, 'src'))

   from 模块名 import 函数名

   def test_功能():
       """测试说明"""
       # 测试代码
       pass

   if __name__ == "__main__":
       test_功能()
   ```
3. 更新本 README 文件，添加新测试的说明

## 相关文档

- [../docs/REMOVE_MAX_TOKENS_CONTROL.md](../docs/REMOVE_MAX_TOKENS_CONTROL.md) - 删除 max_tokens 控制代码说明
- [../docs/VIDEO_TITLE_IN_PROMPT.md](../docs/VIDEO_TITLE_IN_PROMPT.md) - 视频标题注入说明
- [../docs/MAX_TOKENS_UNLIMITED.md](../docs/MAX_TOKENS_UNLIMITED.md) - 无上限功能说明
