# 短链接解析功能说明

## 功能概述

bili2txt-agent 现已支持 B站短链接（b23.tv）的自动解析，可以从用户发送的文本中智能提取视频ID，支持多种输入格式。

## 支持的输入格式

### 1. 直接视频ID
```
BV1GJ411x7h7
av123456
AV123456
```

### 2. 完整视频链接
```
https://www.bilibili.com/video/BV1GJ411x7h7
https://www.bilibili.com/video/av123456
```

### 3. 短链接（自动解析）✨
```
https://b23.tv/6IsW8ui
b23.tv/6IsW8ui
```

### 4. 混合文本
```
看这个视频 https://b23.tv/6IsW8ui 很有趣
推荐：BV1GJ411x7h7
```

## 解析流程

```
用户输入文本
    ↓
1. 正则直接匹配 BV/AV 号
    ↓ (未匹配)
2. 提取文本中的所有 URL
    ↓
3. 遍历 URL
    ↓
4. 检测是否为 b23.tv 短链接
    ↓ (是)
5. 发起 HEAD 请求解析重定向
    ↓
6. 从最终 URL 中提取视频ID
    ↓
返回视频ID
```

## 技术实现

### 核心函数

#### `extract_video_id(text: str) -> Optional[str]`
主入口函数，从文本中提取视频ID。

**特性**：
- 优先直接匹配（快速）
- 自动解析短链接
- 递归处理重定向
- 完善的错误处理

#### `resolve_short_link(short_url: str, timeout: int = 5) -> Optional[str]`
解析短链接，获取真实URL。

**实现**：
```python
requests.head(url, allow_redirects=True, timeout=5)
```

**超时设置**：5秒，避免长时间阻塞

#### `extract_id_from_url(url: str) -> Optional[str]`
从URL中提取视频ID，支持递归调用。

**支持的路径格式**：
- `/video/BVxxxx`
- `/video/avxxxx`
- `/BVxxxx`
- `/avxxxx`

## 错误处理

### 网络错误
- 超时：记录日志，返回 None
- 连接失败：记录日志，返回 None
- 非200状态码：记录日志，返回 None

### 格式错误
- 无效URL：跳过，继续处理下一个
- 无法提取ID：返回 None

所有错误都被捕获，不会抛出未处理异常。

## 性能考虑

### 1. 优先直接匹配
直接正则匹配 BV/AV 号，无需网络请求，性能最优。

### 2. 短链接解析缓存
当前实现未缓存，每次都需要发起 HTTP 请求。

**未来优化**：可以添加 LRU 缓存，避免重复解析同一短链接。

### 3. 超时保护
短链接解析设置 5 秒超时，避免长时间阻塞。

### 4. 后台线程
视频处理本身在后台线程中运行，短链接解析的短暂阻塞不会影响 WebSocket 事件循环。

## 依赖项

新增依赖：
```bash
requests>=2.31.0
```

安装方法：
```bash
pip install -r requirements.txt
```

## 测试

运行测试脚本：
```bash
python test_short_link.py
```

测试覆盖：
- ✅ 直接BV/AV号匹配
- ✅ 完整URL解析
- ✅ 短链接解析（需要网络）
- ✅ 混合文本处理
- ✅ 多链接处理（取第一个）
- ✅ 无效输入处理
- ✅ 错误处理

## 使用示例

### 在飞书中发送消息

**示例 1**：短链接
```
https://b23.tv/6IsW8ui
```

机器人回复：
```
✅ 已收到：BV1GJ411x7h7
📥 开始下载视频...
```

**示例 2**：混合文本
```
推荐这个视频 https://b23.tv/6IsW8ui 讲得很好
```

机器人同样能正确识别并处理。

**示例 3**：完整链接
```
https://www.bilibili.com/video/BV1GJ411x7h7
```

直接提取，无需解析短链接。

## 注意事项

### 1. 网络依赖
短链接解析需要网络连接，如果网络不可用，会解析失败。

### 2. 隐私考虑
短链接解析会向 b23.tv 发起 HTTP HEAD 请求，仅用于获取重定向目标，不下载任何内容。

### 3. 防滥用
如果担心用户恶意发送大量短链接导致大量请求，可以：
- 添加速率限制
- 使用缓存减少重复请求
- 设置请求频率阈值

### 4. User-Agent
请求使用标准浏览器 User-Agent，避免被识别为爬虫：
```python
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

## 日志示例

### 成功解析
```
[Lark] [INFO] Received message - User: xxx, Content: https://b23.tv/6IsW8ui
[bili2txt-agent] [DEBUG] 提取到 1 个URL: ['https://b23.tv/6IsW8ui']
[bili2txt-agent] [DEBUG] 检测到b23.tv短链接，开始解析: https://b23.tv/6IsW8ui
[bili2txt-agent] [DEBUG] 发起 HEAD 请求解析短链接: https://b23.tv/6IsW8ui
[bili2txt-agent] [DEBUG] 短链接解析成功: https://b23.tv/6IsW8ui → https://www.bilibili.com/video/BV1GJ411x7h7
[bili2txt-agent] [INFO] 从URL提取到视频ID: BV1GJ411x7h7 (源URL: https://b23.tv/6IsW8ui)
```

### 解析失败
```
[bili2txt-agent] [DEBUG] 检测到b23.tv短链接，开始解析: https://b23.tv/invalid
[bili2txt-agent] [ERROR] 解析短链接时发生网络错误: https://b23.tv/invalid, 错误: Connection timeout
[bili2txt-agent] [WARNING] 短链接解析失败: https://b23.tv/invalid
```

## 未来优化方向

1. **缓存机制**：使用 LRU 缓存避免重复解析同一短链接
2. **并发请求**：如果用户发送多个短链接，可以并发解析
3. **更智能的提取**：支持更多B站链接格式（如专栏、文章）
4. **预检查**：先检查URL是否已包含视频ID，避免不必要的请求

## 相关文件

- [bilibili_utils.py](bilibili_utils.py) - 核心实现
- [test_short_link.py](test_short_link.py) - 测试脚本
- [requirements.txt](requirements.txt) - 依赖列表
