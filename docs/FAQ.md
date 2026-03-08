# 常见问题解答

本文档汇总了 bili2txt-agent 的常见问题和解决方案。

## 目录

- [安装和配置](#安装和配置)
- [下载问题](#下载问题)
- [飞书集成](#飞书集成)
- [语音识别](#语音识别)
- [性能优化](#性能优化)
- [错误处理](#错误处理)

---

## 安装和配置

### Q: 如何安装项目依赖？

**A**: 运行以下命令：

```bash
# 安装基础依赖
pip install -r requirements.txt

# 推荐：安装 yt-dlp（300倍速度提升）
pip install yt-dlp

# 可选：安装 you-get（备用下载器）
pip install you-get
```

### Q: 如何配置环境变量？

**A**:

1. 复制配置模板：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，至少配置以下变量：
   ```bash
   FEISHU_APP_ID=cli_xxxxxxxxx
   FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
   ```

3. 重启程序

详细配置说明请参考 [配置指南](CONFIGURATION.md)

### Q: FFmpeg 未安装怎么办？

**A**: 根据操作系统安装 FFmpeg：

**Windows**:
```powershell
# 运行项目提供的安装脚本
.\install-ffmpeg.ps1
```

**Linux (Debian/Ubuntu)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Mac (Homebrew)**:
```bash
brew install ffmpeg
```

### Q: 验证安装是否成功？

**A**: 运行测试脚本：

```bash
cd tests
python test_integration.py
```

如果所有测试通过，说明安装成功。

---

## 下载问题

### Q: 下载速度很慢怎么办？

**A**: 使用 yt-dlp 只下载音频：

- **旧方案**: 下载视频（5-10分钟，~500MB）
- **新方案**: 只下载音频（1-2秒，~1MB）

安装 yt-dlp：
```bash
pip install yt-dlp
```

系统会自动优先使用 yt-dlp，无需修改配置。

详情请参考 [视频下载方案](VIDEO_DOWNLOAD.md)

### Q: yt-dlp 下载失败怎么办？

**A**: 系统会自动回退到 you-get：

```
⚠️ 音频下载失败，尝试旧方式
📥 正在下载视频: BV1xx411c7mD
```

无需手动干预，系统会自动选择可用的下载方式。

### Q: 如何确认是否使用了 yt-dlp？

**A**: 查看日志输出：

**使用 yt-dlp**：
```
✅ yt-dlp 下载器已启用（只下载音频模式）
🎵 正在下载音频: BV1xx411c7mD
✅ 音频下载成功（1-2秒）
```

**使用旧方式**：
```
⚠️ yt-dlp 未安装，将使用旧的下载方式
📥 正在下载视频: BV1xx411c7mD
```

### Q: 如何强制使用旧的下载方式？

**A**: 卸载 yt-dlp：

```bash
pip uninstall yt-dlp
```

或删除 `src/bilibili_downloader.py` 文件。

### Q: 下载的视频/音频文件存储在哪里？

**A**:
- 临时文件默认存储在 `./temp` 目录
- 处理完成后会自动清理
- 可通过环境变量 `TEMP_DIR` 自定义路径

### Q: 下载失败，提示网络错误？

**A**: 可能的解决方案：

1. **配置代理**（如果使用代理）：
   ```bash
   export HTTP_PROXY=http://127.0.0.1:7890
   export HTTPS_PROXY=http://127.0.0.1:7890
   ```

2. **检查网络连接**：
   ```bash
   ping bilibili.com
   ```

3. **更新 yt-dlp**：
   ```bash
   pip install -U yt-dlp
   ```

4. **更换下载方式**：系统会自动回退到 you-get

---

## 飞书集成

### Q: 飞书连接失败怎么办？

**错误信息**：
```
Error connecting to Feishu: Invalid app credentials
```

**解决方案**：

1. 确认 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 正确
2. 检查飞书应用是否已启用
3. 确认飞书应用权限配置正确

权限要求：
- `im:message` - 接收和发送消息
- `docx:document` - 创建和管理文档
- `drive:drive` - 文档公开访问

### Q: 文档链接打不开？

**错误信息**：
```
文档链接无法访问
```

**解决方案**：

1. 检查 `FEISHU_DOC_DOMAIN` 配置
2. 确认域名格式正确（包含 `https://`）
3. 手动在浏览器中测试链接

常见域名：
- 国内飞书：`https://my.feishu.cn`
- 海外飞书：`https://docs.larksuite.com`

### Q: 文档创建成功但内容为空？

**错误信息**：
```
field validation failed: children[*].block_type is required
```

**解决方案**：已在新版本中修复。

确保使用最新代码，`block_type=2` 会自动设置。

### Q: WebSocket 连接断开？

**错误信息**：
```
WebSocket connection lost
```

**解决方案**：

1. 检查网络连接
2. 确认飞书服务状态
3. 系统会自动重连，无需手动干预

详情请参考 [WebSocket 配置](WEBSOCKET_SETUP.md)

### Q: 收不到飞书消息？

**解决方案**：

1. 确认已订阅事件：`im.message.receive_v1`
2. 检查机器人是否已添加到群组
3. 确认机器人权限：
   - 发送消息权限
   - 接收消息权限
4. 查看 `main.py` 日志，确认 WebSocket 连接成功

---

## 语音识别

### Q: Whisper 模型加载很慢？

**A**: 首次加载需要下载模型文件（~140MB）。

加载时间：
- 首次：1-2分钟（下载模型）
- 后续：5-10秒（从缓存加载）

### Q: 语音识别不准确怎么办？

**A**: 尝试以下方法：

1. **提高音频质量**：
   ```python
   # 在 src/bilibili_downloader.py 中
   audio_path = download_audio_only(video_id, audio_quality="192")
   ```

2. **使用更大的 Whisper 模型**：
   ```python
   # 在 src/asr_utils.py 中
   model = whisper.load_model("base")  # 可选: small, medium, large
   ```

3. **清理音频**：确保音频质量良好，无背景噪音

### Q: 语音识别很慢？

**A**: 这是正常现象。

识别时间（10分钟视频）：
- base 模型：2-5分钟
- small 模型：5-10分钟
- medium 模型：10-20分钟

推荐使用 **base 模型**，平衡速度和准确率。

---

## 性能优化

### Q: 如何提升处理速度？

**A**: 按优先级：

1. ✅ **使用 yt-dlp**（最重要）
   ```bash
   pip install yt-dlp
   ```
   速度提升：300倍

2. **调整音频质量**：
   ```python
   # 128kbps 足够识别
   audio_path = download_audio_only(video_id, audio_quality="128")
   ```

3. **使用合适的 Whisper 模型**：
   ```python
   # base 模型最快
   model = whisper.load_model("base")
   ```

### Q: 如何减少磁盘占用？

**A**:

1. **使用 yt-dlp 只下载音频**：
   - 旧方案：~500MB
   - 新方案：~1MB
   - 节省：99.8%

2. **定期清理临时文件**：
   ```bash
   rm -rf ./temp/*
   ```

3. **自动清理已启用**：处理完成后自动删除临时文件

### Q: 如何监控资源使用？

**A**:

**CPU 使用率**：
```bash
# Linux/Mac
top -p $(pgrep -f "python main.py")

# Windows
taskmgr.exe
```

**磁盘空间**：
```bash
# 查看临时目录大小
du -sh ./temp
```

**内存使用**：
```bash
# Python 进程内存
ps aux | grep "python main.py"
```

---

## 错误处理

### Q: 遇到错误怎么办？

**A**:

1. **查看日志**：
   - 控制台输出
   - `tests/*.log` 文件

2. **检查配置**：
   ```bash
   python verify_config.py
   ```

3. **运行测试**：
   ```bash
   cd tests
   python test_integration.py
   ```

4. **查看文档**：
   - [配置指南](CONFIGURATION.md)
   - [视频下载方案](VIDEO_DOWNLOAD.md)
   - [飞书文档创建](FEISHU_DOCS.md)

### Q: 如何报告问题？

**A**:

1. 收集信息：
   - 错误信息
   - 日志输出
   - 配置信息（隐藏敏感信息）
   - 复现步骤

2. 提交 Issue：
   - [GitHub Issues](https://github.com/your-repo/bili2txt-agent/issues)

3. 包含信息：
   - 操作系统和版本
   - Python 版本
   - 依赖版本（`pip list`）

### Q: 常见错误代码

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `KeyError: 'FEISHU_APP_ID'` | 缺少配置 | 配置 `.env` 文件 |
| `PermissionError: './temp'` | 目录权限问题 | 检查 `TEMP_DIR` 权限 |
| `ModuleNotFoundError: 'yt_dlp'` | yt-dlp 未安装 | `pip install yt-dlp` |
| `Invalid API key` | API 密钥错误 | 检查 `DEEPSEEK_API_KEY` |
| `field validation failed` | API 参数错误 | 更新到最新代码 |
| `WebSocket connection lost` | 网络问题 | 检查网络连接 |

---

## 其他问题

### Q: 支持哪些视频网站？

**A**: 目前仅支持 B站（bilibili.com）。

支持格式：
- 完整链接：`https://www.bilibili.com/video/BV1xx411c7mD`
- BV 号：`BV1xx411c7mD`
- AV 号：`av123456`
- 短链接：`b23.tv/xxx`（自动解析）

### Q: 可以处理多长的视频？

**A**:

- **推荐**：10-30 分钟的视频
- **最长**：2 小时（受 API 限制）
- **限制因素**：
  - Whisper 识别时间
  - DeepSeek API token 限制（3000 tokens）

### Q: 如何查看处理进度？

**A**: 查看控制台日志：

```
🎵 正在下载音频: BV1xx411c7mD
✅ 音频下载成功（1-2秒）
🎤 正在进行语音识别...
✅ 语音识别成功
🤖 正在进行文本精转...
✅ 文本精转成功
📝 正在创建文档...
✅ 文档创建成功
🔗 文档链接: https://my.feishu.cn/docx/xxxxxx
```

### Q: 如何停止程序？

**A**:

```bash
# 按 Ctrl+C 停止程序
# 系统会自动清理临时文件
```

### Q: 如何重启程序？

**A**:

```bash
# 停止程序（Ctrl+C）
# 重新启动
python main.py
```

### Q: 数据会保留吗？

**A**:

- ✅ 飞书文档：永久保存在飞书云端
- ❌ 临时文件：处理完成后自动删除
- ✅ 处理结果：保存在 `./temp/results/`（如果配置）

---

## 获取帮助

如果以上问题无法解决您的问题：

1. 📖 查看完整文档：
   - [配置指南](CONFIGURATION.md)
   - [视频下载方案](VIDEO_DOWNLOAD.md)
   - [飞书文档创建](FEISHU_DOCS.md)
   - [项目结构说明](PROJECT_STRUCTURE.md)

2. 🐛 提交 Issue：
   - [GitHub Issues](https://github.com/your-repo/bili2txt-agent/issues)

3. 💬 加入讨论：
   - GitHub Discussions

---

**最后更新**: 2026-03-09
**版本**: 1.0.0
