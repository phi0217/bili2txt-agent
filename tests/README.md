# bili2txt-agent 测试

本目录包含项目的测试脚本和测试日志。

## 📋 测试列表

### 测试脚本

| 测试脚本 | 说明 | 运行方式 |
|---------|------|---------|
| [test_short_link.py](test_short_link.py) | B站短链接解析测试 | `python test_short_link.py` |
| [test_simple_write.py](test_simple_write.py) | 飞书文档写入简化测试 | `python test_simple_write.py` |
| [test_document_api.py](test_document_api.py) | 飞书文档 API 完整测试 | `python test_document_api.py` |
| [test_video_quality.py](test_video_quality.py) | B站视频清晰度测试（you-get） | `python test_video_quality.py` |
| [test_actual_download.py](test_actual_download.py) | 实际下载测试（you-get） | `python test_actual_download.py` |
| [diagnose_you_get.py](diagnose_you_get.py) | 🆕 you-get 诊断工具 | `python diagnose_you_get.py` |
| [test_yt_dlp.py](test_yt_dlp.py) | 🆕 yt-dlp 测试 | `python test_yt_dlp.py` |

### 测试日志

| 文件 | 说明 |
|------|------|
| [test_write.log](test_write.log) | 文档写入测试日志 |

## 🚀 快速开始

### 前置条件

1. 安装项目依赖
2. 配置 `.env` 文件（必需的环境变量）
3. 激活虚拟环境

### 运行测试

```bash
# 进入测试目录
cd tests

# 运行单个测试
python test_short_link.py

# 运行所有测试（Windows）
for %f in (test_*.py) do python %f

# 运行所有测试（Linux/macOS）
for f in test_*.py; do python "$f"; done
```

## 📝 测试说明

### 1. 短链接测试 (test_short_link.py)

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

### 2. 文档写入测试 (test_simple_write.py)

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

### 3. 文档 API 测试 (test_document_api.py)

**功能**：系统测试飞书文档 API

**测试内容**：
- 文档创建
- 文档信息获取
- 块结构获取
- 块子节点创建（3种方法）
- API 方法探索

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

## 🛠️ 开发新测试

### 测试模板

```python
#!/usr/bin/env python3
"""
测试描述
"""
import logging
import sys

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

- ✅ B站短链接解析
- ✅ 飞书文档创建
- ✅ 飞书文档内容写入
- ✅ API 调用方式验证

### 待添加

- ⏳ 视频下载测试
- ⏳ 音频提取测试
- ⏳ 语音识别测试
- ⏳ 文本精转测试
- ⏳ 完整流程测试

## 🔧 调试技巧

### 查看详细日志

```bash
# 设置 DEBUG 级别
python test_simple_write.py --log-level DEBUG
```

### 保留临时文件

```bash
# 不删除测试创建的文件
export KEEP_TEMP_FILES=1
python test_simple_write.py
```

### 单步调试

```bash
# 使用 Python 调试器
python -m pdb test_simple_write.py
```

## 🐛 常见问题

### Q: 测试失败怎么办？

A:
1. 检查环境变量配置
2. 查看测试日志
3. 确认网络连接
4. 验证 API 凭证

### Q: 如何查看详细错误？

A:
1. 查看控制台输出
2. 检查测试日志文件
3. 使用 `--verbose` 参数（如支持）

### Q: 测试创建了文档怎么办？

A:
- 文档写入测试会创建真实文档
- 可以手动删除测试文档
- 或配置测试专用的文档目录

## 📚 相关文档

- [项目结构说明](../docs/PROJECT_STRUCTURE.md)
- [飞书文档 API](../docs/FEISHU_DOC_WRITE_API_SOLUTION.md)
- [README](../README.md)

---

**最后更新**: 2026-03-08
**维护**: bili2txt-agent 项目组
