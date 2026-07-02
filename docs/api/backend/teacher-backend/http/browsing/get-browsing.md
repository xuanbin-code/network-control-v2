# GET /browsing/{ip}

查询指定学生机的 DNS 浏览日志。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/browsing/{ip}` |
| 方法 | `GET` |
| 服务 | `local_app`（8771） |

---

## 路径参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ip` | string | 是 | 学生端 IP |

## 查询参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | integer | 否 | 100 | 返回条数上限 |

### 请求示例

```
GET /api/browsing/192.168.1.101?limit=50
```

---

## 响应示例

```json
{
  "ip": "192.168.1.101",
  "logs": [
    { "domain": "www.baidu.com", "ts": 1719500000.123 },
    { "domain": "www.example.com", "ts": 1719499990.456 }
  ]
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ip` | string | 查询的学生端 IP |
| `logs` | array | 浏览记录数组 |
| `logs[].domain` | string | 访问域名 |
| `logs[].ts` | number | 记录时间（Unix 时间戳） |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/browsing.py`
