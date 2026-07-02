# POST /test/send

向指定学生端（或全部学生端）发送测试消息。消息通过 WebSocket 下发，学生端可通过 `GET /api/test_message` 读取。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/test/send` |
| 方法 | `POST` |
| 服务 | `local_app`（8771） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 消息内容 |
| `targets` | string[] | 否 | 目标学生端 IP 列表；不传表示全部 |

### 请求示例

```json
{
  "message": "这是一条测试消息",
  "targets": ["192.168.1.101"]
}
```

---

## 响应示例

```json
{
  "ok": true,
  "message": "这是一条测试消息",
  "targets": ["192.168.1.101"]
}
```

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/test.py`
