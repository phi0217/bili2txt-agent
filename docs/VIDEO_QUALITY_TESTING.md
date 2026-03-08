# B站视频清晰度测试指南

## 测试目的

测试不同的 B站视频下载清晰度选项，找出适合音频转文字的最低可用清晰度，以：
- 减少下载时间
- 节省带宽和存储
- 避免登录要求
- 获取足够的音频质量

## 测试脚本

### 1. test_video_quality.py - 全面格式测试

**功能**：
- 检测视频支持的所有格式
- 批量测试多个清晰度选项
- 分析并推荐最佳格式
- 生成实现建议

**运行**：
```bash
cd tests
python test_video_quality.py
```

**测试内容**：
1. 格式检测（`you-get --info`）
2. 单个格式测试
3. 批量格式测试

**测试的格式**：
- 360p, 480p, 720p, 1080p
- flv360, flv480, flv720
- dash-flv360, dash-flv480
- dash-mp4360, dash-mp4480
- 数字格式ID: 16, 32, 64, 80

**输出**：
```
测试 1: 检测视频支持的格式
============================================================
执行命令: you-get --info https://www.bilibili.com/video/...

测试 2: 尝试下载格式 '360p'
============================================================
✓ 格式 '360p' 可用

测试结果分析
============================================================
成功的格式:
  ✓ 360p
  ✓ 480p

推荐策略:
  建议使用格式: 360p
```

### 2. test_actual_download.py - 实际下载测试

**功能**：
- 测试当前 `download_video` 函数
- 分析实际下载的文件大小
- 推测实际清晰度
- 手动测试不同格式参数

**运行**：
```bash
cd tests
python test_actual_download.py
```

**测试内容**：
1. 使用当前实现下载视频
2. 分析文件大小和分辨率
3. 推测实际清晰度
4. 手动测试不同格式参数

**输出**：
```
测试当前 download_video 实现
============================================================
下载成功！
文件路径: ./temp/xxx.mp4
文件大小: 45.23 MB (47,428,165 bytes)

清晰度推测（基于文件大小）:
  ✓ 可能是 360p 或更低（理想情况）

文件信息:
  分辨率: 640x360
  ✓ 清晰度: 360p
```

## B站视频清晰度说明

### 常见清晰度

| 清晰度 | 分辨率 | 文件大小（10分钟视频） | 是否需要登录 | 音频质量 |
|--------|--------|---------------------|-------------|---------|
| 流畅 360P | 640x360 | ~50MB | 否 | 128K |
| 清晰 480P | 854x480 | ~100MB | 否 | 132K |
| 高清 720P | 1280x720 | ~200MB | 是 | 192K |
| 高清 1080P | 1920x1080 | ~500MB | 是 | 192K |

### you-get 格式说明

#### 格式名称

| 格式 | 说明 | 登录要求 |
|------|------|---------|
| `360p` | 流畅清晰度 | 否 |
| `480p` | 标清清晰度 | 否 |
| `720p` | 高清清晰度 | 是 |
| `flv360` | FLV格式 360P | 否 |
| `flv480` | FLV格式 480P | 否 |
| `dash-flv360` | DASH FLV 360P | 否 |
| `dash-mp4360` | DASH MP4 360P | 否 |

#### 数字格式ID

| ID | 清晰度 | 说明 |
|----|--------|------|
| 16 | 流畅 360P | 最低清晰度 |
| 32 | 清晰 480P | 标清 |
| 64 | 高清 720P | 需要登录 |
| 80 | 高清 1080P | 需要登录 |

### 音频质量

对于语音识别项目：
- **360p (128K)**：足够清晰，识别准确率最高可达 95%+
- **480p (132K)**：略好于 360p，但文件更大
- **720p+ (192K)**：音频质量更高，但对识别提升有限

**推荐**：360p 或 480p 完全满足语音识别需求。

## 测试结果分析

### 场景1：低清晰度可用（理想）

**测试输出**：
```
成功的格式:
  ✓ 360p
  ✓ 480p
  ✓ flv360

推荐策略:
  建议使用格式: 360p
```

**实现建议**：
```python
def download_video(video_id: str, format: str = "360p"):
    # 使用 360p 格式下载
```

### 场景2：所有指定格式失败

