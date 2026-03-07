# 飞书 WebSocket 长连接配置指南（官方 EventDispatcherHandler 方式）

## 重要说明

本项目使用飞书官方推荐的 `EventDispatcherHandler` 方式来处理 WebSocket 事件，这是最标准和稳定的实现方式。

## 飞书开放平台配置（必需步骤）

### 1. 创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建应用 → 选择 **"自建应用"**
3. 记录 **App ID** 和 **App Secret**

### 2. 配置权限管理

在 **"权限管理"** 中添加以下权限：

- `im:message` - 获取与发送消息
- `im:message:send_as_bot` - 以应用身份发送消息
- `im:chat` - 获取群组信息（可选）

### 3. 配置事件订阅（关键！）

在 **"事件订阅"** 中：

1. 订阅以下事件：
   - ✅ `im.message.receive_v1` - 接收消息事件

2. **重要：选择「使用长连接接收事件」**
   - 在事件订阅页面，选择 **"长连接"** 模式
   - 不是 HTTP 回调模式

3. **创建并发布版本**
   - 点击 **"管理版本"**
   - 创建新版本
   - **必须发布版本**，否则事件订阅不会生效

### 4. 添加机器人

- 在飞书中找到您的机器人
- 打开聊天或添加到群聊

---

## 运行程序

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
TEMP_DIR=./temp
FEISHU_DOMAIN=https://www.feishu.cn
```

### 3. 启动程序

```bash
python main.py
```

---

## 验证连接成功

如果配置正确，您会看到：

```
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?...
```

这表示 WebSocket 连接成功建立！

---

## 测试机器人

在飞书中发送测试消息：

1. 发送 "hello" 测试机器人是否在线
2. 发送 B站视频链接测试完整功能：
   ```
   https://www.bilibili.com/video/BV1xx411c7mD
   ```

机器人应该会立即回复：
```
✅ 已收到：BV1xx411c7mD
📥 开始下载视频...
```

然后陆续发送处理状态更新。

---

## 关键代码说明

### EventDispatcherHandler 注册方式

```python
from lark_oapi import EventDispatcherHandler, ws, im

# 创建事件处理器
event_handler = EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(handle_p2_im_message) \
    .build()

# 创建 WebSocket 客户端
cli = ws.Client(
    app_id=config.FEISHU_APP_ID,
    app_secret=config.FEISHU_APP_SECRET,
    event_handler=event_handler,
    log_level=LogLevel.INFO
)

# 启动（阻塞）
cli.start()
```

### 事件处理器函数签名

```python
def handle_p2_im_message(data: im.v1.P2ImMessageReceiveV1) -> None:
    """处理接收消息 v2.0 事件"""
    message = data.event.message
    sender_id = data.event.sender.sender_id.open_id

    # 飞书的 content 是 JSON 字符串，需要用 eval 解析
    content_dict = eval(message.content)
    text = content_dict.get("text", "").strip()

    # 处理业务逻辑...
```

---

## 常见问题

### Q: 连接超时怎么办？

**A:** 检查以下几点：

1. **版本是否已发布**
   - 访问飞书开放平台
   - 确认版本状态是"已发布"

2. **是否选择了长连接模式**
   - 在事件订阅页面
   - 确认选择了"使用长连接接收事件"

3. **事件订阅是否正确**
   - 确认订阅了 `im.message.receive_v1`

4. **权限是否已添加**
   - 确认添加了 `im:message` 等权限

### Q: 能否发送消息但收不到回复？

**A:** 这说明 WebSocket 连接成功，但事件未正确触发。检查：

1. 日志中是否有 "Received P2 IM message event"
2. 如果没有，说明事件订阅配置有问题
3. 如果有但没处理，检查代码逻辑

### Q: HTTP_PROXY 配置有效吗？

**A:** `lark-oapi` SDK 的 WebSocket 客户端不支持直接传代理参数。如果需要代理：

1. 在 `.env` 文件中配置：
   ```bash
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```

2. 或者使用系统代理设置

---

## 参考资料

- [飞书开放平台文档](https://open.feishu.cn/)
- [WebSocket 事件订阅指南](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-subscription-guide-overview)
- [lark-oapi SDK 文档](https://github.com/larksuite/oapi-sdk-python)
