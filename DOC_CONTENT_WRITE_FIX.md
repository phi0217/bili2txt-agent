# 文档内容写入功能修复

## 修复日期
2026-03-08

## 问题描述
文档链接可以打开，但文档内容为空。

## 根本原因
在 `doc_utils.py` 的 `create_document()` 函数中，步骤 2/3（写入文档内容）部分只有日志注释，**没有实际的内容写入代码**。

## 修复内容

### 之前的代码（只有注释）
```python
# ==================== 2. 向文档添加内容 ====================
logger.info("步骤 2/3: 写入文档内容")

# 获取文档的 page_id（通常是文档 ID 本身）
# 注意：需要先获取文档的块结构来找到 page_id，这里简化处理

# 由于 SDK 的限制，我们使用更简单的方法：直接更新文档
# 实际实现可能需要根据 SDK 版本调整

# 简化版本：使用文本块创建
# 注意：这个实现可能需要根据实际 SDK 版本调整
logger.info(f"   准备写入内容到文档: {document_id}")
logger.info(f"   内容长度: {len(content)} 字符")

# 由于飞书 SDK 的复杂性，这里提供一个基础实现
# 实际使用时可能需要根据具体 SDK 版本调整 API 调用方式
```

### 修复后的代码（实际写入）
```python
# ==================== 2. 向文档添加内容 ====================
logger.info("步骤 2/3: 写入文档内容")
logger.info(f"   准备写入内容到文档: {document_id}")
logger.info(f"   内容长度: {len(content)} 字符")

# ✅ 调用实际的内容写入函数
write_success = write_content_to_document(client, document_id, content)

if write_success:
    logger.info("✅ 文档内容写入成功")
else:
    logger.warning("⚠️  文档内容写入失败，文档将为空")
```

## 新增函数：write_content_to_document()

完整实现文档内容写入功能：

```python
def write_content_to_document(client: Client, document_id: str, content: str) -> bool:
    """
    向文档写入内容

    步骤：
    1. 将内容按段落分割（\n\n）
    2. 为每个段落创建文本块（TextBlock）
    3. 批量创建块到文档
    """
    try:
        from lark_oapi.api.docx.v1 import (
            CreateBlockRequest,
            CreateBlockRequestBody,
            BlockType,
            TextBlock
        )

        # 1. 分割内容为段落
        paragraphs = content.split('\n\n')
        logger.info(f"   内容分为 {len(paragraphs)} 个段落")

        # 2. 创建文本块
        text_blocks = []
        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text:
                continue

            # 创建文本块
            text_element = TextBlock.builder() \
                .text_element(para_text) \
                .build()

            text_blocks.append(text_element)

        # 3. 批量写入文档
        request = CreateBlockRequest.builder() \
            .document_id(document_id) \
            .block_type(BlockType.page) \
            .request_body(
                CreateBlockRequestBody.builder()
                .children(text_blocks)
                .build()
            ) \
            .build()

        response = client.docx.v1.document.block.create(request)

        if response.success():
            logger.info(f"   ✅ 成功写入 {len(text_blocks)} 个文本块")
            return True
        else:
            logger.warning(f"   ⚠️  写入内容失败: {response.code} {response.msg}")
            return False

    except Exception as e:
        logger.error(f"   ❌ 写入内容时发生错误: {e}")
        return False
```

## 工作原理

### 1. 内容格式化

在 `task.py` 中，内容会被格式化为 Markdown：

```python
from doc_utils import format_content_as_markdown

formatted_content = format_content_as_markdown(
    original_text,      # 原始识别文本
    refined_text,       # 精转后文本
    video_id            # 视频 ID
)
```

`format_content_as_markdown` 生成的内容格式：

```markdown
# B站视频转写结果

**视频ID**: BV1BTFFzmES1
**处理时间**: 2026-03-08 04:18:48
**来源**: bili2txt-agent 自动生成

---

## 【摘要】

（自动摘要功能开发中...）

## 【原文整理】

这里是精转后的文本内容...

---

## 附录：原始识别文本

这里是原始识别文本...

---

*本文档由 [bili2txt-agent](https://github.com/yourusername/bili2txt-agent) 自动生成*
```

### 2. 段落分割

```python
paragraphs = content.split('\n\n')
```

将 Markdown 内容按双换行符分割成段落数组：
- 段落 1：标题部分
- 段落 2：元数据
- 段落 3：分隔线
- 段落 4：摘要部分
- 段落 5：原文整理
- ... 等等

### 3. 创建文本块

每个段落创建一个 `TextBlock`：

```python
text_element = TextBlock.builder() \
    .text_element(para_text) \
    .build()
```

### 4. 批量写入

使用 `CreateBlockRequest` 批量创建块：

```python
request = CreateBlockRequest.builder() \
    .document_id(document_id) \
    .block_type(BlockType.page) \
    .request_body(
        CreateBlockRequestBody.builder()
        .children(text_blocks)
        .build()
    ) \
    .build()

response = client.docx.v1.document.block.create(request)
```

