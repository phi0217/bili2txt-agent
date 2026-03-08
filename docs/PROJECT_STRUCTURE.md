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
│   ├── bilibili_utils.py         # B站视频下载和处理
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
├── docs/                         # 文档目录
│   ├── PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
│   ├── VIDEO_QUALITY_CONTROL.md  # 视频清晰度控制说明
│   ├── DOC_CONTENT_WRITE_FIX.md  # 文档内容写入修复
│   ├── FEISHU_DOC_DOMAIN_CONFIG.md  # 飞书文档域名配置
│   ├── FEISHU_DOC_WRITE_API_SOLUTION.md  # 飞书文档 API 解决方案
│   ├── FIX_SUMMARY.md            # 修复总结
│   ├── PLACEHOLDER_FIX.md        # 占位符修复
│   ├── PROXY_SETUP.md            # 代理设置
│   ├── SHORT_LINK_PARSING.md     # 短链接解析
│   └── WEBSOCKET_SETUP.md        # WebSocket 设置
│
├── tests/                        # 测试目录
│   ├── test_document_api.py      # 飞书文档 API 测试
│   ├── test_simple_write.py      # 简单写入测试
│   ├── test_short_link.py        # 短链接测试
│   └── test_write.log            # 测试日志
│
├── temp/                         # 临时文件目录
│   └── results/                  # 处理结果缓存
│
└── .venv/                        # 虚拟环境（不提交到 git）
```

## 核心模块说明

### 1. 入口和配置

| 文件 | 说明 |
|------|------|
| [main.py](../main.py) | 程序入口，初始化飞书客户端和事件处理器 |
| [config.py](../config.py) | 配置管理，从环境变量读取配置 |
| [utils.py](../utils.py) | 通用工具函数（文件清理等） |

### 2. 视频处理流程

| 文件 | 说明 |
|------|------|
| [bilibili_utils.py](../bilibili_utils.py) | B站视频下载，支持短链接解析、阶梯式清晰度策略 |
| [audio_utils.py](../audio_utils.py) | 从视频中提取音频（MP3） |
| [asr_utils.py](../asr_utils.py) | 使用 Whisper 进行语音识别 |
| [llm_utils.py](../llm_utils.py) | 使用 DeepSeek API 进行文本精转 |
| [task.py](../task.py) | 完整的视频处理任务流程（同步和异步版本） |

### 3. 飞书集成

| 文件 | 说明 |
|------|------|
| [feishu_handler.py](../feishu_handler.py) | 飞书消息发送，客户端管理 |
| [feishu_ws_client.py](../feishu_ws_client.py) | 飞书 WebSocket 长连接客户端 |
| [doc_utils.py](../doc_utils.py) | 飞书文档创建和内容写入 |

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
下载视频（360p → 480p → 默认）
    ↓
提取音频
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

## 依赖说明

### 核心依赖

| 包 | 版本 | 用途 |
|---|------|------|
| lark-oapi | ^1.2.20 | 飞书开放平台 SDK |
| openai | ^1.55.0 | OpenAI API（用于 Whisper） |
| requests | ^2.32.0 | HTTP 请求 |
| you-get | ^0.4.1690 | 视频下载 |
| ffmpeg-python | ^0.2.0 | 音频处理 |

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
python test_short_link.py          # 测试短链接解析
python test_simple_write.py        # 测试文档写入
python test_document_api.py        # 测试文档 API
```

### 添加新功能

1. 在对应模块中添加功能
2. 更新 [task.py](../task.py) 中的处理流程
3. 在 [tests/](../tests/) 中添加测试脚本
4. 在 [docs/](./) 中添加文档

## 文档说明

| 文档 | 说明 |
|------|------|
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | 项目结构说明（本文件） |
| [VIDEO_QUALITY_CONTROL.md](./VIDEO_QUALITY_CONTROL.md) | 视频清晰度控制策略 |
| [DOC_CONTENT_WRITE_FIX.md](./DOC_CONTENT_WRITE_FIX.md) | 文档内容写入问题修复 |
| [FEISHU_DOC_WRITE_API_SOLUTION.md](./FEISHU_DOC_WRITE_API_SOLUTION.md) | 飞书文档 API 解决方案 |
| [SHORT_LINK_PARSING.md](./SHORT_LINK_PARSING.md) | B站短链接解析功能 |

## 常见问题

### Q: 临时文件存储在哪里？

A: 临时文件默认存储在 `./temp` 目录，处理完成后会自动清理。处理结果会保存在 `./temp/results/` 目录。

### Q: 如何修改下载清晰度策略？

A: 编辑 [bilibili_utils.py](../bilibili_utils.py:203) 中的 `quality_tier` 列表：

```python
quality_tier = ["360p", "480p", None]  # 当前策略
```

### Q: 如何配置代理？

A: 参阅 [PROXY_SETUP.md](./PROXY_SETUP.md)

### Q: WebSocket 连接失败怎么办？

A: 参阅 [WEBSOCKET_SETUP.md](./WEBSOCKET_SETUP.md)

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

测试日志保存在 [tests/test_write.log](../tests/test_write.log)

---

**最后更新**: 2026-03-08
**版本**: 1.0.0
