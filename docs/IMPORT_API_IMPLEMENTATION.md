# 飞书文档Import API实现说明

## 概述

从 v2.1.0 开始，项目引入了**飞书Import API**，支持将Markdown文件上传到飞书云空间，由飞书自动转换为docx格式。相比之前的Block-based API，新方案能够**完美渲染Markdown格式**。

## 实现架构

### 双方案架构

系统采用**优先使用 + 自动回退**的架构：

```
创建文档请求
    ↓
优先尝试: Import API（Markdown完美渲染）
    ↓ (失败)
自动回退: Block-based API（备用方案）
    ↓
至少保证文档能创建成功
```

### 方案对比

| 维度 | Import API (推荐) | Block-based API (备用) |
|------|-------------------|----------------------|
| **格式渲染** | ✅ 完美渲染Markdown | ❌ 纯文本显示 |
| **标题层级** | ✅ 自动转换 | ❌ 显示为 # ## ### |
| **列表** | ✅ 自动识别 | ❌ 显示为 - 1. |
| **加粗/斜体** | ✅ 正确显示 | ❌ 显示为 ** * |
| **代码块** | ✅ 语法高亮 | ❌ 纯文本 |
| **代码复杂度** | ✅ 简单（直接上传） | ❌ 复杂（构建Block） |
| **处理速度** | ⚠️  稍慢（3-10秒） | ✅ 快（1-3秒） |
| **网络依赖** | ❌ 高（需上传文件） | ✅ 低（直接API） |
| **可靠性** | ⚠️  依赖外部服务 | ✅ 稳定 |

## 实现流程

### Import API完整流程

```
1. 保存Markdown临时文件
   ├─ 创建 temp/markdown/ 目录
   ├─ 生成文件名: {timestamp}_{video_id}_{doc_type}.md
   └─ 写入Markdown内容

2. 上传文件到飞书云空间
   ├─ 检查文件大小（<20MB使用小文件上传）
   ├─ 调用 upload_all API
   └─ 获取 file_token

3. 创建导入任务
   ├─ 调用 import_task.create API
   ├─ 传入 file_token、file_type、title
   └─ 获取 task_id

4. 轮询导入状态
   ├─ 每2秒查询一次任务状态
   ├─ 超时时间: 30秒
   └─ 等待状态变为 success

5. 获取文档链接
   ├─ 提取 document_id
   ├─ 构造分享链接
   └─ 设置公开权限

6. 清理临时文件
   └─ 删除本地 .md 文件
```

## 代码结构

### 核心函数（src/doc_utils.py）

#### 1. 自定义异常类

```python
class FileUploadError(Exception):
    """文件上传失败异常"""

class ImportTaskError(Exception):
    """导入任务创建失败异常"""

class PollingTimeoutError(Exception):
    """导入状态轮询超时异常"""

class DocumentCreationError(Exception):
    """文档创建失败异常"""
```

#### 2. Import API相关函数

```python
def save_markdown_temp_file(content: str, video_id: str, doc_type: str) -> str:
    """
    保存Markdown内容为临时文件

    Args:
        content: Markdown文本内容
        video_id: 视频ID
        doc_type: 文档类型（"refined" 或 "summary"）

    Returns:
        保存的文件路径

    Raises:
        IOError: 文件写入失败
    """

def upload_file_to_feishu(client: Client, file_path: str) -> str:
    """
    上传文件到飞书云空间（小文件，<20MB）

    Args:
        client: 飞书客户端
        file_path: 本地文件路径

    Returns:
        file_token: 文件在上传后的标识

    Raises:
        FileUploadError: 上传失败
    """

def create_import_task(client: Client, file_token: str, title: str) -> str:
    """
    创建导入任务，将上传的文件转换为飞书文档

    Args:
        client: 飞书客户端
        file_token: 上传文件后返回的token
        title: 目标文档标题

    Returns:
        task_id: 导入任务ID

    Raises:
        ImportTaskError: 导入任务创建失败
    """

def poll_import_status(client: Client, task_id: str, timeout: int = 30) -> str:
    """
    轮询导入任务状态，直到完成或超时

    Args:
        client: 飞书客户端
        task_id: 导入任务ID
        timeout: 超时时间（秒）

    Returns:
        document_id: 导入成功后的文档ID

    Raises:
        PollingTimeoutError: 轮询超时
        ImportTaskError: 导入失败
    """

def create_document_via_import(client: Client, content: str, title: str) -> str:
    """
    使用导入API创建文档（推荐方式）

    流程：
    1. 保存Markdown临时文件
    2. 上传文件到飞书云空间
    3. 创建导入任务
    4. 轮询导入状态
    5. 返回文档ID

    Args:
        client: 飞书客户端
        content: Markdown格式的内容
        title: 文档标题

    Returns:
        document_id: 创建的文档ID

    Raises:
        DocumentCreationError: 文档创建失败
    """
```