## 预期日志输出

### 成功情况

```
============================================================
开始创建飞书云文档
============================================================
步骤 1/3: 创建空文档
✅ 文档创建成功
   文档 ID: doxcnAbCdEfGhIjKlMnOpQrStUvW
步骤 2/3: 写入文档内容
   准备写入内容到文档: doxcnAbCdEfGhIjKlMnOpQrStUvW
   内容长度: 1234 字符
   正在写入文档内容...
   内容分为 15 个段落
   共创建 15 个文本块
   ✅ 成功写入 15 个文本块
✅ 文档内容写入成功
步骤 3/3: 设置文档公开访问权限
✅ 文档公开权限设置成功
============================================================
✅ 文档创建流程完成
============================================================
```

### 失败情况

```
步骤 2/3: 写入文档内容
   准备写入内容到文档: doxcnAbCdEfGhIjKlMnOpQrStUvW
   内容长度: 1234 字符
   正在写入文档内容...
   内容分为 15 个段落
   共创建 15 个文本块
   ⚠️  写入内容失败: 99991663 无权限
   文档将保持空白
⚠️  文档内容写入失败，文档将为空
```

## 常见问题

### Q1: 文档仍然为空怎么办？

**A:** 检查以下几点：

1. **查看日志**：确认是否看到 `✅ 成功写入 X 个文本块`
2. **检查权限**：飞书应用需要有 `docx:document` 权限
3. **SDK 版本**：确认使用的是最新版本的 `lark-oapi`

### Q2: 写入失败的常见错误码

| 错误码 | 错误信息 | 解决方案 |
|--------|---------|---------|
| `99991663` | 无权限 | 在飞书开放平台添加 `docx:document` 权限 |
| `99991401` | 应用未发布 | 创建并发布应用版本 |
| `99991368` | 参数错误 | 检查文档 ID 是否正确 |
| `400` | 请求参数错误 | 检查文本块格式是否正确 |

### Q3: 内容格式不对怎么办？

**A:** 检查 `format_content_as_markdown` 函数：

```python
# 确保 task.py 中调用了格式化函数
from doc_utils import format_content_as_markdown

formatted_content = format_content_as_markdown(
    original_text,
    refined_text,
    video_id
)
```

### Q4: 能否支持富文本格式？

**A:** 当前实现使用纯文本。未来可以扩展支持：
- 标题（H1, H2, H3）
- 加粗、斜体
- 列表
- 代码块
- 图片

这需要使用不同的块类型（如 `HeadingBlock`, `BulletBlock` 等）。

## 测试验证

### 1. 重启服务

```bash
# 按 Ctrl+C 停止服务
# 重新启动
python main.py
```

### 2. 发送测试视频

在飞书中发送一个 B站视频链接。

### 3. 检查日志

确认看到以下日志：
```
✅ 成功写入 X 个文本块
✅ 文档内容写入成功
```

### 4. 打开文档

点击生成的文档链接，确认：
- ✅ 文档有内容
- ✅ 格式正确（标题、段落等）
- ✅ 文本完整

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| [doc_utils.py](doc_utils.py) | ✅ 添加 `write_content_to_document()` 函数<br>✅ 在 `create_document()` 中调用内容写入 |

## 技术细节

### 飞书文档块（Block）类型

飞书文档使用块（Block）结构：

| 块类型 | 说明 | 用途 |
|--------|------|------|
| `page` | 页面块 | 文档的根容器 |
| `text` | 文本块 | 普通文本段落 |
| `heading1` | 一级标题 | # 标题 |
| `heading2` | 二级标题 | ## 标题 |
| `heading3` | 三级标题 | ### 标题 |
| `bullet` | 无序列表 | * 列表项 |
| `ordered` | 有序列表 | 1. 列表项 |
| `code` | 代码块 | `代码` |
| `quote` | 引用块 | > 引用 |
| `image` | 图片 | 图片嵌入 |

当前实现使用 `text` 类型，适用于纯文本内容。

### API 调用流程

```
1. CreateDocumentRequest → 创建空文档 → 获取 document_id
2. CreateBlockRequest → 批量创建文本块 → 写入内容
3. CreatePermissionPublicRequest → 设置公开权限 → 允许访问
```

## 后续优化

1. **支持富文本格式**
   - 标题（heading1/2/3）
   - 列表（bullet/ordered）
   - 加粗、斜体
   - 代码块

2. **添加图片支持**
   - 支持嵌入视频封面
   - 支持嵌入截图

3. **模板系统**
   - 可自定义文档模板
   - 支持不同格式（简历、报告等）

4. **增量更新**
   - 支持追加内容
   - 支持修改已有文档

## 总结

✅ **问题**：文档创建成功但内容为空
✅ **原因**：内容写入部分只有注释，没有实际代码
✅ **修复**：添加 `write_content_to_document()` 函数实现真实写入
✅ **效果**：文档现在应该包含完整的内容

---

**版本**: 1.0.0
**修复日期**: 2026-03-08
**维护**: bili2txt-agent 项目组
