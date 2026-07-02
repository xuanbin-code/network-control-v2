# POST /config

部分更新学生端配置，并持久化到 `config.json`。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/config` |
| 方法 | `POST` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |
| 请求体 | `application/json` |

---

## 请求参数

请求体为需要修改的配置项，未传入的字段保持不变。

### 请求示例

```json
{
  "controller_url": "ws://192.168.1.200:8765/ws",
  "upstream_dns": "8.8.8.8"
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

## 注意事项

- `controller_url` 修改后，WebSocket 客户端会在下一次重连时使用新地址。
- 密码哈希字段（`tray_password_hash`、`unlock_password_hash`）也可以在此更新。

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/config.py`
