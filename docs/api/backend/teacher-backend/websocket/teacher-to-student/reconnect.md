# reconnect（教师端 → 学生端）

指示学生端恢复到 `normal`（正常上网）模式。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "reconnect"
}
```

---

## 学生端处理逻辑

- 调用 `apply_filter_mode(FilterMode.NORMAL)`。
- 恢复默认网关和防火墙规则。
- 同步托盘图标状态。
- 发送 `status` 消息回执。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
