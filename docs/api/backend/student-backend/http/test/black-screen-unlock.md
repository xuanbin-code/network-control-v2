# POST /test/black_screen_unlock

向本地黑屏安静 IPC 服务器发送解除命令，关闭测试黑屏窗口。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/test/black_screen_unlock` |
| 方法 | `POST` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "ok": true
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功发送解除命令 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/test_features.py`
