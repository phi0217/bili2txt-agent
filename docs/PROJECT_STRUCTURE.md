# 项目结构说明

## 目录结构

```
bili2txt-agent/
├── .env                          # 环境变量配置文件（不提交到 git）
├── .env.example                  # 环境变量配置示例
├── .gitignore                    # Git 忽略文件配置
├── README.md                     # 项目说明文档
├── requirements.txt              # Python 依赖列表
├── main.py                       # 程序入口（在根目录）
│
├── src/                          # 📦 源代码目录
│   ├── __init__.py               # 包初始化文件
│   ├── config.py                 # 配置管理模块
│   ├── utils.py                  # 通用工具函数
│   │
│   ├── bilibili_utils.py         # B站视频下载（you-get 备用）
│   ├── bilibili_downloader.py    # B站视频下载（yt-dlp，推荐）
│   ├── audio_utils.py            # 音频提取
│   ├── asr_utils.py              # 语音识别 (Whisper)
│   ├── llm_utils.py              # 文本精转 (DeepSeek)
│   ├── doc_utils.py              # 飞书文档创建
│   │
│   ├── feishu_handler.py         # 飞书消息处理
│   ├── feishu_ws_client.py       # 飞书 WebSocket 客户端
│   │
│   └── task.py                   # 视频处理任务流程
│
├── install-ffmpeg.ps1            # FFmpeg 安装脚本（Windows）
│
├── docs/                         # 📚 文档目录
│   ├── README.md                 # 文档索引
│   ├── PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
│   ├── CONFIGURATION.md          # 配置指南
│   ├── VIDEO_DOWNLOAD.md         # 视频下载方案
│   ├── FEISHU_DOCS.md            # 飞书文档创建
│   ├── SHORT_LINK_PARSING.md     # 短链接解析
│   ├── WEBSOCKET_SETUP.md        # WebSocket 配置
│   └── PROXY_SETUP.md            # 代理设置
│
├── tests/                        # 🧪 测试目录
│   ├── README.md                 # 测试说明
│   ├── test_yt_dlp.py            # yt-dlp 功能测试
│   ├── test_integration.py       # 集成测试
│   ├── test_document_api.py      # 飞书文档 API 测试
│   ├── test_simple_write.py      # 简单写入测试
│   └── test_short_link.py        # 短链接测试
│
├── temp/                         # ⏱️ 临时文件目录
│   └── results/                  # 处理结果缓存
│
└── .venv/                        # 虚拟环境（不提交到 git）
```

## 核心模块说明

### 1. 入口和配置

| 文件 | 说明 |
|------|------|
| [main.py](../main.py) | 程序入口，初始化飞书客户端和事件处理器 |
| [src/config.py](../src/config.py) | 配置管理，从环境变量读取配置 |
| [src/utils.py](../src/utils.py) | 通用工具函数（文件清理等） |

### 2. 视频处理流程

| 文件 | 说明 |
|------|------|
| [src/bilibili_downloader.py](../src/bilibili_downloader.py) | yt-dlp 下载器（推荐），支持音频和视频下载 |
| [src/bilibili_utils.py](../src/bilibili_utils.py) | you-get 下载器（备用），支持阶梯式清晰度策略 |
| [src/audio_utils.py](../src/audio_utils.py) | 从视频中提取音频（MP3） |
| [src/asr_utils.py](../src/asr_utils.py) | 使用 Whisper 进行语音识别 |
| [src/llm_utils.py](../src/llm_utils.py) | 使用 DeepSeek API 进行文本精转 |
| [src/task.py](../src/task.py) | 完整的视频处理任务流程（智能回退机制） |

### 3. 飞书集成

| 文件 | 说明 |
|------|------|
| [src/feishu_handler.py](../src/feishu_handler.py) | 飞书消息发送，客户端管理 |
| [src/feishu_ws_client.py](../src/feishu_ws_client.py) | 飞书 WebSocket 长连接客户端 |
| [src/doc_utils.py](../src/doc_utils.py) | 飞书文档创建和内容写入 |

### 4. 工具和测试

| 文件 | 说明 |
|------|------|
| [install-ffmpeg.ps1](../install-ffmpeg.ps1) | Windows 下自动安装 FFmpeg |
| [tests/](../tests/) | 测试脚本和测试日志 |

