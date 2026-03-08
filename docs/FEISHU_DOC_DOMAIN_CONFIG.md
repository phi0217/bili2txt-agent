# FEISHU_DOC_DOMAIN 配置说明

## 修改日期
2026-03-08

## 为什么需要这个配置？

为了解决文档链接生成问题，同时**不影响现有的 API 调用**。

## 配置项说明

### FEISHU_DOC_DOMAIN（新增）
- **用途**：专门用于生成**文档分享链接**
- **不影响**：飞书 API 调用
- **推荐值**：
  - 中国大陆：`https://my.feishu.cn`
  - 海外版：`https://my.feishu.com`

### FEISHU_DOMAIN（原有）
- **用途**：飞书 API 相关功能
- **保持不变**：不影响现有功能

## 配置示例

在 `.env` 文件中添加：

```bash
# 飞书域名（原有配置，保持不变）
FEISHU_DOMAIN=https://www.feishu.cn

# 飞书文档访问域名（新增配置）
# 中国大陆用户
FEISHU_DOC_DOMAIN=https://my.feishu.cn

# 海外版用户使用：
# FEISHU_DOC_DOMAIN=https://my.feishu.com
```

## 为什么不直接修改 FEISHU_DOMAIN？

因为 `FEISHU_DOMAIN` 可能被其他模块用于 API 调用，直接修改可能会：

1. ❌ 影响 WebSocket 连接
2. ❌ 影响其他 API 调用
3. ❌ 难以排查问题

添加独立的 `FEISHU_DOC_DOMAIN` 配置：

1. ✅ **不影响** API 调用
2. ✅ **不影响** WebSocket 连接
3. ✅ **仅影响**文档链接生成
4. ✅ **职责分离**：配置更清晰

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| [config.py](config.py) | ✅ 添加 `FEISHU_DOC_DOMAIN` 配置项 |
| [doc_utils.py](doc_utils.py) | ✅ 使用 `FEISHU_DOC_DOMAIN` 生成链接 |
| [.env.example](.env.example) | ✅ 添加配置说明和示例 |

## 快速配置

### 1. 编辑 `.env` 文件

```bash
# 添加新配置
FEISHU_DOC_DOMAIN=https://my.feishu.cn
```

### 2. 重启服务

```bash
# 按 Ctrl+C 停止服务
# 重新启动
python main.py
```

### 3. 测试验证

发送视频链接后，查看日志：

```
✅ 文档分享链接生成成功
   使用域名: https://my.feishu.cn
   文档 ID: doxcnXXXXXXXXXXXXXXXXXX
   完整链接: https://my.feishu.cn/docx/doxcnXXXXXXXXXXXXXXXXXX
```

## 预期结果

生成的链接格式：
- ✅ **正确**：`https://my.feishu.cn/docx/doxcnXXXXXXXXXXXXXXXXXX`
- ❌ **错误**：`https://www.feishu.cn/docx/placeholder`

## 常见问题

### Q1: FEISHU_DOC_DOMAIN 和 FEISHU_DOMAIN 有什么区别？

**A:**
- `FEISHU_DOMAIN`：用于 API 调用（WebSocket、消息发送等）
- `FEISHU_DOC_DOMAIN`：仅用于生成用户访问的文档链接

两者职责分离，互不影响。

### Q2: 不配置 FEISHU_DOC_DOMAIN 会怎样？

**A:** 会使用默认值 `https://www.feishu.cn`，但生成的链接可能无法访问。

日志会显示警告：
```
⚠️  使用默认文档域名 https://www.feishu.cn
⚠️  建议在 .env 文件中配置 FEISHU_DOC_DOMAIN
```

### Q3: 我应该使用哪个值？

**A:**
- **中国大陆用户**：`https://my.feishu.cn`
- **海外版用户**：`https://my.feishu.com`

### Q4: 配置错误会导致 API 调用失败吗？

**A:** **不会**。`FEISHU_DOC_DOMAIN` 仅影响文档链接生成，不影响 API 调用。

## 技术细节

### 配置读取（config.py）

```python
# 飞书域名（原有）
FEISHU_DOMAIN = os.getenv("FEISHU_DOMAIN", "https://www.feishu.cn")

# 飞书文档访问域名（新增）
FEISHU_DOC_DOMAIN = os.getenv("FEISHU_DOC_DOMAIN", "https://www.feishu.cn")
```

### 链接生成（doc_utils.py）

```python
def get_document_share_url(document_id: str) -> str:
    # 使用 FEISHU_DOC_DOMAIN（不影响 API）
    domain = config.FEISHU_DOC_DOMAIN.rstrip('/')
    share_url = f"{domain}/docx/{document_id}"
    return share_url
```

## 总结

✅ **新增独立配置**：`FEISHU_DOC_DOMAIN`
✅ **不影响现有功能**：API 调用、WebSocket 连接等
✅ **职责分离**：配置更清晰，易于维护
✅ **向后兼容**：不配置也能运行，但会警告

---

**版本**: 1.0.0
**更新日期**: 2026-03-08
**维护**: bili2txt-agent 项目组