#### 3. Block-based API函数（备用）

```python
def create_document_via_blocks(client: Client, content: str, title: str) -> Optional[str]:
    """
    使用Block-based API创建飞书云文档（备用方案）

    注意：此方式无法完美渲染Markdown格式
    """
```

#### 4. 主入口函数（带回退机制）

```python
def create_and_share_document(client: Client, content: str, title: str) -> Optional[str]:
    """
    创建文档并返回分享链接（一步完成）

    优先使用Import API，失败时自动回退到Block-based API

    Returns:
        文档分享链接，失败则返回 None
    """
```

## 使用示例

### 基本使用（无需修改）

```python
from feishu_handler import get_feishu_client
from doc_utils import create_and_share_document

# 获取飞书客户端
client = get_feishu_client()

# 创建文档（自动选择最佳方案）
content = """# 标题

这是**加粗**文本。

- 列表1
- 列表2
"""

share_url = create_and_share_document(client, content, "文档标题")
```

### 直接使用Import API

```python
from doc_utils import create_document_via_import

# 直接使用Import API（失败会抛出异常）
document_id = create_document_via_import(client, content, title)
```

### 强制使用Block-based API

```python
from doc_utils import create_document_via_blocks

# 强制使用备用方案
document_id = create_document_via_blocks(client, content, title)
```

## 测试

### 运行测试

```bash
cd tests
python test_import_api.py
```

### 测试用例

1. **test_save_markdown_temp_file**: 测试Markdown文件保存
2. **test_upload_file_to_feishu**: 测试文件上传到飞书云空间
3. **test_create_import_task**: 测试导入任务创建
4. **test_poll_import_status**: 测试导入状态轮询
5. **test_create_document_via_import**: 测试完整Import API流程
6. **test_create_and_share_document**: 测试带回退机制的完整流程

## 错误处理

### 失败场景与处理

| 失败点 | 可能原因 | 处理方式 |
|--------|----------|----------|
| 文件保存 | 磁盘空间不足、权限问题 | 抛出IOError |
| 文件上传 | 网络问题、文件过大、飞书云空间异常 | 抛出FileUploadError，回退到Block-based |
| 导入任务 | file_token无效、飞书服务异常 | 抛出ImportTaskError，回退到Block-based |
| 状态轮询 | 飞书处理缓慢、超时 | 抛出PollingTimeoutError，回退到Block-based |
| 文档链接生成 | document_id提取失败 | 抛出DocumentCreationError |

### 用户友好的错误提示

```
✅ 处理完成！

📹 视频ID：BV1xx411c7mD
⚠️  注意: 使用备用方案创建，Markdown格式可能无法完美渲染

🔗 文档链接：https://my.feishu.cn/docx/doxcnxxxxxxxx
```

## 性能优化

### 当前实现

- **文件上传**: 小文件上传（<20MB）
- **轮询间隔**: 2秒
- **超时时间**: 30秒
- **临时文件**: 自动清理

### 未来优化

1. **大文件分块上传**: 支持大于20MB的文件
2. **并发导入**: 两个文档并发创建
3. **进度提示**: 实时显示导入进度
4. **智能重试**: 失败时自动重试（带退避策略）

## 常见问题

### Q1: Import API失败率高怎么办？

**A**: 系统会自动回退到Block-based API，至少保证文档能创建成功。如果频繁失败，检查：
- 网络连接是否稳定
- 飞书云空间服务是否正常
- 文件大小是否超过限制

### Q2: 如何确认使用了哪种方案？

**A**: 查看日志输出：
- Import API: `"使用导入API创建文档（推荐方式）"`
- Block-based API: `"使用Block-based API创建文档（备用方案）"`

### Q3: 临时文件会占用多少空间？

**A**: 每个Markdown文件约10-100KB，处理完成后自动删除。可以在 `temp/markdown/` 目录查看。

### Q4: 可以强制使用Import API吗？

**A**: 可以直接调用 `create_document_via_import()` 函数，但需要注意异常处理。

## 版本历史

- **v2.1.0** (2026-03-08): 初始实现Import API支持
  - 新增 `save_markdown_temp_file()`
  - 新增 `upload_file_to_feishu()`
  - 新增 `create_import_task()`
  - 新增 `poll_import_status()`
  - 新增 `create_document_via_import()`
  - 重命名 `create_document()` → `create_document_via_blocks()`
  - 修改 `create_and_share_document()` 实现自动回退

## 参考资料

- [飞书导入任务API](https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create)
- [飞书文件上传API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/file/upload_all)
- [lark-oapi Python SDK](https://github.com/larksuite/oapi-sdk-python)

## 贡献

如有问题或建议，欢迎提交Issue或Pull Request！
