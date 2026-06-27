# 学生端 API 文档

> 本文档面向学生端前端（Electron + Vue3）及第三方工具开发者，描述学生端后端的 HTTP API、WebSocket 协议及配置方式。

---

## 1. 服务概览

学生端后端运行在本机 `127.0.0.1:8772`，提供本地 HTTP API 供 Electron 前端调用。同时通过 WebSocket 连接教师端进行长连接通信。

| 项目 | 值 |
|------|-----|
| 默认监听地址 | `127.0.0.1` |
| 默认端口 | `8772`（可通过 `config.json` 的 `local_api_port` 修改） |
| 协议 | HTTP/1.1 |
| 数据格式 | JSON |

---

## 2. HTTP API

所有接口前缀为 `/api`，完整路径示例：`http://127.0.0.1:8772/api/health`

### 2.1 健康检查

```
GET /api/health
```

**响应：**

```json
{
  "status": "ok",
  "connected": true,
  "mode": "whitelist"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定 `"ok"` |
| `connected` | boolean | 是否已连接到教师端 WebSocket |
| `mode` | string | 当前网络模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

---

### 2.2 获取运行状态

```
GET /api/status
```

**响应：**

```json
{
  "mode": "whitelist",
  "connected": true,
  "controller_url": "ws://192.168.1.100:8765/ws",
  "controller_ip": "192.168.1.100",
  "hostname": "STU-001",
  "mac": "aa:bb:cc:dd:ee:ff",
  "filter_active": true,
  "dns_running": true,
  "rule_count": 15
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | string | 当前网络模式 |
| `connected` | boolean | WebSocket 连接状态 |
| `controller_url` | string | 教师端 WebSocket 地址 |
| `controller_ip` | string | 教师端 IP |
| `hostname` | string | 本机主机名 |
| `mac` | string | 本机 MAC 地址 |
| `filter_active` | boolean | 网络过滤器是否激活（whitelist/blacklist 模式为 true） |
| `dns_running` | boolean | DNS 代理是否运行 |
| `rule_count` | integer | 当前生效的域名规则数量 |

---

### 2.3 获取测试消息

```
GET /api/test_message
```

获取教师端最近一次发来的测试消息。

**响应：**

```json
{
  "message": "这是一条测试消息",
  "ts": 1719500000.123,
  "time_str": "2024-06-27 20:00:00"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 消息内容，未收到过时为空字符串 |
| `ts` | number | Unix 时间戳（秒），未收到过时为 `0` |
| `time_str` | string | 格式化时间字符串，未收到过时为空字符串 |

---

### 2.4 获取配置

```
GET /api/config
```

**响应：** 返回完整的 `config.json` 内容，参见 [第4节 配置文件](#4-配置文件)。

---

### 2.5 修改配置

```
POST /api/config
Content-Type: application/json

{
  "controller_url": "ws://192.168.1.200:8765/ws",
  "upstream_dns": "8.8.8.8"
}
```

**请求体：** 需要修改的配置项（部分更新，未传入的字段保持不变）。

**响应：**

```json
{
  "ok": true
}
```

> 注意：`controller_url` 修改后，WebSocket 客户端会在下一次重连时使用新地址。其他配置项立即生效。

---

### 2.5 切换网络模式（本地测试用）

```
POST /api/apply_mode
Content-Type: application/json

{
  "mode": "whitelist"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

**响应：**

```json
{
  "ok": true,
  "mode": "whitelist"
}
```

> 此接口用于前端本地测试，强制切换本机网络模式。正常运行时，模式由教师端通过 WebSocket 下发控制。

---

## 3. WebSocket 协议

学生端主动连接教师端 WebSocket（`ws://<教师IP>:8765/ws`），维持长连接。协议消息为 JSON 文本帧。

### 3.1 学生端 → 教师端

#### REGISTER — 上线注册

```json
{
  "type": "register",
  "payload": {
    "hostname": "STU-001",
    "ip": "192.168.1.101",
    "mac": "aa:bb:cc:dd:ee:ff",
    "mode": "disconnect"
  }
}
```

#### HEARTBEAT — 心跳

间隔 **20 秒** 发送。

```json
{
  "type": "heartbeat",
  "payload": {
    "filter_active": true,
    "net_state": "whitelist"
  }
}
```

#### STATUS — 状态上报

模式切换后主动上报。

```json
{
  "type": "status",
  "payload": {
    "filter_active": true,
    "dns_running": true,
    "rule_count": 15,
    "net_state": "whitelist"
  }
}
```

#### BROWSING_UPDATE — DNS 查询日志

间隔 **15 秒** 批量上报。

```json
{
  "type": "browsing_update",
  "payload": {
    "domains": [
      { "domain": "www.baidu.com", "ts": "20:15:30" },
      { "domain": "www.example.com", "ts": "20:15:31" }
    ]
  }
}
```

#### ACK — 确认应答

```json
{
  "type": "ack",
  "payload": {
    "ok": true,
    "message": "规则已应用"
  }
}
```

### 3.2 教师端 → 学生端

#### SET_FILTER — 设置网络模式

```json
{
  "type": "set_filter",
  "payload": {
    "enabled": true,
    "mode": "whitelist"
  }
}
```

| 字段 | 说明 |
|------|------|
| `enabled` | 是否启用过滤（`normal` 模式为 `false`，其余为 `true`） |
| `mode` | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

#### UPDATE_RULES — 更新规则

```json
{
  "type": "update_rules",
  "payload": {
    "domains": ["www.baidu.com", "www.example.com"],
    "lan_subnets": ["192.168.1.0/24"],
    "controller_ip": "192.168.1.100",
    "upstream_dns": "114.114.114.114",
    "mode": "whitelist",
    "tray_pwd_hash": "240be518fabd...",
    "unlock_pwd_hash": "240be518fabd..."
  }
}
```

| 字段 | 说明 |
|------|------|
| `domains` | 域名规则列表（白名单或黑名单） |
| `lan_subnets` | 局域网子网列表 |
| `controller_ip` | 教师端 IP（用于断网时保留路由） |
| `upstream_dns` | 上游 DNS 服务器 |
| `mode` | 规则对应模式 |
| `tray_pwd_hash` | 系统托盘退出密码 SHA-256 |
| `unlock_pwd_hash` | 锁屏解锁密码 SHA-256 |

#### TEST_MESSAGE — 测试消息

```json
{
  "type": "test_message",
  "payload": {
    "content": "这是一条测试消息"
  }
}
```

教师端通过控制面板发送的测试消息。学生端接收后存入 `state.last_test_message`，可通过 HTTP `GET /api/test_message` 查询。

#### DISCONNECT — 断开连接

```json
{
  "type": "disconnect"
}
```

#### RECONNECT — 重连

```json
{
  "type": "reconnect"
}
```

#### GET_STATUS — 查询状态

```json
{
  "type": "get_status"
}
```

---

## 4. 配置文件

配置文件路径：`packages/student-backend/config.json`（开发环境）或可执行文件同目录（生产环境）。

首次运行自动生成，默认值：

```json
{
  "controller_url": "ws://192.168.1.100:8765/ws",
  "controller_api_url": "http://192.168.1.100:8770",
  "local_api_host": "127.0.0.1",
  "local_api_port": 8772,
  "upstream_dns": "114.114.114.114",
  "lan_subnets": ["192.168.1.0/24"],
  "tray_visible": true,
  "tray_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
  "unlock_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `controller_url` | string | `ws://192.168.1.100:8765/ws` | 教师端 WebSocket 地址 |
| `controller_api_url` | string | `http://192.168.1.100:8770` | 教师端外部 HTTP API 地址 |
| `local_api_host` | string | `127.0.0.1` | 本机 API 监听地址 |
| `local_api_port` | integer | `8772` | 本机 API 监听端口 |
| `upstream_dns` | string | `114.114.114.114` | 上游 DNS（normal 模式使用） |
| `lan_subnets` | string[] | `["192.168.1.0/24"]` | 局域网子网（放行不被过滤） |
| `tray_visible` | boolean | `true` | 是否显示系统托盘图标 |
| `tray_password_hash` | string | — | 托盘退出密码的 SHA-256（默认 `admin123`） |
| `unlock_password_hash` | string | — | 锁屏解锁密码的 SHA-256（默认 `admin123`） |

> ⚠️ `tray_password_hash` 和 `unlock_password_hash` 默认值为 `admin123` 的 SHA-256 小写十六进制。正式上线前务必修改。

---

## 5. 四种网络模式

| 模式 | DNS | 防火墙 | 路由表 | 效果 |
|------|-----|--------|--------|------|
| `normal` | 上游 DNS（如 114.114.114.114） | 全部放行 | 默认网关 | 正常上网 |
| `whitelist` | 劫持到 127.0.0.1（本地 DNS 代理） | 默认封锁 + 仅放行白名单 IP | 删默认路由，按 DNS 解析动态加 `/32` 主机路由 | 仅允许白名单域名 |
| `blacklist` | 劫持到 127.0.0.1 | 清空（仅 DNS 拦截） | 默认网关 | 拦截黑名单域名，其余正常 |
| `disconnect` | 上游 DNS | 清空 | 删默认路由，仅保留到教师端 `/32` 路由 | 完全断网 |

---

## 6. 开发建议

### 轮询模式

学生端 Electron 前端建议采用轮询方式获取状态：

```typescript
// 每 2 秒轮询状态
setInterval(async () => {
  const res = await fetch('http://127.0.0.1:8772/api/status')
  const data = await res.json()
  // 更新 UI
}, 2000)
```

### 测试消息

教师端可向学生端发送测试消息，用于验证通信链路：

1. 教师端调用 `POST http://127.0.0.1:8771/api/test/send` 或通过控制面板 UI 发送
2. 学生端通过 WebSocket 接收，存入 state
3. 学生端前端通过 `GET http://127.0.0.1:8772/api/test_message` 获取最新消息

### 模拟本地测试

不连接教师端时，可通过 `POST /api/apply_mode` 本地切换模式，验证网络控制逻辑。

---

## 7. 错误处理

所有接口在成功时返回 `{"ok": true, ...}`。异常时返回 HTTP 错误状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误（无效模式名、缺少必填字段） |
| 500 | 内部错误（网络控制操作失败等） |
