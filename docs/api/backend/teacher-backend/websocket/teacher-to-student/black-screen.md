# black_screen（教师端 → 学生端）

教师端远程触发学生端黑屏安静窗口。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "black_screen",
  "payload": {
    "countdown_seconds": 30
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `countdown_seconds` | integer | 倒计时秒数；`0` 表示持续黑屏，需手动/IPC 解除 |

---

## 学生端处理逻辑

- 启动独立的锁屏子进程 `python -m app.services.lock_screen <countdown_seconds>`。
- 向教师端回复 `ack` 消息。

---

## 触发场景

- 教师端调用 `POST /api/test/black_screen`。
- 教师端控制面板点击「黑屏测试」。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
- 黑屏实现：`packages/student-backend/app/services/black_screen.py`
