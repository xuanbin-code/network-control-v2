# GET /settings

获取教师端系统设置。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/settings` |
| 方法 | `GET` |
| 服务 | `local_app`（8771） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "filter_mode": "whitelist",
  "lan_subnets": ["192.168.1.0/24"],
  "upstream_dns": "114.114.114.114",
  "tray_password_hash": "240be518fabd...",
  "unlock_password_hash": "240be518fabd..."
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `filter_mode` | string | 默认过滤模式 |
| `lan_subnets` | string[] | 局域网子网列表 |
| `upstream_dns` | string | 上游 DNS 服务器 |
| `tray_password_hash` | string | 托盘退出密码 SHA-256 |
| `unlock_password_hash` | string | 锁屏解锁密码 SHA-256 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/settings.py`
