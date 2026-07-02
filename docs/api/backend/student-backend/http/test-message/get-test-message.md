# GET /test_message

获取教师端最近一次通过 WebSocket 发送的测试消息。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/test_message` |
| 方法 | `GET` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "message": "这是一条测试消息",
  "ts": 1719500000.123,
  "time_str": "2024-06-27 20:00:00"
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 消息内容，未收到过时为空字符串 |
| `ts` | number | Unix 时间戳（秒），未收到过时为 `0` |
| `time_str` | string | 格式化时间字符串，未收到过时为空字符串 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/test_message.py`
