# bili2txt-agent 文档

欢迎来到 bili2txt-agent 项目文档！

## 📚 文档索引

### 快速开始

- [项目结构说明](PROJECT_STRUCTURE.md) - 项目目录结构和模块说明
- [配置指南](CONFIGURATION.md) - 环境变量配置详解
- [README](../README.md) - 项目说明和快速开始指南

### 核心功能

- [视频下载方案](VIDEO_DOWNLOAD.md) - yt-dlp 音频下载（300倍速度提升）
- [飞书文档创建](FEISHU_DOCS.md) - 文档创建和管理
- [视频处理缓存](CACHE.md) - 智能缓存，避免重复处理
- [并发处理支持](CONCURRENT_PROCESSING.md) - 多线程处理，支持批量任务

### 技术实现

- [短链接解析](SHORT_LINK_PARSING.md) - B站短链接支持
- [WebSocket 配置](WEBSOCKET_SETUP.md) - 飞书长连接配置
- [代理设置](PROXY_SETUP.md) - 网络代理配置

## 🎯 按场景查找文档

### 我想了解...

**如何快速开始？**
1. 阅读 [README](../README.md) 了解项目
2. 查看 [配置指南](CONFIGURATION.md) 配置环境变量
3. 查看 [项目结构说明](PROJECT_STRUCTURE.md) 了解代码组织
4. 运行 `python main.py` 启动服务

**如何下载视频？**
- 查看 [视频下载方案](VIDEO_DOWNLOAD.md) 了解 yt-dlp 音频下载
- 下载速度：1-2秒（原来需要 5-10分钟）
- 空间节省：99.8%（1MB vs 500MB）

**如何配置飞书？**
- 查看 [配置指南](CONFIGURATION.md) 设置飞书应用
- 查看 [飞书文档创建](FEISHU_DOCS.md) 了解文档 API
- 查看 [WebSocket 配置](WEBSOCKET_SETUP.md) 设置长连接

**遇到问题怎么办？**
- 查看 [配置指南](CONFIGURATION.md) 的故障排除部分
- 查看 [视频下载方案](VIDEO_DOWNLOAD.md) 的常见问题
- 查看 [飞书文档创建](FEISHU_DOCS.md) 的故障排除部分

## 🚀 快速参考

### 系统架构

```
用户发送 B站视频链接
    ↓
飞书 WebSocket 接收消息
    ↓
提取视频 ID（支持短链接）
    ↓
检查缓存？├─ 是 → 直接返回缓存结果 ✅
    └─ 否 ↓
下载音频（1-2秒）✨ yt-dlp
    ↓
语音识别（Whisper base）
    ↓
文本精转（DeepSeek API）
    ↓
创建飞书文档
    ↓
保存到缓存
    ↓
返回文档链接给用户
```

### 性能提升

| 指标 | 旧方案 | 新方案 | 提升 |
|------|--------|--------|------|
| 下载速度 | 5-10分钟 | 1-2秒 | **300倍** |
| 文件大小 | ~500MB | ~1MB | **99.8%** |
| 首次处理 | 8-17分钟 | 3-7分钟 | **2-5倍** |
| 再次处理（缓存） | 3-7分钟 | **<5秒** | **36-84倍** |

### 核心依赖

- **lark-oapi** - 飞书 SDK
- **openai** - Whisper 语音识别
- **yt-dlp** - 音频下载（推荐）
- **requests** - HTTP 请求
- **python-dotenv** - 配置管理

## 📝 文档贡献

欢迎改进文档！

### 文档风格

- 使用清晰的标题层级
- 提供代码示例
- 添加必要的注释
- 保持更新

### 提交文档

1. 编辑或创建文档文件
2. 在文档顶部添加日期和版本信息
3. 更新本索引文件（如需要）
4. 提交 Pull Request

## 🔗 相关链接

- [项目 README](../README.md)
- [GitHub 仓库](https://github.com/your-repo/bili2txt-agent)

## 📞 获取帮助

- 📖 查看相关文档
- 🐛 [提交 Issue](https://github.com/your-repo/bili2txt-agent/issues)
- 💬 加入讨论

---

**最后更新**: 2026-03-09
**维护**: bili2txt-agent 项目组
