# bili2txt-agent

B站视频转飞书云文档机器人，通过飞书长连接接收用户发送的B站视频链接，自动完成视频下载、音频提取、语音识别、文本精转，并上传至飞书云文档。

## 功能特点

- 🤖 **飞书长连接模式**：无需公网IP，适合本地部署
- 🔗 **短链接支持**：自动解析 B站短链接（b23.tv）
- 🎥 **阶梯式下载**：智能选择最低可用清晰度（360p → 480p → 默认），无需登录
- 🎤 **Whisper语音识别**：使用base模型，平衡速度和精度
- ✨ **DeepSeek API精转**：自动生成摘要和整理全文
- 📄 **飞书云文档**：自动创建并分享文档
- 💾 **本地缓存**：完整内容保存到本地 Markdown 文件

## 系统要求

- Python 3.11+
- FFmpeg
- you-get

## 快速开始

### 1. 安装系统依赖

**安装 FFmpeg：**

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载 FFmpeg 并添加到 PATH：https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
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

# 安装项目依赖
pip install -r requirements.txt
pip install you-get
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入以下配置：
# - FEISHU_APP_ID（飞书应用ID）
# - FEISHU_APP_SECRET（飞书应用密钥）
# - DEEPSEEK_API_KEY（DeepSeek API密钥）
```

### 4. 启动项目

```bash
python main.py
```

## 飞书应用配置

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

## 环境变量说明

### 必需配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FEISHU_APP_ID` | 飞书应用ID | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxxxxx` |

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_BASE_URL` | DeepSeek API地址 | `https://api.deepseek.com/v1` |
| `TEMP_DIR` | 临时文件目录 | `./temp` |
| `FEISHU_DOMAIN` | 飞书 API 域名 | `https://open.feishu.cn` |
| `FEISHU_DOC_DOMAIN` | 飞书文档域名 | `https://my.feishu.cn` |

**注意**：`FEISHU_DOC_DOMAIN` 用于生成用户访问的文档链接，可以根据部署区域调整（如 `https://feishu.cn` 或 `https://my.feishu.cn`）

## 使用方法

1. **向机器人发送B站视频链接**

支持完整链接和短链接：

```
https://www.bilibili.com/video/BV1xx411c7mD
https://b23.tv/abc123
```

2. **或直接发送BV号/AV号**

```
BV1xx411c7mD
av123456
```

3. **等待处理完成**，机器人会返回飞书云文档链接和本地缓存路径

**处理流程**：

```
接收视频链接 → 下载视频（360p优先） → 提取音频 → 语音识别 → 文本精转 → 创建文档 → 返回链接
```

**处理时间**：根据视频长度，通常需要 2-10 分钟

## 项目结构

```
bili2txt-agent/
├── main.py                 # 程序入口
│
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── utils.py            # 通用工具
│   │
│   ├── bilibili_utils.py   # B站视频下载（支持短链接、阶梯清晰度）
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
│   ├── PROJECT_STRUCTURE.md           # 项目结构详细说明
│   ├── VIDEO_QUALITY_CONTROL.md       # 视频清晰度策略
│   ├── DOC_CONTENT_WRITE_FIX.md       # 文档写入修复
│   ├── FEISHU_DOC_WRITE_API_SOLUTION.md  # API 解决方案
│   ├── SHORT_LINK_PARSING.md          # 短链接解析
│   ├── WEBSOCKET_SETUP.md             # WebSocket 配置
│   └── ...
│
├── tests/                  # 🧪 测试目录
│   ├── test_document_api.py           # 文档 API 测试
│   ├── test_simple_write.py           # 写入测试
│   └── test_short_link.py             # 短链接测试
│
├── temp/                   # 临时文件目录
│   └── results/            # 处理结果缓存
│
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

详细的项目结构说明请查看：[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 注意事项

1. **视频下载策略**：默认使用阶梯式清晰度（360p → 480p → 默认），优先选择最低可用清晰度以避免登录要求并加快下载速度
2. **临时文件清理**：程序会自动清理下载的视频和音频文件，处理结果会保存到 `./temp/results/` 目录
3. **Whisper模型**：首次运行会自动下载 Whisper base 模型（约 150MB）
4. **DeepSeek API**：请注意 API 调用费用和 token 限制
5. **长时间运行**：视频处理可能需要较长时间，请耐心等待
6. **飞书长连接**：客户端会自动重连，无需额外处理

## 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md) - 详细的目录结构和模块说明
- [视频清晰度控制](docs/VIDEO_QUALITY_CONTROL.md) - 阶梯式下载策略详解
- [短链接解析](docs/SHORT_LINK_PARSING.md) - B站短链接支持
- [飞书文档 API](docs/FEISHU_DOC_WRITE_API_SOLUTION.md) - 文档创建技术细节
- [WebSocket 配置](docs/WEBSOCKET_SETUP.md) - 飞书长连接配置指南

## 故障排除

### 1. 无法识别视频ID

确保发送的是有效的B站视频链接或BV/AV号

### 2. 视频下载失败

检查网络连接，确保可以访问B站

### 3. 语音识别失败

检查FFmpeg是否正确安装，运行 `ffmpeg -version` 验证

### 4. LLM精转失败

检查DeepSeek API密钥是否正确，确保账户有足够余额

### 5. 飞书连接失败

检查飞书应用配置，确保已正确配置长连接和事件订阅

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
