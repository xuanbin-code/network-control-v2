# status（学生端 → 教师端）

学生端在模式切换或收到状态查询后，主动上报详细运行状态。

---

## 消息方向

学生端 → 教师端

---

## 消息格式

```json
{
  "type": "status",
  "payload": {
    "filter_active": true,
    "dns_running": true,
    "rule_count": 15,
    "net_state": "whitelist"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `filter_active` | boolean | 网络过滤是否激活 |
| `dns_running` | boolean | 本地 DNS 代理是否运行 |
| `rule_count` | integer | 当前生效的域名规则数量 |
| `net_state` | string | 当前网络模式 |

---

## 教师端处理逻辑

更新数据库中对应学生端的 `mode` 和 `online` 状态。

---

## 源码位置

- 发送：`packages/student-backend/app/services/ws_client.py`
- 接收处理：`packages/teacher-backend/app/services/ws_manager.py`
- 协议定义：`packages/shared/protocol.py`
