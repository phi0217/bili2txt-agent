# Placeholder 问题修复说明

## 修复日期
2026-03-08

## 问题描述
飞书机器人处理完视频后，生成的文档链接为 `https://www.feishu.cn/docx/placeholder`，其中 `placeholder` 是固定字符串，导致用户无法访问真实文档。

## 根本原因
在之前的实现中，虽然代码调用了飞书 API 创建文档，但：
1. 错误处理不够严格，API 失败时返回 `None` 而不是抛出异常
2. 缺少对 `document_id` 提取失败的明确处理
3. 日志不够详细，难以定位问题

## 修复内容

### 1. 增强错误处理（create_document 函数）

**修改前：**
```python
if not response.success():
    logger.error(f"创建文档失败: {response.code} {response.msg}")
    return None  # ❌ 返回 None，调用者无法区分是 API 失败还是其他问题
```

**修改后：**
```python
if not response.success():
    error_msg = f"❌ 创建文档失败: code={response.code}, msg={response.msg}"
    logger.error(error_msg)
    if hasattr(response, 'error') and response.error:
        logger.error(f"   详细错误: {response.error}")
    raise Exception(error_msg)  # ✅ 抛出异常，强制调用者处理
```

**改进点：**
- ✅ API 失败时抛出异常而非返回 `None`
- ✅ 记录详细的错误码和错误信息
- ✅ 如果响应中有 `error` 字段，也记录下来
- ✅ 使用 `logger.exception()` 在外层捕获异常时记录完整堆栈

---

### 2. 正确提取 document_id

**关键代码：**
```python
# 只有确认 API 调用成功后，才提取 document_id
if not response.success():
    raise Exception(...)

document_id = response.data.document.document_id
logger.info(f"✅ 文档创建成功")
logger.info(f"   文档 ID: {document_id}")
```

**改进点：**
- ✅ 在 `response.success()` 确认后才提取 `document_id`
- ✅ 添加日志记录提取到的文档 ID
- ✅ 如果提取失败，会抛出异常（`response.data` 为 `None` 时会触发 `AttributeError`）

---

### 3. 避免 placeholder 硬编码

**修改前的风险代码（task.py 中）：**
```python
# 5. 创建飞书文档并获取分享链接
# TODO: 实际创建文档
share_url = "https://www.feishu.cn/docx/placeholder"  # ❌ 硬编码占位符
```

**修改后（已移除）：**
此占位符代码已在 `task.py` 中被移除，替换为真实的文档创建调用。

**在 get_document_share_url 中的验证：**
```python
if not document_id:
    error_msg = "❌ 无法生成文档链接: document_id 为空"
    logger.error(error_msg)
    raise ValueError(error_msg)  # ✅ 抛出异常，避免生成无效链接
```

**改进点：**
- ✅ 移除所有 `placeholder` 硬编码
- ✅ 如果 `document_id` 为空，抛出异常
- ✅ 确保生成的每个链接都包含真实的文档 ID

---

### 4. 确保链接拼接正确

**修改前：**
```python
share_url = f"{config.FEISHU_DOMAIN}/docx/{document_id}"
```

**修改后：**
```python
# 确保域名末尾没有斜杠
domain = config.FEISHU_DOMAIN.rstrip('/') if config.FEISHU_DOMAIN else "https://www.feishu.cn"
share_url = f"{domain}/docx/{document_id}"
```

**改进点：**
- ✅ 使用 `rstrip('/')` 移除域名末尾的斜杠
- ✅ 如果 `FEISHU_DOMAIN` 未配置，使用默认值
- ✅ 添加详细的日志输出

---

### 5. 详细的日志输出

**新增的日志信息：**
```python
logger.info("=" * 60)
logger.info("开始创建飞书云文档")
logger.info("=" * 60)

logger.info("步骤 1/3: 创建空文档")
logger.info(f"✅ 文档创建成功")
logger.info(f"   文档 ID: {document_id}")

logger.info("步骤 2/3: 写入文档内容")
logger.info(f"   准备写入内容到文档: {document_id}")
logger.info(f"   内容长度: {len(content)} 字符")

logger.info("步骤 3/3: 设置文档公开访问权限")

logger.info("✅ 文档分享链接生成成功")
logger.info(f"   使用域名: {domain}")
logger.info(f"   文档 ID: {document_id}")
logger.info(f"   完整链接: {share_url}")
```

**日志输出示例：**
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
步骤 3/3: 设置文档公开访问权限
✅ 文档公开权限设置成功
============================================================
✅ 文档创建流程完成
============================================================
✅ 文档分享链接生成成功
   使用域名: https://my.feishu.cn
   文档 ID: doxcnAbCdEfGhIjKlMnOpQrStUvW
   完整链接: https://my.feishu.cn/docx/doxcnAbCdEfGhIjKlMnOpQrStUvW
