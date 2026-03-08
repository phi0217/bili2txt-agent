# 使用 yt-dlp 替代 you-get

## 问题说明

you-get 在某些环境下可能无法正常访问B站，导致所有请求超时。这通常是因为：
- 网络连接问题
- 需要代理
- B站对you-get的访问限制
- you-get版本过旧

## 解决方案：使用 yt-dlp

yt-dlp 是一个更现代、更强大的视频下载工具，是 youtube-dl 的增强版。

### 优势

1. **更稳定** - 更频繁的更新，更好的B站支持
2. **格式选择** - 更强大的格式选择语法
3. **代理支持** - 内置代理支持
4. **活跃维护** - 社区活跃，bug修复快

### 安装

```bash
pip install yt-dlp
```

### 使用方法

#### 基本下载

```bash
# 下载视频（默认最佳质量）
yt-dlp https://www.bilibili.com/video/BV1xx...

# 只下载音频
yt-dlp -x --audio-format mp3 https://www.bilibili.com/video/BV1xx...
```

#### 指定清晰度

yt-dlp 使用强大的格式选择语法：

```bash
# 下载最低清晰度（推荐用于音频转文字）
yt-dlp -f "worst" https://www.bilibili.com/video/BV1xx...

# 下载指定高度
yt-dlp -f "bestvideo[height<=360]+bestaudio" https://www.bilibili.com/video/BV1xx...

# 下载480p
yt-dlp -f "bestvideo[height<=480]+bestaudio" https://www.bilibili.com/video/BV1xx...

# 只下载音频（最佳质量）
yt-dlp -f "bestaudio" --extract-audio --audio-format mp3 https://www.bilibili.com/video/BV1xx...
```

#### 格式选择语法

| 格式字符串 | 说明 |
|-----------|------|
| `worst` | 最低质量 |
| `bestvideo[height<=360]+bestaudio` | 360p视频+最佳音频 |
| `bestvideo[height<=480]+bestaudio` | 480p视频+最佳音频 |
| `bestaudio` | 仅音频，最佳质量 |
| `worstaudio` | 仅音频，最低质量 |

#### 输出控制

```bash
# 指定输出目录和文件名
yt-dlp -o "./temp/%(title)s.%(ext)s" https://www.bilibili.com/video/BV1xx...

# 只下载不转换
yt-dlp -f "bestvideo[height<=360]+bestaudio" --merge-output-format mp4 https://www.bilibili.com/video/BV1xx...
```

## Python 集成

### 方法1：使用 subprocess

```python
import subprocess

def download_video_yt_dlp(video_id: str) -> str:
    """使用 yt-dlp 下载视频"""
    url = f"https://www.bilibili.com/video/{video_id}"
    temp_dir = "./temp"

    # 下载最低清晰度视频
    cmd = [
        "yt-dlp",
        "-f", "worst",  # 最低质量
        "-o", f"{temp_dir}/%(title)s.%(ext)s",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # 解析输出获取文件路径
        # yt-dlp 会输出下载的文件路径
        for line in result.stdout.split('\n'):
            if '[download] Destination:' in line:
                return line.split('Destination:')[-1].strip()

    return None
```

### 方法2：使用 yt-dlp Python 库

```python
import yt_dlp

def download_video_yt_dlp_lib(video_id: str) -> str:
    """使用 yt-dlp Python 库下载视频"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'worst',  # 最低质量
        'outtmpl': './temp/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

### 方法3：只下载音频（推荐）

对于音频转文字项目，可以直接只下载音频：

```python
import yt_dlp

def download_audio_only(video_id: str) -> str:
    """只下载音频，不需要视频"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'bestaudio',  # 最佳音频
        'outtmpl': './temp/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

## 对比：you-get vs yt-dlp

| 特性 | you-get | yt-dlp |
|------|---------|---------|
| 更新频率 | 较低 | 活跃 |
| B站支持 | 基础 | 优秀 |
| 格式选择 | `--format` | 强大的 `-f` 语法 |
| 音频提取 | 需要ffmpeg | 内置支持 |
| 代理支持 | 需要手动设置 | `--proxy` 参数 |
| Python库 | 无 | 有 |
| 稳定性 | 一般 | 优秀 |

## 实际实现建议

### 方案1：完全替换为 yt-dlp

```python
# src/bilibili_utils.py

import yt_dlp

def download_video(video_id: str) -> str:
    """下载B站视频（使用 yt-dlp）"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'worstvideo[height<=480]+bestaudio',  # 最低480p
        'outtmpl': './temp/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logger.error(f"下载失败: {e}")
        return None
```

### 方案2：混合使用（推荐）

```python
def download_video_smart(video_id: str) -> str:
    """智能下载：优先 yt-dlp，失败则 you-get"""

    # 先尝试 yt-dlp
    try:
        return download_with_yt_dlp(video_id)
    except:
        logger.warning("yt-dlp 失败，尝试 you-get")

    # 回退到 you-get
    try:
        return download_with_you_get(video_id)
    except:
        logger.error("所有方法都失败")
        return None
```

### 方案3：只下载音频（最推荐）

对于音频转文字项目，直接下载音频更高效：

```python
def download_audio_for_transcription(video_id: str) -> str:
    """下载音频用于语音识别"""
    url = f"https://www.bilibili.com/video/{video_id}"

    ydl_opts = {
        'format': 'bestaudio/best',  # 最佳音频
        'outtmpl': './temp/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',  # 128kbps 足够识别
        }],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

**优势**：
- ✅ 跳过视频下载，速度快 10倍+
- ✅ 文件大小减少 95%+
- ✅ 直接获得音频，无需提取
- ✅ 音频质量完全满足识别需求

## 代理配置

### yt-dlp 代理设置

```bash
# 命令行
yt-dlp --proxy http://127.0.0.1:7890 URL

# 环境变量
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# Python 代码
ydl_opts = {
    'proxy': 'http://127.0.0.1:7890',
    # ... 其他选项
}
```

## 测试 yt-dlp

### 安装并测试

```bash
# 1. 安装
pip install yt-dlp

# 2. 测试基本功能
yt-dlp --version

# 3. 测试下载（不实际下载，只查看信息）
yt-dlp --list-formats https://www.bilibili.com/video/BV1GJ411x7h7

# 4. 测试下载最低质量
yt-dlp -f "worst" https://www.bilibili.com/video/BV1GJ411x7h7

# 5. 测试只下载音频
yt-dlp -f "bestaudio" --extract-audio --audio-format mp3 https://www.bilibili.com/video/BV1GJ411x7h7
```

## 迁移步骤

1. **安装 yt-dlp**：
   ```bash
   pip install yt-dlp
   ```

2. **测试功能**：
   ```bash
   cd tests
   python diagnose_you_get.py  # 先诊断 you-get
   yt-dlp --list-formats https://www.bilibili.com/video/BV1GJ411x7h7  # 测试 yt-dlp
   ```

3. **更新代码**：
   - 修改 `src/bilibili_utils.py`
   - 添加 yt-dlp 下载方法
   - 保留 you-get 作为备用

4. **测试验证**：
   - 运行完整流程测试
   - 验证音频质量
   - 确认性能提升

## 总结

对于音频转文字项目：

- ✅ **推荐使用 yt-dlp** - 更稳定，功能更强
- ✅ **只下载音频** - 跳过视频，速度最快
- ✅ **最低音频质量** - 128kbps 完全够用
- ✅ **保留 you-get** - 作为备用方案

---

**最后更新**: 2026-03-09
**版本**: 1.0.0
