# 后端接口文档

本目录收录教师端后端（`packages/teacher-backend`）和学生端后端（`packages/student-backend`）暴露的所有接口。

---

## 教师端后端

教师端后端同时启动三个 Uvicorn 服务：

| 服务 | 监听 | 包含内容 |
|------|------|----------|
| `local_app` | `127.0.0.1:8771` | HTTP API + WebSocket（供 Electron 前端使用） |
| `external_app` | `127.0.0.1:8770` | HTTP API（供第三方教学软件使用） |
| `ws_app` | `0.0.0.0:8765` | WebSocket（供学生端长连接使用） |

因此，HTTP 接口可通过 `8771` 或 `8770` 访问；WebSocket 接口可通过 `8771/ws` 或 `8765/ws` 访问。

详细文档见 [`teacher-backend/README.md`](teacher-backend/README.md)。

---

## 学生端后端

学生端后端启动一个 Uvicorn 服务：

| 服务 | 监听 | 用途 |
|------|------|------|
| FastAPI HTTP | `127.0.0.1:8772`（默认） | 供学生端 Electron 前端调用 |

同时作为 WebSocket **客户端**主动连接教师端 `ws://<教师IP>:8765/ws`。

详细文档见 [`student-backend/README.md`](student-backend/README.md)。

---

## 通用约定

- 所有 HTTP 接口前缀为 `/api`。
- 请求/响应格式为 JSON，`Content-Type: application/json`。
- 成功时通常返回 `{"ok": true, ...}`；参数错误返回 HTTP `400`，服务端异常返回 HTTP `500`。
- WebSocket 消息默认为 JSON 文本帧，结构为 `{"type": "<消息类型>", "payload": {...}}`，同时兼容旧版扁平格式。