```

**改进点：**
- ✅ 使用分隔线使日志更清晰
- ✅ 分步骤记录进度
- ✅ 记录关键数据（文档 ID、内容长度、域名等）
- ✅ 使用 emoji 标记成功（✅）和失败（❌）

---

### 6. 域名配置建议

**新增警告日志：**
```python
# 如果域名是默认值，给出警告
if not config.FEISHU_DOMAIN or config.FEISHU_DOMAIN == "https://www.feishu.cn":
    logger.warning("⚠️  使用默认域名 https://www.feishu.cn")
    logger.warning("⚠️  建议在 .env 文件中配置 FEISHU_DOC_DOMAIN:")
    logger.warning("   - 中国大陆: FEISHU_DOMAIN=https://my.feishu.cn")
    logger.warning("   - 海外版:   FEISHU_DOMAIN=https://my.feishu.com")
```

**配置建议：**
- **中国大陆用户**：在 `.env` 文件中设置 `FEISHU_DOMAIN=https://my.feishu.cn`
- **海外版用户**：在 `.env` 文件中设置 `FEISHU_DOMAIN=https://my.feishu.com`

**为什么需要修改域名？**
- `www.feishu.cn` 是飞书官网首页，不是文档访问域名
- `my.feishu.cn` 是飞书文档的访问域名（中国大陆）
- `my.feishu.com` 是飞书文档的访问域名（海外版）
- 配置错误会导致用户点击链接后显示"文档不存在"

---

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `doc_utils.py` | ✅ 增强错误处理<br>✅ 正确提取 document_id<br>✅ 移除 placeholder 硬编码<br>✅ 详细日志输出<br>✅ 域名配置警告 |
| `task.py` | ✅ 移除 placeholder 硬编码<br>✅ 调用真实文档创建（已在之前完成） |

---

## 保持不变的部分

✅ **配置结构**：保持 `FEISHU_DOMAIN` 单一配置，不拆分 API 域名和文档域名
✅ **文档内容写入**：不修改（保持原有实现）
✅ **权限设置**：不修改（保持原有实现）

---

## 测试验证

### 1. 检查日志输出

运行程序后，查看日志中是否包含：
```
✅ 文档创建成功
   文档 ID: doxcnXXXXXXXXXXXXXXXXXX
✅ 文档分享链接生成成功
   完整链接: https://my.feishu.cn/docx/doxcnXXXXXXXXXXXXXXXXXX
```

### 2. 验证链接可访问

点击生成的链接，确认：
- ✅ 文档可以打开
- ✅ 显示正确的内容
- ✅ 没有显示"文档不存在"

### 3. 检查 .env 配置

```bash
# 查看 .env 文件
cat .env | grep FEISHU_DOMAIN

# 应该看到：
# FEISHU_DOMAIN=https://my.feishu.cn  （中国大陆）
# 或
# FEISHU_DOMAIN=https://my.feishu.com  （海外版）
```

---

## 常见问题

### Q1: 如果仍然生成 placeholder 链接怎么办？

**A:** 检查 `task.py` 文件，确保已经移除了以下代码：
```python
# 如果还在使用这个，需要替换
share_url = "https://www.feishu.cn/docx/placeholder"
```

应该替换为：
```python
from doc_utils import create_and_share_document
from feishu_handler import get_feishu_client

feishu_client = get_feishu_client()
share_url = create_and_share_document(feishu_client, formatted_content)
```

### Q2: 生成的链接无法访问怎么办？

**A:** 检查以下几点：
1. `.env` 文件中的 `FEISHU_DOMAIN` 配置是否正确
2. 中国大陆应为 `https://my.feishu.cn`
3. 海外版应为 `https://my.feishu.com`
4. 查看日志中的"使用域名"是否正确

### Q3: API 调用失败怎么办？

**A:** 查看日志中的错误信息：
```
❌ 创建文档失败: code=XXXXXX, msg=XXXXX
```

常见错误码：
- `99991663` - 权限不足，需要在飞书开放平台添加权限
- `99991401` - 应用未发布，需要创建并发布版本
- `99991368` - 参数错误

---

## 总结

本次修复专注于解决 **placeholder 问题**，通过以下改进确保文档链接的正确性：

1. ✅ **增强错误处理**：API 失败时抛出异常
2. ✅ **正确提取 document_id**：从 API 响应中正确获取
3. ✅ **移除占位符**：彻底消除 `placeholder` 硬编码
4. ✅ **详细日志**：记录每一步的关键信息
5. ✅ **域名建议**：引导用户配置正确的文档访问域名

**不修改的部分**：
- ✅ 保持现有配置结构（单一 `FEISHU_DOMAIN`）
- ✅ 保持文档内容写入逻辑
- ✅ 保持权限设置逻辑

---

**版本**: 1.0.0
**修复日期**: 2026-03-08
**维护**: bili2txt-agent 项目组
