# 教师端 WebSocket 协议

> 对应源码：`packages/teacher-backend/app/websocket/routes.py`、`packages/teacher-backend/app/services/ws_manager.py`、`packages/shared/protocol.py`

---

## 连接信息

| 项目 | 值 |
|------|-----|
| 路径 | `/ws` |
| 端口 | `8765`（学生端主连接）或 `8771`（本地调试） |
| 协议 | WebSocket（JSON 文本帧） |
| 心跳间隔 | 20 秒（学生端发送） |
| 心跳超时 | 60 秒 |

---

## 消息格式

默认使用 `payload` 封装：

```json
{
  "type": "<消息类型>",
  "payload": {
    // 业务字段
  }
}
```

兼容旧版扁平格式：除 `type` 外，其他字段直接放在顶层。

---

## 目录

- [学生端 → 教师端](student-to-teacher/)
  - [`register`](student-to-teacher/register.md)
  - [`heartbeat`](student-to-teacher/heartbeat.md)
  - [`status`](student-to-teacher/status.md)
  - [`browsing_update`](student-to-teacher/browsing-update.md)
  - [`ack`](student-to-teacher/ack.md)
- [教师端 → 学生端](teacher-to-student/)
  - [`set_filter`](teacher-to-student/set-filter.md)
  - [`update_rules`](teacher-to-student/update-rules.md)
  - [`test_message`](teacher-to-student/test-message.md)
  - [`black_screen`](teacher-to-student/black-screen.md)
  - [`black_screen_unlock`](teacher-to-student/black-screen-unlock.md)
  - [`disconnect`](teacher-to-student/disconnect.md)
  - [`reconnect`](teacher-to-student/reconnect.md)
  - [`get_status`](teacher-to-student/get-status.md)
