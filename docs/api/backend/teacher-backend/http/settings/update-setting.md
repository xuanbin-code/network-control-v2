# POST /settings

更新教师端系统设置。若修改的是 `filter_mode`、`lan_subnets`、`upstream_dns`，会自动向学生端重新推送规则。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/settings` |
| 方法 | `POST` |
| 服务 | `local_app`（8771） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `key` | string | 是 | 设置项名称 |
| `value` | string | 是 | 设置项值（列表/对象需 JSON 序列化为字符串） |

### 请求示例

```json
{
  "key": "upstream_dns",
  "value": "8.8.8.8"
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

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/settings.py`
