# GET /server_info

返回教师端本机 IP 和 WebSocket 服务地址，供学生端配置或前端展示二维码/连接信息。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/server_info` |
| 方法 | `GET` |
| 服务 | `local_app`（8771） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "ip": "192.168.1.100",
  "ws_url": "ws://192.168.1.100:8765/ws",
  "ws_port": 8765
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ip` | string | 教师端本机 IP（通过 UDP 探测外网后获得） |
| `ws_url` | string | 学生端应连接的 WebSocket 完整地址 |
| `ws_port` | integer | WebSocket 服务端口 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/server.py`
