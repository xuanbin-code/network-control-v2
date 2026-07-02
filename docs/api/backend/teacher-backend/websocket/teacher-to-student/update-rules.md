# update_rules（教师端 → 学生端）

向学生端更新白名单/黑名单规则、局域网子网、上游 DNS、密码哈希等配置。

---

## 消息方向

教师端 → 学生端

---

## 消息格式

```json
{
  "type": "update_rules",
  "payload": {
    "domains": ["www.baidu.com", "www.example.com"],
    "lan_subnets": ["192.168.1.0/24"],
    "controller_ip": "192.168.1.100",
    "upstream_dns": "114.114.114.114",
    "mode": "whitelist",
    "tray_pwd_hash": "240be518fabd...",
    "unlock_pwd_hash": "240be518fabd..."
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `domains` | string[] | 域名规则列表 |
| `lan_subnets` | string[] | 局域网子网列表 |
| `controller_ip` | string | 教师端 IP，用于断网时保留路由 |
| `upstream_dns` | string | 上游 DNS 服务器 |
| `mode` | string | 当前规则对应的模式 |
| `tray_pwd_hash` | string | 系统托盘退出密码 SHA-256 |
| `unlock_pwd_hash` | string | 锁屏解锁密码 SHA-256 |

---

## 学生端处理逻辑

1. 更新全局状态中的规则、子网、DNS、教师端 IP。
2. 若收到密码哈希，更新 `config.json` 并保存。
3. 热更新本地 DNS 服务器规则和模式。
4. 回复 `ack` 消息。

---

## 触发场景

- 学生端 `register` 上线后，教师端自动下发。
- 教师端修改规则（`/rules/*`）或设置（`/settings`）后，向所有在线学生端推送。

---

## 源码位置

- 发送：`packages/teacher-backend/app/services/ws_manager.py`
- 接收处理：`packages/student-backend/app/services/ws_client.py`
- 协议定义：`packages/shared/protocol.py`
