# GET /health

健康检查接口，同时返回当前连接状态和网络模式。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/health` |
| 方法 | `GET` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "status": "ok",
  "connected": true,
  "mode": "whitelist"
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定值为 `"ok"` |
| `connected` | boolean | 是否已连接到教师端 WebSocket |
| `mode` | string | 当前网络模式 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/health.py`
