# 教师端后端接口

> 对应源码：`packages/teacher-backend/app/api/v1/endpoints/`

---

## HTTP 接口索引

| 路由 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/server_info` | GET | 获取教师端 IP 与 WebSocket 地址 |
| `/machines` | GET | 获取学生机列表 |
| `/status` | GET | 获取学生机在线状态 |
| `/network/set` | POST | 设置网络模式（可指定目标） |
| `/network/enable` | GET / POST | 一键开网（全部） |
| `/network/disable` | GET / POST | 一键禁网（全部） |
| `/network/enable_ip` | GET / POST | 按 IP 开单台 |
| `/network/disable_ip` | GET / POST | 按 IP 禁单台 |
| `/rules` | GET | 获取黑白名单规则 |
| `/rules/{list_type}` | POST | 添加规则 |
| `/rules/{list_type}/{rule_id}` | DELETE | 删除规则 |
| `/rules/{list_type}/{rule_id}/toggle` | POST | 启用/禁用规则 |
| `/scan` | GET | 扫描局域网网段 |
| `/browsing/{ip}` | GET | 查询某学生机的浏览记录 |
| `/settings` | GET / POST | 获取/更新系统设置 |
| `/test/send` | POST | 向学生端发送测试消息 |
| `/test/black_screen` | POST | 向学生端发送黑屏指令 |
| `/test/black_screen_unlock` | POST | 向学生端发送解除黑屏指令 |

---

## WebSocket 接口索引

连接地址：`ws://<教师IP>:8765/ws` 或 `ws://127.0.0.1:8771/ws`

### 学生端 → 教师端

| 消息类型 | 说明 |
|----------|------|
| `register` | 上线注册 |
| `heartbeat` | 心跳保活 |
| `status` | 状态上报 |
| `browsing_update` | 浏览日志上报 |
| `ack` | 确认应答 |

### 教师端 → 学生端

| 消息类型 | 说明 |
|----------|------|
| `set_filter` | 设置网络模式 |
| `update_rules` | 更新规则 |
| `test_message` | 测试消息 |
| `black_screen` | 黑屏安静测试 |
| `black_screen_unlock` | 解除黑屏 |
| `disconnect` | 断开连接 |
| `reconnect` | 恢复连接 |
| `get_status` | 查询状态 |

---

## 源码对应关系

```
app/api/v1/endpoints/
├── health.py      → /health
├── server.py      → /server_info
├── machines.py    → /machines, /status
├── network.py     → /network/*
├── rules.py       → /rules/*
├── scan.py        → /scan
├── browsing.py    → /browsing/*
├── settings.py    → /settings
└── test.py        → /test/send
```
