# POST /test/black_screen

启动黑屏安静测试窗口，用于演示或测试锁屏功能。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/test/black_screen` |
| 方法 | `POST` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `countdown_seconds` | integer | 否 | 30 | 倒计时秒数；`0` 或 `null` 表示持续黑屏，需手动/IPC 解除 |

### 请求示例

```json
{
  "countdown_seconds": 30
}
```

---

## 响应示例

```json
{
  "ok": true,
  "pid": 12345,
  "countdown_seconds": 30,
  "infinite": false
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功 |
| `pid` | integer | 黑屏进程 ID |
| `countdown_seconds` | integer | 实际倒计时秒数 |
| `infinite` | boolean | 是否为持续黑屏 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/test_features.py`
