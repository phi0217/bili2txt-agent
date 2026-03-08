# 飞书文档创建

## 概述

bili2txt-agent 使用飞书开放平台的 lark-oapi SDK 创建和管理文档。

## 功能特性

- ✅ **自动创建文档** - 自动创建飞书云文档
- ✅ **内容写入** - 支持 Markdown 格式内容写入
- ✅ **自动分享** - 设置文档为公开可访问
- ✅ **域名分离** - 支持自定义文档访问域名

## 架构设计

### 核心模块

```
doc_utils.py                 # 文档创建和内容写入
├── create_and_share_document()  # 创建+分享一站式
├── create_document()            # 创建空文档
├── write_content_to_document()   # 写入内容
├── set_document_public()          # 设置公开权限
└── get_document_share_url()      # 生成分享链接
```

### 文档结构

飞书文档采用 **块（Block）** 结构：

```
Document（文档）
  └─ Block（块）
      ├─ block_type: 2 (文本)
      └─ text（文本内容）
          └─ elements（元素列表）
              └─ TextElement（文本元素）
                  └─ text_run（文本片段）
                      └─ content: "文本内容"
```

## API 调用方式

### 创建块子节点

**正确的 API 调用路径**：

```python
from lark_oapi.api.docx.v1 import CreateDocumentBlockChildrenRequest, CreateDocumentBlockChildrenRequestBody
from lark_oapi.api.docx.v1.model import Block, Text, TextElement, TextRun

# 1. 创建文本内容
text_run = TextRun.builder().content("要写入的文本").build()
text_element = TextElement.builder().text_run(text_run).build()
text = Text.builder().elements([text_element]).build()

# 2. 创建块（重要：设置 block_type=2）
block = Block.builder().block_type(2).text(text).build()

# 3. 创建请求
request = CreateDocumentBlockChildrenRequest.builder() \
    .document_id(document_id) \
    .block_id(document_id) \
    .request_body(
        CreateDocumentBlockChildrenRequestBody.builder()
        .children([block])
        .index(-1)
        .build()
    ).build()

# 4. 调用 API（正确路径）
response = client.docx.v1.document_block_children.create(request)
```

**关键点**：
- ✅ `block_type=2` - 必需字段（表示文本类型）
- ✅ API 路径：`client.docx.v1.document_block_children.create()`

## 实现代码

### 创建文档并写入内容

```python
from doc_utils import create_and_share_document
from feishu_handler import get_feishu_client

# 获取客户端
feishu_client = get_feishu_client()

# 准备内容
content = """
# 视频转写结果

**视频ID**: BV1xx411c7mD

## 【摘要】

这里是摘要内容...

## 【原文整理】

这里是正文内容...
"""

# 创建文档并获取分享链接
share_url = create_and_share_document(feishu_client, content)

print(f"文档链接: {share_url}")
```

### 自定义文档域名

通过环境变量配置文档访问域名：

```bash
# .env 文件
FEISHU_DOC_DOMAIN=https://my.feishu.cn
```

生成的文档链接：
```
https://my.feishu.cn/docx/xxxxxxxx
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FEISHU_APP_ID` | 飞书应用ID | 必需 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 必需 |
| `FEISHU_DOMAIN` | API 域名 | `https://open.feishu.cn` |
| `FEISHU_DOC_DOMAIN` | 文档域名 | `https://my.feishu.cn` |

### 权限要求

飞书应用需要以下权限：

- `im:message` - 接收和发送消息
- `docx:document` - 创建和管理文档
- `drive:drive` - 文档公开访问

## 使用示例

### 示例1：创建简单文档

```python
from doc_utils import create_and_share_document

content = """
# 测试文档

这是一个简单的测试文档。
"""

share_url = create_and_share_document(client, content)
```

### 示例2：创建复杂文档

```python
from doc_utils import format_content_as_markdown

# 格式化内容
content = format_content_as_markdown(
    original_text="原始识别文本...",
    refined_text="精转后文本...",
    video_id="BV1xx411c7mD"
)

# 创建文档
share_url = create_and_share_document(client, content)
```

## 故障排除

### Q1: 文档创建失败

**错误信息**：
```
field validation failed: children[*].block_type is required
```

**解决方案**：确保设置了 `block_type=2`

```python
block = Block.builder().block_type(2).text(text).build()
```

### Q2: 文档链接打不开

**可能原因**：
1. 文档未设置公开权限
2. 域名配置错误
3. 网络问题

**检查方法**：
1. 确认 `set_document_public()` 被调用
2. 检查 `FEISHU_DOC_DOMAIN` 配置
3. 手动在浏览器中打开链接测试

### Q3: 内容写入失败

**错误信息**：
```
AttributeError: type object 'Block' has no attribute 'block_type'
```

**解决方案**：
- 检查 lark-oapi SDK 版本
- 使用正确的 Block 类
- 参考 [VIDEO_DOWNLOAD.md](VIDEO_DOWNLOAD.md) 中的示例

### Q4: API 调用路径错误

**常见错误**：
```python
# ❌ 错误路径
client.docx.v1.document.block.children.create()

# ✅ 正确路径
client.docx.v1.document_block_children.create()
```

## 技术细节

### 文档块类型

| block_type | 类型名称 | 用途 |
|-----------|---------|------|
| 1 | Page | 页面块 |
| **2** | **Text** | **文本块** |
| 3 | Heading1 | 一级标题 |
| 4 | Heading2 | 二级标题 |
| 11 | Bullet | 无序列表 |
| 12 | Ordered | 有序列表 |

### API 请求结构

```python
{
    "document_id": "doxcnxxxxxxxx",
    "block_id": "doxcnxxxxxxxx",  # 父块ID（通常是document_id）
    "body": {
        "children": [              # 块列表
            {
                "block_type": 2,     # 必需：块类型
                "text": {            # 文本内容
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
        "index": -1              # 插入位置（-1=末尾）
    }
}
```

## 开发历史

### v1.0 初始版本

- 使用占位符链接
- 无法写入内容
- 文档为空

### v2.0 问题修复

**问题1**: 占位符链接
- **原因**: task.py 使用硬编码占位符
- **修复**: 调用真实的文档创建API
- **结果**: 链接可访问，但内容为空

**问题2**: 内容写入失败
- **原因**: 缺少 `block_type` 字段
- **修复**: 设置 `block_type=2`
- **结果**: 内容成功写入

**问题3**: API 调用路径错误
- **原因**: 使用了错误的API路径
- **修复**: 使用 `client.docx.v1.document_block_children.create()`
- **结果**: API调用成功

## 相关文档

- [项目结构说明](PROJECT_STRUCTURE.md) - 代码组织
- [配置指南](CONFIGURATION.md) - 环境变量配置
- [视频下载方案](VIDEO_DOWNLOAD.md) - 音频下载

## 参考资料

- [飞书开放平台文档](https://open.feishu.cn/)
- [lark-oapi SDK 文档](https://github.com/larksuite/oapi-sdk-python)
- [飞书文档 API 参考](https://open.feishu.cn/document/server/docs03/docs/docx/docx/document/)

---

**最后更新**: 2026-03-09
**版本**: 2.0.0
**维护**: bili2txt-agent 项目组
