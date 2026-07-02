# black_screen_unlock（教师端 → 学生端）

教师端远程解除学生端黑屏安静窗口。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "black_screen_unlock"
}
```

---

## 学生端处理逻辑

- 向本地黑屏 IPC 服务器发送解除命令。
- 向教师端回复 `ack` 消息。

---

## 触发场景

- 教师端调用 `POST /api/test/black_screen_unlock`。
- 教师端控制面板点击「解除黑屏」。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
- 黑屏实现：`packages/student-backend/app/services/black_screen.py`
