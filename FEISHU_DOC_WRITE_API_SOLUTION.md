# 飞书文档内容写入 API 解决方案

## 解决日期
2026-03-08

## 问题描述
文档创建成功但内容为空，多次尝试不同的 API 调用方式均失败。

## 根本原因
1. **错误 1**：使用了不存在的 API 类（如 `CreateBlockRequest`, `TextBlock`）
2. **错误 2**：API 调用路径错误（如 `client.docx.v1.document.block.children.create()`）
3. **错误 3**：缺少必需字段 `block_type`

## 正确的解决方案

### 1. 正确的数据结构

```python
from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun

# 创建文本内容（从内到外）
text_run = TextRun.builder().content("要写入的文本").build()
text_element = TextElement.builder().text_run(text_run).build()
text = Text.builder().elements([text_element]).build()

# 创建块（关键：设置 block_type=2）
block = Block.builder().block_type(2).text(text).build()
```

### 2. 正确的 API 调用方式

```python
from lark_oapi.api.docx.v1 import (
    CreateDocumentBlockChildrenRequest,
    CreateDocumentBlockChildrenRequestBody
)

# 创建请求
request = CreateDocumentBlockChildrenRequest.builder() \
    .document_id(document_id) \
    .block_id(document_id) \
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
        .children([block])  # 可以传入多个块
        .index(-1)          # -1 表示追加到末尾
        .build()
    ).build()

# 调用 API（正确路径）
response = client.docx.v1.document_block_children.create(request)
```

### 3. 关键发现：block_type 值

| block_type | 块类型 | 用途 |
|------------|--------|------|
| 2 | text | 普通文本段落 |
| 1 | page | 页面块 |
| 其他 | heading/bullet/ordered/code | 各种标题、列表、代码块 |

**重要**：`block_type=2` 是必需字段，否则会报错：
```
field validation failed: children[*].block_type is required
```

### 4. API 调用路径（经过验证）

```python
# ✅ 正确路径
client.docx.v1.document_block_children.create(request)

# ❌ 错误路径（尝试过但失败）
client.docx.v1.document.block.children.create()
client.docx.v1.document.block_children.create()
client.docx.v1.block_children.create()
request.create(client)
```

## 完整实现代码

### doc_utils.py 中的 write_content_to_document()

```python
def write_content_to_document(client: Client, document_id: str, content: str) -> bool:
    """向文档写入内容"""
    try:
        from lark_oapi.api.docx.v1 import (
            CreateDocumentBlockChildrenRequest,
            CreateDocumentBlockChildrenRequestBody
        )
        from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun

        # 1. 按段落分割内容
        paragraphs = content.split('\n\n')

        # 2. 为每个段落创建文本块
        blocks = []
        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text:
                continue

            # 创建文本块结构
            text_run = TextRun.builder().content(para_text).build()
            text_element = TextElement.builder().text_run(text_run).build()
            text = Text.builder().elements([text_element]).build()
            block = Block.builder().block_type(2).text(text).build()
            blocks.append(block)

        # 3. 批量写入
        request = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(document_id) \
            .block_id(document_id) \
            .request_body(
                CreateDocumentBlockChildrenRequestBody.builder()
                .children(blocks)
                .index(-1)
                .build()
            ).build()

        response = client.docx.v1.document_block_children.create(request)

        if response.success():
            logger.info(f"✅ 成功写入 {len(blocks)} 个文本块")
            return True
        else:
            logger.warning(f"⚠️ 写入失败: {response.code} {response.msg}")
            return False

    except Exception as e:
        logger.error(f"❌ 写入错误: {e}")
        return False
```

## 测试验证

### 测试脚本：test_simple_write.py

```bash
# 运行测试
.venv/Scripts/python.exe test_simple_write.py
```

**测试结果**：
- ✅ 文档创建成功：OyfodiEzsosCP6xXaKPc0LNanFb
- ✅ 内容写入成功：1 个文本块
- ✅ 文档链接可访问：https://my.feishu.cn/docx/OyfodiEzsosCP6xXaKPc0LNanFb

### 关键错误日志对比

**之前的错误**：
```
❌ AttributeError: type object 'Block' has no attribute 'block_type'
❌ field validation failed: children[*].block_type is required
```

**修复后**：
```
✅ 成功！内容写入成功
✅ 创建了 1 个块
```

## 调试过程

### 尝试 1：错误导入
```python
# ❌ 不存在的类
from lark_oapi.api.docx.v1 import CreateBlockRequest, TextBlock
```

### 尝试 2：错误 API 路径
```python
# ❌ 错误路径
response = client.docx.v1.document.block.children.create(request)
# AttributeError: 'Document' object has no attribute 'block'
```

### 尝试 3：缺少 block_type
```python
# ❌ 缺少必需字段
block = Block.builder().text(text).build()
# field validation failed: children[*].block_type is required
```

### 尝试 4：成功 ✅
```python
# ✅ 正确实现
block = Block.builder().block_type(2).text(text).build()
response = client.docx.v1.document_block_children.create(request)
```

## 技术要点

### Block 对象结构

```python
class Block:
    block_id: str          # 块 ID（创建后自动生成）
    parent_id: str         # 父块 ID
    children: List[str]    # 子块 ID 列表
    block_type: int        # ⭐ 块类型（2=文本，必需字段）
    text: Text             # 文本内容（如果 block_type=2）
    heading1: Text         # 一级标题（如果 block_type=3）
    # ... 其他块类型
```

### API 请求结构

```python
{
  "document_id": "doxcn...",
  "block_id": "doxcn...",      # 父块 ID（文档根节点）
  "body": {
    "children": [              # 要创建的块列表
      {
        "block_type": 2,       # ⭐ 必需：块类型
        "text": {              # 文本内容
          "elements": [
            {
              "text_run": {
                "content": "文本内容"
              }
            }
          ]
        }
      }
    ],
    "index": -1                # 插入位置（-1=末尾）
  }
}
```

## 后续优化建议

1. **支持更多块类型**
   ```python
   # 标题
   Block.builder().block_type(3).heading1(text).build()

   # 无序列表
   Block.builder().block_type(?).bullet(text).build()

   # 代码块
   Block.builder().block_type(?).code(text).build()
   ```

2. **支持富文本格式**
   ```python
   TextRun.builder()
       .content("加粗文本")
       .text_style(...)  # 样式设置
       .build()
   ```

3. **批量写入优化**
   - 飞书 API 支持一次创建多个块
   - 当前实现已使用批量创建

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| [doc_utils.py](doc_utils.py) | ✅ 实现 `write_content_to_document()` 函数<br>✅ 使用正确的 API 调用路径<br>✅ 设置 block_type=2 |
| [test_simple_write.py](test_simple_write.py) | ✅ 新增简化测试脚本<br>✅ 验证 API 调用方式 |

## 总结

✅ **问题**：文档创建成功但内容为空
✅ **根本原因**：
  - API 调用路径错误
  - 缺少必需字段 `block_type`
✅ **解决方案**：
  - 使用 `client.docx.v1.document_block_children.create()`
  - 设置 `block_type=2`（文本类型）
✅ **验证结果**：测试成功，文档内容正常写入

---

**版本**: 1.0.0
**解决日期**: 2026-03-08
**维护**: bili2txt-agent 项目组
