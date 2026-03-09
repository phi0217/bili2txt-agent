# bili2txt-agent

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> B站视频转飞书云文档智能机器人 - 自动下载、语音识别、AI精转，一键生成文档

**bili2txt-agent** 是一个基于飞书长连接的智能机器人，通过接收用户发送的B站视频链接，自动完成视频下载、语音识别、AI文本精转，并生成结构化的飞书云文档。

## ⚡ 性能优势

- **300倍速度提升**：使用 yt-dlp 只下载音频（1-2秒 vs 5-10分钟）
- **99.8% 空间节省**：仅下载 1MB 音频而非 500MB 视频
- **2-5倍总提速**：完整流程从 8-17 分钟缩短到 3-7 分钟

## ✨ 功能特点

### 支持的链接格式

- 🔗 **完整视频链接**：`https://www.bilibili.com/video/BV1xx411c7mD`
- 🔗 **B站短链接**：`https://b23.tv/abc123`（自动解析）
- 🔖 **BV号**：`BV1xx411c7mD`
- 🔖 **AV号**：`av123456`（不区分大小写）

### 核心功能

- 🤖 **飞书长连接模式**：无需公网IP，适合本地部署
- 🎵 **音频下载优先**：使用 yt-dlp 只下载音频，超快速
- 🎤 **Whisper语音识别**：使用base模型，平衡速度和精度
- ✨ **DeepSeek API精转**：自动生成摘要和整理全文
- 📄 **Markdown格式文档**：支持标题、列表、粗体、斜体等格式
- 💾 **本地缓存**：完整内容保存到本地 Markdown 文件
- 🚀 **智能缓存**：缓存文本内容，再次处理时重新创建文档（<5秒）
- 🔄 **智能回退**：yt-dlp 失败时自动使用 you-get

## 📋 系统要求

- Python 3.11+
- FFmpeg
- yt-dlp（推荐）或 you-get（备用）

## 🚀 快速开始

### 1. 安装系统依赖

**安装 FFmpeg：**

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
# 运行项目提供的脚本
.\install-ffmpeg.ps1
```

**验证 FFmpeg 安装：**
```bash
ffmpeg -version
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装所有依赖（包括 yt-dlp 和 you-get）
pip install -r requirements.txt
```

**说明**：
- requirements.txt 已包含 yt-dlp（主下载器）和 you-get（备用下载器）
- 系统会自动优先使用 yt-dlp，失败时自动回退到 you-get
- 无需单独安装

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，至少填入以下配置：
# - FEISHU_APP_ID（飞书应用ID）
# - FEISHU_APP_SECRET（飞书应用密钥）
# - DEEPSEEK_API_KEY（DeepSeek API密钥）
```

详细配置说明请参考 [配置指南](docs/CONFIGURATION.md)

### 4. 启动项目

```bash
python main.py
```

### 5. 验证安装

```bash
# 运行集成测试
cd tests
python test_integration.py

# 如果看到 "🎉 所有测试通过！" 说明安装成功
```

## 🔧 飞书应用配置

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 **App ID** 和 **App Secret**，填入 `.env` 文件

### 2. 开启机器人能力

在应用管理页面，开启"机器人"能力

### 3. 配置长连接接收事件

1. 进入"事件与回调"配置
2. 选择 **"使用长连接接收事件"**
3. 订阅 `im.message.receive_v1` 事件

### 4. 配置权限

授予应用以下权限：

- `im:message`（接收消息、发送消息）
- `docx:document`（创建文档）
- `drive:drive`（管理文档）

### 5. 发布应用

将应用发布到企业或工作台，添加机器人到群组或私聊

详细配置请参考 [WebSocket 配置](docs/WEBSOCKET_SETUP.md)

## 📖 使用方法

### 发送视频链接

**支持完整链接和短链接：**

```
https://www.bilibili.com/video/BV1xx411c7mD
https://b23.tv/abc123
```

**或直接发送BV号/AV号：**

```
BV1xx411c7mD
av123456
```

### 处理流程

```
接收视频链接
    ↓
下载音频（1-2秒）✨ yt-dlp
    ↓
语音识别（2-5分钟）
    ↓
文本精转（30秒-1分钟）
    ↓
创建文档（10-30秒）
    ↓
返回链接
```

### 处理时间

- **总耗时**：3-7 分钟（10分钟视频）
- **瓶颈**：语音识别（主要耗时）

## 📁 项目结构

