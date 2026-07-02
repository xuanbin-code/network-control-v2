# DELETE /rules/{list_type}/{rule_id}

删除一条白名单或黑名单规则。删除成功后会通过 WebSocket 向学生端推送规则更新。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/rules/{list_type}/{rule_id}` |
| 方法 | `DELETE` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 路径参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `list_type` | string | 是 | 规则类型：`whitelist` 或 `blacklist` |
| `rule_id` | integer | 是 | 规则 ID |

### 请求示例

```
DELETE /api/rules/whitelist/1
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
