# B站视频下载问题诊断和解决方案

## 问题现象

运行 `test_video_quality.py` 时，所有测试都超时：

```
ERROR - 命令执行超时
ERROR - 格式 '360p' 测试超时
ERROR - 格式 '480p' 测试超时
...
```

## 原因分析

you-get 无法访问B站，可能原因：
1. 网络连接问题
2. 需要代理
3. B站对 you-get 的访问限制
4. you-get 版本过旧

## 诊断步骤

### 第一步：运行诊断工具

```bash
cd tests
python diagnose_you_get.py
```

这会检查：
- you-get 是否安装
- 网络连接是否正常
- 代理设置
- you-get 基本功能

### 第二步：测试 yt-dlp

```bash
# 安装 yt-dlp
pip install yt-dlp

# 测试 yt-dlp
cd tests
python test_yt_dlp.py
```

### 第三步：根据结果选择方案

## 解决方案

### 方案1：配置代理（如果需要代理）

如果你需要代理访问B站：

**Windows PowerShell**：
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# 然后运行测试
python test_video_quality.py
```

**永久配置（.env 文件）**：
```bash
# 在 .env 文件中添加
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 方案2：使用 yt-dlp（推荐）

yt-dlp 是更现代、更稳定的替代工具：

**优势**：
- 更频繁的更新
- 更好的B站支持
- 更强大的格式选择
- 更好的代理支持

**安装**：
```bash
pip install yt-dlp
```

**测试**：
```bash
cd tests
python test_yt_dlp.py
```

**实现示例**：
```python
# src/bilibili_utils.py

import yt_dlp

def download_video(video_id: str) -> str:
    """使用 yt-dlp 下载视频"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'worst',  # 最低质量
        'outtmpl': './temp/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

### 方案3：只下载音频（最佳方案）

对于音频转文字项目，直接下载音频是最佳选择：

**优势**：
- 速度最快（跳过视频）
- 文件最小（约5-10MB vs 500MB）
- 直接获得MP3，无需提取
- 音频质量完全满足识别需求

**实现**：
```python
import yt_dlp

def download_audio_only(video_id: str) -> str:
    """只下载音频"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': './temp/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',  # 128kbps 足够
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

### 方案4：更新 you-get

```bash
pip install --upgrade you-get
```

### 方案5：使用备用视频

某些视频可能有地区限制，尝试其他视频：
```python
# 测试脚本中可以更换视频ID
test_video_id = "BV1xx411c7mD"  # 换一个视频
```

## 推荐流程

### 立即行动（5分钟）

```bash
# 1. 诊断问题
cd tests
python diagnose_you_get.py

# 2. 安装 yt-dlp
pip install yt-dlp

# 3. 测试 yt-dlp
python test_yt_dlp.py

# 4. 如果成功，使用 yt-dlp
```

### 长期方案（30分钟）

1. **选择工具**：推荐 yt-dlp
2. **更新代码**：修改 `src/bilibili_utils.py`
3. **测试验证**：运行完整流程
4. **性能对比**：验证改进效果

## 代码迁移指南

### from you-get to yt-dlp

#### 旧代码（you-get）
```python
import subprocess

def download_video(video_id: str):
    url = f"https://www.bilibili.com/video/{video_id}"

    cmd = ["you-get", "-o", "./temp", url]
    result = subprocess.run(cmd, ...)
```

#### 新代码（yt-dlp）
```python
import yt_dlp

def download_video(video_id: str):
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'worst',
        'outtmpl': './temp/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

#### 最优方案（只下载音频）
```python
import yt_dlp

def download_audio_for_transcription(video_id: str):
    """只下载音频，跳过视频"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': './temp/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

## 性能对比

| 方案 | 文件大小 | 下载时间 | 提取步骤 | 总耗时 |
|------|---------|---------|---------|--------|
| you-get (1080p) | ~500MB | 5-10分钟 | 需要提取 | 6-12分钟 |
| you-get (480p) | ~100MB | 1-2分钟 | 需要提取 | 2-4分钟 |
| yt-dlp (音频) | ~5MB | 10-30秒 | 直接MP3 | **10-30秒** |

**结论**：只下载音频可以节省 95%+ 的时间和空间。

## 常见问题

### Q: yt-dlp 也会超时怎么办？

**A**: 尝试：
1. 配置代理：`yt-dlp --proxy http://127.0.0.1:7890 URL`
2. 增加超时：`yt-dlp --socket-timeout 60 URL`
3. 使用cookies：`yt-dlp --cookies cookies.txt URL`

### Q: 如何保持兼容性？

**A**: 实现回退机制：
```python
def download_video_fallback(video_id: str):
    # 优先使用 yt-dlp
    try:
        return download_with_yt_dlp(video_id)
    except:
        pass

    # 回退到 you-get
    try:
        return download_with_you_get(video_id)
    except:
        pass

    # 都失败
    return None
```

### Q: 需要修改项目其他部分吗？

**A**: 如果只下载音频，需要修改流程：
```python
# 旧流程
download_video() -> extract_audio() -> transcribe()

# 新流程（只下载音频）
download_audio() -> transcribe()  # 跳过提取步骤
```

## 相关文档

- [yt-dlp 替代方案](YT_DLP_ALTERNATIVE.md) - 详细实现指南
- [视频清晰度测试](VIDEO_QUALITY_TESTING.md) - 测试说明
- [视频清晰度控制](VIDEO_QUALITY_CONTROL.md) - 当前实现

## 总结

**快速解决**：
1. 运行 `python diagnose_you_get.py` 诊断问题
2. 安装并测试 `yt-dlp`
3. 如果成功，迁移到 yt-dlp

**最佳实践**：
- 使用 yt-dlp 替代 you-get
- 只下载音频（跳过视频）
- 128kbps MP3 足够识别

**预期效果**：
- 下载时间：从 5-10分钟 → 10-30秒
- 文件大小：从 500MB → 5MB
- 总体提速：**20倍+**

---

**最后更新**: 2026-03-09
**版本**: 1.0.0
