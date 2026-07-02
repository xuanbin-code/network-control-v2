# GET /config

返回完整的 `config.json` 内容。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/config` |
| 方法 | `GET` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "controller_url": "ws://192.168.1.100:8765/ws",
  "controller_api_url": "http://192.168.1.100:8770",
  "local_api_host": "127.0.0.1",
  "local_api_port": 8772,
  "upstream_dns": "114.114.114.114",
  "lan_subnets": ["192.168.1.0/24"],
  "tray_visible": true,
  "tray_password_hash": "240be518fabd...",
  "unlock_password_hash": "240be518fabd..."
}
```

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/config.py`
