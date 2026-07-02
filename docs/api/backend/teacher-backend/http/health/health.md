# GET /health

健康检查接口，用于确认教师端后端服务是否正常运行。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/health` |
| 方法 | `GET` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "status": "ok"
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定值为 `"ok"` |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/health.py`
