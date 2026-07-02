# disconnect（教师端 → 学生端）

指示学生端切换到 `disconnect`（断网）模式。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "disconnect"
}
```

---

## 学生端处理逻辑

- 调用 `apply_filter_mode(FilterMode.DISCONNECT)`。
- 删除默认路由，仅保留到教师端的 `/32` 主机路由。
- 同步托盘图标状态。
- 发送 `status` 消息回执。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
