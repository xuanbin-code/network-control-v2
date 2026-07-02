# POST /reload_config

重新从磁盘加载 `config.json`，并更新 WebSocket 客户端连接地址。主要用于调试。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/reload_config` |
| 方法 | `POST` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "ok": true,
  "config": {
    "controller_url": "ws://192.168.1.100:8765/ws",
    "local_api_port": 8772,
    ...
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功 |
| `config` | object | 重新加载后的完整配置 |

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/config.py`
