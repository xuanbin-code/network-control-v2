# POST /network/set

设置指定学生端（或全部学生端）的网络模式，并通过 WebSocket 下发指令。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/network/set` |
| 方法 | `POST` |
| 服务 | `local_app`（8771）、`external_app`（8770） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |
| `targets` | string[] | 否 | 目标学生端 IP 列表；不传表示全部 |

### 请求示例

```json
{
  "mode": "whitelist",
  "targets": ["192.168.1.101", "192.168.1.102"]
}
```

---

## 响应示例

```json
{
  "ok": true,
  "mode": "whitelist",
  "targets": ["192.168.1.101", "192.168.1.102"]
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | `mode` 无效或参数格式错误 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/network.py`
