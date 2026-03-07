# bili2txt-agent

B站视频转飞书云文档机器人，通过飞书长连接接收用户发送的B站视频链接，自动完成视频下载、音频提取、语音识别、文本精转，并上传至飞书云文档。

## 功能特点

- 🤖 **飞书长连接模式**：无需公网IP，适合本地部署
- 🎥 **B站视频下载**：支持BV号和AV号识别
- 🎤 **Whisper语音识别**：使用base模型，平衡速度和精度
- ✨ **DeepSeek API精转**：自动生成摘要和整理全文
- 📄 **飞书云文档**：自动创建并分享文档
- 🐳 **Docker支持**：一键容器化部署

## 系统要求

- Python 3.11+
- FFmpeg
- you-get

## 快速开始

### 方式一：Docker 部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd bili2txt-agent
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **查看日志**
```bash
docker-compose logs -f
```

### 方式二：本地部署

1. **安装系统依赖**

```bash
# 安装 FFmpeg
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载 FFmpeg 并添加到 PATH
```

2. **安装 Python 依赖**

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 you-get
pip install you-get
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

4. **启动服务**

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

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FEISHU_APP_ID` | 飞书应用ID | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_BASE_URL` | DeepSeek API地址 | `https://api.deepseek.com/v1` |
| `TEMP_DIR` | 临时文件目录 | `./temp` |
| `FEISHU_DOMAIN` | 飞书域名 | `https://www.feishu.cn` |

## 使用方法

1. **向机器人发送B站视频链接**

```
https://www.bilibili.com/video/BV1xx411c7mD
```

2. **或发送BV号/AV号**

```
BV1xx411c7mD
av123456
```

3. **等待处理完成**，机器人会返回飞书云文档链接

## 项目结构

```
bili2txt-agent/
├── main.py                 # 程序入口
├── config.py               # 配置加载
├── feishu_handler.py       # 飞书消息处理
├── bilibili_utils.py       # B站视频处理
├── audio_utils.py          # 音频提取
├── asr_utils.py            # 语音识别
├── llm_utils.py            # LLM精转
├── doc_utils.py            # 飞书文档操作
├── task.py                 # 后台任务处理
├── utils.py                # 通用工具
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量模板
├── Dockerfile              # Docker镜像
├── docker-compose.yml      # Docker Compose
└── README.md               # 部署说明
```

## 注意事项

1. **临时文件清理**：程序会自动清理下载的视频和音频文件，无需手动清理
2. **Whisper模型**：首次运行会自动下载Whisper base模型（约150MB）
3. **DeepSeek API**：请注意API调用费用和token限制
4. **长时间运行**：视频处理可能需要较长时间，请耐心等待
5. **飞书长连接**：客户端会自动重连，无需额外处理

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
