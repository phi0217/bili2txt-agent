# bili2txt-agent 测试

本目录包含项目的测试脚本和测试日志。

## 📋 测试列表

### 核心测试

| 测试脚本 | 说明 | 运行方式 |
|---------|------|---------|
| [test_yt_dlp.py](test_yt_dlp.py) | yt-dlp 下载器功能测试 | `python test_yt_dlp.py` |
| [test_integration.py](test_integration.py) | 完整集成测试 | `python test_integration.py` |
| [test_short_link.py](test_short_link.py) | B站短链接解析测试 | `python test_short_link.py` |
| [test_simple_write.py](test_simple_write.py) | 飞书文档写入测试 | `python test_simple_write.py` |
| [test_document_api.py](test_document_api.py) | 飞书文档 API 测试 | `python test_document_api.py` |

### 测试日志

| 文件 | 说明 |
|------|------|
| [test_write.log](test_write.log) | 文档写入测试日志 |
| [test_integration.log](test_integration.log) | 集成测试日志 |

## 🚀 快速开始

### 前置条件

1. 安装项目依赖
2. 配置 `.env` 文件（必需的环境变量）
3. 激活虚拟环境

### 运行所有测试

```bash
# 进入测试目录
cd tests

# 运行集成测试（推荐）
python test_integration.py

# 运行单个测试
python test_yt_dlp.py
python test_short_link.py
```

## 📝 测试说明

### 1. yt-dlp 测试 (test_yt_dlp.py)

**功能**：测试 yt-dlp 下载器功能

**测试内容**：
- 格式列表获取
- 格式选择验证
- 音频下载测试

**运行**：
```bash
python test_yt_dlp.py
```

**预期输出**：
```
✅ 音频下载成功
   文件: ./temp/视频标题.mp3
   大小: 1.23MB
```

### 2. 集成测试 (test_integration.py)

**功能**：测试完整的系统集成

**测试内容**：
- 音频下载功能测试
- task.py 集成测试
- 完整工作流程模拟

**运行**：
```bash
python test_integration.py
```

**预期输出**：
```
============================================================
测试 1: 音频下载功能
============================================================
✅ 音频下载成功！

============================================================
测试 2: task.py 集成测试
============================================================
✅ task.py 已正确集成 yt-dlp 下载器

============================================================
测试 3: 模拟完整工作流程
============================================================
✅ 完整流程测试成功

🎉 所有测试通过！
```

### 3. 短链接测试 (test_short_link.py)

**功能**：测试 B站短链接解析功能

**测试内容**：
- 短链接重定向解析
- 视频 ID 提取
- 递归重定向处理

**运行**：
```bash
python test_short_link.py
```

**预期输出**：
```
✅ 短链接解析成功
最终 URL: https://www.bilibili.com/video/BV1xx...
视频 ID: BV1xx...
```

### 4. 文档写入测试 (test_simple_write.py)

**功能**：测试飞书文档内容写入

**测试内容**：
- 创建空文档
- 写入文本内容
- 生成分享链接

**运行**：
```bash
python test_simple_write.py
```

**预期输出**：
```
✅ 文档创建成功
✅ 内容写入成功
🔗 文档链接: https://...
```

**注意**：
- 需要配置有效的飞书应用凭证
- 会创建真实的飞书文档

### 5. 文档 API 测试 (test_document_api.py)

**功能**：系统测试飞书文档 API

**测试内容**：
- 文档创建
- 文档信息获取
- 块结构获取
- 块子节点创建

**运行**：
```bash
python test_document_api.py
```

**预期输出**：
```
============================================================
测试 1: 创建空文档
============================================================
✅ 文档创建成功

============================================================
测试 2: 获取文档信息
============================================================
✅ 文档信息获取成功
...
```

## 🎯 测试优先级

### 推荐测试顺序

1. **test_integration.py** - 首选，验证完整集成
2. **test_yt_dlp.py** - 验证下载功能
3. **test_short_link.py** - 验证链接解析
4. **test_simple_write.py** - 验证文档创建
5. **test_document_api.py** - 深入测试 API

### 快速验证

```bash
# 5分钟快速验证
cd tests
python test_integration.py

# 查看结果
# 如果看到 "🎉 所有测试通过！" 说明系统正常
```

## 🛠️ 开发新测试

### 测试模板

```python
#!/usr/bin/env python3
"""
测试描述
"""
import logging
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主测试函数"""
    logger.info("开始测试")

    try:
        # 测试逻辑
        logger.info("✅ 测试通过")
        return 0
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 测试命名规范

- 文件名：`test_<功能>.py`
- 函数名：描述性名称
- 日志：使用 logger 记录关键步骤

### 测试要求

1. **独立性**：每个测试应该独立运行
2. **清晰性**：有明确的测试目的和预期结果
3. **日志**：输出详细的测试过程
4. **错误处理**：捕获并记录异常

## 📊 测试覆盖率

### 当前覆盖

- ✅ yt-dlp 音频下载
- ✅ 系统集成测试
- ✅ B站短链接解析
- ✅ 飞书文档创建
- ✅ 飞书文档内容写入
- ✅ API 调用方式验证

### 待添加

- ⏳ Whisper 语音识别测试
- ⏳ DeepSeek 文本精转测试
- ⏳ 完整流程端到端测试

## 🔧 调试技巧

### 查看详细日志

```bash
# 修改测试脚本中的日志级别
logging.basicConfig(level=logging.DEBUG)
```

### 保留临时文件

```bash
# 测试后不删除临时文件
# 修改测试脚本，注释掉清理代码
# os.remove(audio_path)
```

### 单步调试

```bash
# 使用 Python 调试器
python -m pdb test_simple_write.py
```

## 🐛 常见问题

### Q: 测试失败怎么办？

A:
1. 检查环境变量配置（`.env` 文件）
2. 查看测试日志（`*.log` 文件）
3. 确认网络连接
4. 验证 API 凭证

### Q: yt-dlp 测试失败？

A:
```bash
# 确认 yt-dlp 已安装
pip install yt-dlp

# 验证安装
yt-dlp --version
```

### Q: 集成测试失败？

A:
1. 确认所有依赖已安装
2. 检查 `.env` 配置
3. 查看日志文件 `test_integration.log`
4. 单独运行各个子测试

### Q: 文档测试创建了真实文档？

A:
- 是的，文档测试会创建真实文档
- 可以手动删除测试文档
- 或使用测试专用的飞书应用

## 📚 相关文档

- [配置指南](../docs/CONFIGURATION.md) - 环境变量配置
- [视频下载方案](../docs/VIDEO_DOWNLOAD.md) - yt-dlp 使用说明
- [飞书文档创建](../docs/FEISHU_DOCS.md) - 文档 API 说明
- [常见问题解答](../docs/FAQ.md) - 故障排除
- [项目结构说明](../docs/PROJECT_STRUCTURE.md) - 代码组织

## 📝 测试报告模板

```markdown
## 测试日期：2026-03-09

### 测试环境
- Python 版本：3.11.0
- 操作系统：Windows 11
- yt-dlp 版本：2024.01.01

### 测试结果
- ✅ test_integration.py - 通过
- ✅ test_yt_dlp.py - 通过
- ✅ test_short_link.py - 通过
- ✅ test_simple_write.py - 通过
- ✅ test_document_api.py - 通过

### 问题记录
无

### 备注
所有测试正常通过
```

---

**最后更新**: 2026-03-09
**维护**: bili2txt-agent 项目组
