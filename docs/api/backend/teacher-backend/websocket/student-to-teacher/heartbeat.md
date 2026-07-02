# heartbeat（学生端 → 教师端）

学生端周期性心跳，用于维持连接并上报当前网络状态。

---

## 消息方向

学生端 → 教师端

---

## 发送频率

每 **20 秒** 发送一次。

---

## 消息格式

```json
{
  "type": "heartbeat",
  "payload": {
    "filter_active": true,
    "net_state": "whitelist"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `filter_active` | boolean | 网络过滤是否激活 |
| `net_state` | string | 当前网络模式 |

---

## 教师端处理逻辑

- 更新该学生端的 `last_heartbeat` 和 `mode`。
- 若超过 60 秒未收到心跳，则标记为离线。

---

## 源码位置

- 发送：`packages/student-backend/app/services/ws_client.py`
- 接收处理：`packages/teacher-backend/app/services/ws_manager.py`
- 协议定义：`packages/shared/protocol.py`
