# get_status（教师端 → 学生端）

教师端要求学生端立即上报当前状态。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "get_status"
}
```

---

## 学生端处理逻辑

- 读取当前运行状态。
- 回复 `status` 消息，包含 `filter_active`、`dns_running`、`rule_count`、`net_state`。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
