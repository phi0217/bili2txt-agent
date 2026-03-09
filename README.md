# bili2txt-agent

<div align="center">

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**B站视频转飞书云文档智能机器人**

自动下载、语音识别、AI精转，一键生成结构化文档

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用说明](#-使用说明) • [文档](#-文档)

</div>


## 📖 项目简介

**bili2txt-agent** 是一个基于飞书长连接的智能机器人，通过接收用户发送的B站视频链接，自动完成视频下载、语音识别、AI文本精转，并生成结构化的飞书云文档。

### 核心价值

- 🎯 **零学习成本**：发送视频链接，自动生成文档
- ⚡ **极致性能**：音频下载比视频快300倍
- 🤖 **AI增强**：DeepSeek API智能精转和摘要
- 💾 **智能缓存**：相同视频秒级处理
- 🌐 **多语言支持**：支持中英文双语模式

## ⚡ 性能优势

| 指标 | 传统方案 | bili2txt-agent | 提升 |
|------|---------|----------------|------|
| 音频下载 | 5-10分钟 | 1-2秒 | **300倍** |
| 文件大小 | ~500MB | ~1MB | **99.8%** |
| 总耗时 | 8-17分钟 | 3-7分钟 | **2-5倍** |
| 并发处理 | 串行 | 3线程 | **3倍** |

## ✨ 功能特性

### 📹 视频处理

- ✅ **多种链接格式**
  - 完整链接：`https://www.bilibili.com/video/BV1xx411c7mD`（自动解析）
  - 短链接：`https://b23.tv/abc123`（自动解析）
  - 直接ID：`BV1xx411c7mD` 或 `av123456`

- ✅ **多语言模式** 🌐
  - **中文模式**：`BV1xx411c7mD`（默认）
  - **英文/双语模式**：`BV1xx411c7mD#en` ⭐
    - 在视频ID后添加 `#en` 即可启用
    - 语音识别使用英文模型
    - 生成中英双语对照文档
  - **支持混合文本**：同时处理中英文内容

- ✅ **智能下载策略**
  - 优先使用 yt-dlp 只下载音频（1-2秒）
  - 失败自动回退到 you-get
  - 支持断点续传

- ✅ **视频标题获取**
  - 自动提取视频标题
  - 注入到LLM提示词中，提升理解准确性

### 🎤 语音识别

- ✅ **Whisper Base模型**
  - 平衡速度和精度
  - 支持中英文识别

- ✅ **多语言识别**
  - 中文模式：`BV1xx411c7mD`
  - 英文模式：`BV1xx411c7mD#en` ⭐
  - 自动语言检测（混合文本）

### ✨ AI文本处理

- ✅ **DeepSeek API增强**
  - 原文精转：修正错别字、添加标点、优化表达
  - 关键纪要：提炼核心信息、结构化输出
  - 移除输出限制，充分利用API能力

- ✅ **双语文档生成** 🌐
  - 中文模式：纯中文精转和摘要
  - 英文模式：中英双语对照精转和摘要
  - 每个自然段采用 "中文内容\n\nEnglish Content" 格式

- ✅ **上下文理解**
  - 视频标题注入提示词
  - 更准确的内容理解
  - 更专业的术语处理

### 📄 文档生成

- ✅ **飞书云文档**
  - 自动创建Markdown格式文档
  - 原文精转文档
  - 关键纪要文档
  - 一键生成分享链接

- ✅ **内容结构**
  - 标题层级清晰
  - 支持列表、粗体、斜体
  - 附录保留原始文本

### 💾 缓存系统

- ✅ **智能缓存**
  - 缓存处理结果
  - 支持快速重建文档
  - 按视频ID和语言分别缓存

- ✅ **去重处理**
  - 防止重复下载
  - 并发保护机制
  - 实时处理状态追踪

## 🚀 快速开始

### 1. 系统要求

- Python 3.11+
- FFmpeg
- yt-dlp（推荐）或 you-get（备用）

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/bili2txt-agent.git
cd bili2txt-agent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装 FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
.\install-ffmpeg.ps1
```

验证安装：
```bash
ffmpeg -version
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
```

**必需配置：**

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FEISHU_APP_ID` | 飞书应用ID | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxxxxx` |

**可选配置：**

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FEISHU_DOMAIN` | 飞书API域名 | `https://open.feishu.cn` |
| `FEISHU_DOC_DOMAIN` | 飞书文档域名 | `https://my.feishu.cn` |
| `DEEPSEEK_BASE_URL` | DeepSeek API地址 | `https://api.deepseek.com/v1` |
| `TEMP_DIR` | 临时文件目录 | `./temp` |

### 5. 启动服务

```bash
python main.py
```

看到以下输出表示启动成功：
```
============================================================
Feishu WebSocket Service Starting...
============================================================

App ID: cli_xxxxxxxxx
Temp Dir: ./temp

Using EventDispatcherHandler (Official Recommended)

Important: Please ensure:
  1. Event subscription is configured in Feishu Open Platform
  2. Subscribed to 'im.message.receive_v1' event
  3. Version is created and published
  4. 'Use long connection to receive events' is selected

Initializing WebSocket client...
```

## 🔧 飞书应用配置

### 步骤1：创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 **App ID** 和 **App Secret**

### 步骤2：开启能力

在应用管理页面，开启"机器人"能力

### 步骤3：配置事件订阅

1. 进入"事件与回调"配置
2. 选择 **"使用长连接接收事件"**（不要开启VPN，会造成长连接失败）
3. 订阅 `im.message.receive_v1` 事件
4. 创建并发布版本

### 步骤4：配置权限

授予应用以下权限：

- `im:message`（接收消息、发送消息）
- `im:message:send_as_bot`（以机器人身份发送消息）
- `docx:document`（创建文档）
- `drive:drive`（管理文档）
- `drive:drive:readonly`（读取文件）

### 步骤5：发布并使用

1. 将应用发布到企业或工作台
2. 添加机器人到群组或私聊
3. 发送视频链接开始使用

详细配置请参考 [飞书WebSocket配置](docs/WEBSOCKET_SETUP.md)

## 📖 使用说明

### 快速示例

> 🎯 **最简单的用法**：直接发送B站视频链接
> ```
> https://www.bilibili.com/video/BV1xx411c7mD
> ```

> 🌐 **双语模式用法**：在视频ID后添加 `#en`
> ```
> BV1xx411c7mD#en
> ```
> - 生成中英双语对照文档
> - 适合翻译和学习场景

### 基本使用

发送B站视频链接或ID：

```
https://www.bilibili.com/video/BV1xx411c7mD
```

或：

```
BV1xx411c7mD
```

### 多语言模式 🌐

**中文模式（默认）：**
```
BV1xx411c7mD
# 或
BV1xx411c7mD#zh
```
- ✅ 语音识别使用中文模型
- 📝 生成纯中文的原文精转
- 📋 生成纯中文的关键纪要

**英文/双语模式：**
```
BV1xx411c7mD#en
```
- ✅ 语音识别使用英文模型
- 📝 生成中英双语对照的原文精转
- 📋 生成中英双语的关键纪要

> 💡 **双语模式特点**：
> - 每个自然段采用中英对照格式
> - 关键术语提供中英双语解释
> - 适合学习和翻译场景

### 处理流程

```
接收视频链接
    ↓
检查缓存（秒级命中）
    ↓
下载音频（1-2秒）
    ↓
语音识别（30秒-1分钟）
    ↓
AI精转（2-5分钟）
    ↓
AI纪要（2-5分钟）
    ↓
创建文档（5-10秒）
    ↓
返回两个链接
```

### 输出示例

```
✅ [BV1xx411c7mD/zh] 处理完成！

📹 视频ID：BV1xx411c7mD
🌐 语言模式：中文
📹 视频标题：视频标题
📄 原文长度：12345 字符
📝 精转后长度：11234 字符

🔗 文档链接：原文精转-视频标题
https://my.feishu.cn/docx/xxxxx

🔗 文档链接：关键纪要-视频标题
https://my.feishu.cn/docx/yyyyy
```

## 📁 项目结构

```
bili2txt-agent/
├── main.py                      # 程序入口
│
├── src/                         # 源代码目录
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   ├── utils.py                 # 通用工具
│   │
│   ├── bilibili_downloader.py  # yt-dlp 下载器（推荐）
│   ├── bilibili_utils.py        # you-get 下载器（备用）
│   ├── audio_utils.py           # 音频提取
│   ├── asr_utils.py             # Whisper 语音识别
│   ├── llm_utils.py             # DeepSeek 文本精转
│   ├── doc_utils.py             # 飞书文档创建
│   │
│   ├── feishu_handler.py        # 飞书消息处理
│   ├── feishu_ws_client.py      # 飞书 WebSocket 客户端
│   ├── cache_utils.py           # 缓存管理
│   ├── processing_tracker.py    # 处理状态追踪
│   │
│   └── task.py                  # 完整处理任务流程
│
├── docs/                        # 📚 文档目录
│   ├── README.md                # 文档索引
│   ├── PROJECT_STRUCTURE.md     # 项目结构详细说明
│   ├── CONFIGURATION.md         # 配置指南
│   ├── FAQ.md                   # 常见问题解答
│   ├── VIDEO_DOWNLOAD.md        # 视频下载方案
│   ├── FEISHU_DOCS.md           # 飞书文档创建
│   ├── SHORT_LINK_PARSING.md    # 短链接解析
│   ├── WEBSOCKET_SETUP.md       # WebSocket 配置
│   ├── PROXY_SETUP.md           # 代理设置
│   ├── VIDEO_TITLE_IN_PROMPT.md # 视频标题注入
│   ├── REMOVE_MAX_TOKENS_CONTROL.md # 移除max_tokens限制
│   └── MAX_TOKENS_UNLIMITED.md  # 无上限功能说明
│
├── tests/                       # 🧪 测试目录
│   ├── README.md                # 测试说明
│   ├── test_remove_max_tokens.py        # max_tokens测试
│   ├── test_video_title_simple.py      # 视频标题测试
│   ├── test_unlimited_tokens_simple.py  # 无上限测试
│   ├── test_max_tokens_unlimited.py     # 完整测试
│   ├── test_video_title_prompt.py       # 提示词测试
│   ├── test_integration.py      # 集成测试
│   ├── test_yt_dlp.py           # yt-dlp 测试
│   ├── test_document_api.py     # 文档 API 测试
│   └── test_short_link.py       # 短链接测试
│
├── temp/                        # 临时文件目录
│   ├── cache/                   # 缓存目录
│   └── results/                 # 处理结果缓存
│
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
└── README.md                    # 本文件
```

详细的项目结构说明请查看：[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 📚 文档

### 🚀 快速开始

- [配置指南](docs/CONFIGURATION.md) - 环境变量配置详解
- [项目结构说明](docs/PROJECT_STRUCTURE.md) - 代码组织

### 🔧 核心功能

- [视频下载方案](docs/VIDEO_DOWNLOAD.md) - yt-dlp 音频下载（300倍速度提升）
- [飞书文档创建](docs/FEISHU_DOCS.md) - 文档创建和管理
- [视频标题注入](docs/VIDEO_TITLE_IN_PROMPT.md) - LLM上下文增强

### 🛠️ 技术实现

- [短链接解析](docs/SHORT_LINK_PARSING.md) - B站短链接支持
- [WebSocket 配置](docs/WEBSOCKET_SETUP.md) - 飞书长连接配置
- [代理设置](docs/PROXY_SETUP.md) - 网络代理配置
- [移除max_tokens限制](docs/REMOVE_MAX_TOKENS_CONTROL.md) - 充分利用API能力

### ❓ 帮助

- [常见问题解答](docs/FAQ.md) - 故障排除和常见问题
- [tests/README.md](tests/README.md) - 测试说明

## 🧪 测试

```bash
# 进入测试目录
cd tests

# 运行集成测试（推荐）
python test_integration.py

# 运行功能测试
python test_remove_max_tokens.py      # max_tokens测试
python test_video_title_simple.py     # 视频标题测试
python test_unlimited_tokens_simple.py # 无上限测试

# 运行组件测试
python test_yt_dlp.py          # 测试音频下载
python test_short_link.py      # 测试短链接
python test_document_api.py    # 测试文档API
```

详细测试说明请参考 [tests/README.md](tests/README.md)

## ⚠️ 注意事项

### 使用注意

1. **音频下载优先**：系统自动使用 yt-dlp 只下载音频（1-2秒），失败时回退到 you-get（5-10分钟）
2. **临时文件清理**：程序会自动清理下载的音频文件，处理结果保存到 `./temp/results/` 目录
3. **Whisper模型**：首次运行会自动下载 Whisper base 模型（约 150MB）
4. **DeepSeek API**：请注意 API 调用费用
5. **处理时间**：视频处理可能需要较长时间（主要是语音识别），请耐心等待
6. **长连接稳定性**：WebSocket 客户端会自动重连，无需额外处理

### 性能优化

1. **缓存利用**：相同视频再次处理只需3-5秒（重建文档）
2. **多语言缓存**：同一视频的不同语言版本分别缓存
3. **并发限制**：相同视频同时发送不会重复处理
4. **智能去重**：处理中状态追踪，避免资源浪费

## ❓ 常见问题

### Q: 如何提升下载速度？

**A**: 确保 yt-dlp 已安装（requirements.txt已包含），系统会自动优先使用，下载速度提升300倍。

### Q: 飞书连接失败？

**A**: 检查以下配置：
1. `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
2. 飞书应用是否已启用
3. 是否已订阅 `im.message.receive_v1` 事件
4. 是否已发布版本
5. 是否选择了"使用长连接接收事件"
6. 是否已关闭VPN，在正常的网络环境下

### Q: 文档链接打不开？

**A**: 检查 `FEISHU_DOC_DOMAIN` 配置：
- 国内飞书：`https://my.feishu.cn`
- 海外飞书：`https://docs.larksuite.com`

### Q: 语音识别失败？

**A**: 确保 FFmpeg 已正确安装：
```bash
ffmpeg -version
```

### Q: 如何使用英文模式？

**A**: 在视频ID后添加 `#en` 后缀：
```
BV1xx411c7mD#en
```

### Q: 相同视频再次处理为什么这么快？

**A**: 系统使用了智能缓存，第一次处理后保存结果，再次处理只需3-5秒重建文档。

更多问题请参考 [常见问题解答](docs/FAQ.md)

## 📊 性能对比

### 下载性能

| 方案 | 下载时间 | 文件大小 |
|------|---------|---------|
| you-get（视频） | 5-10分钟 | ~500MB |
| yt-dlp（音频）✨ | 1-2秒 | ~1MB |

### 总体性能

| 指标 | 旧方案 | 新方案 | 提升 |
|------|--------|--------|------|
| 总耗时 | 8-17分钟 | 3-7分钟 | **2-5倍** |
| 网络流量 | ~500MB | ~1MB | **500倍** |
| 磁盘占用 | ~510MB | ~1MB | **500倍** |
| 并发处理 | 不支持 | 3线程 | **3倍** |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发新功能

1. 在 `src/` 对应模块中添加功能
2. 更新 `src/task.py` 中的处理流程
3. 在 `tests/` 中添加测试脚本
4. 在 `docs/` 中更新文档

### 代码规范

- 使用 black 格式化代码
- 遵循 PEP 8 规范
- 添加必要的文档字符串
- 编写单元测试

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件

```
Copyright 2026 bili2txt-agent Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 🔗 相关链接

- [飞书开放平台](https://open.feishu.cn/)
- [DeepSeek 开放平台](https://platform.deepseek.com/)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [Whisper GitHub](https://github.com/openai/whisper)
- [lark-oapi SDK](https://github.com/larksuite/oapi-sdk-python)

## 🌟 致谢

感谢以下开源项目：

- [lark-oapi](https://github.com/larksuite/oapi-sdk-python) - 飞书SDK
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载
- [openai-whisper](https://github.com/openai/whisper) - 语音识别
- [you-get](https://github.com/soimort/you-get) - 备用下载器

---

<div align="center">

**最后更新**: 2026-03-10 | **版本**: 2.0.0

Made with ❤️ by bili2txt-agent team

</div>
