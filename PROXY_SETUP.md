# 飞书 WebSocket 长连接配置指南

## 概述

本项目使用飞书 WebSocket 长连接模式接收消息，无需公网服务器或 HTTP 回调地址。

## 问题现象

如果运行程序时出现以下错误：

```
[Lark] [ERROR] connect failed, err: timed out during opening handshake
[Lark] [INFO] trying to reconnect for the 1st time
```

或

```
WebSocket 连接失败！已重试 3 次。
```

这表示无法建立 WebSocket 长连接。

## 原因分析

1. **网络环境限制** - 防火墙或网络策略阻止 WebSocket 连接
2. **飞书应用配置不完整** - 事件订阅或权限未正确配置
3. **代理配置问题** - 需要配置代理才能访问飞书服务器

## 解决方案

### 方案 1：配置网络代理（推荐）

如果您使用代理软件（如 Clash、V2Ray、Shadowsocks 等），需要配置代理：

#### 1. 查找代理端口

**常见代理软件默认端口：**
- **Clash**: `7890`
- **V2Ray/NekoRay**: `10808` 或 `10809`
- **Shadowsocks**: `1080`

**查找代理端口方法：**

**Windows:**
- 打开代理软件设置
- 查看"HTTP 代理"或"SOCKS5 代理"设置
- 找到端口号（通常是 127.0.0.1:xxxx）

**macOS:**
```bash
# 系统偏好设置 → 网络 → 高级 → 代理
# 查看已配置的代理服务器和端口
```

**Linux:**
```bash
# 检查常见配置文件
cat ~/.config/clash/config.yaml | grep port
cat ~/.config/v2ray/config.json | grep port
```

#### 2. 编辑 .env 文件

在项目根目录的 `.env` 文件中添加：

```bash
# 将端口号替换为您的实际代理端口
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

#### 3. 重启程序

```bash
python main.py
```

#### 4. 验证代理配置

**Windows PowerShell:**
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
curl https://www.feishu.cn
```

**Linux/macOS:**
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
curl https://www.feishu.cn
```

如果能够访问飞书网站，说明代理配置正确。

### 方案 2：检查飞书应用配置

确保在飞书开放平台正确配置了应用：

#### 1. 访问飞书开放平台

https://open.feishu.cn/

#### 2. 创建/编辑应用

- **应用类型**：必须选择"自建应用"
- **记录应用凭证**：
  - App ID
  - App Secret

#### 3. 配置权限管理

在"权限管理"中添加以下权限：

- `im:message` - 获取与发送消息
- `im:message:send_as_bot` - 以应用身份发送消息
- `im:chat` - 获取群组信息（可选）

#### 4. 配置事件订阅

在"事件订阅"中订阅：

- **im.message.receive_v1** - 接收消息事件

**重要**：
- 订阅事件后，必须**创建并发布版本**
- 发布版本后，事件订阅才会生效

#### 5. 添加机器人到群组/聊天

- 在飞书中打开与机器人的聊天
- 或将机器人添加到群聊

### 方案 3：更新 SDK 版本

确保使用最新版本的 lark-oapi SDK：

```bash
pip install --upgrade lark-oapi
```

查看当前版本：
```bash
pip show lark-oapi
```

建议使用 `>=1.2.0` 版本。

## 测试连接

配置完成后，运行程序并查看日志：

### ✅ 成功连接

```
2026-03-08 02:37:40 - INFO - Using proxy - HTTP: http://127.0.0.1:7890, HTTPS: http://127.0.0.1:7890
2026-03-08 02:37:40 - INFO - Creating WebSocket client...
2026-03-08 02:37:40 - INFO - Event handler registered successfully
2026-03-08 02:37:40 - INFO - Starting WebSocket connection...
2026-03-08 02:37:42 - INFO - WebSocket connection established successfully
```

### ❌ 连接失败

```
2026-03-08 02:37:40 - WARNING - WebSocket connection timeout after 30s
2026-03-08 02:37:40 - ERROR - Max retries (3) reached
```

## 常见问题

### Q: 不使用代理可以直接连接吗？

**A:** 可以，但需要您的网络能够直接访问飞书服务器。如果遇到连接超时，通常需要配置代理。

### Q: 如何确认代理软件正在运行？

**A:** 检查系统托盘（Windows）或菜单栏（macOS），确保代理软件已启动并显示"连接中"或"已连接"状态。

### Q: 配置代理后仍然连接失败？

**A:** 请按以下步骤排查：

1. 确认代理端口正确（查看代理软件设置）
2. 确认代理软件正在运行
3. 测试代理是否工作：
   ```bash
   curl -x http://127.0.0.1:7890 https://www.feishu.cn
   ```
4. 检查防火墙是否阻止了 Python 程序访问网络
5. 尝试更换网络环境（如切换到手机热点）

### Q: 如何查看详细的错误信息？

**A:** 程序会输出详细的错误日志，包括：
- 错误类型
- 错误信息
- 可能的原因
- 解决方案建议

### Q: 飞书应用配置完成后多久生效？

**A:** 通常立即生效，但建议：
1. 确保已创建并发布版本
2. 重新启动机器人程序
3. 向机器人发送测试消息

## 获取帮助

如果以上方案都无法解决问题，请：

1. **检查程序日志**：查看完整的错误信息
2. **验证飞书配置**：重新检查飞书开放平台的应用配置
3. **测试网络连接**：尝试访问 https://www.feishu.cn
4. **查看飞书文档**：https://open.feishu.cn/document/server-docs/event-subscription-guide/event-subscription-guide-overview
5. **提交 Issue**：如果确认是程序问题，请在 GitHub 提交 Issue

## WebSocket vs HTTP 轮询

| 特性 | WebSocket 长连接 | HTTP 轮询 |
|------|------------------|-----------|
| 实时性 | ✅ 高（毫秒级） | ❌ 低（秒级） |
| 公网服务器 | ❌ 不需要 | ✅ 需要 |
| 本地部署 | ✅ 支持 | ❌ 需要 ngrok 等 |
| 资源消耗 | ✅ 低 | ❌ 高（持续轮询） |
| 配置复杂度 | ✅ 简单 | ❌ 复杂 |

**本项目采用 WebSocket 长连接模式，更适合本地部署。**

