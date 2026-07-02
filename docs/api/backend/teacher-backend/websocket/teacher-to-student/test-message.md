# test_message（教师端 → 学生端）

教师端向学生端发送测试消息，用于验证通信链路。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "test_message",
  "payload": {
    "content": "这是一条测试消息"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | string | 消息内容 |

---

## 学生端处理逻辑

- 将消息内容存入 `state.last_test_message` 和 `state.last_test_message_ts`。
- 学生端前端可通过 `GET /api/test_message` 获取最新消息。

---

## 触发场景

- 教师端调用 `POST /api/test/send`。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