**测试输出**：
```
失败的格式:
  ✗ 360p - 格式不存在
  ✗ 480p - 格式不存在
  ✗ flv360 - 需要登录

推荐策略:
  没有找到成功的格式

替代方案:
  1. 不指定格式，让 you-get 自动选择
  2. 使用 cookies 访问更多格式
```

**实现建议**：
```python
def download_video(video_id: str, format: Optional[str] = None):
    # 不指定格式，使用默认
```

### 场景3：部分格式可用

**测试输出**：
```
成功的格式:
  ✓ 480p

失败的格式:
  ✗ 360p - 格式不存在

推荐策略:
  建议使用格式: 480p
```

**实现建议**：
```python
def download_video(video_id: str, format: str = "480p"):
    # 使用可用的最低格式
```

## 常见问题

### Q1: 为什么我下载的都是默认清晰度？

**A**: 可能的原因：
1. `--format` 参数不正确
2. 指定的格式该视频不支持
3. you-get 版本问题

**解决方法**：
- 运行测试脚本检测可用格式
- 使用正确的格式名称
- 更新 you-get 到最新版本

### Q2: 360p 和 480p 哪个更好？

**A**: 对于语音识别：

| 对比项 | 360p | 480p |
|--------|------|------|
| 文件大小 | 小（50MB） | 中（100MB） |
| 下载时间 | 快（1-2分钟） | 中（2-3分钟） |
| 音频质量 | 128K（足够） | 132K（略好） |
| 识别准确率 | 95%+ | 95%+ |
| 登录要求 | 通常不需要 | 通常不需要 |

**推荐**：优先使用 360p，如果不可用则使用 480p。

### Q3: 如何确认实际下载的清晰度？

**A**: 使用 test_actual_download.py：

```bash
cd tests
python test_actual_download.py
```

该脚本会：
1. 下载视频
2. 检查文件大小
3. 使用 ffprobe 获取分辨率
4. 推测实际清晰度

### Q4: 格式参数不生效怎么办？

**A**: 检查清单：

1. **确认格式名称**：
   ```bash
   you-get --info https://www.bilibili.com/video/BV1xx...
   ```

2. **检查 you-get 版本**：
   ```bash
   you-get --version
   ```

3. **测试命令**：
   ```bash
   you-get --format 360p https://www.bilibili.com/video/BV1xx...
   ```

4. **查看日志**：
   ```bash
   # 查看 test_video_quality.log
   cat tests/test_video_quality.log
   ```

## 实现建议

### 方案1：固定格式（简单）

```python
def download_video(video_id: str, format: str = "360p"):
    cmd = ["you-get", "-o", temp_dir, "--format", format, url]
```

**优点**：简单直接
**缺点**：如果格式不存在会失败

### 方案2：阶梯式重试（推荐）

```python
def download_video(video_id: str):
    quality_tier = ["360p", "480p", None]

    for format in quality_tier:
        cmd = ["you-get", "-o", temp_dir]
        if format:
            cmd.extend(["--format", format])
        cmd.append(url)

        result = subprocess.run(cmd)

        if result.returncode == 0:
            return video_path
```

**优点**：自动回退，最大化成功率
**缺点**：实现稍复杂

### 方案3：智能检测（高级）

```python
def download_video(video_id: str):
    # 1. 检测可用格式
    formats = detect_available_formats(video_id)

    # 2. 选择最低格式
    lowest = find_lowest_format(formats)

    # 3. 下载
    return download_with_format(video_id, lowest)
```

**优点**：最智能，适配每个视频
**缺点**：需要额外请求，速度慢

## 后续步骤

1. **运行测试**：
   ```bash
   cd tests
   python test_video_quality.py
   python test_actual_download.py
   ```

2. **分析结果**：
   - 查看测试日志
   - 确定可用格式
   - 选择最佳策略

3. **更新代码**：
   - 根据测试结果更新 bilibili_utils.py
   - 实现推荐的下载策略

4. **验证效果**：
   - 测试实际下载
   - 确认清晰度
   - 测量性能提升

## 相关文档

- [视频清晰度控制](VIDEO_QUALITY_CONTROL.md) - 当前实现说明
- [项目结构说明](PROJECT_STRUCTURE.md) - 代码组织

---

**最后更新**: 2026-03-09
**版本**: 1.0.0
