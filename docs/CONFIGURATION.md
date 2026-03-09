# 配置指南

## 概述

bili2txt-agent 通过环境变量进行配置。本文档详细说明所有配置选项及其用途。

## 快速开始

### 1. 创建配置文件

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
# Windows: notepad .env
# Linux/Mac: vim .env
```

### 2. 必需配置

在 `.env` 文件中至少配置以下变量：

```bash
FEISHU_APP_ID=cli_xxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3. 启动服务

```bash
python main.py
```

## 环境变量说明

### 必需配置

| 变量名 | 说明 | 获取方式 | 示例值 |
|--------|------|---------|--------|
| `FEISHU_APP_ID` | 飞书应用 ID | [飞书开放平台](https://open.feishu.cn/) | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | [飞书开放平台](https://open.feishu.cn/) | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | [DeepSeek 平台](https://platform.deepseek.com/) | `sk-xxxxxxxxxxxxxxxx` |

### 可选配置

| 变量名 | 说明 | 默认值 | 推荐值 |
|--------|------|--------|--------|
| `FEISHU_DOMAIN` | 飞书 API 域名 | `https://open.feishu.cn` | 默认即可 |
| `FEISHU_DOC_DOMAIN` | 飞书文档域名 | `https://my.feishu.cn` | 根据实际情况调整 |
| `TEMP_DIR` | 临时文件目录 | `./temp` | 默认即可 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com/v1` | 默认即可 |

## 配置详解

### 飞书应用配置

#### FEISHU_APP_ID

飞书应用的唯一标识符。

**如何获取**：
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建应用或选择已有应用
3. 在"凭证与基础信息"页面找到"App ID"

**示例**：
```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
```

#### FEISHU_APP_SECRET

飞书应用的密钥。

**如何获取**：
1. 在飞书开放平台的"凭证与基础信息"页面
2. 找到"App Secret"
3. 点击"查看"或"生成"

**示例**：
```bash
FEISHU_APP_SECRET=xxxxxxxxxxxxx
```

#### FEISHU_DOMAIN

飞书 API 的域名地址。

**说明**：
- 默认值适用于国内飞书
- 如果使用海外版飞书（Lark），需要修改为 `https://open.larksuite.com`

**示例**：
```bash
# 国内飞书（默认）
FEISHU_DOMAIN=https://open.feishu.cn

# 海外飞书
FEISHU_DOMAIN=https://open.larksuite.com
```

#### FEISHU_DOC_DOMAIN

飞书文档的访问域名。

**说明**：
- 影响生成的文档链接域名
- 默认值适用于国内飞书
- 如果使用海外版飞书（Lark），需要修改为 `https://docs.larksuite.com`

**示例**：
```bash
# 国内飞书（默认）
FEISHU_DOC_DOMAIN=https://my.feishu.cn

# 海外飞书
FEISHU_DOC_DOMAIN=https://docs.larksuite.com

# 自定义域名（如有）
FEISHU_DOC_DOMAIN=https://feishu.your-company.com
```

**生成的文档链接示例**：
```
https://my.feishu.cn/docx/doxcnAbCdEfGhIjKlMnOpQrStUvW
```

### DeepSeek 配置

#### DEEPSEEK_API_KEY

DeepSeek API 的访问密钥。

**如何获取**：
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 在"API Keys"页面创建新密钥

**示例**：
```bash
DEEPSEEK_API_KEY=sk-xxxx
```

#### DEEPSEEK_BASE_URL

DeepSeek API 的基础 URL。

**说明**：
- 通常使用默认值即可
- 如果有代理或特殊需求，可以修改

**示例**：
```bash
# 默认值
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 使用代理
DEEPSEEK_BASE_URL=https://your-proxy.com/v1
```

### 本地配置

#### TEMP_DIR

临时文件存储目录。

**说明**：
- 存放下载的视频、音频文件
- 处理完成后自动清理
- 确保有足够的磁盘空间

**示例**：
```bash
# 默认值
TEMP_DIR=./temp

# 自定义路径
TEMP_DIR=/var/tmp/bili2txt
TEMP_DIR=D:\temp\bili2txt
```

## 完整配置示例

### 基础配置（.env）

```bash
# 飞书应用配置（必需）
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxx

# DeepSeek 配置（必需）
DEEPSEEK_API_KEY=sk-xxxx

# 飞书域名配置（可选，使用默认值即可）
FEISHU_DOMAIN=https://open.feishu.cn
FEISHU_DOC_DOMAIN=https://my.feishu.cn

# DeepSeek API 配置（可选，使用默认值即可）
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 本地配置（可选，使用默认值即可）
TEMP_DIR=./temp
```

### 高级配置

```bash
# 飞书应用配置（必需）
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxx

# DeepSeek 配置（必需）
DEEPSEEK_API_KEY=sk-xxxx

# 海外飞书配置
FEISHU_DOMAIN=https://open.larksuite.com
FEISHU_DOC_DOMAIN=https://docs.larksuite.com

# 使用代理
DEEPSEEK_BASE_URL=https://your-proxy.com/deepseek/v1

# 自定义临时目录
TEMP_DIR=D:\bili2txt-temp
```

## 配置验证

### 验证脚本

创建 `verify_config.py` 验证配置是否正确：

```python
import os
from dotenv import load_dotenv

def verify_config():
    load_dotenv()

    required_vars = [
        'FEISHU_APP_ID',
        'FEISHU_APP_SECRET',
        'DEEPSEEK_API_KEY'
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ 缺少以下配置：")
        for var in missing:
            print(f"  - {var}")
        return False

    print("✅ 所有必需配置已设置")

    # 显示配置信息
    print("\n当前配置：")
    print(f"  FEISHU_APP_ID: {os.getenv('FEISHU_APP_ID')}")
    print(f"  FEISHU_DOMAIN: {os.getenv('FEISHU_DOMAIN', 'https://open.feishu.cn')}")
    print(f"  FEISHU_DOC_DOMAIN: {os.getenv('FEISHU_DOC_DOMAIN', 'https://my.feishu.cn')}")
    print(f"  TEMP_DIR: {os.getenv('TEMP_DIR', './temp')}")

    return True

if __name__ == "__main__":
    verify_config()
```

运行验证：
```bash
python verify_config.py
```

## 故障排除

### Q1: 启动时提示缺少配置

**错误信息**：
```
KeyError: 'FEISHU_APP_ID'
```

**解决方案**：
1. 确认已创建 `.env` 文件
2. 检查必需的配置项是否已填写
3. 重启程序

### Q2: 飞书连接失败

**错误信息**：
```
Error connecting to Feishu: Invalid app credentials
```

**解决方案**：
1. 确认 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 正确
2. 检查飞书应用是否已启用
3. 确认飞书应用权限配置正确

### Q3: DeepSeek API 调用失败

**错误信息**：
```
Error calling DeepSeek API: Invalid API key
```

**解决方案**：
1. 确认 `DEEPSEEK_API_KEY` 正确
2. 检查 API 密钥是否已过期
3. 确认账户有足够的额度

### Q4: 文档链接打不开

**错误信息**：
```
文档链接无法访问
```

**解决方案**：
1. 检查 `FEISHU_DOC_DOMAIN` 配置
2. 确认域名格式正确（包含 `https://`）
3. 手动在浏览器中测试链接

### Q5: 临时文件目录权限问题

**错误信息**：
```
PermissionError: [Errno 13] Permission denied: './temp'
```

**解决方案**：
1. 检查 `TEMP_DIR` 目录是否存在
2. 确认程序有读写权限
3. 尝试修改为其他目录：
   ```bash
   TEMP_DIR=/tmp/bili2txt
   ```

## 安全建议

### 1. 保护敏感信息

```bash
# 不要将 .env 文件提交到 Git
echo ".env" >> .gitignore

# 检查 .gitignore 是否生效
git status
```

### 2. 使用环境变量（生产环境）

```bash
# Linux/Mac
export FEISHU_APP_ID="cli_xxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxx"

# Windows (PowerShell)
$env:FEISHU_APP_ID="cli_xxxxxxxxx"
$env:FEISHU_APP_SECRET="xxxxxxxxxxxxxxxx"
```

### 3. 定期更新密钥

- 定期更换 API 密钥
- 使用最小权限原则
- 监控 API 使用情况

## 配置模板

### .env.example

```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx

# DeepSeek 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# 飞书域名配置（可选）
FEISHU_DOMAIN=https://open.feishu.cn
FEISHU_DOC_DOMAIN=https://my.feishu.cn

# DeepSeek API 配置（可选）
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 本地配置（可选）
TEMP_DIR=./temp
```

## 参考文档

- [项目结构说明](PROJECT_STRUCTURE.md) - 代码组织
- [视频下载方案](VIDEO_DOWNLOAD.md) - 下载配置
- [飞书文档创建](FEISHU_DOCS.md) - 文档 API 配置

---

**最后更新**: 2026-03-09
**版本**: 1.0.0