```
bili2txt-agent/
├── main.py                 # 程序入口
│
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── utils.py            # 通用工具
│   │
│   ├── bilibili_downloader.py  # yt-dlp 下载器（推荐）
│   ├── bilibili_utils.py   # you-get 下载器（备用）
│   ├── audio_utils.py      # 音频提取
│   ├── asr_utils.py        # Whisper 语音识别
│   ├── llm_utils.py        # DeepSeek 文本精转
│   ├── doc_utils.py        # 飞书文档创建
│   │
│   ├── feishu_handler.py   # 飞书消息处理
│   ├── feishu_ws_client.py # 飞书 WebSocket 客户端
│   │
│   └── task.py             # 完整处理任务流程
│
├── docs/                   # 📚 文档目录
│   ├── README.md           # 文档索引
│   ├── PROJECT_STRUCTURE.md  # 项目结构详细说明
│   ├── CONFIGURATION.md    # 配置指南
│   ├── FAQ.md              # 常见问题解答
│   ├── VIDEO_DOWNLOAD.md   # 视频下载方案
│   ├── FEISHU_DOCS.md      # 飞书文档创建
│   ├── SHORT_LINK_PARSING.md  # 短链接解析
│   ├── WEBSOCKET_SETUP.md  # WebSocket 配置
│   └── PROXY_SETUP.md      # 代理设置
│
├── tests/                  # 🧪 测试目录
│   ├── README.md           # 测试说明
│   ├── test_integration.py # 集成测试
│   ├── test_yt_dlp.py      # yt-dlp 测试
│   ├── test_document_api.py # 文档 API 测试
│   └── test_short_link.py  # 短链接测试
│
├── temp/                   # 临时文件目录
│   └── results/            # 处理结果缓存
│
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

详细的项目结构说明请查看：[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 📚 文档

### 快速开始

- [配置指南](docs/CONFIGURATION.md) - 环境变量配置详解
- [项目结构说明](docs/PROJECT_STRUCTURE.md) - 代码组织

### 核心功能

- [视频下载方案](docs/VIDEO_DOWNLOAD.md) - yt-dlp 音频下载（300倍速度提升）
- [飞书文档创建](docs/FEISHU_DOCS.md) - 文档创建和管理

### 技术实现

- [短链接解析](docs/SHORT_LINK_PARSING.md) - B站短链接支持
- [WebSocket 配置](docs/WEBSOCKET_SETUP.md) - 飞书长连接配置
- [代理设置](docs/PROXY_SETUP.md) - 网络代理配置

### 帮助

- [常见问题解答](docs/FAQ.md) - 故障排除和常见问题

## 🔍 环境变量说明

### 必需配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FEISHU_APP_ID` | 飞书应用ID | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxxxxx` |

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FEISHU_DOMAIN` | 飞书 API 域名 | `https://open.feishu.cn` |
| `FEISHU_DOC_DOMAIN` | 飞书文档域名 | `https://my.feishu.cn` |
| `DEEPSEEK_BASE_URL` | DeepSeek API地址 | `https://api.deepseek.com/v1` |
| `TEMP_DIR` | 临时文件目录 | `./temp` |

详细配置说明请参考 [配置指南](docs/CONFIGURATION.md)

## ⚠️ 注意事项

1. **音频下载优先**：系统会自动使用 yt-dlp 只下载音频（1-2秒，1MB），失败时回退到 you-get（5-10分钟，500MB）
2. **临时文件清理**：程序会自动清理下载的音频文件，处理结果会保存到 `./temp/results/` 目录
3. **Whisper模型**：首次运行会自动下载 Whisper base 模型（约 150MB）
4. **DeepSeek API**：请注意 API 调用费用和 token 限制（3000 tokens）
5. **长时间运行**：视频处理可能需要较长时间（主要是语音识别），请耐心等待
6. **飞书长连接**：客户端会自动重连，无需额外处理

## 🧪 测试

```bash
# 进入测试目录
cd tests

# 运行集成测试（推荐）
python test_integration.py

# 运行单独测试
python test_yt_dlp.py          # 测试音频下载
python test_short_link.py      # 测试短链接
python test_simple_write.py    # 测试文档创建
```

详细测试说明请参考 [tests/README.md](tests/README.md)

## ❓ 常见问题

### Q: 下载速度很慢怎么办？

**A**: 安装 yt-dlp，下载速度提升 300 倍：

```bash
pip install yt-dlp
```

系统会自动优先使用 yt-dlp，无需修改配置。

### Q: 飞书连接失败？

**A**: 检查以下配置：
1. `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
2. 飞书应用是否已启用
3. 是否已订阅 `im.message.receive_v1` 事件
4. 是否已授予必需权限

### Q: 文档链接打不开？

**A**: 检查 `FEISHU_DOC_DOMAIN` 配置：
- 国内飞书：`https://my.feishu.cn`
- 海外飞书：`https://docs.larksuite.com`

### Q: 语音识别失败？

**A**: 确保 FFmpeg 已正确安装：

```bash
ffmpeg -version
```

更多问题请参考 [常见问题解答](docs/FAQ.md)

## 📊 性能对比

### 下载速度

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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发新功能

1. 在 `src/` 对应模块中添加功能
2. 更新 [src/task.py](src/task.py) 中的处理流程
3. 在 [tests/](tests/) 中添加测试脚本
4. 在 [docs/](docs/) 中更新文档

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件

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

## 🔗 相关链接

- [飞书开放平台](https://open.feishu.cn/)
- [DeepSeek 开放平台](https://platform.deepseek.com/)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [Whisper GitHub](https://github.com/openai/whisper)

---

**最后更新**: 2026-03-09
**版本**: 2.0.0