## 数据流

```
用户发送 B站视频链接
    ↓
飞书 WebSocket 接收消息
    ↓
提取视频 ID（支持短链接）
    ↓
下载音频（1-2秒）✨
  ├─ 优先: yt-dlp (1-2秒, 1MB)
  └─ 回退: you-get (5-10分钟, 500MB)
    ↓
语音识别（Whisper）
    ↓
文本精转（DeepSeek）
    ↓
创建飞书文档
    ↓
返回文档链接给用户
```

## 配置说明

### 必需的环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | `cli_xxxxxxxxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxxxxxxxxxxxxxx` |

### 可选的环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FEISHU_DOMAIN` | 飞书 API 域名 | `https://open.feishu.cn` |
| `FEISHU_DOC_DOMAIN` | 飞书文档域名 | `https://my.feishu.cn` |
| `TEMP_DIR` | 临时文件目录 | `./temp` |

详细配置说明请参考 [配置指南](CONFIGURATION.md)

## 依赖说明

### 核心依赖

| 包 | 版本 | 用途 |
|---|------|------|
| lark-oapi | ^1.2.20 | 飞书开放平台 SDK |
| openai | ^1.55.0 | OpenAI API（用于 Whisper） |
| requests | ^2.32.0 | HTTP 请求 |
| python-dotenv | ^1.0.0 | 环境变量管理 |

### 推荐依赖

| 包 | 用途 |
|---|------|
| yt-dlp | 视频下载（推荐，300倍速度提升） |
| ffmpeg-python | 音频处理 |
| whisper | 语音识别 |

### 可选依赖

| 包 | 用途 |
|---|------|
| you-get | 视频下载（备用） |

### 系统依赖

| 软件 | 用途 |
|------|------|
| Python 3.11+ | 运行环境 |
| FFmpeg | 音视频处理 |

## 开发说明

### 运行项目

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必需的配置

# 启动服务
python main.py
```

### 测试

```bash
# 进入 tests 目录
cd tests

# 运行测试脚本
python test_yt_dlp.py              # 测试 yt-dlp 下载
python test_integration.py         # 测试完整集成
python test_short_link.py          # 测试短链接解析
python test_simple_write.py        # 测试文档写入
python test_document_api.py        # 测试文档 API
```

### 添加新功能

1. 在 `src/` 对应模块中添加功能
2. 更新 [src/task.py](../src/task.py) 中的处理流程
3. 在 [tests/](../tests/) 中添加测试脚本
4. 在 [docs/](./) 中添加文档

## 文档说明

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 文档索引 |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | 项目结构说明（本文件） |
| [CONFIGURATION.md](./CONFIGURATION.md) | 配置指南 |
| [VIDEO_DOWNLOAD.md](./VIDEO_DOWNLOAD.md) | 视频下载方案 |
| [FEISHU_DOCS.md](./FEISHU_DOCS.md) | 飞书文档创建 |

## 常见问题

### Q: 临时文件存储在哪里？

A: 临时文件默认存储在 `./temp` 目录，处理完成后会自动清理。处理结果会保存在 `./temp/results/` 目录。

### Q: 如何切换下载方式？

A: 系统会自动选择最优下载方式：
- 优先使用 yt-dlp（1-2秒，1MB）
- 失败时自动回退到 you-get（5-10分钟，500MB）

详情请参考 [视频下载方案](VIDEO_DOWNLOAD.md)

### Q: 如何配置代理？

A: 参阅 [代理设置](PROXY_SETUP.md)

### Q: WebSocket 连接失败怎么办？

A: 参阅 [WebSocket 配置](WEBSOCKET_SETUP.md)

## 维护说明

### 清理临时文件

```bash
# 清理所有临时文件
rm -rf ./temp/*

# 仅清理视频和音频文件（保留结果）
rm -f ./temp/*.mp4 ./temp/*.mp3
```

### 更新依赖

```bash
# 更新 requirements.txt
pip freeze > requirements.txt

# 更新特定包
pip install -U lark-oapi
```

### 查看日志

程序运行时会在控制台输出详细日志，包括：
- 下载进度
- 处理状态
- 错误信息

测试日志保存在 `tests/` 目录

---

**最后更新**: 2026-03-09
**版本**: 2.0.0
