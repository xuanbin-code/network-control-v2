# POST /rules/{list_type}/{rule_id}/toggle

启用或禁用一条规则。操作成功后会通过 WebSocket 向学生端推送规则更新。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/rules/{list_type}/{rule_id}/toggle` |
| 方法 | `POST` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 路径参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `list_type` | string | 是 | 规则类型：`whitelist` 或 `blacklist` |
| `rule_id` | integer | 是 | 规则 ID |

### 请求示例

```
POST /api/rules/whitelist/1/toggle
```

---

## 响应示例

```json
{
  "ok": true,
  "enabled": false
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功 |
| `enabled` | boolean | 切换后的启用状态 |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | `list_type` 无效 |
| 404 | 规则不存在 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/rules.py`
