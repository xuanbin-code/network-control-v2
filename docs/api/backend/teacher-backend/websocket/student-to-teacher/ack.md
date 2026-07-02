# ack（学生端 → 教师端）

学生端对接收到的指令进行确认应答。

---

## 消息方向

学生端 → 教师端

---

## 消息格式

```json
{
  "type": "ack",
  "payload": {
    "ok": true,
    "message": "Rules applied"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 操作是否成功 |
| `message` | string | 结果描述 |

---

## 源码位置

- 发送：`packages/student-backend/app/services/ws_client.py`
- 接收处理：`packages/teacher-backend/app/services/ws_manager.py`
- 协议定义：`packages/shared/protocol.py`
