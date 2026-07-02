# 学生端 WebSocket 协议

> 对应源码：`packages/student-backend/app/services/ws_client.py`、`packages/shared/protocol.py`

---

## 角色说明

学生端后端作为 **WebSocket 客户端**，主动连接教师端后端：

```
ws://<教师IP>:8765/ws
```

连接地址由 `config.json` 中的 `controller_url` 决定。

---

## 消息方向

| 方向 | 说明 |
|------|------|
| 学生端 → 教师端 | 注册、心跳、状态上报、浏览日志、确认应答 |
| 教师端 → 学生端 | 模式切换、规则更新、测试消息、断线/重连、状态查询 |

---

## 详细文档

学生端发送/接收的消息类型与教师端 WebSocket 完全一致，详细格式请参考：

- [教师端 WebSocket 文档](../teacher-backend/websocket/README.md)
- [学生端 → 教师端消息](../teacher-backend/websocket/student-to-teacher/)
- [教师端 → 学生端消息](../teacher-backend/websocket/teacher-to-student/)

---

## 学生端特殊处理

- 连接成功后会立即发送 `register` 消息，上报本机 `hostname`、`ip`、`mac`、`mode`。
- 每 20 秒发送一次 `heartbeat`。
- 每 15 秒批量上报一次 DNS 查询日志（`browsing_update`）。
- 收到 `update_rules` 后，会更新本地 DNS 规则、密码哈希，并保存到 `config.json`。
- 收到 `set_filter`、`disconnect`、`reconnect` 后，会调用 `network_filter.apply_filter_mode` 修改本机网络。
