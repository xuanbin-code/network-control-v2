# register（学生端 → 教师端）

学生端 WebSocket 连接成功后立即发送，上报本机身份信息。

---

## 消息方向

学生端 → 教师端

---

## 消息格式

```json
{
  "type": "register",
  "payload": {
    "hostname": "STU-001",
    "ip": "192.168.1.101",
    "mac": "aa:bb:cc:dd:ee:ff",
    "mode": "disconnect"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `hostname` | string | 学生端主机名 |
| `ip` | string | 学生端本地 IP |
| `mac` | string | 学生端 MAC 地址 |
| `mode` | string | 当前网络模式 |

---

## 教师端处理逻辑

1. 在学生机数据库中插入或更新记录，标记为在线。
2. 向该学生端下发当前规则（`update_rules`）。
3. 向该学生端下发权威模式（`set_filter`）。

---

## 源码位置

- 发送：`packages/student-backend/app/services/ws_client.py`
- 接收处理：`packages/teacher-backend/app/services/ws_manager.py`
- 协议定义：`packages/shared/protocol.py`
