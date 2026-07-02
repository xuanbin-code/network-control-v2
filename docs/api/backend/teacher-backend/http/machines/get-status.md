# GET /status

获取学生端状态汇总，结构与 `/machines` 类似，额外包含 `ok` 字段。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/status` |
| 方法 | `GET` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "ok": true,
  "agents": [
    {
      "ip": "192.168.1.101",
      "hostname": "STU-001",
      "mac": "aa:bb:cc:dd:ee:ff",
      "mode": "whitelist",
      "online": 1,
      "last_heartbeat": 1719500000.123
    }
  ]
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 请求是否成功 |
| `agents` | array | 学生机记录数组，字段同 `/machines` |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/machines.py`
