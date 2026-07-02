# GET /rules

获取当前白名单和黑名单规则列表。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/rules` |
| 方法 | `GET` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "whitelist": [
    { "id": 1, "domain": "www.baidu.com", "enabled": 1 },
    { "id": 2, "domain": "www.example.com", "enabled": 1 }
  ],
  "blacklist": [
    { "id": 3, "domain": "game.example.com", "enabled": 0 }
  ]
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `whitelist` | array | 白名单规则列表 |
| `blacklist` | array | 黑名单规则列表 |
| `*.id` | integer | 规则 ID |
| `*.domain` | string | 域名 |
| `*.enabled` | integer | 是否启用：`1` 启用，`0` 禁用 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/rules.py`
