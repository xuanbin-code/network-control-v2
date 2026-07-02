# set_filter（教师端 → 学生端）

设置学生端的网络模式。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "set_filter",
  "payload": {
    "enabled": true,
    "mode": "whitelist"
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用过滤；`normal` 模式为 `false`，其余为 `true` |
| `mode` | string | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

---

## 学生端处理逻辑

- 若 `enabled` 为 `false`，强制转为 `normal` 模式。
- 调用 `apply_filter_mode` 修改本机网络。
- 同步 DNS 服务器模式与托盘图标状态。
- 发送 `status` 消息回执。

---

## 触发场景

- 教师端调用 `/network/set`、`/network/enable`、`/network/disable`、`/network/enable_ip`、`/network/disable_ip`。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
