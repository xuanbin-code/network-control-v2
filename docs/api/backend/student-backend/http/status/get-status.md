# GET /status

获取学生端当前运行状态。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/status` |
| 方法 | `GET` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "mode": "whitelist",
  "connected": true,
  "controller_url": "ws://192.168.1.100:8765/ws",
  "controller_ip": "192.168.1.100",
  "hostname": "STU-001",
  "mac": "aa:bb:cc:dd:ee:ff",
  "filter_active": true,
  "dns_running": true,
  "rule_count": 15
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | string | 当前网络模式 |
| `connected` | boolean | WebSocket 连接状态 |
| `controller_url` | string | 教师端 WebSocket 地址 |
| `controller_ip` | string | 教师端 IP |
| `hostname` | string | 本机主机名 |
| `mac` | string | 本机 MAC 地址 |
| `filter_active` | boolean | 网络过滤是否激活 |
| `dns_running` | boolean | DNS 代理是否运行 |
| `rule_count` | integer | 当前生效的域名规则数量 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/status.py`
