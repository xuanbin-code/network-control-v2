# POST /rules/{list_type}

添加一条白名单或黑名单规则。添加成功后会通过 WebSocket 向学生端推送规则更新。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/rules/{list_type}` |
| 方法 | `POST` |
| 服务 | `local_app`（8771）、`external_app`（8770） |
| 请求体 | `application/json` |

---

## 路径参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `list_type` | string | 是 | 规则类型：`whitelist` 或 `blacklist` |

## 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `domain` | string | 是 | 域名 |

### 请求示例

```json
// POST /api/rules/whitelist
{
  "domain": "www.baidu.com"
}
```

---

## 响应示例

```json
{
  "ok": true
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | `list_type` 无效 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/rules.py`
