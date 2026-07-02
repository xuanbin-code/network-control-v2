# POST /test/black_screen

向指定学生端（或全部学生端）发送黑屏安静测试指令。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/test/black_screen` |
| 方法 | `POST` |
| 服务 | `local_app`（8771） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `countdown_seconds` | integer | 否 | 30 | 倒计时秒数；`0` 表示持续黑屏 |
| `targets` | string[] | 否 | — | 目标学生端 IP 列表；不传表示全部 |

### 请求示例

```json
{
  "countdown_seconds": 30,
  "targets": ["192.168.1.101"]
}
```

---

## 响应示例

```json
{
  "ok": true,
  "action": "black_screen",
  "countdown_seconds": 30,
  "targets": ["192.168.1.101"]
}
```

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/test.py`
